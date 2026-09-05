# Parakeet TDT + Diarization — Windows Setup (Legion Pro, RTX 3060)

A batch transcription pipeline using NVIDIA Parakeet TDT 0.6b v3 for ASR and
pyannote for speaker diarization. An alternative to the WhisperX pipeline the
`/grade` and `/grade-viva` skills currently use — faster on this GPU, comparable
diarization (same pyannote backbone).

> **Verified working on this machine, 2026-05-22.** Every command, version, and
> code block below was run end-to-end on the Legion Pro and produced a clean
> speaker-labelled transcript from a real student walkthrough video. Where this
> guide departs from a stock Parakeet writeup, the difference is deliberate and
> the reason is given inline.
>
> **Verified stack:** Python 3.12.6 · NeMo 2.7.3 · torch 2.11.0+cu130 ·
> torchaudio 2.11.0+cu130 · pyannote.audio 4.0.4 · driver 596.21.

---

## 1. Prerequisites

Most of these are already in place from the WhisperX setup — verified state in
brackets:

- **Python 3.12** — *[installed: 3.12.6]*. Current NeMo (2.7.x, Feb 2026)
  **requires** Python 3.12+, so 3.12 is correct. **Do not use 3.13** (also
  installed here, and the `py` launcher default) — the ML wheel stack has no
  3.13 builds yet. Always pin the interpreter with `py -3.12`.
- **NVIDIA driver 555+** for modern CUDA wheels — *[installed: 596.21, reports
  CUDA 13.2]*.
- **FFmpeg** on PATH — *[installed: ffmpeg 6.0, the static "essentials" build]*.
  Note the build type: it is a single static `ffmpeg.exe` with **no shared
  DLLs**. That matters in §8.
- **Hugging Face token** for pyannote — *[`HF_TOKEN` is set in the environment]*.
  `huggingface_hub` auto-detects this env var, so no code needs to pass it.
- **Two gated pyannote models must both be accepted** on your HF account
  (one-time, click "Agree" while logged in):
  - https://huggingface.co/pyannote/speaker-diarization-3.1
  - https://huggingface.co/pyannote/segmentation-3.0  ← *easy to miss; the
    diarization pipeline depends on it and fails with a 403 if it is not
    accepted, even when 3.1 is.*
- **Git for Windows** — *[present]*.

**Why a separate venv:** WhisperX 3.8.5 is installed into the **global**
Python 3.12 here (`Python312\Scripts\whisperx.exe`), not a venv. NeMo pulls in a
heavy, version-pinned dependency tree (PyTorch Lightning, OmegaConf, Hydra,
Megatron pieces) that would clash with the faster-whisper stack if installed
globally. Keeping Parakeet in its own venv leaves the existing WhisperX install
untouched.

---

## 2. Environment setup

The venv lives inside this repo at `parakeet-env/` and is git-ignored (see
`.gitignore`). Run everything below from the repo root in PowerShell:

```powershell
cd c:\Users\philo\Projects\teaching-toolkit

# Pin to 3.12 explicitly — the bare `py` launcher defaults to 3.13 here.
py -3.12 -m venv parakeet-env
.\parakeet-env\Scripts\Activate.ps1

python -m pip install --upgrade pip wheel setuptools
```

**Install order matters.** NeMo's dependency resolver will install a
**CPU-only** `torch` and ignore any CUDA build you put down first. So install
NeMo *first*, then overwrite torch with a CUDA build *last*:

```powershell
# 1. NeMo ASR (heavy — several GB, takes a while). This also pulls a CPU-only
#    torch 2.12.0, plus soundfile, librosa, pyannote.core/metrics/database.
#    The CPU torch is expected; step 2 replaces it.
pip install "nemo_toolkit[asr]"

# 2. Replace torch with a CUDA build. torchaudio has no 2.12.x release, so pin
#    the matched 2.11.0 pair (mismatched torch/torchaudio fails to import).
#    cu130 matches the CUDA 13.x driver; NeMo 2.7.3 accepts torch 2.11.0.
pip install "torch==2.11.0" "torchaudio==2.11.0" --index-url https://download.pytorch.org/whl/cu130

# 3. Diarization. pyannote.audio 4.x does not disturb the torch install above.
pip install pyannote.audio
```

