"""
Prometheus Integration Adapter

Handles incoming alerts from Prometheus Alertmanager via webhook and normalizes them for the AlertProcessor.
"""

import logging
from typing import Any, Dict, List, Optional
from .adapter_base import AdapterBase

logger = logging.getLogger(__name__)

class PrometheusAdapter(AdapterBase):
    """
    Adapter for integrating Prometheus Alertmanager alerts.
    Supports webhook (push) integration.
    """
    def fetch_alerts(self) -> List[Dict]:
        """
        Polling is not supported for Prometheus (push/webhook only).
        """
        raise NotImplementedError("PrometheusAdapter does not support polling; use handle_webhook.")

    def handle_webhook(self, request_data: Dict) -> List[Dict]:
        """
        Handle incoming Prometheus Alertmanager webhook payload.
        Returns a list of normalized alert dicts.
        """
        alerts = request_data.get('alerts', [])
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
        Normalize a Prometheus alert to the AlertProcessor schema.
        """
        labels = raw_alert.get('labels', {})
        annotations = raw_alert.get('annotations', {})
        starts_at = raw_alert.get('startsAt')
        ends_at = raw_alert.get('endsAt')
        status = raw_alert.get('status', 'firing')

        # Map Prometheus fields to AlertProcessor schema
        normalized = {
            'name': labels.get('alertname', 'Prometheus Alert'),
            'severity': labels.get('severity', 'P3').upper(),
            'system': labels.get('instance', 'prometheus'),
            'description': annotations.get('description', ''),
            'summary': annotations.get('summary', ''),
            'value': annotations.get('value'),
            'unit': annotations.get('unit'),
            'threshold': annotations.get('threshold'),
            'status': status,
            'created_at': starts_at,
            'resolved_at': ends_at if status == 'resolved' else None,
            'labels': labels,
            'annotations': annotations,
            'dashboard_url': annotations.get('dashboard'),
            'runbook_url': annotations.get('runbook'),
            'raw': raw_alert
        }
        return normalized 