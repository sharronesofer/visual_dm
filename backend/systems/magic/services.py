"""
Magic system services.

This module contains the business logic for the magic system,
including spell casting, magic abilities, and related services.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from .models import (
    MagicModel, SpellModel, SpellSlot, SpellSchool, 
    Spellbook, SpellComponent, SpellEffect
)
from .repositories import (
    MagicRepository, SpellRepository, SpellEffectRepository, 
    SpellbookRepository, SpellSlotRepository
)
from .utils import (
    calculate_spell_power, validate_spell_requirements,
    check_spell_compatibility, can_cast_spell,
    apply_spell_effect, calculate_spell_duration
)
from backend.systems.events import EventDispatcher, EventBase

# Define magic system events
class MagicAbilityEvent(EventBase):
    """Event for magic ability activation"""
    ability_id: int
    caster_id: int
    target_id: int
    target_type: str
    success: bool
    data: Dict[str, Any]

class SpellCastEvent(EventBase):
    """Event for spell casting"""
    spell_id: int
    caster_id: int
    target_id: int
    target_type: str
    effect_id: Optional[int]
    success: bool
    data: Dict[str, Any]

class SpellbookEvent(EventBase):
    """Event for spellbook actions"""
    spellbook_id: int
    owner_id: int
    owner_type: str
    data: Dict[str, Any]

class SpellSlotEvent(EventBase):
    """Event for spell slot actions"""
    owner_id: int
    owner_type: str
    level: int
    count: int
    data: Dict[str, Any]

class SpellEffectEvent(EventBase):
    """Event for spell effects"""
    effect_id: int
    spell_id: int
    target_id: int
    target_type: str
    data: Dict[str, Any]

class MagicService:
    """
    Core service for the magic system.
    
    This service orchestrates the magic system and provides
    access to all related subservices.
    """
    
    def __init__(self, db_session):
        """Initialize the service with database session."""
        self.repository = MagicRepository(db_session)
        self.spell_service = SpellService(db_session)
        self.spellbook_service = SpellbookService(db_session)
        self.spell_effect_service = SpellEffectService(db_session)
        self.spell_slot_service = SpellSlotService(db_session)
        self.event_dispatcher = EventDispatcher.get_instance()
        self.db_session = db_session
    
    def process_magic_tick(self) -> Dict[str, Any]:
        """
        Process a magic system tick.
        
        This function should be called regularly (e.g., each game day)
        to update magical effects, refresh spell slots, etc.
        
        Returns:
            Dict[str, Any]: Summary of what happened during the tick
        """
        # Process any ongoing effects (reduce duration, end expired effects)
        ended_effects = self.spell_effect_service.update_effect_durations()
        
        # Return summary of the tick
        return {
            'ended_effects_count': ended_effects
        }
    
    def refresh_character_spell_slots(self, character_id: int) -> int:
        """
        Refresh all spell slots for a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            int: Number of slots refreshed
        """
        return self.spell_slot_service.refresh_slots("character", character_id)
    
    def generate_spell_slots(self, character_id: int, 
                           level_counts: Dict[int, int]) -> Dict[int, int]:
        """
        Generate spell slots for a character based on level counts.
        
        Args:
            character_id: ID of the character
            level_counts: Dictionary mapping spell level to count
                        (e.g., {1: 4, 2: 3, 3: 2})
            
        Returns:
            Dict[int, int]: Dictionary mapping levels to counts of created slots
        """
        result = {}
        
        for level, count in level_counts.items():
            slots = self.spell_slot_service.create_slots("character", character_id, level, count)
            result[level] = len(slots)
        
        return result
    
    def create_magic_ability(self, data: Dict[str, Any]) -> MagicModel:
        """
        Create a new magic ability.
        
        Args:
            data: Dictionary containing magic ability data
            
        Returns:
            MagicModel: The created magic ability
        """
        magic_ability = self.repository.create(data)
        
        # Emit event
        self.event_dispatcher.publish_sync(MagicAbilityEvent(
            event_type="magic.ability.created",
            ability_id=magic_ability.id,
            caster_id=data.get('owner_id'),
            target_id=0,
            target_type="none",
            success=True,
            data=magic_ability.to_dict()
        ))
        
        return magic_ability
    
    def get_magic_ability(self, ability_id: int) -> Optional[MagicModel]:
        """
        Get a magic ability by ID.
        
        Args:
            ability_id: ID of the magic ability
            
        Returns:
            Optional[MagicModel]: The ability if found, None otherwise
        """
        return self.repository.get_by_id(ability_id)
    
    def update_magic_ability(self, ability_id: int, data: Dict[str, Any]) -> Optional[MagicModel]:
        """
        Update a magic ability.
        
        Args:
            ability_id: ID of the magic ability
            data: Dictionary containing updated magic ability data
            
        Returns:
            Optional[MagicModel]: The updated ability if found, None otherwise
        """
        updated_ability = self.repository.update(ability_id, data)
        
        if updated_ability:
            # Emit event
            self.event_dispatcher.publish_sync(MagicAbilityEvent(
                event_type="magic.ability.updated",
                ability_id=updated_ability.id,
                caster_id=updated_ability.owner_id or 0,
                target_id=0,
                target_type="none",
                success=True,
                data=updated_ability.to_dict()
            ))
        
        return updated_ability
    
    def delete_magic_ability(self, ability_id: int) -> bool:
        """
        Delete a magic ability.
        
        Args:
            ability_id: ID of the magic ability
            
        Returns:
            bool: True if deleted, False otherwise
        """
        # Get ability before deletion for event data
        ability = self.repository.get_by_id(ability_id)
        if not ability:
            return False
            
        ability_data = ability.to_dict()
        success = self.repository.delete(ability_id)
        
        if success:
            # Emit event
            self.event_dispatcher.publish_sync(MagicAbilityEvent(
                event_type="magic.ability.deleted",
                ability_id=ability_id,
                caster_id=ability_data.get('owner_id', 0),
                target_id=0,
                target_type="none",
                success=True,
                data=ability_data
            ))
        
        return success
    
    def use_magic_ability(self, ability_id: int, user_id: int, 
                        target_id: int, target_type: str) -> bool:
        """
        Use a magic ability on a target.
        
        Args:
            ability_id: ID of the magic ability
            user_id: ID of the user using the ability
            target_id: ID of the target
            target_type: Type of the target
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get the ability
        ability = self.repository.get_by_id(ability_id)
        if not ability:
            return False
        
        # Check if the user has this ability
        # This would be a more complex check in a real implementation
        if ability.owner_id != user_id:
            return False
        
        # Apply the ability effects
        # This would interact with other systems based on ability type
        
        # Emit event
        self.event_dispatcher.publish_sync(MagicAbilityEvent(
            event_type="magic.ability.used",
            ability_id=ability_id,
            caster_id=user_id,
            target_id=target_id,
            target_type=target_type,
            success=True,
            data={
                "user_id": user_id,
                "target_id": target_id,
                "target_type": target_type,
                "ability": ability.to_dict()
            }
        ))
        
        return True
    
    def discover_random_spell(self, character_id: int, location_id: int = 0) -> Optional[SpellModel]:
        """
        Discover a random spell for a character based on location or other factors.
        
        Args:
            character_id: ID of the character
            location_id: Optional location ID to influence discovery
            
        Returns:
            Optional[SpellModel]: The discovered spell if successful, None otherwise
        """
        # Build discovery conditions
        conditions = {
            'location_id': location_id,
            'timestamp': datetime.utcnow().isoformat(),
            'character_id': character_id
        }
        
        # Use the spell service's discover_spell method
        return self.spell_service.discover_spell(character_id, conditions)
    
    def analyze_magical_influences(self, location_id: int) -> Dict[str, Any]:
        """
        Analyze magical influences at a location.
        
        Args:
            location_id: ID of the location
            
        Returns:
            Dict[str, Any]: Analysis of magical influences
        """
        # This would be a complex analysis in a real implementation
        # For now, just a simple placeholder return
        
        # Check for active effects in the location
        # This would integrate with a location system
        
        return {
            'location_id': location_id,
            'magic_level': 3,  # 1-10 scale
            'dominant_school': 'arcane',
            'schools': {
                'arcane': 0.6,
                'fire': 0.2,
                'water': 0.1,
                'earth': 0.05,
                'air': 0.05
            },
            'anomalies': [],
            'magical_creatures': []
        }
    
    def get_character_magic_summary(self, character_id: int) -> Dict[str, Any]:
        """
        Get a summary of a character's magical abilities and resources.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dict[str, Any]: Summary of the character's magic
        """
        # Get the character's spellbook
        known_spells = self.spellbook_service.get_known_spells("character", character_id)
        
        # Get the character's spell slots
        slot_summary = self.spell_slot_service.get_slot_summary("character", character_id)
        
        # Get active effects on the character
        active_effects = self.spell_effect_service.get_active_effects("character", character_id)
        
        # Get the character's magic abilities
        abilities = self.repository.get_by_owner_id(character_id)
        
        return {
            'character_id': character_id,
            'known_spell_count': len(known_spells),
            'known_spells': [spell.to_dict() for spell in known_spells],
            'spell_slots': slot_summary,
            'active_effect_count': len(active_effects),
            'active_effects': [effect.to_dict() for effect in active_effects],
            'ability_count': len(abilities),
            'abilities': [ability.to_dict() for ability in abilities]
        }
    
    def cast_spell(self, spell_id: int, caster_id: int, target_id: int, 
                 target_type: str, additional_data: Optional[Dict[str, Any]] = None) -> Optional[SpellEffect]:
        """
        Cast a spell on a target.
        
        Args:
            spell_id: ID of the spell to cast
            caster_id: ID of the character casting the spell
            target_id: ID of the target
            target_type: Type of the target
            additional_data: Additional data for the spell cast
            
        Returns:
            Optional[SpellEffect]: The created spell effect if successful, None otherwise
        """
        # Use the spell service to handle the cast
        return self.spell_service.cast_spell(
            spell_id, caster_id, target_id, target_type, additional_data
        )


