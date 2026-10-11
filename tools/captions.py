"""Transcribe a clip, write an .srt and burn word-by-word captions into the video.

usage: python3 tools/captions.py <in.mp4> <out.mp4> [--srt captions.srt] [--color #FFD400] [--words 3] [--y 0.70] [--replace "wrong=right" ...]

Speech-to-text runs locally: faster-whisper if it is installed (word timestamps), otherwise sherpa-onnx Whisper
(model folder in $WHISPER_ONNX_DIR or tools/models/sherpa-onnx-whisper-tiny.en, see tools/setup.sh).
"""
import argparse, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from media import FFMPEG, STT, audio, probe, report, speech_segments

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--srt", default=None)
ap.add_argument("--color", default="#FFD400", help="highlight color of the word being spoken")
ap.add_argument("--words", type=int, default=3, help="words per caption")
ap.add_argument("--y", type=float, default=0.70, help="vertical position (0 top .. 1 bottom)")
ap.add_argument("--size", type=int, default=92)
ap.add_argument("--replace", action="append", default=[], help='fix a misheard word, e.g. --replace "Post=Posts" (repeatable)')
a = ap.parse_args()
SR = 16000


def words_faster_whisper(path):
    from faster_whisper import WhisperModel
    m = WhisperModel(os.environ.get("WHISPER_MODEL", "small.en"), compute_type="int8")
    segs, _ = m.transcribe(path, word_timestamps=True, vad_filter=True)
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words if w.word.strip()]


def words_phrases(path):
    """Phrase by phrase transcription; each phrase's time is spread over its words by length."""
    stt, pcm, out = STT(), audio(path, SR), []
    for s, e in speech_segments(path, noise_db=-35, min_silence=0.2):
        toks = stt.text(pcm[int(s * SR):int(e * SR)]).split()
        if not toks: continue
        wts = [len(re.sub(r"\W", "", t)) + 2 for t in toks]; tot = sum(wts); t = s + 0.05; span = (e - s) - 0.1
        for tok, w in zip(toks, wts):
            dur = span * w / tot; out.append((tok, t, t + dur * 0.92)); t += dur
    return out


try:
    import faster_whisper  # noqa: F401
    words, engine = words_faster_whisper(a.src), "faster-whisper"
except ImportError:
    words, engine = words_phrases(a.src), "sherpa-onnx whisper"
fixes = dict(r.split("=", 1) for r in a.replace if "=" in r)
words = [(fixes.get(re.sub(r"[.,!?]+$", "", w), None) and fixes[re.sub(r"[.,!?]+$", "", w)] + w[len(re.sub(r"[.,!?]+$", "", w)):] or w, s0, e0) for w, s0, e0 in words]

# captions of N words, never across a sentence end
caps, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) >= a.words or re.search(r"[.!?]$", w[0]):
        caps.append(cur); cur = []
if cur: caps.append(cur)
if len(caps) > 1 and len(caps[-1]) == 1:          # no lonely last word: borrow one from the caption before
    if len(caps[-2]) > 1: caps[-1].insert(0, caps[-2].pop())
    else: caps[-2].extend(caps.pop())


def ts(t): ms = int(round(t * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
srt = a.srt or os.path.splitext(a.out)[0] + ".srt"
with open(srt, "w") as f:
    for i, c in enumerate(caps):
        end = c[-1][2] + 0.15 if i + 1 == len(caps) else min(c[-1][2] + 0.15, caps[i + 1][0][1] - 0.02)
        f.write(f"{i + 1}\n{ts(c[0][1])} --> {ts(end)}\n{' '.join(w[0] for w in c)}\n\n")

# burn in: white words with a dark outline, the spoken word in the brand color
info = probe(a.src); W, H, FPS = info["width"], info["height"], info["fps"] or 30
font = ImageFont.truetype(os.path.join(HERE, "fonts", "Geist.ttf"), a.size)
try: font.set_variation_by_axes([850])
except Exception: pass
hl = tuple(int(a.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
cache = {}


def overlay(ci, wi):
    key = (ci, wi)
    if key in cache: return cache[key]
    c = caps[ci]; txt = [re.sub(r"[.,!?]+$", "", w[0]).upper() for w in c]
    gap = a.size * 0.28; ws = [font.getlength(t) for t in txt]; total = sum(ws) + gap * (len(ws) - 1)
    im = Image.new("RGBA", (W, int(a.size * 2.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = (W - total) / 2
    for i, (t, w) in enumerate(zip(txt, ws)):
        d.text((x, a.size * 0.4), t, font=font, fill=(hl + (255,)) if i == wi else (255, 255, 255, 255), stroke_width=max(4, a.size // 12), stroke_fill=(0, 0, 0, 255))
        x += w + gap
    arr = np.asarray(im).astype(np.float32) / 255; cache[key] = arr; return arr


dec = subprocess.Popen([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", a.src,
                        "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", a.out], stdin=subprocess.PIPE)
y0 = int(H * a.y); n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    t = n / FPS; n += 1; fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    ci = next((i for i, c in enumerate(caps) if c[0][1] - 0.05 <= t < (caps[i + 1][0][1] - 0.05 if i + 1 < len(caps) else c[-1][2] + 0.4)), None)
    if ci is not None:
        wi = max([j for j, w in enumerate(caps[ci]) if w[1] - 0.03 <= t] or [0])
        ov = overlay(ci, wi); h = ov.shape[0]; ya, yb = max(0, y0 - h // 2), min(H, y0 - h // 2 + h)
        region = fr[ya:yb].astype(np.float32) / 255; al = ov[: yb - ya, :, 3:4]
        fr = fr.copy(); fr[ya:yb] = ((region * (1 - al) + ov[: yb - ya, :, :3] * al) * 255 + .5).astype(np.uint8)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); dec.wait()
report(tool="captions", out=a.out, srt=srt, engine=engine, words=len(words), captions=len(caps), replaced=fixes, transcript=" ".join(w[0] for w in words)[:600])
