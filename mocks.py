# mocks.py
def enable():
    try:
        from llmio import llm_remote, tts_piper, stt_whisper
    except Exception:
        import llm_remote, tts_piper, stt_whisper

    stt_whisper.record_audio = lambda duration=2, samplerate=16000: "/tmp/mock.wav"
    stt_whisper.transcribe   = lambda filename="/tmp/mock.wav": "Hi Jarvis"
    llm_remote.complete      = lambda prompt, n_predict=64: "Hello, sir! How can I help you? [MOCK]"
    tts_piper.speak          = lambda text: print(f"[MOCK TTS would say]: {text}")
    print("[MOCK_MODE] Enabled mock STT/LLM/TTS")