class SpellService:
    """
    Service for managing spells.
    
    This service handles the business logic for spells,
    including creation, casting, and modification.
    """
    
    def __init__(self, db_session):
        """Initialize the service with database session."""
        self.repository = SpellRepository(db_session)
        self.effect_repository = SpellEffectRepository(db_session)
        self.spellbook_repository = SpellbookRepository(db_session)
        self.slot_repository = SpellSlotRepository(db_session)
        self.event_dispatcher = EventDispatcher.get_instance()
    
    def create_spell(self, data: Dict[str, Any]) -> SpellModel:
        """
        Create a new spell.
        
        Args:
            data: Dictionary containing spell data
            
        Returns:
            SpellModel: The created spell
        """
        spell = self.repository.create(data)
        
        # Emit event
        self.event_dispatcher.publish_sync(SpellCastEvent(
            event_type="magic.spell.created",
            spell_id=spell.id,
            caster_id=data.get('owner_id'),
            target_id=0,
            target_type="none",
            effect_id=None,
            success=True,
            data=spell.to_dict()
        ))
        
        return spell
    
    def get_spell(self, spell_id: int) -> Optional[SpellModel]:
        """
        Get a spell by ID.
        
        Args:
            spell_id: ID of the spell
            
        Returns:
            Optional[SpellModel]: The spell if found, None otherwise
        """
        return self.repository.get_by_id(spell_id)
    
    def update_spell(self, spell_id: int, data: Dict[str, Any]) -> Optional[SpellModel]:
        """
        Update a spell.
        
        Args:
            spell_id: ID of the spell
            data: Dictionary containing updated spell data
            
        Returns:
            Optional[SpellModel]: The updated spell if found, None otherwise
        """
        updated_spell = self.repository.update(spell_id, data)
        
        if updated_spell:
            # Emit event
            self.event_dispatcher.publish_sync(SpellCastEvent(
                event_type="magic.spell.updated",
                spell_id=updated_spell.id,
                caster_id=updated_spell.owner_id or 0,
                target_id=0,
                target_type="none",
                effect_id=None,
                success=True,
                data=updated_spell.to_dict()
            ))
        
        return updated_spell
    
    def delete_spell(self, spell_id: int) -> bool:
        """
        Delete a spell.
        
        Args:
            spell_id: ID of the spell
            
        Returns:
            bool: True if deleted, False otherwise
        """
        # Get spell before deletion for event data
        spell = self.repository.get_by_id(spell_id)
        if not spell:
            return False
            
        spell_data = spell.to_dict()
        success = self.repository.delete(spell_id)
        
        if success:
            # Emit event
            self.event_dispatcher.publish_sync(SpellCastEvent(
                event_type="magic.spell.deleted",
                spell_id=spell_id,
                caster_id=spell_data.get('owner_id', 0),
                target_id=0,
                target_type="none",
                effect_id=None,
                success=True,
                data=spell_data
            ))
        
        return success
    
    def cast_spell(self, spell_id: int, caster_id: int, target_id: int, target_type: str, 
                  additional_data: Optional[Dict[str, Any]] = None) -> Optional[SpellEffect]:
        """
        Cast a spell on a target.
        
        Args:
            spell_id: ID of the spell to cast
            caster_id: ID of the character casting the spell
            target_id: ID of the target (character, NPC, etc.)
            target_type: Type of the target (character, npc, etc.)
            additional_data: Additional data for the spell cast
            
        Returns:
            Optional[SpellEffect]: The created spell effect if successful, None otherwise
        """
        # Get the spell
        spell = self.repository.get_by_id(spell_id)
        if not spell:
            # Emit failed cast event
            self._emit_cast_failure(spell_id, caster_id, target_id, target_type, "Spell not found")
            return None
        
        # Check if caster knows this spell
        spellbook = self.spellbook_repository.get_by_owner("character", caster_id)
        if not spellbook or not any(s.get('id') == spell_id for s in spellbook.spells.get('spells', [])):
            # Emit failed cast event
            self._emit_cast_failure(spell_id, caster_id, target_id, target_type, "Spell not in spellbook")
            return None
        
        # Check if caster has available spell slot
        has_slot, slot = self._check_spell_slot(caster_id, spell)
        if not has_slot:
            # Emit failed cast event
            self._emit_cast_failure(spell_id, caster_id, target_id, target_type, "No available spell slots")
            return None
        
        # Calculate spell effect details
        effect_data = self._calculate_spell_effect(spell, caster_id, target_id, target_type, additional_data)
        
        # Create the spell effect
        effect_model_data = {
            'spell_id': spell_id,
            'target_id': target_id,
            'target_type': target_type,
            'duration': effect_data.get('duration', 1),
            'remaining_duration': effect_data.get('duration', 1),
            'effects': effect_data
        }
        
        effect = self.effect_repository.create(effect_model_data)
        
        # Use up a spell slot
        if slot:
            self.slot_repository.use_slot(slot.id)
        
        # Apply the effect to the target (would integrate with other systems)
        # In a full implementation, this would update the target's state
        
        # Emit success event
        self.event_dispatcher.publish_sync(SpellCastEvent(
            event_type="magic.spell.cast",
            spell_id=spell_id,
            caster_id=caster_id,
            target_id=target_id,
            target_type=target_type,
            effect_id=effect.id,
            success=True,
            data={
                'spell': spell.to_dict(),
                'effect': effect.to_dict(),
                'additional_data': additional_data or {}
            }
        ))
        
        return effect
    
    def _check_spell_slot(self, caster_id: int, spell: SpellModel) -> Tuple[bool, Optional[SpellSlot]]:
        """
        Check if caster has an available spell slot.
        
        Args:
            caster_id: ID of the caster
            spell: The spell model
            
        Returns:
            Tuple[bool, Optional[SpellSlot]]: (True, slot) if available, (False, None) otherwise
        """
        # Get spell level from requirements or default to 1
        spell_level = spell.requirements.get('level', 1)
        
        # Get available slots for this level
        slots = self.slot_repository.get_available_slots("character", caster_id, spell_level)
        
        if not slots:
            return False, None
            
        return True, slots[0]
    
    def _calculate_spell_effect(self, spell: SpellModel, caster_id: int, target_id: int, 
                              target_type: str, additional_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate the effect of a spell cast.
        
        Args:
            spell: The spell model
            caster_id: ID of the caster
            target_id: ID of the target
            target_type: Type of the target
            additional_data: Additional data for calculations
            
        Returns:
            Dict[str, Any]: Calculated effect data
        """
        # Base effects from spell definition
        effect = spell.effects.copy() if spell.effects else {}
        
        # Add basic data
        effect['spell_id'] = spell.id
        effect['spell_name'] = spell.name
        effect['caster_id'] = caster_id
        effect['cast_time'] = datetime.utcnow().isoformat()
        
        # Calculate power based on spell school
        power = spell.power
        if spell.school.value == 'fire':
            # Fire spells do more damage but have shorter duration
            effect['damage_modifier'] = 1.3
            effect['duration_modifier'] = 0.8
        elif spell.school.value == 'water':
            # Water spells have control effects
            effect['control_modifier'] = 1.2
            effect['area_of_effect'] = effect.get('area_of_effect', 0) + 5
        elif spell.school.value == 'earth':
            # Earth spells are more durable
            effect['durability_modifier'] = 1.4
            effect['resistance_modifier'] = 1.2
        elif spell.school.value == 'air':
            # Air spells are faster and have greater range
            effect['speed_modifier'] = 1.3
            effect['range_modifier'] = 1.5
        elif spell.school.value == 'arcane':
            # Arcane spells have special effects
            effect['arcane_modifier'] = 1.25
            effect['special_effect'] = effect.get('special_effect', '') + " (Arcane Resonance)"
        elif spell.school.value == 'divine':
            # Divine spells heal better
            effect['healing_modifier'] = 1.5
            effect['holy_damage'] = effect.get('holy_damage', 0) + 5
        
        # Calculate duration
        base_duration = effect.get('duration', 3)
        duration_modifier = effect.get('duration_modifier', 1.0)
        effect['duration'] = int(base_duration * duration_modifier)
        
        # Store target info
        effect['target_id'] = target_id
        effect['target_type'] = target_type
        
        # Process any additional data
        if additional_data:
            for key, value in additional_data.items():
                if key not in effect:  # Don't overwrite existing effects
                    effect[key] = value
        
        return effect
    
    def _emit_cast_failure(self, spell_id: int, caster_id: int, target_id: int, 
                         target_type: str, reason: str):
        """
        Emit an event for a failed spell cast.
        
        Args:
            spell_id: ID of the spell
            caster_id: ID of the caster
            target_id: ID of the target
            target_type: Type of the target
            reason: Reason for failure
        """
        self.event_dispatcher.publish_sync(SpellCastEvent(
            event_type="magic.spell.cast_failed",
            spell_id=spell_id,
            caster_id=caster_id,
            target_id=target_id,
            target_type=target_type,
            effect_id=None,
            success=False,
            data={'reason': reason}
        ))
    
    def search_spells(self, name: Optional[str] = None, school: Optional[str] = None, 
                     min_level: Optional[int] = None, max_level: Optional[int] = None) -> List[SpellModel]:
        """
        Search for spells with filters.
        
        Args:
            name: Optional name filter (partial match)
            school: Optional school filter
            min_level: Optional minimum level filter
            max_level: Optional maximum level filter
            
        Returns:
            List[SpellModel]: List of matching spells
        """
        return self.repository.search(name, min_level, max_level, school)
    
    def discover_spell(self, character_id: int, conditions: Dict[str, Any]) -> Optional[SpellModel]:
        """
        Discover a new spell based on conditions.
        
        Args:
            character_id: ID of the character discovering the spell
            conditions: Dictionary of discovery conditions (location, event, etc.)
            
        Returns:
            Optional[SpellModel]: The discovered spell, or None if no discovery
        """
        # This is where we'd implement spell discovery logic
        # For example, based on location, events, or other conditions
        # For now, as a placeholder, we'll just get a random spell
        
        # Get spellbook
        spellbook = self.spellbook_repository.get_by_owner("character", character_id)
        if not spellbook:
            return None
            
        # Get all known spell IDs
        known_spell_ids = [s.get('id') for s in spellbook.spells.get('spells', [])]
        
        # Find a spell the character doesn't know yet
        # This is simplistic - a real implementation would use more complex criteria
        spells = self.repository.get_all(limit=100)
        for spell in spells:
            if spell.id not in known_spell_ids:
                # This is a new spell - let's "discover" it
                
                # Add to spellbook
                self.spellbook_repository.add_spell(spellbook.id, spell.id)
                
                # Emit discovery event
                self.event_dispatcher.publish_sync(SpellCastEvent(
                    event_type="magic.spell.discovered",
                    spell_id=spell.id,
                    caster_id=character_id,
                    target_id=0,
                    target_type="none",
                    effect_id=None,
                    success=True,
                    data={
                        'spell': spell.to_dict(),
                        'discovery_conditions': conditions
                    }
                ))
                
                return spell
                
        # No new spells to discover
        return None


class SpellbookService:
    """
    Service for managing spellbooks.
    
    This service handles operations related to spellbooks,
    including adding and removing spells.
    """
    
    def __init__(self, db_session):
        """Initialize the service with database session."""
        self.repository = SpellbookRepository(db_session)
        self.spell_repository = SpellRepository(db_session)
        self.event_dispatcher = EventDispatcher.get_instance()
    
    def get_spellbook(self, owner_type: str, owner_id: int) -> Optional[Spellbook]:
        """
        Get or create a spellbook for the specified owner.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            
        Returns:
            Optional[Spellbook]: The spellbook if found or created, None on error
        """
        # Try to get existing spellbook
        spellbook = self.repository.get_by_owner(owner_type, owner_id)
        
        # If it doesn't exist, create one
        if not spellbook:
            spellbook_data = {
                'owner_type': owner_type,
                'owner_id': owner_id,
                'spells': {'spells': []}  # Empty spells list
            }
            spellbook = self.repository.create(spellbook_data)
            
            # Emit event for new spellbook
            self.event_dispatcher.publish_sync(SpellbookEvent(
                event_type="magic.spellbook.created",
                spellbook_id=spellbook.id,
                owner_id=owner_id,
                owner_type=owner_type,
                data=spellbook.to_dict()
            ))
        
        return spellbook
    
    def add_spell(self, owner_type: str, owner_id: int, spell_id: int) -> bool:
        """
        Add a spell to a spellbook.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            spell_id: ID of the spell to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get or create spellbook
        spellbook = self.get_spellbook(owner_type, owner_id)
        if not spellbook:
            return False
        
        # Check if spell exists
        spell = self.spell_repository.get_by_id(spell_id)
        if not spell:
            return False
        
        # Add spell to spellbook
        success = self.repository.add_spell(spellbook.id, spell_id)
        
        if success:
            # Emit event
            self.event_dispatcher.publish_sync(SpellbookEvent(
                event_type="magic.spellbook.spell_added",
                spellbook_id=spellbook.id,
                owner_id=owner_id,
                owner_type=owner_type,
                data={
                    'spell': spell.to_dict(),
                    'spellbook': self.repository.get_by_id(spellbook.id).to_dict()
                }
            ))
        
        return success
    
    def remove_spell(self, owner_type: str, owner_id: int, spell_id: int) -> bool:
        """
        Remove a spell from a spellbook.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            spell_id: ID of the spell to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get spellbook
        spellbook = self.repository.get_by_owner(owner_type, owner_id)
        if not spellbook:
            return False
        
        # Check if spell exists
        spell = self.spell_repository.get_by_id(spell_id)
        if not spell:
            return False
        
        # Remove spell from spellbook
        success = self.repository.remove_spell(spellbook.id, spell_id)
        
        if success:
            # Emit event
            self.event_dispatcher.publish_sync(SpellbookEvent(
                event_type="magic.spellbook.spell_removed",
                spellbook_id=spellbook.id,
                owner_id=owner_id,
                owner_type=owner_type,
                data={
                    'spell_id': spell_id,
                    'spell_name': spell.name,
                    'spellbook': self.repository.get_by_id(spellbook.id).to_dict()
                }
            ))
        
        return success
    
    def get_known_spells(self, owner_type: str, owner_id: int) -> List[SpellModel]:
        """
        Get all spells known by an owner.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            
        Returns:
            List[SpellModel]: List of known spells
        """
        # Get spellbook
        spellbook = self.repository.get_by_owner(owner_type, owner_id)
        if not spellbook:
            return []
        
        # Get all spell IDs
        spell_ids = [s.get('id') for s in spellbook.spells.get('spells', [])]
        
        # Get all spells
        spells = []
        for spell_id in spell_ids:
            spell = self.spell_repository.get_by_id(spell_id)
            if spell:
                spells.append(spell)
        
        return spells
    
    def search_known_spells(self, owner_type: str, owner_id: int, filters: Dict[str, Any]) -> List[SpellModel]:
        """
        Search for spells known by an owner with filters.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            filters: Dictionary of search filters
            
        Returns:
            List[SpellModel]: List of matching spells
        """
        # Get all known spells
        all_spells = self.get_known_spells(owner_type, owner_id)
        
        # Apply filters
        filtered_spells = []
        for spell in all_spells:
            include = True
            
            # Filter by name
            if 'name' in filters and filters['name']:
                if filters['name'].lower() not in spell.name.lower():
                    include = False
            
            # Filter by school
            if 'school' in filters and filters['school']:
                if spell.school.value != filters['school']:
                    include = False
            
            # Filter by min level
            if 'min_level' in filters and filters['min_level']:
                if spell.requirements.get('level', 1) < filters['min_level']:
                    include = False
            
            # Filter by max level
            if 'max_level' in filters and filters['max_level']:
                if spell.requirements.get('level', 1) > filters['max_level']:
                    include = False
            
            # Filter by components
            if 'components' in filters and filters['components']:
                required_components = set(filters['components'])
                spell_components = set([c.value for c in spell.components])
                if not required_components.issubset(spell_components):
                    include = False
            
            if include:
                filtered_spells.append(spell)
        
        return filtered_spells
    
    def can_prepare_spell(self, owner_type: str, owner_id: int, spell_id: int) -> Tuple[bool, str]:
        """
        Check if a character can prepare a spell.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            spell_id: ID of the spell to check
            
        Returns:
            Tuple[bool, str]: (True, "") if can prepare, (False, reason) otherwise
        """
        # Get spellbook
        spellbook = self.repository.get_by_owner(owner_type, owner_id)
        if not spellbook:
            return False, "No spellbook found"
        
        # Check if spell exists
        spell = self.spell_repository.get_by_id(spell_id)
        if not spell:
            return False, "Spell not found"
        
        # Check if spell is in spellbook
        spell_ids = [s.get('id') for s in spellbook.spells.get('spells', [])]
        if spell_id not in spell_ids:
            return False, "Spell not in spellbook"
        
        # Here we would check any other conditions (e.g. character level, etc.)
        # This is a simplified implementation
        
        return True, ""


class SpellEffectService:
    """
    Service for managing spell effects.
    
    This service handles operations related to active spell effects,
    including creation, updating, and ending effects.
    """
    
    def __init__(self, db_session):
        """Initialize the service with database session."""
        self.repository = SpellEffectRepository(db_session)
        self.spell_repository = SpellRepository(db_session)
        self.event_dispatcher = EventDispatcher.get_instance()
    
    def get_effect(self, effect_id: int) -> Optional[SpellEffect]:
        """
        Get a spell effect by ID.
        
        Args:
            effect_id: ID of the effect
            
        Returns:
            Optional[SpellEffect]: The effect if found, None otherwise
        """
        return self.repository.get_by_id(effect_id)
    
    def get_active_effects(self, target_type: str, target_id: int) -> List[SpellEffect]:
        """
        Get active spell effects on a target.
        
        Args:
            target_type: Type of the target (character, npc, etc.)
            target_id: ID of the target
            
        Returns:
            List[SpellEffect]: List of active effects
        """
        return self.repository.get_active_effects(target_type, target_id)
    
    def update_effect_durations(self) -> int:
        """
        Update all active spell effect durations (tick down).
        Should be called on each game tick or time increment.
        
        Returns:
            int: Number of effects ended
        """
        # Get all active effects
        active_effects = self.repository.get_all_active()
        
        ended_count = 0
        
        # Process each effect
        for effect in active_effects:
            # Decrease duration
            remaining = effect.remaining_duration - 1
            
            # Update in repository
            if remaining <= 0:
                # End the effect
                ended = self.end_effect(effect.id)
                if ended:
                    ended_count += 1
            else:
                # Update remaining duration
                self.repository.update(effect.id, {'remaining_duration': remaining})
        
        return ended_count
    
    def end_effect(self, effect_id: int) -> bool:
        """
        End a spell effect early.
        
        Args:
            effect_id: ID of the effect
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get the effect
        effect = self.repository.get_by_id(effect_id)
        if not effect:
            return False
            
        # Store effect data for event
        effect_data = effect.to_dict()
        
        # End the effect in the repository
        success = self.repository.end_effect(effect_id)
        
        if success:
            # Emit event
            self.event_dispatcher.publish_sync(SpellEffectEvent(
                event_type="magic.spell_effect.ended",
                effect_id=effect_id,
                spell_id=effect.spell_id,
                target_id=effect.target_id,
                target_type=effect.target_type,
                data=effect_data
            ))
            
            # Apply any end-of-effect consequences
            self._apply_effect_end(effect)
        
        return success
    
    def create_effect(self, data: Dict[str, Any]) -> Optional[SpellEffect]:
        """
        Create a new spell effect.
        
        Args:
            data: Dictionary containing effect data
            
        Returns:
            Optional[SpellEffect]: The created effect if successful, None otherwise
        """
        # Get the spell for validation
        spell_id = data.get('spell_id')
        if not spell_id:
            return None
            
        spell = self.spell_repository.get_by_id(spell_id)
        if not spell:
            return None
        
        # Create the effect
        effect = self.repository.create(data)
        
        # Emit event
        self.event_dispatcher.publish_sync(SpellEffectEvent(
            event_type="magic.spell_effect.created",
            effect_id=effect.id,
            spell_id=spell_id,
            target_id=data.get('target_id', 0),
            target_type=data.get('target_type', 'none'),
            data=effect.to_dict()
        ))
        
        # Apply the immediate effect
        self._apply_effect_start(effect)
        
        return effect
    
    def update_effect(self, effect_id: int, data: Dict[str, Any]) -> Optional[SpellEffect]:
        """
        Update a spell effect.
        
        Args:
            effect_id: ID of the effect
            data: Dictionary containing updated effect data
            
        Returns:
            Optional[SpellEffect]: The updated effect if successful, None otherwise
        """
        # Get the current effect
        current_effect = self.repository.get_by_id(effect_id)
        if not current_effect:
            return None
        
        # Update the effect
        updated_effect = self.repository.update(effect_id, data)
        
        if updated_effect:
            # Emit event
            self.event_dispatcher.publish_sync(SpellEffectEvent(
                event_type="magic.spell_effect.updated",
                effect_id=effect_id,
                spell_id=updated_effect.spell_id,
                target_id=updated_effect.target_id,
                target_type=updated_effect.target_type,
                data=updated_effect.to_dict()
            ))
        
        return updated_effect
    
    def modify_effect_duration(self, effect_id: int, duration_change: int) -> Optional[SpellEffect]:
        """
        Modify the duration of a spell effect.
        
        Args:
            effect_id: ID of the effect
            duration_change: Amount to change duration (can be negative)
            
        Returns:
            Optional[SpellEffect]: The updated effect if successful, None otherwise
        """
        # Get the current effect
        effect = self.repository.get_by_id(effect_id)
        if not effect:
            return None
        
        # Calculate new duration
        new_duration = max(0, effect.remaining_duration + duration_change)
        
        if new_duration <= 0:
            # End the effect
            self.end_effect(effect_id)
            return None
        else:
            # Update the duration
            return self.update_effect(effect_id, {'remaining_duration': new_duration})
    
    def dispel_effect(self, effect_id: int, dispel_power: int) -> Tuple[bool, str]:
        """
        Attempt to dispel a spell effect.
        
        Args:
            effect_id: ID of the effect
            dispel_power: Power of the dispel attempt
            
        Returns:
            Tuple[bool, str]: (True, message) if successful, (False, reason) otherwise
        """
        # Get the current effect
        effect = self.repository.get_by_id(effect_id)
        if not effect:
            return False, "Effect not found"
        
        # Get the spell
        spell = self.spell_repository.get_by_id(effect.spell_id)
        if not spell:
            # If the spell doesn't exist, we'll still allow dispelling
            spell_power = 1
        else:
            spell_power = spell.power
        
        # Simple dispel mechanics: dispel succeeds if power >= spell power
        if dispel_power >= spell_power:
            success = self.end_effect(effect_id)
            if success:
                return True, f"Successfully dispelled effect (power {dispel_power} vs spell power {spell_power})"
            else:
                return False, "Failed to end effect in database"
        else:
            return False, f"Dispel power ({dispel_power}) was less than spell power ({spell_power})"
    
    def get_all_effects_by_spell(self, spell_id: int) -> List[SpellEffect]:
        """
        Get all active effects created by a specific spell.
        
        Args:
            spell_id: ID of the spell
            
        Returns:
            List[SpellEffect]: List of active effects
        """
        return self.repository.get_by_spell(spell_id)
    
    def _apply_effect_start(self, effect: SpellEffect) -> None:
        """
        Apply the immediate effects when a spell effect starts.
        
        Args:
            effect: The spell effect to apply
        """
        # This would interact with other systems based on the effect type
        # For now, it's just a placeholder
        
        # Example: If the effect has damage, we'd apply it to the target
        if effect.effects and 'damage' in effect.effects:
            damage = effect.effects['damage']
            # We would call into the combat system here
            # combat_service.apply_damage(effect.target_id, effect.target_type, damage)
            
            # Emit an event about the damage application
            self.event_dispatcher.publish_sync(SpellEffectEvent(
                event_type="magic.spell_effect.damage_applied",
                effect_id=effect.id,
                spell_id=effect.spell_id,
                target_id=effect.target_id,
                target_type=effect.target_type,
                data={
                    'damage': damage,
                    'effect': effect.to_dict()
                }
            ))
    
    def _apply_effect_end(self, effect: SpellEffect) -> None:
        """
        Apply any final effects when a spell effect ends.
        
        Args:
            effect: The spell effect that ended
        """
        # Similar to start, but applies end-of-effect consequences
        # This would interact with other systems based on the effect type
        
        # Example: If the effect has end_damage, we'd apply it when it ends
        if effect.effects and 'end_damage' in effect.effects:
            end_damage = effect.effects['end_damage']
            # We would call into the combat system here
            # combat_service.apply_damage(effect.target_id, effect.target_type, end_damage)
            
            # Emit an event about the end damage application
            self.event_dispatcher.publish_sync(SpellEffectEvent(
                event_type="magic.spell_effect.end_damage_applied",
                effect_id=effect.id,
                spell_id=effect.spell_id,
                target_id=effect.target_id,
                target_type=effect.target_type,
                data={
                    'end_damage': end_damage,
                    'effect': effect.to_dict()
                }
            ))


class SpellSlotService:
    """
    Service for managing spell slots.
    
    This service handles operations related to spell slots,
    including creation, consumption, and refreshing.
    """
    
    def __init__(self, db_session):
        """Initialize the service with database session."""
        self.repository = SpellSlotRepository(db_session)
        self.event_dispatcher = EventDispatcher.get_instance()
    
    def get_available_slots(self, owner_type: str, owner_id: int, level: Optional[int] = None) -> List[SpellSlot]:
        """
        Get available spell slots for an owner.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            level: Optional level filter
            
        Returns:
            List[SpellSlot]: List of available spell slots
        """
        return self.repository.get_available_slots(owner_type, owner_id, level)
    
    def create_slots(self, owner_type: str, owner_id: int, level: int, count: int) -> List[SpellSlot]:
        """
        Create new spell slots for an owner.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            level: Spell slot level
            count: Number of slots to create
            
        Returns:
            List[SpellSlot]: List of created spell slots
        """
        created_slots = []
        
        for _ in range(count):
            slot_data = {
                'owner_type': owner_type,
                'owner_id': owner_id,
                'level': level,
                'used': False
            }
            slot = self.repository.create(slot_data)
            created_slots.append(slot)
        
        # Emit event
        self.event_dispatcher.publish_sync(SpellSlotEvent(
            event_type="magic.spell_slot.created",
            owner_id=owner_id,
            owner_type=owner_type,
            level=level,
            count=count,
            data={
                'created_slots': [s.to_dict() for s in created_slots]
            }
        ))
        
        return created_slots
    
    def use_slot(self, slot_id: int) -> bool:
        """
        Use a spell slot.
        
        Args:
            slot_id: ID of the spell slot
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get slot before update for event data
        slot = self.repository.get_by_id(slot_id)
        if not slot:
            return False
        
        # Check if already used
        if slot.used:
            return False
        
        # Use the slot
        success = self.repository.use_slot(slot_id)
        
        if success:
            # Emit event
            self.event_dispatcher.publish_sync(SpellSlotEvent(
                event_type="magic.spell_slot.used",
                owner_id=slot.owner_id,
                owner_type=slot.owner_type,
                level=slot.level,
                count=1,
                data={
                    'slot_id': slot_id
                }
            ))
        
        return success
    
    def refresh_slots(self, owner_type: str, owner_id: int, level: Optional[int] = None) -> int:
        """
        Refresh all used spell slots for an owner.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            level: Optional level to refresh only slots of that level
            
        Returns:
            int: Number of slots refreshed
        """
        # Refresh the slots
        refreshed_count = self.repository.refresh_slots(owner_type, owner_id, level)
        
        if refreshed_count > 0:
            # Emit event
            self.event_dispatcher.publish_sync(SpellSlotEvent(
                event_type="magic.spell_slot.refreshed",
                owner_id=owner_id,
                owner_type=owner_type,
                level=level or 0,  # 0 means all levels
                count=refreshed_count,
                data={
                    'level_filter': level
                }
            ))
        
        return refreshed_count
    
    def get_slot_summary(self, owner_type: str, owner_id: int) -> Dict[int, Dict[str, int]]:
        """
        Get a summary of spell slots for an owner.
        
        Args:
            owner_type: Type of the owner (character, npc, etc.)
            owner_id: ID of the owner
            
        Returns:
            Dict[int, Dict[str, int]]: Dictionary with level as key and counts as value
                                     {1: {'total': 4, 'used': 2, 'available': 2}}
        """
        slots = self.repository.get_all_slots(owner_type, owner_id)
        
        # Create summary by level
        summary = {}
        for slot in slots:
            level = slot.level
            
            if level not in summary:
                summary[level] = {
                    'total': 0,
                    'used': 0,
                    'available': 0
                }
            
            summary[level]['total'] += 1
            
            if slot.used:
                summary[level]['used'] += 1
            else:
                summary[level]['available'] += 1
        
        return summary 