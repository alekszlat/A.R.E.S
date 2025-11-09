#!/usr/bin/env bash
cd "$(dirname "$0")"
./llama.cpp/build/bin/llama-server \
  -m ../models/llama-2-7b.Q4_0.gguf \
  -c 2048 \
  -ngl 35 \
  --port 8080