from datetime import datetime
from typing import Callable, List, Dict, Any

# Example configuration for scoring weights
SCORING_WEIGHTS = {
    'recency': 0.5,
    'speaker_importance': 0.3,
    'keyword_match': 0.2
}

# Example list of important speakers and keywords
IMPORTANT_SPEAKERS = {'user', 'npc_important'}
KEYWORDS = {'quest', 'danger', 'reward', 'secret'}


def relevance_score(entry, now: datetime = None, weights: Dict[str, float] = None) -> float:
    """
    Compute a relevance score for a ConversationEntry.
    - Recency: newer messages score higher
    - Speaker importance: certain speakers are prioritized
    - Keyword match: messages containing important keywords score higher
    """
    if weights is None:
        weights = SCORING_WEIGHTS
    if now is None:
        now = datetime.utcnow()

    # Recency: exponential decay based on age (in seconds)
    age_seconds = (now - entry.timestamp).total_seconds()
    recency_score = 1.0 / (1.0 + age_seconds / 3600.0)  # 1 for now, decays over hours

    # Speaker importance
    speaker_score = 1.0 if entry.speaker in IMPORTANT_SPEAKERS else 0.0

    # Keyword match
    keyword_score = 0.0
    for kw in KEYWORDS:
        if kw in entry.message.lower():
            keyword_score = 1.0
            break

    # Weighted sum
    score = (
        weights['recency'] * recency_score +
        weights['speaker_importance'] * speaker_score +
        weights['keyword_match'] * keyword_score
    )
    return score 