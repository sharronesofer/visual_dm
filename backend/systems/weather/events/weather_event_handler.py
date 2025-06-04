"""
Weather System Event Handler

Handles weather-related events according to Development Bible standards.
This replaces the old events.py with proper separation of concerns.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from backend.systems.weather.services.weather_business_service import WeatherBusinessService
from backend.systems.weather.repositories.weather_repository import WeatherRepositoryImpl
from backend.systems.weather.services.weather_validation_service import WeatherValidationServiceImpl
from backend.systems.weather.models.weather_model import Weather


class WeatherEventHandler:
    """Handles weather system events - integrates with game event system"""
    
    def __init__(self, business_service: Optional[WeatherBusinessService] = None):
        if business_service is None:
            # Initialize dependencies
            repository = WeatherRepositoryImpl()
            validation_service = WeatherValidationServiceImpl()
            self.business_service = WeatherBusinessService(repository, validation_service)
        else:
            self.business_service = business_service
    
    def handle_time_advanced(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time advancement event from game system"""
        hours_elapsed = event_data.get("hours_elapsed", 1)
        current_season = event_data.get("season", "spring")
        
        # Advance weather based on time progression
        new_weather = self.business_service.advance_weather(current_season, hours_elapsed)
        
        # Return weather change event data if weather changed
        return self._create_weather_event(new_weather, "time_advanced")
    
    def handle_season_changed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle season change event from game system"""
        new_season = event_data.get("new_season", "spring")
        
        # Force weather evaluation for new season
        current_weather = self.business_service.get_current_weather()
        new_weather = self.business_service.advance_weather(new_season, 0)
        
        return self._create_weather_event(new_weather, "season_changed")
    
    def handle_admin_weather_force(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle admin forcing weather change"""
        condition_str = event_data.get("condition")
        duration_hours = event_data.get("duration_hours")
        temperature = event_data.get("temperature")
        
        if not condition_str:
            raise ValueError("Condition is required for weather force event")
        
        from backend.systems.weather.models.weather_model import WeatherCondition
        try:
            condition = WeatherCondition(condition_str.lower())
        except ValueError:
            raise ValueError(f"Invalid weather condition: {condition_str}")
        
        forced_weather = self.business_service.force_weather_change(
            condition, duration_hours, temperature
        )
        
        return self._create_weather_event(forced_weather, "admin_forced")
    
    def get_current_weather_event(self) -> Dict[str, Any]:
        """Get current weather as event data for initial frontend sync"""
        current_weather = self.business_service.get_current_weather()
        return self._create_weather_event(current_weather, "current_state")
    
    def _create_weather_event(self, weather: Weather, trigger: str) -> Dict[str, Any]:
        """Create standardized weather event data for game event system"""
        effects_data = self.business_service.get_weather_effects_data(weather)
        
        return {
            "event_type": "weather_changed",
            "trigger": trigger,
            "timestamp": datetime.utcnow().isoformat(),
            "weather_data": {
                "condition": weather.condition.value,
                "display_name": effects_data.get("display_name", ""),
                "description": effects_data.get("description", ""),
                "temperature": weather.temperature,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "pressure": weather.pressure,
                "visibility": weather.visibility,
                "duration_hours": weather.duration_hours,
                "weather_timestamp": weather.timestamp.isoformat()
            },
            "effects": {
                "visual_effects": effects_data.get("visual_effects", {}),
                "sound_effects": effects_data.get("sound_effects", {}),
                "temperature_modifier": effects_data.get("temperature_modifier", 0),
                "visibility_modifier": effects_data.get("visibility_modifier", 0)
            }
        }


# Event registration function for integration with game event system
def register_weather_event_handlers(event_system):
    """Register weather event handlers with the game event system"""
    handler = WeatherEventHandler()
    
    # Register for time advancement events
    event_system.register_handler("time_advanced", handler.handle_time_advanced)
    
    # Register for season change events  
    event_system.register_handler("season_changed", handler.handle_season_changed)
    
    # Register for admin weather forcing
    event_system.register_handler("admin_weather_force", handler.handle_admin_weather_force)
    
    return handler


# Factory function for creating event handler
def create_weather_event_handler() -> WeatherEventHandler:
    """Factory function for creating weather event handler"""
    return WeatherEventHandler() 