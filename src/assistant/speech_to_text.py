"""Speech to text processing."""

import os

def listen(timeout: int = 5, phrase_time_limit: int = 10) -> str:
    """
    Capture speech from microphone and convert it to text.
    
    Args:
        timeout: How many seconds to wait for speech to start before giving up.
        phrase_time_limit: Maximum number of seconds the microphone will listen before finishing the phrase.
        
    Returns:
        The recognized text in lowercase or a user-friendly error message.
    """
    # Disable local microphone features in cloud environments completely
    if os.getenv("SPACE_ID") is not None:
        return "Microphone is unavailable in this environment. Please use text input."

    try:
        import speech_recognition as sr
    except ImportError:
        return "Speech recognition module is not installed."
        
    recognizer = sr.Recognizer()
    
    try:
        # Environment check for microphone access
        try:
            mics = sr.Microphone.list_microphone_names()
            if not mics:
                return "Microphone is unavailable in this environment."
        except OSError:
            return "Microphone is unavailable in this environment."
            
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
        text = recognizer.recognize_google(audio)
        return text.lower()
        
    except sr.WaitTimeoutError:
        return "No speech detected."
    except sr.UnknownValueError:
        return "I could not understand the audio."
    except sr.RequestError:
        return "Speech service is unavailable."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    print("Listening...")
    print(listen())
