from llmio import stt_whisper
from llmio import tts_piper
from llmio import llm_remote
from llmio import wake_word

from preflight import PreflightChecks

#------ Main Application Logic ------
def main():

    # run checks unless explicitly disabled via --no-preflight
    PreflightChecks().run()

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
    
if __name__ == "__main__":
    main()