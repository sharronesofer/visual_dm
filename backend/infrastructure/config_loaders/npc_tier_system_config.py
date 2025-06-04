"""
Revolutionary NPC Tier System Configuration

Centralized configuration management for the tier system with environment
variables, runtime settings, and deployment-specific optimizations.
"""

import os
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DeploymentMode(Enum):
    """Deployment mode configurations for different environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class PerformanceProfile(Enum):
    """Performance profiles for different scaling needs"""
    MINIMAL = "minimal"        # <10,000 NPCs, minimal resource usage
    STANDARD = "standard"      # 10,000-50,000 NPCs, balanced performance
    ENHANCED = "enhanced"      # 50,000-200,000 NPCs, optimized for scale
    REVOLUTIONARY = "revolutionary"  # 200,000+ NPCs, maximum efficiency


@dataclass
class TierTimingConfig:
    """Configuration for tier promotion/demotion timing"""
    tier_1_duration_hours: float = 1.0      # Time before demoting from Tier 1
    tier_2_duration_hours: float = 11.0     # Total time before demoting from Tier 2
    tier_3_duration_hours: float = 168.0    # Total time before demoting from Tier 3 (1 week)
    
    # Grace periods for interactions
    interaction_grace_minutes: float = 15.0  # Grace period after interaction
    poi_activation_grace_minutes: float = 30.0  # Grace period after POI activation
    
    # Cycle intervals
    management_cycle_seconds: int = 300      # 5 minutes default
    maintenance_cycle_seconds: int = 3600    # 1 hour default
    optimization_cycle_seconds: int = 7200   # 2 hours default


@dataclass
class ComputationalLimits:
    """Computational budget limits and thresholds"""
    max_tier_1_npcs: int = 1000             # Maximum Tier 1 NPCs globally
    max_tier_2_npcs: int = 5000             # Maximum Tier 2 NPCs globally
    max_visible_npcs: int = 50000           # Maximum visible NPCs (Tiers 1-3.5)
    
    # Performance thresholds
    memory_warning_mb: float = 1000.0       # Warn when memory usage exceeds this
    cpu_warning_units: float = 5000.0       # Warn when CPU usage exceeds this
    efficiency_warning_ratio: float = 0.6   # Warn when visible ratio exceeds this
    
    # Budget allocations (CPU units per hour)
    total_cpu_budget: float = 10000.0       # Total CPU budget
    emergency_reserve_ratio: float = 0.2    # Reserve 20% for emergencies


@dataclass
class SystemIntegrationConfig:
    """Configuration for integration with other game systems"""
    economy_participation_tiers: List[str] = field(default_factory=lambda: ["tier_1_active", "tier_2_background", "tier_3_dormant"])
    diplomacy_participation_tiers: List[str] = field(default_factory=lambda: ["tier_1_active", "tier_2_background"])
    tension_participation_tiers: List[str] = field(default_factory=lambda: ["tier_1_active", "tier_2_background"])
    religion_participation_tiers: List[str] = field(default_factory=lambda: ["tier_1_active", "tier_2_background", "tier_3_dormant"])
    espionage_participation_tiers: List[str] = field(default_factory=lambda: ["tier_1_active", "tier_2_background"])
    
    # POI type configurations
    economy_poi_types: List[str] = field(default_factory=lambda: ["settlement", "social", "economic"])
    diplomacy_poi_types: List[str] = field(default_factory=lambda: ["settlement", "social", "military"])
    espionage_poi_types: List[str] = field(default_factory=lambda: ["military", "settlement"])


@dataclass
class TierSystemConfig:
    """Main configuration class for the Revolutionary NPC Tier System"""
    
    # Environment and deployment
    deployment_mode: DeploymentMode = DeploymentMode.PRODUCTION
    performance_profile: PerformanceProfile = PerformanceProfile.STANDARD
    debug_mode: bool = False
    
    # Timing configuration
    timing: TierTimingConfig = field(default_factory=TierTimingConfig)
    
    # Computational limits
    limits: ComputationalLimits = field(default_factory=ComputationalLimits)
    
    # System integration
    integration: SystemIntegrationConfig = field(default_factory=SystemIntegrationConfig)
    
    # Database and caching
    enable_npc_caching: bool = True
    cache_tier_data: bool = True
    cache_ttl_seconds: int = 300             # 5 minutes cache TTL
    batch_size: int = 100                    # Database batch operation size
    
    # Event system
    enable_tier_events: bool = True
    event_batch_size: int = 50
    
    # Monitoring and logging
    enable_performance_monitoring: bool = True
    enable_tier_metrics: bool = True
    metrics_export_interval_seconds: int = 60
    
    # Feature flags
    enable_chuck_e_cheese_activation: bool = True
    enable_automatic_optimization: bool = True
    enable_memory_compression: bool = True
    enable_predictive_promotion: bool = False  # Future feature
    
    @classmethod
    def from_environment(cls) -> 'TierSystemConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Deployment mode
        deployment_mode = os.getenv('TIER_SYSTEM_DEPLOYMENT_MODE', 'production').lower()
        try:
            config.deployment_mode = DeploymentMode(deployment_mode)
        except ValueError:
            logger.warning(f"Invalid deployment mode: {deployment_mode}, using production")
            config.deployment_mode = DeploymentMode.PRODUCTION
        
        # Performance profile
        performance_profile = os.getenv('TIER_SYSTEM_PERFORMANCE_PROFILE', 'standard').lower()
        try:
            config.performance_profile = PerformanceProfile(performance_profile)
        except ValueError:
            logger.warning(f"Invalid performance profile: {performance_profile}, using standard")
            config.performance_profile = PerformanceProfile.STANDARD
        
        # Debug mode
        config.debug_mode = os.getenv('TIER_SYSTEM_DEBUG', 'false').lower() == 'true'
        
        # Timing configuration
        config.timing.tier_1_duration_hours = float(os.getenv('TIER_1_DURATION_HOURS', '1.0'))
        config.timing.tier_2_duration_hours = float(os.getenv('TIER_2_DURATION_HOURS', '11.0'))
        config.timing.tier_3_duration_hours = float(os.getenv('TIER_3_DURATION_HOURS', '168.0'))
        config.timing.management_cycle_seconds = int(os.getenv('TIER_MANAGEMENT_CYCLE_SECONDS', '300'))
        config.timing.maintenance_cycle_seconds = int(os.getenv('TIER_MAINTENANCE_CYCLE_SECONDS', '3600'))
        config.timing.optimization_cycle_seconds = int(os.getenv('TIER_OPTIMIZATION_CYCLE_SECONDS', '7200'))
        
        # Computational limits
        config.limits.max_tier_1_npcs = int(os.getenv('MAX_TIER_1_NPCS', '1000'))
        config.limits.max_tier_2_npcs = int(os.getenv('MAX_TIER_2_NPCS', '5000'))
        config.limits.max_visible_npcs = int(os.getenv('MAX_VISIBLE_NPCS', '50000'))
        config.limits.total_cpu_budget = float(os.getenv('TOTAL_CPU_BUDGET', '10000.0'))
        
        # Feature flags
        config.enable_chuck_e_cheese_activation = os.getenv('ENABLE_CHUCK_E_CHEESE', 'true').lower() == 'true'
        config.enable_automatic_optimization = os.getenv('ENABLE_AUTO_OPTIMIZATION', 'true').lower() == 'true'
        config.enable_memory_compression = os.getenv('ENABLE_MEMORY_COMPRESSION', 'true').lower() == 'true'
        config.enable_predictive_promotion = os.getenv('ENABLE_PREDICTIVE_PROMOTION', 'false').lower() == 'true'
        
        # Caching and performance
        config.enable_npc_caching = os.getenv('ENABLE_NPC_CACHING', 'true').lower() == 'true'
        config.cache_ttl_seconds = int(os.getenv('CACHE_TTL_SECONDS', '300'))
        config.batch_size = int(os.getenv('DB_BATCH_SIZE', '100'))
        
        # Monitoring
        config.enable_performance_monitoring = os.getenv('ENABLE_PERFORMANCE_MONITORING', 'true').lower() == 'true'
        config.enable_tier_metrics = os.getenv('ENABLE_TIER_METRICS', 'true').lower() == 'true'
        config.metrics_export_interval_seconds = int(os.getenv('METRICS_EXPORT_INTERVAL', '60'))
        
        # Apply performance profile optimizations
        config._apply_performance_profile()
        
        logger.info(f"Tier system configuration loaded: {config.deployment_mode.value} mode, {config.performance_profile.value} profile")
        return config
    
    def _apply_performance_profile(self) -> None:
        """Apply performance profile-specific optimizations"""
        if self.performance_profile == PerformanceProfile.MINIMAL:
            # Minimal resource usage
            self.limits.max_tier_1_npcs = 100
            self.limits.max_tier_2_npcs = 500
            self.limits.max_visible_npcs = 5000
            self.timing.management_cycle_seconds = 600  # 10 minutes
            self.cache_ttl_seconds = 600
            
        elif self.performance_profile == PerformanceProfile.STANDARD:
            # Balanced performance (default values)
            pass
            
        elif self.performance_profile == PerformanceProfile.ENHANCED:
            # Optimized for larger scale
            self.limits.max_tier_1_npcs = 2000
            self.limits.max_tier_2_npcs = 10000
            self.limits.max_visible_npcs = 100000
            self.timing.management_cycle_seconds = 180  # 3 minutes
            self.cache_ttl_seconds = 180
            self.batch_size = 200
            
        elif self.performance_profile == PerformanceProfile.REVOLUTIONARY:
            # Maximum efficiency for 200,000+ NPCs
            self.limits.max_tier_1_npcs = 3000
            self.limits.max_tier_2_npcs = 15000
            self.limits.max_visible_npcs = 200000
            self.timing.management_cycle_seconds = 120  # 2 minutes
            self.cache_ttl_seconds = 120
            self.batch_size = 500
            self.enable_memory_compression = True
            self.enable_automatic_optimization = True
    
    def get_tier_computational_costs(self) -> Dict[str, float]:
        """Get tier computational costs based on performance profile"""
        base_costs = {
            "tier_1_active": 10.0,
            "tier_2_background": 2.0,
            "tier_3_dormant": 0.1,
            "tier_3_5_compressed": 0.02,
            "tier_4_statistical": 0.0
        }
        
        # Apply performance profile modifiers
        if self.performance_profile == PerformanceProfile.MINIMAL:
            # Higher costs for minimal profile (less optimization)
            return {k: v * 1.2 for k, v in base_costs.items()}
        elif self.performance_profile == PerformanceProfile.REVOLUTIONARY:
            # Lower costs for revolutionary profile (maximum optimization)
            return {k: v * 0.8 for k, v in base_costs.items()}
        else:
            return base_costs
    
    def get_tier_memory_costs(self) -> Dict[str, float]:
        """Get tier memory costs based on performance profile"""
        base_costs = {
            "tier_1_active": 2.5,
            "tier_2_background": 1.0,
            "tier_3_dormant": 0.2,
            "tier_3_5_compressed": 0.05,
            "tier_4_statistical": 0.0
        }
        
        # Apply compression optimizations
        if self.enable_memory_compression:
            compression_factor = 0.7 if self.performance_profile == PerformanceProfile.REVOLUTIONARY else 0.85
            return {k: v * compression_factor for k, v in base_costs.items()}
        else:
            return base_costs
    
    def validate(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Validate timing constraints
        if self.timing.tier_1_duration_hours >= self.timing.tier_2_duration_hours:
            issues.append("Tier 1 duration must be less than Tier 2 duration")
        
        if self.timing.tier_2_duration_hours >= self.timing.tier_3_duration_hours:
            issues.append("Tier 2 duration must be less than Tier 3 duration")
        
        # Validate computational limits
        if self.limits.max_tier_1_npcs > self.limits.max_tier_2_npcs:
            issues.append("Max Tier 1 NPCs should not exceed max Tier 2 NPCs")
        
        if self.limits.max_tier_2_npcs > self.limits.max_visible_npcs:
            issues.append("Max Tier 2 NPCs should not exceed max visible NPCs")
        
        # Validate cycle intervals
        if self.timing.management_cycle_seconds < 60:
            issues.append("Management cycle interval should be at least 60 seconds")
        
        # Validate budget allocation
        if self.limits.emergency_reserve_ratio >= 1.0:
            issues.append("Emergency reserve ratio should be less than 1.0")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization"""
        return {
            "deployment_mode": self.deployment_mode.value,
            "performance_profile": self.performance_profile.value,
            "debug_mode": self.debug_mode,
            "timing": {
                "tier_1_duration_hours": self.timing.tier_1_duration_hours,
                "tier_2_duration_hours": self.timing.tier_2_duration_hours,
                "tier_3_duration_hours": self.timing.tier_3_duration_hours,
                "management_cycle_seconds": self.timing.management_cycle_seconds,
                "maintenance_cycle_seconds": self.timing.maintenance_cycle_seconds,
                "optimization_cycle_seconds": self.timing.optimization_cycle_seconds
            },
            "limits": {
                "max_tier_1_npcs": self.limits.max_tier_1_npcs,
                "max_tier_2_npcs": self.limits.max_tier_2_npcs,
                "max_visible_npcs": self.limits.max_visible_npcs,
                "total_cpu_budget": self.limits.total_cpu_budget
            },
            "features": {
                "chuck_e_cheese_activation": self.enable_chuck_e_cheese_activation,
                "automatic_optimization": self.enable_automatic_optimization,
                "memory_compression": self.enable_memory_compression,
                "predictive_promotion": self.enable_predictive_promotion
            },
            "performance": {
                "enable_caching": self.enable_npc_caching,
                "cache_ttl_seconds": self.cache_ttl_seconds,
                "batch_size": self.batch_size
            }
        }


