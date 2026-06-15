"""Voice Assistant Factory for Local vs Cloud Environments."""

import os

IS_CLOUD = os.getenv("SPACE_ID") is not None

def is_cloud_environment() -> bool:
    """Return True if running in Hugging Face Spaces."""
    return IS_CLOUD

def listen() -> str | None:
    """Listen for voice commands using the appropriate environment logic."""
    if IS_CLOUD:
        from src.assistant.browser_speech_to_text import listen_from_browser
        return listen_from_browser()
    else:
        import streamlit as st
        if st.button("🎤 Start Voice Assistant"):
            with st.spinner("Listening..."):
                from src.assistant.speech_to_text import listen as local_listen
                return local_listen()
        return None

def speak(text: str) -> None:
    """Generate speech using the appropriate environment logic."""
    if IS_CLOUD:
        from src.assistant.browser_text_to_speech import play_speech
        play_speech(text)
    else:
        from src.assistant.text_to_speech import speak as local_speak
        local_speak(text)
