"""Timed Parakeet TDT transcription run for the WhisperX side-by-side.

Transcribes in fixed-size chunks — a single 30-min pass OOMs on the 6 GB 3060
even with local attention, so chunking is mandatory on this hardware.

Usage:  python benchmark_parakeet.py <audio.wav>
"""
import math
import os
import sys
import time
import torch
import soundfile as sf
import nemo.collections.asr as nemo_asr

audio = sys.argv[1]
CHUNK_SEC = 300  # 5-minute chunks — comfortably inside 6 GB VRAM

t0 = time.time()
model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v3")
model.change_attention_model("rel_pos_local_attn", [256, 256])
model.change_subsampling_conv_chunking_factor(1)
model = model.to("cuda").eval()
t_load = time.time() - t0

wav, sr = sf.read(audio, dtype="float32")
total_sec = len(wav) / sr
n_chunks = math.ceil(total_sec / CHUNK_SEC)

t1 = time.time()
all_words, all_segs, tmp_files = [], [], []
for i in range(n_chunks):
    offset = i * CHUNK_SEC
    chunk = wav[int(offset * sr):int((offset + CHUNK_SEC) * sr)]
    cf = f"bench_chunk_{i}.wav"
    sf.write(cf, chunk, sr)
    tmp_files.append(cf)

    out = model.transcribe([cf], timestamps=True)
    for w in out[0].timestamp["word"]:
        all_words.append({**w, "start": w["start"] + offset, "end": w["end"] + offset})
    for s in out[0].timestamp["segment"]:
        all_segs.append({**s, "start": s["start"] + offset, "end": s["end"] + offset})
    torch.cuda.empty_cache()
    print(f"  chunk {i + 1}/{n_chunks} done")
t_infer = time.time() - t1

for cf in tmp_files:
    os.remove(cf)

with open("bench_parakeet_transcript.txt", "w", encoding="utf-8") as f:
    for s in all_segs:
        f.write(f"[{s['start']:.2f} - {s['end']:.2f}] {s['segment']}\n")

print(f"\nPARAKEET_RESULT audio={total_sec:.0f}s chunks={n_chunks} "
      f"load={t_load:.1f}s infer={t_infer:.1f}s "
      f"words={len(all_words)} segments={len(all_segs)}")
