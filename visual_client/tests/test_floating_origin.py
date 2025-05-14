"""
Unit tests for the floating origin system.
Tests coordinate conversions, origin shifts, and entity registration.
"""

import unittest
import math
from visual_client.core.utils.coordinates import (
    GlobalCoord, LocalCoord, CoordinateSystem, 
    SHIFT_THRESHOLD, COORD_EPSILON
)
from visual_client.core.utils.floating_origin import FloatingOrigin, OriginShiftMetrics

class TestCoordinates(unittest.TestCase):
    """Test coordinate classes and conversions."""
    
    def test_global_coord(self):
        """Test GlobalCoord class."""
        coord = GlobalCoord(10.5, 20.5, 30.5)
        self.assertEqual(coord.x, 10.5)
        self.assertEqual(coord.y, 20.5)
        self.assertEqual(coord.z, 30.5)
        
        # Test string representation
        self.assertEqual(str(coord), "G(10.50, 20.50, 30.50)")
        
        # Test 2D constructor (z defaults to 0)
        coord_2d = GlobalCoord(10.5, 20.5)
        self.assertEqual(coord_2d.z, 0.0)
    
    def test_local_coord(self):
        """Test LocalCoord class."""
        coord = LocalCoord(15.5, 25.5, 35.5)
        self.assertEqual(coord.x, 15.5)
        self.assertEqual(coord.y, 25.5)
        self.assertEqual(coord.z, 35.5)
        
        # Test string representation
        self.assertEqual(str(coord), "L(15.50, 25.50, 35.50)")
        
        # Test 2D constructor (z defaults to 0)
        coord_2d = LocalCoord(15.5, 25.5)
        self.assertEqual(coord_2d.z, 0.0)
    
    def test_distance_calculation(self):
        """Test distance calculation methods."""
        coord1 = GlobalCoord(0.0, 0.0, 0.0)
        coord2 = GlobalCoord(3.0, 4.0, 0.0)
        
        # Distance should be 5 (Pythagorean theorem: 3-4-5 triangle)
        self.assertEqual(coord1.distance_to(coord2), 5.0)
        
        # Test 3D distance
        coord3 = GlobalCoord(3.0, 0.0, 4.0)
        self.assertEqual(coord1.distance_to(coord3), 5.0)
        
        # Test with LocalCoord
        local1 = LocalCoord(0.0, 0.0, 0.0)
        local2 = LocalCoord(3.0, 4.0, 0.0)
        self.assertEqual(local1.distance_to(local2), 5.0)

