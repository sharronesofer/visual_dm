"""
Tests for Weather Business Service

Basic tests following Development Bible testing patterns.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from backend.systems.weather.services.weather_business_service import WeatherBusinessService
from backend.systems.weather.models.weather_model import Weather, WeatherCondition


class TestWeatherBusinessService:
    """Test suite for WeatherBusinessService"""
    
    def setup_method(self):
        """Setup test dependencies"""
        # Mock dependencies
        self.mock_repository = Mock()
        self.mock_validation_service = Mock()
        
        # Setup validation service defaults
        self.mock_validation_service.load_weather_config.return_value = {
            "weather_system": {"randomness_factor": 0.5},
            "default_weather": {
                "condition": "clear",
                "temperature": 65.0,
                "humidity": 50.0,
                "wind_speed": 5.0,
                "pressure": 29.92,
                "visibility": 10.0,
                "duration_hours": 4
            }
        }
        
        self.mock_validation_service.validate_weather_condition.return_value = WeatherCondition.CLEAR
        self.mock_validation_service.get_temperature_range.return_value = (45, 75)
        self.mock_validation_service.load_weather_types.return_value = {}
        
        self.service = WeatherBusinessService(
            self.mock_repository,
            self.mock_validation_service
        )
    
    def test_get_current_weather_initializes_default_when_none_exists(self):
        """Test that get_current_weather creates default weather when none exists"""
        # Arrange
        self.mock_repository.load_weather_state.return_value = None
        
        # Act
        result = self.service.get_current_weather()
        
        # Assert
        assert result is not None
        assert result.condition == WeatherCondition.CLEAR
        assert result.temperature == 65.0
        assert result.humidity == 50.0
        self.mock_repository.save_weather_state.assert_called_once()
    
    def test_get_current_weather_returns_existing_weather(self):
        """Test that get_current_weather returns existing weather when available"""
        # Arrange
        existing_weather = Weather(
            condition=WeatherCondition.RAIN,
            temperature=55.0,
            humidity=80.0,
            wind_speed=15.0,
            pressure=29.5,
            visibility=3.0,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        self.mock_repository.load_weather_state.return_value = existing_weather
        
        # Act
        result = self.service.get_current_weather()
        
        # Assert
        assert result == existing_weather
        self.mock_repository.save_weather_state.assert_not_called()
    
    def test_force_weather_change_creates_forced_weather(self):
        """Test that force_weather_change creates weather with specified condition"""
        # Arrange
        current_weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=65.0,
            humidity=50.0,
            wind_speed=5.0,
            pressure=29.92,
            visibility=10.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        self.mock_repository.load_weather_state.return_value = current_weather
        
        # Act
        result = self.service.force_weather_change(
            WeatherCondition.THUNDERSTORM,
            duration_hours=2,
            temperature=58.0
        )
        
        # Assert
        assert result.condition == WeatherCondition.THUNDERSTORM
        assert result.temperature == 58.0
        assert result.duration_hours == 2
        self.mock_repository.add_to_history.assert_called_once_with(current_weather)
        self.mock_repository.save_weather_state.assert_called_once()
    
    def test_get_weather_effects_data_returns_effects_from_config(self):
        """Test that get_weather_effects_data returns effects from weather types config"""
        # Arrange
        weather = Weather(
            condition=WeatherCondition.RAIN,
            temperature=55.0,
            humidity=80.0,
            wind_speed=15.0,
            pressure=29.5,
            visibility=3.0,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        
        mock_weather_types = {
            "rain": {
                "visual_effects": {"particle_effects": ["rain_medium"]},
                "sound_effects": {"ambient_loop": "ambient_rain"},
                "temperature_modifier": -10,
                "visibility_modifier": -2,
                "display_name": "Rain",
                "description": "Rainfall"
            }
        }
        self.mock_validation_service.load_weather_types.return_value = mock_weather_types
        
        # Act
        result = self.service.get_weather_effects_data(weather)
        
        # Assert
        assert result["visual_effects"]["particle_effects"] == ["rain_medium"]
        assert result["sound_effects"]["ambient_loop"] == "ambient_rain"
        assert result["temperature_modifier"] == -10
        assert result["visibility_modifier"] == -2
        assert result["display_name"] == "Rain"
        assert result["description"] == "Rainfall"
    
    def test_get_weather_effects_data_returns_fallback_when_no_config(self):
        """Test that get_weather_effects_data returns fallback when no config exists"""
        # Arrange
        weather = Weather(
            condition=WeatherCondition.MIST,
            temperature=60.0,
            humidity=90.0,
            wind_speed=2.0,
            pressure=29.8,
            visibility=2.0,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        
        self.mock_validation_service.load_weather_types.return_value = {}
        
        # Act
        result = self.service.get_weather_effects_data(weather)
        
        # Assert
        assert result["visual_effects"] == {}
        assert result["sound_effects"] == {}
        assert result["temperature_modifier"] == 0
        assert result["visibility_modifier"] == 0
        assert result["display_name"] == "Mist"
        assert result["description"] == ""


if __name__ == "__main__":
    pytest.main([__file__]) 