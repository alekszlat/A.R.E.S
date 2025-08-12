# Jarvis AI – Local Voice Assistant

Jarvis AI is a **fully local voice assistant** that uses:
- **Whisper.cpp** for speech-to-text (STT)
- **Llama.cpp** for natural language processing (LLM)
- **Piper** for text-to-speech (TTS)

No internet connection is required for processing — all models run locally.

---

## Features (Current Progress)
✅ **Speech-to-Text (STT)**  
- Records audio via `sounddevice` or `arecord`  
- Uses `whisper-cli` to transcribe to text  

✅ **Local Language Model (LLM)**  
- Runs `llama.cpp` in server mode for prompt completion  
- Configurable system prompts for personality (e.g., "Jarvis" style)  

✅ **Text-to-Speech (TTS)**  
- Piper HTTP server generates speech from LLM responses  
- Supports multiple voices (e.g., `en_US-bryce-medium`)  

✅ **Main Pipeline**  
- Record → Transcribe → Send to LLM → Speak back with Piper  

✅ **Benchmarking**  
- `latency.md` logs STT, LLM, and TTS timings for performance tuning  

---

## Current Workflow
1. **Start LLM server**  
```bash
cd server/llama.cpp
./server/run_llama_server.sh
```

2. **Start Piper HTTP server** 
```bash
python3 -m piper.http_server -m en_US-bryce-medium --data-dir ./models/piper
```

3. **Run Jarvis main loop** 
```bash
python3 main.py
```


