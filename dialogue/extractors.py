import re
from typing import List, Dict, Any

def extract_key_info(message: str) -> List[Dict[str, Any]]:
    """
    Extract key information from a message using regex and rule-based patterns.
    Returns a list of extracted entities/facts/decisions.
    """
    results = []
    # Example: extract quest names
    quest_match = re.search(r'quest\s*[:=]?\s*([\w\s]+)', message, re.IGNORECASE)
    if quest_match:
        results.append({'type': 'quest', 'value': quest_match.group(1).strip()})
    # Example: extract rewards
    reward_match = re.search(r'reward\s*[:=]?\s*([\w\s]+)', message, re.IGNORECASE)
    if reward_match:
        results.append({'type': 'reward', 'value': reward_match.group(1).strip()})
    # Example: extract decisions (yes/no)
    if re.search(r'\byes\b', message, re.IGNORECASE):
        results.append({'type': 'decision', 'value': 'yes'})
    if re.search(r'\bno\b', message, re.IGNORECASE):
        results.append({'type': 'decision', 'value': 'no'})
    # Add more patterns as needed
    return results 