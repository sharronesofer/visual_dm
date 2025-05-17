"""
Social interaction and relationship utility functions.
"""

from typing import Dict, List, Optional, Union, Any
import random
from app.rules.calculation_utils import calculate_save_dc
from app.core.database import db
from app.core.utils.error_utils import ValidationError, NotFoundError
from app.social.models.social import Reputation, EntityType
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from app.core.utils.gpt.client import GPTClient

def get_reputation_between_entities(source_id: int, source_type: str, target_id: int, target_type: str):
    """Fetch the reputation record between two entities."""
    return Reputation.query.filter_by(
        source_entity_id=source_id,
        source_entity_type=EntityType(source_type),
        target_entity_id=target_id,
        target_entity_type=EntityType(target_type)
    ).first()

def get_all_reputations_for_entity(entity_id: int, entity_type: str, as_source: bool = True):
    """Fetch all reputation records where the entity is source or target."""
    if as_source:
        return Reputation.query.filter_by(
            source_entity_id=entity_id,
            source_entity_type=EntityType(entity_type)
        ).all()
    else:
        return Reputation.query.filter_by(
            target_entity_id=entity_id,
            target_entity_type=EntityType(entity_type)
        ).all()

def summarize_reputation_history(source_id: int, source_type: str, target_id: int, target_type: str, as_dict: bool = False):
    """Summarize the reputation history between two entities."""
    rep = get_reputation_between_entities(source_id, source_type, target_id, target_type)
    if not rep:
        return {} if as_dict else "No reputation history."
    summary_dict = {
        'value': rep.value,
        'strength': rep.strength,
        'last_updated': rep.last_updated,
        'context': rep.context
    }
    if as_dict:
        return summary_dict
    return f"Reputation value: {rep.value}, strength: {rep.strength}, last updated: {rep.last_updated}, context: {rep.context}"

def gpt_summarize_reputation(source_id: int, source_type: str, target_id: int, target_type: str):
    """Generate a GPT-based summary of reputation between two entities, using strength-based intensifiers."""
    rep = get_reputation_between_entities(source_id, source_type, target_id, target_type)
    if not rep:
        return "No reputation history."

    # Choose intensifier based on strength
    strength = rep.strength or 0
    if strength < 20:
        intensifier = "is rumored to be"
        confidence = "uncertain"
    elif strength < 60:
        intensifier = "is known to be"
        confidence = "moderate"
    else:
        intensifier = "is infamous for" if (rep.value and rep.value < 0) else "is renowned for"
        confidence = "established"

    # Compose prompt
    system_prompt = (
        "You are a fantasy world narrator. Summarize the reputation between two entities for a game master or player. "
        "Use immersive, in-universe language. Adjust the confidence and detail of your summary based on the 'strength' value. "
        "If strength is low, use uncertain/rumor language. If high, be confident and specific."
    )
    user_prompt = (
        f"Source Entity: {source_type} (ID: {source_id})\n"
        f"Target Entity: {target_type} (ID: {target_id})\n"
        f"Reputation Value: {rep.value}\n"
        f"Rank: {rep.rank}\n"
        f"Strength: {rep.strength} ({confidence})\n"
        f"Last Updated: {rep.last_updated}\n"
        f"Change Source: {rep.change_source}\n"
        f"Context: {rep.context or 'N/A'}\n"
        f"Summary Template: The target {intensifier} ... (fill in details based on above)."
    )
    try:
        gpt = GPTClient()
        summary = gpt.call(system_prompt, user_prompt, max_tokens=120)
        return summary
    except Exception as e:
        # Fallback to basic summary
        return f"[GPT error: {e}] Reputation value: {rep.value}, strength: {rep.strength}, last updated: {rep.last_updated}, context: {rep.context}" 