`soundfile` and `librosa` are already present (pulled in by NeMo) — no separate
install needed.

**Sanity check** — CUDA must be visible *inside the venv*:

```powershell
python -c "import torch; print(torch.__version__, '| CUDA', torch.cuda.is_available(), '|', torch.cuda.get_device_name(0))"
```

Expected: `2.11.0+cu130 | CUDA True | NVIDIA GeForce RTX 3060 Laptop GPU`.
If the version ends in `+cpu`, something re-installed CPU torch — re-run step 2.

---

## 3. First transcription test

`HF_TOKEN` is already set in your environment, so nothing to do here. If you
ever run from a shell where it is missing:

```powershell
$env:HF_TOKEN = "hf_xxx..."
```

A transcription-only smoke test is committed as `test_parakeet.py`:

```python
import sys
import nemo.collections.asr as nemo_asr

audio = sys.argv[1] if len(sys.argv) > 1 else "test_clip.wav"

asr_model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v3")
asr_model = asr_model.to("cuda").eval()          # .to("cuda") is required — without it inference runs on CPU

output = asr_model.transcribe([audio], timestamps=True)

for s in output[0].timestamp["segment"]:
    print(f"[{s['start']:.2f} - {s['end']:.2f}] {s['segment']}")
```

Run it:

```powershell
python test_parakeet.py test_clip.wav
```

First run downloads the model to `~/.cache/huggingface/hub/` (about 1.2 GB).
`ASRModel.from_pretrained` resolves Parakeet TDT v3 to an `EncDecRNNTBPEModel`.

---

## 4. Video input

Parakeet wants 16 kHz mono WAV — the same format the `/grade` skill already
extracts for WhisperX, so the FFmpeg step is identical:

```powershell
ffmpeg -i lecture.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le lecture.wav
```

For batch:

```powershell
Get-ChildItem *.mp4 | ForEach-Object {
    ffmpeg -i $_.FullName -vn -ac 1 -ar 16000 -c:a pcm_s16le "$($_.BaseName).wav"
}
```

To clip a short section (useful for spot-tests) put `-ss` *before* `-i` for a
fast seek-before-decode jump:

```powershell
ffmpeg -ss 00:01:00 -i lecture.mp4 -t 180 -vn -ac 1 -ar 16000 -c:a pcm_s16le clip.wav
```

---

## 5. Long audio handling on 6 GB VRAM

Parakeet TDT supports long-form natively, but the published 24-minute
full-attention limit assumes an A100 80 GB. **On the 6 GB mobile 3060, a single
pass over long audio OOMs — verified: a 30-minute clip fails with `CUDA out of
memory` even with local attention enabled.** So you need both of the following:

**Step 1 — Enable local attention** (reduces memory; near-lossless for
long-form):

```python
asr_model.change_attention_model("rel_pos_local_attn", [256, 256])
asr_model.change_subsampling_conv_chunking_factor(1)
```

This helps, but on its own is **not** enough for 6 GB — it does not get you to
30 minutes, let alone an hour.

**Step 2 — Chunk anything longer than ~10 minutes.** Split the audio into
fixed-size pieces, transcribe each, and offset the timestamps back to absolute
positions. `benchmark_parakeet.py` is a working implementation — it uses
5-minute chunks and stitches the word and segment timestamps. You lose a little
context at each boundary; in practice that costs a word or two per cut.

> **Superseded 2026-08-24.** 5-minute chunks no longer "sit comfortably inside
> 6 GB". After the torch 2.11.0+cu130 upgrade, a 300 s chunk OOMs outright and
> **180 s in fp16** is the working size. See §7.1. The production script is
> `transcribe_chunked.py`, not `benchmark_parakeet.py`.

