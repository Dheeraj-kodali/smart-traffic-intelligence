"""Browser-compatible Text to Speech."""

from io import BytesIO
import streamlit as st


def generate_speech(text: str) -> bytes:
    """
    Generate speech audio from text using gTTS.
    
    Args:
        text (str): The text to be converted to speech.
        
    Returns:
        bytes: MP3 audio data representing the speech, or empty bytes if generation fails.
    """
    if not text.strip():
        return b""
        
    try:
        from gtts import gTTS
        buffer = BytesIO()
        tts = gTTS(text=text, lang="en")
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except ImportError:
        st.warning("Browser text-to-speech is unavailable.")
        return b""
    except Exception:
        return b""


def play_speech(text: str) -> None:
    """
    Generate speech and render it in the Streamlit UI.
    
    Args:
        text (str): The text to be spoken.
    """
    audio_bytes = generate_speech(text)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    else:
        st.error("Failed to generate speech audio.")