class TestCoordinateSystem(unittest.TestCase):
    """Test the CoordinateSystem class."""
    
    def setUp(self):
        """Set up a fresh coordinate system for each test."""
        self.coord_system = CoordinateSystem()
    
    def test_initial_state(self):
        """Test initial state of coordinate system."""
        origin = self.coord_system.origin.get_origin()
        self.assertEqual(origin.x, 0.0)
        self.assertEqual(origin.y, 0.0)
        self.assertEqual(origin.z, 0.0)
        
        self.assertEqual(len(self.coord_system.shift_listeners), 0)
        self.assertEqual(len(self.coord_system.get_shift_history()), 0)
    
    def test_global_to_local_conversion(self):
        """Test conversion from global to local coordinates."""
        # With origin at (0,0,0)
        global_coord = GlobalCoord(100.0, 200.0, 300.0)
        local_coord = self.coord_system.global_to_local(global_coord)
        
        self.assertEqual(local_coord.x, 100.0)
        self.assertEqual(local_coord.y, 200.0)
        self.assertEqual(local_coord.z, 300.0)
        
        # Shift origin to (50,50,50)
        self.coord_system.shift_origin(GlobalCoord(50.0, 50.0, 50.0))
        
        # Now the same global coord should have different local coords
        local_coord = self.coord_system.global_to_local(global_coord)
        self.assertEqual(local_coord.x, 50.0)  # 100 - 50
        self.assertEqual(local_coord.y, 150.0)  # 200 - 50
        self.assertEqual(local_coord.z, 250.0)  # 300 - 50
    
    def test_local_to_global_conversion(self):
        """Test conversion from local to global coordinates."""
        # With origin at (0,0,0)
        local_coord = LocalCoord(10.0, 20.0, 30.0)
        global_coord = self.coord_system.local_to_global(local_coord)
        
        self.assertEqual(global_coord.x, 10.0)
        self.assertEqual(global_coord.y, 20.0)
        self.assertEqual(global_coord.z, 30.0)
        
        # Shift origin to (100,100,100)
        self.coord_system.shift_origin(GlobalCoord(100.0, 100.0, 100.0))
        
        # Now the same local coord should have different global coords
        global_coord = self.coord_system.local_to_global(local_coord)
        self.assertEqual(global_coord.x, 110.0)  # 10 + 100
        self.assertEqual(global_coord.y, 120.0)  # 20 + 100
        self.assertEqual(global_coord.z, 130.0)  # 30 + 100
    
    def test_bidirectional_conversion(self):
        """Test that converting back and forth works correctly."""
        original_global = GlobalCoord(1234.56, 7890.12, 4321.98)
        
        # Convert to local and back
        local = self.coord_system.global_to_local(original_global)
        roundtrip_global = self.coord_system.local_to_global(local)
        
        # Should match the original
        self.assertAlmostEqual(original_global.x, roundtrip_global.x, places=10)
        self.assertAlmostEqual(original_global.y, roundtrip_global.y, places=10)
        self.assertAlmostEqual(original_global.z, roundtrip_global.z, places=10)
        
        # Shift origin
        self.coord_system.shift_origin(GlobalCoord(500.0, 600.0, 700.0))
        
        # Try again
        local = self.coord_system.global_to_local(original_global)
        roundtrip_global = self.coord_system.local_to_global(local)
        
        # Should still match
        self.assertAlmostEqual(original_global.x, roundtrip_global.x, places=10)
        self.assertAlmostEqual(original_global.y, roundtrip_global.y, places=10)
        self.assertAlmostEqual(original_global.z, roundtrip_global.z, places=10)
    
    def test_check_shift_needed(self):
        """Test the shift needed check logic."""
        # Player at origin - no shift needed
        self.assertFalse(self.coord_system.check_shift_needed(GlobalCoord(0.0, 0.0, 0.0)))
        
        # Player within threshold - no shift needed
        self.assertFalse(self.coord_system.check_shift_needed(GlobalCoord(SHIFT_THRESHOLD * 0.9, 0.0, 0.0)))
        
        # Player at exactly threshold - no shift needed
        # (Usually we want to shift just beyond the threshold)
        self.assertFalse(self.coord_system.check_shift_needed(GlobalCoord(SHIFT_THRESHOLD, 0.0, 0.0)))
        
        # Player beyond threshold - shift needed
        self.assertTrue(self.coord_system.check_shift_needed(GlobalCoord(SHIFT_THRESHOLD + 1.0, 0.0, 0.0)))
        
        # Player beyond threshold on diagonal - shift needed
        diagonal_dist = SHIFT_THRESHOLD / math.sqrt(2) + 1.0  # beyond threshold on diagonal
        self.assertTrue(self.coord_system.check_shift_needed(GlobalCoord(diagonal_dist, diagonal_dist, 0.0)))
    
    def test_shift_origin(self):
        """Test shifting the origin."""
        # Initial state
        self.assertEqual(self.coord_system.origin.global_x, 0.0)
        self.assertEqual(self.coord_system.origin.global_y, 0.0)
        self.assertEqual(self.coord_system.origin.global_z, 0.0)
        
        # Shift to (100,200,300)
        dx, dy, dz = self.coord_system.shift_origin(GlobalCoord(100.0, 200.0, 300.0))
        
        # Check return values
        self.assertEqual(dx, 100.0)
        self.assertEqual(dy, 200.0)
        self.assertEqual(dz, 300.0)
        
        # Check new origin
        self.assertEqual(self.coord_system.origin.global_x, 100.0)
        self.assertEqual(self.coord_system.origin.global_y, 200.0)
        self.assertEqual(self.coord_system.origin.global_z, 300.0)
        
        # Shift again
        dx, dy, dz = self.coord_system.shift_origin(GlobalCoord(150.0, 250.0, 350.0))
        
        # Check delta
        self.assertEqual(dx, 50.0)  # 150 - 100
        self.assertEqual(dy, 50.0)  # 250 - 200
        self.assertEqual(dz, 50.0)  # 350 - 300
        
        # Check shift history
        history = self.coord_system.get_shift_history()
        self.assertEqual(len(history), 2)
        
        first_shift = history[0]
        self.assertEqual(first_shift['id'], 1)
        self.assertEqual(first_shift['old_origin'], GlobalCoord(0.0, 0.0, 0.0))
        self.assertEqual(first_shift['new_origin'], GlobalCoord(100.0, 200.0, 300.0))
        self.assertEqual(first_shift['delta'], (100.0, 200.0, 300.0))
        
        second_shift = history[1]
        self.assertEqual(second_shift['id'], 2)
        self.assertEqual(second_shift['old_origin'], GlobalCoord(100.0, 200.0, 300.0))
        self.assertEqual(second_shift['new_origin'], GlobalCoord(150.0, 250.0, 350.0))
        self.assertEqual(second_shift['delta'], (50.0, 50.0, 50.0))
    
    def test_shift_listeners(self):
        """Test shift event notification system."""
        shift_events = []
        
        def listener1(delta):
            shift_events.append(('listener1', delta))
        
        def listener2(delta):
            shift_events.append(('listener2', delta))
        
        # Add listeners
        self.coord_system.add_shift_listener(listener1)
        self.coord_system.add_shift_listener(listener2)
        
        # Perform shift
        self.coord_system.shift_origin(GlobalCoord(100.0, 200.0, 300.0))
        
        # Check both listeners were called
        self.assertEqual(len(shift_events), 2)
        self.assertEqual(shift_events[0][0], 'listener1')
        self.assertEqual(shift_events[0][1], (100.0, 200.0, 300.0))
        self.assertEqual(shift_events[1][0], 'listener2')
        self.assertEqual(shift_events[1][1], (100.0, 200.0, 300.0))
        
        # Remove one listener
        self.coord_system.remove_shift_listener(listener1)
        
        # Clear events and perform another shift
        shift_events.clear()
        self.coord_system.shift_origin(GlobalCoord(150.0, 250.0, 350.0))
        
        # Only listener2 should be called
        self.assertEqual(len(shift_events), 1)
        self.assertEqual(shift_events[0][0], 'listener2')
        self.assertEqual(shift_events[0][1], (50.0, 50.0, 50.0))
    
    def test_get_total_shift(self):
        """Test getting total accumulated shift."""
        self.assertEqual(self.coord_system.get_total_shift(), (0.0, 0.0, 0.0))
        
        # Shift origin multiple times
        self.coord_system.shift_origin(GlobalCoord(100.0, 200.0, 300.0))
        self.coord_system.shift_origin(GlobalCoord(150.0, 250.0, 350.0))
        
        # Total shift should be latest origin
        self.assertEqual(self.coord_system.get_total_shift(), (150.0, 250.0, 350.0))

