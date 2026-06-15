"""Streamlit Voice Assistant integration."""

import streamlit as st
from typing import Dict, Any, Tuple

from src.assistant.voice_factory import listen, speak
from .command_processor import process_command


def get_dashboard_context() -> Dict[str, Any]:
    """Collect live dashboard data from Streamlit session state."""
    video_result = st.session_state.get("video_analysis_result")
    forecast_result = st.session_state.get("forecast_result")
    
    context = {
        "status": "N/A",
        "trend": "N/A",
        "congestion_score": "N/A",
        "peak_time": "N/A",
        "average_vehicles": "N/A",
        "forecast_summary": "N/A",
        "lowest_traffic_time": "N/A",
        "lowest_traffic_value": 0.0,
        "peak_traffic_time": "N/A",
        "peak_traffic_value": 0.0
    }
    
    if video_result is not None:
        df = video_result.dataframe
        current_vehicles = int(df["vehicle_count"].iloc[-1]) if not df.empty else 0
        all_counts = df["vehicle_count"].tolist() if not df.empty else [0]
        
        from src.intelligence.application.use_cases.calculate_congestion import CalculateCongestionUseCase
        intelligence_uc = CalculateCongestionUseCase()
        intel_result = intelligence_uc.execute(current_vehicles, all_counts)
        context["status"] = intel_result.classification.upper()
        
        peak_veh = video_result.maximum_vehicles_in_frame
        congestion_score = (current_vehicles / peak_veh * 100) if peak_veh > 0 else 0.0
        context["congestion_score"] = round(congestion_score, 1)
        
        if len(df) > 1:
            import numpy as np
            x = np.arange(len(df))
            y = df["vehicle_count"].values
            z = np.polyfit(x, y, 1)
            slope = z[0]
            if slope > 0.05:
                context["trend"] = "Increasing"
            elif slope < -0.05:
                context["trend"] = "Decreasing"
            else:
                context["trend"] = "Stable"
        else:
            context["trend"] = "Stable"
            
        peak_row = df.loc[df["vehicle_count"].idxmax()] if not df.empty else None
        if peak_row is not None and "timestamp" in peak_row and peak_row["timestamp"] is not None:
            try:
                import pandas as pd
                if isinstance(peak_row["timestamp"], pd.Timestamp):
                    context["peak_time"] = peak_row["timestamp"].strftime("%H:%M:%S")
                else:
                    context["peak_time"] = pd.to_datetime(peak_row["timestamp"]).strftime("%H:%M:%S")
            except Exception:
                context["peak_time"] = str(peak_row["timestamp"])
                
        context["average_vehicles"] = round(video_result.average_vehicles_per_frame, 1)
        
    if forecast_result is not None:
        context["forecast_summary"] = f"Expected peak traffic is {forecast_result.peak_prediction:.1f} vehicles. Average prediction is {forecast_result.average_prediction:.1f} vehicles."
        if hasattr(forecast_result, "lowest_traffic_time"):
            context["lowest_traffic_time"] = forecast_result.lowest_traffic_time
            context["lowest_traffic_value"] = forecast_result.lowest_traffic_value
            context["peak_traffic_time"] = forecast_result.peak_traffic_time
            context["peak_traffic_value"] = forecast_result.peak_traffic_value
        
    return context


def run_dashboard_voice_assistant() -> Tuple[str | None, str | None]:
    """Run the voice assistant using the dashboard context."""
    dashboard_data = get_dashboard_context()
    
    command = listen()
    
    if command is None:
        return None, None
        
    error_messages = [
        "no speech detected.",
        "speech service is unavailable.",
        "i could not understand the audio."
    ]
    
    cmd_lower = command.lower()
    
    if cmd_lower in error_messages or cmd_lower.startswith("an error occurred"):
        formatted_error = command.capitalize()
        try:
            speak(formatted_error)
        except Exception as error:
            st.error(f"Voice playback failed: {error}")
        return formatted_error, formatted_error
        
    response = process_command(command, dashboard_data)
    
    try:
        speak(response)
    except Exception as error:
        st.error(f"Voice playback failed: {error}")
        
    return command, response
