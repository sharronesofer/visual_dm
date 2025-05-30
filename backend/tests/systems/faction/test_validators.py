"""
Comprehensive tests for faction validation utilities.
"""

import pytest
from backend.systems.faction.utils.validators import (
    validate_faction_name,
    validate_faction_influence,
    validate_diplomatic_stance,
    FactionValidationError
)
from backend.systems.faction.schemas.faction_types import DiplomaticStance


class TestValidateFactionName: pass
    """Test faction name validation."""

    def test_valid_name(self): pass
        """Test validation of valid faction names."""
        # Test various valid names
        valid_names = [
            "The Order",
            "Crimson Guild",
            "House of Shadows",
            "AB",  # Minimum length
            "X" * 100,  # Maximum length
            "Name with 123 numbers",
            "Special!@#$%^&*()Characters",
        ]
        
        for name in valid_names: pass
            assert validate_faction_name(name) is True

    def test_invalid_name_none(self): pass
        """Test validation rejects None name."""
        with pytest.raises(FactionValidationError, match="must be a non-empty string"): pass
            validate_faction_name(None)

    def test_invalid_name_empty_string(self): pass
        """Test validation rejects empty string."""
        with pytest.raises(FactionValidationError, match="must be a non-empty string"): pass
            validate_faction_name("")

    def test_invalid_name_not_string(self): pass
        """Test validation rejects non-string types."""
        invalid_names = [123, [], {}, True, 45.67]
        
        for name in invalid_names: pass
            with pytest.raises(FactionValidationError, match="must be a non-empty string"): pass
                validate_faction_name(name)

    def test_invalid_name_too_short(self): pass
        """Test validation rejects names that are too short."""
        with pytest.raises(FactionValidationError, match="must be at least 2 characters"): pass
            validate_faction_name("A")

    def test_invalid_name_too_long(self): pass
        """Test validation rejects names that are too long."""
        long_name = "X" * 101  # 101 characters
        with pytest.raises(FactionValidationError, match="cannot exceed 100 characters"): pass
            validate_faction_name(long_name)

    def test_name_exactly_at_limits(self): pass
        """Test names exactly at the character limits."""
        # Exactly 2 characters (minimum)
        assert validate_faction_name("AB") is True
        
        # Exactly 100 characters (maximum)
        max_name = "X" * 100
        assert validate_faction_name(max_name) is True


class TestValidateFactionInfluence: pass
    """Test faction influence validation."""

    def test_valid_influence_values(self): pass
        """Test validation of valid influence values."""
        valid_values = [
            0.0,    # Minimum
            0.1,    # Just above minimum
            50.0,   # Middle
            99.9,   # Just below maximum
            100.0,  # Maximum
            25,     # Integer
            75.5,   # Float
        ]
        
        for value in valid_values: pass
            assert validate_faction_influence(value) is True

    def test_invalid_influence_type(self): pass
        """Test validation rejects non-numeric types."""
        invalid_types = ["50", "high", None, [], {}]  # Removed True since bool converts to numeric
        
        for value in invalid_types: pass
            with pytest.raises(FactionValidationError, match="must be a number"): pass
                validate_faction_influence(value)

    def test_boolean_influence_conversion(self): pass
        """Test that boolean values are treated as numeric (True=1.0, False=0.0)."""
        # Python treats bool as numeric, so these should work
        assert validate_faction_influence(True) is True   # True converts to 1.0
        assert validate_faction_influence(False) is True  # False converts to 0.0

    def test_invalid_influence_too_low(self): pass
        """Test validation rejects negative values."""
        invalid_values = [-1, -0.1, -100, -50.5]
        
        for value in invalid_values: pass
            with pytest.raises(FactionValidationError, match="must be between 0 and 100"): pass
                validate_faction_influence(value)

    def test_invalid_influence_too_high(self): pass
        """Test validation rejects values above 100."""
        invalid_values = [100.1, 101, 150, 1000.0]
        
        for value in invalid_values: pass
            with pytest.raises(FactionValidationError, match="must be between 0 and 100"): pass
                validate_faction_influence(value)

    def test_influence_boundary_values(self): pass
        """Test influence values exactly at boundaries."""
        # Exactly at minimum
        assert validate_faction_influence(0.0) is True
        
        # Exactly at maximum
        assert validate_faction_influence(100.0) is True
        
        # Just outside boundaries should fail
        with pytest.raises(FactionValidationError): pass
            validate_faction_influence(-0.00001)
            
        with pytest.raises(FactionValidationError): pass
            validate_faction_influence(100.00001)


