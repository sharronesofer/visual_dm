#!/usr/bin/env python3
"""
Test Results Analyzer

This script analyzes the results of the alert escalation system tests
and generates a report.
"""

import os
import sys
import json
import logging
import datetime
import argparse
from pathlib import Path
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_test_results(results_dir):
    """Load all test results from the specified directory."""
    results_dir = Path(results_dir)
    if not results_dir.exists() or not results_dir.is_dir():
        logger.error(f"Results directory not found: {results_dir}")
        return {}
    
    results = {}
    for file_path in results_dir.glob('*.json'):
        if file_path.name == 'test_summary.json':
            continue
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Extract test name from filename (remove timestamp, keep full logical name)
                test_name = file_path.stem
                # Remove trailing timestamp if present (e.g., _20250514_182927)
                if '_' in test_name:
                    parts = test_name.rsplit('_', 3)
                    if len(parts) >= 3 and all(p.isdigit() for p in parts[-3:]):
                        test_name = '_'.join(parts[:-3])
                results[test_name] = data
        except Exception as e:
            logger.error(f"Error loading test result from {file_path}: {str(e)}")
    
    return results

def analyze_alert_processing(results):
    """Analyze the alert processing results."""
    processing_results = []
    
    for test_name, data in results.items():
        if 'alert_data' not in data or 'result' not in data:
            continue
        
        alert_data = data['alert_data']
        result = data['result']
        
        severity = alert_data.get('severity', 'Unknown')
        name = alert_data.get('name', 'Unknown Alert')
        action = result.get('action', 'Unknown')
        
        # Use the full test_name for matching
        normalized_test_name = test_name.lower()
        # Check if alert was processed correctly
        if action == 'processed':
            status = 'PASS'
        elif action == 'suppressed' and 'suppression' in normalized_test_name:
            status = 'PASS'  # Suppression was expected
        elif action == 'auto_recovered' and ('recovery' in normalized_test_name or 'auto_recovery' in normalized_test_name):
            status = 'PASS'  # Auto-recovery was expected
        else:
            status = 'FAIL'
        
        processing_results.append([
            test_name,
            name,
            severity,
            action,
            status
        ])
    
    return processing_results

def analyze_escalations(results):
    """Analyze the escalation results."""
    escalation_results = []
    
    for test_name, data in results.items():
        if 'escalation' not in test_name or 'result' not in data:
            continue
        
        result = data['result']
        action = result.get('action', 'Unknown')
        level = result.get('level', 'N/A')
        
        # Extract alert details
        alert = result.get('alert', {})
        severity = alert.get('severity', 'Unknown')
        name = alert.get('name', 'Unknown Alert')
        
        # Determine expected escalation based on test name
        expected_escalation = 'escalated' if 'no_escalation' not in test_name else 'skipped'
        
        # Check if escalation behavior was correct
        if action == expected_escalation:
            status = 'PASS'
        else:
            status = 'FAIL'
        
        escalation_results.append([
            test_name,
            name,
            severity,
            action,
            level,
            status
        ])
    
    return escalation_results

def analyze_notifications(results):
    """Analyze the notification results."""
    notification_results = []
    
    for test_name, data in results.items():
        if 'result' not in data:
            continue
        
        result = data['result']
        if 'notifications' not in result:
            continue
        
        notifications = result['notifications']
        
        # Extract alert details
        alert = result.get('alert', {})
        severity = alert.get('severity', 'Unknown')
        name = alert.get('name', 'Unknown Alert')
        
        # Count successful and failed notifications
        success_count = len(notifications.get('success', []))
        failure_count = len(notifications.get('failure', []))
        
        # List channels that were successfully notified
        channels = set()
        for notification in notifications.get('success', []):
            channel = notification.get('channel', 'unknown')
            channels.add(channel)
        
        # Determine if notifications were successful
        if success_count > 0 and failure_count == 0:
            status = 'PASS'
        elif success_count > 0 and failure_count > 0:
            status = 'PARTIAL'
        else:
            status = 'FAIL'
        
        notification_results.append([
            test_name,
            name,
            severity,
            ', '.join(channels),
            f"{success_count} success, {failure_count} failure",
            status
        ])
    
    return notification_results

