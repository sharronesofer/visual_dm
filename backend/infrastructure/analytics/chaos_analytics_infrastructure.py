"""
Chaos Analytics Infrastructure

Handles file I/O, persistence, and technical aspects of chaos analytics.
Separated from business logic to maintain clean architecture.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsSnapshot:
    """Snapshot of analytics data at a point in time"""
    timestamp: datetime
    chaos_metrics: Dict[str, Any]
    pressure_metrics: Dict[str, Any]
    event_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    configuration_state: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'chaos_metrics': self.chaos_metrics,
            'pressure_metrics': self.pressure_metrics,
            'event_metrics': self.event_metrics,
            'performance_metrics': self.performance_metrics,
            'configuration_state': self.configuration_state
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyticsSnapshot':
        """Create from dictionary data"""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            chaos_metrics=data.get('chaos_metrics', {}),
            pressure_metrics=data.get('pressure_metrics', {}),
            event_metrics=data.get('event_metrics', {}),
            performance_metrics=data.get('performance_metrics', {}),
            configuration_state=data.get('configuration_state', {})
        )

@dataclass
class EventRecord:
    """Record of a chaos event for analytics"""
    timestamp: datetime
    event_id: str
    event_type: str
    severity: str
    regions_affected: List[str]
    pressure_before: Dict[str, float]
    pressure_after: Dict[str, float]
    mitigation_applied: bool
    duration_seconds: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_id': self.event_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'regions_affected': self.regions_affected,
            'pressure_before': self.pressure_before,
            'pressure_after': self.pressure_after,
            'mitigation_applied': self.mitigation_applied,
            'duration_seconds': self.duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventRecord':
        """Create from dictionary data"""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            event_id=data['event_id'],
            event_type=data['event_type'],
            severity=data['severity'],
            regions_affected=data.get('regions_affected', []),
            pressure_before=data.get('pressure_before', {}),
            pressure_after=data.get('pressure_after', {}),
            mitigation_applied=data.get('mitigation_applied', False),
            duration_seconds=data.get('duration_seconds', 0.0)
        )

class ChaosAnalyticsStorage:
    """
    Handles file storage and persistence for chaos analytics data.
    
    Separated from business logic to keep infrastructure concerns isolated.
    """
    
    def __init__(self, analytics_dir: Optional[Path] = None):
        """Initialize analytics storage"""
        if analytics_dir is None:
            # Default to data/infrastructure/analytics/chaos
            self.analytics_dir = Path("data/infrastructure/analytics/chaos")
        else:
            self.analytics_dir = Path(analytics_dir)
        
        # Ensure directory exists
        self.analytics_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.events_file = self.analytics_dir / "event_records.json"
        self.snapshots_file = self.analytics_dir / "analytics_snapshots.json"
        self.metrics_file = self.analytics_dir / "performance_metrics.json"
        
        logger.info(f"Chaos Analytics Storage initialized at {self.analytics_dir}")
    
    async def save_event_records(self, event_records: List[EventRecord]) -> None:
        """Save event records to disk"""
        try:
            # Keep only the most recent 1000 records for performance
            records_to_save = event_records[-1000:] if len(event_records) > 1000 else event_records
            
            with open(self.events_file, 'w') as f:
                json.dump([record.to_dict() for record in records_to_save], f, indent=2)
            
            logger.debug(f"Saved {len(records_to_save)} event records to {self.events_file}")
            
        except Exception as e:
            logger.error(f"Error saving event records: {e}")
    
    async def save_analytics_snapshots(self, snapshots: List[AnalyticsSnapshot]) -> None:
        """Save analytics snapshots to disk"""
        try:
            # Keep only the most recent 1000 snapshots for performance
            snapshots_to_save = snapshots[-1000:] if len(snapshots) > 1000 else snapshots
            
            with open(self.snapshots_file, 'w') as f:
                json.dump([snapshot.to_dict() for snapshot in snapshots_to_save], f, indent=2)
            
            logger.debug(f"Saved {len(snapshots_to_save)} analytics snapshots to {self.snapshots_file}")
            
        except Exception as e:
            logger.error(f"Error saving analytics snapshots: {e}")
    
    async def save_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save performance metrics to disk"""
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            logger.debug(f"Saved performance metrics to {self.metrics_file}")
            
        except Exception as e:
            logger.error(f"Error saving performance metrics: {e}")
    
    async def load_event_records(self) -> List[EventRecord]:
        """Load event records from disk"""
        try:
            if not self.events_file.exists():
                return []
            
            with open(self.events_file, 'r') as f:
                event_data = json.load(f)
            
            return [EventRecord.from_dict(record) for record in event_data]
            
        except Exception as e:
            logger.error(f"Error loading event records: {e}")
            return []
    
    async def load_analytics_snapshots(self) -> List[AnalyticsSnapshot]:
        """Load analytics snapshots from disk"""
        try:
            if not self.snapshots_file.exists():
                return []
            
            with open(self.snapshots_file, 'r') as f:
                snapshot_data = json.load(f)
            
            return [AnalyticsSnapshot.from_dict(snapshot) for snapshot in snapshot_data]
            
        except Exception as e:
            logger.error(f"Error loading analytics snapshots: {e}")
            return []
    
    async def load_performance_metrics(self) -> Dict[str, Any]:
        """Load performance metrics from disk"""
        try:
            if not self.metrics_file.exists():
                return {}
            
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
            
        except Exception as e:
            logger.error(f"Error loading performance metrics: {e}")
            return {}
    
    async def export_analytics_data(self, output_dir: Path) -> Dict[str, str]:
        """Export all analytics data to specified directory"""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            exported_files = {}
            
            # Export event analytics
            event_records = await self.load_event_records()
            if event_records:
                event_file = output_dir / "event_analytics.json"
                with open(event_file, 'w') as f:
                    json.dump([record.to_dict() for record in event_records], f, indent=2)
                exported_files['event_data'] = str(event_file)
            
            # Export performance analytics
            performance_metrics = await self.load_performance_metrics()
            if performance_metrics:
                performance_file = output_dir / "performance_analytics.json"
                with open(performance_file, 'w') as f:
                    json.dump(performance_metrics, f, indent=2)
                exported_files['performance_data'] = str(performance_file)
            
            # Export snapshots
            snapshots = await self.load_analytics_snapshots()
            if snapshots:
                snapshots_file = output_dir / "analytics_snapshots.json"
                with open(snapshots_file, 'w') as f:
                    json.dump([snapshot.to_dict() for snapshot in snapshots], f, indent=2)
                exported_files['snapshots_data'] = str(snapshots_file)
            
            logger.info(f"Analytics data exported to {output_dir}")
            return exported_files
            
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return {}
    
    async def cleanup_old_data(self, max_age_days: int = 30) -> None:
        """Clean up analytics data older than specified age"""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Clean up event records
            event_records = await self.load_event_records()
            filtered_events = [
                record for record in event_records 
                if record.timestamp > cutoff_date
            ]
            if len(filtered_events) < len(event_records):
                await self.save_event_records(filtered_events)
            
            # Clean up snapshots
            snapshots = await self.load_analytics_snapshots()
            filtered_snapshots = [
                snapshot for snapshot in snapshots 
                if snapshot.timestamp > cutoff_date
            ]
            if len(filtered_snapshots) < len(snapshots):
                await self.save_analytics_snapshots(filtered_snapshots)
            
            logger.info(f"Cleaned up analytics data older than {max_age_days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

class ChaosConfigurationPersistence:
    """
    Handles persistence of chaos configuration changes and backups.
    
    Provides file I/O infrastructure for configuration management.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration persistence"""
        if config_dir is None:
            self.config_dir = Path("data/infrastructure/config/chaos")
        else:
            self.config_dir = Path(config_dir)
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # File paths
        self.config_file = self.config_dir / "dynamic_config.json"
        
        logger.info(f"Configuration persistence initialized at {self.config_dir}")
    
    async def save_configuration(self, config_data: Dict[str, Any]) -> None:
        """Save configuration data to disk"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.debug("Configuration saved to file")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    async def load_configuration(self) -> Dict[str, Any]:
        """Load configuration data from disk"""
        try:
            if not self.config_file.exists():
                logger.info("No existing configuration file found, using defaults")
                return {}
            
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            logger.info("Configuration loaded from file")
            return config_data
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    async def create_configuration_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of the current configuration"""
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"config_backup_{timestamp}"
            
            backup_file = self.backup_dir / f"{backup_name}.json"
            
            # Load current configuration
            current_config = await self.load_configuration()
            
            # Add backup metadata
            backup_data = {
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'configuration': current_config
            }
            
            # Save backup
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Configuration backup created: {backup_file}")
            return backup_name
            
        except Exception as e:
            logger.error(f"Error creating configuration backup: {e}")
            return ""
    
    async def restore_configuration_backup(self, backup_name: str) -> Dict[str, Any]:
        """Restore configuration from backup"""
        try:
            backup_file = self.backup_dir / f"{backup_name}.json"
            
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return {}
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Extract configuration from backup
            restored_config = backup_data.get('configuration', {})
            
            # Save as current configuration
            await self.save_configuration(restored_config)
            
            logger.info(f"Configuration restored from backup: {backup_name}")
            return restored_config
            
        except Exception as e:
            logger.error(f"Error restoring configuration backup: {e}")
            return {} 