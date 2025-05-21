import logging
from typing import Any, Dict

def log_usage(model_name: str, usage: Dict[str, Any]) -> None:
    """Log usage statistics for a model call."""
    try:
        logging.info(f"Model: {model_name}, Usage: {usage}")
    except Exception as e:
        logging.error(f"Failed to log usage: {e}")

def get_goodwill_label(score: int) -> str:
    """Return a goodwill label based on the score."""
    if score >= 80:
        return "excellent"
    elif score >= 60:
        return "good"
    elif score >= 40:
        return "neutral"
    elif score >= 20:
        return "poor"
    else:
        return "hostile" 