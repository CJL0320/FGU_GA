#!/usr/bin/env python3
"""Neon glass app-icons in Mustafa's palette C, drawn like his reference images (2026-10-07):
dark violet glass squircle, thin neon-blue -> violet rim with glow, soft lavender-white 3D pictogram with a
bright outline, violet light from the top-left, a soft diagonal light beam, sparkle + dot, aura and shadow.
Pictograms: Google Material Icons Round (Apache 2.0, tools/fonts/MaterialIconsRound-Regular.otf).

  python3 tools/neon_icons.py      -> scratch preview of all icons (neon_icons_preview.png in the cwd)
  tile(name, T, pulse)            -> RGBA icon (with room for glow / shadow), used by edit_reel.py + make_identity.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont

FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
VIOLET, BLUE, PINK = (139, 92, 246), (56, 189, 248), (192, 132, 252)
LAV_TOP, LAV_BOT = (246, 243, 255), (199, 186, 253)

# emoji in the .srt -> Material icon name (anything else falls back to the colour emoji itself)
EMOJI_ICON = {"✅": "check_circle", "✔": "check_circle", "❌": "cancel", "💸": "payments", "💵": "payments",
              "💰": "savings", "🚨": "warning", "⚠": "warning", "🔥": "local_fire_department", "👇": "arrow_downward",
              "💬": "chat", "🛒": "shopping_cart", "📦": "inventory_2", "🤝": "handshake", "📈": "trending_up",
              "📱": "smartphone", "🏠": "home", "💡": "lightbulb", "📣": "campaign", "📢": "campaign",
              "🏪": "storefront", "👤": "person", "⭐": "star", "🚀": "rocket_launch", "🎯": "ads_click",
              "🛍": "shopping_bag", "🚚": "local_shipping",
              "👥": "groups", "🔁": "autorenew", "👀": "visibility", "✋": "back_hand", "⏱": "timer", "🚫": "block",
              "🎬": "movie", "😅": "sentiment_dissatisfied"}

_CP = {}


def icon_char(name):
    if not _CP:
        for line in open(os.path.join(FD, "MaterialIconsRound-Regular.codepoints")):
            n, c = line.split()
            _CP[n] = chr(int(c, 16))
    return _CP.get(name)


def glyph_mask(name, S):
    """L mask (SxS) of a Material icon, trimmed and centred."""
    f = ImageFont.truetype(os.path.join(FD, "MaterialIconsRound-Regular.otf"), int(S * 1.2))
    big = Image.new("L", (int(S * 2), int(S * 2)), 0)
    ImageDraw.Draw(big).text((S, S), icon_char(name), font=f, fill=255, anchor="mm")
    g = big.crop(big.getbbox())
    k = S / max(g.size)
    g = g.resize((max(1, int(g.width * k)), max(1, int(g.height * k))), Image.LANCZOS)
    m = Image.new("L", (S, S), 0)
    m.paste(g, ((S - g.width) // 2, (S - g.height) // 2))
    return m


def _shift(m, dx, dy):
    out = Image.new("L", m.size, 0)
    out.paste(m, (dx, dy))
    return out


def pictogram(mask):
    """Soft 3D lavender pictogram from an L mask: gradient fill, top-left light edge, bottom-right shade, bright outline."""
    S = mask.width
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    grad = Image.new("RGBA", (S, S)); gd = ImageDraw.Draw(grad)
    for y in range(S):
        k = y / S
        gd.line([(0, y), (S, y)], fill=tuple(int(LAV_TOP[i] + (LAV_BOT[i] - LAV_TOP[i]) * k) for i in range(3)) + (255,))
    out.paste(grad, (0, 0), mask)
    d = max(2, S // 60)
    shade = ImageChops.subtract(mask, _shift(mask, -d, -d)).filter(ImageFilter.GaussianBlur(d * .8))
    out.alpha_composite(Image.merge("RGBA", [Image.new("L", (S, S), v) for v in (120, 92, 200)] + [ImageChops.multiply(shade, mask).point(lambda v: v * 0.55)]))
    light = ImageChops.subtract(mask, _shift(mask, d, d)).filter(ImageFilter.GaussianBlur(d * .6))
    out.alpha_composite(Image.merge("RGBA", [Image.new("L", (S, S), 255)] * 3 + [ImageChops.multiply(light, mask).point(lambda v: v * 0.8)]))
    edge = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(2 * (d // 2) + 3)), mask)
    out.alpha_composite(Image.merge("RGBA", [Image.new("L", (S, S), 255)] * 3 + [edge.point(lambda v: v * 0.85)]))
    return out


def _lin(size, c0, c1, diagonal=True, alpha=255):
    w, h = size
    g = Image.new("RGBA", size); d = ImageDraw.Draw(g)
    n = w + h if diagonal else w
    for i in range(n):
        k = i / max(1, n - 1)
        col = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3)) + (alpha,)
        d.line([(i, 0), (0, i)] if diagonal else [(i, 0), (i, h)], fill=col, width=2 if diagonal else 1)
    return g


def tile(name=None, T=420, pulse=1.0, emoji_img=None):
    """The icon: T = squircle size in px; the returned canvas has padding for aura/glow/shadow.
    name = Material icon name (or None + emoji_img = RGBA picture to put inside)."""
    pad = int(T * .34)
    C = T + 2 * pad
    rad = int(T * .25)
    cv = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    box = [pad, pad, pad + T - 1, pad + T - 1]
    # aura (a bigger soft rounded glow behind, like reference 3) + drop shadow
    aura = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    ImageDraw.Draw(aura).rounded_rectangle([pad - T * .07, pad - T * .05, pad + T * 1.07, pad + T * 1.1], radius=rad * 1.3, fill=VIOLET + (int(60 * pulse),))
    cv.alpha_composite(aura.filter(ImageFilter.GaussianBlur(T * .09)))
    sh = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad + T * .04, pad + T * .1, pad + T * .96, pad + T * 1.06], radius=rad, fill=(0, 0, 0, 170))
    cv.alpha_composite(sh.filter(ImageFilter.GaussianBlur(T * .06)))
    # glass body: violet top-left -> night bottom-right, violet light from the top-left, soft diagonal beam
    sq = Image.new("L", (T, T), 0); ImageDraw.Draw(sq).rounded_rectangle([0, 0, T - 1, T - 1], radius=rad, fill=255)
    body = _lin((T, T), (70, 46, 150), (16, 10, 42), alpha=240)
    glow = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-T * .25, -T * .35, T * .75, T * .6], fill=VIOLET + (120,))
    body.alpha_composite(glow.filter(ImageFilter.GaussianBlur(T * .14)))
    beam = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    ImageDraw.Draw(beam).polygon([(T * .62, 0), (T * .95, 0), (T * .3, T), (-T * .03, T)], fill=(235, 225, 255, 34))
    body.alpha_composite(beam.filter(ImageFilter.GaussianBlur(T * .06)))
    body.putalpha(ImageChops.multiply(body.split()[3], sq))
    inner = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    ImageDraw.Draw(inner).rounded_rectangle([T * .02, T * .02, T * .98, T * .98], radius=rad * .92, outline=(255, 255, 255, 34), width=max(1, T // 160))
    body.alpha_composite(inner)
    # neon rim: blue bottom-left -> violet -> pink top-right, with its own glow
    ring = Image.new("L", (T, T), 0)
    ImageDraw.Draw(ring).rounded_rectangle([1, 1, T - 2, T - 2], radius=rad, outline=255, width=max(2, int(T * .013)))
    rimc = _lin((T, T), BLUE, PINK).transpose(Image.FLIP_TOP_BOTTOM)   # blue bottom-left -> pink top-right
    rim = Image.new("RGBA", (T, T), (0, 0, 0, 0)); rim.paste(rimc, (0, 0), ring)
    rg = Image.new("RGBA", (C, C), (0, 0, 0, 0)); rg.alpha_composite(rim, (pad, pad))
    cv.alpha_composite(rg.filter(ImageFilter.GaussianBlur(T * .03 * pulse)))
    cv.alpha_composite(body, (pad, pad))
    # pictogram with a soft lavender glow
    P = int(T * .5)
    if name:
        pic = pictogram(glyph_mask(name, P))
    else:
        pic = Image.new("RGBA", (P, P), (0, 0, 0, 0))
        if emoji_img is not None:
            e = emoji_img.copy(); e.thumbnail((P, P), Image.LANCZOS)
            pic.alpha_composite(e, ((P - e.width) // 2, (P - e.height) // 2))
    px, py = pad + (T - P) // 2, pad + (T - P) // 2 + int(T * .01)
    pg = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    halo = Image.new("RGBA", (P, P), (167, 139, 250, 0)); halo.putalpha(pic.split()[3])
    pg.alpha_composite(halo, (px, py))
    cv.alpha_composite(pg.filter(ImageFilter.GaussianBlur(T * .035 * pulse)))
    cv.alpha_composite(pic, (px, py))
    cv.alpha_composite(rim, (pad, pad))
    # sparkle + small dot (top-right inside the tile)
    d = ImageDraw.Draw(cv)
    sx, sy, r0 = pad + T * .8, pad + T * .19, T * .05
    d.polygon([(sx, sy - r0), (sx + r0 * .22, sy - r0 * .22), (sx + r0, sy), (sx + r0 * .22, sy + r0 * .22),
               (sx, sy + r0), (sx - r0 * .22, sy + r0 * .22), (sx - r0, sy), (sx - r0 * .22, sy - r0 * .22)], fill=(236, 230, 255, 235))
    dr = T * .022
    d.ellipse([pad + T * .87 - dr, pad + T * .31 - dr, pad + T * .87 + dr, pad + T * .31 + dr], fill=(196, 181, 253, 170))
    return cv


if __name__ == "__main__":
    names = ["lightbulb", "campaign", "storefront", "trending_up", "person", "chat", "check_circle", "cancel",
             "payments", "warning", "local_fire_department", "shopping_cart", "inventory_2", "home", "arrow_downward", "handshake"]
    S = 360
    sheet = Image.new("RGB", (S * 4, S * 4), (14, 8, 36))
    for i, n in enumerate(names):
        t = tile(n, 220)
        t = t.resize((S, S), Image.LANCZOS)
        sheet.paste(t, ((i % 4) * S, (i // 4) * S), t)
    sheet.save("neon_icons_preview.png")
    print("neon_icons_preview.png")
