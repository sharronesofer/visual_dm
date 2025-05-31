"""
Configuration Manager

Manages chaos system configuration with real-time updates and validation.
Handles configuration persistence, backup, and dynamic parameter adjustment.
"""

import asyncio
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from threading import Lock

from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


class ConfigurationType(Enum):
    """Types of configuration parameters"""
    PRESSURE_WEIGHTS = "pressure_weights"
    CHAOS_THRESHOLDS = "chaos_thresholds"
    EVENT_PROBABILITIES = "event_probabilities"
    MITIGATION_EFFECTIVENESS = "mitigation_effectiveness"
    TEMPORAL_FACTORS = "temporal_factors"
    PERFORMANCE_SETTINGS = "performance_settings"
    MONITORING_SETTINGS = "monitoring_settings"
    INTEGRATION_SETTINGS = "integration_settings"


@dataclass
class ConfigurationChange:
    """Record of a configuration change"""
    timestamp: datetime
    change_id: str
    configuration_type: str
    parameter_name: str
    old_value: Any
    new_value: Any
    changed_by: str = "system"
    reason: str = ""
    validation_passed: bool = True
    applied_successfully: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'change_id': self.change_id,
            'configuration_type': self.configuration_type,
            'parameter_name': self.parameter_name,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'reason': self.reason,
            'validation_passed': self.validation_passed,
            'applied_successfully': self.applied_successfully
        }


