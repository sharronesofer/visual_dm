"""
Faction Configuration Loader

This module provides utilities for loading and accessing faction system
configuration from JSON files, making the system more modular and configurable.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FactionConfigLoader:
    """Loads and manages faction system configuration from JSON files"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the config loader
        
        Args:
            config_dir: Directory containing config files (defaults to data/systems/faction/)
        """
        if config_dir is None:
            # Default to data/systems/faction directory relative to project root
            # Navigate up from backend/infrastructure/config_loaders/ to project root
            current_dir = Path(__file__).parent.parent.parent.parent
            config_dir = current_dir / "data" / "systems" / "faction"
        
        self.config_dir = Path(config_dir)
        self._configs = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files"""
        config_files = {
            'alliance': 'alliance_config.json',
            'succession': 'succession_config.json', 
            'behavior': 'behavior_config.json'
        }
        
        for config_name, filename in config_files.items():
            self._load_config(config_name, filename)
    
    def _load_config(self, config_name: str, filename: str):
        """Load a specific configuration file
        
        Args:
            config_name: Name to store the config under
            filename: JSON filename to load
        """
        config_path = self.config_dir / filename
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self._configs[config_name] = json.load(f)
                logger.info(f"Loaded {config_name} configuration from {config_path}")
            else:
                logger.warning(f"Configuration file not found: {config_path}")
                self._configs[config_name] = {}
        except Exception as e:
            logger.error(f"Error loading {config_name} config from {config_path}: {e}")
            self._configs[config_name] = {}
    
    def get_alliance_config(self) -> Dict[str, Any]:
        """Get alliance system configuration"""
        return self._configs.get('alliance', {})
    
    def get_succession_config(self) -> Dict[str, Any]:
        """Get succession system configuration"""
        return self._configs.get('succession', {})
    
    def get_behavior_config(self) -> Dict[str, Any]:
        """Get behavior system configuration"""
        return self._configs.get('behavior', {})
    
    def get_alliance_types(self) -> Dict[str, Any]:
        """Get configured alliance types"""
        return self.get_alliance_config().get('alliance_types', {})
    
    def get_betrayal_factors(self) -> Dict[str, Any]:
        """Get betrayal probability factors"""
        return self.get_alliance_config().get('betrayal_factors', {})
    
    def get_succession_types(self) -> Dict[str, Any]:
        """Get succession type configurations"""
        return self.get_succession_config().get('succession_types', {})
    
    def get_behavior_modifiers(self) -> Dict[str, Any]:
        """Get behavior modifier formulas"""
        return self.get_behavior_config().get('behavior_modifiers', {})
    
    def get_personality_archetypes(self) -> Dict[str, Any]:
        """Get predefined personality archetypes"""
        return self.get_behavior_config().get('personality_archetypes', {})
    
    def calculate_behavior_modifier(self, modifier_name: str, attributes: Dict[str, int]) -> float:
        """Calculate a behavior modifier based on hidden attributes
        
        Args:
            modifier_name: Name of the modifier to calculate
            attributes: Dictionary of hidden attributes
            
        Returns:
            Calculated modifier value
        """
        modifiers = self.get_behavior_modifiers()
        
        if modifier_name not in modifiers:
            logger.warning(f"Unknown behavior modifier: {modifier_name}")
            return 0.0
        
        formula = modifiers[modifier_name].get('formula', '')
        
        try:
            # Replace attribute names in formula with actual values
            safe_formula = formula
            for attr_name, value in attributes.items():
                # Validate attribute value is within safe range
                if not isinstance(value, (int, float)) or value < 0 or value > 6:
                    logger.warning(f"Invalid attribute value for {attr_name}: {value}")
                    value = max(0, min(6, int(value)))  # Clamp to safe range
                    
                # Remove 'hidden_' prefix for formula variables
                formula_var = attr_name.replace('hidden_', '')
                safe_formula = safe_formula.replace(formula_var, str(value))
            
            # Use safer evaluation - only allow basic math operations
            # Replace eval() with a restricted math evaluator
            result = self._safe_eval_math_expression(safe_formula)
            return float(result)
            
        except Exception as e:
            logger.error(f"Error calculating behavior modifier '{modifier_name}': {e}")
            return 0.0
    
    def _safe_eval_math_expression(self, expression: str) -> float:
        """Safely evaluate a mathematical expression without allowing code injection
        
        Args:
            expression: Mathematical expression string (e.g., "(3 + 4) / 12.0")
            
        Returns:
            Evaluated result
            
        Raises:
            ValueError: If expression contains unsafe operations
        """
        import re
        import operator
        import ast
        
        # Whitelist allowed characters (numbers, operators, parentheses, decimal points)
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            raise ValueError(f"Expression contains invalid characters: {expression}")
        
        try:
            # Parse the expression into an AST
            node = ast.parse(expression, mode='eval')
            
            # Define allowed operations
            allowed_ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.USub: operator.neg,
                ast.UAdd: operator.pos,
            }
            
            def eval_node(node):
                if isinstance(node, ast.Expression):
                    return eval_node(node.body)
                elif isinstance(node, ast.Num):  # Numbers
                    return node.n
                elif isinstance(node, ast.Constant):  # Python 3.8+ constants
                    return node.value
                elif isinstance(node, ast.BinOp):  # Binary operations
                    left = eval_node(node.left)
                    right = eval_node(node.right)
                    op = allowed_ops.get(type(node.op))
                    if op is None:
                        raise ValueError(f"Operation not allowed: {type(node.op).__name__}")
                    return op(left, right)
                elif isinstance(node, ast.UnaryOp):  # Unary operations
                    operand = eval_node(node.operand)
                    op = allowed_ops.get(type(node.op))
                    if op is None:
                        raise ValueError(f"Operation not allowed: {type(node.op).__name__}")
                    return op(operand)
                else:
                    raise ValueError(f"Node type not allowed: {type(node).__name__}")
            
            result = eval_node(node)
            
            # Ensure result is a valid number
            if not isinstance(result, (int, float)) or not (-1000 <= result <= 1000):
                raise ValueError(f"Result out of safe range: {result}")
                
            return float(result)
            
        except (SyntaxError, ValueError, ZeroDivisionError) as e:
            logger.error(f"Failed to safely evaluate expression '{expression}': {e}")
            return 0.0
    
    def get_alliance_compatibility_factors(self, alliance_type: str) -> Dict[str, float]:
        """Get compatibility factors for a specific alliance type
        
        Args:
            alliance_type: Type of alliance (e.g., 'military', 'economic')
            
        Returns:
            Dictionary of attribute weights for compatibility calculation
        """
        alliance_types = self.get_alliance_types()
        
        if alliance_type not in alliance_types:
            logger.warning(f"Unknown alliance type: {alliance_type}")
            return {}
        
        return alliance_types[alliance_type].get('compatibility_factors', {})
    
    def get_betrayal_probability(self, scenario: str, hidden_attributes: Dict[str, int]) -> float:
        """Calculate betrayal probability for a given scenario and hidden attributes."""
        # Betrayal scenarios are in the alliance config, not behavior config
        betrayal_config = self.get_alliance_config().get("betrayal_factors", {}).get(scenario, {})
        
        if not betrayal_config:
            return 0.0
        
        base_probability = betrayal_config.get("base_probability", 0.0)
        
        # Calculate probability based on hidden attributes and multipliers
        probability = base_probability
        for attr_name, value in hidden_attributes.items():
            # Convert hidden attribute name to multiplier key
            multiplier_key = f"{attr_name.replace('hidden_', '')}_multiplier"
            if multiplier_key in betrayal_config:
                multiplier = betrayal_config[multiplier_key]
                # Normalize attribute value to 0-1 range (assuming 0-6 scale)
                normalized_value = value / 6.0
                probability *= (1.0 + (multiplier - 1.0) * normalized_value)
        
        return max(0.0, min(1.0, probability))
    
    def calculate_alliance_compatibility(self, hidden_attributes: Dict[str, int], alliance_config: Dict) -> float:
        """Calculate how compatible a faction is with a specific alliance type."""
        compatibility_factors = alliance_config.get("compatibility_factors", {})
        base_compatibility = alliance_config.get("base_compatibility", 0.5)
        
        compatibility = base_compatibility
        
        # Handle both naming conventions in our config
        for factor_name, factor_weight in compatibility_factors.items():
            # Convert factor names to hidden attribute names
            attr_name = None
            if "discipline" in factor_name:
                attr_name = "hidden_discipline"
            elif "ambition" in factor_name:
                attr_name = "hidden_ambition"
            elif "integrity" in factor_name:
                attr_name = "hidden_integrity"
            elif "pragmatism" in factor_name:
                attr_name = "hidden_pragmatism"
            elif "resilience" in factor_name:
                attr_name = "hidden_resilience"
            elif "impulsivity" in factor_name:
                attr_name = "hidden_impulsivity"
            
            if attr_name and attr_name in hidden_attributes:
                attribute_value = hidden_attributes[attr_name]
                # Normalize to 0-1 scale (6 is max value)
                normalized_value = attribute_value / 6.0
                compatibility += normalized_value * factor_weight
        
        return max(0.0, min(1.0, compatibility))
    
    def reload_configs(self):
        """Reload all configuration files"""
        self._configs.clear()
        self._load_all_configs()
        logger.info("Reloaded all faction configurations")


# Global instance for easy access
_config_loader = None

def get_faction_config() -> FactionConfigLoader:
    """Get the global faction configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = FactionConfigLoader()
    return _config_loader

def reload_faction_config():
    """Reload the global faction configuration"""
    global _config_loader
    if _config_loader is not None:
        _config_loader.reload_configs()
    else:
        _config_loader = FactionConfigLoader() 