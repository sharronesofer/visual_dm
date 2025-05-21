"""
Validation Mechanisms for Cross-System Data Exchange
- Input validation
- Pre/post-condition checks
- Schema validation using Pydantic
"""
from typing import Any, Dict, Callable, Type
from pydantic import BaseModel, ValidationError

class ValidationManager:
    def __init__(self):
        self._schemas: Dict[str, Type[BaseModel]] = {}
        self._pre_conditions: Dict[str, Callable[[Any], bool]] = {}
        self._post_conditions: Dict[str, Callable[[Any], bool]] = {}

    def register_schema(self, name: str, schema: Type[BaseModel]):
        self._schemas[name] = schema

    def register_pre_condition(self, name: str, check: Callable[[Any], bool]):
        self._pre_conditions[name] = check

    def register_post_condition(self, name: str, check: Callable[[Any], bool]):
        self._post_conditions[name] = check

    def validate(self, name: str, data: Any) -> bool:
        if name in self._schemas:
            try:
                self._schemas[name].model_validate(data)
            except ValidationError as e:
                return False
        if name in self._pre_conditions and not self._pre_conditions[name](data):
            return False
        if name in self._post_conditions and not self._post_conditions[name](data):
            return False
        return True

validation_manager = ValidationManager() 
