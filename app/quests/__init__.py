"""
Quest module initialization.
Exposes quest-related functionality.
"""

from flask import Blueprint

quest_bp = Blueprint('quest', __name__)

from . import quest_routes

from app.models.quest_log import QuestLogEntry
from app.models.arc import PlayerArc
from app.quests.quest_utils import (
    generate_quest_title,
    validate_quest_data,
    calculate_quest_reward,
    generate_quest_steps,
    update_quest_progress,
    generate_journal_entry,
    load_player_arc,
    save_player_arc,
    create_player_arc,
    update_arc_with_event,
    trigger_war_arc,
    generate_character_arc
)

__all__ = [
    'quest_bp',
    'QuestLogEntry',
    'PlayerArc',
    'generate_quest_title',
    'validate_quest_data',
    'calculate_quest_reward',
    'generate_quest_steps',
    'update_quest_progress',
    'generate_journal_entry',
    'load_player_arc',
    'save_player_arc',
    'create_player_arc',
    'update_arc_with_event',
    'trigger_war_arc',
    'generate_character_arc'
]
