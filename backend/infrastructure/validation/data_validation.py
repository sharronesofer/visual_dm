"""
Data Validation Framework

This module provides comprehensive validation for Visual DM data system,
including input validation, data integrity checking, and constraint enforcement.
"""

from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
from uuid import UUID
import re
import jsonschema
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from decimal import Decimal

from backend.infrastructure.shared.models import SharedBaseModel
from backend.infrastructure.database import get_db


class ValidationError(Exception):
    """Custom exception for validation errors"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)


class ValidationResult(BaseModel):
    """Result of validation operation"""
    
    is_valid: bool = True
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_error(self, field: str, message: str, value: Any = None):
        """Add validation error"""
        self.is_valid = False
        self.errors.append({
            "field": field,
            "message": message,
            "value": value
        })
    
    def add_warning(self, field: str, message: str, value: Any = None):
        """Add validation warning"""
        self.warnings.append({
            "field": field,
            "message": message,
            "value": value
        })


class BaseValidator:
    """Base validator class"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def validate(self, data: Any) -> ValidationResult:
        """Override in subclasses"""
        raise NotImplementedError


class FieldValidator:
    """Individual field validation rules"""
    
    @staticmethod
    def validate_uuid(value: Union[str, UUID]) -> bool:
        """Validate UUID format"""
        try:
            if isinstance(value, str):
                UUID(value)
            elif not isinstance(value, UUID):
                return False
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_coordinates(value: Dict[str, Any]) -> bool:
        """Validate coordinate data structure"""
        if not isinstance(value, dict):
            return False
        
        # Check for required coordinate fields
        required_fields = {'x', 'y'}
        if not required_fields.issubset(value.keys()):
            return False
        
        # Validate coordinate values are numeric
        for coord in ['x', 'y', 'z']:
            if coord in value:
                if not isinstance(value[coord], (int, float)):
                    return False
        
        return True
    
    @staticmethod
    def validate_hex_coordinates(value: Dict[str, Any]) -> bool:
        """Validate hexagonal cube coordinates"""
        if not isinstance(value, dict):
            return False
        
        required_fields = {'q', 'r', 's'}
        if not required_fields.issubset(value.keys()):
            return False
        
        # Validate cube coordinate constraint: q + r + s = 0
        try:
            q, r, s = value['q'], value['r'], value['s']
            if not isinstance(q, int) or not isinstance(r, int) or not isinstance(s, int):
                return False
            if q + r + s != 0:
                return False
        except (KeyError, TypeError):
            return False
        
        return True
    
    @staticmethod
    def validate_game_date(value: Dict[str, Any]) -> bool:
        """Validate game world date format"""
        if not isinstance(value, dict):
            return False
        
        required_fields = {'year', 'month', 'day'}
        if not required_fields.issubset(value.keys()):
            return False
        
        try:
            year = int(value['year'])
            month = int(value['month'])
            day = int(value['day'])
            
            if not (1 <= month <= 12):
                return False
            if not (1 <= day <= 31):  # Simplified day validation
                return False
            if year < 0:
                return False
                
        except (ValueError, TypeError):
            return False
        
        return True
    
    @staticmethod
    def validate_currency_amount(value: Union[Dict[str, Any], Decimal, float]) -> bool:
        """Validate currency amounts"""
        if isinstance(value, (Decimal, float, int)):
            return value >= 0
        
        if isinstance(value, dict):
            # Validate multi-currency format
            for currency, amount in value.items():
                if not isinstance(currency, str) or len(currency) == 0:
                    return False
                if not isinstance(amount, (Decimal, float, int)) or amount < 0:
                    return False
            return True
        
        return False
    
    @staticmethod
    def validate_rating(value: int, min_rating: int = 1, max_rating: int = 10) -> bool:
        """Validate rating values within range"""
        return isinstance(value, int) and min_rating <= value <= max_rating
    
    @staticmethod
    def validate_percentage(value: float, min_val: float = 0.0, max_val: float = 1.0) -> bool:
        """Validate percentage values"""
        return isinstance(value, (float, int)) and min_val <= value <= max_val


