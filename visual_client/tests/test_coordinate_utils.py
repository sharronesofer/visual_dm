"""
Unit tests for the coordinate utilities library.
"""

import unittest
import math
from visual_client.core.utils.coordinates import (
    GlobalCoord, LocalCoord, CoordinateSystem, 
    SHIFT_THRESHOLD, COORD_EPSILON
)
from visual_client.core.utils import coordinate_utils as cu

class TestVectorOperations(unittest.TestCase):
    """Test vector and matrix operations."""
    
    def test_vector_conversion(self):
        """Test vector conversion between 2D and 3D."""
        v2 = (10.0, 20.0)
        v3 = cu.vec2_to_vec3(v2)
        self.assertEqual(v3, (10.0, 20.0, 0.0))
        
        v3_with_z = cu.vec2_to_vec3(v2, 30.0)
        self.assertEqual(v3_with_z, (10.0, 20.0, 30.0))
        
        v3 = (10.0, 20.0, 30.0)
        v2 = cu.vec3_to_vec2(v3)
        self.assertEqual(v2, (10.0, 20.0))
    
    def test_vector_arithmetic(self):
        """Test vector arithmetic operations."""
        # 2D vectors
        v1 = (10.0, 20.0)
        v2 = (5.0, 8.0)
        
        # Addition
        result = cu.vec_add(v1, v2)
        self.assertEqual(result, (15.0, 28.0))
        
        # Subtraction
        result = cu.vec_subtract(v1, v2)
        self.assertEqual(result, (5.0, 12.0))
        
        # Scaling
        result = cu.vec_scale(v1, 2.0)
        self.assertEqual(result, (20.0, 40.0))
        
        # 3D vectors
        v1 = (10.0, 20.0, 30.0)
        v2 = (5.0, 8.0, 12.0)
        
        # Addition
        result = cu.vec_add(v1, v2)
        self.assertEqual(result, (15.0, 28.0, 42.0))
        
        # Subtraction
        result = cu.vec_subtract(v1, v2)
        self.assertEqual(result, (5.0, 12.0, 18.0))
        
        # Scaling
        result = cu.vec_scale(v1, 2.0)
        self.assertEqual(result, (20.0, 40.0, 60.0))
    
    def test_vector_magnitude(self):
        """Test vector magnitude calculation."""
        # 2D vector with 3-4-5 triangle
        v = (3.0, 4.0)
        mag = cu.vec_magnitude(v)
        self.assertEqual(mag, 5.0)
        
        # 3D vector
        v = (2.0, 3.0, 6.0)
        mag = cu.vec_magnitude(v)
        self.assertEqual(mag, 7.0)  # sqrt(4+9+36) = sqrt(49) = 7
    
    def test_vector_normalize(self):
        """Test vector normalization."""
        # 2D vector
        v = (3.0, 4.0)
        normal = cu.vec_normalize(v)
        self.assertAlmostEqual(normal[0], 0.6)  # 3/5 = 0.6
        self.assertAlmostEqual(normal[1], 0.8)  # 4/5 = 0.8
        
        # Check that magnitude is 1
        mag = cu.vec_magnitude(normal)
        self.assertAlmostEqual(mag, 1.0)
        
        # 3D vector
        v = (2.0, 3.0, 6.0)
        normal = cu.vec_normalize(v)
        
        # Check that magnitude is 1
        mag = cu.vec_magnitude(normal)
        self.assertAlmostEqual(mag, 1.0)
    
    def test_vector_dot_product(self):
        """Test vector dot product."""
        # 2D vectors
        v1 = (1.0, 0.0)
        v2 = (0.0, 1.0)
        dot = cu.vec_dot(v1, v2)
        self.assertEqual(dot, 0.0)  # Perpendicular vectors
        
        v1 = (1.0, 2.0)
        v2 = (3.0, 4.0)
        dot = cu.vec_dot(v1, v2)
        self.assertEqual(dot, 11.0)  # 1*3 + 2*4 = 11
        
        # 3D vectors
        v1 = (1.0, 2.0, 3.0)
        v2 = (4.0, 5.0, 6.0)
        dot = cu.vec_dot(v1, v2)
        self.assertEqual(dot, 32.0)  # 1*4 + 2*5 + 3*6 = 32
    
    def test_vector_cross_product(self):
        """Test vector cross product."""
        v1 = (1.0, 0.0, 0.0)  # x-axis
        v2 = (0.0, 1.0, 0.0)  # y-axis
        cross = cu.vec_cross(v1, v2)
        self.assertEqual(cross, (0.0, 0.0, 1.0))  # Should be z-axis
        
        v1 = (2.0, 3.0, 4.0)
        v2 = (5.0, 6.0, 7.0)
        cross = cu.vec_cross(v1, v2)
        self.assertEqual(cross, (-3.0, 6.0, -3.0))
    
    def test_vector_distance(self):
        """Test distance calculation between vectors."""
        v1 = (1.0, 2.0)
        v2 = (4.0, 6.0)
        dist = cu.vec_distance(v1, v2)
        self.assertEqual(dist, 5.0)  # sqrt((4-1)^2 + (6-2)^2) = sqrt(25) = 5
        
        v1 = (1.0, 2.0, 3.0)
        v2 = (4.0, 6.0, 9.0)
        dist = cu.vec_distance(v1, v2)
        self.assertEqual(dist, 7.0)  # sqrt((4-1)^2 + (6-2)^2 + (9-3)^2) = sqrt(49) = 7
    
    def test_vector_lerp(self):
        """Test linear interpolation between vectors."""
        v1 = (10.0, 20.0)
        v2 = (20.0, 40.0)
        
        # t = 0 should return v1
        result = cu.vec_lerp(v1, v2, 0.0)
        self.assertEqual(result, v1)
        
        # t = 1 should return v2
        result = cu.vec_lerp(v1, v2, 1.0)
        self.assertEqual(result, v2)
        
        # t = 0.5 should return midpoint
        result = cu.vec_lerp(v1, v2, 0.5)
        self.assertEqual(result, (15.0, 30.0))
        
        # Test clamping for t > 1
        result = cu.vec_lerp(v1, v2, 2.0)
        self.assertEqual(result, v2)
        
        # Test clamping for t < 0
        result = cu.vec_lerp(v1, v2, -1.0)
        self.assertEqual(result, v1)
    
    def test_matrix_multiply(self):
        """Test matrix multiplication."""
        # Identity matrix
        identity = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ]
        v = (1.0, 2.0, 3.0)
        result = cu.matrix_multiply(identity, v)
        self.assertEqual(result, v)
        
        # Rotation matrix (90 degrees around z-axis)
        rotation_z = [
            [0.0, -1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0]
        ]
        v = (1.0, 0.0, 0.0)  # x-axis
        result = cu.matrix_multiply(rotation_z, v)
        self.assertAlmostEqual(result[0], 0.0)
        self.assertAlmostEqual(result[1], 1.0)  # rotated to y-axis
        self.assertAlmostEqual(result[2], 0.0)

