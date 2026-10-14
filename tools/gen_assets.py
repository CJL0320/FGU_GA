#!/usr/bin/env python3
"""Generate the effect assets used by edit_reel.py (no downloads needed).

  python3 tools/gen_assets.py

Creates in assets/_generated/ (git-ignored, auto-created by edit_reel.py when missing; 540x960 @30fps; alpha ones are QuickTime 'qtrle' with transparency):
  assets/_generated/sparks_neon.mov     rising violet / neon-blue sparks
  assets/_generated/flash_white.mov     0.3s white flash
  assets/_generated/light_leak.mov      violet / neon-blue light leak sweep
  assets/_generated/money_rain.mov      falling dollar bills
  assets/_generated/growth_chart.mp4     animated growth chart in brand colours (palette C, opaque)
Put your own files in assets/sparks, assets/broll, assets/icons (they win over generated ones) and reference them from the .srt.
"""
import math, os, random, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, SW, SH = 30, 540, 960          # drawn at half size, upscaled by ffmpeg
random.seed(7)


def encode(frames_dir, out, alpha=True):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    vf = "scale=trunc(iw/2)*2:trunc(ih/2)*2"  # files stay 540x960; edit_reel.py scales them to 1080x1920
    if alpha:
        cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{frames_dir}/%04d.png",
               "-vf", vf + ",format=argb", "-c:v", "qtrle", out]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{frames_dir}/%04d.png",
               "-vf", vf + ",format=yuv420p", "-c:v", "libx264", "-crf", "20", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print("wrote", os.path.relpath(out, ROOT), f"{os.path.getsize(out)/1e6:.1f}MB")


def sparks(n_secs=1.2):
    d = tempfile.mkdtemp()
    parts = [dict(x=random.uniform(0, SW), y=random.uniform(SH * .55, SH * 1.05),
                  vx=random.uniform(-40, 40), vy=random.uniform(-520, -180),
                  r=random.uniform(2, 6), life=random.uniform(.5, 1.2), delay=random.uniform(0, .35),
                  c=(139, 92, 246) if random.random() < .5 else (56, 189, 248))
             for _ in range(140)]
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        for p in parts:
            a = t - p["delay"]
            if a < 0 or a > p["life"]:
                continue
            x = p["x"] + p["vx"] * a
            y = p["y"] + p["vy"] * a + 120 * a * a
            k = 1 - a / p["life"]
            r = p["r"] * (0.5 + k)
            col = tuple(int(v + (255 - v) * .45 * k) for v in p["c"]) + (int(255 * k),)   # violet / neon blue, hot core
            dr.line([(x, y), (x - p["vx"] * .03, y - p["vy"] * .03)], fill=col, width=max(1, int(r)))
            dr.ellipse([x - r, y - r, x + r, y + r], fill=col)
        glow = im.filter(ImageFilter.GaussianBlur(5))
        Image.alpha_composite(glow, im).save(f"{d}/{f+1:04d}.png")
    return d


def flash(n_secs=0.3):
    d = tempfile.mkdtemp()
    n = int(n_secs * FPS)
    for f in range(n):
        a = int(230 * (1 - f / n) ** 1.6)
        Image.new("RGBA", (SW, SH), (255, 255, 255, a)).save(f"{d}/{f+1:04d}.png")
    return d


def light_leak(n_secs=0.9):
    d = tempfile.mkdtemp()
    n = int(n_secs * FPS)
    for f in range(n):
        t = f / (n - 1)
        env = math.sin(math.pi * t) ** 1.5
        im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        cx = -150 + t * (SW + 300)
        dr.ellipse([cx - 260, -200, cx + 260, SH * 0.75], fill=(139, 92, 246, int(190 * env)))
        dr.ellipse([cx - 120, SH * .1, cx + 120, SH * .55], fill=(120, 210, 250, int(150 * env)))
        im.filter(ImageFilter.GaussianBlur(70)).save(f"{d}/{f+1:04d}.png")
    return d