`transcribe.py` does **not** chunk — it is fine for the short clips the grading
skills usually handle, but feed it a 30-minute viva and it will OOM. For long
recordings, use the chunked approach from `benchmark_parakeet.py`.

---

## 6. Full pipeline: transcription + diarization + merge

Committed as `transcribe.py`. Three things in it differ from a stock Parakeet +
pyannote example — each is a fix for something that actually broke during
setup (see §8):

1. **pyannote is fed an in-memory waveform**, not a file path — sidesteps the
   torchcodec/FFmpeg-shared-library problem.
2. **The diarization result is read via `DiarizeOutput.exclusive_speaker_diarization`** —
   pyannote.audio 4.x no longer returns a bare `Annotation`.
3. **Word→speaker assignment uses best temporal overlap with a nearest-segment
   fallback** — a strict "midpoint inside a segment" test mislabels every word
   that lands in an inter-segment gap as `UNKNOWN`.

```python
"""Parakeet TDT transcription + pyannote diarization pipeline.

Usage:  python transcribe.py <audio.wav>
Requires the parakeet-env venv to be active.
"""
import os
import sys
import torch
import gc
import soundfile as sf
import nemo.collections.asr as nemo_asr
from pyannote.audio import Pipeline

# Fail fast with a clear message if the token is missing. We don't pass it
# explicitly below — huggingface_hub auto-detects the HF_TOKEN env var.
if not os.environ.get("HF_TOKEN"):
    sys.exit("HF_TOKEN is not set. See parakeet-setup.md section 3.")


def transcribe(audio_path):
    """Run Parakeet, return list of {start, end, word} dicts."""
    model = nemo_asr.models.ASRModel.from_pretrained(
        "nvidia/parakeet-tdt-0.6b-v3"
    )
    model.change_attention_model("rel_pos_local_attn", [256, 256])
    model.change_subsampling_conv_chunking_factor(1)
    model = model.to("cuda").eval()

    output = model.transcribe([audio_path], timestamps=True)
    words = output[0].timestamp["word"]

    # Free VRAM before loading pyannote.
    del model
    gc.collect()
    torch.cuda.empty_cache()

    return words


def diarize(audio_path):
    """Run pyannote, return list of (start, end, speaker) tuples.

    pyannote.audio 4.x decodes files via torchcodec, which needs FFmpeg *shared*
    libraries that the static 'essentials' FFmpeg build does not ship. Since the
    pipeline input is always a 16 kHz mono WAV, we sidestep torchcodec entirely:
    load the audio with soundfile and hand pyannote an in-memory waveform.
    """
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    pipeline.to(torch.device("cuda"))

    wav, sr = sf.read(audio_path, dtype="float32")
    waveform = torch.from_numpy(wav).unsqueeze(0)  # (1, samples) — mono
    diar = pipeline({"waveform": waveform, "sample_rate": sr})

    # pyannote.audio 4.x returns a DiarizeOutput, not a bare Annotation.
    # exclusive_speaker_diarization has overlapping speech removed — each
    # instant maps to exactly one speaker, which is what word assignment wants.
    annotation = diar.exclusive_speaker_diarization

    segments = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        segments.append((turn.start, turn.end, speaker))
    return segments


def assign_speakers(words, diar_segments):
    """Assign each word to a speaker by best temporal overlap.

    Diarization segments are not gapless — exclusive diarization in particular
    leaves gaps where overlapping speech was trimmed out. A strict "is the
    midpoint inside a segment" test marks every word that lands in a gap as
    UNKNOWN, which shreds a single-speaker transcript. Instead: pick the segment
    the word overlaps most, and if it overlaps none, snap to the nearest one.
    """
    if not diar_segments:
        return [{**w, "speaker": "UNKNOWN"} for w in words]

    out = []
    for w in words:
        ws, we = w["start"], w["end"]
        best_spk, best_overlap = None, 0.0
        for s_start, s_end, spk in diar_segments:
            overlap = min(we, s_end) - max(ws, s_start)
            if overlap > best_overlap:
                best_overlap, best_spk = overlap, spk

        if best_spk is None:
            # Word fell entirely in a gap — snap to the nearest segment.
            mid = (ws + we) / 2
            best_spk = min(
                diar_segments,
                key=lambda s: min(abs(mid - s[0]), abs(mid - s[1])),
            )[2]

        out.append({**w, "speaker": best_spk})
    return out


def format_transcript(words):
    """Group consecutive same-speaker words into readable blocks."""
    lines = []
    if not words:
        return ""

    cur_speaker = words[0]["speaker"]
    cur_start = words[0]["start"]
    cur_words = []

    for w in words:
        if w["speaker"] != cur_speaker:
            text = " ".join(cur_words)
            lines.append(f"[{cur_start:.2f}] {cur_speaker}: {text}")
            cur_speaker = w["speaker"]
            cur_start = w["start"]
            cur_words = []
        cur_words.append(w["word"])

    text = " ".join(cur_words)
    lines.append(f"[{cur_start:.2f}] {cur_speaker}: {text}")
    return "\n".join(lines)


if __name__ == "__main__":
    audio = sys.argv[1]
    print(f"Transcribing {audio}...")
    words = transcribe(audio)
    print(f"Got {len(words)} words. Running diarization...")
    diar = diarize(audio)
    print(f"Got {len(diar)} speaker turns. Merging...")
    merged = assign_speakers(words, diar)

    transcript = format_transcript(merged)
    out_path = audio.rsplit(".", 1)[0] + "_transcript.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"Wrote {out_path}")
```

