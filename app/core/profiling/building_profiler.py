"""
Building generation profiling system.
Provides detailed performance tracking for building and POI generation.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import time
import logging
from functools import wraps
from dataclasses import dataclass, field
from statistics import mean, median, quantiles
from collections import defaultdict
import threading
from app.core.utils.monitoring import PerformanceMonitor

logger = logging.getLogger(__name__)

@dataclass
class BuildingProfile:
    """Profile data for a single building generation."""
    building_id: str
    building_type: str
    size: Tuple[float, float, float]  # width, height, depth
    start_time: float
    end_time: float = field(default=0.0)
    component_times: Dict[str, float] = field(default_factory=dict)
    memory_usage: Dict[str, int] = field(default_factory=dict)
    error_count: int = 0
    warnings: List[str] = field(default_factory=list)

    @property
    def total_time(self) -> float:
        """Get total generation time in seconds."""
        if self.end_time == 0:
            return 0
        return self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary format."""
        return {
            'building_id': self.building_id,
            'building_type': self.building_type,
            'size': {
                'width': self.size[0],
                'height': self.size[1],
                'depth': self.size[2]
            },
            'total_time': self.total_time,
            'component_times': self.component_times,
            'memory_usage': self.memory_usage,
            'error_count': self.error_count,
            'warnings': self.warnings
        }

class BuildingProfiler:
    """Profiler for building generation performance."""
    
    def __init__(self):
        self.profiles: Dict[str, BuildingProfile] = {}
        self.current_profile: Optional[BuildingProfile] = None
        self._lock = threading.Lock()
        self.performance_monitor = PerformanceMonitor()
        
        # Performance thresholds
        self.time_threshold = 2.0  # seconds
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
        
        # Component tracking
        self.component_stats: Dict[str, List[float]] = defaultdict(list)
    
    def start_profile(
        self,
        building_id: str,
        building_type: str,
        size: Tuple[float, float, float]
    ) -> None:
        """Start profiling a building generation."""
        profile = BuildingProfile(
            building_id=building_id,
            building_type=building_type,
            size=size,
            start_time=time.time()
        )
        
        with self._lock:
            self.current_profile = profile
            self.profiles[building_id] = profile
    
    def end_profile(self) -> None:
        """End profiling the current building generation."""
        if not self.current_profile:
            return
            
        self.current_profile.end_time = time.time()
        
        # Check performance thresholds
        if self.current_profile.total_time > self.time_threshold:
            logger.warning(
                f"Building {self.current_profile.building_id} generation exceeded "
                f"time threshold: {self.current_profile.total_time:.2f}s"
            )
            self.current_profile.warnings.append(
                f"Generation time exceeded threshold: {self.current_profile.total_time:.2f}s"
            )
        
        # Update component statistics
        with self._lock:
            for component, time_taken in self.current_profile.component_times.items():
                self.component_stats[component].append(time_taken)
        
        # Record metrics in the main performance monitor
        self.performance_monitor.track_request_time(
            f"building_generation.{self.current_profile.building_type}",
            self.current_profile.total_time
        )
        
        self.current_profile = None
    
    def track_component(self, component_name: str):
        """Decorator to track time spent in a building generation component."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.current_profile:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                try:
                    return func(*args, **kwargs)
                finally:
                    end_time = time.time()
                    component_time = end_time - start_time
                    
                    with self._lock:
                        self.current_profile.component_times[component_name] = component_time
            return wrapper
        return decorator
    
    def get_profile(self, building_id: str) -> Optional[Dict[str, Any]]:
        """Get profile data for a specific building."""
        profile = self.profiles.get(building_id)
        return profile.to_dict() if profile else None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall building generation statistics."""
        with self._lock:
            if not self.profiles:
                return {
                    'total_buildings': 0,
                    'average_time': 0,
                    'median_time': 0,
                    'p95_time': 0,
                    'component_stats': {},
                    'type_stats': {},
                    'size_correlation': 0
                }
            
            # Calculate overall timing statistics
            times = [p.total_time for p in self.profiles.values()]
            
            # Calculate statistics by building type
            type_stats = defaultdict(list)
            for profile in self.profiles.values():
                type_stats[profile.building_type].append(profile.total_time)
            
            type_averages = {
                btype: mean(times) for btype, times in type_stats.items()
            }
            
            # Calculate component statistics
            component_stats = {
                component: {
                    'average': mean(times),
                    'median': median(times),
                    'p95': quantiles(times, n=20)[18] if len(times) >= 20 else max(times)
                }
                for component, times in self.component_stats.items()
            }
            
            # Calculate size correlation
            # Using total volume as size metric
            sizes = [p.size[0] * p.size[1] * p.size[2] for p in self.profiles.values()]
            if len(sizes) > 1:
                # Simple correlation coefficient
                mean_size = mean(sizes)
                mean_time = mean(times)
                covariance = sum((s - mean_size) * (t - mean_time) for s, t in zip(sizes, times))
                variance_size = sum((s - mean_size) ** 2 for s in sizes)
                variance_time = sum((t - mean_time) ** 2 for t in times)
                correlation = covariance / ((variance_size * variance_time) ** 0.5) if variance_size and variance_time else 0
            else:
                correlation = 0
            
            return {
                'total_buildings': len(self.profiles),
                'average_time': mean(times),
                'median_time': median(times),
                'p95_time': quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
                'component_stats': component_stats,
                'type_stats': type_averages,
                'size_correlation': correlation
            }
    
    def reset_statistics(self) -> None:
        """Reset all profiling data."""
        with self._lock:
            self.profiles.clear()
            self.component_stats.clear()
            self.current_profile = None

# Global instance
building_profiler = BuildingProfiler() 