"""
Unit tests for the coordinate validation system.
"""

import unittest
import logging
from unittest.mock import patch, MagicMock
from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
from visual_client.core.utils import coordinate_validation as cv

# Configure logging for testing
logging.basicConfig(level=logging.ERROR)

class TestCoordinateValidation(unittest.TestCase):
    """Tests for the coordinate validation system."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset validation statistics before each test
        cv.reset_validation_stats()
        # Ensure validation is enabled
        cv.configure_validation({"enabled": True, "strict_mode": False})
    
    def test_validate_valid_coords(self):
        """Test validation of valid coordinate objects."""
        global_coord = GlobalCoord(10.0, 20.0, 30.0)
        local_coord = LocalCoord(5.0, 15.0, 25.0)
        
        # Should not produce any errors
        self.assertEqual(len(cv.validate_value(global_coord)), 0)
        self.assertEqual(len(cv.validate_value(local_coord)), 0)
        
        # Check stats
        stats = cv.get_validation_stats()
        self.assertEqual(stats["total_checks"], 2)
        self.assertEqual(stats["failed_checks"], 0)
    
    def test_invalid_coords(self):
        """Test validation of invalid coordinate objects."""
        # Create a GlobalCoord with attributes but missing 'z'
        invalid_global = MagicMock(spec=['x', 'y'])
        invalid_global.x = 10.0
        invalid_global.y = 20.0
        
        # This should be detected by the validator
        with patch.object(cv, '_is_valid_global_coord') as mock_validator:
            mock_validator.return_value = False
            errors = cv.validate_value(invalid_global)
            self.assertTrue(len(errors) > 0)
    
    def test_large_coordinate_warning(self):
        """Test warning for excessively large coordinate values."""
        # Configure a lower threshold for testing
        cv.configure_validation({"max_distance_warning": 100.0})
        
        # Create a coordinate with a value exceeding the threshold
        large_coord = GlobalCoord(1000.0, 50.0, 50.0)
        
        errors = cv.validate_value(large_coord)
        self.assertEqual(len(errors), 1)
        self.assertTrue("exceeds safe threshold" in errors[0][0])
        
        # Check stats
        stats = cv.get_validation_stats()
        self.assertEqual(stats["large_coord_warnings"], 1)
    
    def test_tuple_warning(self):
        """Test warning for using raw tuples instead of coordinate objects."""
        # Enable tuple checking
        cv.configure_validation({"check_for_direct_tuples": True})
        
        # Create tuple that looks like a coordinate
        tuple_coord = (10.0, 20.0, 30.0)
        
        errors = cv.validate_value(tuple_coord)
        self.assertEqual(len(errors), 1)
        self.assertTrue("Tuple used where coordinate object expected" in errors[0][0])
        
        # Check stats
        stats = cv.get_validation_stats()
        self.assertEqual(stats["tuple_usage_warnings"], 1)
    
    def test_function_decorator(self):
        """Test the function validation decorator."""
        
        @cv.validate_function_call
        def test_function(pos: GlobalCoord, value: float):
            return pos  # Return the coordinate unchanged
        
        # Test with valid input
        valid_coord = GlobalCoord(10.0, 20.0, 30.0)
        result = test_function(valid_coord, 5.0)
        self.assertEqual(result, valid_coord)
        
        # Test with tuple input (should warn but not fail)
        with patch.object(cv, 'handle_validation_errors') as mock_handler:
            test_function((10.0, 20.0, 30.0), 5.0)
            mock_handler.assert_called()
    
    def test_return_type_decorator(self):
        """Test the return type validation decorator."""
        
        @cv.validate_coord_type(GlobalCoord)
        def should_return_global() -> GlobalCoord:
            return LocalCoord(10.0, 20.0, 30.0)  # Return wrong type
        
        # This should detect the invalid return type
        with patch.object(cv, 'handle_validation_error') as mock_handler:
            should_return_global()
            mock_handler.assert_called()
            args = mock_handler.call_args[0]
            self.assertTrue("should return GlobalCoord" in args[0])
    
    def test_strict_mode(self):
        """Test that strict mode raises exceptions."""
        # Enable strict mode
        cv.configure_validation({"strict_mode": True})
        
        # Create a coordinate with a value exceeding the threshold
        cv.configure_validation({"max_distance_warning": 100.0})
        large_coord = GlobalCoord(1000.0, 50.0, 50.0)
        
        # This should raise an exception in strict mode
        with self.assertRaises(ValueError):
            cv.validate_value(large_coord)
            
    def test_disable_validation(self):
        """Test that disabling validation works."""
        # Disable validation
        cv.configure_validation({"enabled": False})
        
        # These invalid cases should not be detected
        tuple_coord = (10.0, 20.0, 30.0)
        large_coord = GlobalCoord(100000.0, 100000.0, 100000.0)
        
        self.assertEqual(len(cv.validate_value(tuple_coord)), 0)
        self.assertEqual(len(cv.validate_value(large_coord)), 0)
        
        # Check that stats weren't updated
        stats = cv.get_validation_stats()
        self.assertEqual(stats["total_checks"], 0)

if __name__ == "__main__":
    unittest.main() 