#!/usr/bin/env bash
# benchmark_ai.sh — STT (whisper.cpp) + LLM (llama.cpp server) + TTS (Piper HTTP)
# Prints a ready-to-paste Markdown table row with timings in ms.

set -euo pipefail

### ---------------- Config (edit to your paths/ports) ----------------
DATE=$(date +%F)

# STT (whisper.cpp)
WHISPER_BIN="./server/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL="./models/ggml-base.en.bin"
STT_WAV="/tmp/stt_bench.wav"
STT_RECORD_SEC=${STT_RECORD_SEC:-3}

# LLM (llama.cpp server)
LLM_URL=${LLM_URL:-http://127.0.0.1:8080/completion}
LLM_PROMPT=${LLM_PROMPT:-Hello}
LLM_NPREDICT=${LLM_NPREDICT:-64}

# TTS (Piper HTTP)
TTS_URL=${TTS_URL:-http://127.0.0.1:5000}
TTS_TEXT=${TTS_TEXT:-Hello world}

### ---------------- Sanity checks ----------------
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1" >&2; exit 1; }; }

need arecord
need awk
need curl
need bc

[ -x "$WHISPER_BIN" ] || { echo "Not executable: $WHISPER_BIN" >&2; exit 1; }
[ -f "$WHISPER_MODEL" ] || { echo "Missing model: $WHISPER_MODEL" >&2; exit 1; }

# quick reachability
curl -sS -o /dev/null --connect-timeout 2 "$TTS_URL/voices" || { echo "TTS not reachable at $TTS_URL" >&2; exit 1; }
curl -sS -o /dev/null --connect-timeout 2 "$LLM_URL" || true # some servers 404 on GET; will test with POST below

### ---------------- 1) STT timing ----------------
# Clean recording (no kill errors)
arecord -f S16_LE -r 16000 -c 1 -d "$STT_RECORD_SEC" "$STT_WAV" >/dev/null 2>&1

# whisper.cpp prints timings to stderr; parse the number before 'ms'
STT_MS=$(
  "$WHISPER_BIN" -t 16 -m "$WHISPER_MODEL" -f "$STT_WAV" -nt 2>&1 \
  | awk '/total time/ {print int($(NF-1)+0)}'
)
: "${STT_MS:=0}"

### ---------------- 2) LLM timing ----------------
LLM_MS=$(
  curl -sS -o /dev/null \
       -H 'Content-Type: application/json' \
       --connect-timeout 2 --max-time 30 \
       -w '%{time_total}\n' \
       -d "{\"prompt\":\"$LLM_PROMPT\",\"n_predict\":$LLM_NPREDICT}" \
       "$LLM_URL" \
  | awk 'NF{printf "%.0f", ($1*1000)}'
)
: "${LLM_MS:=0}"

### ---------------- 3) TTS timing ----------------
read TTS_CODE TTS_SIZE TTS_SEC <<<"$(
  curl -sS -o /dev/null \
       -H 'Content-Type: application/json' \
       --connect-timeout 2 --max-time 30 \
       -w '%{http_code} %{size_download} %{time_total}\n' \
       -d "{\"text\":\"$TTS_TEXT\"}" \
       "$TTS_URL"
)"

if [ "$TTS_CODE" = "200" ] && [ "$TTS_SIZE" -gt 0 ]; then
  TTS_MS=$(awk -v t="$TTS_SEC" 'BEGIN { printf("%.0f", t*1000) }')
else
  echo "TTS request failed: code=$TTS_CODE size=$TTS_SIZE" >&2
  TTS_MS=0
fi

### ---------------- 4) Total & print row ----------------
TOTAL_MS=$((STT_MS + LLM_MS + TTS_MS))
echo "| $DATE | $STT_MS | $LLM_MS | $TTS_MS | $TOTAL_MS | base.en, n_predict=$LLM_NPREDICT |" >> docs/latency.md


### ---------------- 5) Additional commands (GPU info) ----------------
#nvidia-smi   --query-gpu=timestamp,index,name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu   --format=csv,noheader,nounits   -l 1