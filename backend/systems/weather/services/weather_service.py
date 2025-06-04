"""
Weather System Service - Legacy API Facade

Facade service that adapts the new business service to existing API expectations
for backward compatibility. Following Development Bible facade pattern.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from backend.systems.weather.models.weather_model import Weather, WeatherCondition
from backend.systems.weather.services.weather_business_service import WeatherBusinessService
from backend.systems.weather.repositories.weather_repository import WeatherRepositoryImpl
from backend.systems.weather.services.weather_validation_service import WeatherValidationServiceImpl


class WeatherService:
    """
    Legacy facade service for weather operations - adapts business service to existing API expectations.
    This maintains backward compatibility while internally using the proper business service.
    """
    
    def __init__(self):
        """Initialize with business service dependencies"""
        # Initialize business service with proper dependencies
        self.repository = WeatherRepositoryImpl()
        self.validation_service = WeatherValidationServiceImpl()
        self.business_service = WeatherBusinessService(self.repository, self.validation_service)
    
    # Legacy API methods - maintained for compatibility
    
    def get_current_weather(self) -> Dict[str, Any]:
        """Get current weather (legacy format)"""
        weather = self.business_service.get_current_weather()
        return self._weather_to_legacy_dict(weather)
    
    def advance_weather(self, season: str = "spring", hours: int = 1) -> Dict[str, Any]:
        """Advance weather system (legacy format)"""
        weather = self.business_service.advance_weather(season, hours)
        return self._weather_to_legacy_dict(weather)
    
    def force_weather_change(self, condition: str, duration_hours: Optional[int] = None) -> Dict[str, Any]:
        """Force weather change (legacy format)"""
        try:
            weather_condition = WeatherCondition(condition.lower())
        except ValueError:
            raise ValueError(f"Invalid weather condition: {condition}")
        
        weather = self.business_service.force_weather_change(weather_condition, duration_hours)
        return self._weather_to_legacy_dict(weather)
    
    def get_weather_forecast(self, hours: int = 24, season: str = "spring") -> List[Dict[str, Any]]:
        """Get weather forecast (legacy format)"""
        forecast = self.business_service.get_weather_forecast(hours, season)
        return [self._weather_to_legacy_dict(w) for w in forecast]
    
    def get_weather_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get weather history (legacy format)"""
        history = self.repository.get_weather_history(limit)
        return [self._weather_to_legacy_dict(w) for w in history]
    
    # Event system integration methods
    
    def handle_time_advance_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle time advance event from game system"""
        from backend.systems.weather.events.weather_event_handler import WeatherEventHandler
        handler = WeatherEventHandler(self.business_service)
        return handler.handle_time_advanced(event_data)
    
    def handle_season_change_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle season change event from game system"""
        from backend.systems.weather.events.weather_event_handler import WeatherEventHandler
        handler = WeatherEventHandler(self.business_service)
        return handler.handle_season_changed(event_data)
    
    def get_current_weather_event_data(self) -> Dict[str, Any]:
        """Get current weather as event data for WebSocket/frontend"""
        from backend.systems.weather.events.weather_event_handler import WeatherEventHandler
        handler = WeatherEventHandler(self.business_service)
        return handler.get_current_weather_event()
    
    # Configuration and validation methods
    
    def load_config(self) -> Dict[str, Any]:
        """Load weather configuration"""
        return self.validation_service.load_weather_config()
    
    def load_weather_types(self) -> Dict[str, Any]:
        """Load weather types configuration"""
        return self.validation_service.load_weather_types()
    
    def get_available_conditions(self) -> List[str]:
        """Get list of available weather conditions"""
        return [condition.value for condition in WeatherCondition]
    
    def validate_condition(self, condition: str) -> bool:
        """Validate weather condition string"""
        try:
            WeatherCondition(condition.lower())
            return True
        except ValueError:
            return False
    
    # Helper methods
    
    def _weather_to_legacy_dict(self, weather: Weather) -> Dict[str, Any]:
        """Convert Weather object to legacy dictionary format"""
        effects_data = self.business_service.get_weather_effects_data(weather)
        
        return {
            "condition": weather.condition.value,
            "display_name": effects_data.get("display_name", weather.condition.value.replace("_", " ").title()),
            "description": effects_data.get("description", ""),
            "temperature": weather.temperature,
            "humidity": weather.humidity,
            "wind_speed": weather.wind_speed,
            "pressure": weather.pressure,
            "visibility": weather.visibility,
            "timestamp": weather.timestamp.isoformat(),
            "duration_hours": weather.duration_hours,
            # Include visual/audio effects for frontend
            "visual_effects": effects_data.get("visual_effects", {}),
            "sound_effects": effects_data.get("sound_effects", {}),
            "temperature_modifier": effects_data.get("temperature_modifier", 0),
            "visibility_modifier": effects_data.get("visibility_modifier", 0)
        }
    
    def _legacy_dict_to_weather(self, data: Dict[str, Any]) -> Weather:
        """Convert legacy dictionary format to Weather object"""
        return Weather(
            condition=WeatherCondition(data["condition"]),
            temperature=data["temperature"],
            humidity=data["humidity"],
            wind_speed=data["wind_speed"],
            pressure=data["pressure"],
            visibility=data["visibility"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            duration_hours=data["duration_hours"]
        )
    
    def initialize_event_subscriptions(self, event_dispatcher) -> None:
        """Initialize event subscriptions to time system events"""
        # Subscribe to time advancement events
        event_dispatcher.subscribe("time_advanced", self._handle_time_advanced_wrapper)
        
        # Subscribe to season change events
        event_dispatcher.subscribe("season_changed", self._handle_season_changed_wrapper)
        
    def _handle_time_advanced_wrapper(self, event) -> None:
        """Wrapper to handle time advanced events from event dispatcher"""
        try:
            event_data = {
                "hours_elapsed": getattr(event, 'hours_elapsed', 1),
                "season": getattr(event, 'season', 'spring')
            }
            weather_event = self.handle_time_advance_event(event_data)
            
            # Emit weather event if weather changed
            if weather_event.get("event_type") == "weather_changed":
                # Re-emit the weather change event for other systems
                from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
                dispatcher = EventDispatcher.get_instance()
                if dispatcher:
                    dispatcher.publish_sync_data("weather_changed", weather_event)
                    
        except Exception as e:
            # Log error but don't crash
            print(f"Error handling time advanced event: {e}")
    
    def _handle_season_changed_wrapper(self, event) -> None:
        """Wrapper to handle season changed events from event dispatcher"""
        try:
            event_data = {
                "new_season": getattr(event, 'new_season', 'spring')
            }
            weather_event = self.handle_season_change_event(event_data)
            
            # Emit weather event if weather changed
            if weather_event.get("event_type") == "weather_changed":
                # Re-emit the weather change event for other systems
                from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
                dispatcher = EventDispatcher.get_instance()
                if dispatcher:
                    dispatcher.publish_sync_data("weather_changed", weather_event)
                    
        except Exception as e:
            # Log error but don't crash
            print(f"Error handling season changed event: {e}")


# Factory function for creating weather service
def create_weather_service() -> WeatherService:
    """Factory function for creating weather service"""
    service = WeatherService()
    
    # Initialize event subscriptions with the global event dispatcher
    try:
        from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
        dispatcher = EventDispatcher.get_instance()
        if dispatcher:
            service.initialize_event_subscriptions(dispatcher)
    except Exception as e:
        print(f"Warning: Could not initialize weather event subscriptions: {e}")
    
    return service


# Legacy singleton instance for backward compatibility
weather_service = create_weather_service() 