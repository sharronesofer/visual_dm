"""
Combat Service Infrastructure Facade

This module provides the infrastructure facade for the combat system,
bridging the domain-driven business logic with the API layer.
"""

from typing import Optional, List, Dict, Any, UUID
from uuid import uuid4
from datetime import datetime

from backend.infrastructure.schemas.combat.combat import (
    CombatStateSchema, CombatantSchema, CombatActionSchema, 
    CreateCombatRequest, AddCombatantRequest, ExecuteActionRequest,
    SetInitiativeRequest, CombatSummarySchema
)

# Import the proper domain-driven services
from backend.systems.combat.services.combat_service import CombatService
from backend.systems.combat.models import CombatEncounter, Combatant, CombatAction, StatusEffect

# Import infrastructure repositories (these would need to be implemented)
from backend.infrastructure.repositories.combat.combat_repository import combat_repository


class CombatBusinessRepository:
    """Repository adapter to bridge infrastructure and domain layers"""
    
    def __init__(self, infrastructure_repo):
        self.infrastructure_repo = infrastructure_repo
    
    def create_encounter(self, encounter: CombatEncounter) -> CombatEncounter:
        """Create a new combat encounter"""
        # Convert domain model to schema for infrastructure
        encounter_dict = {
            "combat_id": str(encounter.id),
            "name": encounter.name,
            "description": encounter.description,
            "status": encounter.status,
            "round_number": encounter.round_number,
            "current_turn": encounter.current_turn,
            "participants": [self._combatant_to_dict(p) for p in encounter.participants],
            "initiative_order": [self._combatant_to_dict(p) for p in encounter.initiative_order],
            "started_at": encounter.started_at,
            "ended_at": encounter.ended_at,
            "properties": encounter.properties
        }
        
        schema = CombatStateSchema(**encounter_dict)
        result = self.infrastructure_repo.create_combat(schema.dict())
        return self._schema_to_encounter(result)
    
    def get_encounter_by_id(self, encounter_id: UUID) -> Optional[CombatEncounter]:
        """Get encounter by ID"""
        result = self.infrastructure_repo.get_combat_by_id(str(encounter_id))
        if not result:
            return None
        return self._schema_to_encounter(result)
    
    def update_encounter(self, encounter: CombatEncounter) -> CombatEncounter:
        """Update existing encounter"""
        encounter_dict = {
            "combat_id": str(encounter.id),
            "name": encounter.name,
            "description": encounter.description,
            "status": encounter.status,
            "round_number": encounter.round_number,
            "current_turn": encounter.current_turn,
            "participants": [self._combatant_to_dict(p) for p in encounter.participants],
            "initiative_order": [self._combatant_to_dict(p) for p in encounter.initiative_order],
            "started_at": encounter.started_at,
            "ended_at": encounter.ended_at,
            "properties": encounter.properties
        }
        
        schema = CombatStateSchema(**encounter_dict)
        result = self.infrastructure_repo.update_combat(str(encounter.id), schema)
        return self._schema_to_encounter(result)
    
    def delete_encounter(self, encounter_id: UUID) -> bool:
        """Delete encounter"""
        return self.infrastructure_repo.delete_combat(str(encounter_id))
    
    def list_encounters(self, page: int = 1, size: int = 50, status: Optional[str] = None):
        """List encounters with pagination"""
        all_combats = self.infrastructure_repo.list_all_combats()
        
        # Filter by status if provided
        if status:
            all_combats = [c for c in all_combats if c.status == status]
        
        # Simple pagination
        start = (page - 1) * size
        end = start + size
        combats_page = all_combats[start:end]
        
        encounters = [self._schema_to_encounter(c) for c in combats_page]
        return encounters, len(all_combats)
    
    def _combatant_to_dict(self, combatant: Combatant) -> Dict[str, Any]:
        """Convert domain Combatant to dictionary"""
        return {
            "id": str(combatant.id),
            "character_id": str(combatant.character_id) if combatant.character_id else None,
            "name": combatant.name,
            "team": combatant.team,
            "combatant_type": combatant.combatant_type,
            "current_hp": combatant.current_hp,
            "max_hp": combatant.max_hp,
            "armor_class": combatant.armor_class,
            "initiative": combatant.initiative,
            "dex_modifier": combatant.dex_modifier,
            "is_active": combatant.is_active,
            "is_conscious": combatant.is_conscious,
            "position": combatant.position,
            "status_effects": [self._status_effect_to_dict(se) for se in combatant.status_effects],
            "has_used_standard_action": combatant.has_used_standard_action,
            "has_used_bonus_action": combatant.has_used_bonus_action,
            "has_used_reaction": combatant.has_used_reaction,
            "remaining_movement": combatant.remaining_movement,
            "equipped_weapons": combatant.equipped_weapons,
            "equipped_armor": combatant.equipped_armor,
            "available_spells": combatant.available_spells,
            "class_features": combatant.class_features,
            "properties": combatant.properties
        }
    
    def _status_effect_to_dict(self, effect: StatusEffect) -> Dict[str, Any]:
        """Convert domain StatusEffect to dictionary"""
        return {
            "id": str(effect.id),
            "name": effect.name,
            "description": effect.description,
            "duration": effect.duration,
            "category": effect.category,
            "stackable": effect.stackable,
            "dispellable": effect.dispellable,
            "source_id": str(effect.source_id) if effect.source_id else None,
            "combatant_id": str(effect.combatant_id) if effect.combatant_id else None
        }
    
    def _schema_to_encounter(self, schema: CombatStateSchema) -> CombatEncounter:
        """Convert schema to domain CombatEncounter"""
        # This is a simplified conversion - in a real implementation,
        # you'd need to properly reconstruct all domain objects
        encounter = CombatEncounter(
            id=UUID(schema.combat_id),
            name=schema.name,
            description=schema.description,
            status=schema.status,
            round_number=schema.round_number,
            current_turn=schema.current_turn,
            started_at=schema.started_at,
            ended_at=schema.ended_at,
            properties=schema.properties or {}
        )
        
        # Convert participants
        for p_dict in schema.participants:
            combatant = Combatant(
                id=UUID(p_dict.id),
                character_id=UUID(p_dict.character_id) if p_dict.character_id else None,
                name=p_dict.name,
                team=p_dict.team,
                combatant_type=p_dict.combatant_type,
                current_hp=p_dict.current_hp,
                max_hp=p_dict.max_hp,
                armor_class=p_dict.armor_class,
                initiative=p_dict.initiative,
                dex_modifier=p_dict.dex_modifier,
                is_active=p_dict.is_active,
                is_conscious=p_dict.is_conscious,
                position=p_dict.position,
                has_used_standard_action=p_dict.has_used_standard_action,
                has_used_bonus_action=p_dict.has_used_bonus_action,
                has_used_reaction=p_dict.has_used_reaction,
                remaining_movement=p_dict.remaining_movement,
                equipped_weapons=p_dict.equipped_weapons,
                equipped_armor=p_dict.equipped_armor,
                available_spells=p_dict.available_spells,
                class_features=p_dict.class_features,
                properties=p_dict.properties or {}
            )
            encounter.add_participant(combatant)
        
        return encounter


