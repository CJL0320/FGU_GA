#!/usr/bin/env python3
"""Preview of the neon app-icons used in the reels (brand palette) -> assets/brand/icons_preview.png + icon_check_anim.gif
   python3 tools/icons_preview.py"""
import os, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit_reel as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "brand")
ICONS = ["✅", "❌", "💸", "🚨", "🔥", "💬", "🛒", "📦", "📈", "💡", "📣", "🏪", "👤", "🏠", "🤝", "👇"]


def frames(ch, tmp):
    mov = os.path.join(tmp, f"i{ord(ch[0]):x}.mov")
    E.render_emoji(ch, mov.replace(".mov", "_flat.png"), size=230)
    E.render_icon3d_mov(ch, mov)
    d = mov + "_f"
    return [Image.open(os.path.join(d, f)).convert("RGBA") for f in sorted(os.listdir(d))]


def main():
    tmp = tempfile.mkdtemp()
    S, G = 370, 4
    sheet = Image.new("RGB", (S * G, S * G))
    dr = ImageDraw.Draw(sheet)
    for y in range(S * G):   # night-violet gradient like the brand background
        k = y / (S * G)
        dr.line([(0, y), (S * G, y)], fill=tuple(int(a + (b - a) * k) for a, b in zip((34, 20, 84), (11, 6, 32))))
    glow = Image.new("RGBA", sheet.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([S * .5, -S * .5, S * 3.2, S * 1.6], fill=E.VIOLET + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(160)); sheet.paste(glow, (0, 0), glow)
    first = None
    for i, ch in enumerate(ICONS):
        fr = frames(ch, tmp)
        if first is None:
            first = fr
        im = fr[30]
        x, y = (i % G) * S + (S - im.width) // 2, (i // G) * S + (S - im.height) // 2
        sheet.paste(im, (x, y), im)
    sheet.save(os.path.join(OUT, "icons_preview.png"))
    bg = Image.new("RGBA", first[0].size, (20, 11, 52, 255))
    gif = [Image.alpha_composite(bg, f).convert("P", palette=Image.ADAPTIVE) for f in first[::2]]
    gif[0].save(os.path.join(OUT, "icon_check_anim.gif"), save_all=True, append_images=gif[1:], duration=66, loop=0)
    print("wrote icons_preview.png + icon_check_anim.gif")


if __name__ == "__main__":
    main()