class CharacterValidator(BaseValidator):
    """Validator for character entities"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        
        # Required fields validation
        required_fields = ['name', 'character_type']
        for field in required_fields:
            if field not in data or not data[field]:
                result.add_error(field, f"Required field '{field}' is missing or empty")
        
        # Name validation
        if 'name' in data:
            name = data['name']
            if not isinstance(name, str) or len(name.strip()) == 0:
                result.add_error('name', "Name must be a non-empty string")
            elif len(name) > 255:
                result.add_error('name', "Name must be 255 characters or less")
        
        # Character type validation
        valid_types = ['pc', 'npc', 'monster']
        if 'character_type' in data:
            if data['character_type'] not in valid_types:
                result.add_error('character_type', f"Character type must be one of: {valid_types}")
        
        # Ability scores validation
        if 'ability_scores' in data and data['ability_scores']:
            ability_scores = data['ability_scores']
            if not isinstance(ability_scores, dict):
                result.add_error('ability_scores', "Ability scores must be a dictionary")
            else:
                valid_abilities = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
                for ability, score in ability_scores.items():
                    if ability not in valid_abilities:
                        result.add_warning('ability_scores', f"Unknown ability score: {ability}")
                    if not isinstance(score, int) or not (1 <= score <= 30):
                        result.add_error('ability_scores', f"Ability score {ability} must be between 1 and 30")
        
        # Level validation
        if 'level' in data:
            level = data['level']
            if not isinstance(level, int) or level < 1 or level > 20:
                result.add_error('level', "Level must be an integer between 1 and 20")
        
        # Hit points validation
        if 'hit_points_current' in data and 'hit_points_maximum' in data:
            hp_current = data['hit_points_current']
            hp_max = data['hit_points_maximum']
            if isinstance(hp_current, int) and isinstance(hp_max, int):
                if hp_current > hp_max:
                    result.add_error('hit_points_current', "Current HP cannot exceed maximum HP")
                if hp_max < 1:
                    result.add_error('hit_points_maximum', "Maximum HP must be at least 1")
        
        # Location validation
        if 'current_location' in data and data['current_location']:
            if not FieldValidator.validate_uuid(data['current_location']):
                result.add_error('current_location', "Current location must be a valid UUID")
        
        # Faction memberships validation
        if 'faction_memberships' in data and data['faction_memberships']:
            memberships = data['faction_memberships']
            if not isinstance(memberships, list):
                result.add_error('faction_memberships', "Faction memberships must be a list")
            else:
                for membership in memberships:
                    if not isinstance(membership, dict):
                        result.add_error('faction_memberships', "Each membership must be a dictionary")
                    elif 'faction_id' not in membership:
                        result.add_error('faction_memberships', "Each membership must have a faction_id")
                    elif not FieldValidator.validate_uuid(membership['faction_id']):
                        result.add_error('faction_memberships', "Faction ID must be a valid UUID")
        
        return result


class RegionValidator(BaseValidator):
    """Validator for region entities"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        
        # Required fields
        if 'name' not in data or not data['name']:
            result.add_error('name', "Region name is required")
        
        # Name validation
        if 'name' in data:
            name = data['name']
            if not isinstance(name, str) or len(name.strip()) == 0:
                result.add_error('name', "Name must be a non-empty string")
            elif len(name) > 255:
                result.add_error('name', "Name must be 255 characters or less")
        
        # Coordinates validation
        if 'coordinates' in data and data['coordinates']:
            if not FieldValidator.validate_coordinates(data['coordinates']):
                result.add_error('coordinates', "Invalid coordinate format")
        
        # Population density validation
        if 'population_density' in data:
            density = data['population_density']
            if not isinstance(density, int) or density < 0:
                result.add_error('population_density', "Population density must be a non-negative integer")
        
        # Development level validation
        valid_levels = ['wilderness', 'frontier', 'rural', 'developed', 'urban', 'metropolitan']
        if 'development_level' in data:
            if data['development_level'] not in valid_levels:
                result.add_error('development_level', f"Development level must be one of: {valid_levels}")
        
        # Political control validation
        if 'political_control' in data and data['political_control']:
            if not FieldValidator.validate_uuid(data['political_control']):
                result.add_error('political_control', "Political control must be a valid faction UUID")
        
        return result


