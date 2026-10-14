#!/usr/bin/env python3
"""Mustafa reel editor: silence cut -> 1080x1920 -> light grade -> subtitles -> brand end card.

Usage:
  python3 tools/edit_reel.py videos/reel2.mov [--srt subs.srt] [--no-silence-cut] [--no-endcard]
Output: videos/<name>_v1.mp4  (use --out to change)

Subtitles come from an .srt written from Mustafa's script (timings relative to the ORIGINAL
video unless --srt-after-cut is passed). Brand colors / contacts live in BRAND below.
"""
import argparse, os, re, subprocess, sys, tempfile

BRAND = dict(navy="140B34", blue="2A1B5E", accent="8B5CF6", neon="38BDF8",  # palette C: night violet + violet + neon blue
             whatsapp="0550 20 54 64", handle="@kabli_ms",
             cta="راسلني على واتساب")
FONT = "Sora ExtraBold"  # Latin caption font for libass (static instance in tools/fonts); Arabic falls back to DejaVu Sans
FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
AR_BOLD, LAT_BOLD, LAT_SEMI = "ReadexPro-Bold.ttf", "Sora-ExtraBold.ttf", "Sora-SemiBold.ttf"   # brand fonts (palette C)
ACCENT = BRAND["accent"]   # words wrapped as *word* in the .srt get this colour
TEXT_COLOR = "FFFFFF"
ACCENT_NEON = "38BDF8"   # neon blue = middle of the neon caption gradient
VIOLET, BLUE, NIGHT = (139, 92, 246), (56, 189, 248), (20, 11, 52)
# neon caption (chosen variant B): ice-blue top -> neon blue -> violet bottom, ice halo, violet wide glow + blue tight glow
CAP_TOP, CAP_DEEP, CAP_HALO, CAP_GLOW_WIDE, CAP_GLOW_TIGHT = (186, 230, 253), VIOLET, (224, 242, 254), VIOLET, BLUE
SCRIPT_DY_AR = 0.76   # vertical offset (x bold size) of the Arabic script word under the bold line
W, H, ENDCARD_SECS = 1080, 1920, 3.0
# warm golden/orange look + soft vignette (style reference: nazih_motivation reels)
GRADES = {
    "warm": "eq=contrast=1.12:saturation=1.2:brightness=-0.02,colorbalance=rs=0.05:gs=0.01:bs=-0.07:rm=0.06:bm=-0.05:rh=0.04:bh=-0.04,vignette=PI/5",
    "none": "null",   # keep his original colours/filter untouched
    "natural": "eq=contrast=1.06:saturation=1.1",
    # skin-friendly: light denoise, highlights rolled off (bright sunroof light on the face), less red in skin, soft vignette
    "pro": "hqdn3d=2:1:3:3,curves=master='0/0 0.25/0.22 0.6/0.6 0.85/0.81 1/0.94',colorbalance=rm=-0.04:bm=0.02:rh=-0.05:bh=0.03,eq=contrast=1.1:saturation=1.08,vignette=PI/6",
    "cinema": "eq=contrast=1.15:saturation=1.05:brightness=-0.03,colorbalance=rs=-0.06:gs=0.0:bs=0.07:rh=0.07:gh=0.01:bh=-0.06,vignette=PI/4.5",   # teal shadows / orange highlights
    "bright": "eq=contrast=1.04:saturation=1.25:brightness=0.04,colorbalance=rm=0.02:bm=-0.02",   # clean, fresh, social look
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, text=True, **kw)


def probe_duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "csv=p=0", path], capture_output=True).stdout
    return float(out.strip())


