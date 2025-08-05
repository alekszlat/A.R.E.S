import subprocess      # To run external programs (like the Whisper CLI)
import tempfile        # For temporary file handling
import sounddevice as sd    # To record audio from your microphone
import numpy as np          # For numerical arrays (used by sounddevice)
import scipy.io.wavfile     # For saving WAV audio files
import os                  # For file operations like deleting files

WHISPER_BIN = "./server/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "./models/ggml-base.en.bin" 

def record_audio(filename="stt_temp.wav", duration=5, samplerate=16000):
    print("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        scipy.io.wavfile.write(temp_file.name, samplerate, audio)
        print("Saved recording:", temp_file.name)
        return temp_file.name

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