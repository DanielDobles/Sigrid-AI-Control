# Voice Module - Speech Recognition and Text-to-Speech

import pyttsx3
import speech_recognition as sr
import threading
from typing import Optional, Callable
from src.config.settings import VOICE_LANGUAGE, VOICE_RATE

class VoiceController:
    """Handles voice input (speech-to-text) and output (text-to-speech)."""
    
    def __init__(self):
        # Initialize Text-to-Speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty("rate", VOICE_RATE)
        self.tts_engine.setProperty("voice", self._get_voice_id())
        
        # Initialize Speech Recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        self.listening = False
        self._listen_thread = None
        
    def _get_voice_id(self) -> str:
        """Get the best available voice ID."""
        voices = self.tts_engine.getProperty("voices")
        # Try to find a male English voice
        for voice in voices:
            if "male" in voice.name.lower() and "english" in voice.name.lower():
                return voice.id
        # Fallback to first voice
        return voices[0].id if voices else None
    
    def speak(self, text: str, block: bool = True):
        """Speak text using TTS."""
        self.tts_engine.say(text)
        if block:
            self.tts_engine.runAndWait()
        else:
            threading.Thread(target=self.tts_engine.runAndWait).start()
    
    def listen_once(self, timeout: int = 10, phrase_time_limit: int = None) -> dict:
        """Listen for one voice command and return the recognized text."""
        try:
            with self.microphone as source:
                print("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
            print("🔄 Processing speech...")
            # Try Google Speech Recognition first (most accurate)
            try:
                text = self.recognizer.recognize_google(audio, language=VOICE_LANGUAGE)
                return {"status": "success", "text": text, "engine": "google"}
            except sr.UnknownValueError:
                return {"status": "no_recognition", "text": None}
            except sr.RequestError:
                # Fallback to Sphinx (offline)
                try:
                    text = self.recognizer.recognize_sphinx(audio, language=VOICE_LANGUAGE[:2])
                    return {"status": "success", "text": text, "engine": "sphinx"}
                except:
                    return {"status": "error", "error": "Speech recognition failed"}
        except sr.WaitTimeoutError:
            return {"status": "timeout", "text": None}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        """Start continuous voice recognition in a background thread."""
        self.listening = True
        self._listen_thread = threading.Thread(target=self._listen_loop, args=(callback,), daemon=True)
        self._listen_thread.start()
        
    def stop_continuous_listening(self):
        """Stop continuous voice recognition."""
        self.listening = False
        if self._listen_thread:
            self._listen_thread.join(timeout=5)
            
    def _listen_loop(self, callback: Callable[[str], None]):
        """Background loop for continuous listening."""
        while self.listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5)
                    
                try:
                    text = self.recognizer.recognize_google(audio, language=VOICE_LANGUAGE)
                    if text.strip():
                        callback(text)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
            except:
                pass  # Timeout, continue listening
    
    def get_available_voices(self) -> list:
        """List all available TTS voices."""
        voices = self.tts_engine.getProperty("voices")
        return [{"id": v.id, "name": v.name, "languages": v.languages} for v in voices]
    
    def set_voice_rate(self, rate: int):
        """Set the speech rate."""
        self.tts_engine.setProperty("rate", rate)
        
    def set_voice(self, voice_id: str):
        """Set the voice by ID."""
        self.tts_engine.setProperty("voice", voice_id)
