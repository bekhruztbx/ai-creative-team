"""Contact sheet: six frames of a video in one image, so an agent can look at an edit with the Read tool.

usage: python3 tools/frames.py <video> <out.jpg>
"""
import os, subprocess, sys
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from media import FFMPEG, probe, report

src, out = sys.argv[1], sys.argv[2]
info = probe(src); W, H = info["width"], info["height"]; tw = 270; th = int(tw * H / W); sheet = Image.new("RGB", (tw * 3 + 40, th * 2 + 30), (12, 12, 16))
for i in range(6):
    t = info["duration"] * (i + 0.5) / 6
    raw = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1", "-vf", f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    im = Image.frombuffer("RGB", (tw, th), raw); x, y = 10 + (i % 3) * (tw + 10), 10 + (i // 3) * (th + 10); sheet.paste(im, (x, y))
    ImageDraw.Draw(sheet).text((x + 8, y + 6), f"{t:.1f}s", fill=(255, 255, 0))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True); sheet.save(out, quality=85)
report(tool="frames", out=out, frames=6, seconds=round(info["duration"], 1))
