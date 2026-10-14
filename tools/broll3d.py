#!/usr/bin/env python3
"""Animated pseudo-3D B-roll clips (own tiny renderer: perspective projection, flat shading, painter's sort).

  python3 tools/broll3d.py        -> assets/_generated/{product3d,trust3d,chat3d}.mp4  (540x960, 30fps, ~1.6s)
Brand palette C (night violet + violet + neon blue). Text sits in the upper half so the burned captions (at ~60% height) stay readable.
"""
import math, os, shutil, subprocess, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "_generated")
FPS, W, H, SS = 30, 540, 960, 2           # SS = supersampling for smooth edges
NAVY, SLATE, VIOLET, BLUE, SOFT = (20, 11, 52), (42, 27, 94), (139, 92, 246), (56, 189, 248), (196, 181, 253)   # palette C
SORA = lambda s: ImageFont.truetype(os.path.join(ROOT, "tools/fonts/Sora-ExtraBold.ttf"), int(s))
READEX = lambda s: ImageFont.truetype(os.path.join(ROOT, "tools/fonts/ReadexPro-Bold.ttf"), int(s))
ease = lambda t: 1 - (1 - min(max(t, 0), 1)) ** 3
back = lambda t: (lambda x: 1 + 2.70158 * (x - 1) ** 3 + 1.70158 * (x - 1) ** 2)(min(max(t, 0), 1))  # overshoot


def rot(ax, ay, az):
    cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def project(P, cx, cy, f=900, z0=600):
    z = P[:, 2] + z0
    return np.stack([cx + f * P[:, 0] / z, cy - f * P[:, 1] / z], 1), z


def shade(col, n, light=np.array([-0.4, 0.7, -0.6])):
    light = light / np.linalg.norm(light)
    k = 0.45 + 0.55 * max(0.0, float(np.dot(n, -light) * -1 if False else np.dot(n, light)))
    return tuple(int(min(255, c * k)) for c in col)


def background(t):
    im = Image.new("RGB", (W * SS, H * SS), NAVY)
    g = Image.new("RGBA", im.size, (0, 0, 0, 0))
    r = (0.55 + 0.05 * math.sin(t * 4)) * W * SS
    ImageDraw.Draw(g).ellipse([W * SS / 2 - r, H * SS * .3 - r, W * SS / 2 + r, H * SS * .3 + r], fill=VIOLET + (60,))
    g = g.filter(ImageFilter.GaussianBlur(70 * SS))
    im.paste(g, (0, 0), g)
    # perspective floor grid for depth
    d = ImageDraw.Draw(im)
    hz = H * SS * .50
    for i in range(-8, 9):
        d.line([(W * SS / 2 + i * 40 * SS, hz), (W * SS / 2 + i * 260 * SS, H * SS)], fill=(52, 34, 110), width=SS)
    for j in range(1, 9):
        y = hz + (H * SS - hz) * (j / 8) ** 2
        d.line([(0, y), (W * SS, y)], fill=(52, 34, 110), width=SS)
    return im


def text3d(im, xy, text, font, face=(255, 255, 255), side=(76, 29, 149), depth=10, t_in=1.0):
    """Extruded text: stacked darker copies give a solid 3D side."""
    d = ImageDraw.Draw(im)
    x, y = xy
    off = int(depth * t_in)
    for i in range(off, 0, -1):
        d.text((x + i * SS * 0.6, y + i * SS * 0.8), text, font=font, fill=side, anchor="mm", direction="rtl" if any("؀" <= c <= "ۿ" for c in text) else None)
    d.text((x, y), text, font=font, fill=face, anchor="mm", direction="rtl" if any("؀" <= c <= "ۿ" for c in text) else None)


def shadow(im, cx, cy, rx, ry, a=110):
    s = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(s).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(0, 0, 0, a))
    s = s.filter(ImageFilter.GaussianBlur(14 * SS))
    im.paste(s, (0, 0), s)


def box_faces(sx, sy, sz):
    v = np.array([[x, y, z] for x in (-sx, sx) for y in (-sy, sy) for z in (-sz, sz)], float)
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return v, faces


