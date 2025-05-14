import unittest
from unittest.mock import MagicMock, patch
from app.core.models.weather_system import WeatherSystem
from app.core.models.time_system import TimeSystem
from app.core.models.season_system import SeasonSystem
from app.core.models.game_state import GameState
from app.core.models.scene_manager import SceneManager
from app.core.enums import WeatherType, WeatherIntensity, Season, GameView

class TestWeatherConsistency(unittest.TestCase):
    def setUp(self):
        self.time_system = TimeSystem()
        self.season_system = SeasonSystem(self.time_system)
        self.weather_system = WeatherSystem(self.time_system, self.season_system)
        
        # Define TypeScript weather type mappings
        self.ts_weather_mappings = {
            'clear': WeatherType.CLEAR,
            'rain': WeatherType.RAIN,
            'storm': WeatherType.THUNDERSTORM,
            'snow': WeatherType.SNOW,
            'fog': WeatherType.FOG,
            'blizzard': WeatherType.BLIZZARD,
            # Note: 'sandstorm' and 'heatwave' don't have direct Python equivalents
        }
        
        # Define TypeScript intensity mappings
        self.ts_intensity_mappings = {
            'light': WeatherIntensity.WEAK,
            'moderate': WeatherIntensity.MODERATE,
            'heavy': WeatherIntensity.STRONG,
            'extreme': WeatherIntensity.SEVERE
        }
        
    def test_weather_type_consistency(self):
        """Test that weather types in Python match their TypeScript counterparts."""
        for ts_type, py_type in self.ts_weather_mappings.items():
            # Verify the Python type exists
            self.assertIn(py_type, WeatherType)
            
            # Get weather effects for both implementations
            self.weather_system.current_weather = py_type
            py_effects = self.weather_system._calculate_weather_effects()
            
            # Verify expected effects exist
            if ts_type in ['rain', 'storm']:
                self.assertIn('temperature_modifier', py_effects)
                self.assertIn('humidity_modifier', py_effects)
                self.assertIn('wind_modifier', py_effects)
                # Rain/storm should decrease temperature
                self.assertLess(py_effects['temperature_modifier'], 0)
                # And increase humidity
                self.assertGreater(py_effects['humidity_modifier'], 0)
                
            elif ts_type in ['snow', 'blizzard']:
                self.assertIn('temperature_modifier', py_effects)
                self.assertLess(py_effects['temperature_modifier'], 0)
                # Snow/blizzard should have significant wind
                self.assertGreater(py_effects['wind_modifier'], 0)
                
            elif ts_type == 'fog':
                self.assertIn('visibility', py_effects)
                # Fog should reduce visibility
                self.assertLess(py_effects['visibility'], 1.0)
                
    def test_intensity_consistency(self):
        """Test that weather intensities are consistent between implementations."""
        # TypeScript intensities: light (0.5), moderate (1.0), heavy (1.5), extreme (2.0)
        # Python should scale effects similarly
        
        test_weather = WeatherType.RAIN
        self.weather_system.current_weather = test_weather
        
        for ts_intensity, py_intensity in self.ts_intensity_mappings.items():
            self.weather_system.weather_intensity = py_intensity
            effects = self.weather_system._calculate_weather_effects()
            
            # Get the expected multiplier based on TypeScript values
            ts_multiplier = {
                'light': 0.5,
                'moderate': 1.0,
                'heavy': 1.5,
                'extreme': 2.0
            }[ts_intensity]
            
            # Python effects should scale proportionally
            base_effects = self.weather_system._calculate_weather_effects()
            for effect_name, effect_value in effects.items():
                expected_value = base_effects[effect_name] * ts_multiplier
                self.assertAlmostEqual(effect_value, expected_value, places=1)
                
    def test_seasonal_consistency(self):
        """Test that seasonal weather patterns are consistent."""
        # Test winter conditions
        self.season_system.current_season = Season.WINTER
        self.weather_system.temperature = -5
        winter_types = self.weather_system._get_possible_weather_types()
        
        # Should include snow and blizzard
        self.assertIn(WeatherType.SNOW, winter_types)
        self.assertIn(WeatherType.BLIZZARD, winter_types)
        # Should not include rain
        self.assertNotIn(WeatherType.RAIN, winter_types)
        
        # Test summer conditions
        self.season_system.current_season = Season.SUMMER
        self.weather_system.temperature = 25
        summer_types = self.weather_system._get_possible_weather_types()
        
        # Should include thunderstorms
        self.assertIn(WeatherType.THUNDERSTORM, summer_types)
        # Should not include snow
        self.assertNotIn(WeatherType.SNOW, summer_types)
        
    def test_effect_application_consistency(self):
        """Test that weather effects are applied consistently."""
        # Test rain effects
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.STRONG
        
        conditions = self.weather_system.get_current_conditions()
        
        # Verify movement modifier exists and is negative (matches TypeScript -0.2 * 1.5)
        self.assertLess(conditions['movement_modifier'], 0)
        
        # Verify visibility is reduced
        self.assertLess(conditions['visibility'], 1.0)
        
        # Test snow effects
        self.weather_system.current_weather = WeatherType.SNOW
        conditions = self.weather_system.get_current_conditions()
        
        # Snow should have stronger movement penalty than rain
        self.assertLess(conditions['movement_modifier'], 0)
        self.assertLess(conditions['visibility'], 1.0)
        
    def test_visual_consistency_across_views(self):
        """Test that weather effects maintain visual consistency across different game views."""
        # Mock the scene manager and game state
        scene_manager = MagicMock(spec=SceneManager)
        game_state = MagicMock(spec=GameState)
        
        # Set up test weather
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.STRONG
        initial_effects = self.weather_system.get_current_conditions()
        
        # Test different game views
        views = [GameView.MAIN_GAMEPLAY, GameView.MENU, GameView.CUTSCENE, GameView.DIALOGUE]
        for view in views:
            game_state.current_view = view
            # Trigger view change
            self.weather_system.on_view_changed(view)
            # Get effects after view change
            current_effects = self.weather_system.get_current_conditions()
            
            # Effects should remain consistent
            self.assertEqual(current_effects['weather_type'], initial_effects['weather_type'])
            self.assertEqual(current_effects['intensity'], initial_effects['intensity'])
            self.assertEqual(current_effects['visibility'], initial_effects['visibility'])
            self.assertEqual(current_effects['movement_modifier'], initial_effects['movement_modifier'])
            
    def test_state_persistence(self):
        """Test that weather states persist correctly during gameplay transitions."""
        # Set up initial weather state
        self.weather_system.current_weather = WeatherType.THUNDERSTORM
        self.weather_system.weather_intensity = WeatherIntensity.SEVERE
        initial_state = self.weather_system.serialize_state()
        
        # Test scene transitions
        self.weather_system.on_scene_change("new_scene")
        after_scene_state = self.weather_system.serialize_state()
        self.assertEqual(initial_state, after_scene_state)
        
        # Test save/load
        saved_state = self.weather_system.serialize_state()
        self.weather_system.current_weather = WeatherType.CLEAR  # Change state
        self.weather_system.deserialize_state(saved_state)  # Load state
        loaded_state = self.weather_system.serialize_state()
        self.assertEqual(saved_state, loaded_state)
        
        # Test fast travel
        self.weather_system.on_fast_travel_begin()
        during_travel_state = self.weather_system.serialize_state()
        self.assertEqual(initial_state, during_travel_state)
        self.weather_system.on_fast_travel_end()
        after_travel_state = self.weather_system.serialize_state()
        self.assertEqual(initial_state, after_travel_state)
        
    def test_transition_visual_consistency(self):
        """Test that weather transitions maintain visual consistency."""
        # Set up transition test
        start_weather = WeatherType.CLEAR
        end_weather = WeatherType.RAIN
        transition_duration = 5.0  # seconds
        
        self.weather_system.current_weather = start_weather
        initial_effects = self.weather_system.get_current_conditions()
        
        # Start transition
        self.weather_system.transition_to_weather(end_weather, transition_duration)
        
        # Check midpoint (should be halfway between effects)
        self.weather_system.update(transition_duration / 2)
        mid_effects = self.weather_system.get_current_conditions()
        
        # Visibility should be halfway between clear and rain
        expected_mid_visibility = (initial_effects['visibility'] + 0.7) / 2  # Rain visibility is 0.7
        self.assertAlmostEqual(mid_effects['visibility'], expected_mid_visibility, places=2)
        
        # Complete transition
        self.weather_system.update(transition_duration / 2)
        final_effects = self.weather_system.get_current_conditions()
        
        # Should match rain effects
        self.assertEqual(final_effects['weather_type'], WeatherType.RAIN)
        self.assertAlmostEqual(final_effects['visibility'], 0.7, places=2)

if __name__ == '__main__':
    unittest.main() 