class TestCoordinateConversion(unittest.TestCase):
    """Test coordinate conversion functions."""
    
    def setUp(self):
        """Set up a fresh coordinate system for each test."""
        self.coord_system = CoordinateSystem()
    
    def test_tuple_conversions(self):
        """Test tuple to coordinate conversions."""
        # 2D tuples
        v2 = (10.0, 20.0)
        global_coord = cu.tuple_to_global(v2)
        self.assertEqual(global_coord, GlobalCoord(10.0, 20.0, 0.0))
        
        local_coord = cu.tuple_to_local(v2)
        self.assertEqual(local_coord, LocalCoord(10.0, 20.0, 0.0))
        
        # 3D tuples
        v3 = (10.0, 20.0, 30.0)
        global_coord = cu.tuple_to_global(v3)
        self.assertEqual(global_coord, GlobalCoord(10.0, 20.0, 30.0))
        
        local_coord = cu.tuple_to_local(v3)
        self.assertEqual(local_coord, LocalCoord(10.0, 20.0, 30.0))
        
        # Coordinate to tuple
        global_coord = GlobalCoord(10.0, 20.0, 30.0)
        v3 = cu.global_to_tuple(global_coord)
        self.assertEqual(v3, (10.0, 20.0, 30.0))
        
        local_coord = LocalCoord(10.0, 20.0, 30.0)
        v3 = cu.local_to_tuple(local_coord)
        self.assertEqual(v3, (10.0, 20.0, 30.0))
    
    def test_global_local_conversions(self):
        """Test global to local coordinate conversions."""
        # With origin at (0,0,0)
        global_coord = GlobalCoord(100.0, 200.0, 300.0)
        local_coord = cu.global_to_local(global_coord, self.coord_system)
        self.assertEqual(local_coord, LocalCoord(100.0, 200.0, 300.0))
        
        # Convert back
        result = cu.local_to_global(local_coord, self.coord_system)
        self.assertEqual(result, global_coord)
        
        # Shift origin to (50,50,50)
        self.coord_system.shift_origin(GlobalCoord(50.0, 50.0, 50.0))
        
        # Now the same global coord should have different local coords
        local_coord = cu.global_to_local(global_coord, self.coord_system)
        self.assertEqual(local_coord, LocalCoord(50.0, 150.0, 250.0))
        
        # Convert back should still give original global
        result = cu.local_to_global(local_coord, self.coord_system)
        self.assertEqual(result, global_coord)
    
    def test_coord_round_floor_ceil(self):
        """Test coordinate rounding, floor, and ceiling functions."""
        # Test rounding
        global_coord = GlobalCoord(10.2, 20.7, 30.5)
        result = cu.coord_round(global_coord)
        self.assertEqual(result, GlobalCoord(10.0, 21.0, 30.0))
        
        local_coord = LocalCoord(10.2, 20.7, 30.5)
        result = cu.coord_round(local_coord)
        self.assertEqual(result, LocalCoord(10.0, 21.0, 30.0))
        
        # Test with decimals
        result = cu.coord_round(global_coord, 1)
        self.assertEqual(result, GlobalCoord(10.2, 20.7, 30.5))
        
        # Test floor
        result = cu.coord_floor(global_coord)
        self.assertEqual(result, GlobalCoord(10.0, 20.0, 30.0))
        
        result = cu.coord_floor(local_coord)
        self.assertEqual(result, LocalCoord(10.0, 20.0, 30.0))
        
        # Test ceil
        result = cu.coord_ceil(global_coord)
        self.assertEqual(result, GlobalCoord(11.0, 21.0, 31.0))
        
        result = cu.coord_ceil(local_coord)
        self.assertEqual(result, LocalCoord(11.0, 21.0, 31.0))

