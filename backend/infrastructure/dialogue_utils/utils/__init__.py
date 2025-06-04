"""Utils for dialogue system"""

from backend.infrastructure.utils.text_utils import (
    count_tokens,
    clean_text,
    truncate_text,
    calculate_similarity,
    format_dialogue_text
)

# Import from our new text processing infrastructure
from backend.infrastructure.text_processing import (
    extract_key_info,
    extract_entities,
    extract_dialogue_metadata,
    extract_conversation_turns
)

__all__ = [
    'count_tokens',
    'extract_key_info',
    'clean_text',
    'truncate_text',
    'extract_entities',
    'calculate_similarity',
    'format_dialogue_text',
    'extract_dialogue_metadata',
    'extract_conversation_turns'
]