class POIValidator(BaseValidator):
    """Validator for POI entities"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        
        # Required fields
        required_fields = ['name', 'poi_type']
        for field in required_fields:
            if field not in data or not data[field]:
                result.add_error(field, f"Required field '{field}' is missing or empty")
        
        # POI type validation
        valid_types = [
            'temple', 'dungeon', 'city', 'town', 'village', 'castle', 'tower',
            'ruins', 'cave', 'forest', 'mountain', 'lake', 'river', 'bridge',
            'tavern', 'shop', 'guild_hall', 'library', 'cemetery', 'monument'
        ]
        if 'poi_type' in data:
            if data['poi_type'] not in valid_types:
                result.add_warning('poi_type', f"Unusual POI type: {data['poi_type']}")
        
        # Region reference validation
        if 'region_id' in data and data['region_id']:
            if not FieldValidator.validate_uuid(data['region_id']):
                result.add_error('region_id', "Region ID must be a valid UUID")
        
        # Coordinates validation
        if 'coordinates' in data and data['coordinates']:
            if not FieldValidator.validate_coordinates(data['coordinates']):
                result.add_error('coordinates', "Invalid coordinate format")
        
        # Danger level validation
        if 'danger_level' in data:
            if not FieldValidator.validate_rating(data['danger_level'], 1, 10):
                result.add_error('danger_level', "Danger level must be between 1 and 10")
        
        # Discovery difficulty validation
        if 'discovery_difficulty' in data:
            if not FieldValidator.validate_rating(data['discovery_difficulty'], 1, 10):
                result.add_error('discovery_difficulty', "Discovery difficulty must be between 1 and 10")
        
        # Size category validation
        valid_sizes = ['tiny', 'small', 'medium', 'large', 'huge', 'gargantuan']
        if 'size_category' in data:
            if data['size_category'] not in valid_sizes:
                result.add_error('size_category', f"Size category must be one of: {valid_sizes}")
        
        return result


class MarketValidator(BaseValidator):
    """Validator for market entities"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        
        # Required fields
        if 'name' not in data or not data['name']:
            result.add_error('name', "Market name is required")
        
        # Market type validation
        valid_types = ['general', 'specialty', 'black', 'noble', 'agricultural', 'craft', 'luxury']
        if 'market_type' in data:
            if data['market_type'] not in valid_types:
                result.add_warning('market_type', f"Unusual market type: {data['market_type']}")
        
        # Size category validation
        valid_sizes = ['village', 'town', 'city', 'metropolis']
        if 'size_category' in data:
            if data['size_category'] not in valid_sizes:
                result.add_error('size_category', f"Size category must be one of: {valid_sizes}")
        
        # Trade volume validation
        if 'trade_volume' in data:
            if not FieldValidator.validate_currency_amount(data['trade_volume']):
                result.add_error('trade_volume', "Trade volume must be a non-negative number")
        
        # Economic health validation
        if 'economic_health' in data:
            if not FieldValidator.validate_percentage(data['economic_health'], 0.0, 2.0):
                result.add_error('economic_health', "Economic health must be between 0.0 and 2.0")
        
        # Reference validations
        if 'region_id' in data and data['region_id']:
            if not FieldValidator.validate_uuid(data['region_id']):
                result.add_error('region_id', "Region ID must be a valid UUID")
        
        if 'poi_id' in data and data['poi_id']:
            if not FieldValidator.validate_uuid(data['poi_id']):
                result.add_error('poi_id', "POI ID must be a valid UUID")
        
        return result


class QuestValidator(BaseValidator):
    """Validator for quest entities"""
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult()
        
        # Required fields
        required_fields = ['title', 'objectives']
        for field in required_fields:
            if field not in data or not data[field]:
                result.add_error(field, f"Required field '{field}' is missing or empty")
        
        # Quest type validation
        valid_types = [
            'main', 'side', 'fetch', 'escort', 'kill', 'explore', 'delivery',
            'rescue', 'diplomacy', 'crafting', 'gathering', 'investigation'
        ]
        if 'quest_type' in data:
            if data['quest_type'] not in valid_types:
                result.add_warning('quest_type', f"Unusual quest type: {data['quest_type']}")
        
        # Objectives validation
        if 'objectives' in data:
            objectives = data['objectives']
            if not isinstance(objectives, list) or len(objectives) == 0:
                result.add_error('objectives', "Objectives must be a non-empty list")
            else:
                for i, objective in enumerate(objectives):
                    if not isinstance(objective, dict):
                        result.add_error('objectives', f"Objective {i+1} must be a dictionary")
                    elif 'description' not in objective:
                        result.add_error('objectives', f"Objective {i+1} must have a description")
        
        # Quest giver validation
        if 'quest_giver_id' in data and data['quest_giver_id']:
            if not FieldValidator.validate_uuid(data['quest_giver_id']):
                result.add_error('quest_giver_id', "Quest giver ID must be a valid UUID")
        
        # Status validation
        valid_statuses = ['available', 'active', 'completed', 'failed', 'cancelled']
        if 'status' in data:
            if data['status'] not in valid_statuses:
                result.add_error('status', f"Status must be one of: {valid_statuses}")
        
        return result


