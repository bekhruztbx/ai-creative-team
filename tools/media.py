"""Small ffmpeg helpers shared by the tools. Only needs ffmpeg on PATH (set FFMPEG to use another binary)."""
import json, os, re, subprocess, sys
import numpy as np

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")


def run(args, **kw):
    """Run ffmpeg quietly; raise with its stderr if it fails."""
    p = subprocess.run([FFMPEG, "-hide_banner", "-y"] + args, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-2000:])
    return p


def probe(path):
    """Duration (s), width, height and fps of a video, read from ffmpeg's own banner."""
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    v = re.search(r"Video: .*?(\d{2,5})x(\d{2,5})", err)
    f = re.search(r"([\d.]+) fps", err)
    if not d:
        raise RuntimeError(f"cannot read {path}")
    dur = int(d[1]) * 3600 + int(d[2]) * 60 + float(d[3])
    return {"duration": dur, "width": int(v[1]) if v else 0, "height": int(v[2]) if v else 0, "fps": float(f[1]) if f else 30.0}


def audio(path, sr=16000):
    """Mono float32 audio samples of a media file."""
    raw = subprocess.run([FFMPEG, "-hide_banner", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def speech_segments(path, noise_db=-32, min_silence=0.45):
    """[(start, end)] of the non-silent parts, from ffmpeg's silencedetect."""
    err = run(["-i", path, "-vn", "-af", f"silencedetect=noise={noise_db}dB:d={min_silence}", "-f", "null", "-"]).stderr
    dur = probe(path)["duration"]
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    segs, t = [], 0.0
    for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if s > t + 0.05:
            segs.append((t, s))
        t = e
    if t < dur - 0.05:
        segs.append((t, dur))
    return segs


def report(**kw):
    """One JSON line on stdout, so the agent can read the result."""
    print(json.dumps(kw, ensure_ascii=False))
    sys.stdout.flush()


FILLERS = {"um", "uh", "erm", "er", "hmm", "ah", "uhm", "mm"}


class STT:
    """Local speech-to-text: faster-whisper if installed, otherwise sherpa-onnx Whisper (see tools/setup.sh)."""
    def __init__(self):
        try:
            from faster_whisper import WhisperModel
            self.fw = WhisperModel(os.environ.get("WHISPER_MODEL", "small.en"), compute_type="int8"); self.engine = "faster-whisper"
        except ImportError:
            import sherpa_onnx
            here = os.path.dirname(os.path.abspath(__file__))
            d = os.environ.get("WHISPER_ONNX_DIR", os.path.join(here, "models", "sherpa-onnx-whisper-tiny.en"))
            pre = os.path.join(d, os.path.basename(d).replace("sherpa-onnx-whisper-", "") + "-")
            self.rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=pre + "encoder.int8.onnx", decoder=pre + "decoder.int8.onnx", tokens=pre + "tokens.txt",
                                                                  language="en", task="transcribe", num_threads=2)
            self.fw = None; self.engine = "sherpa-onnx whisper"

    def text(self, pcm, sr=16000):
        """Transcript of a short piece of audio."""
        if self.fw is not None:
            segs, _ = self.fw.transcribe(pcm, language="en")
            return " ".join(x.text.strip() for x in segs)
        st = self.rec.create_stream(); st.accept_waveform(sr, pcm); self.rec.decode_stream(st)
        return st.result.text.strip()


KEEP = {"okay", "ok", "yes", "yeah", "no", "so", "right", "wow", "hi", "hey", "go", "now"}


def only_fillers(text, seconds=None):
    """True for "um", "uh"... A lone sound shorter than 0.55 s that is not a real short word counts too:
    small models often write a stray "um" as "armed" or "1"."""
    words = [re.sub(r"[^a-z]", "", w.lower()) for w in text.split()]
    words = [w for w in words if w]
    if seconds is not None and seconds < 0.55 and len(words) <= 1 and not (words and words[0] in KEEP):
        return True
    return bool(words) and all(w in FILLERS for w in words)
