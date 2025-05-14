import unittest
from datetime import timedelta
from app.core.models.weather_system import WeatherSystem
from app.core.models.time_system import TimeSystem
from app.core.models.season_system import SeasonSystem
from app.core.models.character import Character
from app.core.models.region import Region
from app.core.enums import WeatherType, WeatherIntensity, Season, RegionType, StatusEffect
from app.utils.constants import (
    BASE_TEMPERATURE,
    BASE_HUMIDITY,
    BASE_WIND_SPEED,
    BASE_VISIBILITY
)

class TestWeatherGameplayImpacts(unittest.TestCase):
    def setUp(self):
        self.time_system = TimeSystem()
        self.season_system = SeasonSystem(self.time_system)
        self.weather_system = WeatherSystem(self.time_system, self.season_system)
        
    def test_environmental_conditions_update(self):
        """Test that environmental conditions update correctly with weather changes."""
        # Test clear weather baseline
        self.weather_system.current_weather = WeatherType.CLEAR
        self.weather_system.weather_intensity = WeatherIntensity.MODERATE
        self.weather_system._update_environmental_conditions()
        
        base_temp = self.weather_system.temperature
        base_humidity = self.weather_system.humidity
        base_wind = self.weather_system.wind_speed
        base_visibility = self.weather_system.visibility
        
        # Test thunderstorm effects
        self.weather_system.current_weather = WeatherType.THUNDERSTORM
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        self.weather_system._update_environmental_conditions()
        
        # Temperature should decrease
        self.assertLess(self.weather_system.temperature, base_temp)
        # Humidity should increase
        self.assertGreater(self.weather_system.humidity, base_humidity)
        # Wind speed should increase
        self.assertGreater(self.weather_system.wind_speed, base_wind)
        # Visibility should decrease
        self.assertLess(self.weather_system.visibility, base_visibility)
        
    def test_weather_intensity_gameplay_effects(self):
        """Test that weather intensity properly affects gameplay modifiers."""
        # Test light rain
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.LIGHT
        conditions = self.weather_system.get_current_conditions()
        
        light_movement_penalty = conditions["movement_modifier"]
        light_combat_penalty = conditions["combat_modifier"]
        
        # Test heavy rain - should have stronger effects
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        conditions = self.weather_system.get_current_conditions()
        
        self.assertLess(conditions["movement_modifier"], light_movement_penalty)
        self.assertLess(conditions["combat_modifier"], light_combat_penalty)
        
    def test_seasonal_weather_generation(self):
        """Test that weather generation is influenced by seasons."""
        # Test winter weather patterns
        self.season_system.current_season = Season.WINTER
        possible_types = self.weather_system._get_possible_weather_types()
        
        self.assertIn(WeatherType.SNOW, possible_types)
        self.assertIn(WeatherType.BLIZZARD, possible_types)
        
        # Test summer weather patterns
        self.season_system.current_season = Season.SUMMER
        possible_types = self.weather_system._get_possible_weather_types()
        
        self.assertIn(WeatherType.THUNDERSTORM, possible_types)
        self.assertIn(WeatherType.HAIL, possible_types)
        
    def test_time_based_weather_generation(self):
        """Test that weather generation considers time of day."""
        # Test dawn/dusk fog generation
        dawn_fog_count = 0
        regular_fog_count = 0
        
        for _ in range(100):  # Run multiple trials
            # Test at dawn
            self.time_system.set_time_of_day("DAWN")
            if WeatherType.FOG in self.weather_system._get_possible_weather_types():
                dawn_fog_count += 1
                
            # Test at noon
            self.time_system.set_time_of_day("NOON")
            if WeatherType.FOG in self.weather_system._get_possible_weather_types():
                regular_fog_count += 1
        
        # Fog should be more common at dawn
        self.assertGreater(dawn_fog_count, regular_fog_count)
        
    def test_weather_transition_timing(self):
        """Test that weather transitions occur at appropriate intervals."""
        initial_weather = self.weather_system.current_weather
        initial_time = self.time_system.current_time
        
        # Set a short duration for testing
        self.weather_system.weather_duration = timedelta(seconds=10)
        
        # Advance time past duration
        self.time_system.advance_time(15)  # 15 seconds
        self.weather_system.update(15)
        
        # Weather should have changed
        self.assertNotEqual(self.weather_system.current_weather, initial_weather)
        
        # New weather change should be scheduled
        events = self.time_system.get_events()
        weather_events = [e for e in events if e.type == "weather_change"]
        
        self.assertTrue(any(e.trigger_time > initial_time for e in weather_events))
        
    def test_weather_pattern_consistency(self):
        """Test that weather patterns maintain consistency over time."""
        weather_history = []
        
        # Generate weather for multiple cycles
        for _ in range(50):
            self.time_system.advance_time(60)  # 1 minute
            self.weather_system.update(60)
            weather_history.append(self.weather_system.current_weather)
        
        # Count transitions between weather types
        transitions = {}
        for i in range(len(weather_history) - 1):
            from_weather = weather_history[i]
            to_weather = weather_history[i + 1]
            key = (from_weather, to_weather)
            transitions[key] = transitions.get(key, 0) + 1
        
        # Check for unrealistic transitions
        unrealistic_pairs = [
            (WeatherType.CLEAR, WeatherType.BLIZZARD),
            (WeatherType.SNOW, WeatherType.THUNDERSTORM),
            (WeatherType.HAIL, WeatherType.FOG)
        ]
        
        for pair in unrealistic_pairs:
            self.assertNotIn(pair, transitions, 
                f"Found unrealistic weather transition: {pair[0]} -> {pair[1]}")
        
    def test_character_status_effects(self):
        """Test that weather conditions properly apply status effects to characters."""
        character = Character("Test Character")
        
        # Test cold weather effects
        self.weather_system.current_weather = WeatherType.SNOW
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        self.weather_system.temperature = -10  # Very cold
        
        self.weather_system.apply_weather_effects(character)
        
        # Check for cold-related status effects
        self.assertIn(StatusEffect.CHILLED, character.status_effects)
        self.assertLess(character.stamina_regeneration_rate, character.base_stamina_regeneration_rate)
        
        # Test heat effects
        self.weather_system.current_weather = WeatherType.CLEAR
        self.weather_system.weather_intensity = WeatherIntensity.EXTREME
        self.weather_system.temperature = 40  # Very hot
        
        self.weather_system.apply_weather_effects(character)
        
        # Check for heat-related status effects
        self.assertIn(StatusEffect.OVERHEATED, character.status_effects)
        self.assertLess(character.movement_speed, character.base_movement_speed)
        
    def test_compound_weather_conditions(self):
        """Test that multiple weather conditions combine effects appropriately."""
        # Test rain + wind combination
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        self.weather_system.wind_speed = BASE_WIND_SPEED * 2
        
        conditions = self.weather_system.get_current_conditions()
        
        # Combined effect should be stronger than individual effects
        self.assertLess(conditions["visibility"], 
                       self.weather_system._calculate_base_visibility_modifier(WeatherType.RAIN))
        self.assertLess(conditions["ranged_combat_modifier"], 
                       self.weather_system._calculate_base_combat_modifier(WeatherType.RAIN))
        
        # Test snow + fog combination
        self.weather_system.current_weather = WeatherType.SNOW
        self.weather_system._add_secondary_weather(WeatherType.FOG)
        
        conditions = self.weather_system.get_current_conditions()
        
        # Visibility should be severely reduced
        self.assertLess(conditions["visibility"], 
                       min(self.weather_system._calculate_base_visibility_modifier(WeatherType.SNOW),
                           self.weather_system._calculate_base_visibility_modifier(WeatherType.FOG)))
        
    def test_region_specific_weather(self):
        """Test that different regions influence weather generation and effects."""
        # Test desert region
        desert_region = Region("Desert", RegionType.DESERT)
        self.weather_system.set_current_region(desert_region)
        
        # Generate weather multiple times
        desert_weather_types = set()
        for _ in range(50):
            self.weather_system.generate_weather()
            desert_weather_types.add(self.weather_system.current_weather)
        
        # Desert should have specific weather patterns
        self.assertIn(WeatherType.SANDSTORM, desert_weather_types)
        self.assertNotIn(WeatherType.SNOW, desert_weather_types)
        
        # Test mountain region
        mountain_region = Region("Mountains", RegionType.MOUNTAIN)
        self.weather_system.set_current_region(mountain_region)
        
        # Generate weather multiple times
        mountain_weather_types = set()
        for _ in range(50):
            self.weather_system.generate_weather()
            mountain_weather_types.add(self.weather_system.current_weather)
        
        # Mountains should have different weather patterns
        self.assertIn(WeatherType.SNOW, mountain_weather_types)
        self.assertNotIn(WeatherType.SANDSTORM, mountain_weather_types)
        
    def test_weather_effect_stacking(self):
        """Test that weather effects stack appropriately with other game modifiers."""
        character = Character("Test Character")
        
        # Apply a base movement speed buff
        character.add_modifier("speed_boost", 1.5)  # 50% speed boost
        base_speed = character.movement_speed
        
        # Apply heavy rain weather effects
        self.weather_system.current_weather = WeatherType.RAIN
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        self.weather_system.apply_weather_effects(character)
        
        # Speed should be reduced but still above base
        self.assertLess(character.movement_speed, base_speed)
        self.assertGreater(character.movement_speed, character.base_movement_speed)
        
        # Test combat modifier stacking
        character.add_modifier("accuracy_boost", 1.3)  # 30% accuracy boost
        base_accuracy = character.accuracy
        
        # Apply fog effects
        self.weather_system.current_weather = WeatherType.FOG
        self.weather_system.weather_intensity = WeatherIntensity.HEAVY
        self.weather_system.apply_weather_effects(character)
        
        # Accuracy should be reduced but still affected by the boost
        self.assertLess(character.accuracy, base_accuracy)
        self.assertGreater(character.accuracy, character.base_accuracy) 