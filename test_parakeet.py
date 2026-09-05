"""Transcription-only smoke test for Parakeet TDT (no diarization).

Usage:  python test_parakeet.py [audio.wav]
Proves the ASR half of the pipeline works independently of pyannote.
See parakeet-setup.md section 3.
"""
import sys
import nemo.collections.asr as nemo_asr

audio = sys.argv[1] if len(sys.argv) > 1 else "test_clip.wav"

asr_model = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v3")
asr_model = asr_model.to("cuda").eval()  # required — without it inference runs on CPU

output = asr_model.transcribe([audio], timestamps=True)

for s in output[0].timestamp["segment"]:
    print(f"[{s['start']:.2f} - {s['end']:.2f}] {s['segment']}")