class TestOriginShiftMetrics(unittest.TestCase):
    """Test the OriginShiftMetrics class."""
    
    def test_metrics_initialization(self):
        """Test initialization of metrics."""
        metrics = OriginShiftMetrics()
        self.assertEqual(metrics.shift_count, 0)
        self.assertEqual(metrics.total_shift_time, 0.0)
        self.assertEqual(metrics.avg_shift_time, 0.0)
        self.assertEqual(metrics.max_shift_time, 0.0)
        self.assertEqual(metrics.last_shift_time, 0.0)
        self.assertEqual(metrics.total_entities_shifted, 0)
    
    def test_record_shift(self):
        """Test recording shift metrics."""
        metrics = OriginShiftMetrics()
        
        # Record first shift
        metrics.record_shift(0.1, 10)
        self.assertEqual(metrics.shift_count, 1)
        self.assertEqual(metrics.total_shift_time, 0.1)
        self.assertEqual(metrics.avg_shift_time, 0.1)
        self.assertEqual(metrics.max_shift_time, 0.1)
        self.assertEqual(metrics.last_shift_time, 0.1)
        self.assertEqual(metrics.total_entities_shifted, 10)
        
        # Record second shift (faster)
        metrics.record_shift(0.05, 15)
        self.assertEqual(metrics.shift_count, 2)
        self.assertEqual(metrics.total_shift_time, 0.15)
        self.assertEqual(metrics.avg_shift_time, 0.075)
        self.assertEqual(metrics.max_shift_time, 0.1)  # Max stays the same
        self.assertEqual(metrics.last_shift_time, 0.05)
        self.assertEqual(metrics.total_entities_shifted, 25)
        
        # Record third shift (slower than both)
        metrics.record_shift(0.2, 5)
        self.assertEqual(metrics.shift_count, 3)
        self.assertEqual(metrics.total_shift_time, 0.35)
        self.assertAlmostEqual(metrics.avg_shift_time, 0.1166666666666667)
        self.assertEqual(metrics.max_shift_time, 0.2)  # Max updated
        self.assertEqual(metrics.last_shift_time, 0.2)
        self.assertEqual(metrics.total_entities_shifted, 30)
    
    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        metrics = OriginShiftMetrics()
        metrics.record_shift(0.1, 10)
        metrics.record_shift(0.2, 20)
        
        metrics_dict = metrics.to_dict()
        self.assertEqual(metrics_dict['shift_count'], 2)
        self.assertEqual(metrics_dict['total_shift_time'], 0.3)
        self.assertEqual(metrics_dict['avg_shift_time'], 0.15)
        self.assertEqual(metrics_dict['max_shift_time'], 0.2)
        self.assertEqual(metrics_dict['last_shift_time'], 0.2)
        self.assertEqual(metrics_dict['total_entities_shifted'], 30)

