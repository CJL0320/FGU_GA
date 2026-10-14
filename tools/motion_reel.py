#!/usr/bin/env python3
"""Faceless motion-graphics reel (no filming needed) in Mustafa's identity:
Remotion `TipReel` scenes from a JSON file + designed SFX (tools/sfx_pro.py) + the animated end card.
  python3 tools/motion_reel.py subs/reel_motion1.json videos/reel_motion1.mp4
JSON: {"scenes": [{"d": frames@30fps, "kicker": "...", "title": "...", "sub": "...", "icon": "<ic_NAME in remotion/public>", "big": true}]}
"""
import glob, json, os, subprocess, sys, tempfile
TOOLS = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import sfx_pro, edit_reel


def main(js, out):
    tmp = tempfile.mkdtemp()
    vid = os.path.join(tmp, "tip.mp4")
    chrome = (glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell") or [None])[0]
    cmd = ["npx", "remotion", "render", "src/index.ts", "TipReel", vid, "--props=" + os.path.abspath(js), "--log=error"]
    if chrome: cmd.append(f"--browser-executable={chrome}")
    subprocess.run(cmd, cwd=os.path.join(ROOT, "remotion"), check=True)
    edit_reel.refresh_generated_cache()
    end = edit_reel.render_endcard()
    p = sfx_pro.make_all(tmp)
    sc = json.load(open(js))["scenes"]; ev = []; t = 0
    for i, s in enumerate(sc):
        st = t / 30
        if i == 0: ev.append(("hit", st, 0.5))
        elif i == 1: ev.append(("swoosh", st, 0.45))
        if s.get("icon"): ev.append(("sparkle", st + 0.05, 0.4))
        for j in range(len(s["title"].split())): ev.append(("pop", st + (3 + j * 4) / 30, 0.45))
        if s.get("sub"): ev.append(("pop", st + 12 / 30, 0.35))
        t += s["d"]
    total = t / 30
    ev.append(("chime", total + 0.1, 0.5))
    inp = ["-i", vid, "-i", end]; fc = "[0:v][1:v]concat=n=2:v=1:a=0[v];"; mix = []
    for k, (n, st, vol) in enumerate(ev):
        inp += ["-i", p[n]]; ms = int(st * 1000)
        fc += f"[{k + 2}:a]adelay={ms}|{ms},volume={vol}[a{k}];"; mix.append(f"[a{k}]")
    fc += "".join(mix) + f"amix=inputs={len(mix)}:normalize=0,alimiter=limit=0.95,apad,atrim=0:{total + 3:.2f}[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    print("OK ->", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
