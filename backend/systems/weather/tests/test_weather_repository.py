"""
Tests for Weather Repository

Tests for both the protocol and implementation following Development Bible patterns.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from backend.systems.weather.repositories.weather_repository import WeatherRepositoryImpl
from backend.systems.weather.models.weather_model import Weather, WeatherCondition


class TestWeatherRepositoryImpl:
    """Test suite for WeatherRepositoryImpl"""
    
    def setup_method(self):
        """Setup test dependencies"""
        self.mock_persistence_service = Mock()
        self.repository = WeatherRepositoryImpl(self.mock_persistence_service)
    
    def test_save_weather_state_with_persistence_service(self):
        """Test saving weather state using persistence service"""
        # Arrange
        weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=65.0,
            humidity=50.0,
            wind_speed=5.0,
            pressure=29.92,
            visibility=10.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        self.mock_persistence_service.save_weather.return_value = True
        
        # Act
        result = self.repository.save_weather_state(weather)
        
        # Assert
        assert result is True
        self.mock_persistence_service.save_weather.assert_called_once_with(weather)
    
    def test_save_weather_state_fallback_to_json(self):
        """Test saving weather state falls back to JSON when no persistence service"""
        # Arrange
        repository = WeatherRepositoryImpl(None)  # No persistence service
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
        
        with patch('backend.systems.weather.repositories.weather_repository.save_json') as mock_save_json:
            mock_save_json.return_value = True
            
            # Act
            result = repository.save_weather_state(weather)
            
            # Assert
            assert result is True
            mock_save_json.assert_called_once()
            args = mock_save_json.call_args[0]
            assert args[0] == "weather_current.json"
            assert args[1] == weather.to_dict()
    
    def test_save_weather_state_handles_exceptions(self):
        """Test save_weather_state handles exceptions gracefully"""
        # Arrange
        weather = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=65.0,
            humidity=50.0,
            wind_speed=5.0,
            pressure=29.92,
            visibility=10.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        self.mock_persistence_service.save_weather.side_effect = Exception("Save error")
        
        # Act
        result = self.repository.save_weather_state(weather)
        
        # Assert
        assert result is False
    
    def test_load_weather_state_with_persistence_service(self):
        """Test loading weather state using persistence service"""
        # Arrange
        expected_weather = Weather(
            condition=WeatherCondition.SNOW,
            temperature=25.0,
            humidity=85.0,
            wind_speed=10.0,
            pressure=29.2,
            visibility=2.0,
            timestamp=datetime.utcnow(),
            duration_hours=6
        )
        self.mock_persistence_service.load_weather.return_value = expected_weather
        
        # Act
        result = self.repository.load_weather_state()
        
        # Assert
        assert result == expected_weather
        self.mock_persistence_service.load_weather.assert_called_once()
    
    def test_load_weather_state_fallback_to_json(self):
        """Test loading weather state falls back to JSON when no persistence service"""
        # Arrange
        repository = WeatherRepositoryImpl(None)  # No persistence service
        weather_data = {
            "condition": "fog",
            "temperature": 45.0,
            "humidity": 95.0,
            "wind_speed": 2.0,
            "pressure": 29.8,
            "visibility": 0.5,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_hours": 5
        }
        
        with patch('backend.systems.weather.repositories.weather_repository.load_json') as mock_load_json:
            mock_load_json.return_value = weather_data
            
            # Act
            result = repository.load_weather_state()
            
            # Assert
            assert result is not None
            assert result.condition == WeatherCondition.FOG
            assert result.temperature == 45.0
            mock_load_json.assert_called_once_with("weather_current.json")
    
    def test_load_weather_state_returns_none_when_no_data(self):
        """Test load_weather_state returns None when no data exists"""
        # Arrange
        self.mock_persistence_service.load_weather.return_value = None
        
        # Act
        result = self.repository.load_weather_state()
        
        # Assert
        assert result is None
    
    def test_load_weather_state_handles_exceptions(self):
        """Test load_weather_state handles exceptions gracefully"""
        # Arrange
        self.mock_persistence_service.load_weather.side_effect = Exception("Load error")
        
        # Act
        result = self.repository.load_weather_state()
        
        # Assert
        assert result is None
    
    def test_add_to_history_adds_weather(self):
        """Test add_to_history adds weather to internal history"""
        # Arrange
        weather1 = Weather(
            condition=WeatherCondition.CLEAR,
            temperature=65.0,
            humidity=50.0,
            wind_speed=5.0,
            pressure=29.92,
            visibility=10.0,
            timestamp=datetime.utcnow(),
            duration_hours=4
        )
        weather2 = Weather(
            condition=WeatherCondition.CLOUDY,
            temperature=60.0,
            humidity=70.0,
            wind_speed=10.0,
            pressure=29.8,
            visibility=8.0,
            timestamp=datetime.utcnow(),
            duration_hours=3
        )
        
        # Act
        self.repository.add_to_history(weather1)
        self.repository.add_to_history(weather2)
        
        # Assert
        history = self.repository.get_weather_history()
        assert len(history) == 2
        assert history[0] == weather1
        assert history[1] == weather2
    
    def test_get_weather_history_with_limit(self):
        """Test get_weather_history respects limit parameter"""
        # Arrange - add multiple weather entries
        for i in range(10):
            weather = Weather(
                condition=WeatherCondition.CLEAR,
                temperature=65.0 + i,
                humidity=50.0,
                wind_speed=5.0,
                pressure=29.92,
                visibility=10.0,
                timestamp=datetime.utcnow() + timedelta(hours=i),
                duration_hours=4
            )
            self.repository.add_to_history(weather)
        
        # Act
        history = self.repository.get_weather_history(limit=3)
        
        # Assert
        assert len(history) == 3
        # Should return the last 3 entries
        assert history[0].temperature == 67.0  # 65.0 + 7
        assert history[1].temperature == 68.0  # 65.0 + 8
        assert history[2].temperature == 69.0  # 65.0 + 9
    
    def test_get_weather_history_unlimited(self):
        """Test get_weather_history with unlimited (0 or negative limit)"""
        # Arrange
        for i in range(5):
            weather = Weather(
                condition=WeatherCondition.CLEAR,
                temperature=65.0 + i,
                humidity=50.0,
                wind_speed=5.0,
                pressure=29.92,
                visibility=10.0,
                timestamp=datetime.utcnow() + timedelta(hours=i),
                duration_hours=4
            )
            self.repository.add_to_history(weather)
        
        # Act
        history = self.repository.get_weather_history(limit=0)
        
        # Assert
        assert len(history) == 5
    
    def test_history_size_management(self):
        """Test that history is limited to 1000 entries to prevent unbounded growth"""
        # Arrange - add more than 1000 entries
        for i in range(1005):
            weather = Weather(
                condition=WeatherCondition.CLEAR,
                temperature=65.0,
                humidity=50.0,
                wind_speed=5.0,
                pressure=29.92,
                visibility=10.0,
                timestamp=datetime.utcnow() + timedelta(hours=i),
                duration_hours=4
            )
            self.repository.add_to_history(weather)
        
        # Act
        history = self.repository.get_weather_history(limit=0)
        
        # Assert
        assert len(history) == 1000  # Should be capped at 1000
    
    def test_clear_weather_history(self):
        """Test clear_weather_history removes all history"""
        # Arrange - add some history
        for i in range(5):
            weather = Weather(
                condition=WeatherCondition.CLEAR,
                temperature=65.0 + i,
                humidity=50.0,
                wind_speed=5.0,
                pressure=29.92,
                visibility=10.0,
                timestamp=datetime.utcnow() + timedelta(hours=i),
                duration_hours=4
            )
            self.repository.add_to_history(weather)
        
        # Act
        result = self.repository.clear_weather_history()
        
        # Assert
        assert result is True
        history = self.repository.get_weather_history()
        assert len(history) == 0
    
    def test_clear_weather_history_handles_exceptions(self):
        """Test clear_weather_history handles exceptions gracefully"""
        # Arrange - simulate exception during clear
        with patch.object(self.repository._weather_history, 'clear', side_effect=Exception("Clear error")):
            # Act
            result = self.repository.clear_weather_history()
            
            # Assert
            assert result is False


if __name__ == "__main__":
    pytest.main([__file__]) 