class TestSpecializedConversions(unittest.TestCase):
    """Test specialized coordinate conversion functions."""
    
    def test_world_grid_conversions(self):
        """Test world to grid coordinate conversions."""
        # Default grid size (1.0)
        world_coord = GlobalCoord(10.7, 20.3)
        grid_pos = cu.world_to_grid(world_coord)
        self.assertEqual(grid_pos, (10, 20))
        
        # Custom grid size (2.0)
        grid_pos = cu.world_to_grid(world_coord, grid_size=2.0)
        self.assertEqual(grid_pos, (5, 10))
        
        # Grid to world (cell center)
        world_pos = cu.grid_to_world(5, 10, grid_size=2.0)
        self.assertEqual(world_pos, GlobalCoord(11.0, 21.0, 0.0))
    
    def test_world_screen_conversions(self):
        """Test world to screen and screen to world conversions."""
        # Setup viewport
        view_pos = (500.0, 300.0)
        view_size = (1000.0, 600.0)
        screen_size = (800.0, 600.0)
        
        # World to screen
        world_coord = GlobalCoord(500.0, 300.0)  # Center of view
        screen_pos = cu.world_to_screen(
            world_coord, view_pos, view_size, screen_size
        )
        
        # Should be center of screen
        self.assertAlmostEqual(screen_pos[0], 400.0)  # 800/2
        self.assertAlmostEqual(screen_pos[1], 300.0)  # 600/2
        
        # Edge of viewport
        world_coord = GlobalCoord(1000.0, 600.0)  # Right-bottom edge
        screen_pos = cu.world_to_screen(
            world_coord, view_pos, view_size, screen_size
        )
        
        self.assertAlmostEqual(screen_pos[0], 800.0)  # Right edge
        self.assertAlmostEqual(screen_pos[1], 600.0)  # Bottom edge
        
        # Screen to world (center of screen)
        screen_pos = (400.0, 300.0)
        world_coord = cu.screen_to_world(
            screen_pos, view_pos, view_size, screen_size
        )
        
        self.assertAlmostEqual(world_coord.x, 500.0)
        self.assertAlmostEqual(world_coord.y, 300.0)
        
        # Screen to world (corner of screen)
        screen_pos = (0.0, 0.0)  # Top-left corner
        world_coord = cu.screen_to_world(
            screen_pos, view_pos, view_size, screen_size
        )
        
        self.assertAlmostEqual(world_coord.x, 0.0)
        self.assertAlmostEqual(world_coord.y, 0.0)

