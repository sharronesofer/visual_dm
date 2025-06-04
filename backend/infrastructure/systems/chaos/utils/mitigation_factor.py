"""
Mitigation Factor - Handles factors that reduce chaos pressure
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MitigationFactor:
    """Represents a factor that reduces chaos pressure"""
    factor_type: str
    effectiveness: float  # 0.0 to 1.0
    duration_hours: float
    source_id: str
    source_type: str  # 'diplomatic', 'economic', 'infrastructure', 'leadership'
    description: str
    affected_regions: List[str]
    affected_sources: List[str]  # Which pressure sources this mitigates
    applied_time: datetime
    expires_time: datetime

class MitigationFactorManager:
    """Manages mitigation factors that reduce chaos pressure"""
    
    def __init__(self):
        self.active_mitigations: List[MitigationFactor] = []
        
        # Mitigation effectiveness by type
        self.mitigation_types = {
            'diplomatic': {
                'max_effectiveness': 0.8,
                'affects': ['political', 'faction_tension', 'social'],
                'duration_multiplier': 1.2
            },
            'economic': {
                'max_effectiveness': 0.7,
                'affects': ['economic', 'social', 'resource'],
                'duration_multiplier': 1.0
            },
            'infrastructure': {
                'max_effectiveness': 0.6,
                'affects': ['environmental', 'social', 'economic'],
                'duration_multiplier': 1.5
            },
            'leadership': {
                'max_effectiveness': 0.9,
                'affects': ['political', 'social', 'faction_tension'],
                'duration_multiplier': 0.8
            },
            'military': {
                'max_effectiveness': 0.7,
                'affects': ['faction_tension', 'political', 'military'],
                'duration_multiplier': 1.0
            }
        }
    
    async def apply_mitigation(self, mitigation_type: str, effectiveness: float,
                             duration_hours: float, source_id: str, source_type: str,
                             description: str = "", affected_regions: List[str] = None,
                             affected_sources: List[str] = None) -> bool:
        """Apply a new mitigation factor"""
        
        try:
            # Validate mitigation type
            if mitigation_type not in self.mitigation_types:
                raise ValueError(f"Unknown mitigation type: {mitigation_type}")
            
            mitigation_config = self.mitigation_types[mitigation_type]
            
            # Clamp effectiveness to maximum for this type
            max_effectiveness = mitigation_config['max_effectiveness']
            effectiveness = min(effectiveness, max_effectiveness)
            
            # Apply duration multiplier
            duration_multiplier = mitigation_config['duration_multiplier']
            actual_duration = duration_hours * duration_multiplier
            
            # Use default affected sources if not specified
            if affected_sources is None:
                affected_sources = mitigation_config['affects']
            
            # Create mitigation factor
            now = datetime.now()
            mitigation = MitigationFactor(
                factor_type=mitigation_type,
                effectiveness=effectiveness,
                duration_hours=actual_duration,
                source_id=source_id,
                source_type=source_type,
                description=description,
                affected_regions=affected_regions or [],
                affected_sources=affected_sources,
                applied_time=now,
                expires_time=now + timedelta(hours=actual_duration)
            )
            
            # Add to active mitigations
            self.active_mitigations.append(mitigation)
            
            # Clean up expired mitigations
            self._cleanup_expired_mitigations()
            
            return True
            
        except Exception as e:
            print(f"Failed to apply mitigation: {e}")
            return False
    
    def calculate_mitigation_effects(self, pressure_sources: Dict[str, float],
                                   region_id: str = None) -> Dict[str, float]:
        """Calculate the mitigation effects on pressure sources"""
        
        mitigated_pressures = pressure_sources.copy()
        
        # Clean up expired mitigations first
        self._cleanup_expired_mitigations()
        
        # Apply each active mitigation
        for mitigation in self.active_mitigations:
            # Check if mitigation applies to this region
            if region_id and mitigation.affected_regions:
                if region_id not in mitigation.affected_regions:
                    continue
            
            # Apply mitigation to affected pressure sources
            for source in mitigation.affected_sources:
                if source in mitigated_pressures:
                    reduction = mitigated_pressures[source] * mitigation.effectiveness
                    mitigated_pressures[source] = max(0.0, mitigated_pressures[source] - reduction)
        
        return mitigated_pressures
    
    def get_active_mitigations(self, region_id: str = None) -> List[MitigationFactor]:
        """Get active mitigations, optionally filtered by region"""
        
        self._cleanup_expired_mitigations()
        
        if region_id is None:
            return self.active_mitigations.copy()
        
        return [
            mitigation for mitigation in self.active_mitigations
            if not mitigation.affected_regions or region_id in mitigation.affected_regions
        ]
    
    def get_mitigation_summary(self) -> Dict[str, Any]:
        """Get summary of current mitigation effects"""
        
        self._cleanup_expired_mitigations()
        
        summary = {
            'total_active': len(self.active_mitigations),
            'by_type': {},
            'by_source': {},
            'expiring_soon': []
        }
        
        now = datetime.now()
        soon_threshold = now + timedelta(hours=6)
        
        for mitigation in self.active_mitigations:
            # Count by type
            if mitigation.factor_type not in summary['by_type']:
                summary['by_type'][mitigation.factor_type] = 0
            summary['by_type'][mitigation.factor_type] += 1
            
            # Count by affected sources
            for source in mitigation.affected_sources:
                if source not in summary['by_source']:
                    summary['by_source'][source] = []
                summary['by_source'][source].append({
                    'type': mitigation.factor_type,
                    'effectiveness': mitigation.effectiveness,
                    'expires': mitigation.expires_time
                })
            
            # Check if expiring soon
            if mitigation.expires_time <= soon_threshold:
                summary['expiring_soon'].append({
                    'type': mitigation.factor_type,
                    'source_id': mitigation.source_id,
                    'expires': mitigation.expires_time,
                    'effectiveness': mitigation.effectiveness
                })
        
        return summary
    
    def _cleanup_expired_mitigations(self):
        """Remove expired mitigation factors"""
        now = datetime.now()
        
        self.active_mitigations = [
            mitigation for mitigation in self.active_mitigations
            if mitigation.expires_time > now
        ]
    
    def remove_mitigation(self, source_id: str, mitigation_type: str = None) -> bool:
        """Remove specific mitigation factor(s)"""
        
        initial_count = len(self.active_mitigations)
        
        self.active_mitigations = [
            mitigation for mitigation in self.active_mitigations
            if not (mitigation.source_id == source_id and 
                   (mitigation_type is None or mitigation.factor_type == mitigation_type))
        ]
        
        return len(self.active_mitigations) < initial_count
    
    def get_mitigation_forecast(self, hours_ahead: float = 24) -> Dict[str, Any]:
        """Get forecast of mitigation effects over time"""
        
        now = datetime.now()
        forecast_time = now + timedelta(hours=hours_ahead)
        
        # Find mitigations that will expire within forecast period
        expiring = [
            mitigation for mitigation in self.active_mitigations
            if now < mitigation.expires_time <= forecast_time
        ]
        
        # Calculate remaining effectiveness over time
        forecast = {
            'current_mitigations': len(self.active_mitigations),
            'expiring_within_period': len(expiring),
            'timeline': [],
            'effectiveness_trend': {}
        }
        
        # Create timeline of expiring mitigations
        for mitigation in sorted(expiring, key=lambda m: m.expires_time):
            forecast['timeline'].append({
                'time': mitigation.expires_time,
                'type': mitigation.factor_type,
                'effectiveness_lost': mitigation.effectiveness,
                'affected_sources': mitigation.affected_sources
            })
        
        return forecast