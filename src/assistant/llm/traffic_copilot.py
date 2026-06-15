"""Traffic Copilot LLM Service."""

from typing import Dict, Any
from .prompt_builder import build_traffic_prompt

class TrafficCopilot:
    """Reusable AI assistant module to answer traffic questions."""
    
    def answer(self, user_question: str, context: Dict[str, Any]) -> str:
        """
        Answer a user's question based on the provided dashboard context.
        
        Currently acts as a placeholder by returning the generated prompt.
        
        Args:
            user_question: The question asked by the user.
            context: A dictionary of current traffic dashboard metrics.
            
        Returns:
            The generated prompt as a placeholder response.
        """
        return build_traffic_prompt(user_question, context)
