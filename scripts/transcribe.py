"""Gera legendas (JSON pro Remotion) a partir da sua voz, com faster-whisper.
Uso: python3 scripts/transcribe.py audio/voz/voz.wav src/captions.json
"""
import json, sys
from faster_whisper import WhisperModel

src, dst = sys.argv[1], sys.argv[2]
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, _ = model.transcribe(src, language="pt", word_timestamps=True)
caps = [
    {"text": w.word.strip(), "startMs": int(w.start * 1000), "endMs": int(w.end * 1000)}
    for s in segments for w in (s.words or [])
]
json.dump(caps, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{len(caps)} palavras -> {dst}")
