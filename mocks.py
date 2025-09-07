# mocks.py
def enable():
    """
    Install mock modules/classes so main.py can import normally,
    but CI/headless runs never touch real audio or hardware.
    """
    import sys, types

    # ---- Mock wake_word module ----
    mock_wake = types.ModuleType("llmio.wake_word")

    class WakeWord_Listener:
        def __init__(self, *args, **kwargs):
            print("[MOCK] WakeWord_Listener.__init__")
        def listen(self) -> bool:
            print("[MOCK] WakeWord_Listener.listen() -> True")
            return True

    mock_wake.WakeWord_Listener = WakeWord_Listener
    sys.modules["llmio.wake_word"] = mock_wake

    # (Optional) also mock other I/O-heavy modules if you want)
    # Example: fake STT/TTS/LLM for CI smoke tests:
    mock_stt = types.ModuleType("llmio.stt_whisper")
    def _stt_record_audio(*a, **k): return "/tmp/mock.wav"
    def _stt_transcribe(*a, **k):   return "what time is it?"
    mock_stt.record_audio = _stt_record_audio
    mock_stt.transcribe   = _stt_transcribe
    sys.modules.setdefault("llmio.stt_whisper", mock_stt)

    mock_tts = types.ModuleType("llmio.tts_piper")
    def _speak(text, *a, **k):
        print(f"[MOCK] TTS speak: {text[:60]!r}")
    mock_tts.speak = _speak
    sys.modules.setdefault("llmio.tts_piper", mock_tts)

    mock_llm = types.ModuleType("llmio.llm_remote")
    def _complete(prompt, *a, **k):
        return "It's 14:05. Anything else?"
    mock_llm.complete = _complete
    sys.modules.setdefault("llmio.llm_remote", mock_llm)
