#!/usr/bin/env python3
"""Draft transcript + REAL word timings from the audio (Whisper large-v3, CPU, ~1 min).

  python3 tools/transcribe.py videos/reel2.mov            -> subs/reel2.draft.txt  (one phrase per line, Arabic script, to be corrected)
                                                              subs/reel2.words.json (word start/end seconds)
Whisper understands Algerian Darija only partly (it got "confiance", "قدامك"...), so the TEXT is a draft that
Mustafa corrects; the TIMINGS are reliable and tools/auto_subs.py uses them when subs/<name>.words.json exists.
Needs: pip install faster-whisper (first run downloads ~3GB model).
"""
import json, os, re, sys
from faster_whisper import WhisperModel

video = sys.argv[1]
name = re.sub(r"\.[^.]+$", "", os.path.basename(video))
os.makedirs("subs", exist_ok=True)
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = m.transcribe(video, language="ar", word_timestamps=True, vad_filter=True, beam_size=5,
                          initial_prompt="كلام بالدارجة الجزائرية عن التجارة الإلكترونية والبيع والمنتج والثقة")
words, phrases = [], []
for s in segs:
    for w in s.words:
        t = w.word.strip()
        if t:
            words.append({"w": t, "start": round(w.start, 3), "end": round(w.end, 3)})
    phrases.append(s.text.strip())
json.dump(words, open(f"subs/{name}.words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# split long text into short lines (~4 words) so it is easy to edit
lines, cur = [], []
for w in words:
    cur.append(w["w"])
    if len(cur) >= 4:
        lines.append(" ".join(cur)); cur = []
if cur: lines.append(" ".join(cur))
open(f"subs/{name}.draft.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"{len(words)} words, duration {info.duration:.1f}s -> subs/{name}.draft.txt + subs/{name}.words.json")