def money_rain(n_secs=2.0):
    d = tempfile.mkdtemp()
    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    base = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(base).text((0, 0), "💵", font=font, embedded_color=True)
    base = base.crop(base.getbbox())
    bills = [dict(x=random.uniform(0, SW), y0=random.uniform(-SH * .6, 0), v=random.uniform(380, 620),
                  s=random.uniform(.5, 1.0), rot=random.uniform(-40, 40), spin=random.uniform(-90, 90))
             for _ in range(22)]
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        for b in bills:
            sz = int(base.width * b["s"])
            bi = base.resize((sz, int(sz * base.height / base.width))).rotate(b["rot"] + b["spin"] * t, expand=True)
            im.alpha_composite(bi, (int(b["x"] - bi.width / 2), int(b["y0"] + b["v"] * t)) if
                               0 <= b["x"] - bi.width / 2 < SW - bi.width and 0 <= b["y0"] + b["v"] * t < SH - bi.height
                               else (SW, SH)) if False else None
            x, y = int(b["x"] - bi.width / 2), int(b["y0"] + b["v"] * t)
            if -bi.width < x < SW and -bi.height < y < SH:
                tmp = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
                tmp.paste(bi, (x, y), bi)
                im = Image.alpha_composite(im, tmp)
        im.save(f"{d}/{f+1:04d}.png")
    return d


def growth_chart(n_secs=2.6):
    d = tempfile.mkdtemp()
    navy, blue, green = (20, 11, 52), (42, 27, 94), (56, 189, 248)   # palette C (line = neon blue)
    font = ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Sora-ExtraBold.ttf"), 56)
    big = ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Sora-ExtraBold.ttf"), 96)
    pts = [0.05, .12, .1, .22, .3, .28, .45, .6, .58, .8, .95]
    n = int(n_secs * FPS)
    L, R, T, B = 50, SW - 50, 330, 640
    for f in range(n):
        t = min(1, (f / (n - 1)) * 1.15)
        e = 1 - (1 - t) ** 3
        im = Image.new("RGB", (SW, SH), navy)
        dr = ImageDraw.Draw(im)
        dr.text((SW / 2, 120), "ROAS", font=font, fill=(255, 255, 255), anchor="mm")
        for g in range(5):
            y = T + g * (B - T) / 4
            dr.line([(L, y), (R, y)], fill=(70, 50, 140), width=1)
        k = e * (len(pts) - 1)
        i = int(k)
        xy = [(L + j * (R - L) / (len(pts) - 1), B - pts[j] * (B - T)) for j in range(i + 1)]
        if i < len(pts) - 1:
            fr = k - i
            x0, y0 = xy[-1]
            x1 = L + (i + 1) * (R - L) / (len(pts) - 1)
            y1 = B - pts[i + 1] * (B - T)
            xy.append((x0 + (x1 - x0) * fr, y0 + (y1 - y0) * fr))
        if len(xy) > 1:
            dr.line(xy, fill=green, width=9, joint="curve")
        ex, ey = xy[-1]
        dr.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=(255, 255, 255), outline=green, width=5)
        dr.text((SW / 2, 760), f"x{1 + 4.2 * e:.1f}", font=big, fill=green, anchor="mm")
        im.save(f"{d}/{f+1:04d}.png")
    return d


def _emoji(ch, size):
    f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    im = Image.new("RGBA", (140, 130), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)


NAVY_B, SLATE_B, ORANGE_B, SOFT_B = (20, 11, 52), (42, 27, 94), (139, 92, 246), (196, 181, 253)   # palette C (ORANGE_B = violet)
BLUE_B = (56, 189, 248)
LALEZAR = lambda s: ImageFont.truetype(os.path.join(ROOT, "tools/fonts/ReadexPro-Bold.ttf"), int(s * .9))   # brand Arabic font (Readex Pro)


