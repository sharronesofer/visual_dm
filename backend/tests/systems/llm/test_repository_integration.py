"""
Integration tests for the LLM system's repository pattern implementation.

These tests validate that the repository components work together correctly: pass
1. Repositories properly store and retrieve data
2. JSON serialization/deserialization works correctly
3. Versioning is maintained
4. Repository pattern abstracts database operations properly
"""

import unittest
import os
import tempfile
import json
import shutil
from datetime import datetime
import time

from backend.systems.llm.repositories.player_repository import PlayerRepository
from backend.systems.llm.repositories.region_repository import RegionRepository
from backend.systems.llm.repositories.npc_repository import NPCRepository
from backend.systems.llm.repositories.faction_repository import FactionRepository
from backend.systems.llm.repositories.world_repository import WorldRepository
from backend.systems.llm.repositories.motif_repository import MotifRepository
from backend.systems.llm.repositories.rumor_repository import RumorRepository


class TestRepositoryIntegration(unittest.TestCase): pass
    """Integration tests for the repository pattern of the LLM system."""

    def setUp(self): pass
        """Set up test environment with a temporary data directory."""
        # Create temporary data directory
        self.temp_dir = tempfile.mkdtemp()
        os.environ["VDM_DATA_DIR"] = self.temp_dir

        # Create necessary subdirectories
        os.makedirs(os.path.join(self.temp_dir, "entities", "players"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "entities", "npcs"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "entities", "factions"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "world", "regions"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "motifs"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "rumors"), exist_ok=True)

        # Reset all singleton instances
        PlayerRepository._instance = None
        RegionRepository._instance = None
        NPCRepository._instance = None
        FactionRepository._instance = None
        WorldRepository._instance = None
        MotifRepository._instance = None
        RumorRepository._instance = None

        # Get clean instances
        self.player_repo = PlayerRepository.get_instance()
        self.region_repo = RegionRepository.get_instance()
        self.npc_repo = NPCRepository.get_instance()
        self.faction_repo = FactionRepository.get_instance()
        self.world_repo = WorldRepository.get_instance()
        self.motif_repo = MotifRepository.get_instance()
        self.rumor_repo = RumorRepository.get_instance()

    def tearDown(self): pass
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)

    def test_player_repository(self): pass
        """Test that the player repository properly stores and retrieves data."""
        # Create test player data
        player_data = {
            "id": "test_player",
            "name": "Test Player",
            "region_id": "test_region",
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "motifs": {
                "active": [
                    {
                        "theme": "vengeance",
                        "weight": 5,
                        "added_at": datetime.utcnow().isoformat(),
                    }
                ],
                "expired": [],
            },
            "relationships": {
                "npc": {
                    "test_npc": {
                        "standing": 0.7,
                        "reputation": 0.5,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                },
                "faction": {
                    "test_faction": {
                        "standing": 0.3,
                        "reputation": 0.2,
                        "updated_at": datetime.utcnow().isoformat(),
                    }
                },
            },
        }

        # Store the player data
        self.player_repo.update_player_data("test_player", player_data)

        # Retrieve the player data
        retrieved_data = self.player_repo.get_player_data("test_player")

        # Check that the data was stored and retrieved correctly
        self.assertEqual(retrieved_data["id"], "test_player")
        self.assertEqual(retrieved_data["name"], "Test Player")
        self.assertEqual(retrieved_data["region_id"], "test_region")
        self.assertEqual(retrieved_data["version"], 1)
        self.assertEqual(len(retrieved_data["motifs"]["active"]), 1)
        self.assertEqual(retrieved_data["motifs"]["active"][0]["theme"], "vengeance")
        self.assertEqual(
            retrieved_data["relationships"]["npc"]["test_npc"]["standing"], 0.7
        )

        # Update the player data
        player_data["name"] = "Updated Player"
        player_data["version"] = 2
        player_data["motifs"]["active"].append(
            {"theme": "honor", "weight": 3, "added_at": datetime.utcnow().isoformat()}
        )
        self.player_repo.update_player_data("test_player", player_data)

        # Retrieve the updated data
        updated_data = self.player_repo.get_player_data("test_player")

        # Check that the data was updated correctly
        self.assertEqual(updated_data["name"], "Updated Player")
        self.assertEqual(updated_data["version"], 2)
        self.assertEqual(len(updated_data["motifs"]["active"]), 2)
        self.assertEqual(updated_data["motifs"]["active"][1]["theme"], "honor")

        # Check file persistence
        player_file = os.path.join(
            self.temp_dir, "entities", "players", "test_player.json"
        )
        self.assertTrue(os.path.exists(player_file))

        with open(player_file, "r") as f: pass
            file_data = json.load(f)
            self.assertEqual(file_data["name"], "Updated Player")
            self.assertEqual(file_data["version"], 2)

    def test_region_repository(self): pass
        """Test that the region repository properly stores and retrieves data."""
        # Create test region data
        region_data = {
            "id": "test_region",
            "name": "Test Region",
            "description": "A region for testing",
            "biome": "forest",
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "tension": {"level": 3, "label": "moderate"},
        }

        # Store the region data
        self.region_repo.update_region_data("test_region", region_data)

        # Retrieve the region data
        retrieved_data = self.region_repo.get_region_data("test_region")

        # Check that the data was stored and retrieved correctly
        self.assertEqual(retrieved_data["id"], "test_region")
        self.assertEqual(retrieved_data["name"], "Test Region")
        self.assertEqual(retrieved_data["biome"], "forest")
        self.assertEqual(retrieved_data["version"], 1)
        self.assertEqual(retrieved_data["tension"]["level"], 3)

        # Update the region data
        region_data["name"] = "Updated Region"
        region_data["version"] = 2
        region_data["tension"]["level"] = 5
        region_data["tension"]["label"] = "high"
        self.region_repo.update_region_data("test_region", region_data)

        # Retrieve the updated data
        updated_data = self.region_repo.get_region_data("test_region")

        # Check that the data was updated correctly
        self.assertEqual(updated_data["name"], "Updated Region")
        self.assertEqual(updated_data["version"], 2)
        self.assertEqual(updated_data["tension"]["level"], 5)
        self.assertEqual(updated_data["tension"]["label"], "high")

        # Check file persistence
        region_file = os.path.join(
            self.temp_dir, "world", "regions", "test_region.json"
        )
        self.assertTrue(os.path.exists(region_file))

        with open(region_file, "r") as f: pass
            file_data = json.load(f)
            self.assertEqual(file_data["name"], "Updated Region")
            self.assertEqual(file_data["version"], 2)

    def test_npc_repository(self): pass
        """Test that the NPC repository properly stores and retrieves data."""
        # Create test NPC data
        npc_data = {
            "id": "test_npc",
            "name": "Test NPC",
            "region_id": "test_region",
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "motifs": {
                "active": [
                    {
                        "theme": "betrayal",
                        "weight": 3,
                        "added_at": datetime.utcnow().isoformat(),
                    }
                ],
                "expired": [],
            },
            "faction_affiliations": [{"id": "test_faction", "loyalty": 2}],
        }

        # Store the NPC data
        self.npc_repo.update_npc_data("test_npc", npc_data)

        # Retrieve the NPC data
        retrieved_data = self.npc_repo.get_npc_data("test_npc")

        # Check that the data was stored and retrieved correctly
        self.assertEqual(retrieved_data["id"], "test_npc")
        self.assertEqual(retrieved_data["name"], "Test NPC")
        self.assertEqual(retrieved_data["region_id"], "test_region")
        self.assertEqual(retrieved_data["version"], 1)
        self.assertEqual(len(retrieved_data["motifs"]["active"]), 1)
        self.assertEqual(retrieved_data["motifs"]["active"][0]["theme"], "betrayal")
        self.assertEqual(len(retrieved_data["faction_affiliations"]), 1)
        self.assertEqual(
            retrieved_data["faction_affiliations"][0]["id"], "test_faction"
        )

        # Update the NPC data
        npc_data["name"] = "Updated NPC"
        npc_data["version"] = 2
        npc_data["motifs"]["active"].append(
            {"theme": "revenge", "weight": 4, "added_at": datetime.utcnow().isoformat()}
        )
        npc_data["faction_affiliations"].append({"id": "new_faction", "loyalty": 1})
        self.npc_repo.update_npc_data("test_npc", npc_data)

        # Retrieve the updated data
        updated_data = self.npc_repo.get_npc_data("test_npc")

        # Check that the data was updated correctly
        self.assertEqual(updated_data["name"], "Updated NPC")
        self.assertEqual(updated_data["version"], 2)
        self.assertEqual(len(updated_data["motifs"]["active"]), 2)
        self.assertEqual(updated_data["motifs"]["active"][1]["theme"], "revenge")
        self.assertEqual(len(updated_data["faction_affiliations"]), 2)
        self.assertEqual(updated_data["faction_affiliations"][1]["id"], "new_faction")

        # Check file persistence
        npc_file = os.path.join(self.temp_dir, "entities", "npcs", "test_npc.json")
        self.assertTrue(os.path.exists(npc_file))

        with open(npc_file, "r") as f: pass
            file_data = json.load(f)
            self.assertEqual(file_data["name"], "Updated NPC")
            self.assertEqual(file_data["version"], 2)

    def test_faction_repository(self): pass
        """Test that the faction repository properly stores and retrieves data."""
        # Create test faction data
        faction_data = {
            "id": "test_faction",
            "name": "Test Faction",
            "description": "A faction for testing",
            "type": "political",
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "regions": ["test_region"],
            "power_level": 5,
            "stability": 0.8,
        }

        # Store the faction data
        self.faction_repo.update_faction_data("test_faction", faction_data)

        # Retrieve the faction data
        retrieved_data = self.faction_repo.get_faction_data("test_faction")

        # Check that the data was stored and retrieved correctly
        self.assertEqual(retrieved_data["id"], "test_faction")
        self.assertEqual(retrieved_data["name"], "Test Faction")
        self.assertEqual(retrieved_data["type"], "political")
        self.assertEqual(retrieved_data["version"], 1)
        self.assertEqual(retrieved_data["regions"], ["test_region"])
        self.assertEqual(retrieved_data["power_level"], 5)
        self.assertEqual(retrieved_data["stability"], 0.8)

        # Update the faction data
        faction_data["name"] = "Updated Faction"
        faction_data["version"] = 2
        faction_data["regions"].append("new_region")
        faction_data["power_level"] = 7
        self.faction_repo.update_faction_data("test_faction", faction_data)

        # Retrieve the updated data
        updated_data = self.faction_repo.get_faction_data("test_faction")

        # Check that the data was updated correctly
        self.assertEqual(updated_data["name"], "Updated Faction")
        self.assertEqual(updated_data["version"], 2)
        self.assertEqual(updated_data["regions"], ["test_region", "new_region"])
        self.assertEqual(updated_data["power_level"], 7)

        # Check file persistence
        faction_file = os.path.join(
            self.temp_dir, "systems", "faction", "test_faction.json"
        )
        self.assertTrue(os.path.exists(faction_file))

        with open(faction_file, "r") as f: pass
            file_data = json.load(f)
            self.assertEqual(file_data["name"], "Updated Faction")
            self.assertEqual(file_data["version"], 2)

    def test_motif_repository(self): pass
        """Test that the motif repository properly stores and retrieves data."""
        # Create test motif data
        motif_data = {
            "id": "test_motif",
            "name": "Test Motif",
            "description": "A motif for testing",
            "category": "betrayal",
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "intensity": 4,
            "associated_emotions": ["anger", "sadness"],
        }

        # Store the motif data
        self.motif_repo.update_motif_data("test_motif", motif_data)

        # Retrieve the motif data
        retrieved_data = self.motif_repo.get_motif_data("test_motif")

        # Check that the data was stored and retrieved correctly
        self.assertEqual(retrieved_data["id"], "test_motif")
        self.assertEqual(retrieved_data["name"], "Test Motif")
        self.assertEqual(retrieved_data["category"], "betrayal")
        self.assertEqual(retrieved_data["version"], 1)
        self.assertEqual(retrieved_data["intensity"], 4)
        self.assertEqual(retrieved_data["associated_emotions"], ["anger", "sadness"])

        # Update the motif data
        motif_data["name"] = "Updated Motif"
        motif_data["version"] = 2
        motif_data["intensity"] = 6
        motif_data["associated_emotions"].append("fear")
        self.motif_repo.update_motif_data("test_motif", motif_data)

        # Retrieve the updated data
        updated_data = self.motif_repo.get_motif_data("test_motif")

        # Check that the data was updated correctly
        self.assertEqual(updated_data["name"], "Updated Motif")
        self.assertEqual(updated_data["version"], 2)
        self.assertEqual(updated_data["intensity"], 6)
        self.assertEqual(
            updated_data["associated_emotions"], ["anger", "sadness", "fear"]
        )

        # Check file persistence
        motif_file = os.path.join(self.temp_dir, "systems", "motif", "test_motif.json")
        self.assertTrue(os.path.exists(motif_file))

        with open(motif_file, "r") as f: pass
            file_data = json.load(f)
            self.assertEqual(file_data["name"], "Updated Motif")
            self.assertEqual(file_data["version"], 2)

    def test_rumor_repository(self): pass
        """Test that the rumor repository properly stores and retrieves data."""
        # Create test rumor data
        rumor_data = {
            "id": "test_rumor",
            "content": "A test rumor about a hidden treasure",
            "rumor_type": "treasure",
            "source_entity_id": "test_npc",
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "truth_value": 0.7,
            "severity": 2,
            "region_id": "test_region",
        }

        # Store the rumor data
        self.rumor_repo.update_rumor_data("test_rumor", rumor_data)

        # Retrieve the rumor data
        retrieved_data = self.rumor_repo.get_rumor_data("test_rumor")

        # Check that the data was stored and retrieved correctly
        self.assertEqual(retrieved_data["id"], "test_rumor")
        self.assertEqual(
            retrieved_data["content"], "A test rumor about a hidden treasure"
        )
        self.assertEqual(retrieved_data["rumor_type"], "treasure")
        self.assertEqual(retrieved_data["version"], 1)
        self.assertEqual(retrieved_data["truth_value"], 0.7)
        self.assertEqual(retrieved_data["severity"], 2)
        self.assertEqual(retrieved_data["region_id"], "test_region")

        # Update the rumor data
        rumor_data["content"] = "Updated rumor content"
        rumor_data["version"] = 2
        rumor_data["truth_value"] = 0.5
        rumor_data["severity"] = 3
        self.rumor_repo.update_rumor_data("test_rumor", rumor_data)

        # Retrieve the updated data
        updated_data = self.rumor_repo.get_rumor_data("test_rumor")

        # Check that the data was updated correctly
        self.assertEqual(updated_data["content"], "Updated rumor content")
        self.assertEqual(updated_data["version"], 2)
        self.assertEqual(updated_data["truth_value"], 0.5)
        self.assertEqual(updated_data["severity"], 3)

        # Check file persistence
        rumor_file = os.path.join(self.temp_dir, "systems", "rumor", "test_rumor.json")
        self.assertTrue(os.path.exists(rumor_file))

        with open(rumor_file, "r") as f: pass
            file_data = json.load(f)
            self.assertEqual(file_data["content"], "Updated rumor content")
            self.assertEqual(file_data["version"], 2)

    def test_version_increment(self): pass
        """Test that the repositories properly handle version incrementing."""
        # Create test player data
        player_data = {
            "id": "test_player",
            "name": "Test Player",
            "region_id": "test_region",
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Store the player data
        self.player_repo.update_player_data("test_player", player_data)

        # Make multiple updates
        for i in range(2, 6): pass
            player_data["name"] = f"Test Player Version {i}"
            player_data["version"] = i
            self.player_repo.update_player_data("test_player", player_data)

        # Retrieve the data
        retrieved_data = self.player_repo.get_player_data("test_player")

        # Check that the version was properly incremented
        self.assertEqual(retrieved_data["version"], 5)
        self.assertEqual(retrieved_data["name"], "Test Player Version 5")

    def test_all_ids_retrieval(self): pass
        """Test that repositories correctly retrieve all entity IDs."""
        # Create multiple player entities
        for i in range(1, 6): pass
            player_data = {
                "id": f"player_{i}",
                "name": f"Player {i}",
                "region_id": "test_region",
                "version": 1,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            self.player_repo.update_player_data(f"player_{i}", player_data)

        # Retrieve all player IDs
        player_ids = self.player_repo.get_all_player_ids()

        # Check that all IDs are retrieved
        self.assertEqual(len(player_ids), 5)
        for i in range(1, 6): pass
            self.assertIn(f"player_{i}", player_ids)

        # Create multiple region entities
        for i in range(1, 4): pass
            region_data = {
                "id": f"region_{i}",
                "name": f"Region {i}",
                "version": 1,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }
            self.region_repo.update_region_data(f"region_{i}", region_data)

        # Retrieve all region IDs
        region_ids = self.region_repo.get_all_region_ids()

        # Check that all IDs are retrieved
        self.assertEqual(len(region_ids), 3)
        for i in range(1, 4): pass
            self.assertIn(f"region_{i}", region_ids)


if __name__ == "__main__": pass
    unittest.main()
