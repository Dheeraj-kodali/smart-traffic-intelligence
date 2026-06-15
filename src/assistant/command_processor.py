"""Command processor."""

import string
from typing import Dict, Any, List

STATUS_KEYWORDS = ["traffic", "status", "busy", "road condition", "update"]
TREND_KEYWORDS = ["trend", "increasing", "decreasing", "improving", "worsening"]
CONGESTION_KEYWORDS = ["congestion", "score", "jam", "traffic level"]
FORECAST_KEYWORDS = ["forecast", "future", "expected", "prediction", "will traffic", "next"]
PEAK_TIME_KEYWORDS = ["peak", "rush hour", "busiest", "highest traffic"]
LOW_TRAFFIC_TIME_KEYWORDS = [
    "when traffic low",
    "traffic will be low",
    "best time to travel",
    "least traffic",
    "when congestion reduce",
    "traffic improve",
    "when road free",
    "when is traffic lowest"
]
AVERAGE_VEHICLES_KEYWORDS = ["average", "vehicles", "vehicle count", "cars"]


def contains_keyword(command: str, keywords: List[str]) -> bool:
    """Check if the normalized command contains any of the keywords."""
    return any(keyword in command for keyword in keywords)


def process_command(command: str, dashboard_data: Dict[str, Any]) -> str:
    """
    Process a voice command and return the appropriate response based on dashboard data.
    
    Args:
        command: The spoken command string.
        dashboard_data: A dictionary containing current traffic dashboard metrics.
        
    Returns:
        A formatted string response suitable for text-to-speech playback.
    """
    # 1. Normalize command: lowercase
    cmd = command.lower()
    
    # 2. Remove punctuation
    cmd = cmd.translate(str.maketrans('', '', string.punctuation))
    
    # 3. Trim extra spaces
    cmd = " ".join(cmd.split())
    
    # Match intents using keyword overlap. 
    # Priority matters since 'traffic' is a generic word in STATUS_KEYWORDS.
    if contains_keyword(cmd, FORECAST_KEYWORDS):
        if "forecast_summary" not in dashboard_data:
            return "Requested traffic information is not available yet."
        return str(dashboard_data["forecast_summary"])
        
    elif contains_keyword(cmd, TREND_KEYWORDS):
        if "trend" not in dashboard_data or "congestion_score" not in dashboard_data:
            return "Requested traffic information is not available yet."
        return f"Traffic trend is {dashboard_data['trend']} with a congestion score of {dashboard_data['congestion_score']} percent."
        
    elif contains_keyword(cmd, LOW_TRAFFIC_TIME_KEYWORDS):
        if "lowest_traffic_time" not in dashboard_data or "lowest_traffic_value" not in dashboard_data:
            return "Requested traffic information is not available yet."
        return f"Traffic is expected to be lowest at {dashboard_data['lowest_traffic_time']}, with approximately {dashboard_data['lowest_traffic_value']:.1f} vehicles."
        
    elif contains_keyword(cmd, PEAK_TIME_KEYWORDS):
        if "peak_traffic_time" not in dashboard_data or "peak_traffic_value" not in dashboard_data:
            return "Requested traffic information is not available yet."
        return f"Traffic is expected to peak at {dashboard_data['peak_traffic_time']}, reaching approximately {dashboard_data['peak_traffic_value']:.1f} vehicles."
        
    elif contains_keyword(cmd, AVERAGE_VEHICLES_KEYWORDS):
        if "average_vehicles" not in dashboard_data:
            return "Requested traffic information is not available yet."
        return f"Average vehicles per frame is {dashboard_data['average_vehicles']}."
        
    elif contains_keyword(cmd, CONGESTION_KEYWORDS):
        if "congestion_score" not in dashboard_data:
            return "Requested traffic information is not available yet."
        return f"Current congestion score is {dashboard_data['congestion_score']} percent."
        
    elif contains_keyword(cmd, STATUS_KEYWORDS):
        if "status" not in dashboard_data or "congestion_score" not in dashboard_data:
            return "Requested traffic information is not available yet."
        return f"Current traffic status is {dashboard_data['status']} and congestion score is {dashboard_data['congestion_score']} percent."
        
    return "Sorry, I did not understand that command."


if __name__ == "__main__":
    sample_data = {
        "status": "Medium",
        "congestion_score": 46.2,
        "trend": "Decreasing",
        "peak_time": "10:11:11",
        "average_vehicles": 8.3,
        "forecast_summary": "Traffic is expected to decrease over the next 30 minutes.",
        "lowest_traffic_time": "03:45 PM",
        "lowest_traffic_value": 4.5,
        "peak_traffic_time": "04:15 PM",
        "peak_traffic_value": 12.3
    }

    test_phrases = [
        # Forecast
        "When will traffic be low?",
        "What does the forecast say?",
        "How many vehicles are expected?",
        "When will congestion reduce?",
        # Trend
        "Is congestion improving?",
        "Is traffic expected to improve?",
        "Is the traffic increasing?",
        # Status
        "Give me the latest traffic update.",
        "How is traffic right now?",
        "Tell me the current traffic.",
        # Peak
        "When is peak traffic?",
        # Congestion
        "What's the congestion level?",
        "How busy is the road?",
        # Unrecognized
        "What is the weather like?",
        "Tell me a joke."
    ]

    print("--- Running Batch Tests ---")
    for phrase in test_phrases:
        response = process_command(phrase, sample_data)
        print(f"User: \"{phrase}\"")
        print(f"Assistant: {response}\n")

    print("--- Interactive Mode ---")
    while True:
        try:
            user_input = input("Command: ")
            print(process_command(user_input, sample_data))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break
