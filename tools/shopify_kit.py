#!/usr/bin/env python3
"""Store visuals for the women's clothing Shopify store (working name "Violet Vogue"), identity palette C, luxury look.
  python3 tools/shopify_kit.py -> content/shopify/{logo_store.png, logo_store_dark.png, banner_desktop.png, banner_mobile.png, favicon.png}"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_identity as M

NAME, SCRIPT = "VIOLET", "Vogue"
OUT = os.path.join(M.ROOT, "content/shopify")
GV = lambda s: M.F("GreatVibes-Regular.ttf", s)


def wordmark(scale=1.0, fg=(255, 255, 255)):
    """VIOLET in wide Sora with a gradient, 'Vogue' in Great Vibes overlapping below-right."""
    W, H = int(900 * scale), int(330 * scale)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = M.SORA(130 * scale); sp = 22 * scale
    widths = [d.textlength(c, font=f) for c in NAME]; tw = sum(widths) + sp * (len(NAME) - 1)
    m = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(m); x = (W - tw) / 2
    for c, w in zip(NAME, widths):
        dm.text((x, 150 * scale), c, font=f, fill=255, anchor="ls"); x += w + sp
    if fg == (255, 255, 255):   # neon glow only for the version used on dark backgrounds
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); glow.paste((139, 92, 246, 200), (0, 0), m)
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14 * scale)))
    M.paste_grad(im, m)
    g = GV(150 * scale)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((W * 0.62, 235 * scale), SCRIPT, font=g, fill=(0, 0, 0, 160), anchor="mm")
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5 * scale)))
    ImageDraw.Draw(im).text((W * 0.62, 228 * scale), SCRIPT, font=g, fill=fg, anchor="mm")
    return im.crop(im.getbbox())


def banner(W, H, path, mobile=False):
    im = M.bg(W, H).convert("RGBA"); d = ImageDraw.Draw(im)
    # soft spotlight + thin neon arch (a fitting-room mirror) as the luxury motif
    sp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cx, cy = (W // 2, int(H * 0.40)) if mobile else (int(W * 0.77), H // 2)
    r = int(min(W, H) * (0.42 if mobile else 0.44))
    ImageDraw.Draw(sp).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(139, 92, 246, 90))
    im.alpha_composite(sp.filter(ImageFilter.GaussianBlur(r * 0.45)))
    aw, ah = int(r * 1.05), int(r * 1.7)
    arch = Image.new("L", (W, H), 0); da = ImageDraw.Draw(arch)
    box = [cx - aw // 2, cy - ah // 2, cx + aw // 2, cy + ah // 2]
    da.rounded_rectangle(box, radius=aw // 2, outline=255, width=max(4, W // 320))
    da.rectangle([box[0], cy + ah // 2 - 6, box[2], cy + ah // 2 + 10], fill=0)
    neon = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.paste_grad(neon, arch)
    im.alpha_composite(neon.filter(ImageFilter.GaussianBlur(10))); im.alpha_composite(neon)
    wm = wordmark(0.95 if not mobile else 1.1)
    if mobile:
        im.alpha_composite(wm, ((W - wm.width) // 2, int(cy - wm.height / 2)))
        ty = int(H * 0.72); ax, anc = W // 2, "mm"
    else:
        im.alpha_composite(wm, (cx - wm.width // 2, cy - wm.height // 2))
        ty = int(H * 0.36); ax, anc = int(W * 0.08), "lm"
    d = ImageDraw.Draw(im)
    d.text((ax, ty), "NOUVELLE COLLECTION", font=M.SORAS(46 if not mobile else 50), fill=M.LAV if hasattr(M, "LAV") else (196, 181, 253), anchor=anc)
    M.grad_text(im, (ax, ty + 95), "L'élégance qui vous ressemble", M.SORA(52 if not mobile else 56), anchor=anc)
    d.text((ax, ty + 185), "Paiement à la livraison  •  Livraison partout en Algérie", font=M.SORAS(34 if not mobile else 30), fill=(237, 233, 254), anchor=anc)
    # call-to-action pill
    lab = "DÉCOUVRIR"; f = M.SORA(36); tw = d.textlength(lab, font=f)
    px = ax if anc == "lm" else ax - (tw + 100) / 2; py = ty + 250
    pill = Image.new("L", (W, H), 0); ImageDraw.Draw(pill).rounded_rectangle([px, py, px + tw + 100, py + 86], radius=43, fill=255)
    fill = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.paste_grad(fill, pill); im.alpha_composite(fill)
    ImageDraw.Draw(im).text((px + (tw + 100) / 2, py + 43), lab, font=f, fill="white", anchor="mm")
    im.convert("RGB").save(path, quality=92)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    wordmark(1.0).save(os.path.join(OUT, "logo_store.png"))                      # on dark backgrounds
    wordmark(1.0, fg=(42, 27, 94)).save(os.path.join(OUT, "logo_store_dark.png"))  # on white backgrounds
    banner(1920, 900, os.path.join(OUT, "banner_desktop.jpg"))
    banner(1080, 1350, os.path.join(OUT, "banner_mobile.jpg"), mobile=True)
    fav = M.bg(512, 512).convert("RGBA"); g = GV(420); m = Image.new("L", (512, 512), 0)
    ImageDraw.Draw(m).text((256, 270), "V", font=g, fill=255, anchor="mm"); M.paste_grad(fav, m)
    fav.convert("RGB").save(os.path.join(OUT, "favicon.png"))
    print("ok", os.listdir(OUT))
