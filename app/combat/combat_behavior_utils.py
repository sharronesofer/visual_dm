import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

def should_abandon(npc_data: Dict[str, Any], combat_data: Dict[str, Any]) -> bool:
    """
    Determine if an NPC should abandon combat based on various factors.
    
    Args:
        npc_data: The NPC's data dictionary
        combat_data: Current combat state data
        
    Returns:
        Boolean indicating whether the NPC should abandon combat
    """
    try:
        # Get NPC's current HP percentage
        current_hp = npc_data.get('HP', 0)
        max_hp = npc_data.get('max_HP', 100)
        hp_percentage = (current_hp / max_hp) * 100 if max_hp > 0 else 0
        
        # Get NPC's morale and loyalty
        morale = npc_data.get('morale', 50)
        loyalty = npc_data.get('loyalty', 50)
        
        # Get number of allies and enemies
        allies_alive = combat_data.get('allies_alive', 1)
        enemies_alive = combat_data.get('enemies_alive', 1)
        odds = allies_alive / enemies_alive if enemies_alive > 0 else 1
        
        # Calculate base chance to flee
        flee_chance = 0
        
        # Low HP increases flee chance
        if hp_percentage < 25:
            flee_chance += 40
        elif hp_percentage < 50:
            flee_chance += 20
            
        # Bad odds increase flee chance
        if odds < 0.5:
            flee_chance += 20
        elif odds < 1:
            flee_chance += 10
            
        # Low morale increases flee chance
        if morale < 30:
            flee_chance += 30
        elif morale < 50:
            flee_chance += 15
            
        # High loyalty reduces flee chance
        flee_chance -= loyalty // 4
        
        # Clamp flee chance between 0 and 100
        flee_chance = max(0, min(100, flee_chance))
        
        # Roll against flee chance
        roll = random.randint(1, 100)
        should_flee = roll <= flee_chance
        
        if should_flee:
            logger.info(f"NPC {npc_data.get('name', 'Unknown')} decided to flee combat. "
                       f"Roll: {roll}, Flee Chance: {flee_chance}%")
        
        return should_flee
        
    except Exception as e:
        logger.error(f"Error checking if NPC should abandon: {str(e)}")
        return False 