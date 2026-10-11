"""Thumbnail / cover: pick the sharpest, best-lit frame and put a short bold text on it.

usage: python3 tools/thumbnail.py <video> <out.jpg> --text "THREE WORD TEXT" [--color #FFD400] [--accent 2] [--at SECONDS] [--pos top|middle|bottom]
--accent N colors the Nth word (1-based) in --color; the rest are white.
"""
import argparse, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from media import FFMPEG, probe, report

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--text", required=True)
ap.add_argument("--color", default="#FFD400")
ap.add_argument("--accent", type=int, default=0, help="which word gets the color (0 = last word)")
ap.add_argument("--at", type=float, default=None, help="use the frame at this second instead of the automatic pick")
ap.add_argument("--pos", choices=["top", "middle", "bottom"], default="top", help="where the text goes")
a = ap.parse_args()

info = probe(a.src); W, H = info["width"], info["height"]
n = max(8, int(info["duration"] * 2))
raw = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", a.src, "-vf", f"fps={n / max(info['duration'], 0.1):.4f},scale={W // 4}:{H // 4}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H // 4, W // 4, 3).astype(np.float32)


def score(f):
    g = f.mean(axis=2); lap = np.abs(4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).mean()   # sharpness
    light = 1 - abs(g.mean() - 128) / 128                                                                                       # not too dark or bright
    color = f.std(axis=2).mean() / 64                                                                                           # colorful
    return lap * (0.6 + light) * (0.8 + color)


skip = max(1, len(frames) // 10)                         # avoid the very first and last moments
best = max(range(skip, len(frames) - skip) or range(len(frames)), key=lambda i: score(frames[i]))
t = best / len(frames) * info["duration"] if a.at is None else min(max(0.0, a.at), info["duration"] - 0.05)
full = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", a.src, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
im = Image.frombuffer("RGB", (W, H), full).convert("RGBA")

# darken the top for the text, then the words, stacked, as big as they fit
grad = Image.new("L", (1, H)); c0 = {"top": 0.0, "middle": 0.5, "bottom": 1.0}[a.pos]
[grad.putpixel((0, y), int(200 * max(0, 1 - abs(y / H - c0) / 0.55) ** 1.3)) for y in range(H)]
im = Image.composite(Image.new("RGBA", (W, H), (0, 0, 0, 255)), im, grad.resize((W, H)))
words = a.text.upper().split(); acc = (a.accent or len(words)) - 1
hl = tuple(int(a.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
size = int(W * 0.2)
font = ImageFont.truetype(os.path.join(HERE, "fonts", "Geist.ttf"), size)
try: font.set_variation_by_axes([900])
except Exception: pass
while max(font.getlength(w) for w in words) > W * 0.86 and size > 40:
    size -= 6; font = ImageFont.truetype(os.path.join(HERE, "fonts", "Geist.ttf"), size)
    try: font.set_variation_by_axes([900])
    except Exception: pass
block = len(words) * int(size * 1.02); y0 = {"top": int(H * 0.08), "middle": (H - block) // 2, "bottom": H - block - int(H * 0.1)}[a.pos]
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh); y = y0
for i, w in enumerate(words):
    d.text(((W - font.getlength(w)) / 2, y + size * 0.06), w, font=font, fill=(0, 0, 0, 180)); y += int(size * 1.02)
im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(size * 0.06))); d = ImageDraw.Draw(im); y = y0
for i, w in enumerate(words):
    d.text(((W - font.getlength(w)) / 2, y), w, font=font, fill=(hl + (255,)) if i == acc else (255, 255, 255, 255)); y += int(size * 1.02)
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
im.convert("RGB").save(a.out, quality=92)
report(tool="thumbnail", out=a.out, frame_at_seconds=round(t, 2), text=" ".join(words), position=a.pos, size=f"{W}x{H}")
