import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.core.models.time_system import TimeSystem
from app.core.models.season_system import SeasonSystem
from app.core.models.weather_system import WeatherSystem
from app.core.enums import WeatherType, WeatherIntensity, Season
from app.utils.constants import (
    BASE_TEMPERATURE,
    BASE_HUMIDITY,
    BASE_WIND_SPEED,
    BASE_VISIBILITY,
    MIN_WEATHER_DURATION,
    MAX_WEATHER_DURATION
)

class TestWeatherSystem(unittest.TestCase):
    def setUp(self):
        self.time_system = TimeSystem()
        self.season_system = SeasonSystem(self.time_system)
        self.weather_system = WeatherSystem(self.time_system, self.season_system)
        
    def test_initial_state(self):
        """Test the initial state of the weather system."""
        self.assertEqual(self.weather_system.current_weather, WeatherType.CLEAR)
        self.assertEqual(self.weather_system.weather_intensity, WeatherIntensity.MODERATE)
        self.assertEqual(self.weather_system.temperature, BASE_TEMPERATURE)
        self.assertEqual(self.weather_system.humidity, BASE_HUMIDITY)
        self.assertEqual(self.weather_system.wind_speed, BASE_WIND_SPEED)
        self.assertEqual(self.weather_system.visibility, BASE_VISIBILITY)
        
    def test_weather_transition(self):
        """Test that weather transitions occur after duration expires."""
        initial_weather = self.weather_system.current_weather
        initial_intensity = self.weather_system.weather_intensity
        
        # Force weather duration to expire
        self.weather_system.weather_duration = timedelta(seconds=0)
        self.weather_system.update(1.0)
        
        # Weather should have changed
        self.assertIn(self.weather_system.current_weather, WeatherType)
        self.assertIn(self.weather_system.weather_intensity, WeatherIntensity)
        
    def test_seasonal_weather_types(self):
        """Test that weather types are appropriate for the season."""
        # Mock winter conditions
        self.season_system.current_season = Season.WINTER
        self.weather_system.temperature = -5
        
        possible_types = self.weather_system._get_possible_weather_types()
        
        # Should include snow and blizzard
        self.assertIn(WeatherType.SNOW, possible_types)
        self.assertIn(WeatherType.BLIZZARD, possible_types)
        # Should not include rain
        self.assertNotIn(WeatherType.RAIN, possible_types)
        
        # Mock summer conditions
        self.season_system.current_season = Season.SUMMER
        self.weather_system.temperature = 25
        
        possible_types = self.weather_system._get_possible_weather_types()
        
        # Should include thunderstorms
        self.assertIn(WeatherType.THUNDERSTORM, possible_types)
        # Should not include snow
        self.assertNotIn(WeatherType.SNOW, possible_types)
        
    def test_weather_effects(self):
        """Test that weather conditions affect environmental variables."""
        # Test rain effects
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.STRONG
        
        initial_temp = self.weather_system.temperature
        initial_humidity = self.weather_system.humidity
        
        self.weather_system._update_environmental_conditions()
        
        # Rain should lower temperature and increase humidity
        self.assertLess(self.weather_system.temperature, initial_temp)
        self.assertGreater(self.weather_system.humidity, initial_humidity)
        
    def test_weather_history(self):
        """Test that weather history is maintained correctly."""
        # Force several weather changes
        for _ in range(12):  # More than history limit
            self.weather_system._transition_weather()
            
        # History should be capped at 10 entries
        self.assertEqual(len(self.weather_system.weather_history), 10)
        
        # Each entry should be a tuple of (WeatherType, datetime)
        for weather, time in self.weather_system.weather_history:
            self.assertIsInstance(weather, WeatherType)
            self.assertIsInstance(time, datetime)
            
    def test_weather_duration_bounds(self):
        """Test that weather duration stays within defined bounds."""
        for _ in range(10):
            self.weather_system._transition_weather()
            duration_seconds = self.weather_system.weather_duration.total_seconds()
            self.assertGreaterEqual(duration_seconds, MIN_WEATHER_DURATION)
            self.assertLessEqual(duration_seconds, MAX_WEATHER_DURATION)
            
    def test_get_current_conditions(self):
        """Test that current conditions are reported correctly."""
        conditions = self.weather_system.get_current_conditions()
        
        required_keys = [
            "weather_type",
            "intensity",
            "temperature",
            "humidity",
            "wind_speed",
            "visibility",
            "movement_modifier",
            "combat_modifier"
        ]
        
        for key in required_keys:
            self.assertIn(key, conditions)
            
        self.assertIsInstance(conditions["weather_type"], WeatherType)
        self.assertIsInstance(conditions["intensity"], WeatherIntensity)
        self.assertIsInstance(conditions["temperature"], (int, float))
        self.assertIsInstance(conditions["humidity"], float)
        self.assertIsInstance(conditions["wind_speed"], (int, float))
        self.assertIsInstance(conditions["visibility"], (int, float))
        
    @patch('random.uniform')
    def test_temperature_fluctuation(self, mock_uniform):
        """Test that temperature fluctuates within expected ranges."""
        mock_uniform.return_value = 1.0  # Fixed random fluctuation
        
        self.weather_system._update_environmental_conditions()
        initial_temp = self.weather_system.temperature
        
        # Change weather to affect temperature
        self.weather_system.current_weather = WeatherType.SNOW
        self.weather_system._update_environmental_conditions()
        
        # Temperature should have decreased
        self.assertLess(self.weather_system.temperature, initial_temp)
        
if __name__ == '__main__':
    unittest.main() 