# ============================================================================
# Global Configuration Instance
# ============================================================================

# Global configuration instance
_tier_config: Optional[TierSystemConfig] = None

def get_tier_config() -> TierSystemConfig:
    """Get global tier system configuration instance"""
    global _tier_config
    
    if _tier_config is None:
        _tier_config = TierSystemConfig.from_environment()
        
        # Validate configuration
        issues = _tier_config.validate()
        if issues:
            logger.warning(f"Configuration validation issues: {', '.join(issues)}")
    
    return _tier_config

def reload_tier_config() -> TierSystemConfig:
    """Reload configuration from environment variables"""
    global _tier_config
    _tier_config = None
    return get_tier_config()

def set_tier_config(config: TierSystemConfig) -> None:
    """Set global tier system configuration (for testing)"""
    global _tier_config
    _tier_config = config


# ============================================================================
# Configuration Profiles for Different Environments
# ============================================================================

def get_development_config() -> TierSystemConfig:
    """Get configuration optimized for development"""
    config = TierSystemConfig()
    config.deployment_mode = DeploymentMode.DEVELOPMENT
    config.performance_profile = PerformanceProfile.MINIMAL
    config.debug_mode = True
    config.timing.management_cycle_seconds = 60  # Faster cycles for testing
    config.limits.max_visible_npcs = 1000  # Smaller scale for development
    config.enable_performance_monitoring = True
    config._apply_performance_profile()
    return config

