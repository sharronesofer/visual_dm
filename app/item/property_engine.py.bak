import json
from typing import Any, Dict
from app.item.models import Item, ItemProperty, PropertyDefinition

class PropertyCalculator:
    def __init__(self, item: Item):
        self.item = item
        self.properties = {p.property_definition.name: p for p in item.properties if p.is_active}

    def get_property(self, name: str) -> Any:
        prop = self.properties.get(name)
        if not prop:
            return None
        return self._convert_value(prop.value, prop.property_definition.data_type)

    def calculate_stat(self, name: str, context: Dict = None) -> Any:
        prop = self.properties.get(name)
        if not prop:
            return None
        definition = prop.property_definition
        if definition.formula:
            return self._evaluate_formula(definition.formula, context or {})
        return self._convert_value(prop.value, definition.data_type)

    def _convert_value(self, value: str, data_type: str) -> Any:
        if data_type == 'int':
            return int(value)
        if data_type == 'float':
            return float(value)
        if data_type == 'bool':
            return value.lower() in ('1', 'true', 'yes')
        if data_type == 'json':
            return json.loads(value)
        return value

    def _evaluate_formula(self, formula: str, context: Dict) -> Any:
        # WARNING: Use a safe eval method in production. Here, use eval with limited globals for demo.
        safe_globals = {**context, **{k: self.get_property(k) for k in self.properties}}
        try:
            return eval(formula, {"__builtins__": {}}, safe_globals)
        except Exception:
            return None 