"""
Weather System API Router

Provides REST API endpoints for weather system following Development Bible standards.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from backend.systems.weather.services.weather_business_service import WeatherBusinessService
from backend.systems.weather.repositories.weather_repository import WeatherRepositoryImpl
from backend.systems.weather.services.weather_validation_service import WeatherValidationServiceImpl
from backend.systems.weather.models.weather_model import Weather, WeatherCondition


# API Models for responses
class WeatherResponse:
    """API response model for weather data"""
    def __init__(self, weather: Weather, effects_data: dict):
        self.condition = weather.condition.value
        self.display_name = effects_data.get("display_name", weather.condition.value.replace("_", " ").title())
        self.description = effects_data.get("description", "")
        self.temperature = weather.temperature
        self.humidity = weather.humidity
        self.wind_speed = weather.wind_speed
        self.pressure = weather.pressure
        self.visibility = weather.visibility
        self.timestamp = weather.timestamp.isoformat()
        self.duration_hours = weather.duration_hours
        self.visual_effects = effects_data.get("visual_effects", {})
        self.sound_effects = effects_data.get("sound_effects", {})


class WeatherForecastResponse:
    """API response model for weather forecast"""
    def __init__(self, forecast: List[Weather], business_service: WeatherBusinessService):
        self.forecast = []
        for weather in forecast:
            effects_data = business_service.get_weather_effects_data(weather)
            self.forecast.append(WeatherResponse(weather, effects_data).__dict__)


# Initialize dependencies (in production, use proper DI container)
def get_weather_business_service() -> WeatherBusinessService:
    """Factory function for weather business service"""
    repository = WeatherRepositoryImpl()
    validation_service = WeatherValidationServiceImpl()
    return WeatherBusinessService(repository, validation_service)


# Create router
weather_router = APIRouter(prefix="/api/weather", tags=["weather"])


@weather_router.get("/current", response_description="Get current weather conditions")
async def get_current_weather():
    """Get current weather with visual/audio effects data for frontend"""
    try:
        business_service = get_weather_business_service()
        current_weather = business_service.get_current_weather()
        effects_data = business_service.get_weather_effects_data(current_weather)
        
        response = WeatherResponse(current_weather, effects_data)
        return response.__dict__
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current weather: {str(e)}")


@weather_router.get("/forecast", response_description="Get weather forecast")
async def get_weather_forecast(
    hours: int = Query(default=24, ge=1, le=168, description="Hours ahead to forecast (max 1 week)"),
    season: str = Query(default="spring", description="Current season")
):
    """Get weather forecast for specified hours ahead"""
    try:
        business_service = get_weather_business_service()
        forecast = business_service.get_weather_forecast(hours, season)
        
        response = WeatherForecastResponse(forecast, business_service)
        return response.__dict__
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather forecast: {str(e)}")


@weather_router.get("/history", response_description="Get weather history")
async def get_weather_history(
    limit: int = Query(default=50, ge=1, le=500, description="Number of historical entries")
):
    """Get weather history"""
    try:
        business_service = get_weather_business_service()
        history = business_service.weather_repository.get_weather_history(limit)
        
        response_data = []
        for weather in history:
            effects_data = business_service.get_weather_effects_data(weather)
            response_data.append(WeatherResponse(weather, effects_data).__dict__)
        
        return {"history": response_data, "count": len(response_data)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather history: {str(e)}")


@weather_router.post("/advance", response_description="Advance weather (admin/game events)")
async def advance_weather(
    season: str = Query(default="spring", description="Current season"),
    hours_elapsed: int = Query(default=1, ge=1, le=24, description="Hours elapsed")
):
    """Advance weather system (for game time progression)"""
    try:
        business_service = get_weather_business_service()
        new_weather = business_service.advance_weather(season, hours_elapsed)
        effects_data = business_service.get_weather_effects_data(new_weather)
        
        response = WeatherResponse(new_weather, effects_data)
        return response.__dict__
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to advance weather: {str(e)}")


@weather_router.post("/force", response_description="Force specific weather (admin only)")
async def force_weather(
    condition: str = Query(description="Weather condition to force"),
    duration_hours: Optional[int] = Query(default=None, description="Duration in hours"),
    temperature: Optional[float] = Query(default=None, description="Specific temperature")
):
    """Force specific weather condition (admin endpoint)"""
    try:
        business_service = get_weather_business_service()
        
        # Validate condition
        try:
            weather_condition = WeatherCondition(condition.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid weather condition: {condition}")
        
        forced_weather = business_service.force_weather_change(
            weather_condition, 
            duration_hours, 
            temperature
        )
        effects_data = business_service.get_weather_effects_data(forced_weather)
        
        response = WeatherResponse(forced_weather, effects_data)
        return response.__dict__
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to force weather: {str(e)}")


@weather_router.get("/conditions", response_description="Get available weather conditions")
async def get_available_conditions():
    """Get list of all available weather conditions"""
    try:
        conditions = []
        for condition in WeatherCondition:
            conditions.append({
                "value": condition.value,
                "display_name": condition.value.replace("_", " ").title()
            })
        
        return {"conditions": conditions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conditions: {str(e)}")


@weather_router.get("/config", response_description="Get weather system configuration")
async def get_weather_config():
    """Get weather system configuration (for frontend debugging)"""
    try:
        business_service = get_weather_business_service()
        config = business_service.validation_service.load_weather_config()
        
        # Don't expose sensitive config details, just basic info
        return {
            "enabled": config.get("weather_system", {}).get("enabled", True),
            "default_condition": config.get("default_weather", {}).get("condition", "clear"),
            "seasonal_support": bool(config.get("seasonal_preferences"))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather config: {str(e)}") 