def get_testing_config() -> TierSystemConfig:
    """Get configuration optimized for testing"""
    config = TierSystemConfig()
    config.deployment_mode = DeploymentMode.TESTING
    config.performance_profile = PerformanceProfile.MINIMAL
    config.debug_mode = True
    config.timing.management_cycle_seconds = 30  # Very fast cycles for testing
    config.limits.max_visible_npcs = 100  # Very small scale for unit tests
    config.enable_npc_caching = False  # Disable caching for predictable tests
    config.enable_tier_events = False  # Disable events for simpler tests
    config._apply_performance_profile()
    return config

def get_production_config() -> TierSystemConfig:
    """Get configuration optimized for production"""
    config = TierSystemConfig()
    config.deployment_mode = DeploymentMode.PRODUCTION
    config.performance_profile = PerformanceProfile.REVOLUTIONARY
    config.debug_mode = False
    config.enable_automatic_optimization = True
    config.enable_memory_compression = True
    config.enable_performance_monitoring = True
    config._apply_performance_profile()
    return config


# ============================================================================
# Environment Variable Documentation
# ============================================================================

ENVIRONMENT_VARIABLES = {
    "TIER_SYSTEM_DEPLOYMENT_MODE": "Deployment mode (development|staging|production|testing)",
    "TIER_SYSTEM_PERFORMANCE_PROFILE": "Performance profile (minimal|standard|enhanced|revolutionary)",
    "TIER_SYSTEM_DEBUG": "Enable debug mode (true|false)",
    "TIER_1_DURATION_HOURS": "Hours before demoting from Tier 1 (default: 1.0)",
    "TIER_2_DURATION_HOURS": "Total hours before demoting from Tier 2 (default: 11.0)",
    "TIER_3_DURATION_HOURS": "Total hours before demoting from Tier 3 (default: 168.0)",
    "TIER_MANAGEMENT_CYCLE_SECONDS": "Tier management cycle interval (default: 300)",
    "TIER_MAINTENANCE_CYCLE_SECONDS": "Maintenance cycle interval (default: 3600)",
    "TIER_OPTIMIZATION_CYCLE_SECONDS": "Optimization cycle interval (default: 7200)",
    "MAX_TIER_1_NPCS": "Maximum Tier 1 NPCs globally (default: 1000)",
    "MAX_TIER_2_NPCS": "Maximum Tier 2 NPCs globally (default: 5000)",
    "MAX_VISIBLE_NPCS": "Maximum visible NPCs (Tiers 1-3.5) (default: 50000)",
    "TOTAL_CPU_BUDGET": "Total CPU budget in units per hour (default: 10000.0)",
    "ENABLE_CHUCK_E_CHEESE": "Enable Chuck-E-Cheese activation system (true|false)",
    "ENABLE_AUTO_OPTIMIZATION": "Enable automatic optimization (true|false)",
    "ENABLE_MEMORY_COMPRESSION": "Enable memory compression (true|false)",
    "ENABLE_PREDICTIVE_PROMOTION": "Enable predictive promotion (true|false)",
    "ENABLE_NPC_CACHING": "Enable NPC data caching (true|false)",
    "CACHE_TTL_SECONDS": "Cache time-to-live in seconds (default: 300)",
    "DB_BATCH_SIZE": "Database batch operation size (default: 100)",
    "ENABLE_PERFORMANCE_MONITORING": "Enable performance monitoring (true|false)",
    "ENABLE_TIER_METRICS": "Enable tier metrics collection (true|false)",
    "METRICS_EXPORT_INTERVAL": "Metrics export interval in seconds (default: 60)"
} 