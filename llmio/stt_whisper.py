import subprocess      # To run external programs (like the Whisper CLI)
import tempfile        # For temporary file handling
import sounddevice as sd    # To record audio from your microphone
import numpy as np          # For numerical arrays (used by sounddevice)
import scipy.io.wavfile     # For saving WAV audio files
import os                  # For file operations like deleting files
import webrtcvad           # For voice activity detection

WHISPER_BIN = "./server/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "./models/ggml-base.en.bin" 

def play_beep(frequency=1000, duration=0.5, samplerate=16000, volume=0.3):
    """Play a short beep sound."""
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    tone = np.sin(2 * np.pi * frequency * t) * volume  #volume (range -1 to 1)
    sd.play(tone, samplerate)
    sd.wait()  # Wait until sound has finished playing

def record_audio(
    dir_path="/tmp",
    prefix="vad_",
    max_seconds=15,
    silence_seconds=0.6,
    aggressiveness=2,
    samplerate=16000,
):
    """
    Record from mic and stop after `silence_seconds` of no speech (VAD).
    Returns the path to the saved WAV file (exactly `out_wav`).
    """

    # --- VAD setup ---
    vad = webrtcvad.Vad(aggressiveness)  # 0..3 (higher = more strict)
    frame_ms = 30                         # valid: 10/20/30 ms
    channels = 1
    bytes_per_sample = 2                  # int16
    frame_samps = int(samplerate * (frame_ms / 1000.0))   # samples per frame

    def is_speech(frame_bytes_buf: bytes) -> bool:
        # webrtcvad expects: mono, 16 kHz, 16-bit PCM, little-endian
        return vad.is_speech(frame_bytes_buf, sample_rate=samplerate)
    
    play_beep()  # Play a beep before recording
    print("🎙️  listening... speak, then pause to stop")
    collected: list[bytes] = []
    silent_ms = 0
    max_ms = int(max_seconds * 1000)
    target_silence_ms = int(silence_seconds * 1000)

    # Open mic as RAW stream so we get bytes directly (int16)
    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=frame_samps,   # samples per read
        dtype="int16",
        channels=channels,
    ) as stream:
        while True:
            # Read one 30 ms frame
            indata, _ = stream.read(frame_samps)
            buf = bytes(indata)          # contiguous bytes for VAD
            collected.append(buf)

            if is_speech(buf):
                silent_ms = 0
            else:
                silent_ms += frame_ms

            # Stop on enough consecutive silence
            if silent_ms >= target_silence_ms:
                print("🛑 silence detected — stopping")
                break

            # Hard timeout
            if len(collected) * frame_ms >= max_ms:
                print("⏱️ max_seconds reached — stopping")
                break


    pcm_bytes = b"".join(collected)
    audio = np.frombuffer(pcm_bytes, dtype=np.int16)

    os.makedirs(dir_path, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".wav", dir=dir_path, prefix=prefix
    ) as temp_file:
        scipy.io.wavfile.write(temp_file.name, samplerate, audio)
        print(f"Saved recording: {temp_file.name}")
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