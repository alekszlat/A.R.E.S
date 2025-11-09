#!/usr/bin/env bash
set -e

# 1) start llama in a tab or background (example)
tmux new-session -d -s ares "cd server/llama.cpp && ./build/bin/llama-server -m ../../models/llama-2-7b.Q4_0.gguf -c 2048 -ngl 35 --port 8080"

# 2) give it a second, then start Piper
tmux split-window -t ares "cd ~/Projects/A.R.E.S && python3 -m piper.http_server -m models/piper/en_US-bryce-medium --data-dir models/piper"

tmux attach -t ares
