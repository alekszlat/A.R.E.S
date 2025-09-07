from llmio import stt_whisper
from llmio import tts_piper
from llmio import llm_remote
from llmio import wake_word

import os
import sys
from preflight import PreflightChecks

#------ Configuration and Preflight Checks ------
#Command-line flags
MOCK_MODE = os.getenv("MOCK_MODE", "0") == "1" or "--mock" in sys.argv
MAX_TURNS = int(os.getenv("MAX_TURNS", "1"))

#------ Main Application Logic ------
def main():

    # run checks unless explicitly disabled via --no-preflight
    PreflightChecks().run()

    turns = 0
    while True:

        listener = wake_word.WakeWord_Listener()
        print("Listening for wake word...")
        if listener.listen():

            print("🎤 Please speak after the beep ...")
            audio_file = stt_whisper.record_audio(max_seconds=15)
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

        turns += 1
        if turns >= MAX_TURNS:
            print(f"Reached MAX_TURNS={MAX_TURNS}, exiting.")
            return 0
    
if __name__ == "__main__":
    main()