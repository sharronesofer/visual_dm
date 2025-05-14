#!/usr/bin/env python3
"""
Escalation System Test Script

This script tests the alert escalation system with various mock alerts
to ensure proper handling and escalation.
"""

import os
import sys
import json
import yaml
import logging
import datetime
import time
from pathlib import Path

# Add the parent directory to the module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from backend.core.monitoring.alert_processor import AlertProcessor
from backend.core.monitoring.escalation_manager import EscalationManager
from backend.core.monitoring.notification_dispatcher import NotificationDispatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('escalation_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Create output directory if it doesn't exist
output_dir = Path('test_results')
output_dir.mkdir(exist_ok=True)

def save_test_result(alert_data, result, test_name):
    """Save test result to a file."""
    filename = output_dir / f"{test_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump({
            'alert_data': alert_data,
            'result': result
        }, f, indent=2, default=str)
    logger.info(f"Test result saved to {filename}")

def test_p1_critical_alert():
    """Test handling of a P1 (Critical) alert."""
    logger.info("=== Testing P1 Critical Alert ===")
    
    processor = AlertProcessor()
    
    alert_data = {
        'name': 'Database Connection Failures',
        'severity': 'P1',
        'system': 'database_system',
        'description': 'Multiple database connection failures detected affecting all services',
        'value': 85,
        'unit': '%',
        'threshold': 10,
        'impact': 'Critical impact on all services. Users unable to access the platform.'
    }
    
    # Process the alert
    result = processor.process_alert(alert_data)
    logger.info(f"Alert processed with action: {result.get('action')}")
    
    # Save the test result
    save_test_result(alert_data, result, 'p1_critical_alert')
    
    # For testing purposes, we can simulate time passing and check for escalation
    processed_alert = result.get('alert', {})
    
    # Simulate not being acknowledged within the timeframe
    processed_alert['created_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
    ).isoformat()
    
    # Check for escalation
    escalation_result = processor.check_and_escalate(processed_alert)
    logger.info(f"Escalation result: {escalation_result.get('action')}")
    
    # Save the escalation result
    save_test_result(processed_alert, escalation_result, 'p1_escalation')
    
    return result, escalation_result

def test_p2_high_alert():
    """Test handling of a P2 (High) alert."""
    logger.info("=== Testing P2 High Alert ===")
    
    processor = AlertProcessor()
    
    alert_data = {
        'name': 'High CPU Usage',
        'severity': 'P2',
        'system': 'web_server',
        'description': 'Web server CPU usage exceeded 90% for more than 5 minutes',
        'value': 92.5,
        'unit': '%',
        'threshold': 90,
        'impact': 'Potential slowdown in web server response times affecting user experience'
    }
    
    # Process the alert
    result = processor.process_alert(alert_data)
    logger.info(f"Alert processed with action: {result.get('action')}")
    
    # Save the test result with correct name for auto-recovery
    if result.get('action') == 'auto_recovered':
        save_test_result(alert_data, result, 'auto_recovery')
    else:
        save_test_result(alert_data, result, 'p2_high_alert')
    
    # For testing purposes, we can simulate time passing and check for escalation
    processed_alert = result.get('alert', {})
    
    # Simulate update but not resolution within the timeframe
    processed_alert['created_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
    ).isoformat()
    processed_alert['acknowledged_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
    ).isoformat()
    processed_alert['last_updated_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
    ).isoformat()
    processed_alert['status'] = 'acknowledged'
    
    # Check for escalation
    escalation_result = processor.check_and_escalate(processed_alert)
    logger.info(f"Escalation result: {escalation_result.get('action')}")
    
    # Save the escalation result
    save_test_result(processed_alert, escalation_result, 'p2_escalation')
    
    return result, escalation_result

def test_p3_medium_alert():
    """Test handling of a P3 (Medium) alert."""
    logger.info("=== Testing P3 Medium Alert ===")
    
    processor = AlertProcessor()
    
    alert_data = {
        'name': 'API Response Time',
        'severity': 'P3',
        'system': 'api_gateway',
        'description': 'API response times exceeded 500ms for more than 10 minutes',
        'value': 650,
        'unit': 'ms',
        'threshold': 500,
        'impact': 'Some API requests experiencing slower response times'
    }
    
    # Process the alert
    result = processor.process_alert(alert_data)
    logger.info(f"Alert processed with action: {result.get('action')}")
    
    # Save the test result
    save_test_result(alert_data, result, 'p3_medium_alert')
    
    # For testing purposes, we can simulate resolution before escalation
    processed_alert = result.get('alert', {})
    
    # Simulate acknowledgment and resolution within the timeframe
    processed_alert['created_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
    ).isoformat()
    processed_alert['acknowledged_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15)
    ).isoformat()
    processed_alert['resolved_at'] = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)
    ).isoformat()
    processed_alert['status'] = 'resolved'
    
    # Check for escalation (should not escalate since it's resolved)
    escalation_result = processor.check_and_escalate(processed_alert)
    logger.info(f"Escalation result: {escalation_result.get('action')}")
    
    # Save the escalation result
    save_test_result(processed_alert, escalation_result, 'p3_no_escalation')
    
    return result, escalation_result

