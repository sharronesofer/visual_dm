# importance_utils.py

def score_interaction(flags: dict) -> int:
    """
    Returns an importance score (1–10) based on interaction flags.
    This feeds into GPT model routing.
    """
    if not flags:
        return 5  # Default neutral

    score = 5

    # Emotional intensity
    if flags.get("emotionally_charged"):
        score += 2

    # Conflict with high stakes
    if flags.get("conflict_type") in ["loyalty", "morality", "betrayal"]:
        score += 2

    # Scope of impact
    scope = flags.get("scope", "")
    if scope == "regional":
        score += 1
    elif scope == "global":
        score += 2

    # Force GPT-4 regardless
    if flags.get("force_gpt4"):
        return 10

    return min(score, 10)
