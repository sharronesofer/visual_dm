from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
from app.core.enums import WeatherType, WeatherIntensity, Season
from app.core.models.time_system import TimeSystem, TimeEvent
from app.core.models.season_system import SeasonSystem
from app.utils.constants import (
    WEATHER_CHANGE_THRESHOLD,
    MIN_WEATHER_DURATION,
    MAX_WEATHER_DURATION,
    BASE_TEMPERATURE,
    BASE_HUMIDITY,
    BASE_WIND_SPEED,
    BASE_VISIBILITY
)

class WeatherSystem:
    """Manages weather conditions and transitions in the game world."""
    
    def __init__(self, time_system: TimeSystem, season_system: SeasonSystem):
        self.time_system = time_system
        self.season_system = season_system
        
        # Current weather state
        self.current_weather = WeatherType.CLEAR
        self.weather_intensity = WeatherIntensity.MODERATE
        self.weather_start_time = self.time_system.current_time
        self.weather_duration = timedelta(seconds=MIN_WEATHER_DURATION)
        
        # Environmental conditions
        self.temperature = BASE_TEMPERATURE
        self.humidity = BASE_HUMIDITY
        self.wind_speed = BASE_WIND_SPEED
        self.visibility = BASE_VISIBILITY
        
        # Weather history for pattern generation
        self.weather_history: List[Tuple[WeatherType, datetime]] = []
        
        # Schedule initial weather change
        self._schedule_next_weather_change()
        
    def update(self, delta_time: float) -> None:
        """Update weather conditions based on time progression."""
        # Update environmental conditions
        self._update_environmental_conditions()
        
        # Check for weather transitions
        if self._should_change_weather():
            self._transition_weather()
            
    def _update_environmental_conditions(self) -> None:
        """Update temperature, humidity, wind speed, and visibility."""
        # Get current season effects
        season_effects = self.season_system.get_current_effects()
        
        # Base temperature affected by season
        self.temperature = (
            BASE_TEMPERATURE +
            season_effects["temperature_modifier"] +
            random.uniform(-2, 2)  # Small random fluctuation
        )
        
        # Modify conditions based on current weather
        weather_effects = self._calculate_weather_effects()
        self.temperature += weather_effects["temperature_modifier"]
        self.humidity = min(1.0, max(0.0, BASE_HUMIDITY + weather_effects["humidity_modifier"]))
        self.wind_speed = max(0, BASE_WIND_SPEED + weather_effects["wind_modifier"])
        self.visibility = max(0, BASE_VISIBILITY * self.current_weather.visibility_modifier)
        
    def _calculate_weather_effects(self) -> Dict[str, float]:
        """Calculate environmental modifiers based on current weather."""
        intensity_mult = self.weather_intensity.effect_multiplier
        
        effects = {
            WeatherType.CLEAR: {
                "temperature_modifier": 2.0,
                "humidity_modifier": -0.1,
                "wind_modifier": 0
            },
            WeatherType.CLOUDY: {
                "temperature_modifier": 0,
                "humidity_modifier": 0,
                "wind_modifier": 2
            },
            WeatherType.OVERCAST: {
                "temperature_modifier": -1.0,
                "humidity_modifier": 0.1,
                "wind_modifier": 3
            },
            WeatherType.RAIN: {
                "temperature_modifier": -2.0,
                "humidity_modifier": 0.3,
                "wind_modifier": 5
            },
            WeatherType.HEAVY_RAIN: {
                "temperature_modifier": -3.0,
                "humidity_modifier": 0.4,
                "wind_modifier": 8
            },
            WeatherType.THUNDERSTORM: {
                "temperature_modifier": -4.0,
                "humidity_modifier": 0.5,
                "wind_modifier": 15
            },
            WeatherType.SNOW: {
                "temperature_modifier": -8.0,
                "humidity_modifier": 0.2,
                "wind_modifier": 4
            },
            WeatherType.BLIZZARD: {
                "temperature_modifier": -15.0,
                "humidity_modifier": 0.3,
                "wind_modifier": 20
            },
            WeatherType.FOG: {
                "temperature_modifier": -1.0,
                "humidity_modifier": 0.5,
                "wind_modifier": -2
            },
            WeatherType.HAIL: {
                "temperature_modifier": -5.0,
                "humidity_modifier": 0.2,
                "wind_modifier": 10
            }
        }
        
        base_effects = effects[self.current_weather]
        return {
            key: value * intensity_mult
            for key, value in base_effects.items()
        }
        
    def _should_change_weather(self) -> bool:
        """Determine if weather should change based on time and conditions."""
        time_elapsed = self.time_system.current_time - self.weather_start_time
        return time_elapsed >= self.weather_duration
        
    def _get_possible_weather_types(self) -> List[WeatherType]:
        """Get list of possible weather types based on season and current conditions."""
        season = self.season_system.current_season
        current_temp = self.temperature
        
        possible_types = []
        
        # Always possible
        possible_types.extend([
            WeatherType.CLEAR,
            WeatherType.CLOUDY,
            WeatherType.OVERCAST
        ])
        
        # Temperature-based conditions
        if current_temp > 0:
            possible_types.extend([
                WeatherType.RAIN,
                WeatherType.HEAVY_RAIN,
                WeatherType.THUNDERSTORM
            ])
        
        if current_temp <= 0:
            possible_types.extend([
                WeatherType.SNOW,
                WeatherType.BLIZZARD
            ])
            
        # Season-specific conditions
        if season == Season.WINTER:
            possible_types.extend([
                WeatherType.SNOW,
                WeatherType.BLIZZARD
            ])
        elif season == Season.SUMMER:
            possible_types.extend([
                WeatherType.THUNDERSTORM,
                WeatherType.HAIL
            ])
            
        # Time-based conditions (fog more likely at dawn/dusk)
        time_of_day = self.time_system.get_time_of_day()
        if time_of_day in ["DAWN", "DUSK"]:
            possible_types.append(WeatherType.FOG)
            
        return list(set(possible_types))  # Remove duplicates
        
    def _transition_weather(self) -> None:
        """Change to a new weather condition."""
        # Record current weather in history
        self.weather_history.append((self.current_weather, self.time_system.current_time))
        if len(self.weather_history) > 10:  # Keep last 10 weather changes
            self.weather_history.pop(0)
            
        # Select new weather type
        possible_types = self._get_possible_weather_types()
        weights = self._calculate_weather_weights(possible_types)
        self.current_weather = random.choices(possible_types, weights=weights)[0]
        
        # Select new intensity
        self.weather_intensity = self._select_weather_intensity()
        
        # Set new duration
        self.weather_duration = timedelta(
            seconds=random.uniform(MIN_WEATHER_DURATION, MAX_WEATHER_DURATION)
        )
        self.weather_start_time = self.time_system.current_time
        
        # Schedule next change
        self._schedule_next_weather_change()
        
    def _calculate_weather_weights(self, possible_types: List[WeatherType]) -> List[float]:
        """Calculate probability weights for possible weather types."""
        weights = []
        for weather_type in possible_types:
            weight = 1.0  # Base weight
            
            # Favor current weather type slightly for stability
            if weather_type == self.current_weather:
                weight *= 1.2
                
            # Consider season's precipitation chance
            if weather_type in [WeatherType.RAIN, WeatherType.HEAVY_RAIN, WeatherType.SNOW]:
                weight *= self.season_system.current_season.precipitation_chance
                
            # Reduce extreme weather probability
            if weather_type in [WeatherType.BLIZZARD, WeatherType.THUNDERSTORM]:
                weight *= 0.5
                
            weights.append(weight)
            
        return weights
        
    def _select_weather_intensity(self) -> WeatherIntensity:
        """Select weather intensity based on current conditions."""
        intensities = list(WeatherIntensity)
        weights = [0.3, 0.4, 0.2, 0.1]  # Moderate weather more common
        
        # Adjust weights based on current weather type
        if self.current_weather in [WeatherType.BLIZZARD, WeatherType.THUNDERSTORM]:
            weights = [0.1, 0.2, 0.4, 0.3]  # Severe weather more likely
            
        return random.choices(intensities, weights=weights)[0]
        
    def _schedule_next_weather_change(self) -> None:
        """Schedule the next weather change event."""
        next_change = self.time_system.current_time + self.weather_duration
        
        event = TimeEvent(
            id=f"weather_change_{self.current_weather.name}_{next_change.isoformat()}",
            type="weather_change",
            trigger_time=next_change,
            data={
                "from_weather": self.current_weather,
                "intensity": self.weather_intensity,
                "duration": self.weather_duration.total_seconds()
            }
        )
        
        self.time_system.add_event(event)
        
    def get_current_conditions(self) -> Dict:
        """Get current weather conditions and effects."""
        return {
            "weather_type": self.current_weather,
            "intensity": self.weather_intensity,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "visibility": self.visibility,
            "movement_modifier": self.current_weather.movement_speed_modifier,
            "combat_modifier": self.current_weather.combat_modifier
        } 