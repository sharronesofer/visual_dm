"""
Magic system utilities.

This module contains utility functions for the magic system,
including calculations, validations, and helper functions.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .models import MagicModel, SpellModel, SpellEffect, SpellSlot

def calculate_spell_power(spell: SpellModel, caster_level: int) -> float:
    """
    Calculate the actual power of a spell based on the base spell and caster level.
    
    Args:
        spell: The spell model
        caster_level: The level of the caster
        
    Returns:
        float: The calculated spell power
    """
    base_power = spell.power
    scaling_factor = spell.effects.get('scaling_factor', 0.1)
    return base_power + (base_power * scaling_factor * caster_level)

def validate_spell_requirements(spell: SpellModel, caster_stats: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that a character meets the requirements to cast a spell.
    
    Args:
        spell: The spell model
        caster_stats: Dictionary of caster stats
        
    Returns:
        Tuple[bool, str]: (True, "") if valid, (False, error_message) otherwise
    """
    requirements = spell.requirements
    
    # Check level requirements
    if 'min_level' in requirements and caster_stats.get('level', 0) < requirements['min_level']:
        return False, f"Caster level too low. Required: {requirements['min_level']}"
    
    # Check attribute requirements
    for attr, value in requirements.get('attributes', {}).items():
        if caster_stats.get(attr, 0) < value:
            return False, f"Insufficient {attr}. Required: {value}"
    
    # Check resource requirements
    if 'mana_cost' in requirements and caster_stats.get('current_mana', 0) < spell.mana_cost:
        return False, "Not enough mana"
    
    return True, ""

def generate_effect_description(effect: SpellEffect) -> str:
    """
    Generate a human-readable description of a spell effect.
    
    Args:
        effect: The spell effect model
        
    Returns:
        str: A human-readable description
    """
    effect_type = effect.effects.get('type', 'unknown')
    magnitude = effect.effects.get('magnitude', 0)
    duration = effect.remaining_duration
    
    if effect_type == 'damage':
        return f"Deals {magnitude} damage for {duration} more rounds"
    elif effect_type == 'heal':
        return f"Heals {magnitude} health for {duration} more rounds"
    elif effect_type == 'buff':
        stat = effect.effects.get('stat', 'unknown')
        return f"Increases {stat} by {magnitude} for {duration} more rounds"
    elif effect_type == 'debuff':
        stat = effect.effects.get('stat', 'unknown')
        return f"Decreases {stat} by {magnitude} for {duration} more rounds"
    else:
        return f"Unknown effect for {duration} more rounds"

def check_spell_slot_availability(character_id: int, spell_level: int, spell_slots: List[SpellSlot]) -> Tuple[bool, Optional[SpellSlot]]:
    """
    Check if a character has an available spell slot of the appropriate level.
    
    Args:
        character_id: ID of the character
        spell_level: Level of the spell
        spell_slots: List of character's spell slots
        
    Returns:
        Tuple[bool, Optional[SpellSlot]]: (True, spell_slot) if available, (False, None) otherwise
    """
    for slot in spell_slots:
        if slot.character_id == character_id and slot.level == spell_level and slot.used < slot.total:
            return True, slot
    return False, None

def calculate_spell_difficulty(spell: SpellModel) -> int:
    """
    Calculate the difficulty class (DC) for a spell save.
    
    Args:
        spell: The spell model
        
    Returns:
        int: The calculated difficulty class
    """
    base_dc = 10
    power_modifier = int(spell.power / 10)
    additional_dc = spell.effects.get('save_dc_modifier', 0)
    
    return base_dc + power_modifier + additional_dc

