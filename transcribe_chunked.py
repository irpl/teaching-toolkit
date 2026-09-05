"""Chunked Parakeet TDT + pyannote pipeline — thin wrapper over asr.py.

Kept for its existing callers and muscle memory. All the logic now lives in
asr.py (chunk sizing, worker isolation, resume, retries, diarization); this
file only preserves the historical entry point and its default of always
diarizing.

Usage:  python transcribe_chunked.py <audio_16k_mono.wav>
Writes: <audio>_transcript.txt and <audio>_words.json  (speaker-labelled)
        plus <audio>.txt / .srt / .json  (readable segments)

For transcription only — ~230 s faster per 30 min of audio, and the right
choice for single-speaker walkthroughs — use asr.py directly:
    python asr.py <audio.wav>
"""
import sys
import asr

if __name__ == "__main__":
    asr.ensure_venv()
    audio = sys.argv[1]
    words = asr.transcribe(audio)
    asr.write_media_outputs(audio, words)
    asr._diarize_subprocess(audio, words, asr._arg("--speakers", int))
    print("DONE", flush=True)
