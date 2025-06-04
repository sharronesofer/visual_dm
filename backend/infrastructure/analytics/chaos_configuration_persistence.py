"""
Chaos Configuration Persistence Infrastructure

Handles the technical aspects of chaos configuration management including
file I/O, backup management, validation infrastructure, and persistence.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum
from threading import Lock

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

class ConfigurationPersistenceService:
    """
    Infrastructure service for configuration persistence and backup management.
    
    Handles all file I/O, backup operations, and configuration storage
    without business logic concerns.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration persistence service"""
        if config_dir is None:
            self.config_dir = Path("data/infrastructure/config/chaos")
        else:
            self.config_dir = Path(config_dir)
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "dynamic_config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Thread safety for file operations
        self.file_lock = Lock()
        
        logger.info(f"Configuration Persistence Service initialized at {self.config_dir}")
    
    async def save_configuration(self, configuration: Dict[str, Any]) -> bool:
        """Save configuration to disk"""
        try:
            with self.file_lock:
                with open(self.config_file, 'w') as f:
                    json.dump(configuration, f, indent=2, default=str)
                
            logger.debug("Configuration saved to disk")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    async def load_configuration(self) -> Dict[str, Any]:
        """Load configuration from disk"""
        try:
            if not self.config_file.exists():
                logger.info("No existing configuration file found, returning empty configuration")
                return {}
            
            with self.file_lock:
                with open(self.config_file, 'r') as f:
                    configuration = json.load(f)
            
            logger.debug("Configuration loaded from disk")
            return configuration
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    async def create_backup(self, configuration: Dict[str, Any], backup_name: Optional[str] = None) -> str:
        """Create a backup of the configuration"""
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"config_backup_{timestamp}"
            
            backup_file = self.backup_dir / f"{backup_name}.json"
            
            backup_data = {
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'configuration': configuration
            }
            
            with self.file_lock:
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Configuration backup created: {backup_file}")
            return backup_name
            
        except Exception as e:
            logger.error(f"Error creating configuration backup: {e}")
            return ""
    
    async def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """Restore configuration from backup"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.json"
            
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return {}
            
            with self.file_lock:
                with open(backup_file, 'r') as f:
                    backup_data = json.load(f)
            
            configuration = backup_data.get('configuration', {})
            logger.info(f"Configuration restored from backup: {backup_name}")
            return configuration
            
        except Exception as e:
            logger.error(f"Error restoring configuration backup: {e}")
            return {}
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available configuration backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.json"):
                try:
                    with open(backup_file, 'r') as f:
                        backup_data = json.load(f)
                    
                    backups.append({
                        'name': backup_data.get('backup_name', backup_file.stem),
                        'created_at': backup_data.get('created_at', ''),
                        'file_size': backup_file.stat().st_size,
                        'file_path': str(backup_file)
                    })
                    
                except Exception as e:
                    logger.warning(f"Error reading backup file {backup_file}: {e}")
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    async def cleanup_old_backups(self, max_age_days: int = 30, max_count: int = 50) -> int:
        """Clean up old backup files"""
        try:
            cleaned_count = 0
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            backups = self.list_backups()
            
            # Remove backups older than max_age_days
            for backup in backups:
                try:
                    backup_date = datetime.fromisoformat(backup['created_at'].replace('Z', '+00:00'))
                    if backup_date < cutoff_date:
                        backup_file = Path(backup['file_path'])
                        backup_file.unlink()
                        cleaned_count += 1
                        logger.debug(f"Removed old backup: {backup['name']}")
                except Exception as e:
                    logger.warning(f"Error removing old backup {backup['name']}: {e}")
            
            # Keep only the most recent max_count backups
            remaining_backups = self.list_backups()
            if len(remaining_backups) > max_count:
                excess_backups = remaining_backups[max_count:]
                for backup in excess_backups:
                    try:
                        backup_file = Path(backup['file_path'])
                        backup_file.unlink()
                        cleaned_count += 1
                        logger.debug(f"Removed excess backup: {backup['name']}")
                    except Exception as e:
                        logger.warning(f"Error removing excess backup {backup['name']}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old backup files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return 0 