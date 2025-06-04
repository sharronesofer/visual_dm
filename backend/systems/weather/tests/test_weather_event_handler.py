"""
Tests for Weather Event Handler

Tests for weather event handling following Development Bible patterns.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from backend.systems.weather.events.weather_event_handler import WeatherEventHandler
from backend.systems.weather.models.weather_model import Weather, WeatherCondition


class TestWeatherEventHandler:
    """Test suite for WeatherEventHandler"""
    
    def setup_method(self):
        """Setup test dependencies"""
        # Mock business service
        self.mock_business_service = Mock()
        self.handler = WeatherEventHandler(self.mock_business_service)
    
    def test_handle_time_advanced_calls_advance_weather(self):
        """Test handle_time_advanced calls business service advance_weather"""
        # Arrange
        event_data = {
            "hours_elapsed": 3,
            "season": "summer"
        }
        
        mock_weather = Weather(
            condition=WeatherCondition.PARTLY_CLOUDY,
            temperature=75.0,
            humidity=60.0,
            wind_speed=8.0,
            pressure=29.9,
            visibility=9.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        
        self.mock_business_service.advance_weather.return_value = mock_weather
        self.mock_business_service.get_weather_effects_data.return_value = {
            "display_name": "Partly Cloudy",
            "description": "Some clouds",
            "visual_effects": {},
            "sound_effects": {},
            "temperature_modifier": 0,
            "visibility_modifier": 0
        }
        
        # Act
        result = self.handler.handle_time_advanced(event_data)
        
        # Assert
        self.mock_business_service.advance_weather.assert_called_once_with("summer", 3)
        assert result["event_type"] == "weather_changed"
        assert result["trigger"] == "time_advanced"
        assert result["weather_data"]["condition"] == "partly_cloudy"
        assert result["weather_data"]["temperature"] == 75.0
    
    def test_handle_time_advanced_default_values(self):
        """Test handle_time_advanced uses default values when not provided"""
        # Arrange
        event_data = {}  # Empty event data
        
        mock_weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=65.0,
            humidity=50.0,
            wind_speed=5.0,
            pressure=29.92,
            visibility=10.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        
        self.mock_business_service.advance_weather.return_value = mock_weather
        self.mock_business_service.get_weather_effects_data.return_value = {
            "display_name": "Clear",
            "description": "Clear skies",
            "visual_effects": {},
            "sound_effects": {},
            "temperature_modifier": 5,
            "visibility_modifier": 0
        }
        
        # Act
        result = self.handler.handle_time_advanced(event_data)
        
        # Assert
        # Should use defaults: 1 hour elapsed, spring season
        self.mock_business_service.advance_weather.assert_called_once_with("spring", 1)
        assert result["event_type"] == "weather_changed"
        assert result["trigger"] == "time_advanced"
    
    def test_handle_season_changed_calls_advance_weather(self):
        """Test handle_season_changed calls advance weather with new season"""
        # Arrange
        event_data = {
            "new_season": "winter"
        }
        
        mock_current_weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=65.0,
            humidity=50.0,
            wind_speed=5.0,
            pressure=29.92,
            visibility=10.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        
        mock_new_weather = Weather(
            condition=WeatherCondition.LIGHT_SNOW,
            temperature=30.0,
            humidity=80.0,
            wind_speed=10.0,
            pressure=29.7,
            visibility=6.0,
            timestamp=datetime.utcnow(),
            duration_hours=5
        )
        
        self.mock_business_service.get_current_weather.return_value = mock_current_weather
        self.mock_business_service.advance_weather.return_value = mock_new_weather
        self.mock_business_service.get_weather_effects_data.return_value = {
            "display_name": "Light Snow",
            "description": "Light snowfall",
            "visual_effects": {"particle_effects": ["snow_light"]},
            "sound_effects": {"ambient_loop": "ambient_light_snow"},
            "temperature_modifier": -15,
            "visibility_modifier": -1
        }
        
        # Act
        result = self.handler.handle_season_changed(event_data)
        
        # Assert
        self.mock_business_service.get_current_weather.assert_called_once()
        self.mock_business_service.advance_weather.assert_called_once_with("winter", 0)
        assert result["event_type"] == "weather_changed"
        assert result["trigger"] == "season_changed"
        assert result["weather_data"]["condition"] == "light_snow"
    
    def test_handle_season_changed_default_season(self):
        """Test handle_season_changed uses default season when not provided"""
        # Arrange
        event_data = {}  # No season specified
        
        mock_weather = Weather(
            condition=WeatherCondition.RAIN,
            temperature=55.0,
            humidity=85.0,
            wind_speed=12.0,
            pressure=29.6,
            visibility=4.0,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        
        self.mock_business_service.get_current_weather.return_value = mock_weather
        self.mock_business_service.advance_weather.return_value = mock_weather
        self.mock_business_service.get_weather_effects_data.return_value = {
            "display_name": "Rain",
            "description": "Rainfall",
            "visual_effects": {},
            "sound_effects": {},
            "temperature_modifier": -10,
            "visibility_modifier": -2
        }
        
        # Act
        result = self.handler.handle_season_changed(event_data)
        
        # Assert
        # Should use default season "spring"
        self.mock_business_service.advance_weather.assert_called_once_with("spring", 0)
        assert result["trigger"] == "season_changed"
    
    def test_handle_admin_weather_force_valid_condition(self):
        """Test handle_admin_weather_force with valid weather condition"""
        # Arrange
        event_data = {
            "condition": "thunderstorm",
            "duration_hours": 2,
            "temperature": 60.0
        }
        
        mock_forced_weather = Weather(
            condition=WeatherCondition.THUNDERSTORM,
            temperature=60.0,
            humidity=95.0,
            wind_speed=35.0,
            pressure=29.3,
            visibility=2.0,
            timestamp=datetime.utcnow(),
            duration_hours=2
        )
        
        self.mock_business_service.force_weather_change.return_value = mock_forced_weather
        self.mock_business_service.get_weather_effects_data.return_value = {
            "display_name": "Thunderstorm",
            "description": "Heavy rain with lightning",
            "visual_effects": {"particle_effects": ["rain_heavy", "lightning"]},
            "sound_effects": {"ambient_loop": "ambient_storm"},
            "temperature_modifier": -12,
            "visibility_modifier": -3
        }
        
        # Act
        result = self.handler.handle_admin_weather_force(event_data)
        
        # Assert
        self.mock_business_service.force_weather_change.assert_called_once_with(
            WeatherCondition.THUNDERSTORM, 2, 60.0
        )
        assert result["event_type"] == "weather_changed"
        assert result["trigger"] == "admin_forced"
        assert result["weather_data"]["condition"] == "thunderstorm"
        assert result["weather_data"]["temperature"] == 60.0
    
    def test_handle_admin_weather_force_missing_condition_raises_error(self):
        """Test handle_admin_weather_force raises error when condition is missing"""
        # Arrange
        event_data = {
            "duration_hours": 2
            # Missing condition
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Condition is required"):
            self.handler.handle_admin_weather_force(event_data)
    
    def test_handle_admin_weather_force_invalid_condition_raises_error(self):
        """Test handle_admin_weather_force raises error for invalid condition"""
        # Arrange
        event_data = {
            "condition": "invalid_weather_type"
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid weather condition"):
            self.handler.handle_admin_weather_force(event_data)
    
    def test_handle_admin_weather_force_optional_parameters(self):
        """Test handle_admin_weather_force handles optional parameters correctly"""
        # Arrange
        event_data = {
            "condition": "fog"
            # No duration_hours or temperature
        }
        
        mock_forced_weather = Weather(
            condition=WeatherCondition.FOG,
            temperature=50.0,
            humidity=100.0,
            wind_speed=2.0,
            pressure=29.8,
            visibility=0.5,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        
        self.mock_business_service.force_weather_change.return_value = mock_forced_weather
        self.mock_business_service.get_weather_effects_data.return_value = {
            "display_name": "Fog",
            "description": "Dense fog",
            "visual_effects": {},
            "sound_effects": {},
            "temperature_modifier": -5,
            "visibility_modifier": -4
        }
        
        # Act
        result = self.handler.handle_admin_weather_force(event_data)
        
        # Assert
        # Should pass None for optional parameters
        self.mock_business_service.force_weather_change.assert_called_once_with(
            WeatherCondition.FOG, None, None
        )
        assert result["trigger"] == "admin_forced"
    
    def test_get_current_weather_event(self):
        """Test get_current_weather_event returns current weather as event"""
        # Arrange
        mock_current_weather = Weather(
            condition=WeatherCondition.WINDY,
            temperature=68.0,
            humidity=45.0,
            wind_speed=25.0,
            pressure=29.95,
            visibility=8.0,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        
        self.mock_business_service.get_current_weather.return_value = mock_current_weather
        self.mock_business_service.get_weather_effects_data.return_value = {
            "display_name": "Windy",
            "description": "Strong winds",
            "visual_effects": {"particle_effects": ["wind_debris"]},
            "sound_effects": {"ambient_loop": "ambient_wind"},
            "temperature_modifier": -2,
            "visibility_modifier": -1
        }
        
        # Act
        result = self.handler.get_current_weather_event()
        
        # Assert
        self.mock_business_service.get_current_weather.assert_called_once()
        assert result["event_type"] == "weather_changed"
        assert result["trigger"] == "current_state"
        assert result["weather_data"]["condition"] == "windy"
        assert result["weather_data"]["wind_speed"] == 25.0
    
    def test_create_weather_event_includes_all_required_fields(self):
        """Test _create_weather_event includes all required event fields"""
        # Arrange
        weather = Weather(
            condition=WeatherCondition.HEAVY_RAIN,
            temperature=45.0,
            humidity=98.0,
            wind_speed=20.0,
            pressure=29.4,
            visibility=1.5,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        
        effects_data = {
            "display_name": "Heavy Rain",
            "description": "Heavy rainfall",
            "visual_effects": {"particle_effects": ["rain_heavy"]},
            "sound_effects": {"ambient_loop": "ambient_heavy_rain", "intensity": "high"},
            "temperature_modifier": -15,
            "visibility_modifier": -3
        }
        
        self.mock_business_service.get_weather_effects_data.return_value = effects_data
        
        # Act
        result = self.handler._create_weather_event(weather, "test_trigger")
        
        # Assert
        # Check top-level event structure
        assert result["event_type"] == "weather_changed"
        assert result["trigger"] == "test_trigger"
        assert "timestamp" in result
        
        # Check weather_data structure
        weather_data = result["weather_data"]
        assert weather_data["condition"] == "heavy_rain"
        assert weather_data["display_name"] == "Heavy Rain"
        assert weather_data["description"] == "Heavy rainfall"
        assert weather_data["temperature"] == 45.0
        assert weather_data["humidity"] == 98.0
        assert weather_data["wind_speed"] == 20.0
        assert weather_data["pressure"] == 29.4
        assert weather_data["visibility"] == 1.5
        assert weather_data["duration_hours"] == 4
        assert "weather_timestamp" in weather_data
        
        # Check effects structure
        effects = result["effects"]
        assert effects["visual_effects"] == {"particle_effects": ["rain_heavy"]}
        assert effects["sound_effects"] == {"ambient_loop": "ambient_heavy_rain", "intensity": "high"}
        assert effects["temperature_modifier"] == -15
        assert effects["visibility_modifier"] == -3
    
    def test_handler_initialization_without_business_service(self):
        """Test WeatherEventHandler can be initialized without business service"""
        # Act
        handler = WeatherEventHandler()
        
        # Assert
        assert handler.business_service is not None
        # Should have created its own business service
        assert hasattr(handler.business_service, 'get_current_weather')
        assert hasattr(handler.business_service, 'advance_weather')


if __name__ == "__main__":
    pytest.main([__file__]) 