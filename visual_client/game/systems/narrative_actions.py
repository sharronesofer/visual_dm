from typing import Dict, List, Optional
import random

def narrate_combat_action(attacker: Dict, defender: Dict, action: str, 
                         result: Dict) -> str:
    """Generate a narrative description of a combat action.
    
    Args:
        attacker: Dictionary containing attacker's stats
        defender: Dictionary containing defender's stats
        action: Type of action taken
        result: Dictionary containing action results
        
    Returns:
        str: Narrative description
    """
    attacker_name = attacker.get('name', 'Unknown')
    defender_name = defender.get('name', 'Unknown')
    
    if not result['hit_success']:
        return f"{attacker_name} attempts to {action} {defender_name}, but misses!"
        
    damage = result['damage']
    if damage == 0:
        return f"{attacker_name} {action}s {defender_name}, but fails to deal any damage!"
        
    return f"{attacker_name} {action}s {defender_name} for {damage} damage!"

def narrate_environment_change(change_type: str, intensity: int) -> str:
    """Generate a narrative description of an environmental change.
    
    Args:
        change_type: Type of change (weather, time, etc.)
        intensity: Intensity of the change (0-10)
        
    Returns:
        str: Narrative description
    """
    descriptions = {
        'weather': {
            'light': [
                "A gentle breeze rustles the leaves.",
                "Light clouds drift across the sky.",
                "A few raindrops begin to fall."
            ],
            'medium': [
                "The wind picks up, swaying the trees.",
                "Dark clouds gather overhead.",
                "Rain begins to fall steadily."
            ],
            'heavy': [
                "A fierce wind howls through the area.",
                "Thunder rumbles in the distance.",
                "Torrential rain pours down."
            ]
        },
        'time': {
            'light': [
                "The sun begins to set.",
                "Shadows grow longer.",
                "The air grows cooler."
            ],
            'medium': [
                "Twilight settles over the land.",
                "The first stars appear in the sky.",
                "The moon rises above the horizon."
            ],
            'heavy': [
                "Darkness envelops the area.",
                "The night is deep and still.",
                "Only the moon's light guides the way."
            ]
        }
    }
    
    intensity_level = 'light' if intensity < 4 else 'medium' if intensity < 7 else 'heavy'
    return random.choice(descriptions[change_type][intensity_level])

def narrate_character_decision(character: Dict, decision: str, 
                             context: Dict) -> str:
    """Generate a narrative description of a character's decision.
    
    Args:
        character: Dictionary containing character's stats
        decision: Type of decision made
        context: Dictionary containing decision context
        
    Returns:
        str: Narrative description
    """
    character_name = character.get('name', 'Unknown')
    personality = character.get('personality', 'neutral')
    
    templates = {
        'abandon': {
            'cowardly': f"{character_name} panics and flees from the danger!",
            'pragmatic': f"{character_name} wisely decides to retreat and live to fight another day.",
            'loyal': f"{character_name} reluctantly withdraws, knowing they must survive to serve their cause."
        },
        'persist': {
            'cowardly': f"{character_name} trembles but stands their ground, fearing the consequences of retreat.",
            'pragmatic': f"{character_name} assesses the situation and decides to press on.",
            'loyal': f"{character_name} bravely continues forward, determined to fulfill their duty."
        }
    }
    
    return templates[decision][personality] 