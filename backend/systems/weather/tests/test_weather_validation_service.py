"""
Tests for Weather Validation Service

Tests for validation service following Development Bible patterns.
"""

import pytest
from unittest.mock import Mock, patch

from backend.systems.weather.services.weather_validation_service import WeatherValidationServiceImpl
from backend.systems.weather.models.weather_model import WeatherCondition


class TestWeatherValidationServiceImpl:
    """Test suite for WeatherValidationServiceImpl"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.service = WeatherValidationServiceImpl()
        # Clear cache between tests
        self.service._config_cache = None
        self.service._types_cache = None
    
    def test_load_weather_config_caches_result(self):
        """Test that load_weather_config caches the result"""
        # Arrange
        mock_config = {
            "weather_system": {"enabled": True, "randomness_factor": 0.7},
            "default_weather": {"condition": "clear", "temperature": 70.0}
        }
        
        with patch('backend.systems.weather.services.weather_validation_service.load_json') as mock_load_json:
            mock_load_json.return_value = mock_config
            
            # Act - call twice
            result1 = self.service.load_weather_config()
            result2 = self.service.load_weather_config()
            
            # Assert
            assert result1 == mock_config
            assert result2 == mock_config
            # Should only call load_json once due to caching
            mock_load_json.assert_called_once_with("data/systems/weather/weather_config.json")
    
    def test_load_weather_config_fallback_on_exception(self):
        """Test that load_weather_config provides fallback config on exception"""
        # Arrange
        with patch('backend.systems.weather.services.weather_validation_service.load_json') as mock_load_json:
            mock_load_json.side_effect = FileNotFoundError("Config not found")
            
            # Act
            result = self.service.load_weather_config()
            
            # Assert
            assert "weather_system" in result
            assert "default_weather" in result
            assert result["weather_system"]["enabled"] is True
            assert result["default_weather"]["condition"] == "clear"
    
    def test_load_weather_types_caches_result(self):
        """Test that load_weather_types caches the result"""
        # Arrange
        mock_types = {
            "clear": {"display_name": "Clear", "temperature_modifier": 5},
            "rain": {"display_name": "Rain", "temperature_modifier": -10}
        }
        
        with patch('backend.systems.weather.services.weather_validation_service.load_json') as mock_load_json:
            mock_load_json.return_value = mock_types
            
            # Act - call twice
            result1 = self.service.load_weather_types()
            result2 = self.service.load_weather_types()
            
            # Assert
            assert result1 == mock_types
            assert result2 == mock_types
            # Should only call load_json once due to caching
            mock_load_json.assert_called_once_with("data/systems/weather/weather_types.json")
    
    def test_load_weather_types_fallback_on_exception(self):
        """Test that load_weather_types provides empty fallback on exception"""
        # Arrange
        with patch('backend.systems.weather.services.weather_validation_service.load_json') as mock_load_json:
            mock_load_json.side_effect = FileNotFoundError("Types not found")
            
            # Act
            result = self.service.load_weather_types()
            
            # Assert
            assert result == {}
    
    def test_validate_weather_condition_valid_condition(self):
        """Test validate_weather_condition with valid conditions"""
        # Test various valid conditions
        test_cases = [
            ("clear", WeatherCondition.CLEAR),
            ("RAIN", WeatherCondition.RAIN),
            ("Light_Snow", WeatherCondition.LIGHT_SNOW),
            ("thunderstorm", WeatherCondition.THUNDERSTORM)
        ]
        
        for condition_str, expected in test_cases:
            # Act
            result = self.service.validate_weather_condition(condition_str)
            
            # Assert
            assert result == expected
    
    def test_validate_weather_condition_invalid_condition(self):
        """Test validate_weather_condition with invalid condition returns default"""
        # Act
        result = self.service.validate_weather_condition("invalid_weather")
        
        # Assert
        assert result == WeatherCondition.CLEAR
    
    def test_get_seasonal_weights_from_json_config(self):
        """Test get_seasonal_weights uses JSON configuration when available"""
        # Arrange
        mock_types = {
            "clear": {"seasonal_probability": {"spring": 0.3, "summer": 0.5}},
            "rain": {"seasonal_probability": {"spring": 0.2, "summer": 0.1}},
            "snow": {"seasonal_probability": {"spring": 0.0, "summer": 0.0}}
        }
        
        with patch.object(self.service, 'load_weather_types', return_value=mock_types):
            # Act
            weights = self.service.get_seasonal_weights("spring")
            
            # Assert
            assert WeatherCondition.CLEAR in weights
            assert WeatherCondition.RAIN in weights
            assert WeatherCondition.SNOW in weights
            assert weights[WeatherCondition.CLEAR] == 0.3
            assert weights[WeatherCondition.RAIN] == 0.2
            assert weights[WeatherCondition.SNOW] == 0.0
    
    def test_get_seasonal_weights_handles_invalid_json_entries(self):
        """Test get_seasonal_weights skips invalid JSON entries gracefully"""
        # Arrange
        mock_types = {
            "clear": {"seasonal_probability": {"spring": 0.3}},
            "invalid_condition": {"seasonal_probability": {"spring": 0.2}},  # Invalid condition
            "rain": {"missing_seasonal": True}  # Missing seasonal_probability
        }
        
        with patch.object(self.service, 'load_weather_types', return_value=mock_types):
            # Act
            weights = self.service.get_seasonal_weights("spring")
            
            # Assert
            # Should only include valid clear condition
            assert WeatherCondition.CLEAR in weights
            assert weights[WeatherCondition.CLEAR] == 0.3
            # Invalid entries should be skipped
            assert len(weights) == 1
    
    def test_get_seasonal_weights_fallback_when_no_json(self):
        """Test get_seasonal_weights uses fallback when no JSON config"""
        # Arrange
        with patch.object(self.service, 'load_weather_types', return_value={}):
            # Act
            spring_weights = self.service.get_seasonal_weights("spring")
            summer_weights = self.service.get_seasonal_weights("summer")
            winter_weights = self.service.get_seasonal_weights("winter")
            
            # Assert - should use fallback weights
            assert len(spring_weights) > 0
            assert len(summer_weights) > 0
            assert len(winter_weights) > 0
            
            # Spring should have reasonable weights
            assert WeatherCondition.CLEAR in spring_weights
            assert WeatherCondition.LIGHT_RAIN in spring_weights
            
            # Summer should favor clear weather
            assert summer_weights[WeatherCondition.CLEAR] > spring_weights[WeatherCondition.CLEAR]
            
            # Winter should have snow conditions
            assert WeatherCondition.SNOW in winter_weights
            assert WeatherCondition.BLIZZARD in winter_weights
    
    def test_get_seasonal_weights_unknown_season_uses_spring_fallback(self):
        """Test get_seasonal_weights uses spring fallback for unknown seasons"""
        # Arrange
        with patch.object(self.service, 'load_weather_types', return_value={}):
            # Act
            unknown_weights = self.service.get_seasonal_weights("unknown_season")
            spring_weights = self.service.get_seasonal_weights("spring")
            
            # Assert - should be identical to spring
            assert unknown_weights == spring_weights
    
    def test_get_temperature_range_from_config(self):
        """Test get_temperature_range uses configuration data"""
        # Arrange
        mock_config = {
            "seasonal_preferences": {
                "spring": {"temperature_range": [40, 80]},
                "summer": {"temperature_range": [70, 100]},
                "winter": {"temperature_range": [10, 50]}
            }
        }
        
        with patch.object(self.service, 'load_weather_config', return_value=mock_config):
            # Act & Assert
            assert self.service.get_temperature_range("spring") == (40, 80)
            assert self.service.get_temperature_range("summer") == (70, 100)
            assert self.service.get_temperature_range("winter") == (10, 50)
    
    def test_get_temperature_range_fallback_for_missing_season(self):
        """Test get_temperature_range provides fallback for missing seasons"""
        # Arrange
        mock_config = {"seasonal_preferences": {}}
        
        with patch.object(self.service, 'load_weather_config', return_value=mock_config):
            # Act
            result = self.service.get_temperature_range("unknown_season")
            
            # Assert - should use default fallback
            assert result == (45, 75)
    
    def test_get_temperature_range_fallback_for_missing_config(self):
        """Test get_temperature_range handles missing configuration gracefully"""
        # Arrange
        mock_config = {}
        
        with patch.object(self.service, 'load_weather_config', return_value=mock_config):
            # Act
            result = self.service.get_temperature_range("summer")
            
            # Assert - should use default fallback
            assert result == (45, 75)
    
    def test_fallback_seasonal_weights_comprehensive(self):
        """Test that fallback seasonal weights cover all seasons appropriately"""
        # Arrange
        with patch.object(self.service, 'load_weather_types', return_value={}):
            # Act
            spring_weights = self.service.get_seasonal_weights("spring")
            summer_weights = self.service.get_seasonal_weights("summer")
            autumn_weights = self.service.get_seasonal_weights("autumn")
            winter_weights = self.service.get_seasonal_weights("winter")
            
            # Assert seasonal characteristics
            # Spring: should be balanced with some rain
            assert spring_weights[WeatherCondition.CLEAR] > 0
            assert spring_weights[WeatherCondition.LIGHT_RAIN] > 0
            
            # Summer: should favor clear and hot weather
            assert summer_weights[WeatherCondition.CLEAR] > spring_weights[WeatherCondition.CLEAR]
            assert WeatherCondition.SCORCHING in summer_weights
            
            # Autumn: should be cloudier
            assert autumn_weights[WeatherCondition.CLOUDY] > 0
            assert autumn_weights[WeatherCondition.OVERCAST] > 0
            
            # Winter: should have snow conditions
            assert winter_weights[WeatherCondition.SNOW] > 0
            assert winter_weights[WeatherCondition.LIGHT_SNOW] > 0
            assert winter_weights[WeatherCondition.BLIZZARD] > 0
            
            # All weights should sum to approximately 1.0 (allowing for rounding)
            for weights in [spring_weights, summer_weights, autumn_weights, winter_weights]:
                total = sum(weights.values())
                assert 0.9 <= total <= 1.1  # Allow for some rounding differences


if __name__ == "__main__":
    pytest.main([__file__]) 