#!/usr/bin/env python3
"""
base.py - Base Data Contracts for World Generation System

This module defines the base classes and interfaces for all world generation data contracts.
It provides mechanisms for versioning, validation, and error handling.

Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol, Generic, Callable, cast
from enum import Enum
from abc import ABC, abstractmethod
import json
import logging
from dataclasses import dataclass, field, asdict

# Set up logging
logger = logging.getLogger("worldgen.contracts")

class WorldGenVersion:
    """Versioning information for world generation contracts"""
    MAJOR = 1
    MINOR = 0
    PATCH = 0
    
    @classmethod
    def get_version_string(cls) -> str:
        """Get the version as a semver string"""
        return f"{cls.MAJOR}.{cls.MINOR}.{cls.PATCH}"
    
    @classmethod
    def get_version_tuple(cls) -> tuple:
        """Get the version as a tuple"""
        return (cls.MAJOR, cls.MINOR, cls.PATCH)
    
    @classmethod
    def is_compatible_with(cls, version_str: str) -> bool:
        """
        Check if the current version is compatible with the provided version.
        
        Following semver principles:
        - Major version changes break compatibility
        - Minor and patch versions maintain compatibility
        
        Args:
            version_str: Version string to compare against (e.g., "1.0.0")
            
        Returns:
            True if compatible, False otherwise
        """
        try:
            # Parse version string
            parts = version_str.split('.')
            if len(parts) < 3:
                return False
                
            other_major = int(parts[0])
            
            # Check major version only (semver compatibility rules)
            return cls.MAJOR == other_major
        except ValueError:
            # If parsing fails, assume incompatible
            return False


class WorldGenContractError(Exception):
    """Base exception for all contract-related errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {json.dumps(self.details)}"
        return self.message


class ValidationError(WorldGenContractError):
    """Exception raised when contract validation fails"""
    pass


class VersionError(WorldGenContractError):
    """Exception raised when version compatibility fails"""
    pass


# Type for validation functions
ValidationFn = Callable[[Any], Union[bool, Dict[str, Any]]]

class WorldGenContractValidator:
    """Validator for WorldGen contracts"""
    
    @staticmethod
    def validate_string(value: Any, 
                         min_length: int = 0, 
                         max_length: Optional[int] = None,
                         allow_empty: bool = False) -> bool:
        """
        Validate a string value
        
        Args:
            value: The value to validate
            min_length: Minimum string length
            max_length: Maximum string length (if any)
            allow_empty: Whether empty strings are allowed
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(value, str):
            return False
            
        if not allow_empty and len(value) == 0:
            return False
            
        if len(value) < min_length:
            return False
            
        if max_length is not None and len(value) > max_length:
            return False
            
        return True
    
    @staticmethod
    def validate_number(value: Any, 
                         min_value: Optional[float] = None, 
                         max_value: Optional[float] = None,
                         allow_zero: bool = True,
                         integer_only: bool = False) -> bool:
        """
        Validate a numeric value
        
        Args:
            value: The value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_zero: Whether zero is allowed
            integer_only: Whether only integers are allowed
            
        Returns:
            True if valid, False otherwise
        """
        if integer_only:
            if not isinstance(value, int):
                return False
        else:
            if not isinstance(value, (int, float)):
                return False
                
        if not allow_zero and value == 0:
            return False
            
        if min_value is not None and value < min_value:
            return False
            
        if max_value is not None and value > max_value:
            return False
            
        return True
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], 
                                 required_fields: List[str]) -> Dict[str, List[str]]:
        """
        Validate that all required fields are present
        
        Args:
            data: The data object to validate
            required_fields: List of required field names
            
        Returns:
            Dict with 'missing' key containing any missing fields
        """
        missing = []
        
        for field in required_fields:
            if field not in data or data[field] is None:
                missing.append(field)
                
        return {"missing": missing}


# Type variable for versioned contract types
T = TypeVar('T')

class ContractVersioned(Protocol):
    """Protocol for classes that support versioning"""
    contract_version: str
    
    def is_compatible_with(self, other_version: str) -> bool:
        """Check if compatible with another version"""
        ...


class WorldGenContract(ABC):
    """Base class for all world generation data contracts"""
    
    contract_version: str = WorldGenVersion.get_version_string()
    
    def __init__(self):
        self._frozen = False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert contract to a dictionary representation
        
        Returns:
            Dictionary representation of the contract
        """
        if hasattr(self, '__dataclass_fields__'):
            # If it's a dataclass, use asdict
            result = asdict(self)
        else:
            # Otherwise, use __dict__
            result = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        # Add version info
        result['contract_version'] = self.contract_version
        
        return result
    
    def to_json(self) -> str:
        """
        Convert contract to a JSON string
        
        Returns:
            JSON string representation of the contract
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls: type[T], data: Dict[str, Any]) -> T:
        """
        Create a contract from a dictionary
        
        Args:
            data: Dictionary containing contract data
            
        Returns:
            New contract instance
            
        Raises:
            VersionError: If version is incompatible
            ValidationError: If validation fails
        """
        # Check version compatibility if version included
        if 'contract_version' in data:
            if not WorldGenVersion.is_compatible_with(data['contract_version']):
                raise VersionError(
                    f"Version mismatch: Current {WorldGenVersion.get_version_string()}, Data {data['contract_version']}",
                    {"current_version": WorldGenVersion.get_version_string(), 
                     "data_version": data['contract_version']}
                )
        
        # Create new instance and populate fields
        instance = cls()
        
        # Validate and populate
        instance._validate_and_populate(data)
        
        return instance
    
    @classmethod
    def from_json(cls: type[T], json_str: str) -> T:
        """
        Create a contract from a JSON string
        
        Args:
            json_str: JSON string containing contract data
            
        Returns:
            New contract instance
            
        Raises:
            WorldGenContractError: If JSON parsing fails
            VersionError: If version is incompatible
            ValidationError: If validation fails
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise WorldGenContractError("Invalid JSON data", {"error": str(e)})
    
    @abstractmethod
    def _validate_and_populate(self, data: Dict[str, Any]) -> None:
        """
        Validate data and populate fields
        
        Args:
            data: Dictionary containing contract data
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    def _freeze(self) -> None:
        """
        Freeze the contract to prevent further modification
        """
        self._frozen = True
    
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Override setattr to enforce immutability after initialization
        
        Args:
            name: Attribute name
            value: Attribute value
            
        Raises:
            WorldGenContractError: If attempting to modify a frozen contract
        """
        if hasattr(self, '_frozen') and self._frozen and not name.startswith('_'):
            raise WorldGenContractError(
                f"Cannot modify frozen contract: attempted to set {name}",
                {"name": name, "value": str(value)}
            )
        super().__setattr__(name, value)


# Basic query result type
@dataclass
class QueryResult(Generic[T]):
    """Generic query result for data contract queries"""
    success: bool = True
    data: Optional[Union[T, List[T]]] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_empty(self) -> bool:
        """Check if the result has no data"""
        if isinstance(self.data, list):
            return len(self.data) == 0
        return self.data is None 