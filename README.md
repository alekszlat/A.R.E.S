# A.R.E.S – Artificial Reasoning Engineered System

Ares is a **fully local voice assistant** that combines:
- 🎤 **Whisper.cpp** for speech-to-text (STT)
- 🧠 **Llama.cpp** for natural language processing (LLM)
- 🔊 **Piper** for text-to-speech (TTS)
- 👂 **OpenWakeWord** for wake word detection ("Hey Ares")

Everything runs **offline** — no internet is required for processing.  
Ares is designed to be modular, hackable, and extendable to control smart devices or even robots.

---

## ✨ Features (Current Progress)

✅ **Wake Word ("Hey Ares/Ares")**  
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
- GitHub Actions run Ares in **Mock Mode** (no audio hardware required)  
- Simulates STT, LLM, and TTS responses for automated testing  

---

## Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

Also build:
- [Whisper.cpp](https://github.com/ggml-org/whisper.cpp)
- [Llama.cpp](https://github.com/ggml-org/llama.cpp)
- [Piper](https://github.com/rhasspy/piper)


### 2. Start LLM + TTS servers
```bash
./scripts/run_servers.sh
```

Say "Hey Ares", wait for the beep 🎵, then speak your command.
Ares will listen, process locally, and respond with speech.

## 🧪 Development & Testing
### Benchmark Latency
```bash
./scripts/benchmark_ai.sh
```

## 📂 Project Structure
```graphql
llmio/               # Input/output modules
 ├─ stt_whisper.py   # Speech-to-text
 ├─ tts_piper.py     # Text-to-speech
 ├─ llm_remote.py    # LLM client
 └─ wake_word.py     # Wake word listener

scripts/             # Helper scripts
 └─ run_servers.sh   # Start LLM and TTS servers

latency.md           # Benchmark results
ci_runner.py         # CI harness with mocks
main.py              # Main application loop

```

## ⚙️ Roadmap

### Voice & Interaction
- Custom wake word — trainable per device/user.
- Custom voice — selectable TTS voice profiles.

### Web & App Actions
- Open websites & apps on command

### Devices & I/O
- Bluetooth device control — pair/connect/disconnect and volume controls.

### Perception
- Visual detection — optional camera input for object/face/basic scene cues.

### Architecture/Security
- Speaker recognition — per-user profiles for personalization/permissions.
- Split LLM server — dedicated local endpoint with resource limits & auth.

### Hardware
- Custom hardware build — mic array, LEDs, physical mute, action button.
