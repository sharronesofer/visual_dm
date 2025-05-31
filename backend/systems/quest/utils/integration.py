"""
Quest system integration module.
Handles connections with other game systems.
"""

import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.infrastructure.events import EventBus
from backend.systems.npc import NPCManager
from backend.systems.world_state.utils.legacy.world_state_manager import WorldStateManager
from backend.systems.player import PlayerManager
from backend.systems.item import ItemManager
from backend.systems.quest.models import Quest, QuestStep
from backend.systems.quest.utils import QuestUtils, QuestValidator
from backend.systems.quest.generator import QuestGenerator
from backend.systems.arc.services.player_arc_manager import PlayerArcManager
from backend.systems.quest.npc_quests import NPCQuestManager

logger = logging.getLogger(__name__)
event_bus = EventBus()

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
        Handle player location change events.
        
        Args:
            event_data: Event data including player_id, location_id
        """
        try:
            player_id = event_data.get("player_id")
            location_id = event_data.get("location_id")
            
            if not player_id or not location_id:
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
                        step.get("target_location_id") == location_id):
                        
                        # Mark the step as completed
                        step["completed"] = True
                        updated = True
                        
                        # Generate a journal entry
                        location_name = WorldStateManager.get_location_name(location_id)
                        journal_entry = {
                            "player_id": player_id,
                            "quest_id": quest["id"],
                            "content": f"I arrived at {location_name}.",
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
        Handle game time change events.
        
        Args:
            event_data: Event data including new_time, day_cycle
        """
        try:
            new_time = event_data.get("new_time")
            day_cycle = event_data.get("day_cycle")  # dawn, day, dusk, night
            
            if not new_time or not day_cycle:
                logger.warning("Missing required data in time_changed event")
                return
                
            # Process time-dependent quests
            quests = QuestUtils.get_all_quests(where=[
                ("status", "in", ["pending", "active"]),
                ("time_dependent", "==", True)
            ])
            
            # Process each time-dependent quest
            for quest in quests:
                # Check if quest has time-specific steps
                updated = False
                steps = quest.get("steps", [])
                
                for i, step in enumerate(steps):
                    # Check for time-dependent steps not yet completed
                    if not step.get("completed", False) and step.get("time_requirement"):
                        req = step.get("time_requirement")
                        
                        # Check if current day cycle matches requirement
                        if day_cycle == req.get("day_cycle"):
                            step["completed"] = True
                            updated = True
                            
                            # Generate a journal entry for the player
                            player_id = quest.get("player_id")
                            if player_id:
                                journal_entry = {
                                    "player_id": player_id,
                                    "quest_id": quest["id"],
                                    "content": f"I completed a task during {day_cycle}.",
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
                        
                        # Publish completion event if there's a player
                        player_id = quest.get("player_id")
                        if player_id:
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
            
            # Generate random NPC quests (10% chance on day cycle change)
            if day_cycle == "dawn" and random.random() < 0.1:
                # Get active regions 
                active_regions = WorldStateManager.get_active_regions()
                
                for region_id in active_regions:
                    # Try to generate quests for each active region
                    NPCQuestManager.generate_npc_quests_for_region(region_id, 2)
                    
        except Exception as e:
            logger.error(f"Error handling time change: {str(e)}")
    
    @staticmethod
    async def handle_enemy_defeated(event_data: Dict[str, Any]):
        """
        Handle enemy defeat events.
        
        Args:
            event_data: Event data including player_id, enemy_id, enemy_type
        """
        try:
            player_id = event_data.get("player_id")
            enemy_id = event_data.get("enemy_id")
            enemy_type = event_data.get("enemy_type")
            
            if not player_id or not enemy_id:
                logger.warning("Missing required data in enemy_defeated event")
                return
            
            # Get active quests for the player
            quests = QuestUtils.get_all_quests(where=[
                ("player_id", "==", player_id),
                ("status", "in", ["pending", "active"])
            ])
            
            # Process each quest to check if defeating this enemy advances any step
            for quest in quests:
                # Check if any steps involve defeating this enemy
                updated = False
                steps = quest.get("steps", [])
                
                for i, step in enumerate(steps):
                    # Check if this step involves defeating this specific enemy or enemy type
                    if not step.get("completed", False) and step.get("type") == "kill":
                        # Check for specific enemy ID match
                        if step.get("target_enemy_id") == enemy_id:
                            step["completed"] = True
                            updated = True
                        # Or check for enemy type match
                        elif step.get("target_enemy_type") == enemy_type:
                            # For enemy types, we might need to track counts
                            if "current_count" not in step:
                                step["current_count"] = 0
                                
                            step["current_count"] += 1
                            
                            # Check if we've reached the required count
                            if step["current_count"] >= step.get("required_count", 1):
                                step["completed"] = True
                                updated = True
                        
                        if updated:
                            # Generate a journal entry
                            enemy_name = enemy_type.capitalize()  # Better to get actual name if available
                            journal_entry = {
                                "player_id": player_id,
                                "quest_id": quest["id"],
                                "content": f"I defeated a {enemy_name}.",
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
        Generate quests for a player at a specific location.
        
        Args:
            player_id: Player ID
            location_id: Location ID (optional)
            count: Number of quests to generate
            
        Returns:
            List[str]: List of generated quest IDs
        """
        try:
            # Validate player ID
            QuestValidator.validate_player_id(player_id)
            
            # Get player data
            player_data = PlayerManager.get_player(player_id)
            if not player_data:
                logger.warning(f"Player {player_id} not found")
                return []
                
            # Get location if not provided
            if not location_id:
                location_id = player_data.get("location_id")
                if not location_id:
                    logger.warning(f"No location found for player {player_id}")
                    return []
            
            # Get location data
            location_data = WorldStateManager.get_location(location_id)
            if not location_data:
                logger.warning(f"Location {location_id} not found")
                return []
            
            # Generate quests
            quest_ids = []
            
            # 1. Check for NPC quests in the area
            npcs = NPCManager.get_npcs_in_location(location_id)
            if npcs:
                # Filter NPCs with available quests
                quest_giving_npcs = []
                for npc in npcs:
                    # Only NPCs with some importance might give quests
                    if npc.get("importance", 0) >= 2:
                        npc_quests = NPCQuestManager.get_npc_quests(npc["id"])
                        available_quests = [q for q in npc_quests if q.get("status") == "pending"]
                        
                        if available_quests:
                            quest_giving_npcs.append((npc, available_quests))
                
                # Assign up to half of the requested quests from NPCs
                npc_quest_count = min(len(quest_giving_npcs), count // 2)
                
                for i in range(npc_quest_count):
                    if not quest_giving_npcs:
                        break
                        
                    # Select a random NPC with quests
                    idx = random.randint(0, len(quest_giving_npcs) - 1)
                    npc, quests = quest_giving_npcs[idx]
                    
                    # Select a random quest from this NPC
                    quest = random.choice(quests)
                    
                    # Assign to player
                    updated_quest = NPCQuestManager.assign_quest_to_player(quest["id"], player_id)
                    quest_ids.append(updated_quest["id"])
                    
                    # Remove this NPC from consideration for more quests
                    quest_giving_npcs.pop(idx)
            
            # 2. Generate location-based quests to fill the remaining count
            remaining = count - len(quest_ids)
            if remaining > 0:
                # Determine quest parameters based on location
                region_type = location_data.get("region_type", "wilderness")
                location_danger = location_data.get("danger_level", 1)
                
                # Map region types to quest themes
                theme_map = {
                    "settlement": "social",
                    "dungeon": "combat",
                    "wilderness": "exploration",
                    "ruins": "mystery"
                }
                theme = theme_map.get(region_type, "exploration")
                
                # Map danger levels to difficulty
                difficulty_map = {
                    1: "easy",
                    2: "easy",
                    3: "medium",
                    4: "medium",
                    5: "hard"
                }
                difficulty = difficulty_map.get(location_danger, "easy")
                
                # Generate remaining quests
                for _ in range(remaining):
                    # Generate quest data
                    title = QuestGenerator.generate_quest_title(theme, difficulty)
                    
                    quest_data = {
                        "title": title,
                        "description": f"A quest in {location_data.get('name', 'this area')}",
                        "player_id": player_id,
                        "location_id": location_id,
                        "theme": theme,
                        "difficulty": difficulty,
                        "level": max(1, player_data.get("level", 1)),
                        "type": "location",
                        "status": "active",
                        "steps": QuestGenerator.generate_quest_steps(theme, difficulty),
                        "rewards": {
                            "gold": QuestGenerator.calculate_quest_reward(difficulty, "gold")["amount"],
                            "experience": QuestGenerator.calculate_quest_reward(difficulty, "experience")["amount"],
                            "reputation": QuestGenerator.calculate_quest_reward(difficulty, "reputation")["amount"]
                        },
                        "created_at": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                    
                    # Save to database
                    quest_id = QuestUtils.create_quest(quest_data)
                    quest_ids.append(quest_id)
                    
                    # Create initial journal entry
                    journal_entry = {
                        "player_id": player_id,
                        "quest_id": quest_id,
                        "content": f"I discovered a new quest: {title}"
                    }
                    QuestUtils.create_journal_entry(journal_entry)
            
            # 3. Attempt to advance story arc if not enough quests were generated
            if len(quest_ids) < count:
                # Check for active player arc
                arc_data = PlayerArcManager.load_player_arc(player_id)
                
                # Create a new arc if none exists
                if not arc_data:
                    arc_data = PlayerArcManager.create_player_arc(player_id)
                
                # Use character background for themed quest if available
                if player_data.get("background"):
                    # Create or ensure character arc exists
                    char_arc = PlayerArcManager.generate_character_arc(player_id, player_data["background"])
                    
                    # Generate a quest based on current chapter
                    current_chapter = char_arc.get("current_chapter", 0)
                    chapters = char_arc.get("chapters", [])
                    
                    if chapters and current_chapter < len(chapters):
                        chapter = chapters[current_chapter]
                        
                        # Generate a quest for this chapter
                        quest_data = {
                            "title": f"{chapter.get('title', 'Character Quest')}",
                            "description": f"A quest related to your past as {player_data.get('background', 'an adventurer')}.",
                            "player_id": player_id,
                            "arc_id": player_id,  # Use player ID as arc ID for character arcs
                            "chapter_index": current_chapter,
                            "theme": "character",
                            "difficulty": "medium",  # Adjust based on chapter/arc
                            "level": max(1, player_data.get("level", 1)),
                            "type": "story",
                            "status": "active",
                            "steps": QuestGenerator.generate_quest_steps("character", "medium"),
                            "rewards": {
                                "gold": QuestGenerator.calculate_quest_reward("medium", "gold")["amount"],
                                "experience": QuestGenerator.calculate_quest_reward("medium", "experience")["amount"],
                                "reputation": QuestGenerator.calculate_quest_reward("medium", "reputation")["amount"]
                            },
                            "created_at": datetime.utcnow().isoformat(),
                            "updated_at": datetime.utcnow().isoformat()
                        }
                        
                        # Save to database
                        quest_id = QuestUtils.create_quest(quest_data)
                        quest_ids.append(quest_id)
                        
                        # Create initial journal entry
                        journal_entry = {
                            "player_id": player_id,
                            "quest_id": quest_id,
                            "content": f"I've begun a journey to {chapter.get('title', 'discover my path')}."
                        }
                        QuestUtils.create_journal_entry(journal_entry)
            
            return quest_ids
        
        except Exception as e:
            logger.error(f"Error generating quests for player: {str(e)}")
            return [] 