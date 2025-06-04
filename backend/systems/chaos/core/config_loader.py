"""
Chaos Configuration Business Logic

Pure business logic for chaos system configuration without infrastructure concerns.
Uses infrastructure configuration loader for file operations.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Import infrastructure for file operations
from backend.infrastructure.config.chaos_config_loader import ConfigurationLoader, EventTypeConfig

@dataclass
class ChaosConfigurationManager:
    """
    Business logic for chaos system configuration management.
    
    Handles configuration validation, defaults, and business rules
    without any file I/O or infrastructure concerns.
    """
    
    def __init__(self, config_loader: Optional[ConfigurationLoader] = None):
        """Initialize with configuration loader dependency injection"""
        self.config_loader = config_loader or ConfigurationLoader()
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize configuration from loader"""
        success = self.config_loader.load_all_configurations()
        self.is_initialized = success
        return success
    
    def get_event_type_config(self, event_type: str) -> Optional[EventTypeConfig]:
        """Get configuration for a specific event type"""
        return self.config_loader.get_event_type_config(event_type)
    
    def get_all_event_types(self) -> Dict[str, EventTypeConfig]:
        """Get all event type configurations"""
        return self.config_loader.get_all_event_types()
    
    def get_event_probabilities(self) -> Dict[str, float]:
        """Get base probabilities for all event types"""
        return self.config_loader.get_event_probabilities()
    
    def get_event_cooldowns(self) -> Dict[str, float]:
        """Get cooldown seconds for all event types"""
        return self.config_loader.get_event_cooldowns()
    
    def get_warning_templates(self, event_type: str) -> Dict[str, List[str]]:
        """Get warning phase templates for an event type"""
        return self.config_loader.get_warning_templates(event_type)
    
    def get_cascade_triggers(self, event_type: str) -> List[str]:
        """Get potential cascade triggers for an event type"""
        return self.config_loader.get_cascade_triggers(event_type)
    
    def get_global_setting(self, setting_path: str, default: Any = None) -> Any:
        """Get a global setting value using dot notation"""
        return self.config_loader.get_global_setting(setting_path, default)
    
    def validate_event_configuration(self, event_type: str) -> List[str]:
        """
        Validate configuration for a specific event type.
        
        Returns:
            List of validation issues
        """
        issues = []
        config = self.get_event_type_config(event_type)
        
        if not config:
            issues.append(f"Event type '{event_type}' not found in configuration")
            return issues
        
        # Business logic validation
        if config.base_probability < 0.0 or config.base_probability > 1.0:
            issues.append(f"Event '{event_type}': Invalid probability {config.base_probability}")
        
        if config.severity_scaling <= 0.0:
            issues.append(f"Event '{event_type}': Severity scaling must be positive")
        
        if config.cooldown_hours < 0.0:
            issues.append(f"Event '{event_type}': Cooldown cannot be negative")
        
        if config.max_concurrent <= 0:
            issues.append(f"Event '{event_type}': Max concurrent must be positive")
        
        # Validate cascade triggers exist
        all_event_types = set(self.get_all_event_types().keys())
        for trigger in config.cascade_triggers:
            if trigger not in all_event_types:
                issues.append(f"Event '{event_type}': Unknown cascade trigger '{trigger}'")
        
        return issues
    
    def validate_all_configurations(self) -> List[str]:
        """Validate all event configurations"""
        all_issues = []
        
        for event_type in self.get_all_event_types().keys():
            issues = self.validate_event_configuration(event_type)
            all_issues.extend(issues)
        
        # Validate global configuration coherence
        probabilities = self.get_event_probabilities()
        if probabilities:
            total_probability = sum(probabilities.values())
            if total_probability > 1.0:
                all_issues.append(f"Total event probabilities ({total_probability:.3f}) exceed 1.0")
        
        return all_issues
    
    def get_effective_probability(self, event_type: str, chaos_level: float) -> float:
        """
        Calculate effective probability for an event given current chaos level.
        
        Business logic for probability scaling.
        """
        config = self.get_event_type_config(event_type)
        if not config:
            return 0.0
        
        # Apply chaos level scaling to base probability
        effective_probability = config.base_probability * (1.0 + chaos_level * config.severity_scaling)
        
        # Ensure probability stays within valid range
        return min(max(effective_probability, 0.0), 1.0)
    
    def get_event_severity_modifier(self, event_type: str, current_pressure: float) -> float:
        """
        Calculate severity modifier based on current pressure.
        
        Business logic for severity scaling.
        """
        config = self.get_event_type_config(event_type)
        if not config:
            return 1.0
        
        # Apply pressure-based severity modification
        pressure_factor = min(current_pressure / 0.75, 1.0)  # Cap at 75% pressure
        severity_modifier = 1.0 + (pressure_factor * config.severity_scaling)
        
        return max(severity_modifier, 0.1)  # Minimum 10% severity
    
    def can_trigger_event(self, event_type: str, current_pressure: Dict[str, float]) -> bool:
        """
        Determine if an event can be triggered based on pressure requirements.
        
        Business logic for event triggering conditions.
        """
        config = self.get_event_type_config(event_type)
        if not config:
            return False
        
        # Check pressure requirements
        for pressure_source, required_level in config.pressure_requirements.items():
            current_level = current_pressure.get(pressure_source, 0.0)
            if current_level < required_level:
                return False
        
        return True
    
    def get_cascade_probability(self, primary_event: str, secondary_event: str) -> float:
        """
        Calculate probability of cascade event triggering.
        
        Business logic for cascade event probability.
        """
        primary_config = self.get_event_type_config(primary_event)
        secondary_config = self.get_event_type_config(secondary_event)
        
        if not primary_config or not secondary_config:
            return 0.0
        
        if secondary_event not in primary_config.cascade_triggers:
            return 0.0
        
        # Base cascade probability (configurable)
        base_cascade_probability = self.get_global_setting('cascade.base_probability', 0.3)
        
        # Modify based on secondary event's base probability
        cascade_probability = base_cascade_probability * secondary_config.base_probability
        
        return min(cascade_probability, 0.8)  # Cap at 80%
    
    def get_event_priorities(self) -> Dict[str, int]:
        """
        Get event priorities for scheduling.
        
        Business logic for event prioritization.
        """
        priorities = {}
        
        for event_type, config in self.get_all_event_types().items():
            # Calculate priority based on severity scaling and probability
            priority_score = int(config.severity_scaling * config.base_probability * 100)
            priorities[event_type] = priority_score
        
        return priorities
    
    def reload_configuration(self) -> bool:
        """Reload configuration from infrastructure"""
        return self.config_loader.reload_configurations()
    
    def save_configuration(self) -> bool:
        """Save configuration via infrastructure"""
        return self.config_loader.save_configurations() 