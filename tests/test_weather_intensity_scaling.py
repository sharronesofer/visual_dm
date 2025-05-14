import unittest
from app.core.models.weather_system import WeatherSystem
from app.core.models.time_system import TimeSystem
from app.core.models.season_system import SeasonSystem
from app.core.models.character import Character
from app.core.models.combat_system import CombatSystem
from app.core.enums import WeatherType, WeatherIntensity, Season, StatusEffect
from datetime import timedelta

class TestWeatherIntensityScaling(unittest.TestCase):
    def setUp(self):
        self.time_system = TimeSystem()
        self.season_system = SeasonSystem(self.time_system)
        self.weather_system = WeatherSystem(self.time_system, self.season_system)
        
    def test_intensity_effect_scaling(self):
        """Test that weather effects scale appropriately with intensity."""
        test_weather = WeatherType.RAIN
        self.weather_system.current_weather = test_weather
        
        # Test each intensity level
        for intensity in WeatherIntensity:
            self.weather_system.weather_intensity = intensity
            effects = self.weather_system._calculate_weather_effects()
            
            # Verify effect scaling matches the intensity multiplier
            expected_multiplier = intensity.effect_multiplier
            base_effects = {
                "temperature_modifier": -2.0,  # Base values for rain
                "humidity_modifier": 0.3,
                "wind_modifier": 5
            }
            
            for effect_name, base_value in base_effects.items():
                expected_value = base_value * expected_multiplier
                self.assertAlmostEqual(effects[effect_name], expected_value, places=1,
                    msg=f"Effect {effect_name} not scaling correctly for intensity {intensity}")
                
    def test_intensity_transition_smoothness(self):
        """Test that weather intensity transitions smoothly."""
        # Start with mild rain
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.MILD
        
        # Force a transition to heavy rain
        self.weather_system.weather_intensity = WeatherIntensity.STRONG
        
        # Verify that effects transition smoothly
        initial_effects = self.weather_system._calculate_weather_effects()
        
        # Simulate time passing (half of transition duration)
        self.time_system.advance_time(timedelta(seconds=500))
        mid_transition_effects = self.weather_system._calculate_weather_effects()
        
        # Verify mid-transition values are between initial and final values
        for effect_name in initial_effects:
            initial_value = initial_effects[effect_name]
            final_value = mid_transition_effects[effect_name]
            self.assertGreater(final_value, initial_value,
                msg=f"Effect {effect_name} not transitioning smoothly")
                
    def test_weather_duration_scaling(self):
        """Test that weather duration scales appropriately with intensity."""
        test_cases = [
            (WeatherType.CLEAR, WeatherIntensity.MILD),
            (WeatherType.RAIN, WeatherIntensity.MODERATE),
            (WeatherType.THUNDERSTORM, WeatherIntensity.STRONG),
            (WeatherType.BLIZZARD, WeatherIntensity.SEVERE)
        ]
        
        for weather_type, intensity in test_cases:
            self.weather_system.current_weather = weather_type
            self.weather_system.weather_intensity = intensity
            
            # Get duration for current weather
            duration = self.weather_system.weather_duration.total_seconds()
            
            # Verify duration is within expected range
            self.assertGreaterEqual(duration, 300,  # Minimum 5 minutes
                msg=f"Duration too short for {weather_type} at {intensity}")
            self.assertLessEqual(duration, 7200,  # Maximum 2 hours
                msg=f"Duration too long for {weather_type} at {intensity}")
            
            # Verify more intense weather has shorter duration
            if intensity in [WeatherIntensity.STRONG, WeatherIntensity.SEVERE]:
                self.weather_system.weather_intensity = WeatherIntensity.MILD
                mild_duration = self.weather_system.weather_duration.total_seconds()
                self.assertGreater(mild_duration, duration,
                    msg=f"Intense weather {weather_type} should have shorter duration")
                    
    def test_visual_effect_scaling(self):
        """Test that visual effects scale appropriately with intensity."""
        test_cases = [
            (WeatherType.RAIN, {
                WeatherIntensity.MILD: {"particle_density": 0.3, "visibility": 0.9},
                WeatherIntensity.MODERATE: {"particle_density": 0.6, "visibility": 0.7},
                WeatherIntensity.STRONG: {"particle_density": 0.8, "visibility": 0.5},
                WeatherIntensity.SEVERE: {"particle_density": 1.0, "visibility": 0.3}
            }),
            (WeatherType.SNOW, {
                WeatherIntensity.MILD: {"particle_density": 0.2, "visibility": 0.8},
                WeatherIntensity.MODERATE: {"particle_density": 0.5, "visibility": 0.6},
                WeatherIntensity.STRONG: {"particle_density": 0.7, "visibility": 0.4},
                WeatherIntensity.SEVERE: {"particle_density": 0.9, "visibility": 0.2}
            })
        ]
        
        for weather_type, intensity_effects in test_cases:
            self.weather_system.current_weather = weather_type
            
            for intensity, expected_effects in intensity_effects.items():
                self.weather_system.weather_intensity = intensity
                conditions = self.weather_system.get_current_conditions()
                
                # Verify visibility scales with intensity
                self.assertAlmostEqual(
                    conditions["visibility"],
                    expected_effects["visibility"],
                    places=1,
                    msg=f"Visibility not scaling correctly for {weather_type} at {intensity}"
                )
                
    def test_combat_effect_scaling(self):
        """Test that weather effects on combat scale appropriately with intensity."""
        combat_system = CombatSystem()
        character = Character()
        
        test_cases = [
            (WeatherType.RAIN, {
                WeatherIntensity.MILD: {"accuracy": -0.05, "evasion": 0.05},
                WeatherIntensity.MODERATE: {"accuracy": -0.10, "evasion": 0.10},
                WeatherIntensity.STRONG: {"accuracy": -0.20, "evasion": 0.15},
                WeatherIntensity.SEVERE: {"accuracy": -0.30, "evasion": 0.20}
            }),
            (WeatherType.FOG, {
                WeatherIntensity.MILD: {"accuracy": -0.10, "evasion": 0.10},
                WeatherIntensity.MODERATE: {"accuracy": -0.20, "evasion": 0.15},
                WeatherIntensity.STRONG: {"accuracy": -0.30, "evasion": 0.20},
                WeatherIntensity.SEVERE: {"accuracy": -0.40, "evasion": 0.25}
            })
        ]
        
        for weather_type, intensity_effects in test_cases:
            self.weather_system.current_weather = weather_type
            
            for intensity, expected_effects in intensity_effects.items():
                self.weather_system.weather_intensity = intensity
                combat_stats = combat_system.calculate_combat_stats(character, self.weather_system)
                
                self.assertAlmostEqual(
                    combat_stats.accuracy_modifier,
                    expected_effects["accuracy"],
                    places=2,
                    msg=f"Accuracy modifier not scaling correctly for {weather_type} at {intensity}"
                )
                self.assertAlmostEqual(
                    combat_stats.evasion_modifier,
                    expected_effects["evasion"],
                    places=2,
                    msg=f"Evasion modifier not scaling correctly for {weather_type} at {intensity}"
                )
                
    def test_status_effect_scaling(self):
        """Test that weather-induced status effects scale with intensity."""
        character = Character()
        
        test_cases = [
            (WeatherType.RAIN, {
                WeatherIntensity.MILD: {"wet": 0.3, "chilled": 0.0},
                WeatherIntensity.MODERATE: {"wet": 0.6, "chilled": 0.2},
                WeatherIntensity.STRONG: {"wet": 0.8, "chilled": 0.4},
                WeatherIntensity.SEVERE: {"wet": 1.0, "chilled": 0.6}
            }),
            (WeatherType.SNOW, {
                WeatherIntensity.MILD: {"chilled": 0.3, "frozen": 0.0},
                WeatherIntensity.MODERATE: {"chilled": 0.6, "frozen": 0.2},
                WeatherIntensity.STRONG: {"chilled": 0.8, "frozen": 0.4},
                WeatherIntensity.SEVERE: {"chilled": 1.0, "frozen": 0.6}
            })
        ]
        
        for weather_type, intensity_effects in test_cases:
            self.weather_system.current_weather = weather_type
            
            for intensity, expected_effects in intensity_effects.items():
                self.weather_system.weather_intensity = intensity
                status_effects = self.weather_system.calculate_status_effects(character)
                
                for effect_name, expected_value in expected_effects.items():
                    actual_value = next(
                        (effect.intensity for effect in status_effects 
                         if effect.type == StatusEffect[effect_name.upper()]),
                        0.0
                    )
                    self.assertAlmostEqual(
                        actual_value,
                        expected_value,
                        places=2,
                        msg=f"Status effect {effect_name} not scaling correctly for {weather_type} at {intensity}"
                    )
                    
    def test_environmental_interaction_scaling(self):
        """Test that weather effects scale properly with environmental conditions."""
        test_cases = [
            {
                "weather": WeatherType.RAIN,
                "intensity": WeatherIntensity.STRONG,
                "season": Season.SUMMER,
                "expected": {
                    "temperature_modifier": -4.0,  # Stronger cooling in summer
                    "humidity_modifier": 0.6
                }
            },
            {
                "weather": WeatherType.SNOW,
                "intensity": WeatherIntensity.STRONG,
                "season": Season.WINTER,
                "expected": {
                    "temperature_modifier": -8.0,  # Enhanced cooling in winter
                    "humidity_modifier": 0.3
                }
            }
        ]
        
        for case in test_cases:
            self.season_system.current_season = case["season"]
            self.weather_system.current_weather = case["weather"]
            self.weather_system.weather_intensity = case["intensity"]
            
            effects = self.weather_system._calculate_weather_effects()
            
            for effect_name, expected_value in case["expected"].items():
                self.assertAlmostEqual(
                    effects[effect_name],
                    expected_value,
                    places=1,
                    msg=f"Effect {effect_name} not scaling correctly with environment"
                )

if __name__ == '__main__':
    unittest.main() 