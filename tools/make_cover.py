#!/usr/bin/env python3
"""Instagram Reel cover (1080x1920, all text inside the 1080x1440 centre crop the profile grid shows), identity C.
  python3 tools/make_cover.py frame.png out.png "E-COM TIP" "#01" "الحلقة 01" "فيديو شباب" "وما جابليش؟"
  python3 tools/make_cover.py --plain frame.png out.png "نصيحة للتجار" "ما تجيكش" "ساهلة!" "حضّر السكريبت قبل ما تصوّر"
"""
import os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_identity as M

W, H = 1080, 1920
TOP, BOT = 240, 1680                       # 3:4 grid crop
SHIFT = 170                                # move the video frame down


def face_card(frame, size=700):
    """Square crop centred on his face (OpenCV), as a rounded card with a violet -> blue neon rim."""
    import cv2, numpy as np
    src = Image.open(frame).convert("RGB")
    g = cv2.cvtColor(np.array(src), cv2.COLOR_RGB2GRAY)
    faces = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml").detectMultiScale(g, 1.1, 5, minSize=(60, 60))
    if len(faces):
        x, y, w, h = min(faces, key=lambda f: f[1]); cx, cy, side = x + w / 2, y + h * 0.62, w * 2.3   # top-most face (a printed face on a T-shirt sits lower)
    else:
        cx, cy, side = src.width / 2, src.height * 0.42, src.width * 0.8
    side = min(side, src.width, src.height)
    x0 = min(max(0, cx - side / 2), src.width - side); y0 = min(max(0, cy - side / 2), src.height - side)
    crop = src.crop((int(x0), int(y0), int(x0 + side), int(y0 + side))).resize((size, size), Image.LANCZOS)
    crop = ImageEnhance.Contrast(crop).enhance(1.06).filter(ImageFilter.UnsharpMask(2, 90, 2))
    R, rim = 60, 8
    card = Image.new("RGBA", (size + 2 * rim + 80, size + 2 * rim + 80), (0, 0, 0, 0)); o = 40
    m = Image.new("L", card.size, 0); ImageDraw.Draw(m).rounded_rectangle([o, o, o + size + 2 * rim, o + size + 2 * rim], radius=R + rim, fill=255)
    glow = Image.new("RGBA", card.size, (0, 0, 0, 0)); M.paste_grad(glow, m)
    card.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22))); card.alpha_composite(glow)
    mm = Image.new("L", (size, size), 0); ImageDraw.Draw(mm).rounded_rectangle([0, 0, size - 1, size - 1], radius=R, fill=255)
    card.paste(crop, (o + rim, o + rim), mm)
    return card


