#!/usr/bin/env python3
"""
Alert Handler Script

This script demonstrates how to use the alert processor to handle alerts.
In a real implementation, this would be an API endpoint or a message queue consumer.
"""

import sys
import os
import json
import logging
import argparse
import datetime
from typing import Dict, Any

# Add the parent directory to the module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.core.monitoring.alert_processor import AlertProcessor
from backend.core.monitoring.integrations import get_adapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_example_alert() -> None:
    """
    Process an example alert to demonstrate the alert processor.
    """
    # Create an alert processor
    processor = AlertProcessor()
    
    # Example alert data
    alert_data = {
        'name': 'High CPU Usage',
        'severity': 'P2',
        'system': 'web_server',
        'description': 'Web server CPU usage exceeded 90% for more than 5 minutes',
        'value': 92.5,
        'unit': '%',
        'threshold': 90,
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'dashboard_url': 'https://grafana.example.com/d/abc123/web-server-metrics',
        'runbook_url': 'https://runbooks.example.com/high-cpu-usage',
        'impact': 'Potential slowdown in web server response times affecting user experience'
    }
    
    logger.info("Processing example alert")
    
    # Process the alert
    result = processor.process_alert(alert_data)
    
    # Log the result
    logger.info(f"Alert processed with action: {result.get('action')}")
    logger.info(f"Alert ID: {result.get('alert', {}).get('id')}")
    
    # Save the processed alert to a file for demonstration purposes
    processed_alert = result.get('alert', {})
    with open('example_processed_alert.json', 'w') as file:
        json.dump(processed_alert, file, indent=2)
    
    logger.info(f"Processed alert saved to example_processed_alert.json")
    
    # Now simulate an acknowledgment after 2 minutes
    processed_alert['status'] = 'acknowledged'
    processed_alert['acknowledged_at'] = (
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=2)
    ).isoformat()
    
    # And simulate a resolution after 10 minutes
    processed_alert['status'] = 'resolved'
    processed_alert['resolved_at'] = (
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    ).isoformat()
    
    logger.info("Simulated alert acknowledgment and resolution")
    
    # Example of checking escalation (would not escalate since it's resolved)
    escalation_result = processor.check_and_escalate(processed_alert)
    logger.info(f"Escalation check result: {escalation_result.get('action')}")
    
    # Now demonstrate escalation with an unacknowledged alert
    unacknowledged_alert = alert_data.copy()
    unacknowledged_alert['id'] = 'unacknowledged-alert-id'
    unacknowledged_alert['created_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
    ).isoformat()
    unacknowledged_alert['status'] = 'pending'
    unacknowledged_alert['current_escalation_level'] = 'initial_response'
    unacknowledged_alert['initial_response_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
    ).isoformat()
    
    logger.info("Checking escalation for unacknowledged alert")
    escalation_result = processor.check_and_escalate(unacknowledged_alert)
    logger.info(f"Escalation result: {escalation_result.get('action')}")
    
    if escalation_result.get('action') == 'escalated':
        logger.info(f"Alert escalated to level: {escalation_result.get('level')}")
        
        # Save the escalated alert to a file for demonstration purposes
        escalated_alert = escalation_result.get('alert', {})
        with open('example_escalated_alert.json', 'w') as file:
            json.dump(escalated_alert, file, indent=2)
        
        logger.info(f"Escalated alert saved to example_escalated_alert.json")

def process_critical_alert() -> None:
    """
    Process a critical (P1) alert to demonstrate the escalation process.
    """
    # Create an alert processor
    processor = AlertProcessor()
    
    # Critical alert data
    alert_data = {
        'name': 'Database Connection Failures',
        'severity': 'P1',
        'system': 'database_system',
        'description': 'Multiple database connection failures detected affecting all services',
        'value': 85,
        'unit': '%',
        'threshold': 10,
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'dashboard_url': 'https://grafana.example.com/d/xyz789/database-metrics',
        'runbook_url': 'https://runbooks.example.com/database-connection-failures',
        'impact': 'Critical impact on all services. Users unable to access the platform.'
    }
    
    logger.info("Processing critical P1 alert")
    
    # Process the alert
    result = processor.process_alert(alert_data)
    
    # Log the result
    logger.info(f"Alert processed with action: {result.get('action')}")
    logger.info(f"Alert ID: {result.get('alert', {}).get('id')}")
    
    # Save the processed alert to a file for demonstration purposes
    processed_alert = result.get('alert', {})
    with open('example_critical_alert.json', 'w') as file:
        json.dump(processed_alert, file, indent=2)
    
    logger.info(f"Processed critical alert saved to example_critical_alert.json")

def process_prometheus_webhook_example() -> None:
    """
    Simulate receiving a Prometheus Alertmanager webhook and process it using the integration adapter.
    """
    logger.info("Processing Prometheus webhook example")
    # Example Prometheus Alertmanager webhook payload
    webhook_payload = {
        'alerts': [
            {
                'status': 'firing',
                'labels': {
                    'alertname': 'HighMemoryUsage',
                    'severity': 'P2',
                    'instance': 'app_server_1'
                },
                'annotations': {
                    'description': 'Memory usage exceeded 90% for 10 minutes',
                    'summary': 'High memory usage on app_server_1',
                    'dashboard': 'https://grafana.example.com/d/xyz/app-metrics',
                    'runbook': 'https://runbooks.example.com/high-memory-usage'
                },
                'startsAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'endsAt': None
            }
        ]
    }
    # Get the Prometheus adapter
    adapter = get_adapter('prometheus')
    normalized_alerts = adapter.handle_webhook(webhook_payload)
    logger.info(f"Normalized {len(normalized_alerts)} alert(s) from Prometheus webhook")
    processor = AlertProcessor()
    for alert in normalized_alerts:
        result = processor.process_alert(alert)
        logger.info(f"Processed alert: {alert.get('name')} | Action: {result.get('action')}")

def main():
    """
    Main entry point for the script.
    """
    parser = argparse.ArgumentParser(description='Alert Handler Example')
    parser.add_argument('--critical', action='store_true', help='Process a critical P1 alert example')
    args = parser.parse_args()
    
    if args.critical:
        process_critical_alert()
    else:
        process_example_alert()

if __name__ == '__main__':
    main() 