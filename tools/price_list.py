#!/usr/bin/env python3
"""Mustafa's sponsoring price list in his identity (palette C, Sora / Readex Pro, neon glass icons, K+M logo).
Prices and reach come from HIS price image (2026-10-07) — edit PLANS below when they change.
  python3 tools/price_list.py   -> assets/brand/identity/price_list.png (1920x1080) + price_list_post.png (1080x1350)
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_identity as M
import neon_icons

PLANS = [  # (title, sub, price, reach, [(level price, reach)], icon, premium)
    ("5 DAYS", "Sponsoring", "3800", "9k - 24k", [("5500", "15k - 35k"), ("7000", "35k - 85k")], "groups", False),
    ("7 DAYS", "Sponsoring", "5300", "12k - 34k", [("7700", "21k - 49k"), ("9800", "49k - 120k")], "ads_click", False),
    ("10 DAYS", "Sponsoring", "7600", "17k - 48k", [("11000", "30k - 70k"), ("14000", "70k - 180k")], "hub", False),
    ("15 DAYS", "Sponsoring", "11400", "20k - 60k", [("16650", "33k - 120k"), ("21000", "105k - 260k")], "campaign", False),
    ("1 MOIS", "Sponsoring", "22000", "40k - 120k", [("32000", "66k - 240k"), ("40000", "210k - 520k")], "workspace_premium", True),
]


def card(im, box, plan):
    title, sub, price, reach, levels, icon, prem = plan
    x0, y0, x1, y1 = box
    w = x1 - x0
    d = ImageDraw.Draw(im)
    # glow behind premium
    if prem:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle([x0 - 10, y0 - 10, x1 + 10, y1 + 10], radius=44, fill=(56, 189, 248, 120))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(28)))
    # glass card with gradient border
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle(box, radius=40, fill=255)
    body = Image.new("RGBA", im.size, (36, 22, 84, 225)); im.paste(body, (0, 0), m)
    ring = Image.new("L", im.size, 0); ImageDraw.Draw(ring).rounded_rectangle(box, radius=40, outline=255, width=4 if prem else 3)
    rgb = Image.new("RGBA", im.size); rgb.paste(M.hgrad(im.width, im.height).convert("RGBA")); im.paste(rgb, (0, 0), ring)
    cx = (x0 + x1) // 2
    if prem:
        pm = M.SORA(22); tw = d.textlength("PREMIUM", font=pm)
        pill = Image.new("L", im.size, 0); ImageDraw.Draw(pill).rounded_rectangle([cx - tw / 2 - 22, y0 - 20, cx + tw / 2 + 22, y0 + 20], radius=20, fill=255)
        im.paste(rgb, (0, 0), pill); d.text((cx, y0), "PREMIUM", font=pm, fill="white", anchor="mm")
    t = neon_icons.tile(icon, 120); im.alpha_composite(t, (cx - t.width // 2, y0 - 10))
    y = y0 + 12 + t.height + 6
    d.text((cx, y), title, font=M.SORA(58), fill="white", anchor="mm"); y += 46
    d.text((cx, y), sub, font=M.SORAS(28), fill=M.LAV, anchor="mm"); y += 52
    # price block
    pb = [x0 + 26, y, x1 - 26, y + 150]
    pm_ = Image.new("L", im.size, 0); ImageDraw.Draw(pm_).rounded_rectangle(pb, radius=26, fill=255)
    im.paste(Image.new("RGBA", im.size, (20, 11, 52, 235)), (0, 0), pm_)
    pf = M.SORA(62); pw = d.textlength(price, font=pf)
    M.grad_text(im, (cx - (pw + 54) / 2, y + 52), price, pf, anchor="lm")
    d.text((cx + (pw + 54) / 2 - 50, y + 62), "DZD", font=M.SORAS(22), fill=M.ICE, anchor="lm")
    d.text((cx, y + 112), reach, font=M.SORA(34), fill="white", anchor="mm")
    d.text((cx, y + 140), "REACH", font=M.SORAS(18), fill=M.LAV, anchor="mm")
    y += 186
    d.text((cx, y), "LEVELS", font=M.SORA(30), fill="white", anchor="mm"); y += 30
    for lp, lr in levels:
        lb = [x0 + 26, y, x1 - 26, y + 86]
        lm = Image.new("L", im.size, 0); ImageDraw.Draw(lm).rounded_rectangle(lb, radius=20, fill=255)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); ov.paste((255, 255, 255, 22), (0, 0), lm); im.alpha_composite(ov)
        ImageDraw.Draw(im).rounded_rectangle(lb, radius=20, outline=(139, 92, 246, 140), width=2)
        f = M.SORA(40); lw = d.textlength(lp, font=f)
        d.text((cx - 22, y + 30), lp, font=f, fill="white", anchor="mm")
        d.text((cx - 22 + lw / 2 + 8, y + 36), "DZD", font=M.SORAS(17), fill=M.ICE, anchor="lm")
        d.text((cx, y + 65), f"({lr})", font=M.SORAS(24), fill=M.LAV, anchor="mm")
        y += 96


def meta_logo(im, x, cy, w):
    """Meta-style infinity mark in Meta blue (#0064E0 -> #0082FB), drawn as a thick lemniscate."""
    import math
    S = 4; W2, H2 = w * S, int(w * 0.55) * S
    m = Image.new("L", (W2, H2), 0); dm = ImageDraw.Draw(m)
    pts = []
    for i in range(400):
        t = 2 * math.pi * i / 400
        den = 1 + math.sin(t) ** 2
        pts.append((W2 / 2 + (W2 * 0.42) * math.cos(t) / den, H2 / 2 + (H2 * 0.78) * math.sin(t) * math.cos(t) / den))
    dm.line(pts + [pts[0]], fill=255, width=int(H2 * 0.2), joint="curve")
    g = Image.new("RGBA", (W2, H2)); gd = ImageDraw.Draw(g)
    for xx in range(W2):
        k = xx / (W2 - 1)
        gd.line([(xx, 0), (xx, H2)], fill=(0, int(100 + 30 * k), int(224 + 27 * k), 255))
    out = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); out.paste(g, (0, 0), m)
    out = out.resize((w, H2 // S), Image.LANCZOS)
    im.alpha_composite(out, (x, cy - out.height // 2))


def landscape(path):
    W, H = 1920, 1080
    im = M.bg(W, H).convert("RGBA")
    d = ImageDraw.Draw(im)
    logo = M.ICON.resize((96, 96), Image.LANCZOS); im.alpha_composite(logo, (60, 40))
    d.text((176, 88), "SPONSORING  •  META ADS", font=M.SORA(40), fill="white", anchor="lm")
    meta_logo(im, int(176 + d.textlength("SPONSORING  •  META ADS", font=M.SORA(40)) + 24), 88, 90)
    M.grad_text(im, (W - 60, 90), "عروض الإعلانات الممولة", M.READ(64), anchor="rm")   # big title, brand gradient
    cw, gap, top = 330, 30, 175
    x = (W - (5 * cw + 4 * gap)) // 2
    for p in PLANS:
        card(im, [x, top, x + cw, top + 735], p); x += cw + gap
    # call to action
    M.grad_text(im, (W // 2, 962), "إذا راك واجد، ابعث ونبداو نخدمو", M.READ(46), anchor="mm")
    # footer: WhatsApp left, Instagram + Facebook + handle right
    wa = neon_icons.tile("chat", 60); im.alpha_composite(wa, (70, H - 95))
    d.text((70 + wa.width - 12, H - 50), "WhatsApp: 0550 20 54 64", font=M.SORA(36), fill="white", anchor="lm")
    hx = W - 60
    d.text((hx, H - 50), "@kabli_ms  •  Kabli Mustapha", font=M.SORAS(30), fill=M.LAV, anchor="rm")
    hx -= d.textlength("@kabli_ms  •  Kabli Mustapha", font=M.SORAS(30)) + 24
    for kind in ("fb", "ig"):
        S = 58; x0, y0 = int(hx - S), H - 50 - S // 2
        dd = ImageDraw.Draw(im)
        if kind == "ig":   # official Instagram colours: yellow -> orange -> pink -> purple -> blue gradient squircle
            stops = [(254, 218, 117), (250, 126, 30), (214, 41, 118), (150, 47, 191), (79, 91, 213)]
            gimg = Image.new("RGBA", (S, S)); gd = ImageDraw.Draw(gimg)
            for i in range(2 * S):
                k = i / (2 * S - 1) * (len(stops) - 1); j = min(int(k), len(stops) - 2); u = k - j
                col = tuple(int(stops[j][c] + (stops[j + 1][c] - stops[j][c]) * u) for c in range(3))
                gd.line([(0, S - 1 - i), (i, S - 1)], fill=col + (255,), width=2)   # bottom-left yellow -> top-right blue
            mk = Image.new("L", (S, S), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, S - 1, S - 1], radius=16, fill=255)
            im.paste(gimg, (x0, y0), mk)
            dd.rounded_rectangle([x0 + 12, y0 + 12, x0 + S - 12, y0 + S - 12], radius=10, outline="white", width=4)
            dd.ellipse([x0 + 21, y0 + 21, x0 + S - 21, y0 + S - 21], outline="white", width=4)
            dd.ellipse([x0 + S - 20, y0 + 16, x0 + S - 15, y0 + 21], fill="white")
        else:              # official Facebook blue circle with white f
            dd.ellipse([x0, y0, x0 + S, y0 + S], fill=(24, 119, 242))
            dd.text((x0 + S / 2 + 3, y0 + S / 2 + 6), "f", font=M.SORA(46), fill="white", anchor="mm")
        hx -= S + 14
    im.convert("RGB").save(path)


if __name__ == "__main__":
    out = os.path.join(M.OUT, "price_list.png"); landscape(out); print(out)
