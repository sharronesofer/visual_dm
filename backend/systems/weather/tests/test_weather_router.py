"""
Tests for Weather Router

Tests for weather API endpoints following Development Bible patterns.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch, Mock
from datetime import datetime

from backend.systems.weather.routers.weather_router import weather_router
from backend.systems.weather.models.weather_model import Weather, WeatherCondition


# Create test app
app = FastAPI()
app.include_router(weather_router)
client = TestClient(app)


class TestWeatherRouter:
    """Test suite for weather API endpoints"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.test_weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=65.0,
            humidity=50.0,
            wind_speed=5.0,
            pressure=29.92,
            visibility=10.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        
        self.test_effects_data = {
            "display_name": "Clear",
            "description": "Clear skies",
            "visual_effects": {"skybox_tint": {"r": 0.5, "g": 0.7, "b": 1.0, "a": 1.0}},
            "sound_effects": {},
            "temperature_modifier": 5,
            "visibility_modifier": 0
        }
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_current_weather_success(self, mock_get_service):
        """Test GET /api/weather/current returns current weather"""
        # Arrange
        mock_service = Mock()
        mock_service.get_current_weather.return_value = self.test_weather
        mock_service.get_weather_effects_data.return_value = self.test_effects_data
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.get("/api/weather/current")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["condition"] == "clear"
        assert data["display_name"] == "Clear"
        assert data["temperature"] == 65.0
        assert data["humidity"] == 50.0
        assert "visual_effects" in data
        assert "sound_effects" in data
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_current_weather_service_error(self, mock_get_service):
        """Test GET /api/weather/current handles service errors"""
        # Arrange
        mock_service = Mock()
        mock_service.get_current_weather.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.get("/api/weather/current")
        
        # Assert
        assert response.status_code == 500
        assert "Failed to get current weather" in response.json()["detail"]
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_weather_forecast_success(self, mock_get_service):
        """Test GET /api/weather/forecast returns forecast"""
        # Arrange
        forecast_weather = [
            Weather(
                condition=WeatherCondition.CLEAR,
                temperature=65.0,
                humidity=50.0,
                wind_speed=5.0,
                pressure=29.92,
                visibility=10.0,
                timestamp=datetime.utcnow(),
                duration_hours=4
            ),
            Weather(
                condition=WeatherCondition.CLOUDY,
                temperature=60.0,
                humidity=70.0,
                wind_speed=10.0,
                pressure=29.8,
                visibility=8.0,
                timestamp=datetime.utcnow(),
                duration_hours=3
            )
        ]
        
        mock_service = Mock()
        mock_service.get_weather_forecast.return_value = forecast_weather
        mock_service.get_weather_effects_data.side_effect = [
            self.test_effects_data,
            {"display_name": "Cloudy", "description": "Overcast", "visual_effects": {}, "sound_effects": {}}
        ]
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.get("/api/weather/forecast?hours=48&season=summer")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert len(data["forecast"]) == 2
        assert data["forecast"][0]["condition"] == "clear"
        assert data["forecast"][1]["condition"] == "cloudy"
        mock_service.get_weather_forecast.assert_called_once_with(48, "summer")
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_weather_forecast_default_parameters(self, mock_get_service):
        """Test GET /api/weather/forecast uses default parameters"""
        # Arrange
        mock_service = Mock()
        mock_service.get_weather_forecast.return_value = [self.test_weather]
        mock_service.get_weather_effects_data.return_value = self.test_effects_data
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.get("/api/weather/forecast")
        
        # Assert
        assert response.status_code == 200
        # Should use defaults: 24 hours, spring season
        mock_service.get_weather_forecast.assert_called_once_with(24, "spring")
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_weather_forecast_parameter_validation(self, mock_get_service):
        """Test GET /api/weather/forecast validates parameters"""
        # Act - test invalid hours (too high)
        response = client.get("/api/weather/forecast?hours=200")
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_weather_history_success(self, mock_get_service):
        """Test GET /api/weather/history returns history"""
        # Arrange
        history = [self.test_weather]
        
        mock_service = Mock()
        mock_service.weather_repository.get_weather_history.return_value = history
        mock_service.get_weather_effects_data.return_value = self.test_effects_data
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.get("/api/weather/history?limit=100")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "count" in data
        assert data["count"] == 1
        assert len(data["history"]) == 1
        assert data["history"][0]["condition"] == "clear"
        mock_service.weather_repository.get_weather_history.assert_called_once_with(100)
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_advance_weather_success(self, mock_get_service):
        """Test POST /api/weather/advance advances weather"""
        # Arrange
        advanced_weather = Weather(
            condition=WeatherCondition.CLOUDY,
            temperature=60.0,
            humidity=70.0,
            wind_speed=10.0,
            pressure=29.8,
            visibility=8.0,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        
        mock_service = Mock()
        mock_service.advance_weather.return_value = advanced_weather
        mock_service.get_weather_effects_data.return_value = {
            "display_name": "Cloudy",
            "description": "Overcast skies",
            "visual_effects": {},
            "sound_effects": {},
            "temperature_modifier": -5,
            "visibility_modifier": -1
        }
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/weather/advance?season=autumn&hours_elapsed=3")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["condition"] == "cloudy"
        assert data["temperature"] == 60.0
        mock_service.advance_weather.assert_called_once_with("autumn", 3)
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_advance_weather_default_parameters(self, mock_get_service):
        """Test POST /api/weather/advance uses default parameters"""
        # Arrange
        mock_service = Mock()
        mock_service.advance_weather.return_value = self.test_weather
        mock_service.get_weather_effects_data.return_value = self.test_effects_data
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/weather/advance")
        
        # Assert
        assert response.status_code == 200
        # Should use defaults: spring season, 1 hour elapsed
        mock_service.advance_weather.assert_called_once_with("spring", 1)
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_force_weather_success(self, mock_get_service):
        """Test POST /api/weather/force forces specific weather"""
        # Arrange
        forced_weather = Weather(
            condition=WeatherCondition.THUNDERSTORM,
            temperature=55.0,
            humidity=95.0,
            wind_speed=35.0,
            pressure=29.3,
            visibility=2.0,
            timestamp=datetime.utcnow(),
            duration_hours=2
        )
        
        mock_service = Mock()
        mock_service.force_weather_change.return_value = forced_weather
        mock_service.get_weather_effects_data.return_value = {
            "display_name": "Thunderstorm",
            "description": "Heavy rain with lightning",
            "visual_effects": {"particle_effects": ["rain_heavy", "lightning"]},
            "sound_effects": {"ambient_loop": "ambient_storm"},
            "temperature_modifier": -12,
            "visibility_modifier": -3
        }
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/weather/force?condition=thunderstorm&duration_hours=2&temperature=55.0")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["condition"] == "thunderstorm"
        assert data["temperature"] == 55.0
        assert data["duration_hours"] == 2
        mock_service.force_weather_change.assert_called_once_with(
            WeatherCondition.THUNDERSTORM, 2, 55.0
        )
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_force_weather_invalid_condition(self, mock_get_service):
        """Test POST /api/weather/force rejects invalid weather condition"""
        # Act
        response = client.post("/api/weather/force?condition=invalid_weather")
        
        # Assert
        assert response.status_code == 400
        assert "Invalid weather condition" in response.json()["detail"]
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_force_weather_optional_parameters(self, mock_get_service):
        """Test POST /api/weather/force handles optional parameters"""
        # Arrange
        mock_service = Mock()
        mock_service.force_weather_change.return_value = self.test_weather
        mock_service.get_weather_effects_data.return_value = self.test_effects_data
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.post("/api/weather/force?condition=clear")
        
        # Assert
        assert response.status_code == 200
        # Should pass None for optional parameters
        mock_service.force_weather_change.assert_called_once_with(
            WeatherCondition.CLEAR, None, None
        )
    
    def test_get_available_conditions_success(self):
        """Test GET /api/weather/conditions returns available conditions"""
        # Act
        response = client.get("/api/weather/conditions")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "conditions" in data
        conditions = data["conditions"]
        
        # Should include all weather conditions
        condition_values = [c["value"] for c in conditions]
        assert "clear" in condition_values
        assert "rain" in condition_values
        assert "snow" in condition_values
        assert "thunderstorm" in condition_values
        
        # Check format
        for condition in conditions:
            assert "value" in condition
            assert "display_name" in condition
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_weather_config_success(self, mock_get_service):
        """Test GET /api/weather/config returns configuration"""
        # Arrange
        mock_config = {
            "weather_system": {"enabled": True},
            "default_weather": {"condition": "clear"},
            "seasonal_preferences": {"spring": {}}
        }
        
        mock_service = Mock()
        mock_service.validation_service.load_weather_config.return_value = mock_config
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.get("/api/weather/config")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["default_condition"] == "clear"
        assert data["seasonal_support"] is True
    
    @patch('backend.systems.weather.routers.weather_router.get_weather_business_service')
    def test_get_weather_config_handles_missing_data(self, mock_get_service):
        """Test GET /api/weather/config handles missing configuration gracefully"""
        # Arrange
        mock_config = {}  # Empty config
        
        mock_service = Mock()
        mock_service.validation_service.load_weather_config.return_value = mock_config
        mock_get_service.return_value = mock_service
        
        # Act
        response = client.get("/api/weather/config")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Should use defaults
        assert data["enabled"] is True  # Default fallback
        assert data["seasonal_support"] is False  # No seasonal preferences


if __name__ == "__main__":
    pytest.main([__file__]) 