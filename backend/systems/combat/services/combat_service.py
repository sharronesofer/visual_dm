from typing import Optional, List, Dict, Any
from backend.systems.combat.schemas.combat import CombatStateSchema
from backend.systems.combat.repositories.combat_repository import combat_repository, CombatRepository

class CombatService:
    def __init__(self, repository: CombatRepository):
        self.repository = repository

    def create_new_combat_instance(self, initial_combat_data: Optional[Dict] = None) -> CombatStateSchema:
        """Creates a new combat instance, potentially with initial data."""
        # The repository now handles assigning a UUID and creating a minimal state if initial_combat_data is None
        return self.repository.create_combat(initial_combat_data=initial_combat_data)

    def get_combat_state(self, combat_id: str) -> Optional[CombatStateSchema]:
        """Retrieves the current state of a specific combat instance."""
        return self.repository.get_combat_by_id(combat_id)

    def update_combat_state(self, combat_id: str, combat_data_update: CombatStateSchema) -> Optional[CombatStateSchema]:
        """
        Updates an existing combat instance. 
        The entire CombatStateSchema is expected for an update for simplicity in this in-memory version.
        More granular updates could be added later.
        """
        # Ensure the combat_id in the payload matches the path parameter if it exists, 
        # or that the combat_data_update is a valid CombatStateSchema
        if combat_data_update.combat_id != combat_id:
            # Or handle this discrepancy as an error, depending on desired behavior
            # For now, we assume the path combat_id is authoritative if they differ, and allow the update to proceed
            # but the repository will use the combat_id from the path for lookup.
            # A stricter approach might be: raise ValueError("Combat ID in path and payload must match")
            pass 

        return self.repository.update_combat(combat_id, combat_data_update)

    def end_combat_instance(self, combat_id: str) -> bool:
        """Marks a combat instance as inactive or deletes it."""
        # For an in-memory store, deleting might be appropriate for "ending"
        return self.repository.delete_combat(combat_id)
    
    def list_all_combat_instances(self) -> List[CombatStateSchema]:
        """Lists all current combat instances."""
        return self.repository.list_all_combats()

# Singleton instance of the service
combat_service = CombatService(repository=combat_repository) 