class DataIntegrityChecker:
    """Checks data integrity across the system"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def check_referential_integrity(self) -> ValidationResult:
        """Check referential integrity across all systems"""
        result = ValidationResult()
        
        # Check character location references
        orphaned_characters = self.db.execute("""
            SELECT c.id, c.name, c.current_location
            FROM character_entities c
            LEFT JOIN region_entities r ON c.current_location = r.id
            LEFT JOIN poi_entities p ON c.current_location = p.id
            WHERE c.current_location IS NOT NULL 
            AND r.id IS NULL 
            AND p.id IS NULL
        """).fetchall()
        
        for char in orphaned_characters:
            result.add_error('referential_integrity', 
                           f"Character {char.name} references non-existent location {char.current_location}")
        
        # Check POI region references
        orphaned_pois = self.db.execute("""
            SELECT p.id, p.name, p.region_id
            FROM poi_entities p
            LEFT JOIN region_entities r ON p.region_id = r.id
            WHERE p.region_id IS NOT NULL AND r.id IS NULL
        """).fetchall()
        
        for poi in orphaned_pois:
            result.add_error('referential_integrity',
                           f"POI {poi.name} references non-existent region {poi.region_id}")
        
        # Check market location references
        orphaned_markets = self.db.execute("""
            SELECT m.id, m.name, m.region_id, m.poi_id
            FROM market_entities m
            LEFT JOIN region_entities r ON m.region_id = r.id
            LEFT JOIN poi_entities p ON m.poi_id = p.id
            WHERE (m.region_id IS NOT NULL AND r.id IS NULL)
            OR (m.poi_id IS NOT NULL AND p.id IS NULL)
        """).fetchall()
        
        for market in orphaned_markets:
            result.add_error('referential_integrity',
                           f"Market {market.name} has invalid location references")
        
        return result
    
    def check_data_consistency(self) -> ValidationResult:
        """Check data consistency rules"""
        result = ValidationResult()
        
        # Check for duplicate character names in same region
        duplicates = self.db.execute("""
            SELECT name, current_location, COUNT(*)
            FROM character_entities
            WHERE current_location IS NOT NULL
            GROUP BY name, current_location
            HAVING COUNT(*) > 1
        """).fetchall()
        
        for dup in duplicates:
            result.add_warning('data_consistency',
                             f"Multiple characters named '{dup.name}' in same location")
        
        # Check for markets without locations
        homeless_markets = self.db.execute("""
            SELECT id, name
            FROM market_entities
            WHERE region_id IS NULL AND poi_id IS NULL
        """).fetchall()
        
        for market in homeless_markets:
            result.add_error('data_consistency',
                           f"Market {market.name} has no location reference")
        
        # Check for negative currency amounts
        negative_transactions = self.db.execute("""
            SELECT id, total_value
            FROM transaction_entities
            WHERE total_value < 0
        """).fetchall()
        
        for txn in negative_transactions:
            result.add_error('data_consistency',
                           f"Transaction {txn.id} has negative value {txn.total_value}")
        
        return result


class ValidationService:
    """Main validation service coordinator"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.validators = {
            'character': CharacterValidator(self.db),
            'region': RegionValidator(self.db),
            'poi': POIValidator(self.db),
            'market': MarketValidator(self.db),
            'quest': QuestValidator(self.db),
        }
        self.integrity_checker = DataIntegrityChecker(self.db)
    
    def validate_entity(self, entity_type: str, data: Dict[str, Any]) -> ValidationResult:
        """Validate a specific entity"""
        if entity_type not in self.validators:
            result = ValidationResult()
            result.add_error('validation', f"No validator found for entity type: {entity_type}")
            return result
        
        return self.validators[entity_type].validate(data)
    
    def validate_system_integrity(self) -> ValidationResult:
        """Validate overall system integrity"""
        result = ValidationResult()
        
        # Check referential integrity
        ref_result = self.integrity_checker.check_referential_integrity()
        result.errors.extend(ref_result.errors)
        result.warnings.extend(ref_result.warnings)
        
        # Check data consistency
        consistency_result = self.integrity_checker.check_data_consistency()
        result.errors.extend(consistency_result.errors)
        result.warnings.extend(consistency_result.warnings)
        
        # Set overall validity
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def bulk_validate(self, entities: List[Dict[str, Any]]) -> Dict[str, ValidationResult]:
        """Validate multiple entities"""
        results = {}
        
        for i, entity_data in enumerate(entities):
            entity_type = entity_data.get('entity_type')
            if not entity_type:
                result = ValidationResult()
                result.add_error('validation', "Entity type not specified")
                results[f"entity_{i}"] = result
                continue
            
            results[f"{entity_type}_{i}"] = self.validate_entity(entity_type, entity_data)
        
        return results 