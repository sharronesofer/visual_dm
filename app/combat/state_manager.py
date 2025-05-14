from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from app.combat.damage_engine import DamageType, AttackType
from app.combat.combat_logger import LogCategory, LogLevel, CombatLogger

@dataclass
class CombatState:
    combat_id: str
    participants: List[str]
    initiative_order: List[str]
    current_round: int
    current_turn: int
    active_effects: Dict[str, List[Dict]]  # participant_id -> list of active effects
    battlefield_conditions: List[Dict]
    status: str  # 'active', 'paused', 'completed'
    created_at: datetime
    updated_at: datetime
    winner: Optional[str] = None
    
class CombatStateManager:
    def __init__(self, app):
        self.app = app
        self.combat_states = app.db.collection('combat_states')
        self.logger = app.logger
        
    async def save_combat_state(self, combat_id: str, state_data: Dict) -> bool:
        """Save the current state of a combat encounter."""
        try:
            # Create or update the combat state
            state = CombatState(
                combat_id=combat_id,
                participants=state_data.get('participants', []),
                initiative_order=state_data.get('initiative_order', []),
                current_round=state_data.get('current_round', 1),
                current_turn=state_data.get('current_turn', 0),
                active_effects=state_data.get('active_effects', {}),
                battlefield_conditions=state_data.get('battlefield_conditions', []),
                status=state_data.get('status', 'active'),
                created_at=state_data.get('created_at', datetime.now()),
                updated_at=datetime.now(),
                winner=state_data.get('winner')
            )
            
            # Convert to dictionary for storage
            state_dict = asdict(state)
            
            # Save to database
            await self.combat_states.update_one(
                {'combat_id': combat_id},
                {'$set': state_dict},
                upsert=True
            )
            
            self.logger.info(f"Combat state saved for combat {combat_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving combat state: {str(e)}")
            return False
            
    async def load_combat_state(self, combat_id: str) -> Optional[CombatState]:
        """Load a saved combat state."""
        try:
            # Retrieve the state from database
            state_data = await self.combat_states.find_one({'combat_id': combat_id})
            
            if not state_data:
                self.logger.warning(f"No saved state found for combat {combat_id}")
                return None
                
            # Convert datetime strings back to datetime objects
            state_data['created_at'] = datetime.fromisoformat(state_data['created_at'])
            state_data['updated_at'] = datetime.fromisoformat(state_data['updated_at'])
            
            # Create and return CombatState object
            return CombatState(**state_data)
            
        except Exception as e:
            self.logger.error(f"Error loading combat state: {str(e)}")
            return None
            
    async def delete_combat_state(self, combat_id: str) -> bool:
        """Delete a saved combat state."""
        try:
            result = await self.combat_states.delete_one({'combat_id': combat_id})
            success = result.deleted_count > 0
            
            if success:
                self.logger.info(f"Combat state deleted for combat {combat_id}")
            else:
                self.logger.warning(f"No combat state found to delete for combat {combat_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting combat state: {str(e)}")
            return False
            
    async def list_active_combats(self) -> List[str]:
        """Get a list of all active combat IDs."""
        try:
            active_states = await self.combat_states.find(
                {'status': 'active'},
                {'combat_id': 1}
            ).to_list(length=None)
            
            return [state['combat_id'] for state in active_states]
            
        except Exception as e:
            self.logger.error(f"Error listing active combats: {str(e)}")
            return []
            
    async def update_combat_status(self, combat_id: str, status: str) -> bool:
        """Update the status of a combat encounter."""
        try:
            result = await self.combat_states.update_one(
                {'combat_id': combat_id},
                {
                    '$set': {
                        'status': status,
                        'updated_at': datetime.now()
                    }
                }
            )
            
            success = result.modified_count > 0
            
            if success:
                self.logger.info(f"Combat {combat_id} status updated to {status}")
            else:
                self.logger.warning(f"No combat state found to update for combat {combat_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error updating combat status: {str(e)}")
            return False 