class TestSerializationDeserialization(unittest.TestCase):
    """Test serialization and deserialization of coordinates."""
    
    def test_serialize_coord(self):
        """Test serialization of coordinates to dictionaries."""
        # Global coordinate
        global_coord = GlobalCoord(10.5, 20.5, 30.5)
        serialized = cu.serialize_coord(global_coord)
        
        self.assertEqual(serialized['x'], 10.5)
        self.assertEqual(serialized['y'], 20.5)
        self.assertEqual(serialized['z'], 30.5)
        self.assertEqual(serialized['type'], 'global')
        
        # Local coordinate
        local_coord = LocalCoord(15.5, 25.5, 35.5)
        serialized = cu.serialize_coord(local_coord)
        
        self.assertEqual(serialized['x'], 15.5)
        self.assertEqual(serialized['y'], 25.5)
        self.assertEqual(serialized['z'], 35.5)
        self.assertEqual(serialized['type'], 'local')
    
    def test_deserialize_coord(self):
        """Test deserialization of dictionaries to coordinates."""
        # Global coordinate
        data = {'x': 10.5, 'y': 20.5, 'z': 30.5, 'type': 'global'}
        coord = cu.deserialize_coord(data)
        
        self.assertIsInstance(coord, GlobalCoord)
        self.assertEqual(coord.x, 10.5)
        self.assertEqual(coord.y, 20.5)
        self.assertEqual(coord.z, 30.5)
        
        # Local coordinate
        data = {'x': 15.5, 'y': 25.5, 'z': 35.5, 'type': 'local'}
        coord = cu.deserialize_coord(data)
        
        self.assertIsInstance(coord, LocalCoord)
        self.assertEqual(coord.x, 15.5)
        self.assertEqual(coord.y, 25.5)
        self.assertEqual(coord.z, 35.5)
        
        # Without z (should default to 0.0)
        data = {'x': 15.5, 'y': 25.5, 'type': 'local'}
        coord = cu.deserialize_coord(data)
        
        self.assertEqual(coord.z, 0.0)
        
        # Test error cases
        with self.assertRaises(ValueError):
            cu.deserialize_coord({})
        
        with self.assertRaises(ValueError):
            cu.deserialize_coord({'x': 10, 'y': 20, 'type': 'unknown'})
    
    def test_serialization_roundtrip(self):
        """Test that serialization followed by deserialization returns equivalent object."""
        # Global coordinate
        original = GlobalCoord(10.5, 20.5, 30.5)
        serialized = cu.serialize_coord(original)
        roundtrip = cu.deserialize_coord(serialized)
        
        self.assertEqual(original, roundtrip)
        
        # Local coordinate
        original = LocalCoord(15.5, 25.5, 35.5)
        serialized = cu.serialize_coord(original)
        roundtrip = cu.deserialize_coord(serialized)
        
        self.assertEqual(original, roundtrip)

class TestValidationFunctions(unittest.TestCase):
    """Test coordinate validation functions."""
    
    def test_is_valid_coord(self):
        """Test coordinate validation."""
        self.assertTrue(cu.is_valid_coord(GlobalCoord(0, 0)))
        self.assertTrue(cu.is_valid_coord(LocalCoord(0, 0)))
        
        self.assertFalse(cu.is_valid_coord((0, 0)))
        self.assertFalse(cu.is_valid_coord("not a coord"))
        self.assertFalse(cu.is_valid_coord(None))
    
    def test_is_within_bounds(self):
        """Test bounds checking."""
        bounds = (0.0, 0.0, 100.0, 200.0)  # min_x, min_y, max_x, max_y
        
        # Within bounds
        coord = GlobalCoord(50.0, 100.0)
        self.assertTrue(cu.is_within_bounds(coord, bounds))
        
        # At boundary
        coord = GlobalCoord(0.0, 0.0)
        self.assertTrue(cu.is_within_bounds(coord, bounds))
        
        coord = GlobalCoord(100.0, 200.0)
        self.assertTrue(cu.is_within_bounds(coord, bounds))
        
        # Outside bounds
        coord = GlobalCoord(-1.0, 100.0)
        self.assertFalse(cu.is_within_bounds(coord, bounds))
        
        coord = GlobalCoord(50.0, 201.0)
        self.assertFalse(cu.is_within_bounds(coord, bounds))
    
    def test_is_safe_coordinate(self):
        """Test safe coordinate checking."""
        # Safe coordinates
        coord = GlobalCoord(0.0, 0.0)
        self.assertTrue(cu.is_safe_coordinate(coord))
        
        coord = GlobalCoord(cu.MAX_SAFE_COORDINATE, cu.MAX_SAFE_COORDINATE)
        self.assertTrue(cu.is_safe_coordinate(coord))
        
        # Unsafe coordinates
        coord = GlobalCoord(cu.MAX_SAFE_COORDINATE + 1.0, 0.0)
        self.assertFalse(cu.is_safe_coordinate(coord))
        
        coord = GlobalCoord(0.0, 0.0, cu.MAX_SAFE_COORDINATE + 1.0)
        self.assertFalse(cu.is_safe_coordinate(coord))
    
    def test_assert_functions(self):
        """Test assertion functions."""
        # Valid assertions
        global_coord = GlobalCoord(0.0, 0.0)
        local_coord = LocalCoord(0.0, 0.0)
        
        # These should not raise
        cu.assert_valid_coord(global_coord)
        cu.assert_valid_coord(local_coord)
        cu.assert_global_coord(global_coord)
        cu.assert_local_coord(local_coord)
        cu.assert_safe_coordinate(global_coord)
        
        # Invalid assertions
        with self.assertRaises(TypeError):
            cu.assert_valid_coord((0.0, 0.0))
        
        with self.assertRaises(TypeError):
            cu.assert_global_coord(local_coord)
        
        with self.assertRaises(TypeError):
            cu.assert_local_coord(global_coord)
        
        # Unsafe coordinate
        unsafe_coord = GlobalCoord(cu.MAX_SAFE_COORDINATE + 1.0, 0.0)
        with self.assertRaises(ValueError):
            cu.assert_safe_coordinate(unsafe_coord)

