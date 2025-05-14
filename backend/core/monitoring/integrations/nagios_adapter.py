"""
Nagios Integration Adapter

Handles incoming alerts from Nagios (via NRDP, NSCA, or custom HTTP) and normalizes them for the AlertProcessor.
"""

import logging
from typing import Any, Dict, List, Optional
from .adapter_base import AdapterBase

logger = logging.getLogger(__name__)

class NagiosAdapter(AdapterBase):
    """
    Adapter for integrating Nagios alerts (via NRDP, NSCA, or HTTP).
    Supports webhook (push) integration.
    """
    def fetch_alerts(self) -> List[Dict]:
        """
        Polling is not supported for Nagios (push/webhook only).
        """
        raise NotImplementedError("NagiosAdapter does not support polling; use handle_webhook.")

    def handle_webhook(self, request_data: Dict) -> List[Dict]:
        """
        Handle incoming Nagios alert payload (NRDP/NSCA/custom HTTP).
        Returns a list of normalized alert dicts.
        """
        # Nagios may send a single alert or a batch
        alerts = request_data.get('alerts')
        if alerts is None:
            alerts = [request_data]
        normalized_alerts = []
        for raw_alert in alerts:
            try:
                normalized = self.normalize_alert(raw_alert)
                normalized_alerts.append(normalized)
            except Exception as e:
                self.handle_error(e, context={'raw_alert': raw_alert})
        return normalized_alerts

    def normalize_alert(self, raw_alert: Dict) -> Dict:
        """
        Normalize a Nagios alert to the AlertProcessor schema.
        """
        # Nagios alert fields may vary by integration method
        host = raw_alert.get('host_name') or raw_alert.get('host')
        service = raw_alert.get('service_description') or raw_alert.get('service')
        state = raw_alert.get('state', 'UNKNOWN')
        output = raw_alert.get('plugin_output', '')
        long_output = raw_alert.get('long_plugin_output', '')
        timestamp = raw_alert.get('timestamp') or raw_alert.get('last_check')
        severity = raw_alert.get('severity', 'P3').upper()
        dashboard_url = raw_alert.get('dashboard_url')
        runbook_url = raw_alert.get('runbook_url')
        # Map Nagios fields to AlertProcessor schema
        normalized = {
            'name': f"Nagios: {service or host}",
            'severity': severity,
            'system': 'nagios',
            'description': output,
            'details': long_output,
            'status': state.lower(),
            'created_at': timestamp,
            'host': host,
            'service': service,
            'dashboard_url': dashboard_url,
            'runbook_url': runbook_url,
            'raw': raw_alert
        }
        return normalized 