from typing import Dict, Optional
from uuid import uuid4

from backend.systems.combat.schemas.combat import CombatStateSchema

class CombatRepository:
    _combats: Dict[str, CombatStateSchema] = {}

    def create_combat(self, initial_combat_data: Optional[Dict] = None) -> CombatStateSchema:
        combat_id = str(uuid4())
        if initial_combat_data:
            # If initial data is provided, merge it with default combat_id
            # This assumes initial_combat_data might already have a combat_id, which we override
            # or it's a partial CombatStateSchema that needs combat_id to be complete
            combat_state = CombatStateSchema(**initial_combat_data, combat_id=combat_id)
        else:
            # Create a minimal default combat state if no data is provided
            combat_state = CombatStateSchema(combat_id=combat_id, turn_order=[], combatants=[])
        
        self._combats[combat_id] = combat_state
        return combat_state

    def get_combat_by_id(self, combat_id: str) -> Optional[CombatStateSchema]:
        return self._combats.get(combat_id)

    def update_combat(self, combat_id: str, combat_data: CombatStateSchema) -> Optional[CombatStateSchema]:
        if combat_id in self._combats:
            # Ensure the combat_id in the data matches the key, or just overwrite if it's part of the model
            if combat_data.combat_id != combat_id:
                 # This case should ideally not happen if combat_id is immutable or handled correctly by service
                 # For now, we'll allow updating if the path param combat_id is the true reference
                 pass # Or raise an error: raise ValueError("Combat ID mismatch")
            
            self._combats[combat_id] = combat_data
            return combat_data
        return None

    def delete_combat(self, combat_id: str) -> bool:
        if combat_id in self._combats:
            del self._combats[combat_id]
            return True
        return False

    def list_all_combats(self) -> list[CombatStateSchema]:
        return list(self._combats.values())

# Singleton instance
combat_repository = CombatRepository() 