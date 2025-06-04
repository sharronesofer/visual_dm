"""
POI Validation Service

Infrastructure service that provides validation for POI data according to
Development Bible standards and business rules.
"""

import logging
from typing import Dict, Any, Optional, List
from uuid import UUID

logger = logging.getLogger(__name__)


class PoiValidationService:
    """Service for validating POI data and business rules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_poi_data(self, poi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate POI creation/update data"""
        self.logger.debug(f"Validating POI data: {poi_data}")
        
        validated_data = {}
        
        # Validate required fields
        if 'name' not in poi_data or not poi_data['name']:
            raise ValueError("POI name is required")
        
        if not isinstance(poi_data['name'], str):
            raise ValueError("POI name must be a string")
        
        if len(poi_data['name'].strip()) == 0:
            raise ValueError("POI name cannot be empty")
        
        if len(poi_data['name']) > 255:
            raise ValueError("POI name cannot exceed 255 characters")
        
        validated_data['name'] = poi_data['name'].strip()
        
        # Validate optional description
        if 'description' in poi_data and poi_data['description'] is not None:
            if not isinstance(poi_data['description'], str):
                raise ValueError("POI description must be a string")
            if len(poi_data['description']) > 1000:
                raise ValueError("POI description cannot exceed 1000 characters")
            validated_data['description'] = poi_data['description'].strip()
        else:
            validated_data['description'] = None
        
        # Validate POI type
        valid_poi_types = [
            'city', 'town', 'village', 'settlement', 'outpost', 
            'fortress', 'temple', 'market', 'mine', 'other'
        ]
        poi_type = poi_data.get('poi_type', 'village')
        if poi_type not in valid_poi_types:
            raise ValueError(f"Invalid POI type '{poi_type}'. Must be one of: {valid_poi_types}")
        validated_data['poi_type'] = poi_type
        
        # Validate POI state
        valid_states = [
            'active', 'inactive', 'abandoned', 'ruined', 'under_construction',
            'declining', 'growing', 'normal', 'ruins', 'dungeon', 'repopulating', 'special'
        ]
        state = poi_data.get('state', 'active')
        if state not in valid_states:
            raise ValueError(f"Invalid POI state '{state}'. Must be one of: {valid_states}")
        validated_data['state'] = state
        
        # Validate population
        if 'population' in poi_data:
            population = poi_data['population']
            if not isinstance(population, int):
                try:
                    population = int(population)
                except (ValueError, TypeError):
                    raise ValueError("Population must be an integer")
            if population < 0:
                raise ValueError("Population cannot be negative")
            validated_data['population'] = population
        else:
            validated_data['population'] = 0
        
        # Validate max_population
        if 'max_population' in poi_data:
            max_population = poi_data['max_population']
            if not isinstance(max_population, int):
                try:
                    max_population = int(max_population)
                except (ValueError, TypeError):
                    raise ValueError("Max population must be an integer")
            if max_population < 0:
                raise ValueError("Max population cannot be negative")
            validated_data['max_population'] = max_population
        else:
            validated_data['max_population'] = 100
        
        # Validate properties
        if 'properties' in poi_data:
            properties = poi_data['properties']
            if properties is not None and not isinstance(properties, dict):
                raise ValueError("Properties must be a dictionary")
            validated_data['properties'] = properties or {}
        else:
            validated_data['properties'] = {}
        
        # Validate coordinates if provided
        for coord in ['location_x', 'location_y', 'location_z']:
            if coord in poi_data and poi_data[coord] is not None:
                try:
                    validated_data[coord] = float(poi_data[coord])
                except (ValueError, TypeError):
                    raise ValueError(f"{coord} must be a number")
        
        # Validate UUIDs if provided
        for uuid_field in ['region_id', 'faction_id']:
            if uuid_field in poi_data and poi_data[uuid_field] is not None:
                try:
                    if isinstance(poi_data[uuid_field], str):
                        UUID(poi_data[uuid_field])  # Validate UUID format
                        validated_data[uuid_field] = poi_data[uuid_field]
                    elif isinstance(poi_data[uuid_field], UUID):
                        validated_data[uuid_field] = str(poi_data[uuid_field])
                    else:
                        raise ValueError(f"{uuid_field} must be a valid UUID string")
                except ValueError:
                    raise ValueError(f"{uuid_field} must be a valid UUID")
        
        self.logger.debug(f"POI data validation successful")
        return validated_data
    
    def validate_population_limits(self, population: int, max_population: int) -> bool:
        """Validate population constraints"""
        try:
            if not isinstance(population, int) or not isinstance(max_population, int):
                return False
            
            if population < 0 or max_population < 0:
                return False
            
            if population > max_population:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating population limits: {e}")
            return False
    
    def validate_poi_state_transition(self, current_state: str, new_state: str) -> bool:
        """Validate if a state transition is allowed"""
        valid_transitions = {
            'active': ['declining', 'growing', 'inactive'],
            'growing': ['active', 'declining'],
            'declining': ['abandoned', 'active'],
            'abandoned': ['ruins', 'repopulating'],
            'ruins': ['abandoned'],
            'repopulating': ['active', 'declining'],
            'inactive': ['active'],
            'under_construction': ['active', 'abandoned'],
            'normal': ['active', 'declining', 'growing'],
            'special': ['active', 'inactive']
        }
        
        if current_state not in valid_transitions:
            return False
        
        return new_state in valid_transitions[current_state]
    
    def validate_poi_type_for_interaction(self, poi_type: str, interaction_type: str) -> bool:
        """Validate if a POI type supports a given interaction type"""
        type_interactions = {
            'city': ['social', 'trade', 'diplomacy', 'neutral'],
            'town': ['social', 'trade', 'diplomacy', 'neutral'],
            'village': ['social', 'trade', 'neutral'],
            'fortress': ['combat', 'diplomacy', 'neutral'],
            'temple': ['social', 'quest', 'exploration', 'neutral'],
            'market': ['trade', 'social', 'neutral'],
            'mine': ['exploration', 'trade', 'neutral'],
            'outpost': ['combat', 'neutral'],
            'settlement': ['social', 'neutral'],
            'other': ['neutral']
        }
        
        if poi_type not in type_interactions:
            return interaction_type == 'neutral'
        
        return interaction_type in type_interactions[poi_type]


def create_poi_validation_service() -> PoiValidationService:
    """Factory function to create POI validation service"""
    return PoiValidationService() 