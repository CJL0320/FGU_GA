#!/usr/bin/env python3
"""Render the same tip post in several palettes -> assets/brand/identity/palette_compare.png"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda s: ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Anton-Regular.ttf"), s)
T = lambda s: ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Tajawal-ExtraBold.ttf"), s)
M = lambda s: ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Montserrat-Bold.ttf"), s)
for f in (M(10),):
    pass
MARK = Image.open(os.path.join(ROOT, "assets/brand/logo_mark_white.png")).convert("RGBA")

PALETTES = [
    ("A  Noir + Lime", "#0B0B0F", "#16161D", "#C6F432", "#FFFFFF", "#0B0B0F"),
    ("B  Navy + Orange", "#0F172A", "#1B2A4A", "#FF6B2C", "#FFFFFF", "#0F172A"),
    ("C  Charcoal + Emerald + Gold", "#111827", "#1F2937", "#10B981", "#FFFFFF", "#FBBF24"),
    ("D  Royal Violet + Neon", "#1E1B4B", "#312E81", "#A3E635", "#FFFFFF", "#1E1B4B"),
]
h2r = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))

def post(p, w=540, h=675):
    name, c1, c2, acc, fg, onacc = p
    im = Image.new("RGB", (w, h), h2r(c1)); d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(h2r(c1)[i] + (h2r(c2)[i] - h2r(c1)[i]) * k) for i in range(3)))
    d.rounded_rectangle([40, 45, 130, 85], radius=20, fill=h2r(acc))
    d.text((85, 65), "TIP", font=M(22), fill=h2r(onacc), anchor="mm")
    d.text((150, 62), "#1", font=A(60), fill=h2r(acc), anchor="lm")
    d.text((40, 140), "ZID L BUDGET", font=A(84), fill=h2r(fg))
    d.text((40, 235), "B 20%", font=A(84), fill=h2r(acc))
    d.text((40, 330), "KOL YOMEIN", font=A(84), fill=h2r(fg))
    d.rounded_rectangle([40, 470, 500, 570], radius=22, outline=h2r(acc), width=3)
    d.text((270, 520), "ما تكبّرش الميزانية دفعة وحدة", font=T(26), fill=h2r(fg), anchor="mm")
    m = MARK.resize((80, 80)); im.paste(m, (30, 585), m)
    d.text((115, 625), "@kabli_ms", font=M(24), fill=h2r(fg), anchor="lm")
    d.text((300, 640), name, font=M(18), fill=h2r(acc), anchor="rm") if False else None
    return im

W, H = 540, 675
sheet = Image.new("RGB", (W * 4 + 50, H + 90), (240, 243, 248))
d = ImageDraw.Draw(sheet)
for i, p in enumerate(PALETTES):
    sheet.paste(post(p), (10 + i * (W + 10), 70))
    d.text((10 + i * (W + 10), 20), p[0], font=M(30), fill=(20, 30, 50))
sheet.save(os.path.join(ROOT, "assets/brand/identity/palette_compare.png"))
print("ok")