def product3d(n_secs=1.7):
    d = tempfile.mkdtemp()
    v, faces = box_faces(72, 56, 72)
    card = (196, 143, 88)
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = background(t)
        k = back(t / 0.45)
        R = rot(-0.45 + 0.1 * math.sin(t * 2), 0.6 + t * 1.6, 0.05 * math.sin(t * 3))
        P = (v * k) @ R.T
        P[:, 1] += 15 * math.sin(t * 5)
        cx, cy = W * SS / 2, H * SS * .22
        shadow(im, cx, H * SS * .33, 120 * SS * k, 18 * SS * k)
        pts, z = project(P * SS, cx, cy, f=900 * SS, z0=600 * SS)
        dr = ImageDraw.Draw(im)
        order = sorted(range(6), key=lambda i: -np.mean(z[list(faces[i])]))
        for i in order:
            idx = list(faces[i])
            a, b, c = P[idx[0]], P[idx[1]], P[idx[2]]
            n = np.cross(b - a, c - a); n = n / (np.linalg.norm(n) + 1e-9)
            if n[2] > 0.02:  # back-face culling (camera looks +z)
                continue
            dr.polygon([tuple(pts[j]) for j in idx], fill=shade(card, -n))
            # tape stripe across each visible face
            q = np.array([P[j] for j in idx])
            mid = (q[0] + q[1]) / 2, (q[3] + q[2]) / 2
            w = 0.12
            stripe = [q[0] + (q[1] - q[0]) * (0.5 - w), q[0] + (q[1] - q[0]) * (0.5 + w), q[3] + (q[2] - q[3]) * (0.5 + w), q[3] + (q[2] - q[3]) * (0.5 - w)]
            sp, _ = project(np.array(stripe) * SS, cx, cy, f=900 * SS, z0=600 * SS)
            dr.polygon([tuple(p) for p in sp], fill=shade((225, 195, 140), -n))
        k2 = ease((t - 0.15) / 0.3)
        text3d(im, (W * SS / 2, H * SS * .40 - 30 * SS * (1 - k2)), "PRODUIT", SORA(70 * SS), depth=12 * SS, t_in=k2)
        ImageDraw.Draw(im).text((W * SS / 2, H * SS * .50), "المنتوج في يدك", font=READEX(50 * SS), fill=BLUE, anchor="mm", direction="rtl")
        im.resize((W, H), Image.LANCZOS).save(f"{d}/{f+1:04d}.png")
    return d


def trust3d(n_secs=1.7):
    """Gold coin spinning in 3D (with visible edge thickness) carrying the handshake."""
    d = tempfile.mkdtemp()
    fe = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    em = Image.new("RGBA", (140, 130), (0, 0, 0, 0)); ImageDraw.Draw(em).text((0, 0), "🤝", font=fe, embedded_color=True)
    em = em.crop(em.getbbox())
    R0 = 150 * SS
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        im = background(t)
        ang = (1 - ease(t / 0.7)) * 3 * math.pi       # spins 1.5 turns then lands facing us
        c = math.cos(ang)
        cx, cy = W * SS / 2, H * SS * .25 + 10 * SS * math.sin(t * 5)
        shadow(im, cx, H * SS * .40, 160 * SS, 22 * SS)
        dr = ImageDraw.Draw(im)
        rx = max(abs(c) * R0, 6 * SS)
        th = 22 * SS * abs(math.sin(ang))           # edge thickness visible when side-on
        for i in range(int(th), 0, -SS):
            dr.ellipse([cx - rx + i * (1 if c >= 0 else -1), cy - R0, cx + rx + i * (1 if c >= 0 else -1), cy + R0], fill=(170, 110, 20))
        dr.ellipse([cx - rx, cy - R0, cx + rx, cy + R0], fill=(255, 190, 60))
        dr.ellipse([cx - rx * .86, cy - R0 * .86, cx + rx * .86, cy + R0 * .86], fill=(255, 210, 90), outline=(220, 150, 30), width=4 * SS)
        if abs(c) > 0.15:
            e = em.resize((max(1, int(190 * SS * abs(c))), int(190 * SS * em.height / em.width)), Image.LANCZOS)
            if c < 0: e = e.transpose(Image.FLIP_LEFT_RIGHT)
            im.paste(e, (int(cx - e.width / 2), int(cy - e.height / 2)), e)
        k2 = ease((t - 0.3) / 0.35)
        text3d(im, (W * SS / 2, H * SS * .41 - 30 * SS * (1 - k2)), "CONFIANCE", SORA(58 * SS), depth=12 * SS, t_in=k2)
        ImageDraw.Draw(im).text((W * SS / 2, H * SS * .505), "الثقة تاع البنادم", font=READEX(48 * SS), fill=BLUE, anchor="mm", direction="rtl")
        im.resize((W, H), Image.LANCZOS).save(f"{d}/{f+1:04d}.png")
    return d


