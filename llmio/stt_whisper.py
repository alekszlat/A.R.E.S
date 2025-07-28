import subprocess
import tempfile
import sounddevice as sd
import numpy as np
import scipy.io.wavfile
import os

WHISPER_BIN = "./server/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "./models/ggml-base.en.bin" 

def record_audio(filename="stt_temp.wav", duration=5, samplerate=16000):
    print("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    scipy.io.wavfile.write(filename, samplerate, audio)
    print("Saved recording:", filename)
    return filename

def transcribe(filename="stt_temp.wav"):
    try:
        result = subprocess.run(
            [WHISPER_BIN, "-m", WHISPER_MODEL, "-f", filename, "-nt"],  # -nt = no timestamps
            capture_output=True, text=True, timeout=90
        )
        # Extract the transcript from output (last line)
        lines = result.stdout.strip().split("\n")
        transcript = lines[-1] if lines else ""
        return transcript
    except Exception as e:
        print(f"Error running Whisper: {e}")
        return ""

if __name__ == "__main__":
    wav = record_audio()
    print("Transcription:", transcribe(wav))
    os.remove(wav)  # Clean up temp file