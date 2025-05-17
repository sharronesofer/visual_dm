import os
import json
import threading
from typing import Dict, Any, Optional, Callable
import logging
from pathlib import Path
import time

# Type definition
FeatureFlag = str
FlagContext = Dict[str, Any]
FlagEvaluator = Callable[[str, FlagContext], bool]

class FeatureFlagSystem:
    """
    Enhanced feature flag system with support for environment variables,
    config files, dynamic reloading, and context-specific evaluation.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._flags: Dict[FeatureFlag, bool] = {}
        self._config_file: Optional[str] = None
        self._last_reload_time = 0
        self._reload_interval = 60  # Seconds
        self._evaluators: Dict[FeatureFlag, FlagEvaluator] = {}
        self._logger = logging.getLogger(__name__)
        
        # Load flags from environment variables during initialization
        self._load_from_environment()
    
    def _load_from_environment(self) -> None:
        """Load feature flags from environment variables with FEATURE_FLAG_ prefix"""
        with self._lock:
            env_flags = {
                key[13:]: value.lower() in ('true', '1', 'yes', 'y')
                for key, value in os.environ.items()
                if key.startswith('FEATURE_FLAG_')
            }
            self._flags.update(env_flags)
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load feature flags from a JSON config file.
        
        Args:
            file_path: Path to the JSON config file
            
        Returns:
            True if successfully loaded, False otherwise
        """
        try:
            config_path = Path(file_path)
            if not config_path.exists():
                self._logger.warning(f"Feature flag config file does not exist: {file_path}")
                return False
                
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            with self._lock:
                if 'featureFlags' in config:
                    self._flags.update(config['featureFlags'])
                    self._config_file = file_path
                    self._last_reload_time = time.time()
                    return True
                else:
                    self._logger.warning("No 'featureFlags' key found in config file")
                    return False
        except Exception as e:
            self._logger.error(f"Error loading feature flags from file: {e}")
            return False
    
    def reload_if_needed(self) -> bool:
        """
        Reload flags from config file if reload interval has passed.
        
        Returns:
            True if reloaded, False otherwise
        """
        if not self._config_file:
            return False
            
        now = time.time()
        if now - self._last_reload_time > self._reload_interval:
            return self.load_from_file(self._config_file)
        return False
    
    def set_reload_interval(self, seconds: int) -> None:
        """Set the interval for automatic config file reloading"""
        if seconds < 1:
            raise ValueError("Reload interval must be at least 1 second")
        self._reload_interval = seconds
    
    def is_feature_enabled(self, flag: FeatureFlag, context: Optional[FlagContext] = None) -> bool:
        """
        Check if a feature flag is enabled, optionally considering a context.
        
        Args:
            flag: The feature flag to check
            context: Optional context dictionary for context-specific evaluation
            
        Returns:
            True if the feature is enabled, False otherwise
        """
        # Reload from file if needed
        self.reload_if_needed()
        
        # If a custom evaluator exists for this flag, use it with the context
        if context and flag in self._evaluators:
            try:
                return self._evaluators[flag](flag, context)
            except Exception as e:
                self._logger.error(f"Error in custom evaluator for flag '{flag}': {e}")
                # Fall back to static flag value
        
        # Otherwise use the static flag value
        with self._lock:
            return self._flags.get(flag, False)
    
    def set_feature_flag(self, flag: FeatureFlag, enabled: bool) -> None:
        """Set a feature flag value"""
        with self._lock:
            self._flags[flag] = enabled
    
    def register_evaluator(self, flag: FeatureFlag, evaluator: FlagEvaluator) -> None:
        """
        Register a custom evaluator function for context-based flag evaluation.
        
        Args:
            flag: The feature flag to register the evaluator for
            evaluator: Function that takes (flag, context) and returns boolean
        """
        with self._lock:
            self._evaluators[flag] = evaluator
    
    def get_all_feature_flags(self) -> Dict[FeatureFlag, bool]:
        """Get all feature flags and their current values"""
        with self._lock:
            return dict(self._flags)

# Create a singleton instance
_feature_flags = FeatureFlagSystem()

# Module-level functions for backward compatibility and ease of use
def is_feature_enabled(flag: FeatureFlag, context: Optional[FlagContext] = None) -> bool:
    """Check if a feature flag is enabled"""
    return _feature_flags.is_feature_enabled(flag, context)

def set_feature_flag(flag: FeatureFlag, enabled: bool) -> None:
    """Set a feature flag value"""
    _feature_flags.set_feature_flag(flag, enabled)

def get_all_feature_flags() -> Dict[FeatureFlag, bool]:
    """Get all feature flags and their values"""
    return _feature_flags.get_all_feature_flags()

def load_feature_flags_from_file(file_path: str) -> bool:
    """Load feature flags from a JSON config file"""
    return _feature_flags.load_from_file(file_path)

def register_context_evaluator(flag: FeatureFlag, evaluator: FlagEvaluator) -> None:
    """Register a custom context-based evaluator for a flag"""
    _feature_flags.register_evaluator(flag, evaluator)

def set_reload_interval(seconds: int) -> None:
    """Set the interval for automatic config file reloading"""
    _feature_flags.set_reload_interval(seconds) 