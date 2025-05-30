from backend.systems.quest.generator import QuestGenerator
from backend.systems.quest.generator import QuestGenerator
from backend.systems.quest.generator import QuestGenerator
from backend.systems.quest.generator import QuestGenerator
from backend.systems.quest.generator import QuestGenerator
from backend.systems.quest.generator import QuestGenerator
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import mock dependencies to avoid actual Firebase calls
import sys
import os

# Make sure the mock_dependencies can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mock_dependencies import *

# Import quest generator and integration modules
try:
    from backend.systems.quest.generator import QuestGenerator
    from backend.systems.quest.integration import QuestIntegration
except ImportError:
    # If imports fail, use mock implementations
    QuestGenerator = None
    QuestIntegration = None


class POIQuestGeneratorTests(unittest.TestCase):
    """Tests for POI-based quest generation."""

    def setUp(self):
        """Set up tests."""
        # Mock the world state manager
        self.world_state_patcher = patch("backend.systems.quest.integration.WorldStateManager")
        self.mock_world_state_class = self.world_state_patcher.start()
        
        # Create mock instance
        self.mock_world_state = MagicMock()
        self.mock_world_state_class.get_instance.return_value = self.mock_world_state

        # Mock EventBus
        self.event_bus_patcher = patch("backend.systems.events.get_event_dispatcher")
        self.mock_event_bus = self.event_bus_patcher.start()

        # Set up mock POI data
        self.poi_data = {
            "town_riverbrook": {
                "id": "town_riverbrook",
                "name": "Riverbrook",
                "type": "town",
                "region_id": "green_valley",
                "region_type": "settlement",
                "danger_level": 1,
                "active_npcs": ["merchant_1", "innkeeper_2", "guard_captain_3"],
                "available_services": ["inn", "blacksmith", "general_store"],
                "quest_themes": ["trade", "local_defense", "gathering"],
                "description": "A peaceful riverside trading town",
            },
            "dungeon_darkhold": {
                "id": "dungeon_darkhold",
                "name": "Darkhold Ruins",
                "type": "dungeon",
                "region_id": "dark_forest",
                "region_type": "dungeon",
                "danger_level": 4,
                "enemy_types": ["undead", "cultists"],
                "boss_types": ["necromancer"],
                "quest_themes": ["exploration", "artifact_recovery", "undead_problem"],
                "description": "Ancient ruins corrupted by dark magic",
            },
            "grove_whisperleaf": {
                "id": "grove_whisperleaf",
                "name": "Whisperleaf Grove",
                "type": "nature",
                "region_id": "green_valley",
                "region_type": "wilderness",
                "danger_level": 2,
                "flora": ["healing_herbs", "rare_flowers"],
                "fauna": ["deer", "sprites"],
                "quest_themes": ["nature_restoration", "gathering", "lost_traveler"],
                "description": "A serene grove with magical properties",
            },
        }

        # Set up mock regional data
        self.region_data = {
            "green_valley": {
                "id": "green_valley",
                "name": "Green Valley",
                "type": "temperate",
                "danger_level": 2,
                "primary_motifs": ["Growth", "Peace"],
                "description": "A peaceful farming valley with gentle rivers and rolling hills",
            },
            "dark_forest": {
                "id": "dark_forest",
                "name": "Dark Forest",
                "type": "corrupted_forest",
                "danger_level": 4,
                "primary_motifs": ["Corruption", "Mystery"],
                "description": "A foreboding forest corrupted by dark magic",
            },
            "default_location": {
                "id": "default_location",
                "name": "Starting Area",
                "type": "settlement",
                "danger_level": 1,
                "primary_motifs": ["Safety", "Home"],
                "description": "The default starting area for new adventurers",
            },
        }

        # Configure world state manager to return our mock data
        self.mock_world_state.get_poi_data = lambda poi_id: self.poi_data.get(poi_id)
        self.mock_world_state.get_region_data = lambda region_id: self.region_data.get(
            region_id
        )
        self.mock_world_state.get_pois_in_region = lambda region_id: [
            poi for poi in self.poi_data.values() if poi["region_id"] == region_id
        ]
        
        # Add the get_location method that was missing
        def mock_get_location(location_id):
            # Check if it's a POI first
            if location_id in self.poi_data:
                poi = self.poi_data[location_id]
                return {
                    "id": poi["id"],
                    "name": poi["name"],
                    "type": poi.get("region_type", poi["type"]),
                    "region_type": poi.get("region_type", poi["type"]),
                    "danger_level": poi.get("danger_level", 1),
                    "description": poi["description"]
                }
            # Check if it's a region
            if location_id in self.region_data:
                region = self.region_data[location_id]
                return {
                    "id": region["id"],
                    "name": region["name"],
                    "type": region["type"],
                    "region_type": region["type"],
                    "danger_level": region.get("danger_level", 1),
                    "description": region["description"]
                }
            return None
            
        self.mock_world_state.get_location = mock_get_location

        # Initialize QuestGenerator mock if needed
        if not QuestGenerator:
            # Create a simple mock for QuestGenerator
            self.quest_generator = MagicMock()
            self.quest_generator.generate_quest_from_poi = (
                self._mock_generate_quest_from_poi
            )
            self.quest_generator.generate_questline_from_region = (
                self._mock_generate_questline
            )
        else:
            # Create actual QuestGenerator instance
            self.quest_generator = QuestGenerator()

    def tearDown(self):
        """Clean up after tests."""
        self.world_state_patcher.stop()
        self.event_bus_patcher.stop()

    def _mock_generate_quest_from_poi(self, poi_id, player_id, quest_type="standard"):
        """Mock implementation of quest generation from POI."""
        poi_data = self.mock_world_state.get_poi_data(poi_id)

        if not poi_data:
            return None

        # Create a basic quest structure based on the POI
        quest = {
            "id": f"quest_{poi_id}_{quest_type}",
            "title": f"{quest_type.capitalize()} at {poi_data['name']}",
            "description": f"A quest related to {poi_data['description']}",
            "player_id": player_id,
            "poi_id": poi_id,
            "region_id": poi_data["region_id"],
            "quest_type": quest_type,
            "status": "pending",
            "steps": [],
        }

        # Add appropriate steps based on POI type
        if poi_data["type"] == "town":
            quest["steps"].append(
                {
                    "id": 1,
                    "description": f"Speak with the quest giver in {poi_data['name']}",
                    "type": "dialogue",
                    "target_npc_id": poi_data["active_npcs"][0],
                    "dialogue_id": f"quest_start_{poi_id}",
                    "completed": False,
                }
            )
            quest["steps"].append(
                {
                    "id": 2,
                    "description": "Complete the main objective",
                    "type": "visit",
                    "target_location_id": poi_data["id"],
                    "completed": False,
                }
            )

        elif poi_data["type"] == "dungeon":
            quest["steps"].append(
                {
                    "id": 1,
                    "description": f"Explore {poi_data['name']}",
                    "type": "visit",
                    "target_location_id": poi_data["id"],
                    "completed": False,
                }
            )
            quest["steps"].append(
                {
                    "id": 2,
                    "description": f"Defeat enemies in {poi_data['name']}",
                    "type": "kill",
                    "target_enemy_type": poi_data["enemy_types"][0],
                    "required_count": 3,
                    "completed": False,
                }
            )

        elif poi_data["type"] == "nature":
            quest["steps"].append(
                {
                    "id": 1,
                    "description": f"Visit {poi_data['name']}",
                    "type": "visit",
                    "target_location_id": poi_data["id"],
                    "completed": False,
                }
            )
            quest["steps"].append(
                {
                    "id": 2,
                    "description": f"Gather resources from {poi_data['name']}",
                    "type": "collect",
                    "target_item_id": poi_data["flora"][0],
                    "quantity": 5,
                    "completed": False,
                }
            )

        # Add quest rewards
        quest["rewards"] = {
            "gold": 50 * (self.region_data[poi_data["region_id"]]["danger_level"]),
            "xp": 100 * (self.region_data[poi_data["region_id"]]["danger_level"]),
        }

        # Add completion step
        quest["steps"].append(
            {
                "id": len(quest["steps"]) + 1,
                "description": "Return to complete the quest",
                "type": "visit",
                "target_location_id": "town_riverbrook",  # Default return location
                "completed": False,
            }
        )

        return quest

    def _mock_generate_questline(self, region_id, player_id, num_quests=3):
        """Mock implementation of questline generation from a region."""
        region_data = self.mock_world_state.get_region_data(region_id)
        pois = self.mock_world_state.get_pois_in_region(region_id)

        if not region_data or not pois:
            return []

        # Generate a series of connected quests
        questline = []
        for i in range(min(num_quests, len(pois))):
            poi = pois[i]
            quest_type = "main" if i == 0 else "side"

            quest = self._mock_generate_quest_from_poi(poi["id"], player_id, quest_type)

            # Connect quests in the line
            if i > 0:
                # Each quest after the first depends on the previous one
                quest["dependencies"] = [questline[i - 1]["id"]]

                # Add story progression
                quest["description"] = (
                    f"Continue your journey in {region_data['name']}: {quest['description']}"
                )

            # Add regional motifs
            quest["motif"] = region_data["primary_motifs"][0]
            quest["motif_intensity"] = (
                3 + i
            )  # Intensity increases with quest progression

            questline.append(quest)

        return questline

    def test_quest_generation_from_town(self):
        """Test generating quests from a town POI."""
        # Generate a quest from Riverbrook town
        quest = self.quest_generator.generate_quest_from_poi(
            "town_riverbrook", "player_123"
        )

        # Verify quest structure - quest is a Quest object, not a dict
        quest_dict = quest.to_dict()  # Convert to dict for easier testing
        self.assertEqual(quest_dict.get("location_id"), "town_riverbrook")
        self.assertIsInstance(quest.steps, list)
        self.assertTrue(len(quest.steps) >= 1)  # Should have at least 1 step
        
        # Check that it's a proper Quest object
        self.assertEqual(quest.player_id, "player_123")
        self.assertEqual(quest.status, "available")

    def test_quest_generation_from_dungeon(self):
        """Test generating quests from a dungeon POI."""
        # Generate a quest from the dungeon
        quest = self.quest_generator.generate_quest_from_poi(
            "dungeon_darkhold", "player_123"
        )

        # Verify quest structure - quest is a Quest object, not a dict
        quest_dict = quest.to_dict()  # Convert to dict for easier testing
        self.assertEqual(quest_dict.get("location_id"), "dungeon_darkhold")
        self.assertIsInstance(quest.steps, list)
        self.assertTrue(len(quest.steps) >= 1)  # Should have at least 1 step
        
        # Check that it's a proper Quest object
        self.assertEqual(quest.player_id, "player_123")
        self.assertEqual(quest.status, "available")

    def test_quest_generation_from_nature(self):
        """Test generating quests from a nature POI."""
        # Generate a quest from the grove
        quest = self.quest_generator.generate_quest_from_poi(
            "grove_whisperleaf", "player_123"
        )

        # Verify quest structure - quest is a Quest object, not a dict
        quest_dict = quest.to_dict()  # Convert to dict for easier testing
        self.assertEqual(quest_dict.get("location_id"), "grove_whisperleaf")
        self.assertIsInstance(quest.steps, list)
        self.assertTrue(len(quest.steps) >= 1)  # Should have at least 1 step
        
        # Check that it's a proper Quest object
        self.assertEqual(quest.player_id, "player_123")
        self.assertEqual(quest.status, "available")

    def test_questline_generation(self):
        """Test generating a questline for a region."""
        # Generate a questline for the green valley
        questline = self.quest_generator.generate_questline_from_region(
            "green_valley", "player_123", 2  # Generate 2 connected quests
        )

        # Verify questline structure - questline contains Quest objects
        self.assertEqual(len(questline), 2)
        
        # Check that all items are Quest objects
        for quest in questline:
            self.assertEqual(quest.player_id, "player_123")
            self.assertEqual(quest.status, "available")
            self.assertIsInstance(quest.steps, list)

    def test_regional_density_and_distribution(self):
        """Test that the POI density matches the game world design."""

        # Let's assume we have functions to count POIs by region and type
        def count_pois_in_region(region_id):
            return len(
                [poi for poi in self.poi_data.values() if poi["region_id"] == region_id]
            )

        def count_poi_types_in_region(region_id):
            types = {}
            for poi in self.poi_data.values():
                if poi["region_id"] == region_id:
                    poi_type = poi["type"]
                    types[poi_type] = types.get(poi_type, 0) + 1
            return types

        # Test our sample data (in a real implementation, you'd test against actual world data)
        green_valley_count = count_pois_in_region("green_valley")
        self.assertEqual(green_valley_count, 2)  # town_riverbrook, grove_whisperleaf

        dark_forest_count = count_pois_in_region("dark_forest")
        self.assertEqual(dark_forest_count, 1)  # dungeon_darkhold

        # Test POI type distribution
        green_valley_types = count_poi_types_in_region("green_valley")
        self.assertEqual(green_valley_types.get("town", 0), 1)
        self.assertEqual(green_valley_types.get("nature", 0), 1)

        dark_forest_types = count_poi_types_in_region("dark_forest")
        self.assertEqual(dark_forest_types.get("dungeon", 0), 1)

        # Note: In a production system, you'd verify against the actual
        # design targets mentioned in the development bible (20 major POIs,
        # 200-400 minor POIs per region)

    def test_generate_quests_for_player_location(self):
        """Test generating quests based on player location."""
        # Set up QuestIntegration mock if needed
        if not QuestIntegration:
            quest_integration = MagicMock()

            # Mock the generate_quests_for_player method
            def mock_generate_quests(player_id, location_id=None, count=3):
                if location_id:
                    # Generate quests for specific location
                    if location_id in self.poi_data:
                        poi_data = self.poi_data[location_id]
                        region_id = poi_data["region_id"]

                        # Generate a quest specific to this POI
                        quest = self.quest_generator.generate_quest_from_poi(
                            location_id, player_id
                        )
                        # Fix: quest is a Quest object, not a dict
                        return [quest.id]

                    # Generate quests from the region
                    for poi_id, poi in self.poi_data.items():
                        if poi["region_id"] == location_id:
                            quests = (
                                self.quest_generator.generate_questline_from_region(
                                    location_id, player_id, count
                                )
                            )
                            # Fix: quests are Quest objects, not dicts
                            return [q.id for q in quests]

                    return []
                else:
                    # No location specified - generate generic quests
                    return ["generic_quest_1", "generic_quest_2"]

            quest_integration.generate_quests_for_player = mock_generate_quests
        else:
            # Use actual implementation
            quest_integration = QuestIntegration()

        # Test generating quests at a specific POI
        quest_ids = quest_integration.generate_quests_for_player(
            "player_123", "town_riverbrook", 1
        )
        self.assertEqual(len(quest_ids), 1)

        # Test generating quests in a region
        quest_ids = quest_integration.generate_quests_for_player(
            "player_123", "green_valley", 2
        )
        self.assertEqual(len(quest_ids), 2)

        # Test generating generic quests with no location
        quest_ids = quest_integration.generate_quests_for_player("player_123", None, 2)
        self.assertEqual(len(quest_ids), 2)


if __name__ == "__main__":
    unittest.main()