@dataclass
class ConfigurationValidation:
    """Validation rules for configuration parameters"""
    parameter_name: str
    value_type: type
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable[[Any], bool]] = None
    description: str = ""
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        """Validate a configuration value"""
        try:
            # Type check
            if not isinstance(value, self.value_type):
                return False, f"Expected {self.value_type.__name__}, got {type(value).__name__}"
            
            # Range check for numeric values
            if self.min_value is not None and value < self.min_value:
                return False, f"Value {value} is below minimum {self.min_value}"
            
            if self.max_value is not None and value > self.max_value:
                return False, f"Value {value} is above maximum {self.max_value}"
            
            # Allowed values check
            if self.allowed_values is not None and value not in self.allowed_values:
                return False, f"Value {value} not in allowed values: {self.allowed_values}"
            
            # Custom validation
            if self.custom_validator and not self.custom_validator(value):
                return False, "Custom validation failed"
            
            return True, "Valid"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class ConfigurationManager:
    """
    Dynamic configuration management for the chaos system
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # Configuration storage
        self.current_configuration: Dict[str, Any] = {}
        self.configuration_history: List[ConfigurationChange] = []
        self.validation_rules: Dict[str, ConfigurationValidation] = {}
        
        # Persistence settings
        self.config_dir = Path("config/chaos")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "dynamic_config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Change tracking
        self.pending_changes: Dict[str, Any] = {}
        self.auto_apply_enabled = True
        self.validation_enabled = True
        
        # Thread safety
        self.config_lock = Lock()
        
        # Change listeners
        self.change_listeners: Dict[str, List[Callable]] = {}
        
        # Performance tracking
        self.configuration_metrics = {
            'changes_applied': 0,
            'changes_rejected': 0,
            'validations_performed': 0,
            'rollbacks_performed': 0,
            'auto_optimizations': 0
        }
        
        logger.info("Configuration Manager initialized")
    
    async def initialize(self) -> None:
        """Initialize the configuration manager"""
        try:
            # Set up validation rules
            self._setup_validation_rules()
            
            # Load initial configuration
            await self._load_configuration()
            
            # Initialize from chaos config
            self._initialize_from_chaos_config()
            
            # Start background optimization if enabled
            if hasattr(self.config, 'enable_auto_optimization') and self.config.enable_auto_optimization:
                asyncio.create_task(self._background_optimization())
            
            logger.info("Configuration Manager initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Configuration Manager: {e}")
            raise
    
    def _setup_validation_rules(self) -> None:
        """Set up validation rules for all configuration parameters"""
        
        # Pressure weight validations
        self.validation_rules.update({
            'pressure_weights.faction_stability': ConfigurationValidation(
                'pressure_weights.faction_stability', float, 0.0, 2.0,
                description="Weight for faction stability pressure"
            ),
            'pressure_weights.economic_health': ConfigurationValidation(
                'pressure_weights.economic_health', float, 0.0, 2.0,
                description="Weight for economic health pressure"
            ),
            'pressure_weights.diplomatic_tension': ConfigurationValidation(
                'pressure_weights.diplomatic_tension', float, 0.0, 2.0,
                description="Weight for diplomatic tension pressure"
            ),
            'pressure_weights.regional_stability': ConfigurationValidation(
                'pressure_weights.regional_stability', float, 0.0, 2.0,
                description="Weight for regional stability pressure"
            ),
            'pressure_weights.population_morale': ConfigurationValidation(
                'pressure_weights.population_morale', float, 0.0, 2.0,
                description="Weight for population morale pressure"
            ),
            'pressure_weights.npc_stress': ConfigurationValidation(
                'pressure_weights.npc_stress', float, 0.0, 2.0,
                description="Weight for NPC stress pressure"
            )
        })
        
        # Chaos threshold validations
        self.validation_rules.update({
            'chaos_thresholds.dormant_max': ConfigurationValidation(
                'chaos_thresholds.dormant_max', float, 0.0, 1.0,
                description="Maximum chaos score for dormant level"
            ),
            'chaos_thresholds.stirring_max': ConfigurationValidation(
                'chaos_thresholds.stirring_max', float, 0.0, 1.0,
                description="Maximum chaos score for stirring level"
            ),
            'chaos_thresholds.rising_max': ConfigurationValidation(
                'chaos_thresholds.rising_max', float, 0.0, 1.0,
                description="Maximum chaos score for rising level"
            ),
            'chaos_thresholds.critical_max': ConfigurationValidation(
                'chaos_thresholds.critical_max', float, 0.0, 1.0,
                description="Maximum chaos score for critical level"
            )
        })
        
        # Event probability validations
        event_types = [
            'political_upheaval', 'natural_disaster', 'economic_collapse',
            'military_conflict', 'social_unrest', 'disease_outbreak',
            'resource_scarcity', 'technological_failure', 'divine_intervention',
            'magical_anomaly', 'environmental_crisis', 'cultural_shift',
            'infrastructure_failure'
        ]
        
        for event_type in event_types:
            for severity in ['minor', 'moderate', 'severe', 'catastrophic']:
                param_name = f'event_probabilities.{event_type}.{severity}'
                self.validation_rules[param_name] = ConfigurationValidation(
                    param_name, float, 0.0, 1.0,
                    description=f"Probability of {severity} {event_type} events"
                )
        
        # Performance setting validations
        self.validation_rules.update({
            'performance.pressure_collection_interval': ConfigurationValidation(
                'performance.pressure_collection_interval', int, 1, 300,
                description="Interval for pressure collection in seconds"
            ),
            'performance.chaos_calculation_interval': ConfigurationValidation(
                'performance.chaos_calculation_interval', int, 1, 60,
                description="Interval for chaos calculation in seconds"
            ),
            'performance.event_processing_batch_size': ConfigurationValidation(
                'performance.event_processing_batch_size', int, 1, 100,
                description="Batch size for event processing"
            ),
            'performance.cache_ttl_seconds': ConfigurationValidation(
                'performance.cache_ttl_seconds', int, 10, 3600,
                description="Cache TTL in seconds"
            ),
            'performance.max_concurrent_events': ConfigurationValidation(
                'performance.max_concurrent_events', int, 1, 50,
                description="Maximum concurrent events"
            )
        })
        
        # Temporal factor validations
        self.validation_rules.update({
            'temporal_factors.pressure_decay_rate': ConfigurationValidation(
                'temporal_factors.pressure_decay_rate', float, 0.0, 1.0,
                description="Rate of pressure decay over time"
            ),
            'temporal_factors.chaos_momentum_factor': ConfigurationValidation(
                'temporal_factors.chaos_momentum_factor', float, 0.0, 2.0,
                description="Factor for chaos momentum"
            ),
            'temporal_factors.mitigation_decay_rate': ConfigurationValidation(
                'temporal_factors.mitigation_decay_rate', float, 0.0, 1.0,
                description="Rate of mitigation effectiveness decay"
            )
        })
    
    def _initialize_from_chaos_config(self) -> None:
        """Initialize current configuration from ChaosConfig"""
        try:
            with self.config_lock:
                # Extract configuration from ChaosConfig
                self.current_configuration.update({
                    'pressure_weights': {
                        'faction_stability': self.config.pressure_weights.get('faction_stability', 1.0),
                        'economic_health': self.config.pressure_weights.get('economic_health', 1.0),
                        'diplomatic_tension': self.config.pressure_weights.get('diplomatic_tension', 1.0),
                        'regional_stability': self.config.pressure_weights.get('regional_stability', 1.0),
                        'population_morale': self.config.pressure_weights.get('population_morale', 1.0),
                        'npc_stress': self.config.pressure_weights.get('npc_stress', 1.0)
                    },
                    'chaos_thresholds': {
                        'dormant_max': self.config.chaos_thresholds.get('dormant_max', 0.2),
                        'stirring_max': self.config.chaos_thresholds.get('stirring_max', 0.4),
                        'rising_max': self.config.chaos_thresholds.get('rising_max', 0.6),
                        'critical_max': self.config.chaos_thresholds.get('critical_max', 0.8)
                    },
                    'performance': {
                        'pressure_collection_interval': getattr(self.config, 'pressure_collection_interval', 30),
                        'chaos_calculation_interval': getattr(self.config, 'chaos_calculation_interval', 10),
                        'event_processing_batch_size': getattr(self.config, 'event_processing_batch_size', 10),
                        'cache_ttl_seconds': getattr(self.config, 'cache_ttl_seconds', 300),
                        'max_concurrent_events': getattr(self.config, 'max_concurrent_events', 5)
                    },
                    'temporal_factors': {
                        'pressure_decay_rate': getattr(self.config, 'pressure_decay_rate', 0.1),
                        'chaos_momentum_factor': getattr(self.config, 'chaos_momentum_factor', 1.2),
                        'mitigation_decay_rate': getattr(self.config, 'mitigation_decay_rate', 0.05)
                    }
                })
                
                logger.debug("Configuration initialized from ChaosConfig")
                
        except Exception as e:
            logger.error(f"Error initializing configuration: {e}")
    
    def get_configuration(self, path: Optional[str] = None) -> Any:
        """Get configuration value(s) by path"""
        try:
            with self.config_lock:
                if path is None:
                    return self.current_configuration.copy()
                
                # Navigate nested path
                parts = path.split('.')
                value = self.current_configuration
                
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        raise KeyError(f"Configuration path not found: {path}")
                
                return value
                
        except Exception as e:
            logger.error(f"Error getting configuration {path}: {e}")
            return None
    
    async def set_configuration(self, path: str, value: Any, changed_by: str = "system",
                              reason: str = "", validate: bool = True) -> bool:
        """Set a configuration value"""
        try:
            # Generate change ID
            change_id = f"config_{int(datetime.now().timestamp() * 1000000)}"
            
            # Get old value
            old_value = self.get_configuration(path)
            
            # Create change record
            change = ConfigurationChange(
                timestamp=datetime.now(),
                change_id=change_id,
                configuration_type=self._get_configuration_type(path),
                parameter_name=path,
                old_value=old_value,
                new_value=value,
                changed_by=changed_by,
                reason=reason
            )
            
            # Validate if enabled
            if validate and self.validation_enabled:
                validation_result = self._validate_configuration_change(path, value)
                change.validation_passed = validation_result[0]
                
                if not validation_result[0]:
                    logger.warning(f"Configuration validation failed for {path}: {validation_result[1]}")
                    self.configuration_metrics['changes_rejected'] += 1
                    self.configuration_history.append(change)
                    return False
                
                self.configuration_metrics['validations_performed'] += 1
            
            # Apply change
            success = await self._apply_configuration_change(path, value)
            change.applied_successfully = success
            
            if success:
                # Update configuration
                with self.config_lock:
                    self._set_nested_value(self.current_configuration, path, value)
                
                # Notify listeners
                await self._notify_change_listeners(path, value, old_value)
                
                # Save to persistence
                await self._save_configuration()
                
                self.configuration_metrics['changes_applied'] += 1
                logger.info(f"Configuration changed: {path} = {value} (by {changed_by})")
                
            else:
                self.configuration_metrics['changes_rejected'] += 1
                logger.error(f"Failed to apply configuration change: {path} = {value}")
            
            # Record change
            self.configuration_history.append(change)
            
            # Keep history size manageable
            if len(self.configuration_history) > 1000:
                self.configuration_history = self.configuration_history[-1000:]
            
            return success
            
        except Exception as e:
            logger.error(f"Error setting configuration {path}: {e}")
            return False
    
    def _get_configuration_type(self, path: str) -> str:
        """Determine configuration type from path"""
        if path.startswith('pressure_weights'):
            return ConfigurationType.PRESSURE_WEIGHTS.value
        elif path.startswith('chaos_thresholds'):
            return ConfigurationType.CHAOS_THRESHOLDS.value
        elif path.startswith('event_probabilities'):
            return ConfigurationType.EVENT_PROBABILITIES.value
        elif path.startswith('performance'):
            return ConfigurationType.PERFORMANCE_SETTINGS.value
        elif path.startswith('temporal_factors'):
            return ConfigurationType.TEMPORAL_FACTORS.value
        else:
            return "unknown"
    
    def _validate_configuration_change(self, path: str, value: Any) -> Tuple[bool, str]:
        """Validate a configuration change"""
        try:
            # Check if validation rule exists
            if path in self.validation_rules:
                return self.validation_rules[path].validate(value)
            
            # Default validation for unknown parameters
            logger.warning(f"No validation rule found for {path}, allowing change")
            return True, "No validation rule"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    async def _apply_configuration_change(self, path: str, value: Any) -> bool:
        """Apply a configuration change to the system"""
        try:
            # Update the chaos config object if it's a known parameter
            if hasattr(self.config, 'update_parameter'):
                return await self.config.update_parameter(path, value)
            
            # For parameters that don't have direct config updates, 
            # the change will be applied through the configuration getter
            return True
            
        except Exception as e:
            logger.error(f"Error applying configuration change {path}: {e}")
            return False
    
    def _set_nested_value(self, config_dict: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested value in configuration dictionary"""
        parts = path.split('.')
        current = config_dict
        
        # Navigate to parent
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set final value
        current[parts[-1]] = value
    
    def register_change_listener(self, path_pattern: str, callback: Callable) -> None:
        """Register a callback for configuration changes"""
        if path_pattern not in self.change_listeners:
            self.change_listeners[path_pattern] = []
        
        self.change_listeners[path_pattern].append(callback)
        logger.debug(f"Registered change listener for {path_pattern}")
    
    async def _notify_change_listeners(self, path: str, new_value: Any, old_value: Any) -> None:
        """Notify registered listeners of configuration changes"""
        try:
            for pattern, callbacks in self.change_listeners.items():
                # Simple pattern matching (could be enhanced)
                if pattern == path or path.startswith(pattern):
                    for callback in callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(path, new_value, old_value)
                            else:
                                callback(path, new_value, old_value)
                        except Exception as e:
                            logger.error(f"Error in change listener callback: {e}")
                            
        except Exception as e:
            logger.error(f"Error notifying change listeners: {e}")
    
    async def create_configuration_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of current configuration"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_file = self.backup_dir / f"{backup_name}.json"
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'configuration': self.current_configuration,
                'metadata': {
                    'changes_applied': self.configuration_metrics['changes_applied'],
                    'backup_reason': 'manual_backup'
                }
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Configuration backup created: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Error creating configuration backup: {e}")
            return ""
    
    async def restore_configuration_backup(self, backup_name: str, 
                                         changed_by: str = "system") -> bool:
        """Restore configuration from backup"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.json"
            
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False
            
            # Create current backup before restore
            await self.create_configuration_backup("pre_restore_backup")
            
            # Load backup data
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            restored_config = backup_data['configuration']
            
            # Apply restored configuration
            with self.config_lock:
                self.current_configuration = restored_config
            
            # Record rollback
            change = ConfigurationChange(
                timestamp=datetime.now(),
                change_id=f"restore_{int(datetime.now().timestamp() * 1000000)}",
                configuration_type="full_restore",
                parameter_name="all",
                old_value="current_configuration",
                new_value=f"backup_{backup_name}",
                changed_by=changed_by,
                reason=f"Restored from backup: {backup_name}",
                validation_passed=True,
                applied_successfully=True
            )
            
            self.configuration_history.append(change)
            self.configuration_metrics['rollbacks_performed'] += 1
            
            # Save current configuration
            await self._save_configuration()
            
            logger.info(f"Configuration restored from backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring configuration backup: {e}")
            return False
    
    async def optimize_configuration(self, optimization_type: str = "performance") -> Dict[str, Any]:
        """Automatically optimize configuration based on system performance"""
        try:
            logger.info(f"Starting configuration optimization: {optimization_type}")
            
            optimization_results = {
                'optimization_type': optimization_type,
                'timestamp': datetime.now().isoformat(),
                'changes_made': [],
                'performance_improvement': 0.0,
                'success': False
            }
            
            if optimization_type == "performance":
                changes = await self._optimize_for_performance()
                optimization_results['changes_made'] = changes
            
            elif optimization_type == "stability":
                changes = await self._optimize_for_stability()
                optimization_results['changes_made'] = changes
            
            elif optimization_type == "balance":
                changes = await self._optimize_for_balance()
                optimization_results['changes_made'] = changes
            
            else:
                logger.warning(f"Unknown optimization type: {optimization_type}")
                return optimization_results
            
            if changes:
                self.configuration_metrics['auto_optimizations'] += 1
                optimization_results['success'] = True
                logger.info(f"Configuration optimization complete: {len(changes)} changes made")
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error during configuration optimization: {e}")
            return {'error': str(e)}
    
    async def _optimize_for_performance(self) -> List[Dict[str, Any]]:
        """Optimize configuration for better performance"""
        changes = []
        
        try:
            # Reduce pressure collection frequency if system is under load
            current_interval = self.get_configuration('performance.pressure_collection_interval')
            if current_interval < 60:  # Less than 1 minute
                new_interval = min(60, current_interval * 1.5)
                success = await self.set_configuration(
                    'performance.pressure_collection_interval',
                    int(new_interval),
                    changed_by="auto_optimizer",
                    reason="Performance optimization - reduce pressure collection frequency"
                )
                if success:
                    changes.append({
                        'parameter': 'performance.pressure_collection_interval',
                        'old_value': current_interval,
                        'new_value': int(new_interval),
                        'reason': 'Reduce system load'
                    })
            
            # Increase cache TTL if hit rate is low
            current_ttl = self.get_configuration('performance.cache_ttl_seconds')
            if current_ttl < 600:  # Less than 10 minutes
                new_ttl = min(600, current_ttl * 2)
                success = await self.set_configuration(
                    'performance.cache_ttl_seconds',
                    int(new_ttl),
                    changed_by="auto_optimizer",
                    reason="Performance optimization - increase cache TTL"
                )
                if success:
                    changes.append({
                        'parameter': 'performance.cache_ttl_seconds',
                        'old_value': current_ttl,
                        'new_value': int(new_ttl),
                        'reason': 'Improve cache efficiency'
                    })
            
            return changes
            
        except Exception as e:
            logger.error(f"Error in performance optimization: {e}")
            return changes
    
    async def _optimize_for_stability(self) -> List[Dict[str, Any]]:
        """Optimize configuration for better system stability"""
        changes = []
        
        try:
            # Reduce maximum concurrent events if system is unstable
            current_max = self.get_configuration('performance.max_concurrent_events')
            if current_max > 3:
                new_max = max(3, current_max - 1)
                success = await self.set_configuration(
                    'performance.max_concurrent_events',
                    new_max,
                    changed_by="auto_optimizer",
                    reason="Stability optimization - reduce concurrent events"
                )
                if success:
                    changes.append({
                        'parameter': 'performance.max_concurrent_events',
                        'old_value': current_max,
                        'new_value': new_max,
                        'reason': 'Improve system stability'
                    })
            
            # Increase pressure decay rate to reduce chaos buildup
            current_decay = self.get_configuration('temporal_factors.pressure_decay_rate')
            if current_decay < 0.15:
                new_decay = min(0.15, current_decay * 1.2)
                success = await self.set_configuration(
                    'temporal_factors.pressure_decay_rate',
                    new_decay,
                    changed_by="auto_optimizer",
                    reason="Stability optimization - increase pressure decay"
                )
                if success:
                    changes.append({
                        'parameter': 'temporal_factors.pressure_decay_rate',
                        'old_value': current_decay,
                        'new_value': new_decay,
                        'reason': 'Reduce chaos buildup'
                    })
            
            return changes
            
        except Exception as e:
            logger.error(f"Error in stability optimization: {e}")
            return changes
    
    async def _optimize_for_balance(self) -> List[Dict[str, Any]]:
        """Optimize configuration for balanced gameplay"""
        changes = []
        
        try:
            # Balance pressure weights if any are too dominant
            pressure_weights = self.get_configuration('pressure_weights')
            total_weight = sum(pressure_weights.values())
            avg_weight = total_weight / len(pressure_weights)
            
            for source, weight in pressure_weights.items():
                if weight > avg_weight * 1.5:  # Too high
                    new_weight = avg_weight * 1.2
                    success = await self.set_configuration(
                        f'pressure_weights.{source}',
                        new_weight,
                        changed_by="auto_optimizer",
                        reason="Balance optimization - reduce dominant pressure weight"
                    )
                    if success:
                        changes.append({
                            'parameter': f'pressure_weights.{source}',
                            'old_value': weight,
                            'new_value': new_weight,
                            'reason': 'Balance pressure weights'
                        })
                
                elif weight < avg_weight * 0.5:  # Too low
                    new_weight = avg_weight * 0.8
                    success = await self.set_configuration(
                        f'pressure_weights.{source}',
                        new_weight,
                        changed_by="auto_optimizer",
                        reason="Balance optimization - increase low pressure weight"
                    )
                    if success:
                        changes.append({
                            'parameter': f'pressure_weights.{source}',
                            'old_value': weight,
                            'new_value': new_weight,
                            'reason': 'Balance pressure weights'
                        })
            
            return changes
            
        except Exception as e:
            logger.error(f"Error in balance optimization: {e}")
            return changes
    
    async def _background_optimization(self) -> None:
        """Background task for automatic optimization"""
        try:
            while True:
                await asyncio.sleep(3600)  # Run every hour
                
                # Perform automatic optimization
                await self.optimize_configuration("performance")
                
        except asyncio.CancelledError:
            logger.info("Background optimization cancelled")
        except Exception as e:
            logger.error(f"Error in background optimization: {e}")
    
    async def _save_configuration(self) -> None:
        """Save current configuration to file"""
        try:
            config_data = {
                'timestamp': datetime.now().isoformat(),
                'configuration': self.current_configuration,
                'metadata': {
                    'changes_applied': self.configuration_metrics['changes_applied'],
                    'last_optimization': None  # Could track last optimization time
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
            logger.debug("Configuration saved to file")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    async def _load_configuration(self) -> None:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                with self.config_lock:
                    self.current_configuration = config_data.get('configuration', {})
                
                logger.info("Configuration loaded from file")
            else:
                logger.info("No existing configuration file found, using defaults")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def get_configuration_history(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent configuration change history"""
        return [change.to_dict() for change in self.configuration_history[-count:]]
    
    def get_configuration_metrics(self) -> Dict[str, Any]:
        """Get configuration management metrics"""
        return {
            **self.configuration_metrics,
            'current_config_size': len(str(self.current_configuration)),
            'validation_rules_count': len(self.validation_rules),
            'change_listeners_count': sum(len(listeners) for listeners in self.change_listeners.values()),
            'history_size': len(self.configuration_history),
            'auto_apply_enabled': self.auto_apply_enabled,
            'validation_enabled': self.validation_enabled
        }
    
    def export_configuration(self, include_history: bool = False) -> Dict[str, Any]:
        """Export current configuration and optionally history"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'configuration': self.current_configuration.copy(),
            'validation_rules': {
                name: {
                    'parameter_name': rule.parameter_name,
                    'value_type': rule.value_type.__name__,
                    'min_value': rule.min_value,
                    'max_value': rule.max_value,
                    'allowed_values': rule.allowed_values,
                    'description': rule.description
                }
                for name, rule in self.validation_rules.items()
            },
            'metrics': self.get_configuration_metrics()
        }
        
        if include_history:
            export_data['history'] = self.get_configuration_history(1000)
        
        return export_data 