Run it (venv must be active):

```powershell
python transcribe.py lecture.wav
```

---

## 7. VRAM strategy on 6 GB

The 3060 here shares VRAM with the Windows desktop — at idle roughly **1.5–2 GB
is already in use**, leaving ~4–4.5 GB free. The pipeline above accounts for
this: it loads Parakeet, transcribes, frees the model, **then** loads pyannote.
Running both simultaneously will OOM. Each model fits alone in the remaining
headroom for short clips — but Parakeet's *activation* memory scales with audio
length, so a long single pass OOMs regardless of how little else is loaded
(see §5: a 30-minute pass fails). Chunk long audio.

If you hit OOM:

- For long audio, chunk it — this is the real fix (§5).
- Close GPU-heavy apps and re-check headroom with `nvidia-smi`.
- Drop Parakeet to FP16 explicitly: `model = model.half()` after `.to("cuda")`.
  **As of 2026-08-24 this is no longer optional** — `transcribe_chunked.py` does
  it by default (`FP16=0` to opt out). fp32 OOMs on real 180 s chunks.
- The pyannote diarization-3.1 footprint is around 1.5 GB — usually fine alone.

---

### 7.1 The torch 2.11.0+cu130 regression (investigated 2026-08-24)

A 57-minute class that previously ran unattended took ~3 hours and needed two
chunks rescued by hand. Measured facts, so the next person does not re-derive
them:

- Peak allocation is **~5.06 GB** against **~5.27 GB free** on an idle desktop.
  That margin is thinner than the run-to-run variance, which is why failures
  look random.
- **Chunk length ceiling**: 300 s fails, **240 s passes**, 150 s passes. The
  default is now 180 s for margin. Peak allocation barely moves with chunk
  length (60 s and 150 s both report 5.06 GB), so the ceiling is a transient
  inside the encoder, not steady-state weight memory.
- **Chrome costs ~250 MB of VRAM** (desktop use 707 MB closed → 945 MB open).
  That is the entire margin. One failure was 20 MiB short. Close it.
- **`expandable_segments:True` is silently ignored on Windows** — torch emits
  `UserWarning: expandable_segments not supported on this platform` and carries
  on. Any advice to set it (including older notes in this repo) is inert here.
