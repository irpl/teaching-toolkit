"""Chunked, RESUMABLE, subprocess-ISOLATED Parakeet TDT + pyannote pipeline for
LONG audio on 6 GB VRAM.

transcribe.py does a single Parakeet pass, which OOMs / CUDA-aborts past ~10 min
on the 6 GB 3060 (parakeet-setup.md §5). Even chunking in ONE process eventually
CUDA-aborts on the tail chunk because VRAM fragmentation accumulates across passes
(observed: crash on chunk 8/8). So each chunk is transcribed in its OWN subprocess,
which fully reclaims VRAM on exit — no accumulation. Each chunk's words are written
to _words_chunk_i.json immediately, so the run is resumable: re-running skips
completed chunks. Diarization + merge reuse transcribe.py's logic.

Usage (self-driving):  python transcribe_chunked.py <audio_16k_mono.wav>
Internal modes:        ... --chunk <i>   (transcribe one chunk)
                       ... --finish      (diarize + merge + write outputs)
Writes: <audio>_transcript.txt  and  <audio>_words.json
"""
import os, sys, gc, math, json, time, subprocess
import soundfile as sf

THIS = os.path.abspath(__file__)
sys.path.insert(0, os.path.dirname(THIS))
# 300 s no longer fits 6 GB VRAM: on torch 2.11.0+cu130 a 300 s chunk dies in the
# preprocessor/decoder (CUDA OOM, then context corruption -> "unknown error" /
# "bad allocation"). Measured 2026-08-24: 240 s passes, 300 s fails; peak alloc is
# ~5.06 GB against ~5.27 GB free. 180 s keeps margin. Override with CHUNK_SEC env.
CHUNK_SEC = int(os.environ.get("CHUNK_SEC", 180))
CHUNK_TRIES = int(os.environ.get("CHUNK_TRIES", 3))
COOLDOWN_SEC = int(os.environ.get("COOLDOWN_SEC", 12))
NEED_COMMIT_GB = float(os.environ.get("NEED_COMMIT_GB", 6.0))
HEADROOM_WAIT = int(os.environ.get("HEADROOM_WAIT", 180))
FP16 = os.environ.get("FP16", "1") != "0"


def layout(audio_path):
    d = os.path.dirname(audio_path)
    info = sf.info(audio_path)
    n = math.ceil((info.frames / info.samplerate) / CHUNK_SEC)
    return d, info.samplerate, n


def cf_path(d, i):  return os.path.join(d, f"_chunk_{i}.wav")
def wj_path(d, i):  return os.path.join(d, f"_words_chunk_{i}.json")


def do_one_chunk(audio_path, i):
    """Subprocess entry: transcribe chunk i only, save its words, exit (frees VRAM)."""
    import torch
    import nemo.collections.asr as nemo_asr
    d, sr, n = layout(audio_path)

    cf = cf_path(d, i)
    if not (os.path.exists(cf) and os.path.getsize(cf) > 0):
        wav, _ = sf.read(audio_path, dtype="float32")
        seg = wav[int(i * CHUNK_SEC * sr):int((i + 1) * CHUNK_SEC * sr)]
        sf.write(cf, seg, sr)

    model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v3")
    model.change_attention_model("rel_pos_local_attn", [256, 256])
    model.change_subsampling_conv_chunking_factor(1)
    model = model.to("cuda").eval()
    if FP16:
        # fp32 peaks right at the 6 GB card's free VRAM and OOMs on some chunks
        # (2026-08-24: chunk 8 failed 3/3 in fp32, passed first try in fp16).
        # Halving the weights buys the margin back; ASR quality is unaffected.
        model = model.half()

    off = i * CHUNK_SEC
    out = model.transcribe([cf], timestamps=True)
    words = [{**w, "start": w["start"] + off, "end": w["end"] + off}
             for w in out[0].timestamp["word"]]
    with open(wj_path(d, i), "w", encoding="utf-8") as f:
        json.dump(words, f)
    del model; gc.collect(); torch.cuda.empty_cache()
    print(f"[chunk {i}] {len(words)} words saved", flush=True)


