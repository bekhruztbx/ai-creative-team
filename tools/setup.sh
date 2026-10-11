#!/usr/bin/env bash
# One-time setup: checks ffmpeg and Node, installs a local speech-to-text engine, creates the folders.
set -e
cd "$(dirname "$0")/.."
command -v ffmpeg >/dev/null || { echo "Install ffmpeg first (macOS: brew install ffmpeg)"; exit 1; }
command -v npx >/dev/null || { echo "Install Node.js 18+ first (it runs the shared-brain memory server)"; exit 1; }
python3 -m pip install --quiet numpy pillow
if python3 -m pip install --quiet faster-whisper; then
  echo "speech-to-text: faster-whisper (downloads its model on first use)"
else
  echo "faster-whisper did not install, using sherpa-onnx Whisper instead"
  python3 -m pip install --quiet sherpa-onnx
  mkdir -p tools/models
  curl -L -o /tmp/whisper-tiny.en.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-tiny.en.tar.bz2
  tar xjf /tmp/whisper-tiny.en.tar.bz2 -C tools/models
fi
mkdir -p inbox out done brain
echo
echo "Ready. Put raw clips in inbox/, start Claude Code here with: claude"
echo "then type: /edit-clips"
