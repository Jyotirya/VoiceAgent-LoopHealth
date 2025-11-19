import os
import speech_recognition as sr
from gtts import gTTS 
from dotenv import load_dotenv
import pydub

load_dotenv()

def transcribe_audio(file_path):
    """
    STT: Uses Google Speech Recognition (Free)
    """
    recognizer = sr.Recognizer()
    wav_path = file_path.replace(os.path.splitext(file_path)[1], ".wav")
    
    try:
        if not os.path.exists(file_path):
            return None

        # Convert WebM to WAV
        audio = pydub.AudioSegment.from_file(file_path)
        audio.export(wav_path, format="wav")
        
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            # recognize_google is free
            text = recognizer.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"❌ STT Error: {e}")
        return None
    finally:
        if os.path.exists(wav_path): os.remove(wav_path)

def text_to_speech(text, output_file_path):
    try:
        print("📢 Generating Voice (Google Free Tier)...")
        
        # Generate audio
        # lang='en' = English
        # tld='co.in' = Indian English accent (optional, use 'com' for US)
        tts = gTTS(text=text, lang='en', tld='co.in', slow=False)
        
        # Save directly to the file path
        tts.save(output_file_path)
        
        return output_file_path
        
    except Exception as e:
        print(f"❌ Google TTS Error: {e}")
        return None