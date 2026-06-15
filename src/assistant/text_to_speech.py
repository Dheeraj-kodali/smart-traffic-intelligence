"""Text to speech processing."""

import os
import multiprocessing


def list_available_voices() -> None:
    """Print all available text-to-speech voices and their IDs."""
    if os.getenv("SPACE_ID") is not None:
        return
        
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        print("Available Voices:")
        for voice in voices:
            print(f" - Name: {voice.name}")
            print(f"   ID: {voice.id}")
    except ImportError:
        print("pyttsx3 not installed.")
    except Exception as e:
        print(f"Speech engine unavailable. Cannot list voices. Error: {e}")


def _speak_worker(text: str) -> None:
    """Worker function to execute pyttsx3 in a separate process."""
    if os.getenv("SPACE_ID") is not None:
        return
        
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)
        
        voices = engine.getProperty("voices")
        preferred_voices = [
            "aria",
            "jenny",
            "guy",
            "zira",
            "david",
        ]
        
        selected_voice = None
        for pref in preferred_voices:
            for voice in voices:
                if pref.lower() in voice.name.lower():
                    selected_voice = voice.id
                    break
            if selected_voice:
                break
                
        if selected_voice:
            engine.setProperty("voice", selected_voice)
            
        engine.say(text)
        engine.runAndWait()
    except Exception as exc:
        print(f"TTS Error: {exc}")
        raise


def speak(text: str) -> None:
    """
    Convert text to offline speech and wait for playback to finish using a separate process.
    
    Args:
        text: The string to be spoken. Empty or whitespace-only strings are ignored.
    """
    if not text or not text.strip():
        return
        
    print(f"Speaking: {text}")
    
    process = multiprocessing.Process(
        target=_speak_worker,
        args=(text,)
    )
    process.start()
    process.join()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    list_available_voices()
    speak("Voice assistant is ready.")
