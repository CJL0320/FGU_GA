#!/usr/bin/env bash
# Mustafa's saved reel style (= reel3_v2_motion, chosen by him). One command for every new reel:
#   tools/reel_mustafa.sh videos/reelN.mov subs/reelN.srt "hook with *key* word" [videos/reelN_final.mp4]
# FULL-SCREEN layout (Mustafa removed the white card background 2026-10-07), his original colours (no filter), key words only as neon captions in the brand palette C
# (ice-blue -> violet + script word; Readex Pro / Sora), hook card + one light shake, one intro zoom-out, whoosh once,
# generated beat, 3D b-roll / circle / neon icons from the .srt tags, top-left K+M coin badge, animated end card.
# Also writes a <out>_send.mp4 copy small enough to send in the chat (< 30 MB).
set -euo pipefail
SRC="$1"; SRT="$2"; HOOK="${3:-}"
OUT="${4:-${SRC%.*}_final.mp4}"
cd "$(dirname "$0")/.."
python3 tools/edit_reel.py "$SRC" --srt "$SRT" \
  --layout full --grade none --keywords-only --accent 38BDF8 \
  --zoom-mode intro --sfx-style pro --wa-badge --no-endcard \
  ${HOOK:+--hook "$HOOK"} --out "$OUT"
ffmpeg -v error -y -i "$OUT" -c:v libx264 -crf 25 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 128k -movflags +faststart "${OUT%.mp4}_send.mp4"
echo "done: $OUT + ${OUT%.mp4}_send.mp4"