class TestDebugVisualization(unittest.TestCase):
    """Test debug visualization helpers."""
    
    def test_format_coord(self):
        """Test coordinate formatting."""
        global_coord = GlobalCoord(10.12345, 20.12345, 30.12345)
        
        # Default precision (2)
        formatted = cu.format_coord(global_coord)
        self.assertEqual(formatted, "G(10.12, 20.12, 30.12)")
        
        # Custom precision
        formatted = cu.format_coord(global_coord, precision=4)
        self.assertEqual(formatted, "G(10.1235, 20.1235, 30.1235)")
        
        # Without type
        formatted = cu.format_coord(global_coord, include_type=False)
        self.assertEqual(formatted, "(10.12, 20.12, 30.12)")
        
        # Local coordinate
        local_coord = LocalCoord(10.12345, 20.12345, 30.12345)
        formatted = cu.format_coord(local_coord)
        self.assertEqual(formatted, "L(10.12, 20.12, 30.12)")
    
    def test_format_vector(self):
        """Test vector formatting."""
        # 2D vector
        v2 = (10.12345, 20.12345)
        formatted = cu.format_vector(v2)
        self.assertEqual(formatted, "(10.12, 20.12)")
        
        # 3D vector
        v3 = (10.12345, 20.12345, 30.12345)
        formatted = cu.format_vector(v3)
        self.assertEqual(formatted, "(10.12, 20.12, 30.12)")
        
        # Custom precision
        formatted = cu.format_vector(v3, precision=4)
        self.assertEqual(formatted, "(10.1235, 20.1235, 30.1235)")
    
    def test_debug_coord_info(self):
        """Test debug info generation for coordinates."""
        coord_system = CoordinateSystem()
        
        # Global coordinate
        global_coord = GlobalCoord(100.0, 200.0, 300.0)
        info = cu.debug_coord_info(global_coord, coord_system)
        
        self.assertEqual(info['original'], global_coord)
        self.assertIsInstance(info['other_space'], LocalCoord)
        self.assertEqual(info['other_space'], LocalCoord(100.0, 200.0, 300.0))
        self.assertTrue(info['is_safe'])
        
        # Local coordinate
        local_coord = LocalCoord(100.0, 200.0, 300.0)
        info = cu.debug_coord_info(local_coord, coord_system)
        
        self.assertEqual(info['original'], local_coord)
        self.assertIsInstance(info['other_space'], GlobalCoord)
        self.assertEqual(info['other_space'], GlobalCoord(100.0, 200.0, 300.0))
        self.assertTrue(info['is_safe'])
    
    def test_get_coord_system_info(self):
        """Test coordinate system info retrieval."""
        coord_system = CoordinateSystem()
        
        # Initial state
        info = cu.get_coord_system_info(coord_system)
        self.assertEqual(info['current_origin'], GlobalCoord(0.0, 0.0, 0.0))
        self.assertEqual(info['shift_count'], 0)
        self.assertIsNone(info['last_shift'])
        
        # After shift
        coord_system.shift_origin(GlobalCoord(100.0, 200.0, 300.0))
        info = cu.get_coord_system_info(coord_system)
        
        self.assertEqual(info['current_origin'], GlobalCoord(100.0, 200.0, 300.0))
        self.assertEqual(info['shift_count'], 1)
        self.assertIsNotNone(info['last_shift'])
        self.assertEqual(info['last_shift']['new_origin'], GlobalCoord(100.0, 200.0, 300.0))

if __name__ == '__main__':
    unittest.main() 