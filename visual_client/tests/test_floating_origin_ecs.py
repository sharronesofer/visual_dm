"""
Unit tests for the floating origin ECS integration.
"""

import unittest
from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
from visual_client.core.utils.floating_origin import FloatingOrigin
from visual_client.core.utils.floating_origin_ecs import (
    TransformComponent,
    FloatingOriginComponent,
    EntityComponentSystem,
    FloatingOriginSystem
)

class TestTransformComponent(unittest.TestCase):
    """Test the TransformComponent class."""
    
    def test_initialization(self):
        """Test component initialization."""
        transform = TransformComponent()
        self.assertEqual(transform.global_x, 0.0)
        self.assertEqual(transform.global_y, 0.0)
        self.assertEqual(transform.global_z, 0.0)
        self.assertEqual(transform.local_x, 0.0)
        self.assertEqual(transform.local_y, 0.0)
        self.assertEqual(transform.local_z, 0.0)
        self.assertEqual(transform.rotation, 0.0)
        self.assertEqual(transform.scale, 1.0)
        
        # Test with custom values
        transform = TransformComponent(
            global_x=10.0,
            global_y=20.0,
            global_z=30.0,
            local_x=5.0,
            local_y=15.0,
            local_z=25.0,
            rotation=45.0,
            scale=2.0
        )
        self.assertEqual(transform.global_x, 10.0)
        self.assertEqual(transform.global_y, 20.0)
        self.assertEqual(transform.global_z, 30.0)
        self.assertEqual(transform.local_x, 5.0)
        self.assertEqual(transform.local_y, 15.0)
        self.assertEqual(transform.local_z, 25.0)
        self.assertEqual(transform.rotation, 45.0)
        self.assertEqual(transform.scale, 2.0)
    
    def test_get_global_position(self):
        """Test getting global position."""
        transform = TransformComponent(global_x=10.0, global_y=20.0, global_z=30.0)
        pos = transform.get_global_position()
        self.assertEqual(pos, GlobalCoord(10.0, 20.0, 30.0))
    
    def test_set_global_position(self):
        """Test setting global position."""
        transform = TransformComponent()
        transform.set_global_position(10.0, 20.0, 30.0)
        self.assertEqual(transform.global_x, 10.0)
        self.assertEqual(transform.global_y, 20.0)
        self.assertEqual(transform.global_z, 30.0)
    
    def test_get_local_position(self):
        """Test getting local position."""
        transform = TransformComponent(local_x=10.0, local_y=20.0, local_z=30.0)
        pos = transform.get_local_position()
        self.assertEqual(pos, LocalCoord(10.0, 20.0, 30.0))
    
    def test_set_local_position(self):
        """Test setting local position."""
        transform = TransformComponent()
        transform.set_local_position(10.0, 20.0, 30.0)
        self.assertEqual(transform.local_x, 10.0)
        self.assertEqual(transform.local_y, 20.0)
        self.assertEqual(transform.local_z, 30.0)
    
    def test_shift_position(self):
        """Test shifting position."""
        transform = TransformComponent(global_x=10.0, global_y=20.0, global_z=30.0)
        transform.shift_position(5.0, 10.0, 15.0)
        self.assertEqual(transform.global_x, 15.0)
        self.assertEqual(transform.global_y, 30.0)
        self.assertEqual(transform.global_z, 45.0)

class TestFloatingOriginComponent(unittest.TestCase):
    """Test the FloatingOriginComponent class."""
    
    def test_initialization(self):
        """Test component initialization."""
        component = FloatingOriginComponent()
        self.assertFalse(component.registered)
        self.assertEqual(component.group, "default")
        
        # Test with custom values
        component = FloatingOriginComponent(registered=True, group="test_group")
        self.assertTrue(component.registered)
        self.assertEqual(component.group, "test_group")