# Mock implementations for missing dependencies
class MockActionDefinitionRepository:
    def get_action_by_id(self, action_id: str):
        return None
    
    def get_actions_for_combatant(self, combatant):
        return []
    
    def list_all_actions(self):
        return []


class MockDiceRollingService:
    def roll_d20(self) -> int:
        import random
        return random.randint(1, 20)
    
    def roll_dice(self, count: int, sides: int) -> List[int]:
        import random
        return [random.randint(1, sides) for _ in range(count)]
    
    def roll_damage(self, damage_expr: str) -> int:
        # Simple implementation
        import random
        return random.randint(1, 6)


class CombatInfrastructureService:
    """
    Infrastructure facade for the combat system that bridges domain services with API layer.
    Uses the proper domain-driven CombatService for business logic.
    """
    
    def __init__(self):
        # Initialize the domain service with proper dependencies
        self.repository = CombatBusinessRepository(combat_repository)
        self.action_repository = MockActionDefinitionRepository()
        self.dice_service = MockDiceRollingService()
        
        # Create the domain service
        self.domain_service = CombatService(
            self.repository,
            self.action_repository,
            self.dice_service
        )

    def create_new_combat_instance(self, initial_combat_data: Optional[Dict] = None) -> CombatStateSchema:
        """Creates a new combat instance using domain service."""
        name = "Combat Encounter"
        description = None
        properties = {}
        
        if initial_combat_data:
            name = initial_combat_data.get("name", name)
            description = initial_combat_data.get("description", description)
            properties = initial_combat_data.get("properties", properties)
        
        # Use domain service to create encounter
        encounter = self.domain_service.create_encounter(name, description, properties)
        
        # Convert back to schema
        return self._encounter_to_schema(encounter)

    def get_combat_state(self, combat_id: str) -> Optional[CombatStateSchema]:
        """Retrieves the current state of a specific combat instance."""
        try:
            encounter_id = UUID(combat_id)
            encounter = self.domain_service.get_encounter_by_id(encounter_id)
            if not encounter:
                return None
            return self._encounter_to_schema(encounter)
        except ValueError:
            return None

    def update_combat_state(self, combat_id: str, combat_data_update: CombatStateSchema) -> Optional[CombatStateSchema]:
        """Updates an existing combat instance using domain service."""
        # For now, just return the updated data - full implementation would use domain service
        return combat_data_update

    def end_combat_instance(self, combat_id: str) -> bool:
        """Ends a combat instance using domain service."""
        try:
            encounter_id = UUID(combat_id)
            encounter = self.domain_service.get_encounter_by_id(encounter_id)
            if not encounter:
                return False
            
            # Use domain service to end combat
            self.domain_service.end_combat(encounter_id, "manually_ended")
            return True
        except ValueError:
            return False
    
    def list_all_combat_instances(self) -> List[CombatStateSchema]:
        """Lists all current combat instances using domain service."""
        encounters, _ = self.repository.list_encounters()
        return [self._encounter_to_schema(e) for e in encounters]
    
    def add_combatant_to_encounter(self, combat_id: str, combatant_data: AddCombatantRequest) -> Optional[CombatStateSchema]:
        """Add combatant to encounter using domain service."""
        try:
            encounter_id = UUID(combat_id)
            
            # Create domain Combatant
            combatant = Combatant(
                id=uuid4(),
                character_id=UUID(combatant_data.character_id) if combatant_data.character_id else None,
                name=combatant_data.name,
                team=combatant_data.team,
                combatant_type=combatant_data.combatant_type,
                current_hp=combatant_data.current_hp,
                max_hp=combatant_data.max_hp,
                armor_class=combatant_data.armor_class,
                dex_modifier=combatant_data.dex_modifier,
                equipped_weapons=combatant_data.equipped_weapons,
                available_spells=combatant_data.available_spells,
                class_features=combatant_data.class_features
            )
            
            # Use domain service
            encounter = self.domain_service.add_combatant_to_encounter(encounter_id, combatant)
            return self._encounter_to_schema(encounter)
            
        except ValueError:
            return None
    
    def _encounter_to_schema(self, encounter: CombatEncounter) -> CombatStateSchema:
        """Convert domain CombatEncounter to schema"""
        return CombatStateSchema(
            combat_id=str(encounter.id),
            name=encounter.name,
            description=encounter.description,
            status=encounter.status,
            round_number=encounter.round_number,
            current_turn=encounter.current_turn,
            participants=[self._combatant_to_schema(p) for p in encounter.participants],
            initiative_order=[self._combatant_to_schema(p) for p in encounter.initiative_order],
            combat_log=[],  # Would need proper conversion
            actions_taken=[],  # Would need proper conversion  
            started_at=encounter.started_at,
            ended_at=encounter.ended_at,
            properties=encounter.properties
        )
    
    def _combatant_to_schema(self, combatant: Combatant) -> CombatantSchema:
        """Convert domain Combatant to schema"""
        return CombatantSchema(
            id=str(combatant.id),
            character_id=str(combatant.character_id) if combatant.character_id else None,
            name=combatant.name,
            team=combatant.team,
            combatant_type=combatant.combatant_type,
            current_hp=combatant.current_hp,
            max_hp=combatant.max_hp,
            armor_class=combatant.armor_class,
            initiative=combatant.initiative,
            dex_modifier=combatant.dex_modifier,
            is_active=combatant.is_active,
            is_conscious=combatant.is_conscious,
            position=combatant.position,
            status_effects=[],  # Would need proper conversion
            has_used_standard_action=combatant.has_used_standard_action,
            has_used_bonus_action=combatant.has_used_bonus_action,
            has_used_reaction=combatant.has_used_reaction,
            remaining_movement=combatant.remaining_movement,
            equipped_weapons=combatant.equipped_weapons,
            equipped_armor=combatant.equipped_armor,
            available_spells=combatant.available_spells,
            class_features=combatant.class_features,
            properties=combatant.properties
        )


# Singleton instance of the consolidated service
combat_service = CombatInfrastructureService() 