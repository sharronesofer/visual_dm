from typing import Dict, Any, Optional
from marshmallow import Schema, fields, validate, validates, ValidationError
from .types import POIType

class POISchema(Schema):
    """Schema for validating POI data."""
    
    # Required fields
    id = fields.Str(required=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    type = fields.Str(required=True, validate=validate.OneOf([t.value for t in POIType]))
    region_id = fields.Str(required=True)
    x = fields.Float(required=True)
    y = fields.Float(required=True)
    z = fields.Float(required=True)
    
    # Optional fields with defaults
    faction_id = fields.Str(required=False, load_default=None, dump_default=None)
    owner_id = fields.Str(required=False, load_default=None, dump_default=None)
    
    # State flags
    is_discovered = fields.Bool(required=False, load_default=False, dump_default=False)
    is_public = fields.Bool(required=False, load_default=True, dump_default=True)
    
    # Timestamps
    created_at = fields.DateTime(required=False, load_default=None, dump_default=None)
    updated_at = fields.DateTime(required=False, load_default=None, dump_default=None)
    
    # Level range for POI content
    level_range = fields.Dict(required=False, load_default=lambda: {"min": 1, "max": 20})
    
    @validates("level_range")
    def validate_level_range(self, value):
        if not isinstance(value, dict):
            raise ValidationError("Level range must be a dictionary with 'min' and 'max' keys")
        
        if "min" not in value or "max" not in value:
            raise ValidationError("Level range must contain both 'min' and 'max' keys")
            
        min_level = value.get("min")
        max_level = value.get("max")
        
        if not isinstance(min_level, int) or not isinstance(max_level, int):
            raise ValidationError("Level range values must be integers")
            
        if min_level < 1:
            raise ValidationError("Minimum level cannot be less than 1")
            
        if max_level > 20:
            raise ValidationError("Maximum level cannot exceed 20")
            
        if min_level > max_level:
            raise ValidationError("Minimum level cannot be greater than maximum level")

    @staticmethod
    def validate_poi_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate POI data against the schema.
        
        Args:
            data: Dictionary containing POI data
            
        Returns:
            Dict[str, Any]: Validated and serialized POI data
            
        Raises:
            ValidationError: If validation fails
        """
        schema = POISchema()
        return schema.load(data) 