"""
Development features system for managing game development and testing.
"""

from typing import Dict, List, Optional, Set, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class DevelopmentFeatureType(str, Enum):
    """Types of development features."""
    DEBUG = "debug"
    TESTING = "testing"
    MONITORING = "monitoring"
    ANALYTICS = "analytics"
    PERFORMANCE = "performance"
    SECURITY = "security"
    DEPLOYMENT = "deployment"

class DevelopmentFeature(BaseModel):
    """Base development feature model."""
    id: str
    name: str
    type: DevelopmentFeatureType
    description: str
    enabled: bool = Field(default=False)
    config: Dict = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    last_update: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict = Field(default_factory=dict)

class DevelopmentSystem(BaseModel):
    """System for managing development features."""
    features: Dict[str, DevelopmentFeature] = Field(default_factory=dict)
    environment: str = Field(default="development")
    version: str = Field(default="0.1.0")
    last_update: datetime = Field(default_factory=datetime.utcnow)

    def add_feature(self, feature: DevelopmentFeature):
        """Add a new development feature."""
        self.features[feature.id] = feature
        self.last_update = datetime.utcnow()

    def remove_feature(self, feature_id: str) -> bool:
        """Remove a development feature."""
        if feature_id in self.features:
            del self.features[feature_id]
            self.last_update = datetime.utcnow()
            return True
        return False

    def enable_feature(self, feature_id: str) -> bool:
        """Enable a development feature."""
        if feature_id in self.features:
            self.features[feature_id].enabled = True
            self.last_update = datetime.utcnow()
            return True
        return False

    def disable_feature(self, feature_id: str) -> bool:
        """Disable a development feature."""
        if feature_id in self.features:
            self.features[feature_id].enabled = False
            self.last_update = datetime.utcnow()
            return True
        return False

    def get_enabled_features(self) -> List[DevelopmentFeature]:
        """Get all enabled development features."""
        return [f for f in self.features.values() if f.enabled]

    def update_feature_config(self, feature_id: str, 
                            config: Dict) -> bool:
        """Update a feature's configuration."""
        if feature_id in self.features:
            self.features[feature_id].config.update(config)
            self.last_update = datetime.utcnow()
            return True
        return False

class DebugSystem(BaseModel):
    """System for managing debug features."""
    enabled: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    breakpoints: Set[str] = Field(default_factory=set)
    watch_variables: Dict[str, Any] = Field(default_factory=dict)
    last_update: datetime = Field(default_factory=datetime.utcnow)

    def add_breakpoint(self, breakpoint_id: str):
        """Add a breakpoint."""
        self.breakpoints.add(breakpoint_id)
        self.last_update = datetime.utcnow()

    def remove_breakpoint(self, breakpoint_id: str) -> bool:
        """Remove a breakpoint."""
        if breakpoint_id in self.breakpoints:
            self.breakpoints.remove(breakpoint_id)
            self.last_update = datetime.utcnow()
            return True
        return False

    def add_watch_variable(self, name: str, value: Any):
        """Add a variable to watch."""
        self.watch_variables[name] = value
        self.last_update = datetime.utcnow()

    def remove_watch_variable(self, name: str) -> bool:
        """Remove a watched variable."""
        if name in self.watch_variables:
            del self.watch_variables[name]
            self.last_update = datetime.utcnow()
            return True
        return False

    class Config:
        arbitrary_types_allowed = True

class TestingSystem(BaseModel):
    """System for managing testing features."""
    enabled: bool = Field(default=False)
    test_cases: Dict[str, Dict] = Field(default_factory=dict)
    test_results: Dict[str, List[Dict]] = Field(default_factory=dict)
    coverage: Dict[str, float] = Field(default_factory=dict)
    last_update: datetime = Field(default_factory=datetime.utcnow)

    def add_test_case(self, test_id: str, test_case: Dict):
        """Add a test case."""
        self.test_cases[test_id] = test_case
        self.last_update = datetime.utcnow()

    def remove_test_case(self, test_id: str) -> bool:
        """Remove a test case."""
        if test_id in self.test_cases:
            del self.test_cases[test_id]
            self.last_update = datetime.utcnow()
            return True
        return False

    def add_test_result(self, test_id: str, result: Dict):
        """Add a test result."""
        if test_id not in self.test_results:
            self.test_results[test_id] = []
        self.test_results[test_id].append(result)
        self.last_update = datetime.utcnow()

    def update_coverage(self, component: str, coverage: float):
        """Update test coverage for a component."""
        self.coverage[component] = coverage
        self.last_update = datetime.utcnow()

class MonitoringSystem(BaseModel):
    """System for managing monitoring features."""
    enabled: bool = Field(default=False)
    metrics: Dict[str, List[Dict]] = Field(default_factory=dict)
    alerts: Dict[str, Dict] = Field(default_factory=dict)
    thresholds: Dict[str, float] = Field(default_factory=dict)
    last_update: datetime = Field(default_factory=datetime.utcnow)

    def add_metric(self, metric_id: str, value: Dict):
        """Add a metric value."""
        if metric_id not in self.metrics:
            self.metrics[metric_id] = []
        self.metrics[metric_id].append({
            **value,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.last_update = datetime.utcnow()

    def set_alert(self, alert_id: str, alert: Dict):
        """Set an alert configuration."""
        self.alerts[alert_id] = alert
        self.last_update = datetime.utcnow()

    def set_threshold(self, metric_id: str, threshold: float):
        """Set a threshold for a metric."""
        self.thresholds[metric_id] = threshold
        self.last_update = datetime.utcnow()

    def check_alerts(self) -> List[Dict]:
        """Check for any triggered alerts."""
        triggered = []
        for alert_id, alert in self.alerts.items():
            metric_id = alert.get("metric_id")
            if metric_id in self.metrics and metric_id in self.thresholds:
                latest = self.metrics[metric_id][-1]
                threshold = self.thresholds[metric_id]
                if alert.get("condition") == "above" and latest["value"] > threshold:
                    triggered.append({
                        "alert_id": alert_id,
                        "metric_id": metric_id,
                        "value": latest["value"],
                        "threshold": threshold,
                        "timestamp": latest["timestamp"]
                    })
                elif alert.get("condition") == "below" and latest["value"] < threshold:
                    triggered.append({
                        "alert_id": alert_id,
                        "metric_id": metric_id,
                        "value": latest["value"],
                        "threshold": threshold,
                        "timestamp": latest["timestamp"]
                    })
        return triggered 