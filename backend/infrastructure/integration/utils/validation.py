"""
Integration system - Validation module for comprehensive schema validation.

This module provides comprehensive validation infrastructure:
- ValidationManager class for coordinating validation across systems
- Pydantic schema integration for data validation
- Cross-system data validation and consistency checks
- Custom validation rules for game-specific logic
- Validation error handling and reporting
"""

import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union, Type, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from pydantic import BaseModel, ValidationError, validator
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Represents the result of a validation operation"""
    is_valid: bool
    system_id: str
    validation_type: str
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    info: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    data_schema: Optional[str] = None
    
    def add_error(self, field: str, message: str, severity: ValidationSeverity = ValidationSeverity.ERROR):
        """Add a validation error"""
        error_entry = {
            "field": field,
            "message": message,
            "severity": severity.value,
            "timestamp": datetime.now()
        }
        
        if severity == ValidationSeverity.CRITICAL or severity == ValidationSeverity.ERROR:
            self.errors.append(error_entry)
            self.is_valid = False
        elif severity == ValidationSeverity.WARNING:
            self.warnings.append(error_entry)
        else:
            self.info.append(error_entry)
    
    def get_error_summary(self) -> str:
        """Get a summary of all errors"""
        if not self.errors:
            return "No errors"
        
        summary = f"{len(self.errors)} error(s):\n"
        for error in self.errors:
            summary += f"  - {error['field']}: {error['message']}\n"
        return summary


class ValidationManager:
    """
    Manages comprehensive validation across systems with Pydantic schema integration.
    
    Provides:
    - Schema registration and validation
    - Cross-system data validation
    - Custom validation rules
    - Performance validation
    - Security validation
    """
    
    def __init__(self):
        self._registered_schemas: Dict[str, Type[BaseModel]] = {}
        self._custom_validators: Dict[str, List[Callable]] = defaultdict(list)
        self._cross_system_validators: Dict[str, Callable] = {}
        self._business_rule_validators: Dict[str, List[Callable]] = defaultdict(list)
        self._validation_cache: Dict[str, ValidationResult] = {}
        self._validation_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._lock = asyncio.Lock()
    
    async def register_schema(
        self,
        system_id: str,
        schema_name: str,
        schema_class: Type[BaseModel],
        custom_validators: Optional[List[Callable]] = None
    ) -> bool:
        """
        Register a Pydantic schema for system validation.
        
        Args:
            system_id: System identifier
            schema_name: Name of the schema
            schema_class: Pydantic model class
            custom_validators: Optional custom validation functions
            
        Returns:
            bool: True if registration successful
        """
        async with self._lock:
            try:
                schema_key = f"{system_id}.{schema_name}"
                self._registered_schemas[schema_key] = schema_class
                
                if custom_validators:
                    self._custom_validators[schema_key].extend(custom_validators)
                
                logger.info(f"Registered schema {schema_key}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to register schema {schema_key}: {e}")
                return False
    
    async def validate_data(
        self,
        system_id: str,
        schema_name: str,
        data: Dict[str, Any],
        enable_cache: bool = True
    ) -> ValidationResult:
        """
        Validate data against a registered schema.
        
        Args:
            system_id: System identifier
            schema_name: Schema to validate against
            data: Data to validate
            enable_cache: Whether to use validation cache
            
        Returns:
            ValidationResult: Validation results
        """
        schema_key = f"{system_id}.{schema_name}"
        cache_key = f"{schema_key}:{hash(json.dumps(data, sort_keys=True))}"
        
        # Check cache
        if enable_cache and cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        
        result = ValidationResult(
            is_valid=True,
            system_id=system_id,
            validation_type=f"schema_validation_{schema_name}",
            data_schema=schema_key
        )
        
        try:
            # Check if schema is registered
            if schema_key not in self._registered_schemas:
                result.add_error("schema", f"Schema {schema_key} not registered", ValidationSeverity.ERROR)
                return result
            
            schema_class = self._registered_schemas[schema_key]
            
            # Validate with Pydantic
            try:
                validated_instance = schema_class(**data)
                result.add_error("validation", "Data passed Pydantic validation", ValidationSeverity.INFO)
            except ValidationError as e:
                for error in e.errors():
                    field_path = ".".join(str(loc) for loc in error["loc"])
                    result.add_error(field_path, error["msg"], ValidationSeverity.ERROR)
            
            # Run custom validators
            for validator_func in self._custom_validators[schema_key]:
                try:
                    custom_result = await self._call_async_safe(validator_func, data)
                    if not custom_result:
                        result.add_error("custom_validation", f"Custom validator {validator_func.__name__} failed", ValidationSeverity.ERROR)
                except Exception as e:
                    result.add_error("custom_validation", f"Custom validator error: {e}", ValidationSeverity.ERROR)
            
            # Update stats
            self._validation_stats[system_id]["total_validations"] += 1
            if result.is_valid:
                self._validation_stats[system_id]["successful_validations"] += 1
            else:
                self._validation_stats[system_id]["failed_validations"] += 1
            
            # Cache result
            if enable_cache:
                self._validation_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            result.add_error("system_error", f"Validation system error: {e}", ValidationSeverity.CRITICAL)
            return result
    
    async def validate_cross_system(
        self,
        primary_system: str,
        related_systems: List[str],
        data: Dict[str, Any],
        consistency_rules: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate data consistency across multiple systems.
        
        Args:
            primary_system: Primary system for validation
            related_systems: Related systems to check consistency with
            data: Data to validate
            consistency_rules: Optional consistency rules
            
        Returns:
            ValidationResult: Cross-system validation results
        """
        result = ValidationResult(
            is_valid=True,
            system_id=primary_system,
            validation_type="cross_system_validation"
        )
        
        try:
            # Check if cross-system validator exists
            validator_key = f"{primary_system}_cross_system"
            if validator_key in self._cross_system_validators:
                validator_func = self._cross_system_validators[validator_key]
                validation_result = await self._call_async_safe(
                    validator_func, primary_system, related_systems, data, consistency_rules
                )
                
                if not validation_result:
                    result.add_error("cross_system", "Cross-system validation failed", ValidationSeverity.ERROR)
            
            # Validate against each related system's constraints
            for related_system in related_systems:
                # Check for referential integrity
                integrity_result = await self._validate_referential_integrity(
                    primary_system, related_system, data
                )
                
                if not integrity_result:
                    result.add_error(
                        f"referential_integrity_{related_system}",
                        f"Referential integrity check failed with {related_system}",
                        ValidationSeverity.ERROR
                    )
            
            return result
            
        except Exception as e:
            result.add_error("cross_system_error", f"Cross-system validation error: {e}", ValidationSeverity.CRITICAL)
            return result
    
    async def validate_business_rules(
        self,
        system_id: str,
        rule_category: str,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate business rules for game-specific logic.
        
        Args:
            system_id: System identifier
            rule_category: Category of business rules
            data: Data to validate
            context: Optional context for validation
            
        Returns:
            ValidationResult: Business rule validation results
        """
        result = ValidationResult(
            is_valid=True,
            system_id=system_id,
            validation_type=f"business_rules_{rule_category}"
        )
        
        try:
            rule_key = f"{system_id}.{rule_category}"
            
            for rule_validator in self._business_rule_validators[rule_key]:
                try:
                    rule_result = await self._call_async_safe(rule_validator, data, context)
                    if isinstance(rule_result, dict):
                        if not rule_result.get("valid", True):
                            result.add_error(
                                rule_result.get("field", "business_rule"),
                                rule_result.get("message", "Business rule validation failed"),
                                ValidationSeverity.ERROR
                            )
                    elif not rule_result:
                        result.add_error(
                            "business_rule",
                            f"Business rule {rule_validator.__name__} failed",
                            ValidationSeverity.ERROR
                        )
                except Exception as e:
                    result.add_error(
                        "business_rule_error",
                        f"Business rule validation error: {e}",
                        ValidationSeverity.ERROR
                    )
            
            return result
            
        except Exception as e:
            result.add_error("business_rule_system_error", f"Business rule system error: {e}", ValidationSeverity.CRITICAL)
            return result
    
    async def validate_performance(
        self,
        system_id: str,
        operation_type: str,
        data: Dict[str, Any],
        performance_thresholds: Optional[Dict[str, float]] = None
    ) -> ValidationResult:
        """
        Validate performance metrics for system operations.
        
        Args:
            system_id: System identifier
            operation_type: Type of operation being validated
            data: Operation data and metrics
            performance_thresholds: Optional performance thresholds
            
        Returns:
            ValidationResult: Performance validation results
        """
        result = ValidationResult(
            is_valid=True,
            system_id=system_id,
            validation_type=f"performance_{operation_type}"
        )
        
        try:
            # Default performance thresholds
            default_thresholds = {
                "max_response_time": 1.0,  # seconds
                "max_memory_usage": 100 * 1024 * 1024,  # 100MB
                "max_cpu_usage": 80.0,  # 80%
                "min_throughput": 100,  # operations per second
            }
            
            thresholds = performance_thresholds or default_thresholds
            
            # Check response time
            response_time = data.get("response_time", 0)
            if response_time > thresholds.get("max_response_time", 1.0):
                result.add_error(
                    "response_time",
                    f"Response time {response_time}s exceeds threshold {thresholds['max_response_time']}s",
                    ValidationSeverity.WARNING
                )
            
            # Check memory usage
            memory_usage = data.get("memory_usage", 0)
            if memory_usage > thresholds.get("max_memory_usage", default_thresholds["max_memory_usage"]):
                result.add_error(
                    "memory_usage",
                    f"Memory usage {memory_usage} bytes exceeds threshold",
                    ValidationSeverity.ERROR
                )
            
            # Check CPU usage
            cpu_usage = data.get("cpu_usage", 0)
            if cpu_usage > thresholds.get("max_cpu_usage", 80.0):
                result.add_error(
                    "cpu_usage",
                    f"CPU usage {cpu_usage}% exceeds threshold {thresholds['max_cpu_usage']}%",
                    ValidationSeverity.WARNING
                )
            
            # Check throughput
            throughput = data.get("throughput", 0)
            if throughput < thresholds.get("min_throughput", 100):
                result.add_error(
                    "throughput",
                    f"Throughput {throughput} ops/s below threshold {thresholds['min_throughput']} ops/s",
                    ValidationSeverity.ERROR
                )
            
            return result
            
        except Exception as e:
            result.add_error("performance_validation_error", f"Performance validation error: {e}", ValidationSeverity.CRITICAL)
            return result
    
    async def validate_security(
        self,
        system_id: str,
        data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate security constraints for data access.
        
        Args:
            system_id: System identifier
            data: Data to validate for security
            user_context: Optional user context for permissions
            
        Returns:
            ValidationResult: Security validation results
        """
        result = ValidationResult(
            is_valid=True,
            system_id=system_id,
            validation_type="security_validation"
        )
        
        try:
            # Check for sensitive data exposure
            sensitive_fields = ["password", "token", "secret", "key", "private"]
            for field, value in data.items():
                if any(sensitive in field.lower() for sensitive in sensitive_fields):
                    if isinstance(value, str) and len(value) > 0:
                        result.add_error(
                            field,
                            f"Sensitive field {field} should not contain raw values",
                            ValidationSeverity.ERROR
                        )
            
            # Check data size limits
            data_size = len(json.dumps(data))
            max_data_size = 10 * 1024 * 1024  # 10MB
            if data_size > max_data_size:
                result.add_error(
                    "data_size",
                    f"Data size {data_size} bytes exceeds security limit {max_data_size} bytes",
                    ValidationSeverity.ERROR
                )
            
            # Validate user permissions if context provided
            if user_context:
                user_role = user_context.get("role", "guest")
                if user_role == "guest" and "admin" in str(data).lower():
                    result.add_error(
                        "permission",
                        "Guest users cannot access admin-related data",
                        ValidationSeverity.ERROR
                    )
            
            return result
            
        except Exception as e:
            result.add_error("security_validation_error", f"Security validation error: {e}", ValidationSeverity.CRITICAL)
            return result
    
    async def register_cross_system_validator(
        self,
        primary_system: str,
        validator_func: Callable
    ) -> bool:
        """Register a cross-system validator function"""
        try:
            validator_key = f"{primary_system}_cross_system"
            self._cross_system_validators[validator_key] = validator_func
            logger.info(f"Registered cross-system validator for {primary_system}")
            return True
        except Exception as e:
            logger.error(f"Failed to register cross-system validator: {e}")
            return False
    
    async def register_business_rule_validator(
        self,
        system_id: str,
        rule_category: str,
        validator_func: Callable
    ) -> bool:
        """Register a business rule validator function"""
        try:
            rule_key = f"{system_id}.{rule_category}"
            self._business_rule_validators[rule_key].append(validator_func)
            logger.info(f"Registered business rule validator for {rule_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to register business rule validator: {e}")
            return False
    
    def get_validation_stats(self, system_id: str) -> Dict[str, Any]:
        """Get validation statistics for a system"""
        return dict(self._validation_stats.get(system_id, {}))
    
    def clear_validation_cache(self, system_id: Optional[str] = None):
        """Clear validation cache for a system or all systems"""
        if system_id:
            # Clear cache entries for specific system
            keys_to_remove = [k for k in self._validation_cache.keys() if k.startswith(f"{system_id}.")]
            for key in keys_to_remove:
                del self._validation_cache[key]
        else:
            # Clear all cache
            self._validation_cache.clear()
    
    async def _validate_referential_integrity(
        self,
        primary_system: str,
        related_system: str,
        data: Dict[str, Any]
    ) -> bool:
        """Validate referential integrity between systems"""
        try:
            # Basic referential integrity checks
            # This is a simplified implementation that can be extended
            
            # Check for foreign key references
            foreign_keys = [k for k in data.keys() if k.endswith("_id") or k.endswith("_ref")]
            
            for fk in foreign_keys:
                fk_value = data.get(fk)
                if fk_value is not None:
                    # Validate that the referenced entity exists (simplified check)
                    if not isinstance(fk_value, (int, str)) or not str(fk_value).strip():
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Referential integrity validation error: {e}")
            return False
    
    async def _call_async_safe(self, callback: Callable, *args, **kwargs) -> Any:
        """Safely call a callback that might be sync or async"""
        try:
            if asyncio.iscoroutinefunction(callback):
                return await callback(*args, **kwargs)
            else:
                return callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Callback failed: {e}")
            return None


# Global instance
validation_manager = ValidationManager()


# Convenience functions
async def register_schema(
    system_id: str,
    schema_name: str,
    schema_class: Type[BaseModel],
    custom_validators: Optional[List[Callable]] = None
) -> bool:
    """Register a Pydantic schema for system validation"""
    return await validation_manager.register_schema(
        system_id, schema_name, schema_class, custom_validators
    )


async def validate_data(
    system_id: str,
    schema_name: str,
    data: Dict[str, Any],
    enable_cache: bool = True
) -> ValidationResult:
    """Validate data against a registered schema"""
    return await validation_manager.validate_data(
        system_id, schema_name, data, enable_cache
    )


async def validate_cross_system(
    primary_system: str,
    related_systems: List[str],
    data: Dict[str, Any],
    consistency_rules: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """Validate data consistency across multiple systems"""
    return await validation_manager.validate_cross_system(
        primary_system, related_systems, data, consistency_rules
    )


async def validate_business_rules(
    system_id: str,
    rule_category: str,
    data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> ValidationResult:
    """Validate business rules for game-specific logic"""
    return await validation_manager.validate_business_rules(
        system_id, rule_category, data, context
    ) 