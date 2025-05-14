"""
Utility functions for GPT-related functionality.
"""

from typing import Dict
from datetime import datetime
import logging
from app.utils.firebase.logging import FirebaseLogger

def get_goodwill_label(score: int) -> str:
    """
    Get a descriptive label for a goodwill score.
    
    Args:
        score: Numeric goodwill score
        
    Returns:
        str: Descriptive label for the goodwill level
    """
    if score >= 90:
        return "Legendary"
    elif score >= 75:
        return "Exalted"
    elif score >= 60:
        return "Honored"
    elif score >= 45:
        return "Friendly"
    elif score >= 30:
        return "Neutral"
    elif score >= 15:
        return "Unfriendly"
    else:
        return "Hostile"

def log_usage(prompt: str, response: str, usage: Dict[str, int], model: str = None) -> None:
    """
    Log GPT usage to Firebase and application logs.
    
    Args:
        prompt: The prompt sent to GPT
        response: The response received from GPT
        usage: Dictionary containing token usage information
        model: Optional model name used for the request
    """
    # Log to Firebase
    logger = FirebaseLogger()
    logger.log_event("gpt_usage", {
        "prompt": prompt,
        "response": response,
        "usage": usage,
        "model": model,
        "timestamp": datetime.now().isoformat()
    })
    
    # Log to application logs
    if usage:
        logging.info(
            f"[GPT USAGE] model={model or 'unknown'} | "
            f"prompt={usage.get('prompt_tokens')} | "
            f"completion={usage.get('completion_tokens')} | "
            f"total={usage.get('total_tokens')}"
        )
    else:
        logging.info(f"[GPT USAGE] model={model or 'unknown'} | no usage data provided.") 