- **CUDA-graph decoding** in the TDT label-looping decoder pre-allocates a
  static buffer and is where 300 s chunks die
  (`tdt_label_looping._warmup_for_cuda_graphs`). Disabling it via
  `cfg.greedy.use_cuda_graph_decoder = False` works but was **not** needed once
  chunks dropped to 180 s — 150 s passes with graphs enabled.
- **`change_subsampling_conv_chunking_factor(-1)` did not help** a stuck chunk,
  despite being the knob nominally aimed at this. Tried at -1 and 4; both failed
  where fp16 succeeded.

**Context churn is a separate failure from VRAM.** With a 12 s gap between chunk
subprocesses, exactly one chunk per orchestrator process succeeded and the next
died. At 45 s, four consecutive chunks succeeded before degrading. A *fresh
orchestrator* resets it. So the shape that works is: cooldown between chunks,
retries per chunk, and an outer loop that restarts the whole orchestrator —
`transcribe_chunked.py` now does the first two, and the caller supplies the third.

**Two chunks failed even alone on a rested GPU.** For those, `rescue_chunk.py`
re-cuts the chunk into 60 s slices and runs each in its own subprocess. Both
went through first try. The important detail: **retrying a failed slice inside
the same process hangs forever** — after a CUDA OOM the context is dead, and the
next `transcribe()` blocks rather than raising. Every retry needs a new process.

**Reading the errors.** Only the first traceback in a subprocess is real. NeMo's
`TemporaryDirectory` cleanup throws `PermissionError: [WinError 32] ...
manifest.json` while unwinding, which lands *last* and hides the cause. And
`CUDA error: unknown error` / `CUBLAS_STATUS_EXECUTION_FAILED` / `RuntimeError:
bad allocation` are all downstream wreckage of an earlier OOM in the same
process — not independent bugs. `bad allocation` in particular reads like host
memory exhaustion but fired here with 8.8 GB of commit free.

---

## 8. Known rough edges (all hit during this setup)

- **NeMo overrides torch with a CPU build.** Covered in §2 — install NeMo
  first, CUDA torch last, and verify `torch.cuda.is_available()` at the end.
- **torchcodec can't find FFmpeg shared libraries.** pyannote.audio 4.x decodes
  audio files through `torchcodec`, whose `libtorchcodec_core{4,5,6,7}.dll`
  link against FFmpeg's *shared* libraries (`avcodec-*.dll`, etc.). The static
  "essentials" FFmpeg build on this machine has none of those, so torchcodec
  fails to load with `Could not find module ... (or one of its dependencies)`.
  `transcribe.py` avoids the whole problem by decoding the WAV with `soundfile`
  and passing pyannote an in-memory waveform. The torchcodec import still prints
  a warning — harmless, because we never call the file-decode path. If you ever
  need torchcodec to work directly (e.g. to feed pyannote a non-WAV file), install
  an FFmpeg *shared* build and put its `bin/` on PATH.
- **pyannote.audio 4.x changed the pipeline return type.** It returns a
  `DiarizeOutput` (fields: `speaker_diarization`, `exclusive_speaker_diarization`,
  `speaker_embeddings`), not an `Annotation`. Call `.itertracks()` on one of the
  annotation fields, not on the result directly.
- **Speaker assignment and diarization gaps.** `exclusive_speaker_diarization`
  removes overlapping speech, which leaves small gaps between turns. Assign each
  word by maximum overlap with a nearest-segment fallback, never by strict
  midpoint containment — otherwise every word in a gap becomes `UNKNOWN`.
- **First model load is slow; throughput varies.** NeMo does a lot of init
  work. On this laptop GPU (power-capped, shares thermal budget with the CPU)
  the same 3-minute clip transcribed in ~14 s on one run and ~68 s on another —
  expect that spread.
- **`nemo_toolkit[asr]` on Windows** may warn about `pynini` /
  `nemo_text_processing`. Safe to ignore (or uninstall) — only needed for
  inverse text normalization in TTS.
