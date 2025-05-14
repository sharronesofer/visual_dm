"""
Integration tests for the World class with persistence system.

This module tests the integration between the World class and the persistence system,
verifying that worlds can be properly saved, loaded, and versioned.
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import time
import json
from datetime import datetime

from app.core.models.world import World
from app.core.models.character import Character
from app.core.models.location import Location
from app.core.models.item import Item
from app.core.persistence.world_persistence import WorldPersistenceManager, FileSystemStorageStrategy


class TestWorldWithPersistence(unittest.TestCase):
    """Test the integration of World with the persistence system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_world_save_load(self):
        """Test saving and loading a world."""
        # Create a world
        world = World(
            name="Test World",
            description="A world for testing persistence",
        )
        
        # Add some entities
        character = Character(name="Test Character", description="A test character")
        location = Location(name="Test Location", description="A test location")
        item = Item(name="Test Item", description="A test item")
        
        world.add_entity(character)
        world.add_entity(location)
        world.add_entity(item)
        
        # Initialize persistence
        world.initialize_persistence(self.temp_dir)
        
        # Save the world
        saved = world.save()
        self.assertTrue(saved, "Failed to save world")
        
        # Load the world
        loaded_world = World.load(world.world_id, self.temp_dir)
        
        # Verify loaded world
        self.assertIsNotNone(loaded_world, "Failed to load world")
        self.assertEqual(loaded_world.name, world.name)
        self.assertEqual(loaded_world.description, world.description)
        self.assertEqual(loaded_world.world_id, world.world_id)
        
        # Verify entities
        loaded_entities = loaded_world.get_all_entities()
        self.assertEqual(len(loaded_entities), 3)
        
        # Verify specific entity types
        loaded_characters = loaded_world.get_characters()
        loaded_locations = loaded_world.get_locations()
        loaded_items = loaded_world.get_items()
        
        self.assertEqual(len(loaded_characters), 1)
        self.assertEqual(len(loaded_locations), 1)
        self.assertEqual(len(loaded_items), 1)
        
        # Verify character details
        self.assertEqual(loaded_characters[0].name, character.name)
    
    def test_world_versioning(self):
        """Test world versioning and rollback."""
        # Create a world
        world = World(
            name="Version Test World",
            description="A world for testing versioning",
        )
        
        # Initialize persistence
        world.initialize_persistence(self.temp_dir)
        
        # Save initial version
        world.save()
        
        # Create a snapshot
        v1_id = world.create_snapshot("Initial version")
        self.assertIsNotNone(v1_id)
        
        # Modify world
        world.name = "Updated World Name"
        world.description = "Updated description"
        
        # Add a character
        character = Character(name="New Character", description="Added after v1")
        world.add_entity(character)
        
        # Create another snapshot
        world.save()
        v2_id = world.create_snapshot("Updated version with character")
        self.assertIsNotNone(v2_id)
        
        # Roll back to v1
        rollback_success = world.rollback_to_version(v1_id)
        self.assertTrue(rollback_success)
        
        # Verify rollback
        self.assertEqual(world.name, "Version Test World")
        self.assertEqual(world.description, "A world for testing versioning")
        self.assertEqual(len(world.get_characters()), 0)
        
        # Roll forward to v2
        rollback_success = world.rollback_to_version(v2_id)
        self.assertTrue(rollback_success)
        
        # Verify roll forward
        self.assertEqual(world.name, "Updated World Name")
        self.assertEqual(world.description, "Updated description")
        self.assertEqual(len(world.get_characters()), 1)
    
    def test_metadata_persistence(self):
        """Test that metadata is persisted."""
        # Create a world
        world = World(
            name="Metadata Test World",
            description="A world for testing metadata persistence",
        )
        
        # Initialize persistence
        world.initialize_persistence(self.temp_dir)
        
        # Set metadata
        world.update_metadata("created_by", "Test User")
        world.update_metadata("genre", "Fantasy")
        world.update_metadata("tags", ["test", "fantasy", "persistence"])
        
        # Save the world
        world.save()
        
        # Load the world
        loaded_world = World.load(world.world_id, self.temp_dir)
        
        # Verify metadata
        self.assertEqual(loaded_world.get_metadata("created_by"), "Test User")
        self.assertEqual(loaded_world.get_metadata("genre"), "Fantasy")
        self.assertEqual(loaded_world.get_metadata("tags"), ["test", "fantasy", "persistence"])
    
    def test_multiple_worlds(self):
        """Test managing multiple worlds with the same storage."""
        # Create worlds
        world1 = World(name="World 1")
        world2 = World(name="World 2")
        world3 = World(name="World 3")
        
        # Initialize persistence
        world1.initialize_persistence(self.temp_dir)
        world2.initialize_persistence(self.temp_dir)
        world3.initialize_persistence(self.temp_dir)
        
        # Save worlds
        world1.save()
        world2.save()
        world3.save()
        
        # Get world IDs
        world1_id = world1.world_id
        world2_id = world2.world_id
        world3_id = world3.world_id
        
        # Create a new persistence manager to check listing
        storage = FileSystemStorageStrategy(self.temp_dir)
        
        # List worlds
        world_ids = storage.list_worlds()
        
        # Verify all worlds are listed
        self.assertIn(world1_id, world_ids)
        self.assertIn(world2_id, world_ids)
        self.assertIn(world3_id, world_ids)
        
        # Load specific world
        loaded_world2 = World.load(world2_id, self.temp_dir)
        
        # Verify correct world loaded
        self.assertEqual(loaded_world2.name, "World 2")
    
    def test_transaction_integration(self):
        """Test integration with the transaction system."""
        # Create a world
        world = World(
            name="Transaction Test World",
            description="A world for testing transactions",
        )
        
        # Initialize persistence
        world.initialize_persistence(self.temp_dir)
        world.save()
        
        # Begin a transaction
        transaction = world.begin_transaction("Add entities batch")
        self.assertIsNotNone(transaction)
        
        # Add entities within transaction
        with transaction:
            character1 = Character(name="Character 1")
            character2 = Character(name="Character 2")
            location = Location(name="Location 1")
            
            world.add_entity(character1)
            world.add_entity(character2)
            world.add_entity(location)
        
        # Save the world
        world.save(create_snapshot=True, description="After transaction")
        
        # Load the world
        loaded_world = World.load(world.world_id, self.temp_dir)
        
        # Verify entities were saved
        self.assertEqual(len(loaded_world.get_characters()), 2)
        self.assertEqual(len(loaded_world.get_locations()), 1)
        
        # Check transaction was committed
        transaction_manager = world.persistence_manager.get_transaction_manager(world.world_id)
        transactions = transaction_manager.get_transaction_history()
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].name, "Add entities batch")
        self.assertEqual(transactions[0].status, "committed")
    
    def test_complex_world_roundtrip(self):
        """Test a complex world with many entities and relationships."""
        # Create a world
        world = World(
            name="Complex World",
            description="A complex world with many entities and relationships",
        )
        
        # Add characters
        hero = Character(name="Hero", description="The main protagonist")
        villain = Character(name="Villain", description="The antagonist")
        ally = Character(name="Ally", description="Hero's friend")
        
        # Add locations
        castle = Location(name="Castle", description="The royal castle")
        village = Location(name="Village", description="A small village")
        dungeon = Location(name="Dungeon", description="A dark dungeon")
        
        # Add items
        sword = Item(name="Sword", description="A sharp sword")
        shield = Item(name="Shield", description="A sturdy shield")
        potion = Item(name="Potion", description="A healing potion")
        
        # Add entities to world
        world.add_entity(hero)
        world.add_entity(villain)
        world.add_entity(ally)
        world.add_entity(castle)
        world.add_entity(village)
        world.add_entity(dungeon)
        world.add_entity(sword)
        world.add_entity(shield)
        world.add_entity(potion)
        
        # Set up relationships
        hero.location_id = village.entity_id
        ally.location_id = village.entity_id
        villain.location_id = castle.entity_id
        
        hero.inventory.append(sword.entity_id)
        hero.inventory.append(shield.entity_id)
        ally.inventory.append(potion.entity_id)
        
        # Update entities
        world.state.update_entity(hero)
        world.state.update_entity(ally)
        world.state.update_entity(villain)
        
        # Initialize persistence and save
        world.initialize_persistence(self.temp_dir)
        world.save()
        
        # Load the world
        loaded_world = World.load(world.world_id, self.temp_dir)
        
        # Verify entity counts
        self.assertEqual(len(loaded_world.get_characters()), 3)
        self.assertEqual(len(loaded_world.get_locations()), 3)
        self.assertEqual(len(loaded_world.get_items()), 3)
        
        # Verify relationships
        loaded_hero = next((c for c in loaded_world.get_characters() if c.name == "Hero"), None)
        loaded_ally = next((c for c in loaded_world.get_characters() if c.name == "Ally"), None)
        loaded_villain = next((c for c in loaded_world.get_characters() if c.name == "Villain"), None)
        
        self.assertIsNotNone(loaded_hero)
        self.assertIsNotNone(loaded_ally)
        self.assertIsNotNone(loaded_villain)
        
        loaded_village = next((l for l in loaded_world.get_locations() if l.name == "Village"), None)
        loaded_castle = next((l for l in loaded_world.get_locations() if l.name == "Castle"), None)
        
        self.assertIsNotNone(loaded_village)
        self.assertIsNotNone(loaded_castle)
        
        # Verify character locations
        self.assertEqual(loaded_hero.location_id, loaded_village.entity_id)
        self.assertEqual(loaded_ally.location_id, loaded_village.entity_id)
        self.assertEqual(loaded_villain.location_id, loaded_castle.entity_id)
        
        # Verify inventories
        self.assertEqual(len(loaded_hero.inventory), 2)
        self.assertEqual(len(loaded_ally.inventory), 1)


if __name__ == "__main__":
    unittest.main() 