#!/usr/bin/env python3
"""Mustafa / @kabli_ms logo, palette C (violet + neon blue): K+M monogram whose K upper arm is a rising arrow
in a violet -> neon-blue gradient, rounded strokes, on a dark-violet glass squircle with a gradient neon rim
(same family as the neon app-icons used in the reels). Outputs to assets/brand/:
  logo_mark.svg/.png          app-icon squircle (transparent corners)
  logo_mark_white.svg/.png    white letters + gradient arrow, transparent (videos, dark backgrounds, badge coin)
  logo_mark_dark.svg/.png     ink letters + gradient arrow, transparent (light backgrounds)
  logo_profile.png            1080x1080 full-bleed, circle-safe (Instagram profile picture)
  logo_horizontal.png         1920x640 banner: mark + KABLI_MS + tagline
"""
import io, os, cairosvg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "brand")
FD = os.path.join(ROOT, "tools", "fonts")
NIGHT, DEEP, VIOLET, BLUE, LAV, WHITE = "#140B34", "#2A1B5E", "#8B5CF6", "#38BDF8", "#C4B5FD", "#FFFFFF"   # palette C

DEFS = f"""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{DEEP}"/><stop offset="1" stop-color="#0B0620"/></linearGradient>
  <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <linearGradient id="arw" gradientUnits="userSpaceOnUse" x1="150" y1="260" x2="300" y2="104"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient>
  <radialGradient id="glow" cx="0.3" cy="0.2" r="0.8"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0.45"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
</defs>"""


def glyphs(fg):
    """K+M in a 512 box (before fitting). The arrow is drawn first so the white K stem covers its start cleanly."""
    return f"""<path d="M152 254 L246 160" stroke="url(#arw)" stroke-width="44" stroke-linecap="round" fill="none"/>
  <polygon points="300,104 280,196 208,124" fill="url(#arw)" stroke="url(#arw)" stroke-width="12" stroke-linejoin="round"/>
  <g fill="none" stroke="{fg}" stroke-width="44" stroke-linecap="round" stroke-linejoin="round">
    <path d="M128 384 V136"/>
    <path d="M152 262 L246 384"/>
    <path d="M352 384 V146 L414 262 L476 146 V384"/>
  </g>"""


def _bbox(fg=WHITE):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">{DEFS}{glyphs(fg)}</svg>'
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert("RGBA")
    return im.getbbox()


def mark(kind="icon"):
    """kind: icon (squircle), white, dark."""
    x0, y0, x1, y1 = _bbox()
    box = 300 if kind == "icon" else 440                 # monogram size inside the 512 canvas
    s = box / max(x1 - x0, y1 - y0)
    tx, ty = 256 - (x0 + x1) / 2 * s, 256 - (y0 + y1) / 2 * s
    fg = NIGHT if kind == "dark" else WHITE
    bg = ""
    if kind == "icon":
        bg = (f'<rect x="14" y="14" width="484" height="484" rx="122" fill="url(#bg)"/>'
              f'<rect x="14" y="14" width="484" height="484" rx="122" fill="url(#glow)"/>'
              f'<path d="M136 14 H376 Q498 14 498 136 V170 Q300 120 14 260 V136 Q14 14 136 14 Z" fill="#FFFFFF" opacity="0.06"/>'
              f'<rect x="14" y="14" width="484" height="484" rx="122" fill="none" stroke="url(#rim)" stroke-width="9"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">{DEFS}{bg}'
            f'<g transform="translate({tx:.1f},{ty:.1f}) scale({s:.4f})">{glyphs(fg)}</g></svg>')


def png(svg, size):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size))).convert("RGBA")


def save(svg, name, size=1024):
    open(os.path.join(OUT, name + ".svg"), "w").write(svg)
    png(svg, size).save(os.path.join(OUT, name + ".png"))