def test_p4_low_alert():
    """Test handling of a P4 (Low) alert."""
    logger.info("=== Testing P4 Low Alert ===")
    
    processor = AlertProcessor()
    
    alert_data = {
        'name': 'Low Disk Space Warning',
        'severity': 'P4',
        'system': 'backup_server',
        'description': 'Disk usage on backup server exceeded 70%',
        'value': 72,
        'unit': '%',
        'threshold': 70,
        'impact': 'No immediate impact, but requires cleanup within the next week'
    }
    
    # Process the alert
    result = processor.process_alert(alert_data)
    logger.info(f"Alert processed with action: {result.get('action')}")
    
    # Save the test result
    save_test_result(alert_data, result, 'p4_low_alert')
    
    return result, None

def test_suppression_rule():
    """Test alert suppression rules."""
    logger.info("=== Testing Alert Suppression Rules ===")
    
    processor = AlertProcessor()
    
    # Create an alert that should be suppressed by maintenance window
    alert_data = {
        'name': 'Database Connection Errors',
        'severity': 'P2',
        'system': 'database_system',
        'description': 'Several database connection errors detected',
        'value': 5,
        'unit': 'errors',
        'threshold': 3
    }
    
    # Temporarily modify suppression rules for testing
    # In a real implementation, you would have a proper test configuration
    # Here we're directly accessing the internal config for simplicity
    original_rules = processor.suppression_rules
    
    # Create a test suppression rule
    test_rule = {
        'maintenance_windows': [
            {
                'name': 'Test Database Maintenance',
                'suppress_alerts': [
                    'Database Connection Errors'
                ],
                'schedule': [
                    'Always'  # For testing purposes, always active
                ]
            }
        ]
    }
    
    processor.suppression_rules = test_rule
    
    # Process the alert (should be suppressed)
    result = processor.process_alert(alert_data)
    logger.info(f"Alert processed with action: {result.get('action')}")
    
    # Restore original rules
    processor.suppression_rules = original_rules
    
    # Save the test result
    save_test_result(alert_data, result, 'suppression_rule')
    
    return result, None

def test_auto_recovery():
    """Test auto-recovery mechanism."""
    logger.info("=== Testing Auto-Recovery Mechanism ===")
    
    processor = AlertProcessor()
    
    # Create an alert that should trigger auto-recovery
    alert_data = {
        'name': 'Service Not Responding',
        'severity': 'P2',
        'system': 'web_server',
        'description': 'Web service not responding to health checks',
        'value': 0,
        'unit': 'responses',
        'threshold': 1
    }
    
    # Temporarily modify auto-recovery config for testing
    original_config = processor.auto_recovery_config
    
    # Create a test auto-recovery config
    test_config = {
        'enabled': True,
        'actions': {
            'restart_service': {
                'conditions': [
                    {
                        'alert': 'Service Not Responding',
                        'severity': ['P1', 'P2'],
                        'attempt_count_max': 2,
                        'wait_between_attempts_seconds': 1  # Short for testing
                    }
                ]
            }
        }
    }
    
    processor.auto_recovery_config = test_config
    
    # Process the alert (should attempt auto-recovery)
    result = processor.process_alert(alert_data)
    logger.info(f"Alert processed with action: {result.get('action')}")
    
    # Restore original config
    processor.auto_recovery_config = original_config
    
    # Save the test result as 'auto_recovery'
    save_test_result(alert_data, result, 'auto_recovery')
    
    return result, None

def test_system_override():
    """Test system-specific overrides."""
    logger.info("=== Testing System-Specific Overrides ===")
    
    processor = AlertProcessor()
    
    # Create an alert for a system with overrides
    alert_data = {
        'name': 'Payment Processing Failures',
        'severity': 'P2',  # Should be automatically upgraded to P1 for payment system
        'system': 'payment_system',
        'description': 'Payment processing failures detected',
        'value': 0.6,  # 0.6% failure rate
        'unit': '%',
        'threshold': 0.5,
        'payment_provider': 'Example Provider',
        'revenue_impact': '$5,000 per hour estimated'
    }
    
    # Process the alert
    result = processor.process_alert(alert_data)
    logger.info(f"Alert processed with action: {result.get('action')}")
    
    # Save the test result
    save_test_result(alert_data, result, 'system_override')
    
    return result, None

def run_all_tests():
    """Run all test scenarios."""
    logger.info("Starting escalation system tests")
    
    test_results = {
        'p1_critical_alert': test_p1_critical_alert(),
        'p2_high_alert': test_p2_high_alert(),
        'p3_medium_alert': test_p3_medium_alert(),
        'p4_low_alert': test_p4_low_alert(),
        'suppression_rule': test_suppression_rule(),
        'auto_recovery': test_auto_recovery(),
        'system_override': test_system_override()
    }
    
    logger.info("All tests completed")
    
    # Save summary report
    summary = {
        'timestamp': datetime.datetime.now().isoformat(),
        'tests_run': len(test_results),
        'test_names': list(test_results.keys())
    }
    
    with open(output_dir / 'test_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Test summary saved to {output_dir / 'test_summary.json'}")

if __name__ == '__main__':
    # Create the test directory
    os.makedirs('backend/core/monitoring/tests', exist_ok=True)
    
    # Run all tests
    run_all_tests() 