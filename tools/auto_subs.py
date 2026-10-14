#!/usr/bin/env python3
"""Auto captions from Mustafa's own words (no speech recognition of Darija needed).

  python3 tools/auto_subs.py videos/reel4.mov script.txt > subs/reel4.srt

script.txt = what he says, plain text (mark the key word of a phrase with *stars*, tags like [flash] allowed).
Method: detect speech spans in the audio (silence detection), spread the words across the spoken time in
proportion to word length, group them in chunks of 1-3 words (short words stick together).
Timings are approximate (+-0.2s) -> always eyeball the result and tweak the .srt if needed.
"""
import json, os, re, subprocess, sys

def speech_spans(path, noise="-32dB", min_sil=0.30):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                               capture_output=True, text=True).stdout)
    err = subprocess.run(["ffmpeg", "-i", path, "-af", f"silencedetect=n={noise}:d={min_sil}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    spans, cur = [], 0.0
    for i, s in enumerate(starts):
        if s - cur > 0.15:
            spans.append((cur, s))
        cur = ends[i] if i < len(ends) else dur
    if dur - cur > 0.15:
        spans.append((cur, dur))
    return spans or [(0.0, dur)]

def tokens(text):
    out, pending_tags = [], []
    for raw in text.split():
        if re.fullmatch(r"\[[^\]]+\]", raw) or not re.search(r"\w", raw):  # tags / emoji stick to the previous word
            if out: out[-1] += " " + raw
            continue
        out.append(raw)
    return out

def chunks(words, max_words=3):
    res, cur = [], []
    for w in words:
        plain = re.sub(r"[*\[\]]|\s.*", "", w)
        cur.append(w)
        if max_words == 1 and len(plain) <= 2:   # tiny words (FL, EL, F, W...) ride with the next word
            continue
        if len(cur) >= max_words or (max_words > 1 and len(cur) >= 2 and len(plain) >= 5) or re.search(r"[.!?؟،,]$", plain):
            res.append(cur); cur = []
    if cur:
        if res and len(cur) == 1 and len(re.sub(r"[*]", "", cur[0])) <= 3:
            res[-1] += cur
        else:
            res.append(cur)
    return res

def ts(t):
    return f"{int(t//3600):02d}:{int(t%3600//60):02d}:{int(t%60):02d},{int(t%1*1000):03d}"

def word_timeline(video):
    """Real word onsets from tools/transcribe.py (subs/<name>.words.json), else None."""
    name = re.sub(r"\.[^.]+$", "", os.path.basename(video))
    p = os.path.join("subs", name + ".words.json")
    if not os.path.exists(p):
        return None
    w = json.load(open(p, encoding="utf-8"))
    return ([x["start"] for x in w], [x["end"] for x in w]) if len(w) >= 2 else None


def interp(arr, pos):
    i = int(pos); f = pos - i
    return arr[i] if i >= len(arr) - 1 else arr[i] + (arr[i + 1] - arr[i]) * f


def main():
    video, script = sys.argv[1], open(sys.argv[2], encoding="utf-8").read()
    maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 3   # optional 3rd arg: max words per caption (1 = word-by-word)
    lines = [l for l in script.splitlines() if l.strip()]   # each line of the script is its own phrase: captions never cross a line break
    cs = [c for l in lines for c in chunks(tokens(l), maxw)]
    tl = word_timeline(video)
    if tl:
        starts, ends = tl
        allw = [w for l in lines for w in tokens(l)]
        n, m = len(allw), len(starts)
        # i-th corrected word <-> same relative position in Whisper's real word timeline
        t_of = lambda i: interp(starts, i * (m - 1) / max(n - 1, 1))
        idx, out = 0, []
        for c in cs:
            a = t_of(idx); idx += len(c)
            b = t_of(idx) if idx < n else ends[-1]
            out.append((a, max(b, a + 0.4), " ".join(c)))
        for i, (a, b, t) in enumerate(out, 1):
            nxt = out[i][0] if i < len(out) else b
            print(f"{i}\n{ts(a)} --> {ts(min(b, nxt - 0.03) if nxt - 0.03 > a + 0.3 else b)}\n{t}\n")
        return
    spans = speech_spans(video)
    total_speech = sum(b - a for a, b in spans)
    weight = lambda w: max(len(re.sub(r"[*]|\[[^\]]+\]", "", w)), 2) + 1.5
    wt = [sum(weight(w) for w in c) for c in cs]
    per_sec = sum(wt) / total_speech
    # walk through speech spans consuming chunk durations
    si, pos, out = 0, spans[0][0], []
    for n, c in enumerate(cs, 1):
        need = wt[n - 1] / per_sec
        start = pos
        while need > 1e-6:
            a, b = spans[si]
            take = min(need, b - pos)
            pos += take; need -= take
            if pos >= b - 1e-6 and si < len(spans) - 1:
                si += 1; pos = spans[si][0]
        out.append((start, pos, " ".join(c)))
    for i, (a, b, t) in enumerate(out, 1):
        nxt = out[i][0] if i < len(out) else b
        end = min(max(b, a + 0.5), nxt - 0.03) if nxt > a + 0.55 else b
        print(f"{i}\n{ts(a)} --> {ts(end)}\n{t}\n")

if __name__ == "__main__":
    main()
