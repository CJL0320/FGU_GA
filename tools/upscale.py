#!/usr/bin/env python3
"""AI upscale of a low-resolution phone video (e.g. 480x854) to 1080x1920 with Real-ESRGAN "realesr-general-x4v3"
(small SRVGG model, runs on CPU). The x4 result is blended with a plain Lanczos upscale (--strength, 0..1) so faces stay
natural, then resized to the target. Audio is copied untouched.
  python3 tools/upscale.py videos/reelN.mov videos/reelN_hd.mov [--strength 0.7] [--denoise 0.5]
Weights (downloaded once into assets/_generated/models):
  https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth (+ -wdn- variant)
Needs: pip install torch --index-url https://download.pytorch.org/whl/cpu
"""
import argparse, os, subprocess, sys, json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(ROOT, "assets", "_generated", "models")
URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/"


class SRVGGNetCompact(nn.Module):
    """Real-ESRGAN compact network (same layout as basicsr.archs.srvgg_arch)."""
    def __init__(self, num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4):
        super().__init__()
        self.upscale = upscale
        self.body = nn.ModuleList([nn.Conv2d(num_in_ch, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)])
        for _ in range(num_conv):
            self.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1)); self.body.append(nn.PReLU(num_parameters=num_feat))
        self.body.append(nn.Conv2d(num_feat, num_out_ch * upscale * upscale, 3, 1, 1))
        self.upsampler = nn.PixelShuffle(upscale)

    def forward(self, x):
        out = x
        for layer in self.body:
            out = layer(out)
        out = self.upsampler(out)
        return out + F.interpolate(x, scale_factor=self.upscale, mode="nearest")


def load(denoise):
    os.makedirs(MODELS, exist_ok=True)
    def weights(name):
        p = os.path.join(MODELS, name)
        if not os.path.exists(p):
            subprocess.run(["curl", "-sSL", "-o", p, URL + name], check=True)
        sd = torch.load(p, map_location="cpu")
        return sd.get("params", sd)
    a, b = weights("realesr-general-x4v3.pth"), weights("realesr-general-wdn-x4v3.pth")
    # dni: blend the normal and the "without denoise" weights (denoise 1 = full denoise, 0 = keep all detail/noise)
    sd = {k: denoise * a[k] + (1 - denoise) * b[k] for k in a}
    net = SRVGGNetCompact(); net.load_state_dict(sd, strict=True); net.eval()
    return net


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    n, d = s["r_frame_rate"].split("/")
    return s["width"], s["height"], s["r_frame_rate"], float(n) / float(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--width", type=int, default=1080); ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--strength", type=float, default=0.7, help="share of the AI result vs a plain Lanczos upscale")
    ap.add_argument("--denoise", type=float, default=0.5)
    ap.add_argument("--frames", type=int, default=0, help="only the first N frames (test)")
    a = ap.parse_args()
    torch.set_num_threads(os.cpu_count() or 4)
    w, h, rate, fps = probe(a.src)
    net = load(a.denoise)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{a.width}x{a.height}",
                            "-r", rate, "-i", "-", "-i", a.src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "slow",
                            "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", a.out], stdin=subprocess.PIPE)
    fsz = w * h * 3; i = 0
    with torch.inference_mode():
        while True:
            buf = dec.stdout.read(fsz)
            if len(buf) < fsz or (a.frames and i >= a.frames):
                break
            x = torch.from_numpy(np.frombuffer(buf, np.uint8).reshape(h, w, 3).copy()).permute(2, 0, 1)[None].float() / 255
            y = net(x).clamp(0, 1)
            y = F.interpolate(y, size=(a.height, a.width), mode="bicubic", antialias=True, align_corners=False)
            base = F.interpolate(x, size=(a.height, a.width), mode="bicubic", antialias=True, align_corners=False)
            y = (a.strength * y + (1 - a.strength) * base).clamp(0, 1)
            enc.stdin.write((y[0].permute(1, 2, 0).numpy() * 255 + 0.5).astype(np.uint8).tobytes())
            i += 1
            if i % 50 == 0:
                print(f"{i} frames", flush=True)
    dec.stdout.close(); dec.terminate(); enc.stdin.close(); enc.wait()
    print("OK ->", a.out, f"({i} frames)")


if __name__ == "__main__":
    main()
