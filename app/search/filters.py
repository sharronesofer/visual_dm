"""Filter expression parsing and handling for search functionality.

This module provides classes and utilities for parsing and handling filter expressions
in search queries. It supports multiple filter conditions with logical operators and
field-specific filtering for different data types.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from dataclasses import dataclass

class FilterOperator(str, Enum):
    """Supported filter operators."""
    EQ = 'eq'
    NE = 'ne'
    GT = 'gt'
    GTE = 'gte'
    LT = 'lt'
    LTE = 'lte'
    IN = 'in'
    NIN = 'nin'
    CONTAINS = 'contains'
    NOT_CONTAINS = 'not_contains'
    BETWEEN = 'between'
    RANGE = 'range'
    EXISTS = 'exists'
    NOT_EXISTS = 'not_exists'

class FilterDataType(str, Enum):
    """Supported data types for filter values."""
    STRING = 'string'
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    DATE = 'date'
    LIST = 'list'
    RANGE = 'range'
    NESTED = 'nested'

class FilterCondition(BaseModel):
    """Single filter condition.
    
    Attributes:
        field: Field name to filter on
        operator: Filter operator to apply
        value: Filter value(s)
        data_type: Expected data type of the field
        nested_path: Optional path for nested fields
    """
    field: str = Field(..., description="Field name to filter on")
    operator: FilterOperator = Field(..., description="Filter operator to apply")
    value: Union[str, int, float, bool, datetime, List[Any], Dict[str, Any]] = Field(
        ..., 
        description="Filter value(s)"
    )
    data_type: FilterDataType = Field(..., description="Expected data type of the field")
    nested_path: Optional[str] = Field(None, description="Path for nested fields")

class FilterExpression:
    """Filter expression combining multiple conditions.
    
    Attributes:
        conditions: List of filter conditions
        combine_with: How to combine conditions ('and' or 'or')
    """
    def __init__(
        self,
        conditions: List[FilterCondition],
        combine_with: str = "and"
    ):
        self.conditions = conditions
        self.combine_with = combine_with

# Game entity field types
GAME_FIELD_TYPES = {
    # Common fields
    "name": FilterDataType.STRING,
    "description": FilterDataType.STRING,
    "type": FilterDataType.STRING,
    "tags": FilterDataType.LIST,
    "created_at": FilterDataType.DATE,
    "updated_at": FilterDataType.DATE,
    
    # NPC fields
    "level": FilterDataType.NUMBER,
    "faction": FilterDataType.STRING,
    "location": FilterDataType.STRING,
    "dialogue": FilterDataType.LIST,
    "quests": FilterDataType.LIST,
    "schedule": FilterDataType.NESTED,
    "inventory": FilterDataType.LIST,
    "stats": FilterDataType.NESTED,
    
    # Item fields
    "rarity": FilterDataType.STRING,
    "category": FilterDataType.STRING,
    "level_requirement": FilterDataType.NUMBER,
    "value": FilterDataType.NUMBER,
    "stats": FilterDataType.NESTED,
    "effects": FilterDataType.NESTED,
    "durability": FilterDataType.NESTED,
    
    # Location fields
    "region": FilterDataType.STRING,
    "terrain_type": FilterDataType.STRING,
    "danger_level": FilterDataType.NUMBER,
    "npcs": FilterDataType.LIST,
    "items": FilterDataType.LIST,
    "quests": FilterDataType.LIST,
    "connections": FilterDataType.LIST,
    "resources": FilterDataType.NESTED,
    
    # Quest fields
    "difficulty": FilterDataType.STRING,
    "status": FilterDataType.STRING,
    "prerequisites": FilterDataType.NESTED,
    "objectives": FilterDataType.NESTED,
    "rewards": FilterDataType.NESTED,
    "giver": FilterDataType.STRING,
    "location": FilterDataType.STRING,
    "time_limit": FilterDataType.NUMBER,
    
    # Faction fields
    "faction_type": FilterDataType.STRING,
    "status": FilterDataType.STRING,
    "influence": FilterDataType.NUMBER,
    "relationships": FilterDataType.NESTED,
    "leaders": FilterDataType.LIST,
    "headquarters": FilterDataType.STRING,
    "ranks": FilterDataType.NESTED,
    "perks": FilterDataType.NESTED
}

class FilterValidator:
    """Validator for filter values based on field type."""
    
    @staticmethod
    def validate_field(field: str, value: Any, data_type: FilterDataType) -> None:
        """Validate a filter value for a specific field and data type.
        
        Args:
            field: Field name being filtered
            value: Value to validate
            data_type: Expected data type
            
        Raises:
            ValueError: If value is invalid for the field
        """
        try:
            if data_type == FilterDataType.NUMBER:
                if isinstance(value, (list, dict)):
                    for v in (value if isinstance(value, list) else value.values()):
                        float(v)  # Validate each value can be converted to float
                else:
                    float(value)
            elif data_type == FilterDataType.DATE:
                if isinstance(value, str):
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
            elif data_type == FilterDataType.RANGE:
                if not isinstance(value, dict) or "from" not in value or "to" not in value:
                    raise ValueError("Range must be a dict with 'from' and 'to' keys")
            elif data_type == FilterDataType.NESTED:
                if not isinstance(value, dict):
                    raise ValueError("Nested filter value must be a dictionary")
        except Exception as e:
            raise ValueError(f"Invalid value for field '{field}' ({data_type}): {str(e)}")

class FilterParser:
    """Parser for filter expressions."""
    
    @staticmethod
    def parse_value(value: Any, data_type: FilterDataType, field: str) -> Any:
        """Parse and validate a filter value.
        
        Args:
            value: Value to parse
            data_type: Expected data type
            field: Field name for validation context
            
        Returns:
            Parsed and validated value
            
        Raises:
            ValueError: If value cannot be parsed or is invalid
        """
        # Validate the value first
        FilterValidator.validate_field(field, value, data_type)
        
        try:
            if data_type == FilterDataType.STRING:
                return str(value)
            elif data_type == FilterDataType.NUMBER:
                return float(value)
            elif data_type == FilterDataType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() == "true"
                return bool(value)
            elif data_type == FilterDataType.DATE:
                if isinstance(value, str):
                    return datetime.fromisoformat(value.replace("Z", "+00:00"))
                return value
            elif data_type == FilterDataType.LIST:
                if isinstance(value, str):
                    return value.split(",")
                return list(value)
            elif data_type == FilterDataType.RANGE:
                if isinstance(value, dict):
                    return value
                elif isinstance(value, str):
                    parts = value.split(",")
                    if len(parts) != 2:
                        raise ValueError("Range must have two values")
                    return {"from": float(parts[0]), "to": float(parts[1])}
                raise ValueError("Invalid range format")
            elif data_type == FilterDataType.NESTED:
                if isinstance(value, dict):
                    return value
                elif isinstance(value, str):
                    import json
                    return json.loads(value)
                return value
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
        except Exception as e:
            raise ValueError(f"Failed to parse value '{value}' for field '{field}' as {data_type}: {str(e)}")

    @staticmethod
    def build_es_filter(condition: FilterCondition) -> Dict[str, Any]:
        """Build Elasticsearch filter clause from condition.
        
        Args:
            condition: Filter condition to convert
            
        Returns:
            Elasticsearch filter clause
        """
        value = FilterParser.parse_value(
            condition.value,
            condition.data_type,
            condition.field
        )
        
        # Handle nested fields
        if condition.nested_path:
            return {
                "nested": {
                    "path": condition.nested_path,
                    "query": {
                        "bool": {
                            "must": [FilterParser._build_basic_filter(condition, value)]
                        }
                    }
                }
            }
            
        return FilterParser._build_basic_filter(condition, value)

    @staticmethod
    def _build_basic_filter(condition: FilterCondition, value: Any) -> Dict[str, Any]:
        """Build basic Elasticsearch filter clause.
        
        Args:
            condition: Filter condition
            value: Parsed filter value
            
        Returns:
            Elasticsearch filter clause
        """
        if condition.operator == FilterOperator.EQ:
            return {"term": {condition.field: value}}
        elif condition.operator == FilterOperator.NE:
            return {"bool": {"must_not": {"term": {condition.field: value}}}}
        elif condition.operator in [
            FilterOperator.GT,
            FilterOperator.GTE,
            FilterOperator.LT,
            FilterOperator.LTE
        ]:
            op_map = {
                FilterOperator.GT: "gt",
                FilterOperator.GTE: "gte",
                FilterOperator.LT: "lt",
                FilterOperator.LTE: "lte"
            }
            return {"range": {condition.field: {op_map[condition.operator]: value}}}
        elif condition.operator == FilterOperator.IN:
            return {"terms": {condition.field: value}}
        elif condition.operator == FilterOperator.NIN:
            return {"bool": {"must_not": {"terms": {condition.field: value}}}}
        elif condition.operator == FilterOperator.CONTAINS:
            if condition.data_type == FilterDataType.LIST:
                return {"terms": {condition.field: [value]}}
            return {"wildcard": {condition.field: f"*{value}*"}}
        elif condition.operator == FilterOperator.NOT_CONTAINS:
            if condition.data_type == FilterDataType.LIST:
                return {"bool": {"must_not": {"terms": {condition.field: [value]}}}}
            return {"bool": {"must_not": {"wildcard": {condition.field: f"*{value}*"}}}}
        elif condition.operator == FilterOperator.BETWEEN:
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError("BETWEEN operator requires two values")
            return {"range": {condition.field: {"gte": value[0], "lte": value[1]}}}
        elif condition.operator == FilterOperator.RANGE:
            if not isinstance(value, dict) or "from" not in value or "to" not in value:
                raise ValueError("RANGE operator requires 'from' and 'to' values")
            return {"range": {condition.field: {"gte": value["from"], "lte": value["to"]}}}
        elif condition.operator == FilterOperator.EXISTS:
            return {"exists": {"field": condition.field}}
        elif condition.operator == FilterOperator.NOT_EXISTS:
            return {"bool": {"must_not": {"exists": {"field": condition.field}}}}
        else:
            raise ValueError(f"Unsupported operator: {condition.operator}")

    @staticmethod
    def build_es_query(expression: FilterExpression) -> Dict[str, Any]:
        """Build complete Elasticsearch query from filter expression.
        
        Args:
            expression: Filter expression to convert
            
        Returns:
            Elasticsearch query dict
        """
        if not expression.conditions:
            return {}
            
        filters = [
            FilterParser.build_es_filter(condition)
            for condition in expression.conditions
        ]
        
        if len(filters) == 1:
            return filters[0]
            
        return {
            "bool": {
                "must" if expression.combine_with == "and" else "should": filters,
                "minimum_should_match": 1 if expression.combine_with == "or" else None
            }
        }

def parse_filter_params(
    params: Dict[str, Any],
    field_types: Optional[Dict[str, FilterDataType]] = None
) -> FilterExpression:
    """Parse filter parameters from request into a FilterExpression.
    
    Args:
        params: Dictionary of filter parameters
        field_types: Mapping of field names to their data types (defaults to GAME_FIELD_TYPES)
        
    Returns:
        FilterExpression instance
        
    Raises:
        ValueError: If filter parameters are invalid
    """
    field_types = field_types or GAME_FIELD_TYPES
    conditions = []
    combine_with = params.get("combine_with", "and")
    
    for field, field_type in field_types.items():
        if field not in params:
            continue
            
        value = params[field]
        operator = params.get(f"{field}_op", "eq")
        nested_path = None
        
        # Handle nested fields
        if "." in field:
            nested_path = field.split(".")[0]
            
        try:
            operator = FilterOperator(operator)
            conditions.append(FilterCondition(
                field=field,
                operator=operator,
                value=value,
                data_type=field_type,
                nested_path=nested_path
            ))
        except ValueError as e:
            raise ValueError(f"Invalid filter for field '{field}': {str(e)}")
            
    return FilterExpression(conditions=conditions, combine_with=combine_with)

def parse_filter_expression(field: str, filter_data: Dict[str, Any]) -> FilterExpression:
    """Parse a filter expression for a single field.
    
    Args:
        field: Field name
        filter_data: Filter data
        
    Returns:
        FilterExpression instance
    """
    field_type = GAME_FIELD_TYPES.get(field)
    if not field_type:
        raise ValueError(f"Unknown field: {field}")
        
    operator = filter_data.get("operator", "eq")
    value = filter_data.get("value")
    nested_path = None
    
    if "." in field:
        nested_path = field.split(".")[0]
        
    condition = FilterCondition(
        field=field,
        operator=FilterOperator(operator),
        value=value,
        data_type=field_type,
        nested_path=nested_path
    )
    
    return FilterExpression(conditions=[condition])

def apply_filters(entities: List[Any], expressions: List[FilterExpression]) -> List[Any]:
    """Apply multiple filter expressions to a list of entities.
    
    Args:
        entities: List of entities to filter
        expressions: List of filter expressions to apply
        
    Returns:
        Filtered list of entities
    """
    result = entities
    for expr in expressions:
        result = [
            entity for entity in result
            if all(
                apply_filter(entity, condition)
                for condition in expr.conditions
            )
        ]
    return result

def apply_filter(entity: Any, condition: FilterCondition) -> bool:
    """Apply a single filter condition to an entity.
    
    Args:
        entity: Entity to filter
        condition: Filter condition to apply
        
    Returns:
        True if entity matches the filter, False otherwise
    """
    try:
        # Get field value, handling nested paths
        value = entity
        for part in condition.field.split("."):
            value = getattr(value, part, None)
            if value is None:
                return False
                
        # Parse filter value
        filter_value = FilterParser.parse_value(condition.value, condition.data_type, condition.field)
        
        # Apply operator
        if condition.operator == FilterOperator.EQ:
            return value == filter_value
        elif condition.operator == FilterOperator.NE:
            return value != filter_value
        elif condition.operator == FilterOperator.GT:
            return value > filter_value
        elif condition.operator == FilterOperator.GTE:
            return value >= filter_value
        elif condition.operator == FilterOperator.LT:
            return value < filter_value
        elif condition.operator == FilterOperator.LTE:
            return value <= filter_value
        elif condition.operator == FilterOperator.IN:
            return value in filter_value
        elif condition.operator == FilterOperator.NIN:
            return value not in filter_value
        elif condition.operator == FilterOperator.CONTAINS:
            if isinstance(value, (list, tuple)):
                return filter_value in value
            return str(filter_value) in str(value)
        elif condition.operator == FilterOperator.NOT_CONTAINS:
            if isinstance(value, (list, tuple)):
                return filter_value not in value
            return str(filter_value) not in str(value)
        elif condition.operator == FilterOperator.BETWEEN:
            return filter_value[0] <= value <= filter_value[1]
        elif condition.operator == FilterOperator.RANGE:
            return filter_value["from"] <= value <= filter_value["to"]
        elif condition.operator == FilterOperator.EXISTS:
            return value is not None
        elif condition.operator == FilterOperator.NOT_EXISTS:
            return value is None
        else:
            raise ValueError(f"Unsupported operator: {condition.operator}")
    except Exception as e:
        logger.warning(f"Filter application failed: {str(e)}")
        return False

def get_field_type(field: str) -> FilterDataType:
    """Get the data type for a field.
    
    Args:
        field: Field name
        
    Returns:
        Expected data type for the field
        
    Raises:
        ValueError: If field type is unknown
    """
    if field not in GAME_FIELD_TYPES:
        # Default to string for unknown fields
        return FilterDataType.STRING
    return GAME_FIELD_TYPES[field]

def validate_filter_params(
    params: Dict[str, Any],
    field_types: Optional[Dict[str, FilterDataType]] = None
) -> None:
    """Validate filter parameters against field types.
    
    Args:
        params: Filter parameters to validate
        field_types: Optional mapping of field names to expected types
        
    Raises:
        ValueError: If any parameter is invalid
    """
    types = field_types or GAME_FIELD_TYPES
    
    for field, value in params.items():
        if isinstance(value, dict):
            # Handle operator-based filters
            operator = value.get("operator")
            if operator and operator not in FilterOperator.__members__:
                raise ValueError(f"Invalid operator '{operator}' for field '{field}'")
                
            filter_value = value.get("value")
            if filter_value is None:
                raise ValueError(f"Missing value for field '{field}'")
                
            data_type = types.get(field, FilterDataType.STRING)
            FilterValidator.validate_field(field, filter_value, data_type)
        else:
            # Handle direct value filters
            data_type = types.get(field, FilterDataType.STRING)
            FilterValidator.validate_field(field, value, data_type) 