def generate_report(results, output_file):
    """Generate a human-readable report based on the analysis."""
    processing_results = analyze_alert_processing(results)
    escalation_results = analyze_escalations(results)
    notification_results = analyze_notifications(results)
    
    # Calculate summary statistics
    total_tests = len(processing_results)
    passed_tests = sum(1 for r in processing_results if r[4] == 'PASS')
    failed_tests = total_tests - passed_tests
    
    total_escalations = len(escalation_results)
    passed_escalations = sum(1 for r in escalation_results if r[5] == 'PASS')
    failed_escalations = total_escalations - passed_escalations
    
    total_notifications = len(notification_results)
    passed_notifications = sum(1 for r in notification_results if r[5] == 'PASS')
    partial_notifications = sum(1 for r in notification_results if r[5] == 'PARTIAL')
    failed_notifications = total_notifications - passed_notifications - partial_notifications
    
    # Create the report
    report = []
    report.append("# Alert Escalation System Test Results\n")
    report.append(f"Report generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Summary section
    report.append("## Summary\n")
    report.append(f"- Total Tests: {total_tests}")
    report.append(f"- Passed: {passed_tests} ({passed_tests/total_tests*100 if total_tests else 0:.1f}%)")
    report.append(f"- Failed: {failed_tests} ({failed_tests/total_tests*100 if total_tests else 0:.1f}%)\n")
    
    report.append(f"- Total Escalation Tests: {total_escalations}")
    report.append(f"- Passed Escalations: {passed_escalations} ({passed_escalations/total_escalations*100 if total_escalations else 0:.1f}%)")
    report.append(f"- Failed Escalations: {failed_escalations} ({failed_escalations/total_escalations*100 if total_escalations else 0:.1f}%)\n")
    
    report.append(f"- Total Notification Tests: {total_notifications}")
    report.append(f"- Passed Notifications: {passed_notifications} ({passed_notifications/total_notifications*100 if total_notifications else 0:.1f}%)")
    report.append(f"- Partial Notifications: {partial_notifications} ({partial_notifications/total_notifications*100 if total_notifications else 0:.1f}%)")
    report.append(f"- Failed Notifications: {failed_notifications} ({failed_notifications/total_notifications*100 if total_notifications else 0:.1f}%)\n")
    
    # Alert Processing section
    report.append("## Alert Processing Results\n")
    headers = ["Test", "Alert Name", "Severity", "Action", "Status"]
    report.append(tabulate(processing_results, headers=headers, tablefmt="github"))
    report.append("\n")
    
    # Escalation section
    report.append("## Escalation Results\n")
    headers = ["Test", "Alert Name", "Severity", "Action", "Level", "Status"]
    report.append(tabulate(escalation_results, headers=headers, tablefmt="github"))
    report.append("\n")
    
    # Notification section
    report.append("## Notification Results\n")
    headers = ["Test", "Alert Name", "Severity", "Channels", "Results", "Status"]
    report.append(tabulate(notification_results, headers=headers, tablefmt="github"))
    report.append("\n")
    
    # Write report to file
    with open(output_file, 'w') as f:
        f.write("\n".join(report))
    
    logger.info(f"Test analysis report generated: {output_file}")
    
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'total_escalations': total_escalations,
        'passed_escalations': passed_escalations,
        'failed_escalations': failed_escalations,
        'total_notifications': total_notifications,
        'passed_notifications': passed_notifications,
        'partial_notifications': partial_notifications,
        'failed_notifications': failed_notifications
    }

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Analyze alert escalation system test results')
    parser.add_argument('--results-dir', default='test_results', help='Directory containing test results')
    parser.add_argument('--output', default='test_analysis_report.md', help='Output file for the analysis report')
    args = parser.parse_args()
    
    # Load test results
    results = load_test_results(args.results_dir)
    if not results:
        logger.error("No test results found to analyze")
        return 1
    
    logger.info(f"Loaded {len(results)} test results for analysis")
    
    # Generate report
    summary = generate_report(results, args.output)
    
    # Print summary to console
    print("\nTest Analysis Summary:")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']} ({summary['passed_tests']/summary['total_tests']*100 if summary['total_tests'] else 0:.1f}%)")
    print(f"Failed: {summary['failed_tests']} ({summary['failed_tests']/summary['total_tests']*100 if summary['total_tests'] else 0:.1f}%)")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 