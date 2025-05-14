"""
AI combat utilities.
Provides functionality for AI-controlled combat behavior.
"""

from typing import Dict, List, Optional
from app.core.models.combat import CombatState, CombatParticipant, CombatEngine
from app.core.models.character import Character
from app.core.models.npc import NPC
from app.core.models.spell import Spell, SpellEffect

def get_ai_action(participant: CombatParticipant, combat_state: CombatState) -> Dict:
    """Get an AI action for a participant."""
    # Get potential targets
    targets = [p for p in combat_state.participants if p.id != participant.id]
    if not targets:
        return {'type': 'end_turn'}

    # Choose target based on health
    target = min(targets, key=lambda p: p.current_health)

    # Choose action based on participant type and state
    if participant.character:
        # Character AI
        if participant.current_health < participant.max_health * 0.3:
            # Low health - try to heal
            healing_spells = [s for s in participant.character.spells if s.school == 'healing']
            if healing_spells:
                return {
                    'type': 'spell',
                    'spell_id': healing_spells[0].id,
                    'target_id': participant.id
                }
    else:
        # NPC AI
        if participant.npc.type == 'caster':
            # Caster NPC - use spells
            if participant.current_mana > 0:
                offensive_spells = [s for s in participant.npc.spells if s.school in ['evocation', 'necromancy']]
                if offensive_spells:
                    return {
                        'type': 'spell',
                        'spell_id': offensive_spells[0].id,
                        'target_id': target.id
                    }

    # Default to attack
    return {
        'type': 'attack',
        'target_id': target.id,
        'damage': 5  # Base damage
    }

def evaluate_combat_state(combat_state: CombatState) -> Dict:
    """Evaluate the current combat state for AI decision making."""
    # Count active participants
    active_participants = [p for p in combat_state.participants if p.current_health > 0]
    characters = [p for p in active_participants if p.character]
    npcs = [p for p in active_participants if p.npc]

    # Calculate total health
    total_character_health = sum(p.current_health for p in characters)
    total_npc_health = sum(p.current_health for p in npcs)

    # Calculate average health
    avg_character_health = total_character_health / len(characters) if characters else 0
    avg_npc_health = total_npc_health / len(npcs) if npcs else 0

    return {
        'active_characters': len(characters),
        'active_npcs': len(npcs),
        'avg_character_health': avg_character_health,
        'avg_npc_health': avg_npc_health,
        'total_character_health': total_character_health,
        'total_npc_health': total_npc_health
    }

def should_retreat(participant: CombatParticipant, combat_state: CombatState) -> bool:
    """Determine if an AI participant should retreat."""
    if participant.character:
        # Character AI retreat logic
        if participant.current_health < participant.max_health * 0.2:
            return True
    else:
        # NPC AI retreat logic
        if participant.npc.traits and 'cowardly' in participant.npc.traits:
            if participant.current_health < participant.max_health * 0.3:
                return True

    # Check if outnumbered
    active_participants = [p for p in combat_state.participants if p.current_health > 0]
    allies = [p for p in active_participants if (p.character and participant.character) or (p.npc and participant.npc)]
    enemies = [p for p in active_participants if (p.character and participant.npc) or (p.npc and participant.character)]

    if len(enemies) >= 2 * len(allies):
        return True

    return False