def cover(frame, out, series, num, pill, line1, line2):
    im = M.bg(W, H).convert("RGBA")
    card = face_card(frame)
    im.alpha_composite(card, ((W - card.width) // 2, 575))
    return finish(im, out, series, num, pill, line1, line2)


def cover_plain(frame, out, kicker, title1, title2, sub):
    """Cover for a reel outside the series: kicker pill, big 2-line title (line 2 in the gradient), face card, one sub line."""
    im = M.bg(W, H).convert("RGBA")
    pf = M.READ(44); d = ImageDraw.Draw(im); tw = d.textlength(kicker, font=pf)
    pw, ph = tw + 80, 82; px, py = (W - pw) / 2, TOP + 40
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([px, py, px + pw, py + ph], radius=ph // 2, fill=255)
    fill = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.paste_grad(fill, m); im.alpha_composite(fill)
    ImageDraw.Draw(im).text((W / 2, py + ph / 2 + 2), kicker, font=pf, fill="white", anchor="mm")
    ft = M.READ(150)
    for txt, y, grad in ((title1, TOP + 225, False), (title2, TOP + 390, True)):
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((W / 2, y), txt, font=ft, fill=(139, 92, 246, 255) if grad else (0, 0, 0, 190), anchor="mm")
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20 if grad else 8)))
        if grad:
            M.grad_text(im, (W / 2, y), txt, ft, anchor="mm")
        else:
            ImageDraw.Draw(im).text((W / 2, y), txt, font=ft, fill="white", anchor="mm")
    card = face_card(frame, 620)
    im.alpha_composite(card, ((W - card.width) // 2, TOP + 470))
    fs = M.READ(60)
    ImageDraw.Draw(im).text((W / 2, BOT - 70), sub, font=fs, fill=(237, 233, 254), anchor="mm")
    logo = M.ICON.resize((76, 76), Image.LANCZOS)
    hf = M.SORAS(40); hw = ImageDraw.Draw(im).textlength("@kabli_ms", font=hf)
    x0 = (W - (76 + 16 + hw)) / 2; y0 = BOT + 60
    im.alpha_composite(logo, (int(x0), int(y0 - 38)))
    ImageDraw.Draw(im).text((x0 + 92, y0), "@kabli_ms", font=hf, fill=(237, 233, 254), anchor="lm")
    im.convert("RGB").save(out, quality=95)
    print(out)


def cover_full(frame, out, series, num, pill, line1, line2):
    im = Image.open(frame).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    shifted = Image.new("RGB", (W, H), (20, 11, 52)); shifted.paste(im, (0, SHIFT))
    fade = Image.new("L", (W, H), 255); fd = ImageDraw.Draw(fade)
    for y in range(SHIFT, SHIFT + 220):
        fd.line([(0, y), (W, y)], fill=int(255 * (1 - (y - SHIFT) / 220)))
    shifted.paste(Image.new("RGB", (W, H), (20, 11, 52)), (0, 0), fade.point(lambda v: v if v < 255 else 0)); im = shifted   # face lower: room for the title
    im = ImageEnhance.Contrast(im).enhance(1.08).filter(ImageFilter.UnsharpMask(2, 80, 2))
    im = ImageEnhance.Brightness(im).enhance(0.88).convert("RGBA")
    # violet night gradients top + bottom so the text reads, face stays natural in the middle
    g = Image.new("RGBA", (W, H)); gd = ImageDraw.Draw(g)
    for y in range(H):
        a = max(0, 1 - (y - TOP) / 560) if y < TOP + 560 else max(0, (y - 1060) / 620)
        gd.line([(0, y), (W, y)], fill=(20, 11, 52, int(235 * min(1, a))))
    im.alpha_composite(g)
    return finish(im, out, series, num, pill, line1, line2)


def finish(im, out, series, num, pill, line1, line2):
    d = ImageDraw.Draw(im)
    # series name + big episode number (neon gradient + glow)
    f1 = M.SORA(92); f2 = M.SORA(230)
    for txt, f, y in ((series, f1, TOP + 40), (num, f2, TOP + 190)):
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((W / 2, y), txt, font=f, fill=(139, 92, 246, 255), anchor="mm")
        im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22)))
        M.grad_text(im, (W / 2, y), txt, f, anchor="mm")
    # episode pill
    pf = M.READ(46); d = ImageDraw.Draw(im); tw = d.textlength(pill, font=pf)
    pw, ph = tw + 80, 84; px, py = (W - pw) / 2, TOP + 280
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([px, py, px + pw, py + ph], radius=ph // 2, fill=255)
    fill = Image.new("RGBA", (W, H), (0, 0, 0, 0)); M.paste_grad(fill, m); im.alpha_composite(fill)
    ImageDraw.Draw(im).text((W / 2, py + ph / 2 + 2), pill, font=pf, fill="white", anchor="mm")
    # hook lines at the bottom
    d = ImageDraw.Draw(im)
    fa = M.READ(104)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((W / 2 + 4, BOT - 205 + 6), line1, font=fa, fill=(0, 0, 0, 200), anchor="mm")
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).text((W / 2, BOT - 205), line1, font=fa, fill="white", anchor="mm")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((W / 2, BOT - 75), line2, font=fa, fill=(56, 189, 248, 255), anchor="mm")
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
    M.grad_text(im, (W / 2, BOT - 75), line2, fa, anchor="mm")
    # handle + small logo at the very bottom of the grid zone
    logo = M.ICON.resize((76, 76), Image.LANCZOS)
    hf = M.SORAS(40); hw = ImageDraw.Draw(im).textlength("@kabli_ms", font=hf)
    x0 = (W - (76 + 16 + hw)) / 2; y0 = BOT + 60
    im.alpha_composite(logo, (int(x0), int(y0 - 38)))
    ImageDraw.Draw(im).text((x0 + 92, y0), "@kabli_ms", font=hf, fill=(237, 233, 254), anchor="lm")
    im.convert("RGB").save(out, quality=95)
    print(out)


if __name__ == "__main__":
    if sys.argv[1] == "--plain":     # make_cover.py --plain frame out "kicker" "title 1" "title 2" "sub line"
        cover_plain(*sys.argv[2:8])
    else:
        cover(*sys.argv[1:8])
