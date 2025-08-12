from llmio import stt_whisper
from llmio import tts_piper
from llmio import llm_remote

import os
import sys
import time
import requests

# Env or defaults
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://127.0.0.1:8080/completion")
PIPER_URL    = os.getenv("PIPER_URL",    "http://127.0.0.1:5000")

def check_llm(endpoint: str, timeout_s: float = 5.0) -> bool:
    """Send a tiny prompt to the LLM server and expect HTTP 200 quickly."""
    try:
        r = requests.post(
            endpoint,
            json={"prompt": "ping", "n_predict": 8},
            timeout=timeout_s,
        )
        r.raise_for_status()
        # Optional sanity: make sure response JSON looks right
        j = r.json()
        if not any(k in j for k in ("content", "text")):
            print("[Preflight][LLM] Reachable but unexpected JSON (no 'content'/'text').")
        return True
    except requests.RequestException as e:
        print(f"[Preflight][LLM] Unreachable or slow: {e}")
        return False

def check_tts(base_url: str, timeout_s: float = 5.0) -> bool:
    """Ask Piper for /voices and expect HTTP 200 quickly."""
    try:
        r = requests.get(f"{base_url}/voices", timeout=timeout_s)
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[Preflight][TTS] Unreachable or slow: {e}")
        return False

def wait_for(predicate, desc: str, attempts: int = 10, delay_s: float = 0.5) -> bool:
    """Retry helper: try up to N times before giving up."""
    for _ in range(attempts):
        if predicate():
            print(f"[Preflight] {desc}: OK")
            return True
        time.sleep(delay_s)
    print(f"[Preflight] {desc}: FAILED")
    return False

# ---- Run preflight before starting your main loop ----
if not wait_for(lambda: check_llm(LLM_ENDPOINT, timeout_s=5), "LLM server ready"):
    sys.exit(1)

if not wait_for(lambda: check_tts(PIPER_URL, timeout_s=3), "TTS server ready"):
    sys.exit(1)

print("[Preflight] All services healthy. Starting Jarvis…")


def main():
    print("Starting Jarvis AI...")
    print("🎤 Please speak after the beep (recording for 5 seconds)...")
    audio_file = stt_whisper.record_audio(duration=5)
    promt = stt_whisper.transcribe(audio_file)
    print(f"Transcribed text: {promt}")
    
    if promt.strip():
        print("💡 Sending prompt to LLM...")
        response = llm_remote.complete(promt)
        print(f"LLM Response: {response}")
        
        print("🔊 Speaking the response...")
        tts_piper.speak(response)
    else:
        print("No valid prompt detected. Please try again.")
    
if __name__ == "__main__":
    main()