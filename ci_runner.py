# ci_runner.py
import os
import sys
import types
import importlib

class CI_Runner:
    """
    CI/headless harness that:
      - Installs mock llmio modules (no audio/devices/servers)
      - Forces a single turn (MAX_TURNS=1)
      - Skips preflight by appending --no-preflight
      - Imports main only after mocks are in place
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

    def _purge_if_loaded(self, name: str):
        """Remove a module from sys.modules if it was already imported."""
        if name in sys.modules:
            del sys.modules[name]

    def enable(self):
        print("[CI_Runner] Installing mock modules…")
        # Purge real modules if they were imported already (defensive)
        for m in (
            "llmio.wake_word",
            "llmio.stt_whisper",
            "llmio.llm_remote",
            "llmio.tts_piper",
        ):
            self._purge_if_loaded(m)

        # Install mocks
        self._mock_wake()
        self._mock_stt()
        self._mock_llm()
        self._mock_tts()

        # One cycle only
        os.environ["MAX_TURNS"] = str(self.max_turns)

        # Ensure preflight skips by CLI flag (your PreflightChecks reads sys.argv)
        if "--no-preflight" not in sys.argv:
            sys.argv.append("--no-preflight")

        # Important: if main was imported earlier by something else, purge it
        self._purge_if_loaded("main")

    def run(self) -> int:
        # Install mocks & prep environment BEFORE importing main
        self.enable()

        print("[CI_Runner] Launching app (one turn)…")
        main = importlib.import_module("main")  # import only now (after mocks)

        if not hasattr(main, "main") or not callable(main.main):
            print("[CI_Runner] main.py must expose a callable `main()`.")
            return 2

        try:
            rc = main.main()  # main will read MAX_TURNS=1 and exit after one loop
            return int(rc) if rc is not None else 0
        except SystemExit as e:
            return int(e.code) if e.code is not None else 0

if __name__ == "__main__":
    runner = CI_Runner(max_turns=1)
    raise SystemExit(runner.run())