def _card_bg():
    im = Image.new("RGB", (SW, SH), NAVY_B)
    glow = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([SW * .1, SH * .15, SW * .9, SH * .6], fill=ORANGE_B + (60,))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    im.paste(glow, (0, 0), glow)
    return im


def _ease(t):
    return 1 - (1 - min(max(t, 0), 1)) ** 3


def broll_icon(emoji, big, small, n_secs=1.6):
    """Emoji pops in, big Latin word + Arabic line slide up."""
    d = tempfile.mkdtemp()
    base = _emoji(emoji, 300)
    fb = ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Sora-ExtraBold.ttf"), 68)
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = _card_bg()
        dr = ImageDraw.Draw(im)
        k = _ease(t / 0.35)
        sc = 0.6 + 0.4 * k + 0.04 * math.sin(t * 6)
        e = base.resize((int(base.width * sc), int(base.height * sc)), Image.LANCZOS)
        im.paste(e, (int(SW / 2 - e.width / 2), int(SH * .21 - e.height / 2)), e)
        k2 = _ease((t - 0.2) / 0.35)
        dr.text((SW / 2, SH * .39 + 40 * (1 - k2)), big, font=fb, fill=(255, 255, 255), anchor="mm")
        k3 = _ease((t - 0.35) / 0.35)
        dr.text((SW / 2, SH * .47 + 40 * (1 - k3)), small, font=LALEZAR(64), fill=BLUE_B, anchor="mm", direction="rtl")
        im.save(f"{d}/{f+1:04d}.png")
    return d


def broll_chat(n_secs=1.8):
    """Customer messages pop in like WhatsApp: people talking to you = trust."""
    d = tempfile.mkdtemp()
    msgs = [("السلام، المنتوج متوفر؟", 0.0, False), ("إيه خويا، متوفر", 0.45, True), ("نحب نكوموندي واحد", 0.9, False)]
    font = LALEZAR(34)
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = _card_bg()
        dr = ImageDraw.Draw(im)
        dr.rounded_rectangle([50, 90, SW - 50, SH * .56], radius=40, fill=(11, 20, 26), outline=SLATE_B, width=4)
        dr.text((SW / 2, 140), "WhatsApp", font=ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Sora-SemiBold.ttf"), 32), fill=(255, 255, 255), anchor="mm")
        y = 200
        for text, start, mine in msgs:
            k = _ease((t - start) / 0.25)
            if k <= 0:
                continue
            w = dr.textlength(text, font=font, direction="rtl") + 60
            x0 = max(70, SW - 80 - w) if not mine else 80
            fill = (32, 44, 51) if not mine else (0, 92, 75)
            yy = y + 30 * (1 - k)
            dr.rounded_rectangle([x0, yy, x0 + w, yy + 70], radius=24, fill=fill)
            dr.text((x0 + w - 30, yy + 35), text, font=font, fill=(255, 255, 255), anchor="rm", direction="rtl")
            y += 100
        im.save(f"{d}/{f+1:04d}.png")
    return d


def main():
    jobs = [("assets/_generated/sparks_neon.mov", sparks, True), ("assets/_generated/flash_white.mov", flash, True),
            ("assets/_generated/light_leak.mov", light_leak, True), ("assets/_generated/money_rain.mov", money_rain, True),
            ("assets/_generated/growth_chart.mp4", growth_chart, False),
            ("assets/_generated/trust.mp4", lambda: broll_icon("🤝", "CONFIANCE", "الثقة تاع البنادم"), False),
            ("assets/_generated/product.mp4", lambda: broll_icon("📦", "PRODUIT", "المنتوج في يدك"), False),
            ("assets/_generated/face.mp4", lambda: broll_icon("🎥", "B WJHEK", "اخدم بوجهك"), False),
            ("assets/_generated/chat.mp4", broll_chat, False)]
    for rel, fn, alpha in jobs:
        d = fn()
        encode(d, os.path.join(ROOT, rel), alpha)
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
