"""Rough cut: drop every pause, keep the talking, cap the length and reframe to vertical 1080x1920.

usage: python3 tools/cut.py <raw clip> <out.mp4> [--max 45] [--pause 0.45] [--frame crop|blur] [--keep-fillers]
Phrases that are only filler words ("um", "uh") are dropped unless --keep-fillers is given.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from media import STT, audio, only_fillers, probe, report, run, speech_segments

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--max", type=float, default=45, help="longest allowed edit in seconds")
ap.add_argument("--pause", type=float, default=0.45, help="cut pauses longer than this (s)")
ap.add_argument("--pad", type=float, default=0.12, help="breathing room kept around each phrase (s)")
ap.add_argument("--frame", choices=["crop", "blur"], default="crop", help="how a wide clip becomes vertical")
ap.add_argument("--keep-fillers", action="store_true", help="keep phrases that are only um/uh")
a = ap.parse_args()

info = probe(a.src)
segs = speech_segments(a.src, min_silence=a.pause)
fillers = []
if not a.keep_fillers:                              # a short phrase that is only "um"/"uh" goes
    stt, pcm, kept = STT(), audio(a.src), []
    for s, e in segs:
        txt = stt.text(pcm[int(s * 16000):int(e * 16000)]) if e - s < 1.6 else ""
        if txt and only_fillers(txt, e - s):
            fillers.append((round(s, 2), txt))
        else:
            kept.append((s, e))
    segs = kept
keep, total = [], 0.0
for s, e in segs:                                   # pad each phrase, merge overlaps, stop at --max
    s, e = max(0.0, s - a.pad), min(info["duration"], e + a.pad)
    if keep and s <= keep[-1][1]:
        keep[-1] = (keep[-1][0], e)
    else:
        keep.append((s, e))
out, total = [], 0.0
for s, e in keep:
    if total + (e - s) > a.max:
        e = s + (a.max - total)
    if e - s > 0.2:
        out.append((s, e)); total += e - s
    if total >= a.max - 0.05:
        break

parts = "".join(f"[0:v]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[a{i}];" for i, (s, e) in enumerate(out))
cat = "".join(f"[v{i}][a{i}]" for i in range(len(out))) + f"concat=n={len(out)}:v=1:a=1[cv][ca]"
if a.frame == "crop":
    frame = "[cv]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v]"
else:
    frame = "[cv]split[b][f];[b]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40[bg];[f]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]"
os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
run(["-i", a.src, "-filter_complex", parts + cat + ";" + frame + ";[ca]loudnorm=I=-14:TP=-1.5[a]", "-map", "[v]", "-map", "[a]",
     "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", a.out])
report(tool="cut", out=a.out, raw_seconds=round(info["duration"], 1), edit_seconds=round(total, 1), removed_seconds=round(info["duration"] - total, 1), phrases_kept=len(out),
       fillers_removed=[f"{t}s {w}" for t, w in fillers])