- **Word timestamps from TDT** can drift a few hundred ms at segment
  boundaries. Fine for speaker assignment, not for tight word-level subtitling.

---

## 9. Test results on this machine

### Pipeline smoke test (3-minute clip)

End-to-end `transcribe.py` run on a 3-minute clip from a real student
walkthrough video (single speaker):

| Stage | Result |
|-------|--------|
| Transcription | 387–388 words, clean readable text incl. disfluencies |
| Diarization | 35 turns, correctly all one speaker (`SPEAKER_00`) |
| Merge | 0 `UNKNOWN` words after the overlap-based fix |

### Parakeet vs. WhisperX — 30-minute benchmark

Same 30-minute audio (`bench_30min.wav`, a student walkthrough) through both
engines, transcription only, RTX 3060 6 GB. Parakeet via `benchmark_parakeet.py`
(6 × 5-min chunks); WhisperX 3.8.5 via the `/grade` command
(`--model large-v3 --device cuda --compute_type int8`, default alignment on).

| | Parakeet TDT 0.6b | WhisperX large-v3 (int8) |
|---|---|---|
| **Total wall-clock** | **85 s** | **223 s** |
| ↳ model load | 21 s | included |
| ↳ transcription | 44 s | ~126 s |
| ↳ other | ~20 s chunk I/O | ~alignment + VAD |
| Real-time factor (total) | ~21× | ~8× |
| Real-time factor (transcription only) | ~41× | ~14× |
| Words produced | 4098 | 3935 |
| Segments | 91 | 95 |
| Segment length (min / max / median) | 0.8 / **283** / 8.6 s | 0.8 / 30 / 23 s |
| Long audio in one pass | **no — OOMs, must chunk** | yes, handled natively |

**Speed:** Parakeet is **~2.6× faster end-to-end** (~2.8× on transcription
alone) on this hardware.

**Accuracy:** no ground-truth transcript exists, so no WER — but the two
outputs are near-identical on a spot-check (word counts within ~4 %, same
content, even the same mistakes, e.g. both mishear the same uncommon surname). For
classroom audio, treat them as equivalent in word accuracy.

**Segmentation — the real difference:** WhisperX produces uniform, readable
segments (capped ~30 s). Parakeet's *segment* timestamps are bimodal — mostly
short, but **4 segments run over a minute, one a 283-second wall of text** with
no sentence breaks, because TDT only splits on clear pauses. Parakeet's
*word-level* timestamps are fine (4098 individually-timed words), so citing "(at
12:34) the student said…" works either way — but if you display Parakeet's
segment transcript to a human, or build segment-based feedback, you will want to
re-segment its word stream yourself (split on word-gap > ~0.7 s).

**Diarization** was not separately benchmarked — both pipelines use the same
pyannote 3.1 backbone, so quality is equivalent by construction.

### Verdict

For the grading skills: Parakeet is the better **speed-critical batch**
transcriber — 2.6× faster, equivalent word accuracy, native word timestamps.
WhisperX stays the better choice when you want **readable segment transcripts
out of the box** and **no chunking ceremony** on long recordings. A practical
split: Parakeet for bulk walkthrough transcription, WhisperX for long vivas and
anything a human will read raw.

---

## 10. Optional: swap pyannote for Sortformer

If you want to try NVIDIA's newer Sortformer diarization (better DER in their
benchmarks), it's available in NeMo:

```python
from nemo.collections.asr.models import SortformerEncLabelModel

diar_model = SortformerEncLabelModel.from_pretrained(
    "nvidia/diar_sortformer_4spk-v1"
)
diar_model = diar_model.to("cuda").eval()
```

Caveats: it's currently capped at 4 speakers, and the output format differs
from pyannote's, so you'd rewrite `diarize()` and `assign_speakers()`. Worth
trying once the pyannote baseline works — which, as of §9, it does.