class TestValidateDiplomaticStance: pass
    """Test diplomatic stance validation."""

    def test_valid_diplomatic_stances(self): pass
        """Test validation of all valid diplomatic stances."""
        valid_stances = [
            DiplomaticStance.ALLIED.value,
            DiplomaticStance.NEUTRAL.value,
            DiplomaticStance.RIVALRY.value,
            DiplomaticStance.WAR.value,
            DiplomaticStance.TRUCE.value,
            DiplomaticStance.HOSTILE.value,
        ]
        
        for stance in valid_stances: pass
            assert validate_diplomatic_stance(stance) is True

    def test_invalid_diplomatic_stance(self): pass
        """Test validation rejects invalid stance values."""
        invalid_stances = [
            "invalid",
            "friendly",  # Not a valid DiplomaticStance
            "enemy",
            "",
            "ALLIED",  # Wrong case
            "neutral_evil",  # Wrong enum
        ]
        
        for stance in invalid_stances: pass
            with pytest.raises(FactionValidationError, match="Invalid diplomatic stance"): pass
                validate_diplomatic_stance(stance)

    def test_none_stance_not_allowed(self): pass
        """Test validation rejects None when not allowed."""
        with pytest.raises(FactionValidationError, match="cannot be None"): pass
            validate_diplomatic_stance(None, allow_none=False)

    def test_none_stance_allowed(self): pass
        """Test validation accepts None when allowed."""
        assert validate_diplomatic_stance(None, allow_none=True) is True

    def test_none_stance_default_behavior(self): pass
        """Test that None is not allowed by default."""
        with pytest.raises(FactionValidationError, match="cannot be None"): pass
            validate_diplomatic_stance(None)

    def test_invalid_stance_format(self): pass
        """Test validation rejects non-string formats."""
        invalid_formats = [123, [], {}, 45.67]  # Removed True since it converts to string
        
        for stance in invalid_formats: pass
            with pytest.raises(FactionValidationError, match="Invalid diplomatic stance"): pass
                validate_diplomatic_stance(stance)

    def test_error_message_includes_valid_options(self): pass
        """Test that error messages include valid stance options."""
        try: pass
            validate_diplomatic_stance("invalid_stance")
            assert False, "Should have raised FactionValidationError"
        except FactionValidationError as e: pass
            error_message = str(e)
            # Check that error includes valid options
            assert "allied" in error_message
            assert "neutral" in error_message
            assert "rivalry" in error_message
            assert "war" in error_message
            assert "truce" in error_message
            assert "hostile" in error_message


class TestFactionValidationError: pass
    """Test FactionValidationError exception."""

    def test_error_instantiation(self): pass
        """Test creating FactionValidationError."""
        error = FactionValidationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_error_inheritance(self): pass
        """Test that FactionValidationError inherits from Exception."""
        error = FactionValidationError("Test")
        assert isinstance(error, Exception)

    def test_error_raised_in_validation(self): pass
        """Test that validation functions properly raise FactionValidationError."""
        with pytest.raises(FactionValidationError): pass
            validate_faction_name(None)
            
        with pytest.raises(FactionValidationError): pass
            validate_faction_influence(-1)
            
        with pytest.raises(FactionValidationError): pass
            validate_diplomatic_stance("invalid")


class TestValidatorsIntegration: pass
    """Integration tests for validators working together."""

    def test_valid_faction_data_components(self): pass
        """Test that valid faction data components pass all validations."""
        # Valid faction data components
        name = "The Noble Order"
        influence = 75.5
        stance = DiplomaticStance.ALLIED.value
        
        # All should validate successfully
        assert validate_faction_name(name) is True
        assert validate_faction_influence(influence) is True
        assert validate_diplomatic_stance(stance) is True

    def test_mixed_valid_and_invalid_data(self): pass
        """Test behavior with mixed valid and invalid data."""
        # Valid name, invalid influence
        valid_name = "Valid Faction"
        invalid_influence = -10
        
        assert validate_faction_name(valid_name) is True
        
        with pytest.raises(FactionValidationError): pass
            validate_faction_influence(invalid_influence)

    def test_validation_with_edge_cases(self): pass
        """Test validation with edge case values."""
        # Edge case values that should be valid
        min_name = "AB"
        max_name = "X" * 100
        min_influence = 0.0
        max_influence = 100.0
        none_stance_allowed = None
        
        assert validate_faction_name(min_name) is True
        assert validate_faction_name(max_name) is True
        assert validate_faction_influence(min_influence) is True
        assert validate_faction_influence(max_influence) is True
        assert validate_diplomatic_stance(none_stance_allowed, allow_none=True) is True

    def test_comprehensive_error_scenarios(self): pass
        """Test various error scenarios across validators."""
        # Test each validator's main error cases
        error_cases = [
            (lambda: validate_faction_name(""), "name"),
            (lambda: validate_faction_influence(150), "influence"),
            (lambda: validate_diplomatic_stance("invalid"), "stance"),
        ]
        
        for error_func, error_type in error_cases: pass
            with pytest.raises(FactionValidationError): pass
                error_func()
