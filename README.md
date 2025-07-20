# jarvis-ai
Working with AI models



chat-llm/
├── README.md                  # quick-start, commands, credits
├── docs/                      # screenshots, latency notes, issues
│   └── troubleshooting.md
|   |__ latency.md
│
├── io/                        # thin adapters (pure-Python)
│   ├── stt_whisper.py         # mic → Whisper.cpp → text
│   ├── tts_piper.py           # text → Piper/Coqui → wav → speakers
│   └── llm_remote.py          # POST prompt → local llama server
│
├── models/                    
│   └── .gitignore             
│
├── server/                    # **optional** helper to host the LLM
│   ├── run_llama_server.sh    # build & launch llama.cpp server
│   └── README.md
│
├── main.py                    # orchestrates mic → LLM → TTS loop
│
├── requirements.txt           # requests, sounddevice, pyyaml, python-dotenv
├── .env.example               
├── .gitignore                 
└── .github/
    └── workflows/
        └── ci.yml             # lint + 30-sec smoke test (no audio)