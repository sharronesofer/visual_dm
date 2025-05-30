"""
Event handlers and triggers for the quest system.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.models.quest_system import (
    Quest, QuestStage, QuestStatus, QuestType,
    QuestCondition, QuestReward, QuestWorldImpact
)
from app.core.services.quest_service import QuestService
from app.core.services.character_service import CharacterService
from app.core.services.inventory_service import InventoryService
from app.core.services.faction_service import FactionService
from app.core.services.world_state_service import WorldStateService
from app.core.events.base import EventHandler, GameEvent

class QuestEventHandler(EventHandler):
    """Handles quest-related game events."""
    
    def __init__(
        self,
        quest_service: QuestService,
        character_service: CharacterService,
        inventory_service: InventoryService,
        faction_service: FactionService,
        world_state_service: WorldStateService
    ):
        self.quest_service = quest_service
        self.character_service = character_service
        self.inventory_service = inventory_service
        self.faction_service = faction_service
        self.world_state_service = world_state_service
        
    def handle_event(self, event: GameEvent) -> None:
        """
        Handle a game event that might trigger quest updates.
        
        Args:
            event: The game event to process
        """
        # Map event types to their handlers
        handlers = {
            'ITEM_COLLECTED': self._handle_item_collection,
            'ENEMY_DEFEATED': self._handle_enemy_defeat,
            'LOCATION_VISITED': self._handle_location_visit,
            'NPC_INTERACTION': self._handle_npc_interaction,
            'SKILL_LEARNED': self._handle_skill_learned,
            'FACTION_REP_CHANGED': self._handle_faction_rep_change,
            'RESOURCE_GATHERED': self._handle_resource_gathering,
            'CRAFTING_COMPLETED': self._handle_crafting_completion,
            'QUEST_ACCEPTED': self._handle_quest_acceptance,
            'QUEST_ABANDONED': self._handle_quest_abandonment,
            'TIME_PASSED': self._handle_time_passage,
            'WORLD_STATE_CHANGED': self._handle_world_state_change
        }
        
        handler = handlers.get(event.type)
        if handler:
            handler(event.data)
            
    def _handle_item_collection(self, data: Dict[str, Any]) -> None:
        """
        Handle item collection events.
        
        Args:
            data: Event data including item_id, character_id, quantity
        """
        character_id = data['character_id']
        item_id = data['item_id']
        quantity = data.get('quantity', 1)
        
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            # Check if this item collection satisfies any quest conditions
            for condition in current_stage.conditions:
                if (condition.type == 'COLLECT_ITEM' and
                    condition.target_id == item_id and
                    not condition.is_completed):
                    
                    # Update progress
                    new_progress = condition.current_progress + quantity
                    if new_progress >= condition.required_amount:
                        condition.is_completed = True
                        condition.current_progress = condition.required_amount
                    else:
                        condition.current_progress = new_progress
                        
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
    def _handle_enemy_defeat(self, data: Dict[str, Any]) -> None:
        """
        Handle enemy defeat events.
        
        Args:
            data: Event data including enemy_id, character_id, location_id
        """
        character_id = data['character_id']
        enemy_id = data['enemy_id']
        location_id = data.get('location_id')
        
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            # Check defeat conditions
            for condition in current_stage.conditions:
                if condition.type == 'DEFEAT_ENEMY' and condition.target_id == enemy_id:
                    condition.current_progress += 1
                    if condition.current_progress >= condition.required_amount:
                        condition.is_completed = True
                        
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
    def _handle_location_visit(self, data: Dict[str, Any]) -> None:
        """
        Handle location visit events.
        
        Args:
            data: Event data including location_id, character_id
        """
        character_id = data['character_id']
        location_id = data['location_id']
        
        # Check for quests that require visiting this location
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            for condition in current_stage.conditions:
                if condition.type == 'VISIT_LOCATION' and condition.target_id == location_id:
                    condition.is_completed = True
                    
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
        # Check for new quests that become available at this location
        self.quest_service.check_location_quest_availability(character_id, location_id)
        
    def _handle_npc_interaction(self, data: Dict[str, Any]) -> None:
        """
        Handle NPC interaction events.
        
        Args:
            data: Event data including npc_id, character_id, interaction_type
        """
        character_id = data['character_id']
        npc_id = data['npc_id']
        interaction_type = data['interaction_type']
        
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            for condition in current_stage.conditions:
                if (condition.type == 'INTERACT_NPC' and
                    condition.target_id == npc_id and
                    condition.interaction_type == interaction_type):
                    condition.is_completed = True
                    
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
        # Check for new quests from this NPC
        self.quest_service.check_npc_quest_availability(character_id, npc_id)
        
    def _handle_skill_learned(self, data: Dict[str, Any]) -> None:
        """
        Handle skill learning events.
        
        Args:
            data: Event data including skill_id, character_id, level
        """
        character_id = data['character_id']
        skill_id = data['skill_id']
        skill_level = data.get('level', 1)
        
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            for condition in current_stage.conditions:
                if (condition.type == 'LEARN_SKILL' and
                    condition.target_id == skill_id and
                    skill_level >= condition.required_level):
                    condition.is_completed = True
                    
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
    def _handle_faction_rep_change(self, data: Dict[str, Any]) -> None:
        """
        Handle faction reputation change events.
        
        Args:
            data: Event data including faction_id, character_id, reputation_change
        """
        character_id = data['character_id']
        faction_id = data['faction_id']
        rep_change = data['reputation_change']
        
        # Update quest availability based on new reputation
        current_rep = self.faction_service.get_reputation(character_id, faction_id)
        self.quest_service.check_faction_quest_availability(character_id, faction_id, current_rep)
        
        # Check active quests for reputation requirements
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            for condition in current_stage.conditions:
                if (condition.type == 'FACTION_REP' and
                    condition.target_id == faction_id and
                    current_rep >= condition.required_amount):
                    condition.is_completed = True
                    
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
    def _handle_resource_gathering(self, data: Dict[str, Any]) -> None:
        """
        Handle resource gathering events.
        
        Args:
            data: Event data including resource_id, character_id, quantity
        """
        character_id = data['character_id']
        resource_id = data['resource_id']
        quantity = data.get('quantity', 1)
        
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            for condition in current_stage.conditions:
                if condition.type == 'GATHER_RESOURCE' and condition.target_id == resource_id:
                    condition.current_progress += quantity
                    if condition.current_progress >= condition.required_amount:
                        condition.is_completed = True
                        condition.current_progress = condition.required_amount
                        
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
    def _handle_crafting_completion(self, data: Dict[str, Any]) -> None:
        """
        Handle crafting completion events.
        
        Args:
            data: Event data including recipe_id, character_id, item_id
        """
        character_id = data['character_id']
        recipe_id = data['recipe_id']
        item_id = data['item_id']
        
        active_quests = self.quest_service.get_active_quests_for_character(character_id)
        
        for quest in active_quests:
            current_stage = self.quest_service.get_current_stage(quest.id)
            if not current_stage:
                continue
                
            for condition in current_stage.conditions:
                if (condition.type == 'CRAFT_ITEM' and
                    (condition.target_id == recipe_id or condition.target_id == item_id)):
                    condition.current_progress += 1
                    if condition.current_progress >= condition.required_amount:
                        condition.is_completed = True
                        
                    # Check if stage is completed
                    if all(c.is_completed for c in current_stage.conditions):
                        self.quest_service.complete_stage(quest.id, current_stage.id)
                        
    def _handle_quest_acceptance(self, data: Dict[str, Any]) -> None:
        """
        Handle quest acceptance events.
        
        Args:
            data: Event data including quest_id, character_id
        """
        character_id = data['character_id']
        quest_id = data['quest_id']
        
        # Initialize quest progress
        self.quest_service.initialize_quest_progress(character_id, quest_id)
        
        # Check for chain quest triggers
        self.quest_service.check_chain_quest_availability(character_id, quest_id)
        
    def _handle_quest_abandonment(self, data: Dict[str, Any]) -> None:
        """
        Handle quest abandonment events.
        
        Args:
            data: Event data including quest_id, character_id
        """
        character_id = data['character_id']
        quest_id = data['quest_id']
        
        # Clean up quest progress
        self.quest_service.clean_up_abandoned_quest(character_id, quest_id)
        
        # Update chain quest availability
        self.quest_service.check_chain_quest_availability(character_id, quest_id)
        
    def _handle_time_passage(self, data: Dict[str, Any]) -> None:
        """
        Handle time passage events.
        
        Args:
            data: Event data including time_passed, current_time
        """
        current_time = data['current_time']
        
        # Check for expired quests
        expired_quests = self.quest_service.get_expired_quests()
        for quest in expired_quests:
            self.quest_service.expire_quest(quest.id)
            
        # Check for repeatable quests ready to reset
        ready_quests = self.quest_service.get_repeatable_quests_ready()
        for quest in ready_quests:
            self.quest_service.reset_repeatable_quest(quest.id)
            
        # Check time-based quest availability
        self.quest_service.check_time_based_quest_availability(current_time)
        
    def _handle_world_state_change(self, data: Dict[str, Any]) -> None:
        """
        Handle world state change events.
        
        Args:
            data: Event data including state_key, new_value, old_value
        """
        state_key = data['state_key']
        new_value = data['new_value']
        
        # Check for quests that depend on this world state
        self.quest_service.check_world_state_quest_conditions(state_key, new_value)
        
        # Check for new quests that become available due to world state
        self.quest_service.check_world_state_quest_availability(state_key, new_value) 
