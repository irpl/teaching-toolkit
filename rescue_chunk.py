"""Rescue one stuck pipeline chunk by transcribing it in smaller sub-slices,
each in its OWN subprocess (a dead CUDA context cannot be retried in-process --
the retry blocks forever). Writes the pipeline's _words_chunk_<i>.json.

  orchestrate:  rescue_chunk.py <i> [sub_sec]
  one slice:    rescue_chunk.py <i> <sub_sec> --sub <j>
"""
import os, sys, json, time, subprocess
import soundfile as sf

THIS = os.path.abspath(__file__)
CHUNK_SEC = 180
D = "D:/Videos/uwi/2026"
TMP = "D:/nemo_tmp"


def slice_paths(i, sub):
    wav, sr = sf.read(f"{D}/_chunk_{i}.wav", dtype="float32")
    n = -(-len(wav) // (sub * sr))
    out = []
    for j in range(n):
        p = f"{TMP}/_resc_{i}_{j}.wav"
        if not os.path.exists(p):
            sf.write(p, wav[j*sub*sr:(j+1)*sub*sr], sr)
        out.append(p)
    return out


def do_sub(i, sub, j):
    import torch, nemo.collections.asr as nemo_asr
    p = slice_paths(i, sub)[j]
    m = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v3")
    m.change_attention_model("rel_pos_local_attn", [256, 256])
    m.change_subsampling_conv_chunking_factor(1)
    m = m.to("cuda").eval().half()
    off = i * CHUNK_SEC + j * sub
    out = m.transcribe([p], timestamps=True)
    words = [{**w, "start": w["start"] + off, "end": w["end"] + off}
             for w in out[0].timestamp["word"]]
    with open(f"{TMP}/_resc_words_{i}_{j}.json", "w", encoding="utf-8") as f:
        json.dump(words, f)
    print(f"  sub {j}: {len(words)} words (t+{off}s)", flush=True)


def orchestrate(i, sub):
    paths = slice_paths(i, sub)
    print(f"chunk {i}: {len(paths)} sub-slices of {sub}s", flush=True)
    for j in range(len(paths)):
        wj = f"{TMP}/_resc_words_{i}_{j}.json"
        if os.path.exists(wj):
            print(f"  sub {j}: already done", flush=True)
            continue
        for attempt in range(1, 6):
            r = subprocess.run([sys.executable, THIS, str(i), str(sub), "--sub", str(j)])
            if r.returncode == 0 and os.path.exists(wj):
                break
            print(f"  sub {j} try {attempt} failed (rc={r.returncode})", flush=True)
            time.sleep(30)
        else:
            print(f"  sub {j}: GAVE UP", flush=True)
            sys.exit(1)
    words = []
    for j in range(len(paths)):
        with open(f"{TMP}/_resc_words_{i}_{j}.json", encoding="utf-8") as f:
            words.extend(json.load(f))
    with open(f"{D}/_words_chunk_{i}.json", "w", encoding="utf-8") as f:
        json.dump(words, f)
    print(f"chunk {i}: {len(words)} words saved", flush=True)


if __name__ == "__main__":
    i = int(sys.argv[1])
    sub = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else 60
    if "--sub" in sys.argv:
        do_sub(i, sub, int(sys.argv[sys.argv.index("--sub") + 1]))
    else:
        orchestrate(i, sub)