def neon_glow(im, k=0.035):
    """Soft violet/blue halo around the shape (for the squircle versions)."""
    a = im.split()[3]
    pad = int(im.width * 0.12)
    cv = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    halo = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    col = Image.new("RGBA", im.size, (139, 92, 246, 255)); col.putalpha(a)
    halo.alpha_composite(col, (pad, pad))
    cv.alpha_composite(halo.filter(ImageFilter.GaussianBlur(im.width * k)))
    cv.alpha_composite(im, (pad, pad))
    return cv


def sora(size, bold=True):
    return ImageFont.truetype(os.path.join(FD, "Sora-ExtraBold.ttf" if bold else "Sora-SemiBold.ttf"), size)


def gradient(w, h, c0, c1, diagonal=True):
    g = Image.new("RGB", (w, h)); d = ImageDraw.Draw(g)
    c0 = tuple(int(c0[i:i + 2], 16) for i in (1, 3, 5)); c1 = tuple(int(c1[i:i + 2], 16) for i in (1, 3, 5))
    n = w + h if diagonal else h
    for i in range(n):
        k = i / max(1, n - 1)
        col = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
        d.line([(i, 0), (0, i)] if diagonal else [(0, i), (w, i)], fill=col, width=2 if diagonal else 1)
    return g


def main():
    os.makedirs(OUT, exist_ok=True)
    save(mark("icon"), "logo_mark")
    save(mark("white"), "logo_mark_white")
    save(mark("dark"), "logo_mark_dark")
    # profile picture: full-bleed dark violet, glow behind, monogram centred inside the circle crop
    P = 1080
    prof = gradient(P, P, DEEP, "#0B0620").convert("RGBA")
    glow = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([P * .18, P * .14, P * .82, P * .78], fill=(139, 92, 246, 110))
    ImageDraw.Draw(glow).ellipse([P * .45, P * .35, P * .95, P * .9], fill=(56, 189, 248, 60))
    prof.alpha_composite(glow.filter(ImageFilter.GaussianBlur(P * .12)))
    ring = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([P * .06, P * .06, P * .94, P * .94], outline=(139, 92, 246, 140), width=6)
    prof.alpha_composite(ring.filter(ImageFilter.GaussianBlur(2)))
    m = png(mark("white"), int(P * .62))
    prof.alpha_composite(m, ((P - m.width) // 2, (P - m.height) // 2 + 6))
    prof.convert("RGB").save(os.path.join(OUT, "logo_profile.png"))
    # horizontal lockup
    Wd, Ht = 1920, 640
    im = gradient(Wd, Ht, "#1C1145", "#0B0620").convert("RGBA")
    g2 = Image.new("RGBA", (Wd, Ht), (0, 0, 0, 0))
    ImageDraw.Draw(g2).ellipse([40, 20, 760, 620], fill=(139, 92, 246, 90))
    im.alpha_composite(g2.filter(ImageFilter.GaussianBlur(110)))
    icon = neon_glow(png(mark("icon"), 400))
    im.alpha_composite(icon, (160 - (icon.width - 400) // 2, 120 - (icon.height - 400) // 2))
    d = ImageDraw.Draw(im)
    d.text((640, 300), "KABLI_MS", font=sora(150), fill=WHITE, anchor="ls")
    bar = Image.new("RGB", (220, 12)); bd = ImageDraw.Draw(bar)   # violet -> blue underline
    for x in range(220):
        k = x / 219
        bd.line([(x, 0), (x, 12)], fill=tuple(int(a + (b - a) * k) for a, b in zip((139, 92, 246), (56, 189, 248))))
    im.paste(bar, (646, 350))
    d.text((646, 440), "E-COMMERCE  •  SPONSOR  •  META ADS", font=sora(44, False), fill=LAV, anchor="ls")
    im.convert("RGB").save(os.path.join(OUT, "logo_horizontal.png"))
    print("done:", sorted(f for f in os.listdir(OUT) if f.startswith("logo")))


if __name__ == "__main__":
    main()
