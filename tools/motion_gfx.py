#!/usr/bin/env python3
"""Motion graphics / illustration / documentary B-roll in Mustafa's brand (palette C: night violet + violet + neon blue), 540x960 @30fps.

  python3 tools/motion_gfx.py            -> assets/_generated/{funnel,merchant}.mp4
  doc_card(text, out)                    -> documentary paper card with a highlighter stroke (used by [doc:TEXT])
Text sits in the upper ~55% so burned captions below stay readable.
"""
import math, os, random, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(ROOT, "tools", "fonts")
FPS, W, H, SS = 30, 540, 960, 2
NAVY, SLATE, ORANGE, AMBER, CREAM = (20, 11, 52), (42, 27, 94), (139, 92, 246), (56, 189, 248), (245, 238, 225)   # palette C: ORANGE = violet, AMBER = neon blue
TAJ = lambda s: ImageFont.truetype(os.path.join(FD, "ReadexPro-Bold.ttf"), int(s))
SORA_SEMI = lambda s: ImageFont.truetype(os.path.join(FD, "Sora-SemiBold.ttf"), int(s))
ease = lambda t: 1 - (1 - min(max(t, 0), 1)) ** 3
back = lambda t: (lambda x: 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2)(min(max(t, 0), 1))


def encode(frames, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{frames}/%04d.png",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], check=True)
    shutil.rmtree(frames, ignore_errors=True)


def navy_bg(t):
    im = Image.new("RGB", (W * SS, H * SS), NAVY)
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    r = (0.5 + 0.04 * math.sin(t * 3)) * W * SS
    ImageDraw.Draw(g).ellipse([W * SS * .5 - r, H * SS * .25 - r, W * SS * .5 + r, H * SS * .25 + r], fill=ORANGE + (45,))
    g = g.filter(ImageFilter.GaussianBlur(80 * SS)); im.paste(g, (0, 0), g)
    return im


def neon_text(im, xy, text, size, col=ORANGE):
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).text(xy, text, font=TAJ(size), fill=col + (255,), anchor="mm")
    im.paste(g.filter(ImageFilter.GaussianBlur(size * .25)), (0, 0), g.filter(ImageFilter.GaussianBlur(size * .25)))
    ImageDraw.Draw(im).text(xy, text, font=TAJ(size), fill=(237, 233, 254), anchor="mm")


# ---------- 1. motion graphic: sales funnel  إعلان -> رسائل -> طلبيات ----------
def funnel(n_secs=2.2):
    d = tempfile.mkdtemp()
    stages = [("إعلان", 1.0), ("رسائل", 0.74), ("طلبيات", 0.5)]
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = navy_bg(t); dr = ImageDraw.Draw(im)
        neon_text(im, (W * SS / 2, 95 * SS), "طريق البيع", 46 * SS)
        top = 165 * SS
        for i, (lab, wf) in enumerate(stages):
            k = back((t - 0.15 - i * 0.28) / 0.35)
            if k <= 0: continue
            y0 = top + i * 120 * SS; h = 100 * SS
            w0 = W * SS * .8 * wf * k; w1 = W * SS * .8 * (stages[i + 1][1] if i < 2 else wf * .8) * k
            cx = W * SS / 2
            col = tuple(int(ORANGE[j] * (1 - i * .18) + SLATE[j] * i * .18) for j in range(3))
            dr.polygon([(cx - w0 / 2, y0), (cx + w0 / 2, y0), (cx + w1 / 2, y0 + h), (cx - w1 / 2, y0 + h)], fill=col)
            dr.line([(cx - w0 / 2, y0), (cx + w0 / 2, y0)], fill=AMBER, width=3 * SS)
            if k > .8:
                dr.text((cx, y0 + h / 2), lab, font=TAJ(40 * SS), fill=(255, 255, 255), anchor="mm")
        # dots falling through the funnel
        for j in range(14):
            ph = (t * 1.3 + j * .23) % 1.6
            if ph > 1.15 or t < .9: continue
            yy = top - 30 * SS + ph * 380 * SS; xx = W * SS / 2 + math.sin(j * 2.3) * (1 - ph / 1.15) * 120 * SS
            dr.ellipse([xx - 7 * SS, yy - 7 * SS, xx + 7 * SS, yy + 7 * SS], fill=(186, 230, 253))
        im.resize((W, H), Image.LANCZOS).save(f"{d}/{f + 1:04d}.png")
    return d


