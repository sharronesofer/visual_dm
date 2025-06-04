from .client import GPTClient
from .flavor import gpt_flavor_identify_effect, gpt_flavor_reveal_full_item, get_goodwill_label
from .dialogue import DialogueGPTClient

# Simple log_usage function to avoid circular import
def log_usage(operation: str, tokens: int = 0, **kwargs):
    """Log GPT usage for tracking purposes."""
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"GPT usage: {operation}, tokens: {tokens}, extras: {kwargs}")

# Import IntentAnalyzer only if it exists to avoid errors
try:
    from backend.infrastructure.events.intents import IntentAnalyzer
except ImportError:
    IntentAnalyzer = None

__all__ = [
    'GPTClient',
    'gpt_flavor_identify_effect',
    'gpt_flavor_reveal_full_item',
    'get_goodwill_label',
    'log_usage',
    'DialogueGPTClient'
]

if IntentAnalyzer:
    __all__.append('IntentAnalyzer') 