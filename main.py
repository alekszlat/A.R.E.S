from llmio import stt_whisper
from llmio import tts_piper
from llmio import llm_remote

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