# ---------- 2. illustration: merchant silhouette with neon rim light (reference style) ----------
def merchant(n_secs=2.2):
    d = tempfile.mkdtemp()
    def figure(scale):
        S = W * SS
        m = Image.new("L", (S, H * SS), 0); dd = ImageDraw.Draw(m)
        cx, base = S / 2, H * SS * .6
        u = 1.0 * SS * scale
        P = lambda pts: [(cx + x * u, base + y * u) for x, y in pts]
        dd.polygon(P([(-185, 300), (-175, -40), (-150, -95), (-60, -125), (60, -125), (150, -95), (175, -40), (185, 300)]), fill=255)  # suit
        dd.polygon(P([(-30, -175), (30, -175), (34, -110), (-34, -110)]), fill=255)                      # neck
        dd.ellipse(P([(-60, -330), (60, -170)])[0] + P([(-60, -330), (60, -170)])[1], fill=255)          # head
        dd.polygon(P([(-62, -265), (-58, -320), (-10, -345), (50, -330), (66, -280), (40, -300), (-20, -300)]), fill=255)  # hair
        return m
    def shirt_tie(scale):
        S = W * SS
        sh = Image.new("RGBA", (S, H * SS), (0, 0, 0, 0)); dd = ImageDraw.Draw(sh)
        cx, base = S / 2, H * SS * .6
        u = 1.0 * SS * scale
        P = lambda pts: [(cx + x * u, base + y * u) for x, y in pts]
        dd.polygon(P([(-62, -122), (62, -122), (0, 60)]), fill=(236, 226, 205, 255))                     # shirt V
        dd.polygon(P([(-14, -118), (14, -118), (8, -98), (-8, -98)]), fill=ORANGE + (255,))               # knot
        dd.polygon(P([(-8, -98), (8, -98), (18, 30), (0, 52), (-18, 30)]), fill=ORANGE + (255,))          # tie
        dd.polygon(P([(-62, -122), (-20, -40), (-44, 20)]), fill=(6, 9, 18, 255))                          # lapels
        dd.polygon(P([(62, -122), (20, -40), (44, 20)]), fill=(6, 9, 18, 255))
        return sh
    m = figure(1.0)
    st = shirt_tie(1.0)
    rim = m.filter(ImageFilter.MaxFilter(13)); rim = Image.eval(rim, lambda v: v)
    edge = Image.new("L", m.size, 0); edge.paste(rim); edge = Image.composite(Image.new("L", m.size, 0), edge, m)
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = navy_bg(t)
        sweep = Image.new("L", m.size, 0)
        sx = (-0.3 + t / n_secs * 1.6) * W * SS
        ImageDraw.Draw(sweep).polygon([(sx, 0), (sx + 220 * SS, 0), (sx - 200 * SS, H * SS), (sx - 420 * SS, H * SS)], fill=255)
        glow = Image.new("RGBA", m.size, ORANGE + (0,)); glow.putalpha(edge)
        im.paste(glow.filter(ImageFilter.GaussianBlur(14 * SS)), (0, 0), glow.filter(ImageFilter.GaussianBlur(14 * SS)))
        body = Image.new("RGBA", m.size, (6, 9, 18, 255)); body.putalpha(m)
        im.paste(body, (0, 0), body)
        im.paste(st, (0, 0), st)
        rimc = Image.new("RGBA", m.size, AMBER + (0,)); rimc.putalpha(edge)
        im.paste(rimc, (0, 0), rimc)
        hl = Image.new("RGBA", m.size, (224, 231, 255, 0))
        from PIL import ImageChops
        hl.putalpha(ImageChops.multiply(ImageChops.multiply(m, sweep), Image.new("L", m.size, 28)))
        im.paste(hl, (0, 0), hl)
        k = ease((t - .2) / .5)
        neon_text(im, (W * SS / 2, (110 - 20 * (1 - k)) * SS), "التاجر الذكي", 52 * SS)
        im.resize((W, H), Image.LANCZOS).save(f"{d}/{f + 1:04d}.png")
    return d


