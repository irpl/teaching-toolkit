"""Single Parakeet TDT engine for every local transcription job on this machine.

Before 2026-09-04 this logic existed in three divergent copies —
teaching-toolkit/transcribe_chunked.py, Desktop/video-summaries/transcribe_parakeet.py,
and the recipes inlined in the grading skills. They drifted: only one used fp16,
only one had retries, only one rebuilt readable segments, and they used three
different chunk sizes. This module is the one implementation; the others are thin
callers.

WHAT THIS DOES
  Cuts long audio into chunks, transcribes each in a worker subprocess that
  reclaims VRAM on exit, banks each chunk's words to disk immediately (so a
  crashed run resumes), then optionally diarizes and writes outputs.

CHUNK SIZING (measured 2026-09-04 on the 6 GB RTX 3060, fp16 — see
parakeet-setup.md §7.2). Peak allocation by chunk length:

    180 s -> 3.77 GB    900 s -> 4.30 GB     1800 s -> 7.34 GB (spills, RTF 20x)
    600 s -> 3.77 GB    1200 s -> 5.32 GB

Below ~900 s the CUDA-graph static decoder buffer dominates and peak is FLAT, so
short chunks buy NO headroom and cost a ~20 s model load each. This is the
opposite of what the older notes assumed. 600 s is the operating point: maximum
RTF (~32x) with ~2.3 GB of margin.

Usage as a library:
    import asr
    words = asr.transcribe(path)                  # word dicts, absolute times
    asr.write_media_outputs(path, words)          # .txt / .srt / .json
    asr.write_diarized_outputs(path, words)       # _transcript.txt / _words.json

Usage as a CLI:
    python asr.py <audio_16k_mono.wav> [--diarize] [--media]
Internal worker modes (not for humans):
    python asr.py <audio> --chunks 0,1,2
"""
import os, sys, gc, math, json, time, subprocess

THIS = os.path.abspath(__file__)
PARAKEET_PY = os.path.join(os.path.dirname(THIS), "parakeet-env", "Scripts", "python.exe")
MODEL_NAME = "nvidia/parakeet-tdt-0.6b-v3"

# --- tunables (see the sizing table above before changing CHUNK_SEC) ----------
CHUNK_SEC = int(os.environ.get("CHUNK_SEC", 600))
# Peak VRAM is flat in chunk length below ~900 s, so the only per-chunk cost is
# the ~20 s model load. Several chunks per worker amortise that, and the CUDA
# graph stays warm — measured 18.8 s for a worker's first 600 s chunk vs ~5.2 s
# for each subsequent one. Set to 1 for the old one-chunk-per-process behaviour.
CHUNKS_PER_PROC = int(os.environ.get("CHUNKS_PER_PROC", 3))
CHUNK_TRIES = int(os.environ.get("CHUNK_TRIES", 3))
COOLDOWN_SEC = int(os.environ.get("COOLDOWN_SEC", 5))
NEED_COMMIT_GB = float(os.environ.get("NEED_COMMIT_GB", 4.5))
HEADROOM_WAIT = int(os.environ.get("HEADROOM_WAIT", 180))
FP16 = os.environ.get("FP16", "1") != "0"
# CUDA-graph decoding costs a fixed ~3.8 GB buffer but is ~1.8x faster, and that
# cost is free at the chunk sizes above. CUDA_GRAPHS=0 drops peak to ~3.3 GB at
# 600 s if you ever need the headroom back (e.g. another GPU app is running).
CUDA_GRAPHS = os.environ.get("CUDA_GRAPHS", "1") != "0"
# Readable-segment rebuild. Raw Parakeet TDT segments are bimodal and can run
# 280 s without a break, so segments are always rebuilt from the word stream.
GAP_SPLIT = float(os.environ.get("GAP_SPLIT", 0.7))
SEG_CAP = float(os.environ.get("SEG_CAP", 30.0))


def ensure_venv(script=None):
    """Re-exec under the parakeet-env interpreter if we aren't already on it.

    Re-execs the *calling* script, not this module — a thin wrapper that called
    ensure_venv() and got asr.py back would silently lose whatever the wrapper
    does after transcription (e.g. diarization).
    """
    if os.path.normcase(sys.executable) != os.path.normcase(PARAKEET_PY):
        if not os.path.exists(PARAKEET_PY):
            sys.exit(f"parakeet-env python not found at {PARAKEET_PY} — "
                     "see teaching-toolkit/parakeet-setup.md")
        script = os.path.abspath(script or sys.argv[0] or THIS)
        os.execv(PARAKEET_PY, [PARAKEET_PY, script] + sys.argv[1:])


# --- layout ------------------------------------------------------------------

def layout(audio_path):
    import soundfile as sf
    info = sf.info(audio_path)
    dur = info.frames / info.samplerate
    d = os.path.dirname(audio_path) or "."
    return d, info.samplerate, math.ceil(dur / CHUNK_SEC)


