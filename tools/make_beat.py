#!/usr/bin/env python3
"""Royalty-free background beat synthesised from scratch (no downloads, no copyright issues).

  python3 tools/make_beat.py out.wav SECONDS [BPM]
Kick on 1 & 3, clap on 2 & 4, offbeat hats, sub-bass on an A-minor loop. Calm, modern, sits under a voice.
"""
import sys, wave
import numpy as np

SR = 48000

def env(n, a=0.002, d=0.25):
    t = np.arange(n) / SR
    e = np.minimum(t / a, 1.0) * np.exp(-t / d)
    return e

def kick(n):
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.18)

def clap(n):
    return np.random.default_rng(1).normal(0, 1, n) * env(n, 0.001, 0.07) * 0.5

def hat(n):
    x = np.random.default_rng(2).normal(0, 1, n)
    x = np.diff(np.concatenate([[0], x]))  # crude high-pass
    return x * env(n, 0.0005, 0.025) * 0.25

def bass(n, freq):
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * env(n, 0.01, 0.5) * 0.45

def main():
    out, secs = sys.argv[1], float(sys.argv[2])
    bpm = float(sys.argv[3]) if len(sys.argv) > 3 else 100
    beat = 60 / bpm
    n = int(secs * SR)
    mix = np.zeros(n + SR)
    notes = [55.0, 43.65, 49.0, 41.2]  # A1 F1 G1 E1
    b = 0
    while b * beat < secs:
        i = int(b * beat * SR)
        L = int(beat * SR)
        if b % 2 == 0:
            mix[i:i + L] += kick(L)
        else:
            mix[i:i + L] += clap(L)
        h = i + L // 2
        mix[h:h + L // 2] += hat(L // 2)
        if b % 4 == 0:
            BL = int(4 * beat * SR)
            seg = bass(BL, notes[(b // 4) % 4])
            mix[i:i + BL] += seg[:len(mix[i:i + BL])]
        b += 1
    mix = mix[:n]
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.8
    st = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())

if __name__ == "__main__":
    main()