class TestEntityComponentSystem(unittest.TestCase):
    """Test the EntityComponentSystem class."""
    
    def setUp(self):
        """Set up a fresh ECS for each test."""
        self.ecs = EntityComponentSystem()
    
    def test_create_entity(self):
        """Test entity creation."""
        entity_id = self.ecs.create_entity("test_entity")
        self.assertEqual(entity_id, "test_entity")
        self.assertIn("test_entity", self.ecs.entities)
        
        # Test duplicate entity
        with self.assertRaises(ValueError):
            self.ecs.create_entity("test_entity")
    
    def test_add_component(self):
        """Test adding components to entities."""
        entity_id = self.ecs.create_entity("test_entity")
        
        # Add a component
        transform = TransformComponent(global_x=10.0, global_y=20.0, global_z=30.0)
        self.ecs.add_component(entity_id, "transform", transform)
        
        # Verify component was added
        self.assertIn("transform", self.ecs.entities[entity_id])
        self.assertEqual(self.ecs.entities[entity_id]["transform"], transform)
        
        # Test adding to non-existent entity
        with self.assertRaises(ValueError):
            self.ecs.add_component("non_existent", "transform", transform)
    
    def test_get_component(self):
        """Test getting components from entities."""
        entity_id = self.ecs.create_entity("test_entity")
        
        # Add a component
        transform = TransformComponent(global_x=10.0, global_y=20.0, global_z=30.0)
        self.ecs.add_component(entity_id, "transform", transform)
        
        # Get the component
        retrieved = self.ecs.get_component(entity_id, "transform")
        self.assertEqual(retrieved, transform)
        
        # Get non-existent component
        self.assertIsNone(self.ecs.get_component(entity_id, "non_existent"))
        
        # Get from non-existent entity
        with self.assertRaises(ValueError):
            self.ecs.get_component("non_existent", "transform")
    
    def test_has_component(self):
        """Test checking if entity has component."""
        entity_id = self.ecs.create_entity("test_entity")
        
        # Add a component
        transform = TransformComponent()
        self.ecs.add_component(entity_id, "transform", transform)
        
        # Check has component
        self.assertTrue(self.ecs.has_component(entity_id, "transform"))
        self.assertFalse(self.ecs.has_component(entity_id, "non_existent"))
        
        # Check non-existent entity
        self.assertFalse(self.ecs.has_component("non_existent", "transform"))
    
    def test_get_entities_with_components(self):
        """Test getting entities with specific components."""
        # Create entities
        entity1 = self.ecs.create_entity("entity1")
        entity2 = self.ecs.create_entity("entity2")
        entity3 = self.ecs.create_entity("entity3")
        
        # Add components
        self.ecs.add_component(entity1, "transform", TransformComponent())
        self.ecs.add_component(entity1, "floating_origin", FloatingOriginComponent())
        
        self.ecs.add_component(entity2, "transform", TransformComponent())
        
        self.ecs.add_component(entity3, "floating_origin", FloatingOriginComponent())
        
        # Get entities with single component
        with_transform = self.ecs.get_entities_with_components("transform")
        self.assertEqual(set(with_transform), {"entity1", "entity2"})
        
        with_fo = self.ecs.get_entities_with_components("floating_origin")
        self.assertEqual(set(with_fo), {"entity1", "entity3"})
        
        # Get entities with multiple components
        with_both = self.ecs.get_entities_with_components("transform", "floating_origin")
        self.assertEqual(with_both, ["entity1"])
        
        # Get entities with non-existent component
        with_non_existent = self.ecs.get_entities_with_components("non_existent")
        self.assertEqual(with_non_existent, [])
    
    def test_remove_entity(self):
        """Test removing entities."""
        entity_id = self.ecs.create_entity("test_entity")
        
        # Add a component
        self.ecs.add_component(entity_id, "transform", TransformComponent())
        
        # Remove entity
        self.ecs.remove_entity(entity_id)
        
        # Verify entity is removed
        self.assertNotIn(entity_id, self.ecs.entities)
        
        # Removing non-existent entity shouldn't raise error
        self.ecs.remove_entity("non_existent")

class TestFloatingOriginSystem(unittest.TestCase):
    """Test the FloatingOriginSystem class."""
    
    def setUp(self):
        """Set up a fresh ECS with floating origin for each test."""
        self.floating_origin = FloatingOrigin()
        self.ecs = EntityComponentSystem(floating_origin=self.floating_origin)
        self.system = FloatingOriginSystem()
    
    def test_update_no_player(self):
        """Test system update with no player entity."""
        # Create an entity
        entity_id = self.ecs.create_entity("test_entity")
        self.ecs.add_component(entity_id, "transform", TransformComponent(
            global_x=100.0, global_y=200.0, global_z=300.0
        ))
        self.ecs.add_component(entity_id, "floating_origin", FloatingOriginComponent())
        
        # Run system update
        self.system.update(self.ecs, 0.016)
        
        # Verify local position is updated
        transform = self.ecs.get_component(entity_id, "transform")
        self.assertEqual(transform.local_x, 100.0)
        self.assertEqual(transform.local_y, 200.0)
        self.assertEqual(transform.local_z, 300.0)
    
    def test_update_with_player(self):
        """Test system update with player entity."""
        # Create player entity
        player_id = self.ecs.create_entity("player")
        self.ecs.add_component(player_id, "transform", TransformComponent(
            global_x=2000.0, global_y=2000.0, global_z=0.0
        ))
        self.ecs.add_component(player_id, "floating_origin", FloatingOriginComponent(group="player"))
        self.ecs.add_component(player_id, "player", {})
        
        # Create another entity
        entity_id = self.ecs.create_entity("test_entity")
        self.ecs.add_component(entity_id, "transform", TransformComponent(
            global_x=2100.0, global_y=2200.0, global_z=0.0
        ))
        self.ecs.add_component(entity_id, "floating_origin", FloatingOriginComponent())
        
        # Run system update (should trigger origin shift)
        self.system.update(self.ecs, 0.016)
        
        # Verify player local position
        player_transform = self.ecs.get_component(player_id, "transform")
        self.assertAlmostEqual(player_transform.local_x, 0.0)
        self.assertAlmostEqual(player_transform.local_y, 0.0)
        self.assertAlmostEqual(player_transform.local_z, 0.0)
        
        # Verify other entity local position
        entity_transform = self.ecs.get_component(entity_id, "transform")
        self.assertAlmostEqual(entity_transform.local_x, 100.0)
        self.assertAlmostEqual(entity_transform.local_y, 200.0)
        self.assertAlmostEqual(entity_transform.local_z, 0.0)
        
        # Test floating origin metrics
        metrics = self.ecs.floating_origin.get_metrics()
        self.assertEqual(metrics["shift_count"], 1)
        self.assertEqual(metrics["total_entities_shifted"], 2)

