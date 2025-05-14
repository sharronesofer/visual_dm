#!/usr/bin/env python3
"""
Python Module Template

This template demonstrates the structure and style for Python modules
in the Visual DM project after TypeScript to Python migration.

Usage:
  1. Copy this template to create new Python modules
  2. Update the docstring, class names, and implementations
  3. Add proper type annotations for all parameters and return values
"""

import os
import sys
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass


class ExampleEnum(Enum):
    """
    Example enumeration that demonstrates Python enum usage.
    
    Replaces TypeScript enums with Python's Enum class.
    """
    OPTION_ONE = "option_one"
    OPTION_TWO = "option_two"
    OPTION_THREE = "option_three"


@dataclass
class ExampleDataClass:
    """
    Example dataclass for simple data structures.
    
    Dataclasses are useful for simple data containers that were
    often represented as interfaces in TypeScript.
    """
    id: str
    name: str
    value: int
    is_active: bool = True
    tags: Optional[List[str]] = None


class ExampleModel:
    """
    Example model class that demonstrates a complex class structure.
    
    This replaces TypeScript classes with Python classes using
    type annotations for properties and methods.
    """
    
    def __init__(
        self, 
        id: str, 
        name: str, 
        options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize the ExampleModel.
        
        Args:
            id: Unique identifier for the model
            name: Display name for the model
            options: Optional configuration dictionary
        """
        self.id: str = id
        self.name: str = name
        self.options: Dict[str, Any] = options or {}
        self._private_value: int = 0
    
    @property
    def private_value(self) -> int:
        """
        Get the private value.
        
        Returns:
            The current private value
        """
        return self._private_value
    
    @private_value.setter
    def private_value(self, value: int) -> None:
        """
        Set the private value with validation.
        
        Args:
            value: New value to set (must be non-negative)
        
        Raises:
            ValueError: If value is negative
        """
        if value < 0:
            raise ValueError("Private value cannot be negative")
        self._private_value = value
    
    def process_data(self, data: List[Dict[str, Any]]) -> Dict[str, List[Any]]:
        """
        Process a list of data dictionaries.
        
        This is an example of a method with complex types.
        
        Args:
            data: List of data dictionaries to process
        
        Returns:
            Dictionary of processed results grouped by category
        """
        result: Dict[str, List[Any]] = {}
        
        for item in data:
            category = item.get("category", "uncategorized")
            if category not in result:
                result[category] = []
            result[category].append(self._transform_item(item))
        
        return result
    
    def _transform_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single data item (private method).
        
        Args:
            item: Data dictionary to transform
        
        Returns:
            Transformed data dictionary
        """
        return {
            "id": item.get("id", "unknown"),
            "name": item.get("name", "").upper(),
            "processed_by": self.name,
            "timestamp": item.get("timestamp"),
            "status": ExampleEnum.OPTION_ONE.value
        }


def example_function(param1: str, param2: int = 0) -> Optional[str]:
    """
    Example standalone function.
    
    Args:
        param1: First parameter description
        param2: Second parameter description with default
    
    Returns:
        Result string or None if parameters are invalid
    """
    if not param1 or param2 < 0:
        return None
    
    return f"{param1}_{param2}"


def main() -> int:
    """
    Example main function.
    
    Returns:
        Exit code (0 for success)
    """
    # Example usage of the module components
    model = ExampleModel(id="example1", name="Example Model")
    model.private_value = 42
    
    data = [
        {"id": "1", "name": "item1", "category": "A", "timestamp": "2023-01-01"},
        {"id": "2", "name": "item2", "category": "B", "timestamp": "2023-01-02"},
        {"id": "3", "name": "item3", "category": "A", "timestamp": "2023-01-03"},
    ]
    
    results = model.process_data(data)
    print(f"Processed {len(data)} items into {len(results)} categories")
    
    result = example_function("test", 123)
    print(f"Function result: {result}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 