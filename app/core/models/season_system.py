from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from app.core.enums import Season
from app.core.models.time_system import TimeSystem, TimeEvent
from app.utils.constants import DAYS_PER_SEASON

class SeasonSystem:
    """Manages seasonal changes and their effects on the game world."""
    
    def __init__(self, time_system: TimeSystem):
        self.time_system = time_system
        self.current_season = Season.SPRING
        self.season_start_date = self.time_system.current_time
        self.season_progress = 0.0  # 0.0 to 1.0
        self.transition_effects: Dict[str, float] = {}
        self.seasonal_events: List[TimeEvent] = []
        
        # Schedule the first season change
        self._schedule_next_season_change()
        
    def update(self, delta_time: float) -> None:
        """Update season progress and check for season changes."""
        # Calculate season progress
        days_elapsed = (self.time_system.current_time - self.season_start_date).days
        self.season_progress = min(days_elapsed / DAYS_PER_SEASON, 1.0)
        
        # Update transition effects
        self._update_transition_effects()
        
    def _schedule_next_season_change(self) -> None:
        """Schedule the next season change event."""
        next_change = self.season_start_date + timedelta(days=DAYS_PER_SEASON)
        
        event = TimeEvent(
            id=f"season_change_{self.current_season.name}_{next_change.isoformat()}",
            type="season_change",
            trigger_time=next_change,
            data={"from_season": self.current_season, "to_season": self.current_season.next_season},
            recurring=False
        )
        
        self.time_system.add_event(event)
        self.seasonal_events.append(event)
        
    def _update_transition_effects(self) -> None:
        """Update visual and gameplay effects during season transitions."""
        # Early season transition effects (first 10% of the season)
        early_transition = min(self.season_progress * 10, 1.0)
        
        # Late season transition effects (last 10% of the season)
        late_transition = max(min((self.season_progress - 0.9) * 10, 1.0), 0.0)
        
        self.transition_effects = {
            "foliage_density": self._calculate_foliage_density(),
            "day_length": self._calculate_day_length(),
            "color_shift": self._calculate_seasonal_colors(),
        }
        
    def _calculate_foliage_density(self) -> float:
        """Calculate the current foliage density based on season and progress."""
        base_density = {
            Season.SPRING: 0.7,  # Growing
            Season.SUMMER: 1.0,  # Full
            Season.FALL: 0.5,    # Falling
            Season.WINTER: 0.1   # Minimal
        }[self.current_season]
        
        # Adjust for transition periods
        if self.current_season == Season.FALL and self.season_progress > 0.5:
            base_density *= (1.0 - (self.season_progress - 0.5) * 2)
        elif self.current_season == Season.SPRING:
            base_density *= min(self.season_progress * 2, 1.0)
            
        return base_density
        
    def _calculate_day_length(self) -> float:
        """Calculate the current day length modifier based on season."""
        # Base day length modifiers (1.0 = normal length)
        base_lengths = {
            Season.SUMMER: 1.3,  # Longer days
            Season.WINTER: 0.7,  # Shorter days
            Season.SPRING: 1.0,  # Normal
            Season.FALL: 1.0     # Normal
        }
        
        return base_lengths[self.current_season]
        
    def _calculate_seasonal_colors(self) -> Tuple[float, float, float]:
        """Calculate the color shift for the current season."""
        # RGB color modifiers for each season
        color_shifts = {
            Season.SPRING: (0.9, 1.1, 0.9),  # More green
            Season.SUMMER: (1.0, 1.0, 0.9),  # Slightly yellow
            Season.FALL: (1.2, 0.9, 0.8),    # Orange/red
            Season.WINTER: (0.9, 0.9, 1.1)   # Bluish
        }
        
        return color_shifts[self.current_season]
        
    def change_season(self) -> None:
        """Trigger a season change."""
        old_season = self.current_season
        self.current_season = self.current_season.next_season
        self.season_start_date = self.time_system.current_time
        self.season_progress = 0.0
        
        # Clear old seasonal events
        self.seasonal_events = [
            event for event in self.seasonal_events
            if event.trigger_time > self.time_system.current_time
        ]
        
        # Schedule the next season change
        self._schedule_next_season_change()
        
        # Schedule season-specific events
        self._schedule_seasonal_events()
        
    def _schedule_seasonal_events(self) -> None:
        """Schedule events specific to the current season."""
        events = []
        
        if self.current_season == Season.SPRING:
            # Spring events
            events.extend([
                ("spring_bloom", timedelta(days=5)),
                ("bird_migration", timedelta(days=10)),
                ("heavy_rain", timedelta(days=15))
            ])
        elif self.current_season == Season.SUMMER:
            # Summer events
            events.extend([
                ("heat_wave", timedelta(days=20)),
                ("summer_storm", timedelta(days=30)),
                ("drought", timedelta(days=40))
            ])
        elif self.current_season == Season.FALL:
            # Fall events
            events.extend([
                ("leaves_changing", timedelta(days=10)),
                ("harvest_time", timedelta(days=25)),
                ("first_frost", timedelta(days=45))
            ])
        elif self.current_season == Season.WINTER:
            # Winter events
            events.extend([
                ("first_snow", timedelta(days=5)),
                ("blizzard", timedelta(days=30)),
                ("winter_solstice", timedelta(days=45))
            ])
            
        # Create and schedule the events
        for event_type, delay in events:
            event = TimeEvent(
                id=f"{event_type}_{self.time_system.current_time.isoformat()}",
                type=event_type,
                trigger_time=self.time_system.current_time + delay,
                data={"season": self.current_season},
                recurring=False
            )
            self.time_system.add_event(event)
            self.seasonal_events.append(event)
            
    def get_current_effects(self) -> Dict[str, float]:
        """Get the current seasonal effects including transitions."""
        return {
            "temperature_modifier": self.current_season.temperature_modifier,
            "precipitation_chance": self.current_season.precipitation_chance,
            **self.transition_effects
        } 