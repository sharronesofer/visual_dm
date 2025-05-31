"""
Utility functions for NPC-related operations.
"""

from typing import Dict, List, Optional, TYPE_CHECKING
import random
from datetime import datetime, timedelta
from backend.infrastructure.shared.utils.time_utils import get_current_time
from backend.infrastructure.shared.utils.location_utils import get_distance

if TYPE_CHECKING:
    from backend.systems.npc import NPC, NPCType, NPCDisposition

class NPCUtils:
    """Utility class for NPC-related operations."""
    
    @staticmethod
    def calculate_disposition(npc: 'app.core.models.npc.NPC', player_reputation: float) -> float:
        """Calculate NPC's disposition towards player based on reputation."""
        base_disposition = npc.base_disposition
        reputation_factor = 0.1 * player_reputation
        return min(max(base_disposition + reputation_factor, -1.0), 1.0)
    
    @staticmethod
    def update_schedule(npc: 'app.core.models.npc.NPC', current_time: datetime) -> None:
        """Update NPC's location based on their schedule."""
        if not npc.schedule:
            return
            
        current_hour = current_time.hour
        for time_slot in npc.schedule:
            if time_slot['start_hour'] <= current_hour < time_slot['end_hour']:
                npc.current_location_id = time_slot['location_id']
                break
    
    @staticmethod
    def generate_dialogue(npc: 'app.core.models.npc.NPC', context: Dict) -> str:
        """Generate contextual dialogue for the NPC."""
        if not npc.dialogue_options:
            return "..."
            
        relevant_options = [
            option for option in npc.dialogue_options
            if all(context.get(req) for req in option.get('requirements', []))
        ]
        
        if not relevant_options:
            return random.choice(npc.dialogue_options['default'])
            
        chosen_option = random.choice(relevant_options)
        return chosen_option['text'].format(**context)
    
    @staticmethod
    def check_interaction_availability(npc: 'app.core.models.npc.NPC', player_level: int) -> bool:
        """Check if NPC is available for interaction."""
        current_time = get_current_time()
        
        # Check schedule availability
        if npc.schedule:
            current_hour = current_time.hour
            is_scheduled = any(
                time_slot['start_hour'] <= current_hour < time_slot['end_hour']
                for time_slot in npc.schedule
            )
            if not is_scheduled:
                return False
        
        # Check level requirement
        if player_level < npc.level_requirement:
            return False
            
        # Check cooldown
        if npc.last_interaction:
            cooldown = timedelta(minutes=npc.interaction_cooldown)
            if current_time - npc.last_interaction < cooldown:
                return False
                
        return True
    
    @staticmethod
    def process_interaction(npc: 'app.core.models.npc.NPC', interaction_type: str, context: Dict) -> Dict:
        """Process an interaction with the NPC."""
        result = {
            'success': True,
            'message': '',
            'rewards': {},
            'reputation_change': 0
        }
        
        if not NPCUtils.check_interaction_availability(npc, context.get('player_level', 0)):
            result['success'] = False
            result['message'] = "NPC is not available for interaction"
            return result
            
        # Update last interaction time
        npc.last_interaction = get_current_time()
        
        # Handle different interaction types
        if interaction_type == 'trade':
            result.update(NPCUtils._handle_trade(npc, context))
        elif interaction_type == 'quest':
            result.update(NPCUtils._handle_quest(npc, context))
        elif interaction_type == 'dialogue':
            result.update(NPCUtils._handle_dialogue(npc, context))
        elif interaction_type == 'training':
            result.update(NPCUtils._handle_training(npc, context))
        
        return result
    
    @staticmethod
    def _handle_trade(npc: 'app.core.models.npc.NPC', context: Dict) -> Dict:
        """Handle trade interaction with NPC."""
        if npc.type != 'merchant':
            return {
                'success': False,
                'message': "This NPC is not a merchant"
            }
            
        # Implement trade logic here
        return {
            'success': True,
            'message': "Trade successful",
            'inventory': npc.inventory
        }
    
    @staticmethod
    def _handle_quest(npc: 'app.core.models.npc.NPC', context: Dict) -> Dict:
        """Handle quest interaction with NPC."""
        if not npc.available_quests:
            return {
                'success': False,
                'message': "No quests available"
            }
            
        # Implement quest handling logic here
        return {
            'success': True,
            'message': "Quest interaction successful",
            'available_quests': npc.available_quests
        }
    
    @staticmethod
    def _handle_dialogue(npc: 'app.core.models.npc.NPC', context: Dict) -> Dict:
        """Handle dialogue interaction with NPC."""
        dialogue = NPCUtils.generate_dialogue(npc, context)
        return {
            'success': True,
            'message': dialogue,
            'disposition_change': random.uniform(-0.1, 0.1)
        }
    
    @staticmethod
    def _handle_training(npc: 'app.core.models.npc.NPC', context: Dict) -> Dict:
        """Handle training interaction with NPC."""
        if npc.type != 'trainer':
            return {
                'success': False,
                'message': "This NPC cannot provide training"
            }
            
        # Implement training logic here
        return {
            'success': True,
            'message': "Training session completed",
            'skills_improved': []
        } 