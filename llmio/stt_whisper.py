"""
Simple mic → VAD-record → Whisper.cpp transcription.

Dependencies:
  pip install sounddevice numpy scipy webrtcvad
  # plus your whisper.cpp binary + model on disk

Whisper.cpp flags used:
  -m <model>     path to GGML model (e.g., ggml-base.en.bin)
  -f <wav>       path to input WAV file (16 kHz, mono, int16)
  -nt            no timestamps in output (just text)
"""

import os
import subprocess
import tempfile
from typing import List

import numpy as np
import sounddevice as sd
import scipy.io.wavfile
import webrtcvad

# --- Configure these paths for your machine ---
WHISPER_BIN = "./server/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "./models/ggml-base.en.bin"

# --- Small helper: beep so the user knows recording started ---
def play_beep(frequency: int = 1000, duration: float = 0.15, samplerate: int = 16000, volume: float = 0.3) -> None:
    """Play a short sine beep (default: 1kHz, 150ms)."""
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False, dtype=np.float32)
    tone = np.sin(2 * np.pi * frequency * t) * volume
    sd.play(tone, samplerate)
    sd.wait()  # block until finished


def record_audio(
    dir_path: str = "/tmp",
    prefix: str = "vad_",
    max_seconds: int = 15,
    silence_seconds: float = 0.6,
    aggressiveness: int = 2,
    samplerate: int = 16000,
) -> str:
    """
    Record from mic until the user goes quiet for `silence_seconds`.
    Returns the path to the saved WAV file.
    - Uses WebRTC VAD (aggressiveness 0..3; higher = more strict).
    - Streams raw 30 ms frames (optimal for VAD) from sounddevice.
    """
    # ---- Set up VAD and frame math ----
    vad = webrtcvad.Vad(aggressiveness)     # speech detector
    frame_ms = 30                           # valid choices: 10, 20, 30 ms
    channels = 1
    frame_samps = int(samplerate * frame_ms / 1000)  # samples in one frame
    silence_target_ms = int(silence_seconds * 1000)  # how long of silence to stop
    max_ms = max_seconds * 1000

    def is_speech(frame_bytes: bytes) -> bool:
        """webrtcvad expects mono, 16kHz, 16-bit little-endian PCM bytes."""
        return vad.is_speech(frame_bytes, sample_rate=samplerate)

    # ---- Tell the user we’re listening ----
    play_beep()
    print("🎙️  listening… speak, then pause to stop")

    # We collect raw 30 ms frames as bytes, then write a single WAV at the end
    collected: List[bytes] = []
    silent_ms = 0

    # Open microphone as RAW (bytes) stream in the exact format VAD expects
    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=frame_samps,   # frames per read → one 30 ms chunk
        dtype="int16",
        channels=channels,
    ) as stream:
        while True:
            data, overflowed = stream.read(frame_samps)
            if overflowed:
                # Not fatal; you could log if you want tighter diagnostics
                pass

            frame = bytes(data)      # contiguous bytes for VAD + file
            collected.append(frame)

            # Update silence counter
            if is_speech(frame):
                silent_ms = 0
            else:
                silent_ms += frame_ms

            # Stop if we've seen enough consecutive silence
            if silent_ms >= silence_target_ms:
                print("🛑 silence detected — stopping")
                break

            # Hard timeout (safety net)
            if len(collected) * frame_ms >= max_ms:
                print("⏱️ max_seconds reached — stopping")
                break

    # ---- Save one WAV with all frames ----
    os.makedirs(dir_path, exist_ok=True)
    pcm_bytes = b"".join(collected)
    audio = np.frombuffer(pcm_bytes, dtype=np.int16)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=dir_path, prefix=prefix) as f:
        scipy.io.wavfile.write(f.name, samplerate, audio)
        print(f"💾 Saved recording: {f.name}")
        return f.name


def transcribe(wav_path: str) -> str:
    """
    Call whisper.cpp CLI on the given WAV and return the transcript string.
    - Requires WHISPER_BIN and WHISPER_MODEL to exist.
    - Uses `-nt` to omit timestamps (just text).
    """
    # Basic safety checks so failures are obvious:
    if not os.path.isfile(WHISPER_BIN):
        print(f"[Whisper] Binary not found: {WHISPER_BIN}")
        return ""
    if not os.path.isfile(WHISPER_MODEL):
        print(f"[Whisper] Model not found: {WHISPER_MODEL}")
        return ""
    if not os.path.isfile(wav_path):
        print(f"[Whisper] WAV not found: {wav_path}")
        return ""

    try:
        result = subprocess.run(
            [WHISPER_BIN, "-m", WHISPER_MODEL, "-f", wav_path, "-nt"],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if result.returncode != 0:
            # whisper.cpp prints timings to stderr; errors too
            print(f"[Whisper] Failed (code {result.returncode}): {result.stderr.strip()}")
            return ""

        # Typically final line of stdout is the transcribed text
        lines = result.stdout.strip().splitlines()
        return lines[-1] if lines else ""

    except subprocess.TimeoutExpired:
        print("[Whisper] Timed out after 90s")
        return ""
    except Exception as e:
        print(f"[Whisper] Error: {e}")
        return ""


# --- Manual test (run this file directly) ---
if __name__ == "__main__":
    wav = record_audio()
    text = transcribe(wav)
    print("📝 Transcription:", text or "(empty)")
