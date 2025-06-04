"""
Espionage Configuration Loader

Utility for loading and managing configuration data for the espionage system.
Handles JSON configuration files and provides type-safe access to settings.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class EspionageConfig:
    """Configuration manager for the espionage system"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration loader
        
        Args:
            config_path: Optional path to config file. If None, uses default location.
        """
        if config_path is None:
            # Default to config file in data directory
            project_root = Path(__file__).parent.parent.parent.parent
            config_path = project_root / "data" / "systems" / "espionage" / "espionage_config.json"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Espionage config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in espionage config: {e}")
    
    def reload_config(self) -> None:
        """Reload configuration from file"""
        self._load_config()
    
    # Operation Success Rates
    def get_operation_success_rate(self, operation_type: str) -> float:
        """Get base success rate for an operation type"""
        rates = self._config.get("operation_success_rates", {})
        return rates.get(operation_type, 0.5)  # Default 50% if not found
    
    def get_all_operation_success_rates(self) -> Dict[str, float]:
        """Get all operation success rates"""
        return self._config.get("operation_success_rates", {})
    
    # Operation Damage
    def get_operation_damage(self, operation_type: str) -> float:
        """Get base damage for an operation type"""
        damage = self._config.get("operation_damage", {})
        return damage.get(operation_type, 0.0)
    
    def get_all_operation_damage(self) -> Dict[str, float]:
        """Get all operation damage values"""
        return self._config.get("operation_damage", {})
    
    # Intelligence Rewards
    def get_intelligence_rewards(self, operation_type: str) -> list[str]:
        """Get intelligence types that can be gained from an operation"""
        rewards = self._config.get("intelligence_rewards", {})
        return rewards.get(operation_type, [])
    
    def get_all_intelligence_rewards(self) -> Dict[str, list[str]]:
        """Get all intelligence reward mappings"""
        return self._config.get("intelligence_rewards", {})
    
    # Burn Risk
    def get_burn_risk_multiplier(self, operation_type: str) -> float:
        """Get burn risk multiplier for an operation type"""
        multipliers = self._config.get("burn_risk_multipliers", {})
        return multipliers.get(operation_type, 0.15)  # Default 15% if not found
    
    def get_all_burn_risk_multipliers(self) -> Dict[str, float]:
        """Get all burn risk multipliers"""
        return self._config.get("burn_risk_multipliers", {})
    
    # Risk Thresholds
    def get_risk_threshold(self, threshold_type: str) -> float:
        """Get a risk threshold value"""
        thresholds = self._config.get("risk_thresholds", {})
        defaults = {
            "agent_retirement": 0.8,
            "operation_restriction": 0.6,
            "heightened_security": 0.4,
            "detection_consequence": 0.7
        }
        return thresholds.get(threshold_type, defaults.get(threshold_type, 0.5))
    
    def get_all_risk_thresholds(self) -> Dict[str, float]:
        """Get all risk thresholds"""
        return self._config.get("risk_thresholds", {})
    
    # Agent Effectiveness
    def get_agent_effectiveness(self, agent_role: str, operation_type: str) -> float:
        """Get effectiveness multiplier for an agent role on a specific operation"""
        effectiveness = self._config.get("agent_effectiveness", {})
        role_data = effectiveness.get(agent_role, {})
        return role_data.get(operation_type, 1.0)  # Default 100% effectiveness
    
    def get_agent_role_effectiveness(self, agent_role: str) -> Dict[str, float]:
        """Get all effectiveness multipliers for a specific agent role"""
        effectiveness = self._config.get("agent_effectiveness", {})
        return effectiveness.get(agent_role, {})
    
    def get_all_agent_effectiveness(self) -> Dict[str, Dict[str, float]]:
        """Get all agent effectiveness data"""
        return self._config.get("agent_effectiveness", {})
    
    # Calculation Parameters
    def get_calculation_parameter(self, parameter_name: str) -> float:
        """Get a calculation parameter value"""
        params = self._config.get("calculation_parameters", {})
        defaults = {
            "agent_skill_bonus_multiplier": 0.1,
            "skill_modifier_base": 5.0,
            "skill_modifier_multiplier": 0.05,
            "security_modifier_base": 5.0,
            "security_modifier_multiplier": 0.04,
            "expertise_bonus_multiplier": 0.02,
            "success_threshold_for_intelligence": 0.3,
            "max_damage_multiplier": 0.5,
            "detection_bonus_multiplier": 0.2,
            "heat_bonus_multiplier": 0.02
        }
        return params.get(parameter_name, defaults.get(parameter_name, 1.0))
    
    def get_all_calculation_parameters(self) -> Dict[str, float]:
        """Get all calculation parameters"""
        return self._config.get("calculation_parameters", {})
    
    # Validation Methods
    def validate_config(self) -> Dict[str, list[str]]:
        """Validate configuration and return any issues found"""
        issues: Dict[str, list[str]] = {}
        
        # Check required sections
        required_sections = [
            "operation_success_rates",
            "operation_damage",
            "intelligence_rewards",
            "burn_risk_multipliers",
            "risk_thresholds",
            "agent_effectiveness",
            "calculation_parameters"
        ]
        
        for section in required_sections:
            if section not in self._config:
                if "missing_sections" not in issues:
                    issues["missing_sections"] = []
                issues["missing_sections"].append(section)
        
        # Validate success rates are between 0 and 1
        success_rates = self._config.get("operation_success_rates", {})
        for op_type, rate in success_rates.items():
            if not (0.0 <= rate <= 1.0):
                if "invalid_success_rates" not in issues:
                    issues["invalid_success_rates"] = []
                issues["invalid_success_rates"].append(f"{op_type}: {rate}")
        
        # Validate burn risk multipliers are non-negative
        burn_risks = self._config.get("burn_risk_multipliers", {})
        for op_type, risk in burn_risks.items():
            if risk < 0.0:
                if "negative_burn_risks" not in issues:
                    issues["negative_burn_risks"] = []
                issues["negative_burn_risks"].append(f"{op_type}: {risk}")
        
        # Validate risk thresholds are between 0 and 1
        thresholds = self._config.get("risk_thresholds", {})
        for threshold_type, value in thresholds.items():
            if not (0.0 <= value <= 1.0):
                if "invalid_risk_thresholds" not in issues:
                    issues["invalid_risk_thresholds"] = []
                issues["invalid_risk_thresholds"].append(f"{threshold_type}: {value}")
        
        return issues


# Global configuration instance
_config_instance: Optional[EspionageConfig] = None


def get_espionage_config() -> EspionageConfig:
    """Get the global espionage configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = EspionageConfig()
    return _config_instance


def reload_espionage_config() -> None:
    """Reload the global configuration from file"""
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload_config()
    else:
        _config_instance = EspionageConfig() 