# mocks.py
def enable():
    """
    Install mock modules/classes so main.py can import normally,
    but CI/headless runs never touch real audio or hardware.
    """
    import sys, types, time

    # wake_word
    mock_wake = types.ModuleType("llmio.wake_word")
    class WakeWord_Listener:
        def __init__(self, *a, **k): print("[MOCK] WakeWord_Listener.__init__")
        def listen(self) -> bool:
            print("[MOCK] WakeWord_Listener.listen() -> True")
            return True
    mock_wake.WakeWord_Listener = WakeWord_Listener
    sys.modules["llmio.wake_word"] = mock_wake

    # stt_whisper
    mock_stt = types.ModuleType("llmio.stt_whisper")
    mock_stt.record_audio = lambda *a, **k: "/tmp/mock.wav"
    mock_stt.transcribe   = lambda *a, **k: "what time is it?"
    sys.modules["llmio.stt_whisper"] = mock_stt

    # llm_remote
    mock_llm = types.ModuleType("llmio.llm_remote")
    mock_llm.complete = lambda prompt, *a, **k: "It’s 14:05. Anything else?"
    sys.modules["llmio.llm_remote"] = mock_llm

    # tts_piper
    mock_tts = types.ModuleType("llmio.tts_piper")
    mock_tts.speak = lambda text, *a, **k: print(f"[MOCK] TTS speak: {text[:40]!r}")
    sys.modules["llmio.tts_piper"] = mock_tts