def parse_spell_target_area(spell: SpellModel) -> Dict[str, Any]:
    """
    Parse and normalize the target area of a spell.
    
    Args:
        spell: The spell model
        
    Returns:
        Dict[str, Any]: Normalized target area information
    """
    target_info = spell.effects.get('target_area', {})
    
    if not target_info:
        # Default to single target
        return {
            'type': 'single',
            'range': 30,
            'affects_self': False
        }
    
    # Normalize the target area
    target_type = target_info.get('type', 'single')
    
    if target_type == 'aoe':
        shape = target_info.get('shape', 'circle')
        size = target_info.get('size', 10)
        range_value = target_info.get('range', 60)
        return {
            'type': 'aoe',
            'shape': shape,
            'size': size,
            'range': range_value,
            'affects_self': target_info.get('affects_self', False)
        }
    elif target_type == 'line':
        length = target_info.get('length', 30)
        width = target_info.get('width', 5)
        return {
            'type': 'line',
            'length': length,
            'width': width,
            'affects_self': target_info.get('affects_self', True)
        }
    else:  # single target
        return {
            'type': 'single',
            'range': target_info.get('range', 30),
            'affects_self': target_info.get('affects_self', False)
        }

def calculate_magic_learning_time(character_level: int, spell_level: int) -> int:
    """
    Calculate the time needed to learn a new spell (in hours).
    
    Args:
        character_level: Level of the character
        spell_level: Level of the spell
        
    Returns:
        int: Hours needed to learn the spell
    """
    base_time = spell_level * 4  # Base hours per spell level
    level_modifier = max(0, spell_level - (character_level / 2))  # More time if spell level > half character level
    
    return int(base_time + (level_modifier * 2))

def format_spell_duration(duration_rounds: int) -> str:
    """
    Format a spell duration from rounds to a human-readable string.
    
    Args:
        duration_rounds: Duration in rounds
        
    Returns:
        str: Formatted duration string
    """
    if duration_rounds <= 0:
        return "Instantaneous"
    elif duration_rounds == 1:
        return "1 round"
    elif duration_rounds <= 10:
        return f"{duration_rounds} rounds"
    elif duration_rounds <= 600:  # 10 minutes (10 rounds per minute)
        minutes = duration_rounds // 10
        return f"{minutes} minute{'s' if minutes > 1 else ''}"
    elif duration_rounds <= 36000:  # 1 hour (600 rounds per hour)
        hours = duration_rounds // 600
        return f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        days = duration_rounds // 14400  # 24 hours (14400 rounds per day)
        return f"{days} day{'s' if days > 1 else ''}"

def check_spell_compatibility(spell: SpellModel, character_class: str, alignment: str) -> Tuple[bool, str]:
    """
    Check if a spell is compatible with a character's class and alignment.
    
    Args:
        spell: The spell model
        character_class: The character's class
        alignment: The character's alignment
        
    Returns:
        Tuple[bool, str]: (True, "") if compatible, (False, error_message) otherwise
    """
    # Check class compatibility
    compatible_classes = spell.requirements.get('classes', [])
    if compatible_classes and character_class not in compatible_classes:
        return False, f"This spell cannot be learned by {character_class}s"
    
    # Check alignment compatibility
    if 'alignment' in spell.requirements:
        req_alignment = spell.requirements['alignment']
        
        # Check if alignment is specified as a list of allowed alignments
        if isinstance(req_alignment, list) and alignment not in req_alignment:
            return False, f"This spell requires one of these alignments: {', '.join(req_alignment)}"
        
        # Check if alignment is specified as forbidden alignments
        if isinstance(req_alignment, dict) and 'forbidden' in req_alignment:
            if alignment in req_alignment['forbidden']:
                return False, f"This spell cannot be used by {alignment} characters"
    
    return True, ""

