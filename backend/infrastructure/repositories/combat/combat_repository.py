"""
Combat Repository Infrastructure Implementation

This module provides the infrastructure implementation of the combat repository protocol,
handling data persistence and retrieval according to the Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime

# Business domain imports (for mapping)
from backend.systems.combat.models import CombatEncounter, Combatant, CombatAction, StatusEffect
from backend.systems.combat.models.combat_action import ActionDefinition


class CombatRepositoryImpl:
    """
    Infrastructure implementation of the CombatRepository protocol.
    
    For demo purposes, uses in-memory storage. In production, would use SQLAlchemy.
    """
    
    def __init__(self):
        # In-memory storage for demo purposes
        self._encounters: Dict[UUID, CombatEncounter] = {}
    
    def create_encounter(self, encounter: CombatEncounter) -> CombatEncounter:
        """Create a new combat encounter."""
        self._encounters[encounter.id] = encounter
        return encounter
    
    def get_encounter_by_id(self, encounter_id: UUID) -> Optional[CombatEncounter]:
        """Get encounter by ID."""
        return self._encounters.get(encounter_id)
    
    def update_encounter(self, encounter: CombatEncounter) -> CombatEncounter:
        """Update existing encounter."""
        if encounter.id not in self._encounters:
            raise ValueError(f"Encounter {encounter.id} not found")
        
        self._encounters[encounter.id] = encounter
        return encounter
    
    def delete_encounter(self, encounter_id: UUID) -> bool:
        """Delete encounter."""
        if encounter_id in self._encounters:
            del self._encounters[encounter_id]
            return True
        return False
    
    def list_encounters(self, 
                       page: int = 1, 
                       size: int = 50, 
                       status: Optional[str] = None) -> Tuple[List[CombatEncounter], int]:
        """List encounters with pagination."""
        encounters = list(self._encounters.values())
        
        # Apply status filter
        if status:
            encounters = [e for e in encounters if e.status == status]
        
        # Apply pagination
        total = len(encounters)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated = encounters[start_idx:end_idx]
        
        return paginated, total


def create_combat_repository() -> CombatRepositoryImpl:
    """Factory function to create combat repository."""
    return CombatRepositoryImpl()


__all__ = ["CombatRepositoryImpl", "create_combat_repository"] 