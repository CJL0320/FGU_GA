#!/usr/bin/env python3
"""Designed sound effects for Mustafa's reels (no downloads, royalty-free, synthesized with numpy).
Soft and modern, so they support the voice without covering it:
  pop     caption appears      bubble sweep + tiny transient + short room
  sparkle icon appears         3 quick bell notes, airy shimmer, stereo spread
  swoosh  b-roll enters (once) noise through a moving band-pass, panned left -> right
  hit     hook (start)         soft deep hit: falling sine + muffled transient + tail
  chime   end card             C-E-G bell arpeggio with reverb
  python3 tools/sfx_pro.py OUT_DIR      -> writes the .wav files (48 kHz stereo)
"""
import math, os, sys, wave
import numpy as np

SR = 48000


def _env(n, attack=0.004, decay=10.0):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1) if attack > 0 else 1
    return a * np.exp(-t * decay)


def _reverb(x, room=0.25, decay=2.2, wet=0.25, seed=1):
    """Tiny convolution reverb (exponentially decaying noise impulse)."""
    rng = np.random.default_rng(seed)
    n = int(SR * room * decay)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * room / 3))
    ir /= np.sqrt((ir ** 2).sum()) + 1e-9
    y = np.convolve(x, ir)[: len(x) + n]
    out = np.zeros(len(y)); out[: len(x)] = x
    return out + wet * y


def _stereo(x, pan=0.0, width=0.0, seed=2):
    """pan -1..1 (can be an array), width = decorrelated delay spread."""
    pan = np.broadcast_to(np.asarray(pan, float), x.shape)
    l = x * np.cos((pan + 1) * math.pi / 4)
    r = x * np.sin((pan + 1) * math.pi / 4)
    if width:
        d = int(SR * 0.008 * width)
        r = np.concatenate([np.zeros(d), r])[: len(r)]
    return np.stack([l, r], 1)


def _norm(s, peak=0.9):
    m = np.abs(s).max() + 1e-9
    return s * (peak / m)


def _lp(x, fc):
    """One-pole low-pass (fc in Hz, scalar)."""
    a = math.exp(-2 * math.pi * fc / SR)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y


def pop():
    n = int(SR * 0.16); t = np.arange(n) / SR
    f = 520 + 900 * (1 - np.exp(-t * 45))                       # bubble rises quickly then settles
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(n, 0.003, 32)
    rng = np.random.default_rng(3)
    tick = _lp(rng.standard_normal(n), 5000) * _env(n, 0.0005, 260) * 0.5
    x = _reverb(body + tick, room=0.12, wet=0.18)
    return _norm(_stereo(x, 0, 0.6), 0.8)


def sparkle():
    n = int(SR * 0.9); x = np.zeros(n); t = np.arange(n) / SR
    for k, (f, start) in enumerate([(2093, 0.0), (2637, 0.045), (3136, 0.09)]):
        s = int(start * SR); tt = t[: n - s]
        tone = (np.sin(2 * math.pi * f * tt) + 0.35 * np.sin(2 * math.pi * f * 2.76 * tt) + 0.15 * np.sin(2 * math.pi * f * 5.4 * tt))
        x[s:] += tone * _env(n - s, 0.002, 9 + 3 * k) * (0.9 - 0.15 * k)
    rng = np.random.default_rng(4)
    air = rng.standard_normal(n); air = air - _lp(air, 6000)        # high shimmer
    x += air * _env(n, 0.01, 14) * 0.08
    x = _reverb(x, room=0.3, wet=0.35)
    pan = np.linspace(-0.25, 0.35, len(x))
    return _norm(_stereo(x, pan, 1.0), 0.75)


def swoosh(dur=0.55):
    n = int(SR * dur); t = np.arange(n) / SR
    rng = np.random.default_rng(5)
    noise = rng.standard_normal(n)
    # moving band-pass: state-variable filter with centre sweeping 300 -> 3500 -> 1200 Hz
    fc = 300 + 3200 * np.sin(math.pi * np.clip(t / dur, 0, 1)) ** 1.5
    q = 2.2; low = band = 0.0; y = np.empty(n)
    for i in range(n):
        f = 2 * math.sin(math.pi * fc[i] / SR)
        high = noise[i] - low - band / q
        band += f * high; low += f * band; y[i] = band
    amp = np.sin(math.pi * np.clip(t / dur, 0, 1)) ** 2
    x = _reverb(y * amp, room=0.2, wet=0.2)
    pan = np.linspace(-0.8, 0.8, len(x))
    return _norm(_stereo(x, pan, 0.8), 0.7)


def hit():
    n = int(SR * 0.9); t = np.arange(n) / SR
    f = 45 + 55 * np.exp(-t * 18)
    body = np.sin(2 * math.pi * np.cumsum(f) / SR) * _env(n, 0.002, 5.5)
    rng = np.random.default_rng(6)
    thump = _lp(rng.standard_normal(n), 900) * _env(n, 0.001, 60) * 0.7
    x = _reverb(body + thump, room=0.35, wet=0.3)
    return _norm(_stereo(x, 0, 0.4), 0.85)


def chime():
    n = int(SR * 2.2); x = np.zeros(n); t = np.arange(n) / SR
    for k, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):          # C6 E6 G6 C7
        s = int(k * 0.09 * SR); tt = t[: n - s]
        tone = np.sin(2 * math.pi * f * tt) + 0.3 * np.sin(2 * math.pi * f * 3.01 * tt)
        x[s:] += tone * _env(n - s, 0.003, 3.2) * (1 - 0.12 * k)
    x = _reverb(x, room=0.45, wet=0.4)
    pan = np.linspace(-0.3, 0.3, len(x))
    return _norm(_stereo(x, pan, 1.0), 0.7)


SOUNDS = {"pop": pop, "sparkle": sparkle, "swoosh": swoosh, "hit": hit, "chime": chime}


def write(path, st):
    st = np.clip(st, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


def make_all(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for name, fn in SOUNDS.items():
        p = os.path.join(out_dir, f"pro_{name}.wav"); write(p, fn()); paths[name] = p
    return paths


if __name__ == "__main__":
    print(make_all(sys.argv[1] if len(sys.argv) > 1 else "."))
