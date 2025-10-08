# preflight.py
import sys
import time
import requests
from typing import Callable


class PreflightChecks:
    """
    Preflight checker for local services (LLM + Piper).
    Default: RUN preflight.
    Skip only if '--no-preflight' is present in sys.argv.
    """

    def __init__(
        self,
        llm_url: str = "http://127.0.0.1:8080/completion",
        piper_url: str = "http://127.0.0.1:5000",
        attempts: int = 10,
        delay_s: float = 0.5,
        timeout_s: float = 5.0,
        strict_exit: bool = True,
        enabled: bool | None = None,  # if None, computed from CLI flag
    ):
        self.llm_url = llm_url
        self.piper_url = piper_url
        self.attempts = attempts
        self.delay_s = delay_s
        self.timeout_s = timeout_s
        self.strict_exit = strict_exit

        # Always ON by default; skip only if the CLI flag is present
        if enabled is None:
            self.enabled = ("--no-preflight" not in sys.argv)
        else:
            self.enabled = enabled
            
    # -------- checks --------
    def check_llm(self) -> bool:
        try:
            r = requests.post(
                self.llm_url,
                json={"prompt": "ping", "n_predict": 8},
                timeout=self.timeout_s,
            )
            r.raise_for_status()
            j = r.json()
            if not any(k in j for k in ("content", "text")):
                print("[Preflight][LLM] Reachable but unexpected JSON (no 'content'/'text').")
            return True
        except requests.RequestException as e:
            print(f"[Preflight][LLM] Unreachable or slow: {e}")
            return False

    def check_tts(self) -> bool:
        try:
            r = requests.get(f"{self.piper_url}/voices", timeout=self.timeout_s)
            r.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"[Preflight][TTS] Unreachable or slow: {e}")
            return False

    # -------- retry wrapper --------
    def wait_for(self, fn: Callable[[], bool], desc: str) -> bool:
        for _ in range(self.attempts):
            if fn():
                print(f"[Preflight] {desc}: OK")
                return True
            time.sleep(self.delay_s)
        print(f"[Preflight] {desc}: FAILED")
        return False

    # -------- entrypoint --------
    def run(self) -> bool:
        if not self.enabled:
            print("[Preflight] Skipping checks (--no-preflight flag).")
            return True

        ok = True
        ok &= self.wait_for(self.check_llm, "LLM server reachable")
        ok &= self.wait_for(self.check_tts, "TTS server reachable")

        if ok:
            print("[Preflight] All checks passed! Starting Ares ...")
            return True

        if self.strict_exit:
            import sys
            sys.exit(1)
        return False