# ---------- 3. documentary: paper card, slow Ken-Burns, highlighter + grain ----------
def doc_card(text, out, n_secs=2.0):
    d = tempfile.mkdtemp()
    rnd = random.Random(3)
    paper = Image.new("RGB", (W * SS, H * SS), CREAM)
    pd = ImageDraw.Draw(paper)
    for _ in range(9000):   # paper fibres
        x, y = rnd.randrange(W * SS), rnd.randrange(H * SS); c = rnd.randint(215, 240)
        pd.point((x, y), fill=(c, c - 6, c - 16))
    for i in range(8):      # faint text lines (newspaper)
        y = (470 + i * 52) * SS
        pd.rounded_rectangle([60 * SS, y, (480 - (i % 3) * 60) * SS, y + 14 * SS], radius=6 * SS, fill=(200, 192, 178))
    pd.text((W * SS / 2, 120 * SS), "E-COMMERCE  •  DZ", font=SORA_SEMI(26 * SS), fill=(120, 110, 95), anchor="mm")
    pd.line([(60 * SS, 150 * SS), (480 * SS, 150 * SS)], fill=(120, 110, 95), width=2 * SS)
    font = TAJ(66 * SS)
    tw = pd.textlength(text, font=font, direction="rtl")
    while tw > 440 * SS and font.size > 30 * SS:
        font = TAJ(font.size - 4 * SS); tw = pd.textlength(text, font=font, direction="rtl")
    ty = 300 * SS
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = paper.copy(); dr = ImageDraw.Draw(im, "RGBA")
        k = ease((t - .25) / .6)            # highlighter sweeps right -> left (Arabic reading direction)
        x1 = W * SS / 2 + tw / 2 + 14 * SS; x0 = x1 - (tw + 28 * SS) * k
        if k > 0:
            dr.rounded_rectangle([x0, ty - 34 * SS, x1, ty + 40 * SS], radius=10 * SS, fill=AMBER + (140,))
        dr.text((W * SS / 2, ty), text, font=font, fill=(25, 22, 18), anchor="mm", direction="rtl")
        z = 1 + 0.06 * t / n_secs           # Ken Burns
        cw, ch = int(W * SS / z), int(H * SS / z)
        im = im.crop(((W * SS - cw) // 2, (H * SS - ch) // 3, (W * SS - cw) // 2 + cw, (H * SS - ch) // 3 + ch)).resize((W, H), Image.LANCZOS)
        g = Image.effect_noise((W, H), 22).convert("RGB")      # film grain + vignette
        im = Image.blend(im, g, 0.06)
        v = Image.new("L", (W, H), 0); ImageDraw.Draw(v).ellipse([-W * .3, -H * .2, W * 1.3, H * 1.2], fill=255)
        im = Image.composite(im, Image.new("RGB", (W, H), (40, 30, 20)), v.filter(ImageFilter.GaussianBlur(90)))
        im.save(f"{d}/{f + 1:04d}.png")
    encode(d, out)


if __name__ == "__main__":
    out = os.path.join(ROOT, "assets", "_generated")
    for name, fn in (("funnel", funnel), ("merchant", merchant)):
        encode(fn(), os.path.join(out, name + ".mp4")); print("wrote", name)
    if len(sys.argv) > 1:
        doc_card(sys.argv[1], os.path.join(out, "doc_test.mp4")); print("wrote doc_test")
