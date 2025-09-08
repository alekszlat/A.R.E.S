# ci_runner.py
import os
import sys
import types
import main  # NOTE: we will import after mocks; see enable() below

class CI_Runner:
    """
    CI/headless harness that:
      - Installs mock llmio modules (no audio/devices/servers)
      - Forces a single turn
      - Skips preflight via CLI flag
    """

    def __init__(self, max_turns: int = 1):
        self.max_turns = max_turns

    # ---------- mock installers ----------
    def _mock_wake(self):
        mod = types.ModuleType("llmio.wake_word")

        class WakeWord_Listener:
            def __init__(self, *a, **k):
                print("[MOCK] WakeWord_Listener.__init__")
            def listen(self) -> bool:
                print("[MOCK] WakeWord_Listener.listen() -> True")
                return True

        mod.WakeWord_Listener = WakeWord_Listener
        sys.modules["llmio.wake_word"] = mod

    def _mock_stt(self):
        mod = types.ModuleType("llmio.stt_whisper")
        mod.record_audio = lambda *a, **k: "/tmp/mock.wav"
        mod.transcribe   = lambda *a, **k: "what time is it?"
        sys.modules["llmio.stt_whisper"] = mod

    def _mock_llm(self):
        mod = types.ModuleType("llmio.llm_remote")
        mod.complete = lambda prompt, *a, **k: "It’s 14:05. Anything else?"
        sys.modules["llmio.llm_remote"] = mod

    def _mock_tts(self):
        mod = types.ModuleType("llmio.tts_piper")
        mod.speak = lambda text, *a, **k: print(f"[MOCK] TTS speak: {text[:60]!r}")
        sys.modules["llmio.tts_piper"] = mod

    def enable(self):
        """Install mocks BEFORE importing main, set one-turn, and add --no-preflight."""
        print("[CI_Runner] Installing mock modules…")
        self._mock_wake()
        self._mock_stt()
        self._mock_llm()
        self._mock_tts()

        # one cycle only
        os.environ["MAX_TURNS"] = str(self.max_turns)

        # ensure preflight skips by CLI flag (your PreflightChecks reads sys.argv)
        if "--no-preflight" not in sys.argv:
            sys.argv.append("--no-preflight")

    def run(self) -> int:
        """Run the application for exactly one turn under mocks."""
        # Mocks must be installed BEFORE importing main’s llmio modules.
        # If your main imports at module import time, reimport after enabling:
        self.enable()

        # If main was already imported above, reload to ensure it sees mocks/env
        import importlib
        importlib.reload(main)

        print("[CI_Runner] Launching app (one turn)…")
        try:
            rc = main.main()  # main() will read MAX_TURNS=1 and exit after one loop
            return int(rc) if rc is not None else 0
        except SystemExit as e:
            return int(e.code) if e.code is not None else 0

if __name__ == "__main__":
    runner = CI_Runner(max_turns=1)
    raise SystemExit(runner.run())
