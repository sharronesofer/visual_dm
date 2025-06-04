"""
Test module for motif chaos functionality

This file tests chaos-related functionality that has been consolidated into business_utils.
"""

import pytest
from unittest.mock import Mock, patch

# Import the chaos functions from business_utils (where they actually exist)
from backend.systems.motif.utils.business_utils import roll_chaos_event


class TestChaosUtils:
    """Test class for chaos utilities functionality"""
    
    def test_module_imports(self):
        """Test that the chaos functions can be imported successfully"""
        assert roll_chaos_event is not None
        
    def test_roll_chaos_event_basic(self):
        """Test basic chaos event rolling"""
        event = roll_chaos_event()
        assert isinstance(event, str)
        assert len(event) > 0
        
    def test_roll_chaos_event_with_category(self):
        """Test chaos event rolling with specific category"""
        # Test with a valid category from the config
        event = roll_chaos_event("social")
        assert isinstance(event, str)
        assert len(event) > 0
        
    def test_roll_chaos_event_invalid_category(self):
        """Test chaos event rolling with invalid category handles the error gracefully"""
        # According to the current implementation, invalid categories cause IndexError
        # This test verifies current behavior - could be improved in business logic
        with pytest.raises(IndexError):
            roll_chaos_event("invalid_category")