def do_finish(audio_path):
    """Subprocess entry: concat words, diarize, merge, write final outputs."""
    import transcribe as T
    d, sr, n = layout(audio_path)
    words = []
    for i in range(n):
        with open(wj_path(d, i), encoding="utf-8") as f:
            words.extend(json.load(f))
    print(f"[finish] {len(words)} words; running diarization...", flush=True)
    diar = T.diarize(audio_path)
    print(f"[finish] {len(diar)} speaker turns; merging...", flush=True)
    merged = T.assign_speakers(words, diar)
    base = audio_path.rsplit(".", 1)[0]
    with open(base + "_transcript.txt", "w", encoding="utf-8") as f:
        f.write(T.format_transcript(merged))
    with open(base + "_words.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print(f"[finish] wrote {base}_transcript.txt and {base}_words.json", flush=True)


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


def wait_for_headroom(i, attempt):
    """Windows does not release a dead subprocess's ~5 GB of commit instantly; starting
    the next chunk too early raises std::bad_alloc ("RuntimeError: bad allocation") in
    the NeMo preprocessor. Observed 2026-08-24: every run banked exactly one chunk, then
    the second subprocess died. Cool down, then wait for commit to actually come back."""
    time.sleep(COOLDOWN_SEC * attempt)
    deadline = time.time() + HEADROOM_WAIT
    while time.time() < deadline:
        g = free_commit_gb()
        if g is None or g >= NEED_COMMIT_GB:
            if g is not None:
                print(f"[chunk {i}] free commit {g:.1f} GB — proceeding", flush=True)
            return
        print(f"[chunk {i}] free commit {g:.1f} GB < {NEED_COMMIT_GB} GB — waiting", flush=True)
        time.sleep(10)
    print(f"[chunk {i}] headroom wait timed out — proceeding anyway", flush=True)


def orchestrate(audio_path):
    d, sr, n = layout(audio_path)
    print(f"orchestrate: {n} chunks of {CHUNK_SEC}s, isolated subprocess each", flush=True)
    for i in range(n):
        if os.path.exists(wj_path(d, i)):
            print(f"[chunk {i}] already done — skip", flush=True)
            continue
        ok = False
        for attempt in range(1, CHUNK_TRIES + 1):
            wait_for_headroom(i, attempt)
            print(f"[chunk {i}] launching subprocess (try {attempt}/{CHUNK_TRIES})...", flush=True)
            r = subprocess.run([sys.executable, THIS, audio_path, "--chunk", str(i)])
            if r.returncode == 0 and os.path.exists(wj_path(d, i)):
                ok = True
                break
            print(f"[chunk {i}] try {attempt} failed (rc={r.returncode})", flush=True)
        if not ok:
            print(f"[chunk {i}] FAILED after {CHUNK_TRIES} tries. Re-run to resume.", flush=True)
            sys.exit(1)
    # diarization + merge in its own subprocess too (clean VRAM for pyannote)
    print("[finish] launching diarize+merge subprocess...", flush=True)
    r = subprocess.run([sys.executable, THIS, audio_path, "--finish"])
    if r.returncode != 0:
        print(f"[finish] FAILED (rc={r.returncode}).", flush=True); sys.exit(1)
    # cleanup temps
    for i in range(n):
        for p in (cf_path(d, i), wj_path(d, i)):
            if os.path.exists(p):
                os.remove(p)
    print("DONE", flush=True)


if __name__ == "__main__":
    audio = sys.argv[1]
    if "--chunk" in sys.argv:
        do_one_chunk(audio, int(sys.argv[sys.argv.index("--chunk") + 1]))
    elif "--finish" in sys.argv:
        do_finish(audio)
    else:
        orchestrate(audio)