def _coeffs(dst, src):
    A, B = [], []
    for (x, y), (X, Y) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -X * x, -X * y], [0, 0, 0, x, y, 1, -Y * x, -Y * y]]
        B += [X, Y]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def chat3d(n_secs=1.8):
    """Phone in perspective swinging toward us while customer messages pop in."""
    d = tempfile.mkdtemp()
    PW, PH = 300 * SS, 560 * SS
    msgs = [("السلام، المنتوج متوفر؟", 0.08, False), ("إيه خويا، متوفر", 0.33, True), ("نحب نكوموندي واحد", 0.58, False)]
    font = READEX(23 * SS)
    for f in range(int(n_secs * FPS)):
        t = f / FPS
        ph = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        pd = ImageDraw.Draw(ph)
        pd.rounded_rectangle([0, 0, PW - 1, PH - 1], radius=46 * SS, fill=(20, 20, 24))
        pd.rounded_rectangle([10 * SS, 10 * SS, PW - 10 * SS, PH - 10 * SS], radius=38 * SS, fill=(11, 20, 26))
        pd.rectangle([10 * SS, 40 * SS, PW - 10 * SS, 90 * SS], fill=(0, 92, 75))
        pd.text((PW / 2, 65 * SS), "WhatsApp", font=SORA(26 * SS), fill=(255, 255, 255), anchor="mm")
        y = 115 * SS
        for txt, st, mine in msgs:
            k = back((t - st) / 0.2)
            if k <= 0: continue
            w = pd.textlength(txt, font=font, direction="rtl") + 36 * SS
            x0 = PW - 24 * SS - w if not mine else 24 * SS
            bw, bh = w * k, 54 * SS * k
            pd.rounded_rectangle([x0, y, x0 + bw, y + bh], radius=18 * SS, fill=(32, 44, 51) if not mine else (0, 92, 75))
            if k > 0.8:
                pd.text((x0 + w - 18 * SS, y + 27 * SS), txt, font=font, fill=(255, 255, 255), anchor="rm", direction="rtl")
            y += 74 * SS
        im = background(t).convert("RGBA")
        ay = (1 - ease(t / 0.55)) * 0.9 - 0.12        # swing from 50deg to -7deg
        ax = 0.12
        R = rot(ax, ay, 0)
        corners = np.array([[-PW / 2, PH / 2, 0], [PW / 2, PH / 2, 0], [PW / 2, -PH / 2, 0], [-PW / 2, -PH / 2, 0]]) @ R.T
        cx, cy = W * SS / 2, H * SS * .30
        pts, _ = project(corners, cx, cy, f=1400 * SS, z0=1500 * SS)
        shadow(im, cx + 20 * SS, H * SS * .58, 170 * SS, 26 * SS)
        coeffs = _coeffs([tuple(p) for p in pts], [(0, 0), (PW, 0), (PW, PH), (0, PH)])
        warped = ph.transform(im.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)
        im.alpha_composite(warped)
        im.convert("RGB").resize((W, H), Image.LANCZOS).save(f"{d}/{f+1:04d}.png")
    return d


def encode(frames, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{frames}/%04d.png",
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], check=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("product3d", product3d), ("trust3d", trust3d), ("chat3d", chat3d)):
        fr = fn(); encode(fr, os.path.join(OUT, name + ".mp4")); shutil.rmtree(fr, ignore_errors=True)
        print("wrote", name)
