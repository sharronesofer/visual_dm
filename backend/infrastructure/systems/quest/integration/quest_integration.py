"""
Quest Integration Layer

Handles quest system integration with other game systems.
Updates quest progress based on game events.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.infrastructure.events import event_bus

# Updated imports for new quest system structure
from backend.systems.quest.services.services import QuestBusinessService
from backend.systems.quest.models import QuestData, QuestStatus
from backend.systems.quest.utils import QuestBusinessUtils

# Infrastructure imports
from backend.infrastructure.databases.quest_repository import QuestRepository
from backend.infrastructure.validation.quest_validation import QuestValidationService

logger = logging.getLogger(__name__)

class QuestIntegration:
    """Handles integration of quests with other game systems."""
    
    @staticmethod
    def register_event_handlers():
        """Register event handlers for quest integration."""
        # Register events the quest system should respond to
        event_bus.subscribe("npc:dialogue_completed", QuestIntegration.handle_dialogue_completed)
        event_bus.subscribe("player:item_acquired", QuestIntegration.handle_item_acquired)
        event_bus.subscribe("player:location_changed", QuestIntegration.handle_location_changed)
        event_bus.subscribe("world:time_changed", QuestIntegration.handle_time_changed)
        event_bus.subscribe("combat:enemy_defeated", QuestIntegration.handle_enemy_defeated)
        logger.info("Quest event handlers registered")
    
    @staticmethod
    async def handle_dialogue_completed(event_data: Dict[str, Any]):
        """
        Handle dialogue completion events.
        
        Args:
            event_data: Event data including player_id, npc_id, dialogue_id
        """
        try:
            # Lazy imports to prevent circular dependencies
            from backend.systems.npc import NPCManager
            from backend.systems.quest.utils.legacy.quest_utils import QuestUtils
            
            player_id = event_data.get("player_id")
            npc_id = event_data.get("npc_id")
            dialogue_id = event_data.get("dialogue_id")
            
            if not player_id or not npc_id or not dialogue_id:
                logger.warning("Missing required data in dialogue_completed event")
                return
            
            # Get active quests for the player
            player_quests = []
            quests = QuestUtils.get_all_quests(where=[
                ("player_id", "==", player_id),
                ("status", "in", ["pending", "active"])
            ])
            
            # Process each quest to check if the dialogue advances any step
            for quest in quests:
                # Check if any steps involve dialogue with this NPC
                updated = False
                steps = quest.get("steps", [])
                
                for i, step in enumerate(steps):
                    # Check if this step involves talking to the specific NPC and uses this dialogue
                    if (not step.get("completed", False) and 
                        step.get("type") == "dialogue" and 
                        step.get("target_npc_id") == npc_id and 
                        step.get("dialogue_id") == dialogue_id):
                        
                        # Mark the step as completed
                        step["completed"] = True
                        updated = True
                        
                        # Generate a journal entry
                        journal_entry = {
                            "player_id": player_id,
                            "quest_id": quest["id"],
                            "content": f"I spoke with {NPCManager.get_npc_name(npc_id)} about {step.get('description', 'something important')}.",
                        }
                        QuestUtils.create_journal_entry(journal_entry)
                
                # Update the quest if steps changed
                if updated:
                    # Check if all steps are completed
                    all_steps_completed = all(s.get("completed", False) for s in steps)
                    
                    if all_steps_completed:
                        # Mark quest as completed
                        quest["status"] = "completed"
                        quest["completed_at"] = datetime.utcnow().isoformat()
                        
                        # Publish completion event
                        event_bus.publish("quest:completed", {
                            "quest_id": quest["id"],
                            "player_id": player_id,
                            "title": quest.get("title"),
                            "rewards": quest.get("rewards", {})
                        })
                    
                    # Update the quest in the database
                    quest["updated_at"] = datetime.utcnow().isoformat()
                    quest["steps"] = steps
                    QuestUtils.update_quest(quest["id"], quest)
        
        except Exception as e:
            logger.error(f"Error handling dialogue completion: {str(e)}")
    
    @staticmethod
    async def handle_item_acquired(event_data: Dict[str, Any]):
        """
        Handle item acquisition events.
        
        Args:
            event_data: Event data including player_id, item_id, quantity
        """
        try:
            # Lazy imports to prevent circular dependencies
            from backend.systems.item import ItemManager
            from backend.systems.quest.utils.legacy.quest_utils import QuestUtils
            
            player_id = event_data.get("player_id")
            item_id = event_data.get("item_id")
            quantity = event_data.get("quantity", 1)
            
            if not player_id or not item_id:
                logger.warning("Missing required data in item_acquired event")
                return
            
            # Get active quests for the player
            quests = QuestUtils.get_all_quests(where=[
                ("player_id", "==", player_id),
                ("status", "in", ["pending", "active"])
            ])
            
            # Process each quest to check if the acquired item advances any step
            for quest in quests:
                # Check if any steps involve acquiring this item
                updated = False
                steps = quest.get("steps", [])
                
                for i, step in enumerate(steps):
                    # Check if this step involves collecting the specific item
                    if (not step.get("completed", False) and 
                        step.get("type") == "collect" and 
                        step.get("target_item_id") == item_id and
                        step.get("quantity", 1) <= quantity):
                        
                        # Mark the step as completed
                        step["completed"] = True
                        updated = True
                        
                        # Generate a journal entry
                        item_name = ItemManager.get_item_name(item_id)
                        journal_entry = {
                            "player_id": player_id,
                            "quest_id": quest["id"],
                            "content": f"I collected {quantity} {item_name}.",
                        }
                        QuestUtils.create_journal_entry(journal_entry)
                
                # Update the quest if steps changed
                if updated:
                    # Check if all steps are completed
                    all_steps_completed = all(s.get("completed", False) for s in steps)
                    
                    if all_steps_completed:
                        # Mark quest as completed
                        quest["status"] = "completed"
                        quest["completed_at"] = datetime.utcnow().isoformat()
                        
                        # Publish completion event
                        event_bus.publish("quest:completed", {
                            "quest_id": quest["id"],
                            "player_id": player_id,
                            "title": quest.get("title"),
                            "rewards": quest.get("rewards", {})
                        })
                    
                    # Update the quest in the database
                    quest["updated_at"] = datetime.utcnow().isoformat()
                    quest["steps"] = steps
                    QuestUtils.update_quest(quest["id"], quest)
        
        except Exception as e:
            logger.error(f"Error handling item acquisition: {str(e)}")
    
    @staticmethod
    async def handle_location_changed(event_data: Dict[str, Any]):
        """
        Handle location change events.
        
        Args:
            event_data: Event data including player_id, old_location, new_location
        """
        try:
            # Lazy imports to prevent circular dependencies
            from backend.systems.quest.utils.legacy.quest_utils import QuestUtils
            
            player_id = event_data.get("player_id")
            old_location = event_data.get("old_location")
            new_location = event_data.get("new_location")
            
            if not player_id or not new_location:
                logger.warning("Missing required data in location_changed event")
                return
            
            # Get active quests for the player
            quests = QuestUtils.get_all_quests(where=[
                ("player_id", "==", player_id),
                ("status", "in", ["pending", "active"])
            ])
            
            # Process each quest to check if the location change advances any step
            for quest in quests:
                # Check if any steps involve visiting this location
                updated = False
                steps = quest.get("steps", [])
                
                for i, step in enumerate(steps):
                    # Check if this step involves visiting the specific location
                    if (not step.get("completed", False) and 
                        step.get("type") == "visit" and 
                        step.get("target_location_id") == new_location):
                        
                        # Mark the step as completed
                        step["completed"] = True
                        updated = True
                        
                        # Generate a journal entry
                        journal_entry = {
                            "player_id": player_id,
                            "quest_id": quest["id"],
                            "content": f"I arrived at {new_location}.",
                        }
                        QuestUtils.create_journal_entry(journal_entry)
                
                # Update the quest if steps changed
                if updated:
                    # Check if all steps are completed
                    all_steps_completed = all(s.get("completed", False) for s in steps)
                    
                    if all_steps_completed:
                        # Mark quest as completed
                        quest["status"] = "completed"
                        quest["completed_at"] = datetime.utcnow().isoformat()
                        
                        # Publish completion event
                        event_bus.publish("quest:completed", {
                            "quest_id": quest["id"],
                            "player_id": player_id,
                            "title": quest.get("title"),
                            "rewards": quest.get("rewards", {})
                        })
                    
                    # Update the quest in the database
                    quest["updated_at"] = datetime.utcnow().isoformat()
                    quest["steps"] = steps
                    QuestUtils.update_quest(quest["id"], quest)
        
        except Exception as e:
            logger.error(f"Error handling location change: {str(e)}")
    
    @staticmethod
    async def handle_time_changed(event_data: Dict[str, Any]):
        """
        Handle time change events.
        
        Args:
            event_data: Event data including current_time, time_delta
        """
        try:
            # Lazy imports to prevent circular dependencies
            from backend.systems.quest.utils.legacy.quest_utils import QuestUtils
            
            current_time = event_data.get("current_time")
            time_delta = event_data.get("time_delta", 0)
            
            if not current_time:
                logger.warning("Missing required data in time_changed event")
                return
            
            # Get all active quests that might have time-based conditions
            quests = QuestUtils.get_all_quests(where=[
                ("status", "in", ["pending", "active"])
            ])
            
            # Process each quest to check for time-based updates
            for quest in quests:
                updated = False
                steps = quest.get("steps", [])
                
                for i, step in enumerate(steps):
                    # Check if this step has time-based conditions
                    if (not step.get("completed", False) and 
                        step.get("type") == "wait" and 
                        step.get("wait_until")):
                        
                        wait_until = step.get("wait_until")
                        if current_time >= wait_until:
                            # Mark the step as completed
                            step["completed"] = True
                            updated = True
                            
                            # Generate a journal entry
                            journal_entry = {
                                "player_id": quest.get("player_id"),
                                "quest_id": quest["id"],
                                "content": f"The waiting period has ended.",
                            }
                            QuestUtils.create_journal_entry(journal_entry)
                
                # Update the quest if steps changed
                if updated:
                    # Check if all steps are completed
                    all_steps_completed = all(s.get("completed", False) for s in steps)
                    
                    if all_steps_completed:
                        # Mark quest as completed
                        quest["status"] = "completed"
                        quest["completed_at"] = datetime.utcnow().isoformat()
                        
                        # Publish completion event
                        event_bus.publish("quest:completed", {
                            "quest_id": quest["id"],
                            "player_id": quest.get("player_id"),
                            "title": quest.get("title"),
                            "rewards": quest.get("rewards", {})
                        })
                    
                    # Update the quest in the database
                    quest["updated_at"] = datetime.utcnow().isoformat()
                    quest["steps"] = steps
                    QuestUtils.update_quest(quest["id"], quest)
        
        except Exception as e:
            logger.error(f"Error handling time change: {str(e)}")
    
    @staticmethod
    async def handle_enemy_defeated(event_data: Dict[str, Any]):
        """
        Handle enemy defeated events.
        
        Args:
            event_data: Event data including player_id, enemy_type, enemy_id, location
        """
        try:
            # Lazy imports to prevent circular dependencies
            from backend.systems.quest.utils.legacy.quest_utils import QuestUtils
            
            player_id = event_data.get("player_id")
            enemy_type = event_data.get("enemy_type")
            enemy_id = event_data.get("enemy_id")
            location = event_data.get("location")
            
            if not player_id or not enemy_type:
                logger.warning("Missing required data in enemy_defeated event")
                return
            
            # Get active quests for the player
            quests = QuestUtils.get_all_quests(where=[
                ("player_id", "==", player_id),
                ("status", "in", ["pending", "active"])
            ])
            
            # Process each quest to check if the enemy defeat advances any step
            for quest in quests:
                # Check if any steps involve defeating this type of enemy
                updated = False
                steps = quest.get("steps", [])
                
                for i, step in enumerate(steps):
                    # Check if this step involves killing the specific enemy type
                    if (not step.get("completed", False) and 
                        step.get("type") == "kill" and 
                        step.get("data", {}).get("enemy_type") == enemy_type):
                        
                        # Update kill count
                        current_count = step.get("data", {}).get("current_count", 0)
                        required_count = step.get("data", {}).get("quantity", 1)
                        new_count = current_count + 1
                        
                        step["data"]["current_count"] = new_count
                        
                        # Check if requirement is met
                        if new_count >= required_count:
                            step["completed"] = True
                            updated = True
                            
                            # Generate a journal entry
                            journal_entry = {
                                "player_id": player_id,
                                "quest_id": quest["id"],
                                "content": f"I defeated {new_count}/{required_count} {enemy_type}s.",
                            }
                            QuestUtils.create_journal_entry(journal_entry)
                
                # Update the quest if steps changed
                if updated:
                    # Check if all steps are completed
                    all_steps_completed = all(s.get("completed", False) for s in steps)
                    
                    if all_steps_completed:
                        # Mark quest as completed
                        quest["status"] = "completed"
                        quest["completed_at"] = datetime.utcnow().isoformat()
                        
                        # Publish completion event
                        event_bus.publish("quest:completed", {
                            "quest_id": quest["id"],
                            "player_id": player_id,
                            "title": quest.get("title"),
                            "rewards": quest.get("rewards", {})
                        })
                    
                    # Update the quest in the database
                    quest["updated_at"] = datetime.utcnow().isoformat()
                    quest["steps"] = steps
                    QuestUtils.update_quest(quest["id"], quest)
        
        except Exception as e:
            logger.error(f"Error handling enemy defeat: {str(e)}")
    
    @staticmethod
    def generate_quests_for_player(player_id: str, location_id: Optional[str] = None, count: int = 3) -> List[str]:
        """
        Generate quests for a player based on their current context.
        
        Args:
            player_id: ID of the player
            location_id: Current location of the player
            count: Number of quests to generate
            
        Returns:
            List of generated quest IDs
        """
        try:
            # Lazy imports to prevent circular dependencies
            from backend.systems.quest.services.generator import QuestGenerator
            
            quest_ids = []
            
            for _ in range(count):
                # Generate a quest using the quest generator
                quest = QuestGenerator.generate_quest(
                    player_id=player_id,
                    location_id=location_id
                )
                
                if quest:
                    quest_ids.append(quest.id)
            
            return quest_ids
        
        except Exception as e:
            logger.error(f"Error generating quests for player: {str(e)}")
            return [] 