#!/usr/bin/env python3
"""Visual identity pack for @kabli_ms e-commerce tips content, palette C (violet + neon blue) -> assets/brand/identity/
   python3 tools/make_logo.py && python3 tools/make_identity.py   (needs pillow with raqm)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets/brand/identity")
F = lambda n, s: ImageFont.truetype(os.path.join(ROOT, "tools/fonts", n), int(s))
SORA = lambda s: F("Sora-ExtraBold.ttf", s)       # Latin headlines, numbers
SORAS = lambda s: F("Sora-SemiBold.ttf", s)       # Latin labels
READ = lambda s: F("ReadexPro-Bold.ttf", s)       # Arabic headlines
READM = lambda s: F("ReadexPro-Medium.ttf", s)    # Arabic body
RUQ = lambda s: F("ArefRuqaa-Bold.ttf", s)        # script accent
NIGHT, DEEP, VIOLET, BLUE, WHITE, INK = (20, 11, 52), (42, 27, 94), (139, 92, 246), (56, 189, 248), (255, 255, 255), (11, 6, 32)
LAV, ICE, MUTED = (196, 181, 253), (186, 230, 253), (110, 100, 150)
MARK = Image.open(os.path.join(ROOT, "assets/brand/logo_mark_white.png")).convert("RGBA")
ICON = Image.open(os.path.join(ROOT, "assets/brand/logo_mark.png")).convert("RGBA")


def lerp(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def hgrad(w, h, c0=VIOLET, c1=BLUE):
    g = Image.new("RGB", (w, h)); d = ImageDraw.Draw(g)
    for x in range(w):
        d.line([(x, 0), (x, h)], fill=lerp(c0, c1, x / max(1, w - 1)))
    return g


def paste_grad(im, mask, c0=VIOLET, c1=BLUE):
    """Fill the white parts of an L mask with the violet -> blue gradient."""
    im.paste(hgrad(im.width, im.height, c0, c1), (0, 0), mask)


def bg(w, h):
    im = Image.new("RGB", (w, h)); px = ImageDraw.Draw(im)
    for y in range(h):
        px.line([(0, y), (w, y)], fill=lerp((30, 18, 78), INK, y / h))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse([w * .35, -h * .15, w * 1.3, h * .45], fill=VIOLET + (80,))
    gd.ellipse([-w * .4, h * .55, w * .5, h * 1.1], fill=BLUE + (45,))
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    im.paste(glow, (0, 0), glow)
    return im


def fit(d, t, font_fn, size, maxw):
    while size > 20 and d.textlength(t, font=font_fn(size)) > maxw:
        size -= 4
    return font_fn(size)


def wrap(d, t, font, maxw):
    lines, cur = [], ""
    for w in t.split():
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= maxw:
            cur = trial
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def glass(im, box, radius=36):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, radius=radius, fill=(255, 255, 255, 18))
    out = Image.alpha_composite(im.convert("RGBA"), ov)
    ring = Image.new("L", im.size, 0)
    ImageDraw.Draw(ring).rounded_rectangle(box, radius=radius, outline=255, width=3)
    out = out.convert("RGB"); paste_grad(out, ring)
    im.paste(out)


def chip(im, x, y, label, font, pad=26):
    d = ImageDraw.Draw(im)
    w = d.textlength(label, font=font); h = font.size + pad
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([x, y, x + w + pad * 2, y + h], radius=h // 2, fill=255)
    paste_grad(im, m)
    ImageDraw.Draw(im).text((x + pad, y + h / 2), label, font=font, fill=WHITE, anchor="lm")
    return x + w + pad * 2


def paste_mark(im, size, xy, src=MARK):
    m = src.resize((size, size), Image.LANCZOS)
    im.paste(m, xy, m)


def grad_text(im, xy, t, font, anchor="la"):
    """Text filled with the violet -> blue gradient."""
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).text(xy, t, font=font, fill=255, anchor=anchor)
    x0, _, x1, _ = m.getbbox() or (0, 0, im.width, 0)
    g = Image.new("RGB", im.size); g.paste(hgrad(max(1, x1 - x0), im.height, VIOLET, BLUE), (x0, 0))
    im.paste(g, (0, 0), m)


def sample_caption(path):
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import edit_reel
    edit_reel.render_caption_png("*باش تبيع*", path, None, size=110)
    return Image.open(path).convert("RGBA")


def brand_board():
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), (246, 244, 252))
    left = bg(760, H); im.paste(left, (0, 0))
    d = ImageDraw.Draw(im)
    paste_mark(im, 300, (230, 90), ICON)
    d.text((380, 500), "KABLI_MS", font=SORA(96), fill=WHITE, anchor="mm")
    im.paste(hgrad(140, 10), (310, 560))
    d.text((380, 620), "E-COMMERCE  •  SPONSOR  •  META ADS", font=SORAS(24), fill=LAV, anchor="mm")
    cap = sample_caption(os.path.join(OUT, "_caption_sample.png"))
    cap = cap.resize((int(cap.width * .78), int(cap.height * .78)), Image.LANCZOS)
    im.paste(cap, (380 - cap.width // 2, 690), cap)
    os.remove(os.path.join(OUT, "_caption_sample.png"))
    d.text((380, 1010), "نصائح عملية للتجار المبتدئين", font=READM(30), fill=ICE, anchor="mm")
    d.text((840, 80), "PALETTE", font=SORA(30), fill=NIGHT)
    sw = [("Night Violet", "#140B34", NIGHT, "الخلفية"), ("Deep Violet", "#2A1B5E", DEEP, "البطاقات · العمق"),
          ("Violet", "#8B5CF6", VIOLET, "اللون الأساسي"), ("Neon Blue", "#38BDF8", BLUE, "النيون · الكلمة المهمة"),
          ("White", "#FFFFFF", WHITE, "النص")]
    for i, (n, hx, c, use) in enumerate(sw):
        x = 840 + i * 205
        d.rounded_rectangle([x, 140, x + 185, 380], radius=26, fill=c, outline=(215, 210, 235), width=2)
        d.text((x + 12, 400), n, font=SORA(21), fill=NIGHT)
        d.text((x + 12, 432), hx, font=SORAS(20), fill=MUTED)
        d.text((x + 173, 470), use, font=READM(20), fill=MUTED, anchor="ra")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([840, 515, 1840, 545], radius=15, fill=255)
    paste_grad(im, m)
    d.text((840, 580), "TYPOGRAPHY", font=SORA(30), fill=NIGHT)
    d.text((840, 630), "Sora ExtraBold — HEADLINES", font=SORA(52), fill=NIGHT)
    d.text((840, 710), "Sora SemiBold — labels, numbers 0550 20 54 64", font=SORAS(30), fill=NIGHT)
    d.text((1840, 770), "Readex Pro — العناوين والترجمة بالعربية", font=READ(46), fill=NIGHT, anchor="ra")
    d.text((1840, 845), "Aref Ruqaa — لمسة بخط اليد", font=RUQ(46), fill=VIOLET, anchor="ra")
    grad_text(im, (840, 935), "RULE: key words only · neon ice-blue » violet + one script word", SORA(25))
    d.text((840, 985), "Hook in 2 seconds · one intro zoom · CTA = WhatsApp", font=SORAS(25), fill=MUTED)
    im.save(os.path.join(OUT, "brand_board.png"))


def reel_cover():
    W, H = 1080, 1920
    im = bg(W, H)
    chip(im, 80, 150, "TIP E-COMMERCE", SORA(38))
    d = ImageDraw.Draw(im)
    lines = [("3 AKHTA2", False), ("TOUSSAR", True), ("L SPONSOR", False)]
    for i, (t, acc) in enumerate(lines):
        f = fit(d, t, SORA, 190, 920)
        if acc:
            grad_text(im, (80, 360 + i * 270), t, f)
        else:
            d.text((80, 360 + i * 270), t, font=f, fill=WHITE)
    d.text((1000, 1290), "3 أخطاء تحرق ميزانية الإعلان تاعك", font=READ(56), fill=ICE, anchor="ra")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).line([(80, 1500), (1000, 1500)], fill=255, width=4)
    paste_grad(im, m)
    paste_mark(im, 210, (70, 1550), ICON)
    d.text((310, 1625), "@kabli_ms", font=SORA(56), fill=WHITE, anchor="lm")
    d.text((310, 1700), "WhatsApp 0550 20 54 64", font=SORAS(34), fill=LAV, anchor="lm")
    im.save(os.path.join(OUT, "reel_cover_template.png"))


def tip_post(n=1, title="ZID L BUDGET B 20% KOL YOMEIN", sub="ما تكبّرش الميزانية دفعة وحدة، وراقب السعر في كل مرة.", name="tip_post_template.png"):
    W, H = 1080, 1350
    im = bg(W, H)
    x = chip(im, 80, 90, "TIP", SORA(40))
    grad_text(im, (x + 30, 128), f"#{n}", SORA(110), anchor="lm")
    d = ImageDraw.Draw(im)
    tf = SORA(108)
    y = 270
    for ln in wrap(d, title.upper(), tf, 920):
        d.text((80, y), ln, font=tf, fill=WHITE)
        y += 130
    glass(im, [80, 790, 1000, 1060])
    d = ImageDraw.Draw(im)
    y = 865
    for ln in wrap(d, sub, READ(48), 820):
        d.text((540, y), ln, font=READ(48), fill=WHITE, anchor="mm")
        y += 76
    paste_mark(im, 130, (70, 1140), ICON)
    d.text((220, 1205), "@kabli_ms", font=SORA(44), fill=WHITE, anchor="lm")
    grad_text(im, (1000, 1205), "SWIPE  »", SORA(34), anchor="rm")
    im.save(os.path.join(OUT, name))


def icon(kind, d, cx, cy, s, col, acc=BLUE):
    w = max(8, s // 11)
    if kind == "tips":      # lightbulb
        d.ellipse([cx - s * .32, cy - s * .5, cx + s * .32, cy + s * .14], outline=col, width=w)
        d.rectangle([cx - s * .16, cy + s * .2, cx + s * .16, cy + s * .28], fill=col)
        d.rectangle([cx - s * .1, cy + s * .34, cx + s * .1, cy + s * .4], fill=col)
    elif kind == "ads":     # megaphone
        d.polygon([(cx - s * .4, cy - s * .12), (cx - s * .1, cy - s * .12), (cx + s * .38, cy - s * .42), (cx + s * .38, cy + s * .42), (cx - s * .1, cy + s * .12), (cx - s * .4, cy + s * .12)], outline=col, width=w)
        d.rectangle([cx - s * .32, cy + s * .12, cx - s * .16, cy + s * .42], outline=col, width=w)
    elif kind == "store":   # cart
        d.line([(cx - s * .5, cy - s * .38), (cx - s * .32, cy - s * .38), (cx - s * .15, cy + s * .2), (cx + s * .36, cy + s * .2), (cx + s * .46, cy - s * .2), (cx - s * .27, cy - s * .2)], fill=col, width=w, joint="curve")
        for x in (cx - s * .08, cx + s * .3):
            d.ellipse([x - s * .08, cy + s * .3, x + s * .08, cy + s * .46], fill=col)
    elif kind == "results": # chart + arrow
        for i, h in enumerate((.2, .35, .55)):
            x = cx - s * .42 + i * s * .3
            d.rectangle([x, cy + s * .4 - s * h, x + s * .2, cy + s * .4], fill=col)
        d.line([(cx - s * .45, cy - s * .05), (cx - s * .05, cy - s * .3), (cx + s * .15, cy - s * .15), (cx + s * .46, cy - s * .48)], fill=acc, width=w, joint="curve")
        d.polygon([(cx + s * .5, cy - s * .52), (cx + s * .3, cy - s * .5), (cx + s * .48, cy - s * .32)], fill=acc)


def highlights():
    """Instagram highlight covers in Mustafa's neon glass icon style (his reference images): night-violet background
    with a corner glow, one glass app-icon in the centre (fits the round crop), no text (IG shows the title)."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import neon_icons
    items = [("tips", "lightbulb"), ("ads", "campaign"), ("store", "storefront"), ("results", "trending_up"),
             ("me", "person"), ("contact", "chat")]
    for kind, icon in items:
        S = 1080
        im = Image.new("RGB", (S, S)); d = ImageDraw.Draw(im)
        for y in range(S):
            d.line([(0, y), (S, y)], fill=lerp((26, 15, 62), (10, 6, 28), y / S))
        g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([S * .55, -S * .45, S * 1.45, S * .45], fill=(120, 60, 170, 90))
        g = g.filter(ImageFilter.GaussianBlur(160)); im.paste(g, (0, 0), g)
        t = neon_icons.tile(icon, 600)
        im.paste(t, ((S - t.width) // 2, (S - t.height) // 2 + 10), t)
        im.save(os.path.join(OUT, f"highlight_{kind}.png"))


def canva_backgrounds():
    """Text-free backgrounds for the editable Canva templates (texts are Canva text boxes on top)."""
    def grid(im, step=72, alpha=18):
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for x in range(0, im.width, step): d.line([(x, 0), (x, im.height)], fill=LAV + (alpha,), width=1)
        for y in range(0, im.height, step): d.line([(0, y), (im.width, y)], fill=LAV + (alpha,), width=1)
        return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    def pill(im, box):
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=255)
        paste_grad(im, m)
    p = grid(bg(1080, 1350)); pill(p, [80, 90, 236, 156]); glass(p, [80, 790, 1000, 1060])
    p.save(os.path.join(OUT, "canva_bg_post.png"))
    c = grid(bg(1080, 1920)); pill(c, [80, 150, 560, 224])
    m = Image.new("L", c.size, 0); ImageDraw.Draw(m).line([(80, 1500), (1000, 1500)], fill=255, width=4); paste_grad(c, m)
    c.save(os.path.join(OUT, "canva_bg_cover.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    brand_board(); reel_cover(); tip_post(); highlights(); canva_backgrounds()
    print(sorted(os.listdir(OUT)))