def can_cast_spell(spell: SpellModel, character_stats: Dict[str, Any], available_slots: List[SpellSlot]) -> Tuple[bool, str, Optional[SpellSlot]]:
    """
    Check if a character can cast a spell based on requirements and available slots.
    
    Args:
        spell: The spell model
        character_stats: Dictionary of character stats
        available_slots: List of available spell slots
        
    Returns:
        Tuple[bool, str, Optional[SpellSlot]]: (can_cast, message, slot_to_use)
    """
    # Check basic requirements
    valid, message = validate_spell_requirements(spell, character_stats)
    if not valid:
        return False, message, None
    
    # Check class and alignment compatibility
    compatible, message = check_spell_compatibility(
        spell, 
        character_stats.get('class', ''), 
        character_stats.get('alignment', '')
    )
    if not compatible:
        return False, message, None
    
    # Check spell slot availability
    if 'use_spell_slot' in spell.requirements and spell.requirements['use_spell_slot']:
        has_slot, slot = check_spell_slot_availability(
            character_stats['id'], 
            spell.level, 
            available_slots
        )
        if not has_slot:
            return False, f"No available level {spell.level} spell slot", None
        return True, "Can cast spell", slot
    
    # If no spell slot required, check if there's a cooldown
    if 'cooldown' in spell.requirements:
        cooldown = spell.requirements['cooldown']
        last_cast = character_stats.get('last_cast_times', {}).get(str(spell.id), 0)
        current_time = character_stats.get('current_time', 0)
        
        if current_time - last_cast < cooldown:
            remaining = cooldown - (current_time - last_cast)
            return False, f"Spell is on cooldown for {remaining} more rounds", None
    
    return True, "Can cast spell", None

def apply_spell_effect(spell: SpellModel, caster_stats: Dict[str, Any], target_stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply a spell's effect to a target and return the resulting changes.
    
    Args:
        spell: The spell model
        caster_stats: Dictionary of caster stats
        target_stats: Dictionary of target stats
        
    Returns:
        Dict[str, Any]: Dictionary of changes applied to the target
    """
    effect_type = spell.effects.get('type', 'none')
    power = calculate_spell_power(spell, caster_stats.get('level', 1))
    changes = {}
    
    # Process different effect types
    if effect_type == 'damage':
        damage_type = spell.effects.get('damage_type', 'magical')
        resistance = target_stats.get('resistances', {}).get(damage_type, 0)
        damage = max(1, power - resistance)
        
        # Apply damage to target
        current_hp = target_stats.get('current_hp', 0)
        new_hp = max(0, current_hp - damage)
        changes['current_hp'] = new_hp
        changes['damage_taken'] = damage
        
    elif effect_type == 'heal':
        healing = power
        max_hp = target_stats.get('max_hp', 0)
        current_hp = target_stats.get('current_hp', 0)
        new_hp = min(max_hp, current_hp + healing)
        
        changes['current_hp'] = new_hp
        changes['healing_received'] = healing
        
    elif effect_type == 'buff' or effect_type == 'debuff':
        stat = spell.effects.get('stat', '')
        modifier = power if effect_type == 'buff' else -power
        
        if stat:
            current_value = target_stats.get(stat, 0)
            changes[stat] = current_value + modifier
            changes['buff_applied' if effect_type == 'buff' else 'debuff_applied'] = {
                'stat': stat,
                'modifier': modifier
            }
    
    # Handle special effects
    if 'special_effects' in spell.effects:
        special = spell.effects['special_effects']
        
        if 'status' in special:
            status = special['status']
            duration = special.get('status_duration', 1)
            changes['status_effect'] = {
                'type': status,
                'duration': duration
            }
    
    return changes

def calculate_spell_duration(spell: SpellModel, caster_level: int) -> int:
    """
    Calculate the duration of a spell effect in rounds.
    
    Args:
        spell: The spell model
        caster_level: Level of the caster
        
    Returns:
        int: Duration in rounds
    """
    base_duration = spell.effects.get('duration', 0)
    scaling = spell.effects.get('duration_scaling', 0)
    
    # Calculate duration based on caster level and scaling factor
    if base_duration <= 0:
        return 0  # Instantaneous spell
    
    additional_duration = int(caster_level * scaling)
    return base_duration + additional_duration 