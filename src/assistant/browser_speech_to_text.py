"""Browser-based Speech to Text."""

import os
import tempfile
import speech_recognition as sr
import streamlit as st
from streamlit_mic_recorder import mic_recorder


def listen_from_browser() -> str | None:
    """
    Display a browser microphone widget to capture audio and transcribe it.
    
    Returns:
        The recognized text in lowercase, a user-friendly error message, or None if no recording exists yet.
    """
    audio = mic_recorder(
        start_prompt="🎤 Start Voice Assistant",
        stop_prompt="🛑 Stop Recording",
        just_once=True,
        key='browser_mic_recorder',
        format='wav'
    )
    
    if audio is None or "bytes" not in audio:
        return None
        
    recognizer = sr.Recognizer()
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio["bytes"])
            temp_file_path = temp_audio_file.name
            
        try:
            with sr.AudioFile(temp_file_path) as source:
                audio_data = recognizer.record(source)
                
            text = recognizer.recognize_google(audio_data)
            return text.lower()
            
        except sr.UnknownValueError:
            return "I could not understand the audio."
        except sr.RequestError:
            return "Speech service is unavailable."
        except ValueError:
            return "I could not understand the audio."
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        return f"An error occurred: {str(e)}"