def cf_path(d, i):  return os.path.join(d, f"_chunk_{i}.wav")
def wj_path(d, i):  return os.path.join(d, f"_words_chunk_{i}.json")


# --- model + worker ----------------------------------------------------------

def load_model():
    import nemo.collections.asr as nemo_asr
    from omegaconf import open_dict

    model = nemo_asr.models.ASRModel.from_pretrained(MODEL_NAME)
    # Local attention: required headroom for anything beyond a short clip.
    model.change_attention_model("rel_pos_local_attn", [256, 256])
    model.change_subsampling_conv_chunking_factor(1)
    model = model.to("cuda").eval()
    if FP16:
        # fp32 peaks right at the card's free VRAM and OOMs on some chunks.
        # Halving the weights buys the margin back; word counts match fp32
        # within ~0.1 %, so ASR quality is unaffected.
        model = model.half()
    if not CUDA_GRAPHS:
        cfg = model.cfg.decoding
        with open_dict(cfg):
            cfg.greedy.use_cuda_graph_decoder = False
        model.change_decoding_strategy(cfg)
    return model


def do_chunks(audio_path, idxs):
    """Worker entry: transcribe the listed chunks, bank each, exit (frees VRAM)."""
    import torch, soundfile as sf
    d, sr, _ = layout(audio_path)
    model = load_model()

    for i in idxs:
        cf = cf_path(d, i)
        if not (os.path.exists(cf) and os.path.getsize(cf) > 0):
            wav, _ = sf.read(audio_path, dtype="float32")
            sf.write(cf, wav[int(i * CHUNK_SEC * sr):int((i + 1) * CHUNK_SEC * sr)], sr)
            del wav
        off = i * CHUNK_SEC
        out = model.transcribe([cf], timestamps=True)
        words = [{"word": w["word"], "start": w["start"] + off, "end": w["end"] + off}
                 for w in out[0].timestamp["word"]]
        with open(wj_path(d, i), "w", encoding="utf-8") as f:
            json.dump(words, f)
        peak = torch.cuda.max_memory_allocated() / 1e9
        print(f"[chunk {i}] {len(words)} words (peak {peak:.2f} GB)", flush=True)

    del model; gc.collect(); torch.cuda.empty_cache()


# --- host-memory headroom ----------------------------------------------------

def free_commit_gb():
    """Free Windows commit charge, in GB. Returns None off Windows / on error."""
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MEMORYSTATUSEX()
        m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullAvailPageFile / 1e9
    except Exception:
        return None


def wait_for_headroom(tag, attempt):
    """Windows does not release a dead worker's commit instantly; starting the next
    one too early raises std::bad_alloc ("RuntimeError: bad allocation") inside the
    NeMo preprocessor. Cool down, then wait for commit to actually come back."""
    time.sleep(COOLDOWN_SEC * attempt)
    deadline = time.time() + HEADROOM_WAIT
    while time.time() < deadline:
        g = free_commit_gb()
        if g is None or g >= NEED_COMMIT_GB:
            return
        print(f"{tag} free commit {g:.1f} GB < {NEED_COMMIT_GB} GB — waiting", flush=True)
        time.sleep(10)
    print(f"{tag} headroom wait timed out — proceeding anyway", flush=True)


# --- orchestration -----------------------------------------------------------

def transcribe(audio_path, cleanup=True):
    """Transcribe any-length audio. Returns word dicts with absolute timestamps."""
    d, _, n = layout(audio_path)
    print(f"asr: {n} chunk(s) of {CHUNK_SEC}s, {CHUNKS_PER_PROC} per worker, "
          f"fp16={FP16} cuda_graphs={CUDA_GRAPHS}", flush=True)

    todo = [i for i in range(n) if not os.path.exists(wj_path(d, i))]
    if len(todo) < n:
        print(f"resuming: {n - len(todo)}/{n} chunks already banked", flush=True)

    while todo:
        batch = todo[:CHUNKS_PER_PROC]
        tag = f"[chunks {batch[0]}-{batch[-1]}]"
        ok = False
        for attempt in range(1, CHUNK_TRIES + 1):
            wait_for_headroom(tag, attempt)
            print(f"{tag} worker (try {attempt}/{CHUNK_TRIES})...", flush=True)
            r = subprocess.run([PARAKEET_PY if os.path.exists(PARAKEET_PY) else sys.executable,
                                THIS, audio_path, "--chunks", ",".join(map(str, batch))])
            # Partial progress counts: a worker that banked some chunks before
            # dying still moved the run forward, so re-check rather than blindly
            # retrying the whole batch.
            remaining = [i for i in batch if not os.path.exists(wj_path(d, i))]
            if not remaining:
                ok = True
                break
            if len(remaining) < len(batch):
                print(f"{tag} partial: {len(batch) - len(remaining)} banked, "
                      f"{len(remaining)} left", flush=True)
                batch = remaining
            print(f"{tag} try {attempt} incomplete (rc={r.returncode})", flush=True)
        if not ok:
            sys.exit(f"{tag} FAILED after {CHUNK_TRIES} tries. Re-run to resume.")
        todo = [i for i in todo if not os.path.exists(wj_path(d, i))]

    words = []
    for i in range(n):
        with open(wj_path(d, i), encoding="utf-8") as f:
            words.extend(json.load(f))
    if cleanup:
        for i in range(n):
            for p in (cf_path(d, i), wj_path(d, i)):
                if os.path.exists(p):
                    os.remove(p)
    return words


