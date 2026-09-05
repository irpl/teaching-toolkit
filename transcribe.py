"""Parakeet TDT transcription + pyannote diarization pipeline.

Usage:  python transcribe.py <audio.wav>
See parakeet-setup.md for setup. Requires the parakeet-env venv to be active.
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
