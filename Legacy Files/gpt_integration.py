import openai
import json
import logging
from datetime import datetime
from firebase_admin import db

# === GPT Model Routing and Usage Logging ===

def gpt_router(score=5, flags=None):
    """
    Routes to the appropriate GPT model based on importance score and flags.

    Args:
        score (int): Importance score from 1–10
        flags (dict): Optional flags like {'emotional': True, 'plot': True}

    Returns:
        str: GPT model name (e.g. 'gpt-4o', 'gpt-3.5-turbo')
    """
    flags = flags or {}

    # Override logic
    if flags.get("plot") or flags.get("secret") or flags.get("emotional"):
        return "gpt-4"

    if flags.get("force_gpt4"):
        return "gpt-4"

    # Score-based routing
    if score <= 3:
        return "gpt-4o-mini"
    elif 4 <= score <= 7:
        return "gpt-4o"
    else:
        return "gpt-4"


def log_gpt_usage(model, usage):
    """
    Log GPT API usage data to Firebase for monitoring purposes.
    """
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_ref = db.reference(f'/gpt_usage/{model}/{timestamp}')
        log_ref.set(usage)
    except Exception as e:
        logging.error("Error logging GPT usage: %s", str(e))


def call_gpt_model(model, messages, temperature=0.7, max_tokens=150):
    """
    Make a call to the GPT API using the provided model and messages.
    Returns either a parsed JSON (if possible) or the raw text response.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        usage = response.get("usage", {})
        log_gpt_usage(model, usage)
        message_content = response.choices[0].message.content.strip()
        try:
            return json.loads(message_content)
        except Exception:
            return message_content
    except Exception as e:
        logging.error(f"Error calling GPT model {model}: {str(e)}")
        return None


# === High-Level DM and NPC Prompts ===

def get_dm_response(context, prompt, importance_score=5, flags=None, temperature=0.7, max_tokens=150):
    model = gpt_router(score=importance_score, flags=flags)
    messages = [
        {"role": "system", "content": "You are a Dungeon Master managing a persistent fantasy world."},
        {"role": "user", "content": f"Context: {context}\nPrompt: {prompt}"}
    ]
    return call_gpt_model(model, messages, temperature, max_tokens)


def get_npc_response(npc_context, conversation_history, prompt, importance_score=5, flags=None, temperature=0.7, max_tokens=150):
    model = gpt_router(score=importance_score, flags=flags)
    messages = [
        {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
        {"role": "user", "content": f"NPC Context: {npc_context}\nConversation History: {conversation_history}\nPrompt: {prompt}"}
    ]
    return call_gpt_model(model, messages, temperature, max_tokens)


# === Interaction Scoring for Routing ===

def score_interaction(flags: dict) -> int:
    """
    Returns an importance score (1–10) based on interaction flags.
    This feeds into GPT model routing.
    """
    if not flags:
        return 5

    score = 5

    if flags.get("emotionally_charged"):
        score += 2

    if flags.get("conflict_type") in ["loyalty", "morality", "betrayal"]:
        score += 2

    scope = flags.get("scope", "")
    if scope == "regional":
        score += 1
    elif scope == "global":
        score += 2

    if flags.get("force_gpt4"):
        return 10

    return min(score, 10)