# --- segmentation + writers --------------------------------------------------

def segment(words):
    """Rebuild readable segments from the word stream.

    Necessary, not cosmetic: raw Parakeet TDT segment timestamps only split on
    clear pauses, which on a 30-min benchmark produced one 283-second segment
    with no sentence break. Word-level timestamps are fine, so segments are
    rebuilt from them.
    """
    segs, cur = [], []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > GAP_SPLIT
                    or w["end"] - cur[0]["start"] > SEG_CAP):
            segs.append(cur)
            cur = []
        cur.append(w)
    if cur:
        segs.append(cur)
    return [{"start": s[0]["start"], "end": s[-1]["end"],
             "text": " ".join(w["word"] for w in s)} for s in segs]


def ts_txt(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def ts_srt(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{int((s % 1) * 1000):03}"


def write_media_outputs(audio_path, words):
    """WhisperX-compatible names: <base>.txt / .srt / .json — for video pipelines."""
    base = audio_path.rsplit(".", 1)[0]
    segs = segment(words)
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write("\n".join(f"[{ts_txt(s['start'])}] {s['text']}" for s in segs) + "\n")
    with open(base + ".srt", "w", encoding="utf-8") as f:
        for n, s in enumerate(segs, 1):
            f.write(f"{n}\n{ts_srt(s['start'])} --> {ts_srt(s['end'])}\n{s['text']}\n\n")
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump({"segments": segs, "words": words}, f, ensure_ascii=False, indent=1)
    print(f"Wrote {base}.txt / .srt / .json  ({len(words)} words, {len(segs)} segments)")


def write_diarized_outputs(audio_path, words, num_speakers=None):
    """Speaker-labelled outputs: <base>_transcript.txt / _words.json — for vivas.

    Pass num_speakers when known (viva = 2, walkthrough = 1); it is the biggest
    accuracy lever available here. See transcribe.diarize().
    """
    import transcribe as T
    print(f"[diarize] {len(words)} words; diarizing "
          f"(speakers={num_speakers or 'auto'})...", flush=True)
    diar = T.diarize(audio_path, num_speakers=num_speakers)
    print(f"[diarize] {len(diar)} speaker turns; merging...", flush=True)
    merged = T.assign_speakers(words, diar)
    base = audio_path.rsplit(".", 1)[0]
    with open(base + "_transcript.txt", "w", encoding="utf-8") as f:
        f.write(T.format_transcript(merged))
    with open(base + "_words.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print(f"Wrote {base}_transcript.txt and {base}_words.json")
    return merged


def _diarize_subprocess(audio_path, words, num_speakers=None):
    """Diarize in a fresh process so pyannote gets clean VRAM after Parakeet."""
    d, _, _ = layout(audio_path)
    stash = os.path.join(d, "_words_all.json")
    with open(stash, "w", encoding="utf-8") as f:
        json.dump(words, f)
    wait_for_headroom("[diarize]", 1)
    cmd = [PARAKEET_PY if os.path.exists(PARAKEET_PY) else sys.executable,
           THIS, audio_path, "--diarize-only", stash]
    if num_speakers:
        cmd += ["--speakers", str(num_speakers)]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"[diarize] FAILED (rc={r.returncode}).")
    os.remove(stash)


def _arg(flag, cast=str, default=None):
    return cast(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default


if __name__ == "__main__":
    ensure_venv()
    audio = sys.argv[1]
    if "--chunks" in sys.argv:
        do_chunks(audio, [int(x) for x in sys.argv[sys.argv.index("--chunks") + 1].split(",")])
    elif "--diarize-only" in sys.argv:
        stash = sys.argv[sys.argv.index("--diarize-only") + 1]
        with open(stash, encoding="utf-8") as f:
            write_diarized_outputs(audio, json.load(f), _arg("--speakers", int))
    else:
        words = transcribe(audio)
        # Media outputs are cheap and always useful; diarization costs ~230 s per
        # 30 min of audio, so it is opt-in — most recordings here are one speaker.
        write_media_outputs(audio, words)
        if "--diarize" in sys.argv:
            _diarize_subprocess(audio, words, _arg("--speakers", int))
        print("DONE", flush=True)
