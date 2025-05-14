"""
Integration Loader for Monitoring System Adapters

Discovers and registers all available monitoring system adapters.
"""

from .adapter_base import AdapterBase
from .prometheus_adapter import PrometheusAdapter
from .cloudwatch_adapter import CloudWatchAdapter
from .nagios_adapter import NagiosAdapter

# Registry of available adapters
ADAPTER_REGISTRY = {
    'prometheus': PrometheusAdapter,
    'cloudwatch': CloudWatchAdapter,
    'nagios': NagiosAdapter,
    # Add other adapters here (e.g., 'datadog': DatadogAdapter)
}

def get_adapter(system_name: str, config=None) -> AdapterBase:
    """
    Get an adapter instance for the given monitoring system.
    """
    adapter_cls = ADAPTER_REGISTRY.get(system_name.lower())
    if not adapter_cls:
        raise ValueError(f"No adapter registered for system: {system_name}")
    return adapter_cls(config=config) 