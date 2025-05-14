#!/usr/bin/env python3
"""
environment.py - Environment Data Contracts for World Generation System

This module defines the standardized data contracts for environmental features,
including weather, hazards, seasons, and time-based effects.

Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
import uuid
from datetime import datetime

from .base import (
    WorldGenContract, 
    WorldGenContractError,
    ValidationError,
    WorldGenContractValidator as Validator,
    QueryResult
)


class WeatherType(Enum):
    """Types of weather"""
    CLEAR = "clear"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    STORM = "storm"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    BLIZZARD = "blizzard"
    FOG = "fog"
    HEAVY_FOG = "heavy_fog"
    WINDY = "windy"
    CLOUDY = "cloudy"
    PARTLY_CLOUDY = "partly_cloudy"
    HAIL = "hail"
    SANDSTORM = "sandstorm"


class HazardType(Enum):
    """Types of environmental hazards"""
    FLOOD = "flood"
    AVALANCHE = "avalanche"
    RADIATION = "radiation"
    FIRE = "fire"
    STORM = "storm"
    LIGHTNING = "lightning"
    POISON_GAS = "poison_gas"
    EXTREME_COLD = "extreme_cold"
    EXTREME_HEAT = "extreme_heat"
    VOLCANIC = "volcanic"
    MAGIC = "magic"


class SeasonType(Enum):
    """Types of seasons"""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    DRY = "dry"  # For tropical regions
    RAINY = "rainy"  # For tropical regions


@dataclass
class WeatherContract(WorldGenContract):
    """Contract for weather data"""
    id: str
    type: WeatherType
    intensity: float  # 0.0 to 1.0
    region_id: str
    duration: float  # Duration in game hours
    start_time: float = 0.0  # Game time when the weather started
    effects: List[Dict[str, Any]] = field(default_factory=list)
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate weather data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "type", "intensity", "region_id", "duration"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for WeatherContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID and region_id
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        if not Validator.validate_string(data.get("region_id", ""), min_length=1):
            errors["region_id"] = "region_id must be a non-empty string"
        
        # Validate type
        weather_type = data.get("type")
        if isinstance(weather_type, WeatherType):
            weather_type = weather_type.value
            
        if not isinstance(weather_type, str) or not any(weather_type == t.value for t in WeatherType):
            errors["type"] = f"type must be one of: {', '.join(t.value for t in WeatherType)}"
        
        # Validate numeric fields
        if not Validator.validate_number(data.get("intensity", 0), min_value=0, max_value=1):
            errors["intensity"] = "intensity must be a number between 0 and 1"
        
        if not Validator.validate_number(data.get("duration", 0), min_value=0):
            errors["duration"] = "duration must be a non-negative number"
        
        if "start_time" in data and not Validator.validate_number(data["start_time"], min_value=0):
            errors["start_time"] = "start_time must be a non-negative number"
        
        # Validate effects
        if "effects" in data:
            effects = data.get("effects", [])
            if not isinstance(effects, list):
                errors["effects"] = "effects must be a list of dictionaries"
            else:
                for i, effect in enumerate(effects):
                    if not isinstance(effect, dict):
                        if "effects" not in errors or not isinstance(errors["effects"], list):
                            errors["effects"] = []
                        errors["effects"].append(f"Effect at index {i} must be a dictionary")
        
        if errors:
            raise ValidationError("WeatherContract validation failed", errors)
        
        # Populate fields
        self.id = data["id"]
        
        # Handle enum conversion
        if isinstance(data["type"], str):
            self.type = WeatherType(data["type"])
        else:
            self.type = data["type"]
            
        self.intensity = data["intensity"]
        self.region_id = data["region_id"]
        self.duration = data["duration"]
        self.start_time = data.get("start_time", 0.0)
        self.effects = data.get("effects", [])
    
    @property
    def end_time(self) -> float:
        """Calculate the end time of the weather event"""
        return self.start_time + self.duration
    
    @property
    def is_precipitation(self) -> bool:
        """Check if this weather type involves precipitation"""
        return self.type in [
            WeatherType.RAIN, WeatherType.HEAVY_RAIN, 
            WeatherType.STORM, WeatherType.THUNDERSTORM,
            WeatherType.SNOW, WeatherType.BLIZZARD,
            WeatherType.HAIL
        ]
    
    @property
    def visibility_modifier(self) -> float:
        """Calculate the visibility modifier (0.0-1.0, lower means worse visibility)"""
        if self.type == WeatherType.CLEAR:
            return 1.0
        elif self.type in [WeatherType.PARTLY_CLOUDY, WeatherType.CLOUDY, WeatherType.WINDY]:
            return 0.9
        elif self.type == WeatherType.RAIN:
            return 0.7 - (self.intensity * 0.3)
        elif self.type in [WeatherType.HEAVY_RAIN, WeatherType.STORM, WeatherType.THUNDERSTORM]:
            return 0.4 - (self.intensity * 0.2)
        elif self.type == WeatherType.SNOW:
            return 0.6 - (self.intensity * 0.3)
        elif self.type == WeatherType.BLIZZARD:
            return 0.3 - (self.intensity * 0.2)
        elif self.type == WeatherType.FOG:
            return 0.5 - (self.intensity * 0.3)
        elif self.type == WeatherType.HEAVY_FOG:
            return 0.2 - (self.intensity * 0.1)
        elif self.type in [WeatherType.SANDSTORM, WeatherType.HAIL]:
            return 0.3 - (self.intensity * 0.2)
        else:
            return 0.8  # Default


@dataclass
class HazardContract(WorldGenContract):
    """Contract for environmental hazard data"""
    id: str
    type: HazardType
    region_id: str
    x: int
    y: int
    radius: float  # Area of effect radius
    severity: float  # 0.0 to 1.0
    active: bool = True
    start_time: float = 0.0  # Game time when the hazard started
    duration: Optional[float] = None  # Duration in game hours, None for permanent
    effects: List[Dict[str, Any]] = field(default_factory=list)
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate hazard data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "type", "region_id", "x", "y", "radius", "severity"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for HazardContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID and region_id
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        if not Validator.validate_string(data.get("region_id", ""), min_length=1):
            errors["region_id"] = "region_id must be a non-empty string"
        
        # Validate type
        hazard_type = data.get("type")
        if isinstance(hazard_type, HazardType):
            hazard_type = hazard_type.value
            
        if not isinstance(hazard_type, str) or not any(hazard_type == t.value for t in HazardType):
            errors["type"] = f"type must be one of: {', '.join(t.value for t in HazardType)}"
        
        # Validate coordinates
        if not Validator.validate_number(data.get("x", 0), integer_only=True):
            errors["x"] = "x must be an integer"
        
        if not Validator.validate_number(data.get("y", 0), integer_only=True):
            errors["y"] = "y must be an integer"
        
        # Validate numeric fields
        if not Validator.validate_number(data.get("radius", 0), min_value=0):
            errors["radius"] = "radius must be a non-negative number"
        
        if not Validator.validate_number(data.get("severity", 0), min_value=0, max_value=1):
            errors["severity"] = "severity must be a number between 0 and 1"
        
        if "start_time" in data and not Validator.validate_number(data["start_time"], min_value=0):
            errors["start_time"] = "start_time must be a non-negative number"
        
        if "duration" in data and data["duration"] is not None and not Validator.validate_number(data["duration"], min_value=0):
            errors["duration"] = "duration must be a non-negative number or None"
        
        # Validate active
        if "active" in data and not isinstance(data["active"], bool):
            errors["active"] = "active must be a boolean"
        
        # Validate effects
        if "effects" in data:
            effects = data.get("effects", [])
            if not isinstance(effects, list):
                errors["effects"] = "effects must be a list of dictionaries"
            else:
                for i, effect in enumerate(effects):
                    if not isinstance(effect, dict):
                        if "effects" not in errors or not isinstance(errors["effects"], list):
                            errors["effects"] = []
                        errors["effects"].append(f"Effect at index {i} must be a dictionary")
        
        if errors:
            raise ValidationError("HazardContract validation failed", errors)
        
        # Populate fields
        self.id = data["id"]
        
        # Handle enum conversion
        if isinstance(data["type"], str):
            self.type = HazardType(data["type"])
        else:
            self.type = data["type"]
            
        self.region_id = data["region_id"]
        self.x = data["x"]
        self.y = data["y"]
        self.radius = data["radius"]
        self.severity = data["severity"]
        self.active = data.get("active", True)
        self.start_time = data.get("start_time", 0.0)
        self.duration = data.get("duration", None)
        self.effects = data.get("effects", [])
    
    @property
    def coordinates(self) -> Tuple[int, int]:
        """Get the hazard coordinates as a tuple"""
        return (self.x, self.y)
    
    @property
    def end_time(self) -> Optional[float]:
        """Calculate the end time of the hazard"""
        if self.duration is None:
            return None
        return self.start_time + self.duration
    
    @property
    def is_temporary(self) -> bool:
        """Check if the hazard is temporary (has a duration)"""
        return self.duration is not None
    
    def is_point_affected(self, x: int, y: int) -> bool:
        """Check if a point is within the hazard's radius"""
        import math
        distance = math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
        return distance <= self.radius


