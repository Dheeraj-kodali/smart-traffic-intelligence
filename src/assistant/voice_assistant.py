"""Main Voice Assistant orchestrator."""

from typing import Dict, Any, Tuple

from .speech_to_text import listen
from .text_to_speech import speak
from .command_processor import process_command


def run_voice_assistant(dashboard_data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Orchestrate the voice assistant workflow: listen, process, and speak.
    
    Args:
        dashboard_data: A dictionary containing current traffic dashboard metrics.
        
    Returns:
        A tuple containing (recognized_command, assistant_response).
    """
    command = listen()
    
    # Handle speech-to-text failures gracefully
    error_messages = [
        "no speech detected.",
        "speech service is unavailable.",
        "i could not understand the audio."
    ]
    
    # Since listen() returns lowercase text, we lower the error conditions
    # Note: exception messages might be capitalized depending on implementation,
    # but the current listen() specifically returns lowercase strings unless it's a raw exception string.
    # To be perfectly safe, we check against the lowercase version of the command.
    cmd_lower = command.lower()
    
    if cmd_lower in error_messages or cmd_lower.startswith("an error occurred"):
        # Capitalize for text-to-speech presentation
        formatted_error = command.capitalize()
        speak(formatted_error)
        return formatted_error, formatted_error
        
    response = process_command(command, dashboard_data)
    speak(response)
    
    return command, response


if __name__ == "__main__":
    sample_dashboard = {
        "status": "Medium",
        "congestion_score": 46.2,
        "trend": "Decreasing",
        "peak_time": "10:11:11",
        "average_vehicles": 8.3,
        "forecast_summary": "Traffic is expected to decrease over the next 30 minutes."
    }

    command_output, response_output = run_voice_assistant(sample_dashboard)

    print("You said:", command_output)
    print("Assistant:", response_output)