class TestEcsFloatingOriginIntegration(unittest.TestCase):
    """Test the integration of ECS with floating origin."""
    
    def setUp(self):
        """Set up a fresh ECS with floating origin for each test."""
        self.floating_origin = FloatingOrigin()
        self.ecs = EntityComponentSystem(floating_origin=self.floating_origin)
        self.ecs.add_system(FloatingOriginSystem.update)
    
    def test_auto_registration(self):
        """Test auto-registration of entities with floating origin component."""
        # Create entity with transform component
        entity_id = self.ecs.create_entity("test_entity")
        self.ecs.add_component(entity_id, "transform", TransformComponent())
        
        # Add floating origin component - should auto-register
        self.ecs.add_component(entity_id, "floating_origin", FloatingOriginComponent())
        
        # Verify entity is registered with floating origin
        self.assertIn(entity_id, self.floating_origin.registered_entities)
        self.assertTrue(self.ecs.get_component(entity_id, "floating_origin").registered)
    
    def test_origin_shift_propagation(self):
        """Test that origin shifts properly update entity positions."""
        # Create player entity that will trigger origin shift
        player_id = self.ecs.create_entity("player")
        player_transform = TransformComponent(global_x=0.0, global_y=0.0, global_z=0.0)
        self.ecs.add_component(player_id, "transform", player_transform)
        self.ecs.add_component(player_id, "floating_origin", FloatingOriginComponent(group="player"))
        self.ecs.add_component(player_id, "player", {})
        
        # Create other entities at various positions
        entities = []
        for i in range(5):
            entity_id = self.ecs.create_entity(f"entity_{i}")
            entity_transform = TransformComponent(
                global_x=i * 100.0, 
                global_y=i * 100.0, 
                global_z=0.0
            )
            self.ecs.add_component(entity_id, "transform", entity_transform)
            self.ecs.add_component(entity_id, "floating_origin", FloatingOriginComponent())
            entities.append(entity_id)
        
        # Initial update to establish baseline
        self.ecs.update(0.016)
        
        # Move player far enough to trigger origin shift
        player_transform.set_global_position(2000.0, 2000.0, 0.0)
        
        # Update system - should trigger origin shift
        self.ecs.update(0.016)
        
        # Verify player position
        self.assertEqual(player_transform.global_x, 2000.0)
        self.assertEqual(player_transform.global_y, 2000.0)
        self.assertEqual(player_transform.local_x, 0.0)  # Local position should be at origin
        self.assertEqual(player_transform.local_y, 0.0)
        
        # Verify other entities were shifted
        for i, entity_id in enumerate(entities):
            entity_transform = self.ecs.get_component(entity_id, "transform")
            
            # Global position should still reflect absolute position
            self.assertEqual(entity_transform.global_x, i * 100.0)
            self.assertEqual(entity_transform.global_y, i * 100.0)
            
            # Local position should be offset by player position
            self.assertAlmostEqual(entity_transform.local_x, i * 100.0 - 2000.0)
            self.assertAlmostEqual(entity_transform.local_y, i * 100.0 - 2000.0)
        
        # Verify metrics
        metrics = self.floating_origin.get_metrics()
        self.assertEqual(metrics["shift_count"], 1)
        self.assertEqual(metrics["total_entities_shifted"], 6)  # player + 5 entities

if __name__ == '__main__':
    unittest.main() 