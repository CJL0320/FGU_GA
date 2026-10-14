#!/usr/bin/env python3
""""Reference reel" layer (the look Mustafa liked, 2026-10-09) on top of a reel made by edit_reel.py.
Adds, at times given on the SOURCE timeline (mapped through the silence cut with --dump-timeline):
  phone  : full-frame split — bokeh bg, tilted 3D phone playing a clip, his face shrinking into a PIP + neon label
  card   : glass card with a counter that counts up (only real figures he says in the video)
  search : search bar whose text types itself (typewriter) + keyboard clicks
  cta    : WhatsApp / Instagram / Partage pills popping one by one at the very end
SFX: swoosh on each phone split, sparkle on its label, pop on cards and pills, typing clicks. No music.

  python3 tools/ref_style.py base.mp4 timeline.json plan.json out.mp4
plan.json: {"phone": [[a, b, "clip.mp4", "label"]], "card": [[a, b, "TITLE", 80, "sub", x, y]],
            "search": [[a, b, "text", y]], "cta": {"items": [...], "dur": 3.5, "y": 1250}}
"""
import glob, json, os, shutil, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit_reel as E
import sfx_pro

FPS = 30
PUB = os.path.join(E.REMOTION, "public", "ref")


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def rm(comp, out, props, alpha=False):
    chrome = (glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell") or [None])[0]
    cmd = ["npx", "remotion", "render", "src/index.ts", comp, os.path.abspath(out), "--log=error",
           "--props=" + json.dumps(props, ensure_ascii=False)]
    if alpha:
        cmd += ["--codec=prores", "--prores-profile=4444", "--pixel-format=yuva444p10le", "--image-format=png"]
    if chrome:
        cmd.append(f"--browser-executable={chrome}")
    run(cmd, cwd=E.REMOTION)
    return out


def typing(dur, seed=3):
    """Soft keyboard clicks for a typewriter line (stereo, 48 kHz)."""
    rng = np.random.default_rng(seed); n = int(dur * sfx_pro.SR); x = np.zeros(n)
    t = 0.05
    while t < dur - 0.05:
        i = int(t * sfx_pro.SR); m = int(0.012 * sfx_pro.SR)
        burst = rng.standard_normal(m) * np.exp(-np.linspace(0, 6, m))
        x[i:i + m] += burst[: n - i] * rng.uniform(0.5, 1.0)
        t += rng.uniform(0.06, 0.12)
    x = np.diff(x, prepend=0)                     # brighter click
    return sfx_pro._norm(sfx_pro._stereo(x, 0, 0.3), 0.5)


def series_pill(text, path):
    """Neon pill (violet -> blue gradient, white Readex Pro text) for the series name, top-right of the frame."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    f = ImageFont.truetype(os.path.join(E.FONTS_DIR, E.AR_BOLD), 34)
    tw = ImageDraw.Draw(Image.new("RGBA", (10, 10))).textlength(text, font=f)
    w, h, pad = int(tw + 56), 66, 24
    im = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([pad, pad, pad + w, pad + h], radius=h // 2, fill=255)
    glow = Image.new("RGBA", im.size, (56, 189, 248, 0)); glow.putalpha(m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 0.6))
    im.alpha_composite(glow)
    g = Image.new("RGBA", im.size); gd = ImageDraw.Draw(g)
    for x in range(im.width):
        k = x / (im.width - 1)
        gd.line([(x, 0), (x, im.height)], fill=tuple(int(a + (b - a) * k) for a, b in zip(E.VIOLET, E.BLUE)) + (255,))
    im.paste(g, (0, 0), m)
    ImageDraw.Draw(im).text((pad + w / 2, pad + h / 2 + 1), text, font=f, fill="white", anchor="mm")
    im.save(path)


def main(base, timeline, plan_path, out):
    tl = json.load(open(timeline)); segs = tl["segs"]; total = tl["total"]
    plan = json.load(open(plan_path))
    om = lambda t: E.remap(t, segs)
    work = os.path.join(os.path.dirname(os.path.abspath(out)), "ref_work"); os.makedirs(work, exist_ok=True)
    os.makedirs(PUB, exist_ok=True)
    sfx_dir = os.path.join(work, "sfx"); os.makedirs(sfx_dir, exist_ok=True)
    snd = sfx_pro.make_all(sfx_dir)               # dict name -> wav path
    layers, sounds = [], []                       # (path, start, end, full_frame) / (wav, start, gain_db)

    for i, (a, b, clip, label) in enumerate(plan.get("phone", [])):
        oa, ob = om(a), om(b); d = ob - oa; nf = int(round(d * FPS))
        pip, ph = os.path.join(PUB, f"pip{i}.mp4"), os.path.join(PUB, f"phone{i}.mp4")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{oa:.3f}", "-t", f"{d:.3f}", "-i", base, "-an", "-r", str(FPS),
             "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", pip])
        run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "5", "-i", clip, "-t", f"{d:.3f}", "-an", "-r", str(FPS),
             "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", ph])
        o = rm("PhoneSplit", os.path.join(work, f"split{i}.mp4"), {"pip": f"ref/pip{i}.mp4", "phone": f"ref/phone{i}.mp4", "label": label, "d": nf})
        layers.append((o, oa, ob, True))
        sounds += [(snd["swoosh"], oa, -16), (snd["sparkle"], oa + 0.33, -22)]

    for i, (a, b, title, value, sub, x, y) in enumerate(plan.get("card", [])):
        oa, ob = om(a), om(b)
        o = rm("GlassCard", os.path.join(work, f"card{i}.mov"), {"title": title, "value": value, "sub": sub, "x": x, "y": y,
                                                                "d": int(round((ob - oa) * FPS))}, alpha=True)
        layers.append((o, oa, ob, False)); sounds.append((snd["pop"], oa, -18))

    for i, (a, b, text, y) in enumerate(plan.get("search", [])):
        oa, ob = om(a), om(b); d = ob - oa
        o = rm("SearchBar", os.path.join(work, f"search{i}.mov"), {"text": text, "y": y, "d": int(round(d * FPS))}, alpha=True)
        layers.append((o, oa, ob, False))
        tw = os.path.join(sfx_dir, f"typing{i}.wav"); sfx_pro.write(tw, typing(max(0.3, d - 0.2 - 14 / FPS)))
        sounds += [(snd["pop"], oa, -20), (tw, oa + 6 / FPS, -14)]

    ser = plan.get("series")      # persistent series pill (top-right), e.g. "E-COM TIP • الحلقة 01"
    if ser:
        png = os.path.join(work, "series.png"); series_pill(ser["text"], png)
        oa = ser.get("from", 2.7); ob = total
        layers.append((png, oa, ob, "png"))

    cta = plan.get("cta")
    if cta:
        dur = cta.get("dur", 3.5); oa, ob = total - dur, total - 0.05
        o = rm("CtaPills", os.path.join(work, "cta.mov"), {"items": cta["items"], "y": cta.get("y", 1250), "d": int(round(dur * FPS))}, alpha=True)
        layers.append((o, oa, ob, False))
        sounds += [(snd["pop"], oa + k * 9 / FPS, -18) for k in range(len(cta["items"]))]

    # composite
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", base]
    fc, cur = "", "0:v"
    for k, (p, oa, ob, full) in enumerate(layers, 1):
        if full == "png":
            cmd += ["-loop", "1", "-t", f"{ob:.3f}", "-i", p]
            fc += (f"[{k}:v]format=rgba,fade=t=in:st={oa:.3f}:d=0.3:alpha=1[l{k}];"
                   f"[{cur}][l{k}]overlay=W-w-20:120:enable='between(t,{oa:.3f},{ob:.3f})'[v{k}];")
            cur = f"v{k}"; continue
        cmd += ["-i", p]
        fmt = "format=yuv420p" if full else "format=yuva444p10le"
        fc += f"[{k}:v]{fmt},setpts=PTS-STARTPTS+{oa:.3f}/TB[l{k}];[{cur}][l{k}]overlay=0:0:eof_action=pass:enable='between(t,{oa:.3f},{ob:.3f})'[v{k}];"
        cur = f"v{k}"
    n0 = len(layers) + 1
    mix = ["[0:a]"]
    for j, (w, t, g) in enumerate(sounds):
        cmd += ["-i", w]
        ms = int(t * 1000)
        fc += f"[{n0 + j}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{j}];"
        mix.append(f"[s{j}]")
    fc += "".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[am]"
    cmd += ["-filter_complex", fc, "-map", f"[{cur}]", "-map", "[am]", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    run(cmd)
    shutil.rmtree(PUB, ignore_errors=True)        # temp clips for Remotion (not part of the repo)
    print("OK ->", out)


if __name__ == "__main__":
    main(*sys.argv[1:5])
