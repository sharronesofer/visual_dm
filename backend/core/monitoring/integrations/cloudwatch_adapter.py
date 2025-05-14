"""
CloudWatch Integration Adapter

Handles incoming alerts from AWS CloudWatch (via SNS) and normalizes them for the AlertProcessor.
"""

import logging
from typing import Any, Dict, List, Optional
from .adapter_base import AdapterBase

logger = logging.getLogger(__name__)

class CloudWatchAdapter(AdapterBase):
    """
    Adapter for integrating AWS CloudWatch alerts (via SNS HTTP/S).
    Supports webhook (push) integration.
    """
    def fetch_alerts(self) -> List[Dict]:
        """
        Polling is not supported for CloudWatch (push/webhook only).
        """
        raise NotImplementedError("CloudWatchAdapter does not support polling; use handle_webhook.")

    def handle_webhook(self, request_data: Dict) -> List[Dict]:
        """
        Handle incoming AWS SNS notification payload for CloudWatch alarms.
        Returns a list of normalized alert dicts.
        """
        # SNS sends a single message per request
        try:
            normalized = self.normalize_alert(request_data)
            return [normalized]
        except Exception as e:
            self.handle_error(e, context={'raw_alert': request_data})
            return []

    def normalize_alert(self, raw_alert: Dict) -> Dict:
        """
        Normalize a CloudWatch/SNS alert to the AlertProcessor schema.
        """
        # CloudWatch alarm notifications are JSON-encoded in the 'Message' field
        message = raw_alert.get('Message')
        if isinstance(message, str):
            import json
            try:
                message = json.loads(message)
            except Exception as e:
                self.handle_error(e, context={'raw_alert': raw_alert})
                message = {}
        alarm_name = message.get('AlarmName', 'CloudWatch Alarm')
        new_state = message.get('NewStateValue', 'ALARM')
        reason = message.get('NewStateReason', '')
        state_change_time = message.get('StateChangeTime')
        severity = message.get('Severity', 'P3').upper()
        metric_name = message.get('Trigger', {}).get('MetricName')
        threshold = message.get('Trigger', {}).get('Threshold')
        unit = message.get('Trigger', {}).get('Unit')
        dashboard_url = message.get('DashboardURL')
        runbook_url = message.get('RunbookURL')
        # Map CloudWatch fields to AlertProcessor schema
        normalized = {
            'name': alarm_name,
            'severity': severity,
            'system': 'cloudwatch',
            'description': reason,
            'status': new_state.lower(),
            'created_at': state_change_time,
            'value': message.get('NewStateValue'),
            'unit': unit,
            'threshold': threshold,
            'metric_name': metric_name,
            'dashboard_url': dashboard_url,
            'runbook_url': runbook_url,
            'raw': raw_alert
        }
        return normalized 