class TestFloatingOrigin(unittest.TestCase):
    """Test the FloatingOrigin class."""
    
    def setUp(self):
        """Set up a fresh floating origin system for each test."""
        self.coord_system = CoordinateSystem()
        self.floating_origin = FloatingOrigin(self.coord_system)
    
    def test_initial_state(self):
        """Test initial state of floating origin system."""
        self.assertEqual(len(self.floating_origin.registered_entities), 0)
        self.assertEqual(self.floating_origin.last_shift_time, 0)
        self.assertFalse(self.floating_origin.debug_mode)
        self.assertEqual(self.floating_origin.metrics.shift_count, 0)
        self.assertEqual(len(self.floating_origin.entity_groups), 0)
    
    def test_entity_registration(self):
        """Test entity registration and unregistration."""
        # Define entity position getter and setter
        def get_pos():
            return GlobalCoord(10.0, 20.0, 30.0)
        
        def set_pos(dx, dy, dz):
            pass  # No-op for test
        
        # Register entity
        self.floating_origin.register_entity('entity1', get_pos, set_pos)
        self.assertEqual(len(self.floating_origin.registered_entities), 1)
        self.assertIn('entity1', self.floating_origin.registered_entities)
        
        # Register a second entity
        self.floating_origin.register_entity('entity2', get_pos, set_pos)
        self.assertEqual(len(self.floating_origin.registered_entities), 2)
        
        # Unregister entity
        self.floating_origin.unregister_entity('entity1')
        self.assertEqual(len(self.floating_origin.registered_entities), 1)
        self.assertNotIn('entity1', self.floating_origin.registered_entities)
        self.assertIn('entity2', self.floating_origin.registered_entities)
    
    def test_update_player_position_no_shift(self):
        """Test player position update with no shift needed."""
        # Player within threshold
        player_pos = GlobalCoord(SHIFT_THRESHOLD * 0.5, 0.0, 0.0)
        result = self.floating_origin.update_player_position(player_pos)
        
        # Should not perform shift
        self.assertFalse(result)
        self.assertEqual(self.coord_system.origin.global_x, 0.0)
        self.assertEqual(self.coord_system.origin.global_y, 0.0)
        self.assertEqual(self.coord_system.origin.global_z, 0.0)
    
    def test_update_player_position_with_shift(self):
        """Test player position update with shift needed."""
        # Set up a test entity
        entity_position = [0.0, 0.0, 0.0]  # Mutable to track updates
        shift_calls = []
        
        def get_pos():
            return GlobalCoord(*entity_position)
        
        def set_pos(dx, dy, dz):
            entity_position[0] += dx
            entity_position[1] += dy
            entity_position[2] += dz
            shift_calls.append((dx, dy, dz))
        
        self.floating_origin.register_entity('test_entity', get_pos, set_pos)
        
        # Player beyond threshold
        player_pos = GlobalCoord(SHIFT_THRESHOLD + 100.0, 200.0, 300.0)
        result = self.floating_origin.update_player_position(player_pos)
        
        # Should perform shift
        self.assertTrue(result)
        
        # Origin should be updated to player position
        self.assertEqual(self.coord_system.origin.global_x, player_pos.x)
        self.assertEqual(self.coord_system.origin.global_y, player_pos.y)
        self.assertEqual(self.coord_system.origin.global_z, player_pos.z)
        
        # Entity should be updated
        self.assertEqual(len(shift_calls), 1)
        
        # Entity should be shifted by negative delta (since world moves opposite to origin)
        dx, dy, dz = shift_calls[0]
        self.assertEqual(dx, -player_pos.x)
        self.assertEqual(dy, -player_pos.y)
        self.assertEqual(dz, -player_pos.z)
        
        # Metrics should be updated
        self.assertEqual(self.floating_origin.metrics.shift_count, 1)
        self.assertEqual(self.floating_origin.metrics.total_entities_shifted, 1)
    
    def test_coordinate_conversions(self):
        """Test convenience coordinate conversion methods."""
        # Set origin to non-zero
        self.coord_system.shift_origin(GlobalCoord(100.0, 200.0, 300.0))
        
        # Test global to local
        global_coord = GlobalCoord(150.0, 250.0, 350.0)
        local_coord = self.floating_origin.get_local_position(global_coord)
        
        self.assertEqual(local_coord.x, 50.0)  # 150 - 100
        self.assertEqual(local_coord.y, 50.0)  # 250 - 200
        self.assertEqual(local_coord.z, 50.0)  # 350 - 300
        
        # Test local to global
        local_coord = LocalCoord(25.0, 25.0, 25.0)
        global_coord = self.floating_origin.get_global_position(local_coord)
        
        self.assertEqual(global_coord.x, 125.0)  # 25 + 100
        self.assertEqual(global_coord.y, 225.0)  # 25 + 200
        self.assertEqual(global_coord.z, 325.0)  # 25 + 300
    
    def test_debug_mode(self):
        """Test debug mode toggle."""
        self.assertFalse(self.floating_origin.debug_mode)
        
        # Enable debug
        self.floating_origin.enable_debug(True)
        self.assertTrue(self.floating_origin.debug_mode)
        
        # Disable debug
        self.floating_origin.enable_debug(False)
        self.assertFalse(self.floating_origin.debug_mode)
    
    def test_get_metrics(self):
        """Test getting performance metrics."""
        # Set up a test entity
        def get_pos():
            return GlobalCoord(0.0, 0.0, 0.0)
        
        def set_pos(dx, dy, dz):
            pass
        
        self.floating_origin.register_entity('test_entity', get_pos, set_pos)
        
        # Initial metrics
        metrics = self.floating_origin.get_metrics()
        self.assertEqual(metrics['shift_count'], 0)
        
        # Perform a shift
        self.floating_origin.update_player_position(GlobalCoord(SHIFT_THRESHOLD + 100.0, 0.0, 0.0))
        
        # Metrics should be updated
        metrics = self.floating_origin.get_metrics()
        self.assertEqual(metrics['shift_count'], 1)
        self.assertEqual(metrics['total_entities_shifted'], 1)
        self.assertGreater(metrics['total_shift_time'], 0)
    
    def test_batch_register_entities(self):
        """Test batch registration of entities."""
        entities = []
        for i in range(10):
            def get_pos(i=i):  # Capture i in closure
                return GlobalCoord(i*10.0, i*20.0, i*30.0)
            
            def set_pos(dx, dy, dz, i=i):  # Capture i in closure
                pass
            
            entities.append((f"entity{i}", get_pos, set_pos))
        
        # Register in batch
        self.floating_origin.batch_register_entities(entities, group="test_group")
        
        # Check registration
        self.assertEqual(len(self.floating_origin.registered_entities), 10)
        for i in range(10):
            self.assertIn(f"entity{i}", self.floating_origin.registered_entities)
            self.assertEqual(self.floating_origin.registered_entities[f"entity{i}"]["group"], "test_group")
        
        # Check group
        self.assertIn("test_group", self.floating_origin.entity_groups)
        self.assertEqual(len(self.floating_origin.entity_groups["test_group"]), 10)
    
    def test_unregister_group(self):
        """Test unregistering a group of entities."""
        # Register some entities in different groups
        def dummy_get_pos():
            return GlobalCoord(0.0, 0.0, 0.0)
        
        def dummy_set_pos(dx, dy, dz):
            pass
        
        for i in range(5):
            self.floating_origin.register_entity(f"group1_entity{i}", dummy_get_pos, dummy_set_pos, group="group1")
            
        for i in range(3):
            self.floating_origin.register_entity(f"group2_entity{i}", dummy_get_pos, dummy_set_pos, group="group2")
        
        # Initial state check
        self.assertEqual(len(self.floating_origin.registered_entities), 8)
        self.assertEqual(len(self.floating_origin.entity_groups), 2)
        
        # Unregister group1
        count = self.floating_origin.unregister_group("group1")
        
        # Check unregistration
        self.assertEqual(count, 5)
        self.assertEqual(len(self.floating_origin.registered_entities), 3)
        self.assertEqual(len(self.floating_origin.entity_groups), 1)
        self.assertNotIn("group1", self.floating_origin.entity_groups)
        self.assertIn("group2", self.floating_origin.entity_groups)
        
        # Try unregistering non-existent group
        count = self.floating_origin.unregister_group("non_existent")
        self.assertEqual(count, 0)
    
    def test_get_entity_groups(self):
        """Test getting entity group information."""
        # Register some entities in different groups
        def dummy_get_pos():
            return GlobalCoord(0.0, 0.0, 0.0)
        
        def dummy_set_pos(dx, dy, dz):
            pass
        
        for i in range(5):
            self.floating_origin.register_entity(f"group1_entity{i}", dummy_get_pos, dummy_set_pos, group="group1")
            
        for i in range(3):
            self.floating_origin.register_entity(f"group2_entity{i}", dummy_get_pos, dummy_set_pos, group="group2")
        
        # Get group info
        groups = self.floating_origin.get_entity_groups()
        
        # Check group counts
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups["group1"], 5)
        self.assertEqual(groups["group2"], 3)
    
    def test_serialize_state(self):
        """Test serializing the floating origin state."""
        # Register an entity
        def dummy_get_pos():
            return GlobalCoord(0.0, 0.0, 0.0)
        
        def dummy_set_pos(dx, dy, dz):
            pass
        
        self.floating_origin.register_entity("test_entity", dummy_get_pos, dummy_set_pos, group="test_group")
        
        # Perform a shift
        self.floating_origin.update_player_position(GlobalCoord(SHIFT_THRESHOLD + 100.0, 200.0, 300.0))
        
        # Get serialized state
        state = self.floating_origin.serialize_state()
        
        # Check state
        self.assertEqual(state["entity_count"], 1)
        self.assertEqual(state["groups"]["test_group"], 1)
        self.assertEqual(state["metrics"]["shift_count"], 1)
        self.assertEqual(state["origin"]["x"], SHIFT_THRESHOLD + 100.0)
        self.assertEqual(state["origin"]["y"], 200.0)
        self.assertEqual(state["origin"]["z"], 300.0)
        self.assertEqual(len(state["shifts"]), 1)

if __name__ == '__main__':
    unittest.main() 