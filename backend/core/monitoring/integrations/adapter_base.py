"""
Adapter Base Class for Monitoring System Integrations

Defines the standard interface for all monitoring system adapters.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class AdapterBase:
    """
    Base class for monitoring system integration adapters.
    All adapters should inherit from this class and implement required methods.
    """
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logger

    def fetch_alerts(self) -> List[Dict]:
        """
        Fetch alerts from the monitoring system (for polling-based integrations).
        Returns a list of raw alert objects.
        """
        raise NotImplementedError("fetch_alerts() must be implemented by adapter.")

    def handle_webhook(self, request_data: Dict) -> List[Dict]:
        """
        Handle incoming webhook data (for push-based integrations).
        Returns a list of raw alert objects.
        """
        raise NotImplementedError("handle_webhook() must be implemented by adapter.")

    def normalize_alert(self, raw_alert: Dict) -> Dict:
        """
        Normalize a raw alert from the monitoring system to the AlertProcessor schema.
        Returns a normalized alert dictionary.
        """
        raise NotImplementedError("normalize_alert() must be implemented by adapter.")

    def handle_error(self, error: Exception, context: Optional[Dict] = None) -> None:
        """
        Handle errors during integration (logging, retries, notifications).
        """
        self.logger.error(f"Integration error: {error}", exc_info=True)
        # Optionally implement retry or notification logic here 