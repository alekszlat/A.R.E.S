# J.A.R.V.I.S – Local Voice Assistant

Jarvis is a **fully local voice assistant** that combines:
- 🎤 **Whisper.cpp** for speech-to-text (STT)
- 🧠 **Llama.cpp** for natural language processing (LLM)
- 🔊 **Piper** for text-to-speech (TTS)
- 👂 **OpenWakeWord** for wake word detection ("Hey Jarvis")

⚡ Everything runs **offline** — no internet is required for processing.  
Jarvis is designed to be modular, hackable, and extendable to control smart devices or even robots.

---

## ✨ Features (Current Progress)

✅ **Wake Word ("Hey Jarvis")**  
- Powered by [OpenWakeWord](https://github.com/dscripka/openWakeWord?tab=readme-ov-file)  
- Starts listening only after hearing the wake phrase  

✅ **Speech-to-Text (STT)**  
- Uses `sounddevice` + `webrtcvad` for smart recording (stops when you go quiet)  
- Transcribes audio with `whisper-cli` (from Whisper.cpp)  

✅ **Local Language Model (LLM)**  
- Runs `llama.cpp` in server mode  
- Configurable system prompt → "Jarvis"-like personality  

✅ **Text-to-Speech (TTS)**  
- Piper HTTP server generates natural-sounding voices  
- Multiple voices available (e.g., `en_US-bryce-medium`)  

✅ **Main Pipeline**  
Wake Word → Record → Transcribe → Send to LLM → Speak Response

✅ **Benchmarking**  
- `benchmark_ai.sh` logs timings for STT, LLM, and TTS  
- Results are stored in `latency.md`  

✅ **CI / Mock Mode**  
- GitHub Actions run Jarvis in **Mock Mode** (no audio hardware required)  
- Simulates STT, LLM, and TTS responses for automated testing  

---

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

Also build:
- Whisper.cpp
- Llama.cpp
- Piper


### 2. Start LLM + TTS servers
```bash
./scripts/run_servers.sh
```

Say "Hey Jarvis", wait for the beep 🎵, then speak your command.
Jarvis will listen, process locally, and respond with speech.

