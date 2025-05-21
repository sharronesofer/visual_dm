"""
Quest generation utilities.
Handles creation of quests, quest steps, and related narrative elements.
"""

import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.systems.npc import NPCManager
from backend.systems.world import WorldStateManager
from backend.systems.item import ItemManager
from .models import Quest, QuestStep

logger = logging.getLogger(__name__)

class QuestGenerator:
    """Utilities for generating quests, steps, and related narrative content."""
    
    @staticmethod
    def generate_quest_title(theme: str, difficulty: str) -> str:
        """Generate a quest title based on theme and difficulty."""
        try:
            themes = {
                'combat': ['Slay the', 'Defeat the', 'Conquer the', 'Vanquish the'],
                'exploration': ['Discover the', 'Find the', 'Explore the', 'Search for the'],
                'social': ['Convince the', 'Persuade the', 'Negotiate with the', 'Mediate between'],
                'mystery': ['Investigate the', 'Uncover the', 'Solve the', 'Decipher the']
            }
            
            adjectives = {
                'easy': ['Curious', 'Local', 'Minor', 'Small'],
                'medium': ['Dangerous', 'Forgotten', 'Hidden', 'Valuable'],
                'hard': ['Ancient', 'Cursed', 'Legendary', 'Mythical'],
                'epic': ['Dreadful', 'Divine', 'Infernal', 'Primordial']
            }
            
            nouns = {
                'combat': ['Dragon', 'Beast', 'Warband', 'Champion'],
                'exploration': ['Ruins', 'Cavern', 'Shrine', 'Artifact'],
                'social': ['Noble', 'Merchant', 'Guild', 'Council'],
                'mystery': ['Conspiracy', 'Disappearance', 'Secret', 'Prophecy']
            }
            
            prefix = random.choice(themes.get(theme, themes['exploration']))
            adjective = random.choice(adjectives.get(difficulty, adjectives['medium']))
            noun = random.choice(nouns.get(theme, nouns['exploration']))
            
            return f"{prefix} {adjective} {noun}"
        except Exception as e:
            logger.error(f"Error generating quest title: {str(e)}")
            return "Untitled Quest"
    
    @staticmethod
    def generate_quest_steps(theme: str, difficulty: str, location_id: Optional[str] = None) -> List[QuestStep]:
        """Generate quest steps based on theme and difficulty."""
        try:
            steps = []
            
            # Number of steps based on difficulty
            step_count = {
                'easy': random.randint(1, 2),
                'medium': random.randint(2, 3),
                'hard': random.randint(3, 4),
                'epic': random.randint(4, 6)
            }.get(difficulty, 2)
            
            # Generate steps based on theme
            for i in range(step_count):
                step = None
                
                if theme == 'combat':
                    enemy_types = ['bandit', 'wolf', 'goblin', 'cultist', 'undead']
                    enemy = random.choice(enemy_types)
                    quantity = random.randint(1, 5) if difficulty != 'epic' else random.randint(5, 10)
                    
                    step = QuestStep(
                        id=i+1,
                        description=f"Defeat {quantity} {enemy}s",
                        type="kill",
                        completed=False,
                        data={"enemy_type": enemy, "quantity": quantity}
                    )
                
                elif theme == 'exploration':
                    locations = WorldStateManager.get_nearby_locations(location_id, 5) if location_id else ["an unknown location"]
                    location = random.choice(locations) if locations else "the mysterious ruins"
                    
                    step = QuestStep(
                        id=i+1,
                        description=f"Explore {location}",
                        type="explore",
                        completed=False,
                        target_location_id=location_id,
                        data={"discover": True}
                    )
                
                elif theme == 'social':
                    npcs = NPCManager.get_npcs_in_location(location_id) if location_id else []
                    npc_id = random.choice(npcs) if npcs else None
                    npc_name = NPCManager.get_npc_name(npc_id) if npc_id else "the local official"
                    
                    step = QuestStep(
                        id=i+1,
                        description=f"Speak with {npc_name}",
                        type="dialogue",
                        completed=False,
                        target_npc_id=npc_id,
                        data={"dialogue_type": "information"}
                    )
                
                elif theme == 'mystery':
                    items = ItemManager.get_items_by_type("clue") if hasattr(ItemManager, "get_items_by_type") else []
                    item_id = random.choice(items) if items else None
                    item_name = ItemManager.get_item_name(item_id) if item_id else "the mysterious object"
                    
                    step = QuestStep(
                        id=i+1,
                        description=f"Find {item_name}",
                        type="collect",
                        completed=False,
                        data={"item_id": item_id, "quantity": 1}
                    )
                
                # Default step if none of the above themes match
                if not step:
                    step = QuestStep(
                        id=i+1,
                        description=f"Complete task {i+1}",
                        type="generic",
                        completed=False
                    )
                
                steps.append(step)
            
            return steps
        except Exception as e:
            logger.error(f"Error generating quest steps: {str(e)}")
            return [QuestStep(id=1, description="Complete the quest", completed=False)]
    
    @staticmethod
    def calculate_quest_reward(difficulty: str, level: int = 1) -> Dict[str, Any]:
        """Calculate appropriate rewards based on quest difficulty and player level."""
        try:
            # Base reward multipliers
            multipliers = {
                'easy': 1.0,
                'medium': 1.5,
                'hard': 2.5,
                'epic': 4.0
            }
            
            multiplier = multipliers.get(difficulty, 1.0)
            
            # Scale rewards with level
            base_gold = int(25 * multiplier * (1 + (level * 0.1)))
            base_xp = int(50 * multiplier * (1 + (level * 0.08)))
            
            # Add variance
            gold_variance = random.uniform(0.8, 1.2)
            xp_variance = random.uniform(0.9, 1.1)
            
            gold = max(1, int(base_gold * gold_variance))
            xp = max(5, int(base_xp * xp_variance))
            
            # Chance for item rewards based on difficulty
            item_chance = {
                'easy': 0.1,
                'medium': 0.25,
                'hard': 0.5,
                'epic': 0.75
            }.get(difficulty, 0.1)
            
            rewards = {
                'gold': gold,
                'experience': xp
            }
            
            # Add item rewards with some probability
            if random.random() < item_chance:
                item_level = max(1, level - random.randint(0, 2))
                rewards['items'] = [{"item_level": item_level}]
            
            return rewards
        except Exception as e:
            logger.error(f"Error calculating quest reward: {str(e)}")
            return {'gold': 10, 'experience': 25}
    
    @staticmethod
    def generate_quest(player_id: str, theme: Optional[str] = None, difficulty: Optional[str] = None, 
                     location_id: Optional[str] = None, npc_id: Optional[str] = None, 
                     level: int = 1) -> Quest:
        """Generate a complete quest with steps and rewards."""
        try:
            # Use provided theme/difficulty or choose random ones
            themes = ['combat', 'exploration', 'social', 'mystery']
            difficulties = ['easy', 'medium', 'hard', 'epic']
            
            theme = theme or random.choice(themes)
            difficulty = difficulty or random.choice(difficulties)
            
            # Generate quest title
            title = QuestGenerator.generate_quest_title(theme, difficulty)
            
            # Get NPC information if provided
            npc_name = ""
            if npc_id:
                npc_name = NPCManager.get_npc_name(npc_id) if hasattr(NPCManager, "get_npc_name") else "Unknown"
            
            # Generate description based on theme and difficulty
            descriptions = {
                'combat': [
                    f"Dangerous creatures threaten the area. Defeat them to restore safety.",
                    f"A powerful enemy must be vanquished to protect the innocent."
                ],
                'exploration': [
                    f"An important location needs to be explored for valuable artifacts.",
                    f"Uncharted territories hold secrets waiting to be discovered."
                ],
                'social': [
                    f"Local tensions require diplomatic intervention to prevent conflict.",
                    f"Important information must be gathered from key individuals."
                ],
                'mystery': [
                    f"Strange occurrences need investigation to uncover the truth.",
                    f"A puzzling situation requires your detective skills to resolve."
                ]
            }
            
            description = random.choice(descriptions.get(theme, ["A quest awaits you."]))
            if npc_name:
                description = f"{npc_name} has requested your help. {description}"
            
            # Generate steps
            steps = QuestGenerator.generate_quest_steps(theme, difficulty, location_id)
            
            # Calculate rewards
            rewards = QuestGenerator.calculate_quest_reward(difficulty, level)
            
            # Create the quest
            quest = Quest(
                title=title,
                description=description,
                status="available",
                difficulty=difficulty,
                npc_id=npc_id,
                steps=steps,
                reward_type="multiple",
                reward_details=rewards,
                is_main_quest=False,
                tags=[theme, difficulty]
            )
            
            return quest
        except Exception as e:
            logger.error(f"Error generating quest: {str(e)}")
            # Return a basic fallback quest
            return Quest(
                title="Untitled Quest",
                description="A basic quest.",
                status="available",
                difficulty="medium",
                steps=[QuestStep(id=1, description="Complete the quest", completed=False)],
                reward_type="gold",
                reward_details={"gold": 10}
            )
    
    @staticmethod
    def generate_journal_entry(quest_data: Dict[str, Any], 
                            event_type: str = "update",
                            details: Optional[str] = None) -> Dict[str, Any]:
        """Generate a quest journal entry based on event type."""
        try:
            title = quest_data.get("title", "Unknown Quest")
            
            entry_titles = {
                "started": f"Quest Started: {title}",
                "updated": f"Quest Update: {title}",
                "completed": f"Quest Completed: {title}",
                "failed": f"Quest Failed: {title}"
            }
            
            entry_title = entry_titles.get(event_type, f"Quest {event_type.capitalize()}: {title}")
            
            # Create content based on event type if not provided
            if not details:
                if event_type == "started":
                    details = f"I have begun a new quest: {title}. {quest_data.get('description', '')}"
                elif event_type == "updated":
                    details = f"Made progress on the quest '{title}'."
                elif event_type == "completed":
                    details = f"I have successfully completed the quest '{title}' and claimed my reward."
                elif event_type == "failed":
                    details = f"I was unable to complete the quest '{title}'."
                else:
                    details = f"Quest '{title}' status has been updated."
            
            # Create the journal entry
            entry = {
                "player_id": quest_data.get("player_id", "unknown"),
                "quest_id": quest_data.get("id", "unknown"),
                "title": entry_title,
                "content": details,
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type
            }
            
            return entry
        except Exception as e:
            logger.error(f"Error generating journal entry: {str(e)}")
            return {
                "player_id": quest_data.get("player_id", "unknown"),
                "quest_id": quest_data.get("id", "unknown"),
                "title": "Quest Update",
                "content": "Something happened with your quest.",
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "update"
            }
    
    @staticmethod
    def generate_arc_for_character(character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a narrative arc for a character based on their background."""
        try:
            character_id = character_data.get("id", "unknown")
            character_name = character_data.get("name", "Unknown Adventurer")
            character_class = character_data.get("class", "adventurer")
            character_background = character_data.get("background", "")
            
            # Arc themes based on character class
            class_themes = {
                "warrior": ["honor", "duty", "strength"],
                "mage": ["knowledge", "power", "mystery"],
                "rogue": ["freedom", "wealth", "secrecy"],
                "cleric": ["faith", "service", "divinity"],
                "ranger": ["nature", "exploration", "balance"],
                "bard": ["art", "legacy", "charisma"]
            }
            
            theme = random.choice(class_themes.get(character_class.lower(), ["destiny"]))
            
            # Sample arc titles based on themes
            arc_titles = {
                "honor": [f"{character_name}'s Honor", "The Path of Righteousness", "A Question of Loyalty"],
                "duty": ["Sworn Obligation", "The Burden of Responsibility", f"{character_name}'s Pledge"],
                "strength": ["Trial of Might", "Proving Grounds", "The Strongest Shall Lead"],
                "knowledge": ["Forbidden Knowledge", "Ancient Secrets", "The Arcane Truth"],
                "power": ["The Source of Power", "Mastery of Elements", "Beyond Mortal Limits"],
                "mystery": ["Whispers of the Unknown", "Shadows of the Past", "The Veiled Truth"],
                "freedom": ["Breaking Chains", "The Price of Liberty", "No Master But Oneself"],
                "wealth": ["Fortune's Favor", "The Greatest Heist", "Treasures Untold"],
                "secrecy": ["Hidden Motives", "The Unseen Hand", "Masks and Shadows"],
                "faith": ["Divine Calling", "Test of Faith", "The Faithful Servant"],
                "service": ["For the Greater Good", "The Humble Path", "Service Above Self"],
                "divinity": ["Touched by the Gods", "Divine Intervention", "The Mortal Vessel"],
                "nature": ["Call of the Wild", "Nature's Balance", "The Verdant Path"],
                "exploration": ["Uncharted Territories", "Beyond the Horizon", "The Lost Expedition"],
                "balance": ["Harmony Restored", "Between Two Worlds", "The Middle Path"],
                "art": ["The Greatest Tale", "Songs of Legend", "Art Immortal"],
                "legacy": ["Echoes of the Past", "Blood of Heroes", "The Name Remembered"],
                "charisma": ["Hearts and Minds", "The Silver Tongue", "Friend of All"],
                "destiny": ["Fate's Design", "The Chosen One", "Written in the Stars"]
            }
            
            title = random.choice(arc_titles.get(theme, ["A New Beginning"]))
            
            # Create the arc data
            arc_data = {
                "id": f"arc_{character_id}",
                "title": title,
                "theme": theme,
                "character_id": character_id,
                "created_at": datetime.utcnow().isoformat(),
                "progress": 0,
                "completed": False,
                "milestones": [],
                "linked_quests": []
            }
            
            # Add some background-influenced content if available
            if character_background:
                # Extract key elements from background
                keywords = character_background.lower().split()
                background_themes = []
                
                theme_keywords = {
                    "revenge": ["revenge", "vengeance", "avenge", "wronged"],
                    "redemption": ["redemption", "atone", "forgiveness", "mistake"],
                    "discovery": ["discovery", "find", "search", "lost", "family"],
                    "ambition": ["ambition", "power", "wealth", "status", "rise"],
                    "protection": ["protect", "defend", "safety", "shelter", "guard"]
                }
                
                for theme, words in theme_keywords.items():
                    if any(word in keywords for word in words):
                        background_themes.append(theme)
                
                if background_themes:
                    chosen_theme = random.choice(background_themes)
                    arc_data["background_theme"] = chosen_theme
                    
                    # Add a milestone based on the background theme
                    milestones = {
                        "revenge": f"Find those who wronged you and make them pay",
                        "redemption": f"Seek to atone for past mistakes",
                        "discovery": f"Uncover the truth about your origins",
                        "ambition": f"Rise to a position of influence and power",
                        "protection": f"Ensure the safety of those you care about"
                    }
                    
                    arc_data["milestones"].append({
                        "description": milestones.get(chosen_theme, "Begin your journey"),
                        "completed": False
                    })
            
            return arc_data
        except Exception as e:
            logger.error(f"Error generating character arc: {str(e)}")
            return {
                "id": f"arc_{character_data.get('id', 'unknown')}",
                "title": "A New Beginning",
                "theme": "destiny",
                "character_id": character_data.get("id", "unknown"),
                "created_at": datetime.utcnow().isoformat(),
                "progress": 0,
                "completed": False,
                "milestones": [{"description": "Begin your journey", "completed": False}],
                "linked_quests": []
            } 