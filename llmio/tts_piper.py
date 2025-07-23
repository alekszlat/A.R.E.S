import requests
import subprocess
import tempfile
import os

PIPER_URL = "http://localhost:5000"  # Change if you used a different port

def speak(text, voice=None):
    """
    Send text to Piper HTTP server, save audio to temp file, and play it.
    """
    payload = {"text": text}
    if voice:
        payload["voice"] = voice

    try:
        # Send POST request to Piper server
        response = requests.post(PIPER_URL, json=payload, timeout=60)
        response.raise_for_status()

        # Save to temp WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        # Play the WAV file (Linux: use aplay; Windows: use another player)
        subprocess.run(["aplay", tmp_path])

    except Exception as e:
        print(f"[Piper TTS Error] {e}")

    finally:
        # Clean up the temp file
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    speak("Hello! This is your local AI speaking using Piper.")
