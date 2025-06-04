"""
Chaos System Repository

Provides data persistence for chaos system state, events, and metrics.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
from pathlib import Path

from backend.systems.chaos.core.warning_system import WarningEvent, WarningPhase
from backend.systems.chaos.core.narrative_moderator import NarrativeTheme, StoryBeat

logger = logging.getLogger(__name__)


class ChaosRepository:
    """Repository for chaos system data persistence"""
    
    def __init__(self, data_directory: str = "data/chaos"):
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.system_state_file = self.data_dir / "system_state.json"
        self.events_file = self.data_dir / "events_history.json"
        self.warnings_file = self.data_dir / "warnings_active.json"
        self.narrative_file = self.data_dir / "narrative_state.json"
        self.metrics_file = self.data_dir / "metrics_history.json"
        self.pressure_file = self.data_dir / "pressure_history.json"
    
    def save_system_state(self, state: Dict[str, Any]) -> bool:
        """Save current system state"""
        try:
            state_data = {
                **state,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.system_state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save system state: {e}")
            return False
    
    def load_system_state(self) -> Optional[Dict[str, Any]]:
        """Load system state"""
        try:
            if not self.system_state_file.exists():
                return None
                
            with open(self.system_state_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to load system state: {e}")
            return None
    
    def save_active_warnings(self, warnings: Dict[str, Dict[str, WarningEvent]]) -> bool:
        """Save currently active warnings"""
        try:
            warnings_data = {}
            
            for region_id, region_warnings in warnings.items():
                warnings_data[region_id] = {}
                for warning_key, warning in region_warnings.items():
                    warnings_data[region_id][warning_key] = warning.to_dict()
            
            with open(self.warnings_file, 'w') as f:
                json.dump(warnings_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save active warnings: {e}")
            return False
    
    def load_active_warnings(self) -> Dict[str, Dict[str, WarningEvent]]:
        """Load active warnings"""
        try:
            if not self.warnings_file.exists():
                return {}
                
            with open(self.warnings_file, 'r') as f:
                warnings_data = json.load(f)
            
            warnings = {}
            for region_id, region_warnings in warnings_data.items():
                warnings[region_id] = {}
                for warning_key, warning_dict in region_warnings.items():
                    # Reconstruct WarningEvent from dict
                    warning = WarningEvent(
                        warning_id=warning_dict['warning_id'],
                        region_id=warning_dict['region_id'],
                        phase=WarningPhase(warning_dict['phase']),
                        event_type=warning_dict['event_type'],
                        severity=warning_dict['severity'],
                        triggered_at=datetime.fromisoformat(warning_dict['triggered_at']),
                        expires_at=datetime.fromisoformat(warning_dict['expires_at']),
                        description=warning_dict['description'],
                        visible_clues=warning_dict['visible_clues'],
                        hidden_indicators=warning_dict['hidden_indicators'],
                        escalation_probability=warning_dict['escalation_probability']
                    )
                    warnings[region_id][warning_key] = warning
            
            return warnings
            
        except Exception as e:
            logger.error(f"Failed to load active warnings: {e}")
            return {}
    
    def save_narrative_state(self, themes: Dict[str, NarrativeTheme], 
                           story_beats: Dict[str, StoryBeat],
                           tension_history: List[Dict[str, Any]],
                           engagement_history: List[Dict[str, Any]]) -> bool:
        """Save narrative moderator state"""
        try:
            narrative_data = {
                'themes': {
                    theme_id: {
                        'theme_id': theme.theme_id,
                        'name': theme.name,
                        'description': theme.description,
                        'priority': theme.priority.value,
                        'weight_modifier': theme.weight_modifier,
                        'active_until': theme.active_until.isoformat() if theme.active_until else None,
                        'related_events': theme.related_events
                    }
                    for theme_id, theme in themes.items()
                },
                'story_beats': {
                    beat_id: {
                        'beat_id': beat.beat_id,
                        'name': beat.name,
                        'description': beat.description,
                        'drama_level': beat.drama_level,
                        'engagement_impact': beat.engagement_impact,
                        'chaos_compatibility': beat.chaos_compatibility,
                        'duration_hours': beat.duration_hours,
                        'created_at': beat.created_at.isoformat()
                    }
                    for beat_id, beat in story_beats.items()
                },
                'tension_history': tension_history,
                'engagement_history': engagement_history,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.narrative_file, 'w') as f:
                json.dump(narrative_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Failed to save narrative state: {e}")
            return False
    
    def load_narrative_state(self) -> Optional[Dict[str, Any]]:
        """Load narrative moderator state"""
        try:
            if not self.narrative_file.exists():
                return None
                
            with open(self.narrative_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to load narrative state: {e}")
            return None
    
    def append_event_history(self, event_data: Dict[str, Any]) -> bool:
        """Append event to history"""
        try:
            # Load existing history
            events = self.load_event_history() or []
            
            # Add new event
            event_data['recorded_at'] = datetime.now().isoformat()
            events.append(event_data)
            
            # Keep only last 1000 events
            if len(events) > 1000:
                events = events[-1000:]
            
            # Save back
            with open(self.events_file, 'w') as f:
                json.dump(events, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Failed to append event history: {e}")
            return False
    
    def load_event_history(self, limit: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Load event history"""
        try:
            if not self.events_file.exists():
                return []
                
            with open(self.events_file, 'r') as f:
                events = json.load(f)
            
            if limit:
                events = events[-limit:]
                
            return events
            
        except Exception as e:
            logger.error(f"Failed to load event history: {e}")
            return None
    
    def append_metrics(self, metrics_data: Dict[str, Any]) -> bool:
        """Append metrics data"""
        try:
            # Load existing metrics
            metrics = self.load_metrics_history() or []
            
            # Add timestamp
            metrics_data['timestamp'] = datetime.now().isoformat()
            metrics.append(metrics_data)
            
            # Keep only last week of metrics (assuming hourly recording)
            if len(metrics) > 168:  # 24 * 7 hours
                metrics = metrics[-168:]
            
            # Save back
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Failed to append metrics: {e}")
            return False
    
    def load_metrics_history(self, hours: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Load metrics history"""
        try:
            if not self.metrics_file.exists():
                return []
                
            with open(self.metrics_file, 'r') as f:
                metrics = json.load(f)
            
            if hours:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                metrics = [
                    m for m in metrics 
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ]
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to load metrics history: {e}")
            return None
    
    def append_pressure_data(self, pressure_data: Dict[str, Any]) -> bool:
        """Append pressure monitoring data"""
        try:
            # Load existing pressure data
            pressures = self.load_pressure_history() or []
            
            # Add timestamp
            pressure_data['timestamp'] = datetime.now().isoformat()
            pressures.append(pressure_data)
            
            # Keep only last 48 hours (assuming 15-minute intervals)
            if len(pressures) > 192:  # 48 * 4 per hour
                pressures = pressures[-192:]
            
            # Save back
            with open(self.pressure_file, 'w') as f:
                json.dump(pressures, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Failed to append pressure data: {e}")
            return False
    
    def load_pressure_history(self, hours: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Load pressure history"""
        try:
            if not self.pressure_file.exists():
                return []
                
            with open(self.pressure_file, 'r') as f:
                pressures = json.load(f)
            
            if hours:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                pressures = [
                    p for p in pressures 
                    if datetime.fromisoformat(p['timestamp']) > cutoff_time
                ]
                
            return pressures
            
        except Exception as e:
            logger.error(f"Failed to load pressure history: {e}")
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old data files"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            
            # Clean event history
            events = self.load_event_history()
            if events:
                events = [
                    e for e in events 
                    if datetime.fromisoformat(e.get('recorded_at', datetime.now().isoformat())) > cutoff_time
                ]
                with open(self.events_file, 'w') as f:
                    json.dump(events, f, indent=2, default=str)
            
            # Clean metrics history
            metrics = self.load_metrics_history()
            if metrics:
                metrics = [
                    m for m in metrics 
                    if datetime.fromisoformat(m['timestamp']) > cutoff_time
                ]
                with open(self.metrics_file, 'w') as f:
                    json.dump(metrics, f, indent=2, default=str)
            
            # Clean pressure history (keep less time)
            pressure_cutoff = datetime.now() - timedelta(days=7)  # Keep 1 week
            pressures = self.load_pressure_history()
            if pressures:
                pressures = [
                    p for p in pressures 
                    if datetime.fromisoformat(p['timestamp']) > pressure_cutoff
                ]
                with open(self.pressure_file, 'w') as f:
                    json.dump(pressures, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {}
            
            files = [
                ('system_state', self.system_state_file),
                ('events_history', self.events_file),
                ('active_warnings', self.warnings_file),
                ('narrative_state', self.narrative_file),
                ('metrics_history', self.metrics_file),
                ('pressure_history', self.pressure_file)
            ]
            
            for name, path in files:
                if path.exists():
                    stats[name] = {
                        'size_bytes': path.stat().st_size,
                        'last_modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                    }
                else:
                    stats[name] = {'size_bytes': 0, 'last_modified': None}
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {} 