@dataclass
class SeasonContract(WorldGenContract):
    """Contract for season data"""
    id: str
    type: SeasonType
    region_id: str
    start_time: float
    duration: float  # Duration in game hours
    temperature_modifier: float = 0.0  # Modifier to base temperature
    moisture_modifier: float = 0.0  # Modifier to base moisture
    growth_modifier: float = 1.0  # Modifier to plant growth rate
    effects: List[Dict[str, Any]] = field(default_factory=list)
    
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """Validate season data"""
        # Check required fields
        missing = Validator.validate_required_fields(
            data, ["id", "type", "region_id", "start_time", "duration"]
        )
        
        if missing["missing"]:
            raise ValidationError(
                f"Missing required fields for SeasonContract: {', '.join(missing['missing'])}",
                {"missing_fields": missing["missing"]}
            )
        
        # Validate field types and constraints
        errors = {}
        
        # Validate ID and region_id
        if not Validator.validate_string(data.get("id", ""), min_length=1):
            errors["id"] = "id must be a non-empty string"
        
        if not Validator.validate_string(data.get("region_id", ""), min_length=1):
            errors["region_id"] = "region_id must be a non-empty string"
        
        # Validate type
        season_type = data.get("type")
        if isinstance(season_type, SeasonType):
            season_type = season_type.value
            
        if not isinstance(season_type, str) or not any(season_type == t.value for t in SeasonType):
            errors["type"] = f"type must be one of: {', '.join(t.value for t in SeasonType)}"
        
        # Validate numeric fields
        if not Validator.validate_number(data.get("start_time", 0), min_value=0):
            errors["start_time"] = "start_time must be a non-negative number"
        
        if not Validator.validate_number(data.get("duration", 0), min_value=0):
            errors["duration"] = "duration must be a non-negative number"
        
        if "temperature_modifier" in data and not Validator.validate_number(data["temperature_modifier"]):
            errors["temperature_modifier"] = "temperature_modifier must be a number"
        
        if "moisture_modifier" in data and not Validator.validate_number(data["moisture_modifier"]):
            errors["moisture_modifier"] = "moisture_modifier must be a number"
        
        if "growth_modifier" in data and not Validator.validate_number(data["growth_modifier"], min_value=0):
            errors["growth_modifier"] = "growth_modifier must be a non-negative number"
        
        # Validate effects
        if "effects" in data:
            effects = data.get("effects", [])
            if not isinstance(effects, list):
                errors["effects"] = "effects must be a list of dictionaries"
            else:
                for i, effect in enumerate(effects):
                    if not isinstance(effect, dict):
                        if "effects" not in errors or not isinstance(errors["effects"], list):
                            errors["effects"] = []
                        errors["effects"].append(f"Effect at index {i} must be a dictionary")
        
        if errors:
            raise ValidationError("SeasonContract validation failed", errors)
        
        # Populate fields
        self.id = data["id"]
        
        # Handle enum conversion
        if isinstance(data["type"], str):
            self.type = SeasonType(data["type"])
        else:
            self.type = data["type"]
            
        self.region_id = data["region_id"]
        self.start_time = data["start_time"]
        self.duration = data["duration"]
        self.temperature_modifier = data.get("temperature_modifier", 0.0)
        self.moisture_modifier = data.get("moisture_modifier", 0.0)
        self.growth_modifier = data.get("growth_modifier", 1.0)
        self.effects = data.get("effects", [])
    
    @property
    def end_time(self) -> float:
        """Calculate the end time of the season"""
        return self.start_time + self.duration
    
    def is_growing_season(self) -> bool:
        """Check if this is a growing season"""
        return (self.type in [SeasonType.SPRING, SeasonType.SUMMER, SeasonType.RAINY] or 
                self.growth_modifier > 1.0) 