def keep_segments(path, noise="-32dB", min_sil=0.35, pad=0.08):
    dur = probe_duration(path)
    err = subprocess.run(["ffmpeg", "-i", path, "-af",
                          f"silencedetect=n={noise}:d={min_sil}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    segs, cur = [], 0.0
    for i, s in enumerate(starts):
        if s - cur > 0.15:
            segs.append((max(0, cur - pad), min(dur, s + pad)))
        cur = ends[i] if i < len(ends) else dur
    if dur - cur > 0.15:
        segs.append((max(0, cur - pad), dur))
    return segs or [(0, dur)], dur


TAG_RE = re.compile(r"\[(sparks|flash|leak|money|broll|icon|shake|ding|circle|arrow|notif|doc)(?::([^\]]+))?\]", re.I)
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27bf]")


def srt_to_events(srt_text, offset_map=None):
    ev = []
    for blk in re.split(r"\n\s*\n", srt_text.strip()):
        lines = blk.strip().splitlines()
        m = next((re.match(r"(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)", l)
                  for l in lines if "-->" in l), None)
        if not m:
            continue
        g = list(map(int, m.groups()))
        a = g[0]*3600 + g[1]*60 + g[2] + g[3]/1000
        b = g[4]*3600 + g[5]*60 + g[6] + g[7]/1000
        text = " ".join(l for l in lines if "-->" not in l and not l.strip().isdigit())
        tags = [(m.group(1).lower(), (m.group(2) or "").strip()) for m in TAG_RE.finditer(text)]
        text = TAG_RE.sub("", text)
        emojis = EMOJI_RE.findall(text)  # libass can't draw colour emoji: strip from text, overlay as PNG instead
        text = re.sub(r"\s+", " ", EMOJI_RE.sub("", text).replace("\ufe0f", "")).strip()
        ev.append((a, b, text, emojis, tags))
    return ev


def remap(t, segs):
    """Map original timeline -> cut timeline."""
    acc = 0.0
    for a, b in segs:
        if t <= b:
            return acc + max(0, t - a)
        acc += b - a
    return acc


def ass_ts(t):
    h, m, s = int(t//3600), int(t % 3600//60), t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def bgr(hexrgb):  # ASS colour is BGR
    return f"&H00{hexrgb[4:6]}{hexrgb[2:4]}{hexrgb[0:2]}"


POP = r"{\\fscx85\\fscy85\\t(0,110,\\fscx100\\fscy100)}"


def style_text(t):
    """UPPERCASE Latin, pop-in animation, *word* -> accent colour. Arabic gets a font with Arabic glyphs."""
    arabic = bool(re.search(r"[\u0600-\u06ff]", t))
    base = r"{\fnDejaVu Sans\b1\fs104\fsp0\c&H00FFFFFF&\fscx100\fscy100}" if arabic else r"{\r}"
    t = t if arabic else (t.upper() if re.search(r"[A-Za-z]", t) else t)
    t = re.sub(r"\*([^*]+)\*", lambda m: f"{{\\c{bgr(ACCENT)}&}}{m.group(1)}{base}", t)
    return POP + (base if arabic else "") + t


def build_ass(events, total, with_endcard, tagline=""):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Sub,{FONT},128,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,2,0,1,5,3,2,80,200,700,1
Style: CardBig,{FONT},70,{bgr(BRAND['accent'])},&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1
Style: CardSmall,{FONT},64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [f"Dialogue: 0,{ass_ts(a)},{ass_ts(b)},Sub,,0,0,0,,{style_text(t)}" for a, b, t, *_ in events if t and not ARABIC_RE.search(t)]
    if with_endcard:
        s, e = ass_ts(total), ass_ts(total + ENDCARD_SECS)
        lines += [
            f"Dialogue: 0,{s},{e},CardSmall,,0,0,0,,{{\\pos({W//2},{H//2-260})}}{BRAND['cta']}",
            f"Dialogue: 0,{s},{e},CardBig,,0,0,0,,{{\\pos({W//2},{H//2-60})}}WhatsApp: {BRAND['whatsapp']}",
            f"Dialogue: 0,{s},{e},CardSmall,,0,0,0,,{{\\pos({W//2},{H//2+140})}}Instagram: {BRAND['handle']}",
        ]
        if tagline:
            lines.append(f"Dialogue: 0,{s},{e},CardBig,,0,0,0,,{{\\pos({W//2},{H//2-480})\\fs80\\c&H00FFFFFF&}}{tagline}")
    return head + "\n".join(lines) + "\n"


ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
ALIASES = {"sparks": "sparks_neon", "flash": "flash_white", "leak": "light_leak", "money": "money_rain"}


REMOTION = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "remotion")
TITLED = {"rm_cube", "rm_funnel", "rm_dress"}   # Remotion b-roll whose title = the caption words
REMOTION_COMPS = {"rm_badge": "BrandBadge", "rm_cube": "Cube3D", "rm_dress": "Dress3D", "rm_funnel": "Funnel", "rm_phone": "Phone3D", "rm_doc": "DocCard"}


def remotion_render(comp, out, props=None):
    """Render a Remotion composition (remotion/src) to an mp4 with the preinstalled headless Chromium."""
    import json, glob
    if not os.path.isdir(os.path.join(REMOTION, "node_modules")):
        run(["npm", "install", "--no-audit", "--no-fund"], cwd=REMOTION)
    chrome = (glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell") or [None])[0]
    cmd = ["npx", "remotion", "render", "src/index.ts", comp, os.path.abspath(out), "--log=error"]
    if chrome:
        cmd.append(f"--browser-executable={chrome}")
    if props:
        cmd.append("--props=" + json.dumps(props, ensure_ascii=False))
    run(cmd, cwd=REMOTION)
    return out


PALETTE_ID = "C-violet-neonblue-v1"   # change it when the brand look changes: cached generated clips are then rebuilt


def refresh_generated_cache():
    """assets/_generated holds clips rendered in the brand colours (git-ignored, all reproducible).
    If they were made with another palette, delete them so they are rebuilt in the current one."""
    import shutil
    gen = os.path.join(ASSETS, "_generated")
    stamp = os.path.join(gen, ".palette")
    old = open(stamp).read().strip() if os.path.exists(stamp) else None
    if os.path.isdir(gen) and old != PALETTE_ID:
        print(f"brand palette changed ({old} -> {PALETTE_ID}): rebuilding assets/_generated")
        shutil.rmtree(gen)
    os.makedirs(gen, exist_ok=True)
    open(stamp, "w").write(PALETTE_ID)


def render_endcard(tagline=""):
    """Animated end card (Remotion 'EndCard', 1080x1920, 3 s): logo pop + glow, handle, Arabic CTA, WhatsApp pill.
    Cached per text in assets/_generated; returns None if Remotion can't run (then the simple ASS card is used)."""
    import hashlib, json
    props = {"handle": BRAND["handle"], "whatsapp": BRAND["whatsapp"], "cta": BRAND["cta"],
             "tag": tagline or "E-COMMERCE • SPONSOR • META ADS"}
    key = hashlib.md5((PALETTE_ID + json.dumps(props, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()[:8]
    path = os.path.join(ASSETS, "_generated", f"rm_endcard_{key}.mp4")
    if not os.path.exists(path):
        try:
            remotion_render("EndCard", path, props)
        except Exception as e:
            print("end card: Remotion failed, using the simple card:", e)
            return None
    return path


def find_asset(kind, name):
    """User files (assets/sparks|broll|icons) win over generated ones (assets/_generated)."""
    name = ALIASES.get(name, name) if kind != "icon" else name
    dirs = [os.path.join(ASSETS, d) for d in ("sparks", "broll", "icons", "_generated")]
    for attempt in (0, 1):
        for d in dirs:
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if os.path.splitext(f)[0] == name:
                        return os.path.join(d, f)
        if attempt == 0 and name in REMOTION_COMPS:
            os.makedirs(os.path.join(ASSETS, "_generated"), exist_ok=True)
            remotion_render(REMOTION_COMPS[name], os.path.join(ASSETS, "_generated", name + ".mp4"))
            continue
        if attempt == 0:
            tools_dir = os.path.dirname(os.path.abspath(__file__))
            run([sys.executable, os.path.join(tools_dir, "broll3d.py" if name.endswith("3d") else "gen_assets.py")])
    sys.exit(f"asset '{name}' not found in assets/ (tag [{kind}:{name}])")


def sfx_pro_chime(tmp):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sfx_pro
    p = os.path.join(tmp, "pro_chime_end.wav"); sfx_pro.write(p, sfx_pro.chime()); return p


def make_sfx(tmp):
    """Tiny synthetic sound effects (no downloads): whoosh (filtered noise sweep) and pop."""
    out = {}
    specs = {
        "whoosh": ["-f", "lavfi", "-i", "anoisesrc=d=0.35:c=pink:a=0.8",
                   "-af", "highpass=f=400,lowpass=f=3500,afade=t=in:d=0.12,afade=t=out:st=0.15:d=0.2,volume=0.9"],
        "pop": ["-f", "lavfi", "-i", "sine=f=900:d=0.12",
                "-af", "afade=t=out:st=0.02:d=0.1,volume=0.8"],
        # caption sound: soft rising "bubble pop" (sine sweep 600 -> 1400 Hz, fast decay) instead of a noise click
        "click": ["-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(600*t+4500*t*t))*exp(-t*38)':d=0.11:s=48000",
                  "-af", "afade=t=in:d=0.004,volume=0.9"],
        "ding": ["-f", "lavfi", "-i", "sine=f=1318:d=0.6", "-f", "lavfi", "-i", "sine=f=1975:d=0.6",
                 "-filter_complex", "[0][1]amix=inputs=2,afade=t=out:st=0.01:d=0.58,volume=0.9"],
        "boom": ["-f", "lavfi", "-i", "sine=f=55:d=0.7",
                 "-af", "vibrato=f=6:d=0.3,afade=t=out:st=0.05:d=0.65,volume=1.6"],
    }
    for name, args in specs.items():
        path = os.path.join(tmp, name + ".wav")
        run(["ffmpeg", "-v", "error", "-y", *args, "-ar", "48000", "-ac", "2", path])
        out[name] = path
    return out


ARABIC_RE = re.compile(r"[\u0600-\u06ff]")


def render_caption_png(text, path, font_file, size=118, maxw=860, stacked=False):
    """NEON + SCRIPT caption (Mustafa's reference "Personal Branding"), brand colours (palette C):
    first word(s) in a big bold sans (Readex Pro / Sora) with a violet + neon-blue glow, the last word in white
    handwriting script overlapping its bottom-right with a soft white glow. One word -> bold neon only.
    Works for Arabic and French."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
    clean = re.sub(r"\*", "", text).strip()
    words = clean.split()
    ar = bool(ARABIC_RE.search(clean))
    bold_f = os.path.join(FONTS_DIR, AR_BOLD if ar else LAT_BOLD)
    scr_f = os.path.join(FONTS_DIR, "ArefRuqaa-Bold.ttf" if ar else "GreatVibes-Regular.ttf")
    if len(words) >= 2:
        k = max(1, len(words) - (2 if len(words) >= 4 else 1))
        top, bottom = " ".join(words[:k]), " ".join(words[k:])
    else:
        top, bottom = clean, ""
    def font(pth, sz):
        return ImageFont.truetype(pth, sz)
    tmpd = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bs = int(size * 1.05)
    while bs > 50 and tmpd.textlength(top, font=font(bold_f, bs)) > maxw:
        bs -= 6
    bf = font(bold_f, bs)
    ss = int(bs * (1.15 if ar else 0.95))
    while bottom and ss > 40 and tmpd.textlength(bottom, font=font(scr_f, ss)) > maxw * 0.9:
        ss -= 6
    sf = font(scr_f, ss)
    tw = tmpd.textlength(top, font=bf)
    sw = tmpd.textlength(bottom, font=sf) if bottom else 0
    pad = 60
    W2 = int(max(tw, sw) + pad * 2 + 40)
    H2 = int(bs * 1.25 + (ss * 0.95 if bottom else 0) + pad * 2)
    cx = W2 / 2
    ty = pad + bs * 0.62
    if stacked and bottom:   # hook: script word on its OWN row under the bold line, centred (no text over text)
        bb = tmpd.textbbox((0, 0), top, font=bf, anchor="mm"); sb = tmpd.textbbox((0, 0), bottom, font=sf, anchor="mm")
        ty = pad - bb[1]
        H2 = int(ty + bb[3] + bs * 0.10 - sb[1] + sb[3] + pad)
    accent = tuple(int(ACCENT_NEON[i:i + 2], 16) for i in (0, 2, 4))
    lay = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    def draw(img, xy, t, f, fill, stroke=0, sfill=None):
        ImageDraw.Draw(img).text(xy, t, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=sfill)
    # neon glow: wide neon-blue haze + tight violet glow, then crisp bold text with a lighter core
    for col, rad, n in ((CAP_GLOW_WIDE, 0.30, 2), (CAP_GLOW_TIGHT, 0.10, 1)):
        g = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); draw(g, (cx, ty), top, bf, col + (255,))
        for _ in range(n):
            lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(bs * rad)))
    shadow = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); draw(shadow, (cx + 4, ty + 6), top, bf, (0, 0, 0, 150))
    lay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))
    # bright outline halo, then a vertical gradient fill (ice-blue top -> neon blue -> violet bottom)
    halo = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    draw(halo, (cx, ty), top, bf, CAP_HALO + (255,), stroke=max(3, bs // 40), sfill=CAP_HALO + (255,))
    lay.alpha_composite(halo.filter(ImageFilter.GaussianBlur(1.2)))
    m = Image.new("L", (W2, H2), 0); ImageDraw.Draw(m).text((cx, ty), top, font=bf, fill=255, anchor="mm")
    grad = Image.new("RGBA", (W2, H2)); gd = ImageDraw.Draw(grad)
    y0, y1 = ty - bs * 0.55, ty + bs * 0.45
    for y in range(H2):
        k = min(1, max(0, (y - y0) / (y1 - y0)))
        c0, c1, c2 = CAP_TOP, accent, CAP_DEEP
        col = [int(c0[i] + (c1[i] - c0[i]) * k * 2) if k < .5 else int(c1[i] + (c2[i] - c1[i]) * (k - .5) * 2) for i in range(3)]
        gd.line([(0, y), (W2, y)], fill=tuple(col) + (255,))
    lay.paste(grad, (0, 0), m)
    top_half = Image.new("L", (W2, H2), 0); ImageDraw.Draw(top_half).rectangle([0, 0, W2, int(ty - bs * 0.05)], fill=60)
    shine = Image.new("RGBA", (W2, H2), (255, 255, 255, 0))
    shine.putalpha(ImageChops.multiply(m, top_half))                       # glossy top half, inside the letters only
    lay.alpha_composite(shine)
    if bottom:   # white script overlapping the bold line, shifted toward the reading end
        sx = cx + (tw - sw) / 2 * (-0.6 if ar else 0.6)
        sy = ty + bs * (SCRIPT_DY_AR if ar else 0.55)   # Readex Pro has deep dots below: drop the Arabic script word a bit more
        if stacked:
            sx, sy = cx, ty + bb[3] + bs * 0.10 - sb[1]
        wg = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); draw(wg, (sx, sy), bottom, sf, (255, 255, 255, 255))
        lay.alpha_composite(wg.filter(ImageFilter.GaussianBlur(ss * 0.12)))
        draw(lay, (sx, sy), bottom, sf, (255, 255, 255, 255), stroke=2, sfill=(30, 30, 30, 180))
    lay.save(path)
    return W2, H2


def render_hook_title_png(text, path):
    """Reference-reel hook (Mustafa 2026-10-09): big WHITE bold title, no plate, soft dark shadow; *word* = neon blue.
    Up to 2 lines (split at ' / ' or after the 2nd word when long)."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    clean = text.replace("*", "")
    lines = [l.strip() for l in (text.split(" / ") if " / " in text else [text])]
    if len(lines) == 1 and len(clean.split()) > 3:
        w = text.split(); lines = [" ".join(w[:2]), " ".join(w[2:])]
    W2 = 1000
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    def fnt(t, sz): return ImageFont.truetype(os.path.join(FONTS_DIR, AR_BOLD if ARABIC_RE.search(t) else LAT_BOLD), sz)
    sizes = []
    for l in lines:
        sz = 118
        while sz > 60 and tmp.textlength(l.replace("*", ""), font=fnt(l, sz)) > W2 - 60:
            sz -= 4
        sizes.append(sz)
    H2 = int(sum(s_ * 1.3 for s_ in sizes) + 60)
    lay = Image.new("RGBA", (W2, H2), (0, 0, 0, 0)); y = 30
    for l, sz in zip(lines, sizes):
        f = fnt(l, sz); parts = re.split(r"(\*[^*]+\*)", l)
        full = l.replace("*", ""); tw = tmp.textlength(full, font=f)
        sh = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((W2 / 2 + 3, y + sz * 0.65 + 6), full, font=f, fill=(0, 0, 0, 200), anchor="mm")
        lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        d = ImageDraw.Draw(lay)
        if ARABIC_RE.search(full):    # RTL: draw the whole line white, then re-draw accent words in blue at their measured spot
            d.text((W2 / 2, y + sz * 0.65), full, font=f, fill="white", anchor="mm", stroke_width=2, stroke_fill=(20, 11, 52))
            for p in parts:
                if p.startswith("*"):
                    w = p.strip("*"); i = full.find(w)
                    # position of the word inside an RTL line: measured from the right edge
                    xr = W2 / 2 + tw / 2 - tmp.textlength(full[:i], font=f)
                    d.text((xr, y + sz * 0.65), w, font=f, fill="#" + ACCENT_NEON, anchor="rm", stroke_width=2, stroke_fill=(20, 11, 52))
        else:
            x = W2 / 2 - tw / 2
            for p in parts:
                acc = p.startswith("*"); p = p.strip("*")
                d.text((x, y + sz * 0.65), p, font=f, fill=("#" + ACCENT_NEON) if acc else "white", anchor="lm", stroke_width=2, stroke_fill=(20, 11, 52))
                x += tmp.textlength(p, font=f)
        y += int(sz * 1.3)
    lay.crop(lay.getbbox()).save(path)
    return Image.open(path).size


def render_hook_png(text, path, font_file):
    """Hook card: huge text, accent words in the brand accent, on a rounded night-violet plate with a violet->blue neon rim."""
    from PIL import Image, ImageDraw
    cap = os.path.join(os.path.dirname(path), "hook_txt.png")
    if ARABIC_RE.search(text):
        cw, ch = render_caption_png(text, cap, font_file, size=104, maxw=800, stacked=True)
    else:
        from PIL import ImageFont
        f = ImageFont.truetype(os.path.join(FONTS_DIR, LAT_BOLD), 130)
        parts = re.split(r"(\*[^*]+\*)", text.upper())
        d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
        tw = sum(d0.textlength(p.strip("*"), font=f) for p in parts)
        cw, ch = int(tw) + 80, 230
        im0 = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im0); x = 40
        for p in parts:
            acc = p.startswith("*"); p = p.strip("*")
            d.text((x, ch / 2), p, font=f, fill="#" + ACCENT if acc else "#FFFFFF", anchor="lm", stroke_width=6, stroke_fill="#000000")
            x += d.textlength(p, font=f)
        im0.save(cap)
    txt = Image.open(cap)
    pad = 14
    im = Image.new("RGBA", (txt.width + pad * 2, txt.height + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=48, fill=NIGHT + (215,))
    ring = Image.new("L", im.size, 0)
    ImageDraw.Draw(ring).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=48, outline=255, width=6)
    grad = Image.new("RGBA", im.size); gd = ImageDraw.Draw(grad)
    for x in range(im.width):   # violet (left) -> neon blue (right)
        k = x / max(1, im.width - 1)
        gd.line([(x, 0), (x, im.height)], fill=tuple(int(VIOLET[j] + (BLUE[j] - VIOLET[j]) * k) for j in range(3)) + (255,))
    im.paste(grad, (0, 0), ring)
    im.alpha_composite(txt, (pad, pad))
    im.save(path)
    return im.size


def unmap(t, segs):
    """Cut timeline -> source timeline."""
    acc = 0.0
    for a, b in segs:
        if t <= acc + (b - a):
            return a + (t - acc)
        acc += b - a
    return segs[-1][1]


def find_face(src, t_src):
    """Face centre and radius (in the 1080x1920 output frame) at source time t_src, or None. Needs opencv."""
    try:
        import cv2
        cv2.CascadeClassifier
    except (ImportError, AttributeError):   # pip install "opencv-python-headless<5"
        return None
    png = tempfile.mktemp(suffix=".png")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t_src:.2f}", "-i", src, "-frames:v", "1", "-vf",
         f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", png])
    img = cv2.imread(png, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = casc.detectMultiScale(img, 1.1, 6, minSize=(160, 160))
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    return int(x + w / 2), int(y + h / 2), int(max(w, h) * 0.75)


def caption_y(a, segs, ea, chh, tags, vis=None, eb=None):
    """Top y of a caption image: just BELOW his face if there is room, else just ABOVE it, never on the face.
    vis = (top, bottom) rows of the caption's opaque part (the rest of the image is glow padding).
    Face found with opencv at the cue's start and middle (he moves); the caption avoids both positions.
    B-roll cues (face hidden) and no-face frames use the default spot."""
    cards = a.layout == "cards"
    vt, vb = vis or (0, chh)
    default = int(H * (0.52 if cards else 0.60)) - chh // 2
    if any(kd in ("broll", "doc") for kd, _ in tags):   # b-roll text sits in the upper half: caption just above the face card
        return (CARD_Y + CARD_H - 520 - 30 - chh) if cards else int(H * 0.66) - chh // 2
    times = [ea + 0.1] + ([(ea + eb) / 2] if eb and eb - ea > 0.6 else [])
    faces = [f for f in (find_face(a.src, unmap(t, segs)) for t in times) if f]
    if not faces:
        return default
    if cards:   # content is shrunk into the card: map face coords to the final frame
        sc = CARD_W / W
        f_top = min(CARD_Y + (fy - fr) * sc for _, fy, fr in faces)
        f_bot = max(CARD_Y + (fy + fr) * sc for _, fy, fr in faces)
        top_lim, bot_lim = CARD_Y + 30, CARD_Y + CARD_H - 520 - 20   # stay above the small face card
    else:
        f_top = min(fy - fr for _, fy, fr in faces)
        f_bot = max(fy + fr for _, fy, fr in faces)
        top_lim = 110 + 245 if not a.no_badge else int(H * 0.12)      # below the top-left @kabli_ms badge (y 110..345)
        bot_lim = H - 440 if getattr(a, "wa_badge", False) else int(H * 0.80)   # above the WhatsApp badge
    gap = 25
    below = int(f_bot + gap - vt)          # visible top just under his chin
    if below + vb <= bot_lim:
        return below
    above = int(f_top - gap - vb)          # visible bottom just over his hair line
    if above + vt >= top_lim:
        return above
    # no clean spot: use the side with more room, so the caption covers as little of the face as possible
    return int(top_lim - vt) if f_top - top_lim >= bot_lim - f_bot else int(bot_lim - vb)


def render_circle_mov(path, r=230, n=14):
    """Hand-drawn style ring that draws itself in ~0.45 s (alpha .mov)."""
    from PIL import Image, ImageDraw
    d = os.path.join(os.path.dirname(path), "circ_frames"); os.makedirs(d, exist_ok=True)
    S = 2 * r + 40
    for i in range(n):
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
        end = -100 + 380 * min(1, (i + 1) / (n - 3))
        dr.arc([20, 20, S - 20, S - 20], start=-100, end=end, fill="#000000", width=20)
        dr.arc([20, 20, S - 20, S - 20], start=-100, end=end, fill="#FF2D2D", width=13)
        im.save(f"{d}/{i:03d}.png")
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{d}/%03d.png", "-c:v", "qtrle", "-pix_fmt", "argb", path])
    return S


def render_arrow_png(path):
    """Thick red arrow pointing up-left (its tip is the image's top-left corner)."""
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (260, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(8, 8), (120, 30), (88, 62), (240, 214), (214, 240), (62, 88), (30, 120)]
    d.polygon(pts, fill="#FF2D2D", outline="#000000", width=6)
    im.save(path)


def render_notif_png(text, path):
    """WhatsApp-like push notification banner."""
    from PIL import Image, ImageDraw, ImageFont
    w, h = 900, 170
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=40, fill=(245, 245, 247, 245))
    d.rounded_rectangle([28, 35, 128, 135], radius=24, fill=(37, 211, 102))
    d.ellipse([52, 59, 104, 111], outline=(255, 255, 255), width=7)
    fl = ImageFont.truetype(os.path.join(FONTS_DIR, LAT_SEMI), 30)
    d.text((150, 52), "WhatsApp", font=fl, fill=(60, 60, 67), anchor="lm")
    d.text((w - 30, 52), "now", font=fl, fill=(140, 140, 150), anchor="rm")
    fa = ImageFont.truetype(os.path.join(FONTS_DIR, AR_BOLD), 40)
    d.text((w - 30, 115), text, font=fa, fill=(20, 20, 25), anchor="rm", direction="rtl" if ARABIC_RE.search(text) else None)
    im.save(path)


CARD_W, CARD_H, CARD_Y = 800, 1422, 250


def render_wa_badge(path):
    """WhatsApp pill: official green logo (circle + phone) + number in Sora on a night-violet glass pill with a
    violet -> blue rim."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    f = ImageFont.truetype(os.path.join(FONTS_DIR, LAT_BOLD), 44)
    num = BRAND["whatsapp"]
    tw = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(num, font=f)
    S = 84; pad = 16; Wp, Hp = int(S + 34 + tw + 40), S + 2 * pad
    im = Image.new("RGBA", (Wp + 40, Hp + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 26, 20 + Wp, 26 + Hp], radius=Hp // 2, fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    body = Image.new("RGBA", im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([20, 20, 20 + Wp, 20 + Hp], radius=Hp // 2, fill=NIGHT + (225,))
    im.alpha_composite(body)
    ring = Image.new("L", im.size, 0); ImageDraw.Draw(ring).rounded_rectangle([20, 20, 20 + Wp, 20 + Hp], radius=Hp // 2, outline=255, width=3)
    grad = Image.new("RGBA", im.size); gd = ImageDraw.Draw(grad)
    for x in range(im.width):
        k = x / im.width; gd.line([(x, 0), (x, im.height)], fill=tuple(int(VIOLET[j] + (BLUE[j] - VIOLET[j]) * k) for j in range(3)) + (255,))
    im.paste(grad, (0, 0), ring)
    d = ImageDraw.Draw(im)
    cx, cy, r = 20 + pad + S // 2, 20 + Hp // 2, S // 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(37, 211, 102))          # WhatsApp green
    d.ellipse([cx - r * .62, cy - r * .62, cx + r * .62, cy + r * .62], outline="white", width=6)
    d.polygon([(cx - r * .55, cy + r * .35), (cx - r * .75, cy + r * .78), (cx - r * .25, cy + r * .6)], fill="white")
    # phone handset inside the bubble
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import neon_icons
    ph = neon_icons.glyph_mask("call", int(r * .7))
    im.paste((255, 255, 255, 255), (int(cx - ph.width / 2), int(cy - ph.height / 2)), ph)
    d.text((20 + pad + S + 22, cy + 2), num, font=f, fill="white", anchor="lm")
    im.save(path)


def render_card_assets(tmp):
    """Light grid paper with soft window-light shadows, card mask, card shadow, pip mask."""
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    bg = Image.new("RGB", (W, H), (240, 240, 236))
    d = ImageDraw.Draw(bg)
    for x in range(0, W, 72):
        d.line([(x, 0), (x, H)], fill=(222, 222, 218), width=2)
    for y in range(0, H, 72):
        d.line([(0, y), (W, y)], fill=(222, 222, 218), width=2)
    sh = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sh)
    for i in range(4):   # window frame bars falling diagonally
        x0 = -300 + i * 330
        sd.polygon([(x0, 0), (x0 + 60, 0), (x0 + 760, H), (x0 + 700, H)], fill=120)
    sd.polygon([(-200, 520), (W + 200, 260), (W + 200, 320), (-200, 580)], fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    bg = Image.composite(Image.new("RGB", (W, H), (150, 150, 146)), bg, sh.point(lambda v: int(v * 0.85)))
    d = ImageDraw.Draw(bg)
    fa = ImageFont.truetype(os.path.join(FONTS_DIR, LAT_BOLD), 400)
    d.text((40, H - 40), "#", font=fa, fill=NIGHT, anchor="ls")
    for i in range(42):    # barcode decoration
        if (i * 7) % 5 < 3:
            d.rectangle([W - 300 + i * 6, H - 150, W - 300 + i * 6 + (2 if i % 3 else 4), H - 70], fill=NIGHT)
    bgp = os.path.join(tmp, "cards_bg.png"); bg.save(bgp)

    def rounded(w, h, r, path):
        m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255); m.save(path)
    mask = os.path.join(tmp, "card_mask.png"); rounded(CARD_W, CARD_H, 46, mask)
    pipm = os.path.join(tmp, "pip_mask.png"); rounded(360, 480, 34, pipm)
    pb = Image.new("RGBA", (384, 504), (0, 0, 0, 0))
    ImageDraw.Draw(pb).rounded_rectangle([0, 0, 383, 503], radius=44, fill=(255, 255, 255, 255))
    pbs = Image.new("RGBA", (444, 564), (0, 0, 0, 0)); ImageDraw.Draw(pbs).rounded_rectangle([30, 40, 414, 544], radius=44, fill=(0, 0, 0, 110))
    pbs = pbs.filter(ImageFilter.GaussianBlur(16)); pbs.alpha_composite(pb, (30, 30))
    pbs.save(os.path.join(tmp, "pip_border.png"))
    shp = Image.new("RGBA", (CARD_W + 160, CARD_H + 160), (0, 0, 0, 0))
    ImageDraw.Draw(shp).rounded_rectangle([80, 95, CARD_W + 80, CARD_H + 95], radius=46, fill=(0, 0, 0, 120))
    shp = shp.filter(ImageFilter.GaussianBlur(30)); shadow = os.path.join(tmp, "card_shadow.png"); shp.save(shadow)
    return bgp, mask, pipm, shadow


ICON_COLORS_OLD = {"🔥": ((255, 140, 40), (230, 60, 20)), "🚨": ((255, 90, 90), (200, 20, 40)),
               "💸": ((90, 220, 140), (20, 150, 80)), "💰": ((255, 210, 80), (220, 150, 20)),
               "✅": ((90, 220, 140), (20, 150, 80)), "❌": ((250, 250, 252), (185, 190, 205)),
               "🤝": ((255, 210, 80), (220, 150, 20)), "👇": ((120, 170, 255), (40, 90, 220))}


GLASS_TINT = {"🔥": (255, 120, 40), "🚨": (255, 70, 80), "❌": (255, 70, 80), "💸": (60, 210, 130),
              "💰": (255, 200, 60), "✅": (60, 210, 130), "🤝": (255, 200, 60), "👇": (90, 150, 255)}


def _persp_coeffs(dst, src):
    import numpy as np
    A, B = [], []
    for (x, y), (X, Y) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -X * x, -X * y], [0, 0, 0, x, y, 1, -Y * x, -Y * y]]
        B += [X, Y]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def _glyph_layer(ch, size, tint):
    """The symbol, extruded in 3D (stacked darker copies) with a white->tint face gradient."""
    from PIL import Image, ImageDraw, ImageFont
    S = size
    mask = Image.new("L", (S, S), 0); d = ImageDraw.Draw(mask)
    c = S / 2
    if ch == "✅":
        d.line([(c - S * .26, c + S * .02), (c - S * .07, c + S * .22), (c + S * .28, c - S * .22)], fill=255, width=int(S * .13), joint="curve")
    elif ch == "❌":
        w = int(S * .13)
        d.line([(c - S * .23, c - S * .23), (c + S * .23, c + S * .23)], fill=255, width=w)
        d.line([(c + S * .23, c - S * .23), (c - S * .23, c + S * .23)], fill=255, width=w)
    elif ch in ("💸", "💰"):
        f = ImageFont.truetype(os.path.join(FONTS_DIR, LAT_BOLD), int(S * .72))
        d.text((c, c + S * .02), "$", font=f, fill=255, anchor="mm")
    elif ch == "🚨":
        f = ImageFont.truetype(os.path.join(FONTS_DIR, LAT_BOLD), int(S * .72))
        d.text((c, c + S * .02), "!", font=f, fill=255, anchor="mm")
    else:
        return None
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dark = tuple(int(v * 0.45) for v in tint)
    for i in range(int(S * .06), 0, -1):     # extrusion depth
        out.paste(Image.new("RGBA", (S, S), dark + (255,)), (i, i), mask)
    grad = Image.new("RGBA", (S, S))
    gd = ImageDraw.Draw(grad)
    for y in range(S):
        k = y / S
        gd.line([(0, y), (S, y)], fill=tuple(int(255 * (1 - k) + tint[j] * k) for j in range(3)) + (255,))
    out.paste(grad, (0, 0), mask)
    return out


def render_icon_glass_mov(ch, path, secs=2.0, size=210):
    """NEW icon type: transparent 3D GLASS tile (frosted, see-through) with a glowing edge, a 3D extruded symbol
    floating inside (parallax), rotating in 3D around Y, with a light streak sweeping across the glass.
    Pops in with overshoot then floats. Alpha .mov (qtrle)."""
    from PIL import Image, ImageDraw, ImageFilter
    import math
    tint = GLASS_TINT.get(ch, VIOLET)
    T = size * 2                                   # draw at 2x
    rad = int(T * .26)
    tile = Image.new("RGBA", (T, T), (0, 0, 0, 0)); td = ImageDraw.Draw(tile)
    td.rounded_rectangle([0, 0, T - 1, T - 1], radius=rad, fill=tint + (70,))                  # tinted glass
    glow = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for y in range(T // 2):
        gd.line([(0, y), (T, y)], fill=(255, 255, 255, int(80 * (1 - y / (T / 2)))))          # top sheen
    m = Image.new("L", (T, T), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, T - 1, T - 1], radius=rad, fill=255)
    tile.paste(glow, (0, 0), Image.composite(glow.split()[3], Image.new("L", (T, T), 0), m))
    td.rounded_rectangle([3, 3, T - 4, T - 4], radius=rad, outline=(255, 255, 255, 210), width=7)  # bright rim
    td.rounded_rectangle([18, 18, T - 19, T - 19], radius=rad - 14, outline=tint + (150,), width=4)
    glyph = _glyph_layer(ch, T, tint)
    if glyph is None:   # complex emoji: use it as the symbol
        em = Image.open(path.replace(".mov", "_flat.png")).convert("RGBA")
        em = em.resize((int(T * .62), int(T * .62 * em.height / em.width)), Image.LANCZOS)
        glyph = Image.new("RGBA", (T, T), (0, 0, 0, 0)); glyph.alpha_composite(em, ((T - em.width) // 2, (T - em.height) // 2))
    gsh = Image.new("RGBA", (T, T), (0, 0, 0, 0)); gsh.paste((0, 0, 0, 120), (10, 22), glyph)
    glyph_full = gsh.filter(ImageFilter.GaussianBlur(10)); glyph_full.alpha_composite(glyph)
    tile_s = tile.resize((size, size), Image.LANCZOS)
    glyph_s = glyph_full.resize((int(size * .78), int(size * .78)), Image.LANCZOS)
    mask_s = m.resize((size, size), Image.LANCZOS)
    OW, OH = int(size * 1.5), int(size * 1.6)
    d = os.path.join(os.path.dirname(path), os.path.basename(path) + "_f"); os.makedirs(d, exist_ok=True)
    n = int(secs * 30)
    for f in range(n):
        t = f / 30
        u = min(t / 0.38, 1)
        pop = max(0.02, 1 + 2.70158 * (u - 1) ** 3 + 1.70158 * (u - 1) ** 2)
        ang = (1 - u) * 1.2 + 0.42 * math.sin(t * 2.4) * u          # spins in, then sways in 3D
        bob = 9 * math.sin(t * 3.6)
        fr = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
        # shadow on the "floor"
        sh = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
        sw = size * .42 * pop * (0.8 + 0.2 * abs(math.cos(ang)))
        ImageDraw.Draw(sh).ellipse([OW / 2 - sw, OH - 46, OW / 2 + sw, OH - 22], fill=(0, 0, 0, int(80 * min(1, pop))))
        fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
        # shine streak inside the glass
        tl = tile_s.copy()
        if 0.35 < t < 1.1:
            st = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            sx = (t - 0.35) / 0.75 * size * 1.8 - size * .4
            ImageDraw.Draw(st).polygon([(sx, 0), (sx + size * .18, 0), (sx - size * .22, size), (sx - size * .4, size)], fill=(255, 255, 255, 120))
            st.putalpha(Image.composite(st.split()[3], Image.new("L", (size, size), 0), mask_s))
            tl.alpha_composite(st.filter(ImageFilter.GaussianBlur(3)))
        def place(img, depth):
            w, h = img.size
            hw, hh = w * pop / 2, h * pop / 2
            ca, sa = math.cos(ang), math.sin(ang)
            pts = []
            for (x, y) in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
                X, Z = x * ca, x * sa + depth
                p = 900 / (900 + Z)
                pts.append((OW / 2 + X * p + depth * sa * 0.6, OH / 2 - 24 + y * p + bob))
            co = _persp_coeffs(pts, [(0, 0), (w, 0), (w, h), (0, h)])
            fr.alpha_composite(img.transform((OW, OH), Image.PERSPECTIVE, co, Image.BICUBIC))
        place(tl, 0)
        place(glyph_s, -40)          # symbol floats in front of the glass (parallax)
        fr.save(f"{d}/{f:03d}.png")
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{d}/%03d.png", "-c:v", "qtrle", "-pix_fmt", "argb", path])
    return OW, OH


def _neon_glyph_mask(ch, S):
    """Clean flat white pictograms (modern app-icon style). Returns an L mask or None."""
    from PIL import Image, ImageDraw, ImageFont
    m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
    c = S / 2; u = S / 2
    P = lambda pts: [(c + x * u, c + y * u) for x, y in pts]
    w = int(S * .11)
    if ch == "✅":
        d.line(P([(-.45, .02), (-.12, .36), (.48, -.36)]), fill=255, width=w, joint="curve")
        for x, y in ((-.45, .02), (.48, -.36)): d.ellipse([c + x * u - w / 2, c + y * u - w / 2, c + x * u + w / 2, c + y * u + w / 2], fill=255)
    elif ch == "❌":
        for a_, b_ in (((-.38, -.38), (.38, .38)), ((.38, -.38), (-.38, .38))):
            d.line(P([a_, b_]), fill=255, width=w)
            for x, y in (a_, b_): d.ellipse([c + x * u - w / 2, c + y * u - w / 2, c + x * u + w / 2, c + y * u + w / 2], fill=255)
    elif ch in ("💸", "💰"):
        f = ImageFont.truetype(os.path.join(FONTS_DIR, LAT_BOLD), int(S * .74))
        d.text((c, c + S * .03), "$", font=f, fill=255, anchor="mm")
    elif ch == "🚨":   # rounded warning triangle with "!"
        d.polygon(P([(0, -.62), (.66, .5), (-.66, .5)]), fill=255)
        m2 = Image.new("L", (S, S), 0); d2 = ImageDraw.Draw(m2)
        d2.rounded_rectangle([c - S * .045, c - S * .17, c + S * .045, c + S * .1], radius=int(S * .04), fill=255)
        d2.ellipse([c - S * .05, c + S * .15, c + S * .05, c + S * .25], fill=255)
        m.paste(0, (0, 0), m2)
    elif ch == "🔥":
        pts = [(0, .9), (-.5, .72), (-.66, .32), (-.52, -.08), (-.3, -.3), (-.26, -.58), (-.02, -.92), (.08, -.6),
               (.3, -.42), (.56, -.1), (.66, .3), (.5, .72)]
        d.polygon(P(pts), fill=255)
        inner = [(0, .78), (-.26, .62), (-.32, .34), (-.16, .08), (-.04, -.18), (.08, .06), (.28, .3), (.24, .62)]
        d.polygon(P(inner), fill=0)
        from PIL import ImageFilter
        m = m.filter(ImageFilter.GaussianBlur(S * .035)).point(lambda v: 255 if v > 110 else 0)   # soften the corners
    elif ch == "👇":
        d.rounded_rectangle([c - S * .09, c - S * .45, c + S * .09, c + S * .12], radius=int(S * .06), fill=255)
        d.polygon(P([(-.38, .02), (.38, .02), (0, .5)]), fill=255)
    elif ch == "💬":
        d.rounded_rectangle([c - S * .44, c - S * .38, c + S * .44, c + S * .2], radius=int(S * .16), fill=255)
        d.polygon(P([(-.3, .3), (-.42, .74), (.04, .32)]), fill=255)
        for x in (-.22, 0, .22):   # three typing dots
            d.ellipse([c + x * u - S * .055, c - .18 * u - S * .055, c + x * u + S * .055, c - .18 * u + S * .055], fill=0)
    elif ch == "🛒":
        d.line(P([(-.55, -.4), (-.38, -.4), (-.22, .22), (.4, .22), (.52, -.22), (-.3, -.22)]), fill=255, width=int(S * .08), joint="curve")
        for x in (-.14, .32): d.ellipse([c + x * u - S * .065, c + .36 * u, c + x * u + S * .065, c + .36 * u + S * .13], fill=255)
    elif ch == "📦":
        d.polygon(P([(-.48, -.22), (0, -.48), (.48, -.22), (.48, .32), (0, .58), (-.48, .32)]), fill=255)
        d.line(P([(-.48, -.22), (0, .04), (.48, -.22)]), fill=0, width=int(S * .035))
        d.line(P([(0, .04), (0, .58)]), fill=0, width=int(S * .035))
    else:
        return None
    return m


def render_icon3d_mov(ch, path, secs=2.0, size=210):
    """Neon glass app-icon from Mustafa's references (palette C, drawn by tools/neon_icons.py): dark violet glass
    squircle, neon-blue -> violet rim with glow, soft lavender 3D pictogram (Material Icons), light beam, sparkle.
    Pops in, sways in 3D, floats; glow pulses. An emoji without a matching pictogram goes inside the tile as is.
    Alpha .mov."""
    from PIL import Image
    import math
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import neon_icons
    name = neon_icons.EMOJI_ICON.get(ch) or neon_icons.EMOJI_ICON.get(ch.replace("\ufe0f", ""))
    emoji = None if name else Image.open(path.replace(".mov", "_flat.png")).convert("RGBA")
    statics = {}
    for p in (0.8, 1.0, 1.2):   # drawn at 2x, glow strength pulses between these
        cv = neon_icons.tile(name, size * 2, p, emoji_img=emoji)
        statics[p] = cv.resize((cv.width // 2, cv.height // 2), Image.LANCZOS)
    OW = OH = statics[1.0].width + 40
    d = os.path.join(os.path.dirname(path), os.path.basename(path) + "_f"); os.makedirs(d, exist_ok=True)
    for f in range(int(secs * 30)):
        t = f / 30
        u = min(t / 0.38, 1)
        pop = max(0.02, 1 + 2.70158 * (u - 1) ** 3 + 1.70158 * (u - 1) ** 2)
        ang = (1 - u) * 0.9 + 0.28 * math.sin(t * 2.4) * u
        bob = 7 * math.sin(t * 3.4)
        img = statics[min(statics, key=lambda p: abs(p - (1 + 0.2 * math.sin(t * 5))))]
        w, h = img.size; hw, hh = w * pop / 2, h * pop / 2
        ca, sa = math.cos(ang), math.sin(ang)
        pts = []
        for (x, y) in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)):
            X, Z = x * ca, x * sa
            pz = 700 / (700 + Z)
            pts.append((OW / 2 + X * pz, OH / 2 + y * pz + bob))
        co = _persp_coeffs(pts, [(0, 0), (w, 0), (w, h), (0, h)])
        fr = img.transform((OW, OH), Image.PERSPECTIVE, co, Image.BICUBIC)
        fr.save(f"{d}/{f:03d}.png")
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", f"{d}/%03d.png", "-c:v", "qtrle", "-pix_fmt", "argb", path])
    return OW, OH


def render_emoji(ch, path, size=230):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    im = im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)
    im.save(path)


BEATS = []
HOOK = False


def zoom_expr(events, segs, total, k=0.45):
    """Alternating punch zoom-OUT (1.14 -> 1.0) and slow push-IN (1.0 -> 1.10), restarted at each caption / cut."""
    pts = sorted({round(a, 2) for a, *_ in events if a < total}
                 | {round(sum(b - x for x, b in segs[:i]), 2) for i in range(1, len(segs))})
    if not pts:
        pts = [round(i * 3.0, 2) for i in range(int(total // 3) + 1)]
    if BEATS:  # snap each punch to the nearest music beat when it is close (beat sync)
        pts = sorted({min(BEATS, key=lambda b: abs(b - p)) if min(abs(b - p) for b in BEATS) < 0.15 else p for p in pts})
    if pts[0] > 0.05:
        pts.insert(0, 0.0)
    terms = []
    for i, t0 in enumerate(pts):
        t1 = pts[i + 1] if i + 1 < len(pts) else total
        if i % 2 == 0:   # punch out (the very first one is strong: hook)
            kk = max(k, 1.3) if i == 0 and HOOK else k
            terms.append(f"between(t\\,{t0}\\,{t1})*(1+{0.14*kk:.3f}*max(0\\,1-(t-{t0})/0.6))")
        else:            # push in
            terms.append(f"between(t\\,{t0}\\,{t1})*(1+{0.10*k:.3f}*min(1\\,(t-{t0})/{max(t1 - t0, 0.3):.2f}))")
    return "(" + "+".join(terms) + ")"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--srt")
    ap.add_argument("--srt-after-cut", action="store_true")
    ap.add_argument("--no-silence-cut", action="store_true")
    ap.add_argument("--no-endcard", action="store_true")
    ap.add_argument("--no-zoom", action="store_true")
    ap.add_argument("--no-sfx", action="store_true")
    ap.add_argument("--sfx-style", choices=["basic", "pro"], default="basic", help="pro = designed sounds (tools/sfx_pro.py): pop on captions, sparkle on icons, one swoosh on the first b-roll, soft hit on the hook, chime on the end card")
    ap.add_argument("--text-sfx-only", action="store_true", help="only the caption sounds (pop when a key word / icon appears): no whoosh, ding or boom (Mustafa 2026-10-07)")
    ap.add_argument("--wa-badge", action="store_true", help="WhatsApp logo + number pill bottom-left for the whole reel (Mustafa 2026-10-07)")
    ap.add_argument("--no-badge", action="store_true", help="hide the top-left @kabli_ms badge with the spinning 3D K+M coin")
    ap.add_argument("--layout", choices=["full", "cards"], default="cards", help="cards = After-Effects style: video in a rounded card on a light grid background with window shadows + a small face card")
    ap.add_argument("--keywords-only", action="store_true", help="show only the *starred* key words, big, instead of full sentences")
    ap.add_argument("--accent", default="", help="hex colour for key words, e.g. 38BDF8 (neon blue); default = brand violet")
    ap.add_argument("--text-color", default="FFFFFF", help="hex colour for the other words")
    ap.add_argument("--hook-style", choices=["card", "title"], default="card", help="card = night plate with neon rim; title = big white bold title, no plate (reference-reel look)")
    ap.add_argument("--dump-timeline", default="", help="write the silence-cut segments as JSON (used by tools/ref_style.py to place overlays)")
    ap.add_argument("--hook", default="", help="big hook text shown 0-2.6s (top safe zone) with flash + impact sound; *word* = accent")
    ap.add_argument("--music", default="", help="'beat' = generated royalty-free beat, or a path to your own audio file")
    ap.add_argument("--bpm", type=float, default=100)
    ap.add_argument("--zoom-mode", choices=["intro", "all"], default="intro", help="intro = ONE zoom-out at the start only (Mustafa's choice); all = a zoom on every caption")
    ap.add_argument("--zoom", type=float, default=0.45, help="zoom strength: 1 = strong punch, 0.45 = soft (default), 0 = none")
    ap.add_argument("--ar-font", default=AR_BOLD, help="(unused: captions use the brand fonts AR_BOLD / LAT_BOLD)")
    ap.add_argument("--no-bar", action="store_true")
    ap.add_argument("--tagline", default="")
    ap.add_argument("--no-emoji", action="store_true")
    ap.add_argument("--grade", choices=["warm", "natural", "cinema", "bright", "pro", "none"], default="pro")
    ap.add_argument("--out")
    a = ap.parse_args()

    out = a.out or re.sub(r"\.[^.]+$", "", a.src) + "_v1.mp4"
    refresh_generated_cache()
    endcard = None if a.no_endcard else render_endcard(a.tagline)
    segs, dur = ([(0, probe_duration(a.src))], None) if a.no_silence_cut else keep_segments(a.src)
    total = sum(b - x for x, b in segs)
    if a.dump_timeline:
        import json
        json.dump({"segs": segs, "total": total}, open(a.dump_timeline, "w"))

    events = []
    if a.srt:
        raw = srt_to_events(open(a.srt, encoding="utf-8").read())
        events = raw if a.srt_after_cut or a.no_silence_cut else [
            (remap(s, segs), remap(e, segs), t, em, tg) for s, e, t, em, tg in raw]
    if a.hook:   # nothing is written over the hook card: captions/icons start once it is gone (2.65 s)
        events = [(max(ea, 2.7), eb, t, em, tg) for ea, eb, t, em, tg in events if eb > 3.0]
    global ACCENT, TEXT_COLOR
    if a.accent:
        ACCENT = a.accent.lstrip("#").upper()
    TEXT_COLOR = a.text_color.lstrip("#").upper()
    if a.keywords_only:   # keep only the *key words* of each cue (cue with none -> no caption)
        events = [(ea, eb, " ".join(f"*{m}*" for m in re.findall(r"\*([^*]+)\*", t)), em, tg) for ea, eb, t, em, tg in events]
    tmp = tempfile.mkdtemp()
    ass = os.path.join(tmp, "s.ass")
    ass_events = [(ea, eb, "", em, tg) for ea, eb, t, em, tg in events] if a.keywords_only else events  # keywords: all drawn as images
    open(ass, "w", encoding="utf-8").write(build_ass(ass_events, total, not a.no_endcard and not endcard, a.tagline))

    n = len(segs)
    parts = []
    for i, (x, y) in enumerate(segs):
        parts.append(f"[0:v]trim={x:.3f}:{y:.3f},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={x:.3f}:{y:.3f},asetpts=PTS-STARTPTS[a{i}]")
    cat = "".join(f"[v{i}][a{i}]" for i in range(n))
    fc = ";".join(parts) + f";{cat}concat=n={n}:v=1:a=1[vc][ac];"
    global BEATS, HOOK
    HOOK = bool(a.hook)
    if a.music:
        BEATS = [i * 60 / a.bpm for i in range(int(total * a.bpm / 60) + 2)]
    if a.zoom_mode == "intro" and not a.no_zoom:
        zexpr = "(1+0.16*max(0\\,1-t/0.8))"   # single zoom-out over the first 0.8 s, then static
        zoom = f"scale=w='trunc({W}*{zexpr}/2)*2':h='trunc({H}*{zexpr}/2)*2':eval=frame,crop={W}:{H},"
    else:
      zoom = ("" if a.no_zoom else
            f"scale=w='trunc({W}*{zoom_expr(events, segs, total, a.zoom)}/2)*2':h='trunc({H}*{zoom_expr(events, segs, total, a.zoom)}/2)*2':eval=frame,crop={W}:{H},")
    shakes = [ea for (ea, eb, _t, _em, tg) in events for kd, _ in tg if kd == "shake"] + ([0.0] if a.hook else [])
    if shakes:
        sx = "+".join(f"between(t,{t0:.2f},{t0 + 0.25:.2f})*12*sin(75*(t-{t0:.2f}))*(1-(t-{t0:.2f})/0.25)" for t0 in shakes)
        sy = "+".join(f"between(t,{t0:.2f},{t0 + 0.25:.2f})*8*cos(63*(t-{t0:.2f}))*(1-(t-{t0:.2f})/0.25)" for t0 in shakes)
        zoom += f"scale={int(W * 1.03) // 2 * 2}:{int(H * 1.03) // 2 * 2},crop={W}:{H}:x='(iw-{W})/2+{sx}':y='(ih-{H})/2+{sy}',"
    fc += (f"[vc]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{zoom}"
           f"{GRADES[a.grade]},unsharp=5:5:0.4,fps=30"
           + ("" if a.no_bar else f",drawbox=x=0:y=0:w='iw*t/{total:.2f}':h=12:color=0x{BRAND['neon']}@1:t=fill")
           + "[vm0];"
           f"[ac]loudnorm=I=-14:TP=-1.5,aresample=48000[am0];")

    extra_inputs, cur, k, n_in = [], "vm0", 0, 1
    if a.layout == "cards":
        fc += "[vm0]split[vm0a][pipraw];"
        cur = "vm0a"

    # effect tags from the .srt: sparks / flash / leak / money / broll:NAME / icon:NAME
    for (ea, eb, _t, _em, tags) in events:
        for kind, arg in tags:
            if kind in ("shake", "ding"):
                continue   # handled by the camera / sound passes
            if kind == "circle":
                r0 = 230
                if arg:
                    cx, cy = (int(v) for v in arg.split(","))
                else:   # follow the face: detect it at the moment the circle appears
                    face = find_face(a.src, unmap(ea + 0.15, segs))
                    cx, cy, r0 = face if face else (W // 2 - 20, int(H * 0.43), 230)
                mov = os.path.join(tmp, f"circle{k}.mov"); S0 = render_circle_mov(mov, r=r0)
                extra_inputs += ["-i", mov]
                fc += (f"[{n_in}:v]format=rgba,setpts=PTS-STARTPTS+{ea:.2f}/TB[fx{k}];"
                       f"[{cur}][fx{k}]overlay=x={cx - S0 // 2}:y={cy - S0 // 2}:eof_action=repeat:enable='between(t,{ea:.2f},{eb:.2f})'[ov{k}];")
            elif kind == "arrow":
                cx, cy = (int(v) for v in arg.split(",")) if arg else (W // 2 + 120, int(H * 0.40))
                png = os.path.join(tmp, f"arrow{k}.png"); render_arrow_png(png)
                extra_inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", png]
                bob = f"18*abs(sin(8*(t-{ea:.2f})))"
                fc += (f"[{n_in}:v]format=rgba[fx{k}];"
                       f"[{cur}][fx{k}]overlay=x='{cx}+{bob}':y='{cy}+{bob}':enable='between(t,{ea:.2f},{eb:.2f})'[ov{k}];")
            elif kind == "notif":
                png = os.path.join(tmp, f"notif{k}.png"); render_notif_png(arg or "رسالة جديدة", png)
                extra_inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", png]
                y = f"{int(H * 0.06)}-260*(1-min(1,(t-{ea:.2f})/0.22))"
                fc += (f"[{n_in}:v]format=rgba[fx{k}];"
                       f"[{cur}][fx{k}]overlay=x=(W-w)/2:y='{y}':enable='between(t,{ea:.2f},{eb:.2f})'[ov{k}];")
            elif kind in ("sparks", "flash", "leak", "money", "broll", "doc"):
                if kind == "broll" and arg in TITLED and _t:
                    import hashlib
                    title = re.sub(r"\*", "", _t).strip()
                    path = os.path.join(ASSETS, "_generated", f"{arg}_" + hashlib.md5(title.encode()).hexdigest()[:8] + ".mp4")
                    if not os.path.exists(path):
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        props = {"title": title} if arg == "rm_funnel" else {"title": title, "sub": ""}
                        remotion_render(REMOTION_COMPS[arg], path, props)
                elif kind == "doc":   # documentary paper card with highlighter, rendered by Remotion
                    import hashlib
                    path = os.path.join(ASSETS, "_generated", "doc_" + hashlib.md5(arg.encode()).hexdigest()[:8] + ".mp4")
                    if not os.path.exists(path):
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        remotion_render("DocCard", path, {"text": arg, "kicker": "E-COMMERCE • DZ"})
                    kind = "broll"
                elif not (kind == "broll" and arg in TITLED and _t):
                    path = find_asset("broll" if kind == "broll" else kind, arg if kind == "broll" else kind)
                extra_inputs += ["-i", path]
                cut = f",trim=duration={max(eb - ea, 0.4):.2f}" if kind == "broll" else ""
                # b-roll enters with a fast whip (slides in from the right in 0.12 s)
                xpos = f"x='W*max(0,1-(t-{ea:.2f})/0.12)':" if kind == "broll" else ""
                fc += (f"[{n_in}:v]format=rgba,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}{cut},"
                       f"setpts=PTS-STARTPTS+{ea:.2f}/TB[fx{k}];"
                       f"[{cur}][fx{k}]overlay={xpos}eof_action=pass:repeatlast=0[ov{k}];")
            else:  # icon: PNG, placed like an emoji
                path = find_asset("icon", arg)
                extra_inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", path]
                fc += (f"[{n_in}:v]format=rgba,scale=230:-1,fade=t=in:st={ea:.2f}:d=0.12:alpha=1[fx{k}];"
                       f"[{cur}][fx{k}]overlay=x='(W-w)/2':y='{int(H * 0.11)}':enable='between(t,{ea:.2f},{eb:.2f})'[ov{k}];")
            cur, k, n_in = f"ov{k}", k + 1, n_in + 1

    # CARDS layout: shrink the finished content into a rounded card on the grid background, + a small face card
    if a.layout == "cards":
        bgp, maskp, pipm, shadowp = render_card_assets(tmp)
        cx0 = (W - CARD_W) // 2
        ent = f"(1-min(1,t/0.5))*(1-min(1,t/0.5))*(1-min(1,t/0.5))"     # ease-out entry
        extra_inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", bgp, "-loop", "1", "-t", f"{total:.2f}", "-i", maskp,
                         "-loop", "1", "-t", f"{total:.2f}", "-i", shadowp, "-loop", "1", "-t", f"{total:.2f}", "-i", pipm,
                         "-loop", "1", "-t", f"{total:.2f}", "-i", os.path.join(tmp, "pip_border.png")]
        ib, im_, ish, ip, ipb = n_in, n_in + 1, n_in + 2, n_in + 3, n_in + 4
        n_in += 5
        face = find_face(a.src, unmap(1.2, segs)) or (W // 2, int(H * 0.40), 260)
        fx, fy, fr = face
        cw_, ch_ = 600, 800
        x0c = min(max(fx - cw_ // 2, 0), W - cw_); y0c = min(max(fy - int(ch_ * 0.42), 0), H - ch_)
        fc += (f"[{cur}]null[cardsrc];[pipraw]null[pipsrc];"
               f"[cardsrc]scale={CARD_W}:{CARD_H},format=rgba[cs];[{im_}:v]format=gray,scale={CARD_W}:{CARD_H}[cm];[cs][cm]alphamerge[card];"
               f"[pipsrc]crop={cw_}:{ch_}:{x0c}:{y0c},scale=360:480,format=rgba[ps];[{ip}:v]format=gray[pm];[ps][pm]alphamerge[pipc];"
               f"[{ib}:v]format=rgba[bgc];"
               f"[bgc][{ish}:v]overlay=x={cx0 - 80}:y='{CARD_Y - 80}+{H}*{ent}'[bgs];"
               f"[bgs][card]overlay=x={cx0}:y='{CARD_Y}+{H}*{ent}'[withcard];"
               f"[withcard][{ipb}:v]overlay=x='40-30-500*(1-min(1,(t-1.0)/0.35))':y={CARD_Y + CARD_H - 520 - 42}:enable='gte(t,1.0)'[wpb];"
               f"[wpb][pipc]overlay=x='40-500*(1-min(1,(t-1.0)/0.35))':y={CARD_Y + CARD_H - 520}:enable='gte(t,1.0)'[cardsout];")
        cur = "cardsout"

    # caption images + positions (above/below the face) computed once, used by emoji and captions
    caps = {}
    for i_ev, (ea, eb, t, _em, _tg) in enumerate(events):
        if t and (ARABIC_RE.search(t) or a.keywords_only):
            on_broll = any(kd in ("broll", "doc") for kd, _ in _tg)
            if any(kd == "doc" and re.sub(r"\*", "", t).strip() == (ar_ or "").strip() for kd, ar_ in _tg) \
                    or any(kd == "broll" and ar_ in TITLED for kd, ar_ in _tg):
                continue   # the graphic already shows these exact words as its title
            png = os.path.join(tmp, f"capimg{i_ev}.png")
            sz = (105 if on_broll else 150) if a.keywords_only else 106
            cw, chh = render_caption_png(t, png, a.ar_font, size=sz)
            if _em and not a.no_emoji and (W - cw) // 2 - 60 + cw - 40 + 230 > W + 30:   # icon would sit on the text
                cw, chh = render_caption_png(t, png, a.ar_font, size=sz, maxw=640)
            from PIL import Image
            vis = Image.open(png).split()[3].point(lambda v: 255 if v > 40 else 0).getbbox() or (0, 0, cw, chh)
            caps[i_ev] = (png, cw, chh, caption_y(a, segs, ea, chh, _tg, vis=(vis[1], vis[3]), eb=eb))

    # colour emoji: rendered to PNG and overlaid near the top (clear of the face and the caption) with a small slide-down
    if not a.no_emoji:
        cache = {}
        for i_ev, (ea, eb, _t, ems, _tg) in enumerate(events):
            if any(kd == "doc" or (kd == "broll" and ar_ in TITLED) for kd, ar_ in _tg):
                continue   # full-frame graphic with its own title: no icon on top of it
            for j, ch in enumerate(ems[:2]):
                if ch not in cache:
                    mov = os.path.join(tmp, f"e{len(cache)}.mov")
                    render_emoji(ch, mov.replace(".mov", "_flat.png"), size=230)
                    cache[ch] = (mov, render_icon3d_mov(ch, mov))
                mov, (iw_, ih_) = cache[ch]
                extra_inputs += ["-i", mov]
                n_em = len(ems[:2])
                if i_ev in caps:   # right next to the caption (its image is centred at W/2-60), never on the face
                    _p, cw, chh, yc = caps[i_ev]
                    right = (W - cw) // 2 - 60 + cw - 40
                    x = f"{min(right + j * (iw_ - 40), W - iw_ + 30)}"
                    y = f"{yc + chh // 2 - ih_ // 2}"
                else:
                    x = f"(W-w)/2+({j}-{(n_em - 1) / 2})*{iw_}"
                    y = f"{int(H * 0.11)}"
                fc += (f"[{n_in}:v]format=rgba,setpts=PTS-STARTPTS+{ea:.2f}/TB[em{k}];"
                       f"[{cur}][em{k}]overlay=x='{x}':y='{y}':eof_action=repeat:enable='between(t,{ea:.2f},{eb:.2f})'[ov{k}];")
                cur, k, n_in = f"ov{k}", k + 1, n_in + 1
    # HOOK: big text card in the top safe zone for the first 2.6 s, flash at 0
    if a.hook:
        hp = os.path.join(tmp, "hook.png")
        hw, hh = (render_hook_title_png(a.hook, hp) if a.hook_style == "title" else render_hook_png(a.hook, hp, a.ar_font))
        extra_inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", hp]
        y = f"{int(H * 0.075)}-60*(1-min(1,t/0.2))"
        fc += (f"[{n_in}:v]format=rgba,fade=t=out:st=2.4:d=0.25:alpha=1[hk];"
               f"[{cur}][hk]overlay=x=(W-w)/2-30:y='{y}':enable='between(t,0,2.65)'[ovhk];")
        cur, n_in = "ovhk", n_in + 1
        extra_inputs += ["-i", find_asset("flash", "flash")]
        fc += (f"[{n_in}:v]format=rgba,scale={W}:{H}[hfl];[{cur}][hfl]overlay=eof_action=pass:repeatlast=0[ovhf];")
        cur, n_in = "ovhf", n_in + 1

    # WHATSAPP BADGE (bottom-left): official green WhatsApp logo + number in a brand pill, whole reel
    if a.wa_badge:
        wp = os.path.join(tmp, "wa_badge.png"); render_wa_badge(wp)
        extra_inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", wp]
        t0 = 2.7 if a.hook else 0.3
        fc += (f"[{n_in}:v]format=rgba,fade=t=in:st={t0}:d=0.4:alpha=1[wab];"
               f"[{cur}][wab]overlay=x=36:y={H - 420}:enable='gte(t,{t0})'[ovwa];")
        cur, n_in = "ovwa", n_in + 1

    # BRAND BADGE (top-left): spinning 3D K+M coin + @kabli_ms pill, rendered by Remotion (ProRes 4444 alpha), looped
    if not a.no_badge:
        badge = os.path.join(ASSETS, "_generated", "rm_badge.mov")
        if not os.path.exists(badge):
            os.makedirs(os.path.dirname(badge), exist_ok=True)
            run(["npx", "remotion", "render", "src/index.ts", "BrandBadge", badge, "--codec=prores", "--prores-profile=4444",
                 "--pixel-format=yuva444p10le", "--image-format=png", "--log=error"] +
                [f"--browser-executable={c}" for c in __import__("glob").glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell")[:1]],
                cwd=REMOTION)
        t0 = 2.7 if a.hook else 0.3
        extra_inputs += ["-stream_loop", "-1", "-i", badge]
        by = 50 if a.layout == "cards" else 110
        fc += (f"[{n_in}:v]format=yuva444p,scale=740:-1,setpts=PTS-STARTPTS+{t0}/TB,fade=t=in:st={t0}:d=0.35:alpha=1[bdg];"
               f"[{cur}][bdg]overlay=x=20:y={by}:enable='between(t,{t0},{total:.2f})':shortest=0:eof_action=pass[ovbd];")
        cur, n_in = "ovbd", n_in + 1

    # Arabic captions as images, on top of everything, slide-up + fade-in
    for i_ev, (ea, eb, t, _em, _tg) in enumerate(events):
        if i_ev in caps:
            png, cw, chh, yc = caps[i_ev]   # above or below his face, wherever there is room
            extra_inputs += ["-loop", "1", "-t", f"{total:.2f}", "-i", png]
            y = f"{yc}+28*(1-min(1,(t-{ea:.2f})/0.15))"
            fc += (f"[{n_in}:v]format=rgba,fade=t=in:st={ea:.2f}:d=0.1:alpha=1[cp{k}];"
                   f"[{cur}][cp{k}]overlay=x='max(10,min(W-w-10,(W-w)/2-60))':y='{y}':enable='between(t,{ea:.2f},{eb:.2f})'[ov{k}];")
            cur, k, n_in = f"ov{k}", k + 1, n_in + 1
    fc += f"[{cur}]null[vm];"

    # sound effects: whoosh on every caption change, pop when an emoji / effect tag appears
    if a.no_sfx:
        fc += "[am0]anull[am];"
    else:
        sfx = make_sfx(tmp)
        VOLP = {}
        if a.sfx_style == "pro":   # designed sounds replace the basic ones
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import sfx_pro
            pro = sfx_pro.make_all(tmp)
            sfx.update({"click": pro["pop"], "pop": pro["sparkle"], "whoosh": pro["swoosh"], "boom": pro["hit"], "ding": pro["sparkle"]})
            VOLP = {"click": 0.30, "pop": 0.30, "whoosh": 0.30, "ding": 0.30, "boom": 0.45}
        mix, n_mix = ["[am0]"], 1
        VOL = {"click": 0.35, "whoosh": 0.25, "pop": 0.38, "ding": 0.28, "boom": 0.8}
        VOL.update(VOLP)
        whoosh_used = False   # Mustafa: whoosh must not repeat -> once per reel
        for i, (ea, eb, _t, ems, tags) in enumerate(events):
            kinds = {kd for kd, _ in tags}
            plan = ["click"] if "*" in _t else []
            if kinds & {"broll", "doc"} and not whoosh_used and not a.text_sfx_only:
                plan.append("whoosh"); whoosh_used = True
            if ems or kinds & {"sparks", "icon", "circle", "arrow", "notif", "leak"}: plan.append("pop")
            if kinds & {"ding", "flash", "money"} and not a.text_sfx_only: plan.append("ding")
            if "shake" in kinds and not a.text_sfx_only: plan.append("boom")
            for kind in plan:
                extra_inputs += ["-i", sfx[kind]]
                ms = int(max(ea - 0.03, 0) * 1000)
                vol = VOL[kind]
                fc += f"[{n_in}:a]adelay={ms}|{ms},volume={vol}[sf{n_in}];"
                mix.append(f"[sf{n_in}]")
                n_in += 1
        if a.hook and not a.text_sfx_only:
            boom = os.path.join(tmp, "boom.wav")
            if a.sfx_style == "pro":
                boom = sfx["boom"]
            else:
                run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=55:d=0.7", "-af",
                     "vibrato=f=6:d=0.3,afade=t=out:st=0.05:d=0.65,volume=1.6", "-ar", "48000", "-ac", "2", boom])
            extra_inputs += ["-i", boom]
            fc += f"[{n_in}:a]volume={VOL['boom'] if a.sfx_style == 'pro' else 1}[sfboom];"; mix.append("[sfboom]"); n_in += 1
        if a.music:
            mpath = a.music
            if a.music == "beat":
                mpath = os.path.join(tmp, "beat.wav")
                run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_beat.py"), mpath, f"{total + 0.5:.2f}", str(a.bpm)])
            extra_inputs += ["-i", mpath]
            fc += f"[{n_in}:a]atrim=0:{total:.2f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=0.16,afade=t=out:st={max(total - 0.6, 0):.2f}:d=0.6[mus];"
            mix.append("[mus]"); n_in += 1
        fc += "".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.95[am];"
    if a.no_endcard:
        fc += f"[vm]subtitles={ass}:fontsdir={FONTS_DIR}[vout];[am]anull[aout]"
    else:
        if endcard:   # animated Remotion end card
            extra_inputs += ["-i", endcard]
            fc += (f"[{n_in}:v]scale={W}:{H},fps=30,format=yuv420p,setsar=1,"
                   f"trim=duration={ENDCARD_SECS},setpts=PTS-STARTPTS[card];")
            n_in += 1
        else:
            fc += f"color=c=0x{BRAND['navy']}:s={W}x{H}:d={ENDCARD_SECS}:r=30,format=yuv420p,setsar=1[card];"
        if a.sfx_style == "pro" and not a.no_sfx:   # chime under the end card instead of silence
            extra_inputs += ["-i", sfx_pro_chime(tmp)]
            fc += (f"[{n_in}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.35,apad,atrim=0:{ENDCARD_SECS}[csil];")
            n_in += 1
        else:
            fc += f"anullsrc=r=48000:cl=stereo,atrim=0:{ENDCARD_SECS}[csil];"
        fc += (f"[vm]format=yuv420p,setsar=1[vms];[vms][card]concat=n=2:v=1:a=0[vv];[am][csil]concat=n=2:v=0:a=1[aout];"
               f"[vv]subtitles={ass}:fontsdir={FONTS_DIR}[vout]")
    run(["ffmpeg", "-v", "error", "-y", "-i", a.src, *extra_inputs, "-filter_complex", fc,
         "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-crf", "21",
         "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", out])
    print(f"OK -> {out}  (kept {total:.1f}s of {sum(b-x for x,b in segs):.1f}s segments, {n} segment(s))")


if __name__ == "__main__":
    sys.exit(main())
