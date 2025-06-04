"""
Weather System Business Service - Pure Business Logic

Contains the core weather business rules according to Development Bible standards.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import random
from backend.systems.weather.models.weather_model import Weather, WeatherCondition
from backend.systems.weather.repositories.weather_repository import WeatherRepository
from backend.systems.weather.services.weather_validation_service import WeatherValidationService


class WeatherBusinessService:
    """Pure business logic for weather system"""
    
    def __init__(self, 
                 weather_repository: WeatherRepository,
                 validation_service: WeatherValidationService):
        self.weather_repository = weather_repository
        self.validation_service = validation_service
    
    def get_current_weather(self) -> Weather:
        """Get current weather state or initialize default"""
        current = self.weather_repository.load_weather_state()
        
        if current is None:
            # Business rule: Initialize with default weather if none exists
            config = self.validation_service.load_weather_config()
            default_data = config.get("default_weather", {})
            
            current = Weather(
                condition=self.validation_service.validate_weather_condition(
                    default_data.get("condition", "clear")
                ),
                temperature=float(default_data.get("temperature", 65.0)),
                humidity=float(default_data.get("humidity", 50.0)),
                wind_speed=float(default_data.get("wind_speed", 5.0)),
                pressure=float(default_data.get("pressure", 29.92)),
                visibility=float(default_data.get("visibility", 10.0)),
                timestamp=datetime.utcnow(),
                duration_hours=int(default_data.get("duration_hours", 4))
            )
            
            # Save the initial weather
            self.weather_repository.save_weather_state(current)
        
        return current
    
    def advance_weather(self, season: str = "spring", hours_elapsed: int = 1) -> Weather:
        """Advance weather based on time and season (core business logic)"""
        current = self.get_current_weather()
        
        # Business rule: Check if weather should change
        if not self._should_weather_change(current, hours_elapsed):
            return current
        
        # Business rule: Generate new weather based on season and transitions
        new_weather = self._generate_new_weather(current, season)
        
        # Business rule: Apply temporal progression
        new_weather.timestamp = datetime.utcnow()
        
        # Business rule: Save state and add to history
        self.weather_repository.add_to_history(current)
        self.weather_repository.save_weather_state(new_weather)
        
        return new_weather
    
    def force_weather_change(self, 
                           condition: WeatherCondition, 
                           duration_hours: Optional[int] = None,
                           temperature: Optional[float] = None) -> Weather:
        """Force specific weather condition (admin/event use)"""
        current = self.get_current_weather()
        
        # Business rule: Create forced weather with sensible defaults
        forced_weather = Weather(
            condition=condition,
            temperature=temperature or self._calculate_seasonal_temperature(condition, "spring"),
            humidity=self._calculate_humidity_for_condition(condition),
            wind_speed=self._calculate_wind_speed_for_condition(condition),
            pressure=current.pressure,  # Keep current pressure
            visibility=self._calculate_visibility_for_condition(condition),
            timestamp=datetime.utcnow(),
            duration_hours=duration_hours or 2
        )
        
        # Business rule: Save forced weather
        self.weather_repository.add_to_history(current)
        self.weather_repository.save_weather_state(forced_weather)
        
        return forced_weather
    
    def get_weather_forecast(self, hours_ahead: int = 24, season: str = "spring") -> List[Weather]:
        """Generate weather forecast (business prediction logic)"""
        current = self.get_current_weather()
        forecast = []
        
        # Business rule: Forecast based on current conditions and seasonal patterns
        sim_weather = current
        
        for hour in range(1, hours_ahead + 1):
            # Business rule: Probabilistic weather progression
            if hour % 4 == 0 or random.random() < 0.3:  # Change every 4 hours or 30% chance
                sim_weather = self._generate_new_weather(sim_weather, season)
                sim_weather.timestamp = current.timestamp + timedelta(hours=hour)
            
            forecast.append(sim_weather)
        
        return forecast
    
    def get_weather_effects_data(self, weather: Weather) -> Dict[str, Any]:
        """Get visual/audio effects data for frontend (business rule for presentation)"""
        weather_types = self.validation_service.load_weather_types()
        condition_key = weather.condition.value
        
        if condition_key in weather_types:
            effects_data = weather_types[condition_key]
            return {
                "visual_effects": effects_data.get("visual_effects", {}),
                "sound_effects": effects_data.get("sound_effects", {}),
                "temperature_modifier": effects_data.get("temperature_modifier", 0),
                "visibility_modifier": effects_data.get("visibility_modifier", 0),
                "display_name": effects_data.get("display_name", condition_key.replace("_", " ").title()),
                "description": effects_data.get("description", ""),
            }
        
        # Fallback minimal effects data
        return {
            "visual_effects": {},
            "sound_effects": {},
            "temperature_modifier": 0,
            "visibility_modifier": 0,
            "display_name": condition_key.replace("_", " ").title(),
            "description": "",
        }
    
    def _should_weather_change(self, current: Weather, hours_elapsed: int) -> bool:
        """Business rule: Determine if weather should change"""
        # Check if duration has expired
        time_since = datetime.utcnow() - current.timestamp
        if time_since.total_seconds() / 3600 >= current.duration_hours:
            return True
        
        # Random chance for early change
        config = self.validation_service.load_weather_config()
        randomness = config.get("weather_system", {}).get("randomness_factor", 0.5)
        
        return random.random() < (randomness * 0.1 * hours_elapsed)
    
    def _generate_new_weather(self, current: Weather, season: str) -> Weather:
        """Business rule: Generate new weather based on current conditions and season"""
        # Get possible transitions from JSON config
        weather_types = self.validation_service.load_weather_types()
        current_condition_key = current.condition.value
        
        possible_conditions = []
        
        if current_condition_key in weather_types:
            transitions = weather_types[current_condition_key].get("can_transition_to", [])
            for transition in transitions:
                try:
                    condition = WeatherCondition(transition)
                    possible_conditions.append(condition)
                except ValueError:
                    continue
        
        # Fallback: Use seasonal weights if no transitions defined
        if not possible_conditions:
            seasonal_weights = self.validation_service.get_seasonal_weights(season)
            possible_conditions = list(seasonal_weights.keys())
        
        # Business rule: Choose new condition
        if possible_conditions:
            new_condition = random.choice(possible_conditions)
        else:
            new_condition = WeatherCondition.CLEAR
        
        # Business rule: Generate realistic parameters
        return Weather(
            condition=new_condition,
            temperature=self._calculate_seasonal_temperature(new_condition, season),
            humidity=self._calculate_humidity_for_condition(new_condition),
            wind_speed=self._calculate_wind_speed_for_condition(new_condition),
            pressure=self._calculate_pressure_for_condition(new_condition, current.pressure),
            visibility=self._calculate_visibility_for_condition(new_condition),
            timestamp=datetime.utcnow(),
            duration_hours=random.randint(2, 8)
        )
    
    def _calculate_seasonal_temperature(self, condition: WeatherCondition, season: str) -> float:
        """Business rule: Calculate temperature based on season and condition"""
        temp_min, temp_max = self.validation_service.get_temperature_range(season)
        base_temp = random.uniform(temp_min, temp_max)
        
        # Apply condition-specific temperature modifiers
        weather_types = self.validation_service.load_weather_types()
        condition_key = condition.value
        
        if condition_key in weather_types:
            modifier = weather_types[condition_key].get("temperature_modifier", 0)
            base_temp += modifier
        
        return round(base_temp, 1)
    
    def _calculate_humidity_for_condition(self, condition: WeatherCondition) -> float:
        """Business rule: Calculate humidity based on weather condition"""
        humidity_map = {
            WeatherCondition.CLEAR: random.uniform(30, 60),
            WeatherCondition.PARTLY_CLOUDY: random.uniform(40, 70),
            WeatherCondition.CLOUDY: random.uniform(60, 80),
            WeatherCondition.OVERCAST: random.uniform(70, 85),
            WeatherCondition.LIGHT_RAIN: random.uniform(80, 95),
            WeatherCondition.RAIN: random.uniform(85, 98),
            WeatherCondition.HEAVY_RAIN: random.uniform(90, 100),
            WeatherCondition.DRIZZLE: random.uniform(85, 95),
            WeatherCondition.MIST: random.uniform(85, 98),
            WeatherCondition.FOG: random.uniform(90, 100),
            WeatherCondition.LIGHT_SNOW: random.uniform(70, 90),
            WeatherCondition.SNOW: random.uniform(80, 95),
            WeatherCondition.HEAVY_SNOW: random.uniform(85, 100),
            WeatherCondition.BLIZZARD: random.uniform(80, 95),
            WeatherCondition.THUNDERSTORM: random.uniform(85, 100),
            WeatherCondition.WINDY: random.uniform(35, 65),
            WeatherCondition.SCORCHING: random.uniform(20, 40),
            WeatherCondition.HAIL: random.uniform(80, 95),
            WeatherCondition.HURRICANE: random.uniform(85, 100),
            WeatherCondition.SANDSTORM: random.uniform(20, 50),
        }
        
        return round(humidity_map.get(condition, random.uniform(40, 70)), 1)
    
    def _calculate_wind_speed_for_condition(self, condition: WeatherCondition) -> float:
        """Business rule: Calculate wind speed based on weather condition"""
        wind_ranges = {
            WeatherCondition.CLEAR: (0, 10),
            WeatherCondition.PARTLY_CLOUDY: (5, 15),
            WeatherCondition.CLOUDY: (5, 20),
            WeatherCondition.OVERCAST: (5, 15),
            WeatherCondition.LIGHT_RAIN: (5, 15),
            WeatherCondition.RAIN: (10, 25),
            WeatherCondition.HEAVY_RAIN: (15, 35),
            WeatherCondition.DRIZZLE: (0, 10),
            WeatherCondition.MIST: (0, 5),
            WeatherCondition.FOG: (0, 5),
            WeatherCondition.LIGHT_SNOW: (5, 15),
            WeatherCondition.SNOW: (10, 25),
            WeatherCondition.HEAVY_SNOW: (15, 35),
            WeatherCondition.BLIZZARD: (35, 70),
            WeatherCondition.THUNDERSTORM: (20, 50),
            WeatherCondition.WINDY: (25, 45),
            WeatherCondition.SCORCHING: (0, 15),
            WeatherCondition.HAIL: (20, 40),
            WeatherCondition.HURRICANE: (70, 120),
            WeatherCondition.SANDSTORM: (30, 60),
        }
        
        min_wind, max_wind = wind_ranges.get(condition, (5, 15))
        return round(random.uniform(min_wind, max_wind), 1)
    
    def _calculate_pressure_for_condition(self, condition: WeatherCondition, current_pressure: float) -> float:
        """Business rule: Calculate atmospheric pressure based on condition"""
        # Pressure changes are gradual
        pressure_changes = {
            WeatherCondition.CLEAR: random.uniform(-0.02, 0.05),
            WeatherCondition.PARTLY_CLOUDY: random.uniform(-0.02, 0.02),
            WeatherCondition.CLOUDY: random.uniform(-0.05, 0.02),
            WeatherCondition.OVERCAST: random.uniform(-0.08, -0.02),
            WeatherCondition.LIGHT_RAIN: random.uniform(-0.10, -0.03),
            WeatherCondition.RAIN: random.uniform(-0.15, -0.05),
            WeatherCondition.HEAVY_RAIN: random.uniform(-0.20, -0.08),
            WeatherCondition.THUNDERSTORM: random.uniform(-0.25, -0.10),
            WeatherCondition.BLIZZARD: random.uniform(-0.20, -0.05),
            WeatherCondition.HAIL: random.uniform(-0.20, -0.08),
            WeatherCondition.HURRICANE: random.uniform(-0.30, -0.15),
            WeatherCondition.SANDSTORM: random.uniform(-0.05, 0.05),
        }
        
        change = pressure_changes.get(condition, random.uniform(-0.02, 0.02))
        new_pressure = current_pressure + change
        
        # Keep within realistic bounds
        return round(max(28.5, min(31.0, new_pressure)), 2)
    
    def _calculate_visibility_for_condition(self, condition: WeatherCondition) -> float:
        """Business rule: Calculate visibility based on weather condition"""
        visibility_ranges = {
            WeatherCondition.CLEAR: (8, 10),
            WeatherCondition.PARTLY_CLOUDY: (7, 10),
            WeatherCondition.CLOUDY: (6, 9),
            WeatherCondition.OVERCAST: (5, 8),
            WeatherCondition.LIGHT_RAIN: (4, 7),
            WeatherCondition.RAIN: (2, 5),
            WeatherCondition.HEAVY_RAIN: (1, 3),
            WeatherCondition.DRIZZLE: (3, 6),
            WeatherCondition.MIST: (2, 5),
            WeatherCondition.FOG: (0.1, 1),
            WeatherCondition.LIGHT_SNOW: (3, 6),
            WeatherCondition.SNOW: (1, 4),
            WeatherCondition.HEAVY_SNOW: (0.5, 2),
            WeatherCondition.BLIZZARD: (0.1, 0.5),
            WeatherCondition.THUNDERSTORM: (1, 4),
            WeatherCondition.WINDY: (5, 9),
            WeatherCondition.SCORCHING: (4, 8),  # Heat haze can reduce visibility
            WeatherCondition.HAIL: (1, 3),
            WeatherCondition.HURRICANE: (0.5, 2),
            WeatherCondition.SANDSTORM: (0.1, 0.5),
        }
        
        min_vis, max_vis = visibility_ranges.get(condition, (5, 8))
        return round(random.uniform(min_vis, max_vis), 1) 