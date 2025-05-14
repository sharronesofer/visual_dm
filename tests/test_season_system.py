import unittest
from datetime import datetime, timedelta
from app.core.models.time_system import TimeSystem
from app.core.models.season_system import SeasonSystem
from app.core.enums import Season
from app.utils.constants import DAYS_PER_SEASON

class TestSeasonSystem(unittest.TestCase):
    def setUp(self):
        self.time_system = TimeSystem()
        self.season_system = SeasonSystem(self.time_system)
        
    def test_initial_state(self):
        """Test the initial state of the season system."""
        self.assertEqual(self.season_system.current_season, Season.SPRING)
        self.assertEqual(self.season_system.season_progress, 0.0)
        self.assertEqual(len(self.season_system.seasonal_events), 1)  # Season change event
        
    def test_season_progression(self):
        """Test that seasons change correctly as time advances."""
        # Advance almost to season change
        days_to_advance = DAYS_PER_SEASON - 1
        self.time_system.advance_time(days=days_to_advance)
        self.season_system.update(0)
        
        # Should still be spring but close to summer
        self.assertEqual(self.season_system.current_season, Season.SPRING)
        self.assertAlmostEqual(self.season_system.season_progress, 0.989, places=3)
        
        # Advance one more day to trigger season change
        self.time_system.advance_time(days=1)
        self.season_system.update(0)
        
        # Should now be summer
        self.assertEqual(self.season_system.current_season, Season.SUMMER)
        self.assertAlmostEqual(self.season_system.season_progress, 0.0, places=3)
        
    def test_seasonal_effects(self):
        """Test that seasonal effects are calculated correctly."""
        effects = self.season_system.get_current_effects()
        
        # Test spring effects
        self.assertEqual(effects["temperature_modifier"], 0.0)  # Spring is neutral
        self.assertEqual(effects["precipitation_chance"], 0.4)  # Spring is rainy
        self.assertIn("foliage_density", effects)
        self.assertIn("day_length", effects)
        self.assertIn("color_shift", effects)
        
        # Advance to summer and test effects
        self.time_system.advance_time(days=DAYS_PER_SEASON)
        self.season_system.update(0)
        
        effects = self.season_system.get_current_effects()
        self.assertEqual(effects["temperature_modifier"], 10.0)  # Summer is hot
        self.assertEqual(effects["precipitation_chance"], 0.2)   # Summer is drier
        
    def test_seasonal_events(self):
        """Test that seasonal events are scheduled correctly."""
        # Spring should have specific events scheduled
        spring_events = [
            event for event in self.season_system.seasonal_events
            if event.type in ["spring_bloom", "bird_migration", "heavy_rain"]
        ]
        self.assertEqual(len(spring_events), 0)  # Events are scheduled after season change
        
        # Change to summer and check its events
        self.time_system.advance_time(days=DAYS_PER_SEASON)
        self.season_system.update(0)
        
        summer_events = [
            event for event in self.season_system.seasonal_events
            if event.type in ["heat_wave", "summer_storm", "drought"]
        ]
        self.assertEqual(len(summer_events), 3)
        
    def test_transition_effects(self):
        """Test seasonal transition effects."""
        # Start of spring
        initial_density = self.season_system._calculate_foliage_density()
        
        # Mid-spring
        self.time_system.advance_time(days=DAYS_PER_SEASON // 2)
        self.season_system.update(0)
        mid_density = self.season_system._calculate_foliage_density()
        
        # Density should increase from start to middle of spring
        self.assertGreater(mid_density, initial_density)
        
        # Test day length changes
        self.season_system.current_season = Season.SUMMER
        summer_day_length = self.season_system._calculate_day_length()
        
        self.season_system.current_season = Season.WINTER
        winter_day_length = self.season_system._calculate_day_length()
        
        # Summer days should be longer than winter days
        self.assertGreater(summer_day_length, winter_day_length)
        
    def test_color_shifts(self):
        """Test seasonal color shift calculations."""
        # Test each season's color profile
        for season in Season:
            self.season_system.current_season = season
            r, g, b = self.season_system._calculate_seasonal_colors()
            
            # All color channels should be reasonable values
            self.assertTrue(0.5 <= r <= 1.5)
            self.assertTrue(0.5 <= g <= 1.5)
            self.assertTrue(0.5 <= b <= 1.5)
            
            if season == Season.SPRING:
                # Spring should be more green
                self.assertGreater(g, r)
                self.assertGreater(g, b)
            elif season == Season.FALL:
                # Fall should be more red
                self.assertGreater(r, g)
                self.assertGreater(r, b)

if __name__ == '__main__':
    unittest.main() 