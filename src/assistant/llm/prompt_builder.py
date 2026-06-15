"""Traffic Copilot Prompt Builder."""

from typing import Dict, Any

def build_traffic_prompt(user_question: str, context: Dict[str, Any]) -> str:
    """
    Build a comprehensive LLM prompt using dashboard context and the user's question.
    
    Args:
        user_question: The question asked by the user.
        context: A dictionary of current traffic dashboard metrics.
        
    Returns:
        The formatted prompt string for the LLM.
    """
    prompt = (
        "You are an AI traffic analyst. Answer using only the provided traffic data. "
        "If the information is unavailable, clearly say so.\n\n"
        "--- Traffic Data Context ---\n"
        f"Status: {context.get('status', 'N/A')}\n"
        f"Trend: {context.get('trend', 'N/A')}\n"
        f"Congestion Score: {context.get('congestion_score', 'N/A')}\n"
        f"Peak Time: {context.get('peak_time', 'N/A')}\n"
        f"Average Vehicles: {context.get('average_vehicles', 'N/A')}\n"
        f"Forecast Summary: {context.get('forecast_summary', 'N/A')}\n"
        f"Lowest Traffic Time: {context.get('lowest_traffic_time', 'N/A')}\n"
        f"Lowest Traffic Value: {context.get('lowest_traffic_value', 'N/A')}\n"
        f"Peak Traffic Value: {context.get('peak_traffic_value', 'N/A')}\n\n"
        "--- User Question ---\n"
        f"{user_question}"
    )
    return prompt
