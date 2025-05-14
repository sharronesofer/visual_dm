"""
Alert Processor

This module provides the main alert processing functionality, coordinating
between the escalation manager and notification dispatcher.
"""

import os
import uuid
import yaml
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .escalation_manager import EscalationManager
from .notification_dispatcher import NotificationDispatcher

logger = logging.getLogger(__name__)

class AlertProcessor:
    """
    Main alert processor that handles the entire alert lifecycle,
    including initial processing, escalation, and notification.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the alert processor with configuration.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), 'config')
        self.escalation_manager = EscalationManager(self.config_dir)
        self.notification_dispatcher = NotificationDispatcher(self.config_dir)
        
        # Load configuration
        self.config = self._load_config('escalation_config.yaml')
        self.auto_recovery_config = self.config.get('auto_recovery', {})
        self.suppression_rules = self.config.get('suppression_rules', {})
        
        logger.info("Alert Processor initialized")
    
    def _load_config(self, filename: str) -> Dict:
        """
        Load a YAML configuration file.
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Dictionary containing the configuration
        """
        config_path = os.path.join(self.config_dir, filename)
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.debug(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {str(e)}")
            return {}
    
    def process_alert(self, alert_data: Dict) -> Dict:
        """
        Process an incoming alert.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing alert: {alert_data.get('name', 'Unknown')}")
        
        # Ensure required fields
        processed_data = self._ensure_required_fields(alert_data)
        
        # Apply suppression rules
        if self._should_suppress(processed_data):
            logger.info(f"Alert {processed_data.get('id')} suppressed by suppression rules")
            return {
                'action': 'suppressed',
                'alert': processed_data
            }
        
        # Check for auto-recovery actions
        if self._should_attempt_recovery(processed_data):
            recovery_result = self._attempt_recovery(processed_data)
            if recovery_result.get('success'):
                logger.info(f"Auto-recovery successful for alert {processed_data.get('id')}")
                return {
                    'action': 'auto_recovered',
                    'alert': recovery_result.get('alert', processed_data),
                    'recovery': recovery_result
                }
        
        # Get initial escalation path
        severity = processed_data.get('severity')
        system = processed_data.get('system')
        escalation_path = self.escalation_manager.get_escalation_path(severity, system)
        
        # Set initial escalation level
        processed_data['current_escalation_level'] = 'initial_response'
        processed_data['initial_response_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Get initial targets and actions
        initial_targets = []
        initial_roles = escalation_path.get('initial_response', {}).get('roles', [])
        for role_name in initial_roles:
            role_info = self.escalation_manager.roles.get(role_name, {})
            if role_info:
                notification_methods = role_info.get('notification_methods', [])
                initial_targets.append({
                    'role': role_name,
                    'description': role_info.get('description', ''),
                    'notification_methods': notification_methods
                })
        
        # System-specific additional notifications
        if system and system in self.escalation_manager.system_overrides:
            system_override = self.escalation_manager.system_overrides.get(system, {})
            additional_roles = system_override.get('notify_additional', {}).get('roles', [])
            
            for role_name in additional_roles:
                role_info = self.escalation_manager.roles.get(role_name, {})
                if role_info:
                    notification_methods = role_info.get('notification_methods', [])
                    initial_targets.append({
                        'role': role_name,
                        'description': role_info.get('description', ''),
                        'notification_methods': notification_methods
                    })
        
        initial_actions = escalation_path.get('initial_response', {}).get('actions', [])
        initial_automations = escalation_path.get('initial_response', {}).get('automation', [])
        
        processed_data['initial_targets'] = initial_targets
        processed_data['initial_actions'] = initial_actions
        processed_data['initial_automations'] = initial_automations
        
        # Record in alert history
        if 'history' not in processed_data:
            processed_data['history'] = []
        
        processed_data['history'].append({
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'event': 'alert_received',
            'targets': [target['role'] for target in initial_targets],
            'actions': initial_actions,
            'automations': initial_automations
        })
        
        # Send initial notifications
        notification_results = self.notification_dispatcher.send_notifications(
            processed_data, initial_targets, 'default'
        )
        
        # Execute initial automations
        automation_results = self._execute_automations(processed_data, initial_automations)
        
        # Return the processing results
        return {
            'action': 'processed',
            'alert': processed_data,
            'notifications': notification_results,
            'automations': automation_results
        }
    
    def _ensure_required_fields(self, alert_data: Dict) -> Dict:
        """
        Ensure that the alert data has all required fields.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            Alert data with required fields added if missing
        """
        result = alert_data.copy()
        
        # Generate ID if missing
        if 'id' not in result:
            result['id'] = str(uuid.uuid4())
        
        # Set created timestamp if missing
        if 'created_at' not in result:
            result['created_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Default severity to P3 if missing
        if 'severity' not in result:
            result['severity'] = 'P3'
        
        # Default status to 'new' if missing
        if 'status' not in result:
            result['status'] = 'new'
        
        # Ensure name field
        if 'name' not in result and 'alert_name' in result:
            result['name'] = result['alert_name']
        elif 'name' not in result:
            result['name'] = f"Alert {result['id']}"
        
        # Default system to 'unknown' if missing
        if 'system' not in result:
            result['system'] = 'unknown'
        
        return result
    
    def _should_suppress(self, alert_data: Dict) -> bool:
        """
        Determine if an alert should be suppressed based on suppression rules.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            True if the alert should be suppressed, False otherwise
        """
        # Check maintenance windows
        maintenance_windows = self.suppression_rules.get('maintenance_windows', [])
        for window in maintenance_windows:
            window_name = window.get('name', 'Unnamed')
            suppress_alerts = window.get('suppress_alerts', [])
            
            # Check if alert name matches any in the suppression list
            alert_name = alert_data.get('name', '')
            for suppress_pattern in suppress_alerts:
                if suppress_pattern in alert_name:
                    # In a real implementation, you would also check if the current time
                    # falls within the scheduled maintenance window
                    logger.info(f"Alert {alert_data.get('id')} matches maintenance window {window_name}")
                    return True
        
        # Check duplicate alert suppression
        duplicate_rules = self.suppression_rules.get('duplicate_alerts', [])
        for rule in duplicate_rules:
            # In a real implementation, you would check for duplicate alerts in the database
            # This is a placeholder for demonstration purposes
            
            # Don't suppress P1 alerts if they're configured as exceptions
            severity = alert_data.get('severity')
            exception_severities = rule.get('exception_severity', [])
            if severity in exception_severities:
                continue
        
        # Check group alert suppression
        group_rules = self.suppression_rules.get('group_alerts', [])
        for rule in group_rules:
            # In a real implementation, you would check for related alerts to group
            # This is a placeholder for demonstration purposes
            pass
        
        return False
    
    def _should_attempt_recovery(self, alert_data: Dict) -> bool:
        """
        Determine if auto-recovery should be attempted for an alert.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            True if auto-recovery should be attempted, False otherwise
        """
        # Check if auto-recovery is enabled
        if not self.auto_recovery_config.get('enabled', False):
            return False
        
        # Get the alert name and severity
        alert_name = alert_data.get('name', '')
        severity = alert_data.get('severity', '')
        
        # Check if there's a matching recovery action
        for action_name, action_config in self.auto_recovery_config.get('actions', {}).items():
            conditions = action_config.get('conditions', [])
            
            for condition in conditions:
                condition_alert = condition.get('alert', '')
                condition_severities = condition.get('severity', [])
                
                # Check if the alert name and severity match
                if condition_alert in alert_name and severity in condition_severities:
                    return True
        
        return False
    
    def _attempt_recovery(self, alert_data: Dict) -> Dict:
        """
        Attempt to automatically recover from an alert.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            Dictionary with recovery results
        """
        logger.info(f"Attempting auto-recovery for alert {alert_data.get('id')}")
        
        # Get the alert name and severity
        alert_name = alert_data.get('name', '')
        severity = alert_data.get('severity', '')
        
        # Find matching recovery actions
        for action_name, action_config in self.auto_recovery_config.get('actions', {}).items():
            conditions = action_config.get('conditions', [])
            
            for condition in conditions:
                condition_alert = condition.get('alert', '')
                condition_severities = condition.get('severity', [])
                
                # Check if the alert name and severity match
                if condition_alert in alert_name and severity in condition_severities:
                    # Check attempt count
                    attempt_count = alert_data.get('auto_recovery_attempts', {}).get(action_name, 0)
                    max_attempts = condition.get('attempt_count_max', 1)
                    
                    if attempt_count >= max_attempts:
                        logger.info(f"Max auto-recovery attempts ({max_attempts}) reached for action {action_name}")
                        continue
                    
                    # In a real implementation, you would execute the actual recovery action here
                    logger.info(f"Executing auto-recovery action: {action_name}")
                    
                    # Update the alert data with recovery information
                    updated_data = alert_data.copy()
                    
                    if 'auto_recovery_attempts' not in updated_data:
                        updated_data['auto_recovery_attempts'] = {}
                    
                    updated_data['auto_recovery_attempts'][action_name] = attempt_count + 1
                    
                    if 'history' not in updated_data:
                        updated_data['history'] = []
                    
                    updated_data['history'].append({
                        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        'event': 'auto_recovery_attempted',
                        'action': action_name,
                        'attempt': attempt_count + 1,
                        'max_attempts': max_attempts
                    })
                    
                    # Send notification about the auto-recovery action
                    self._send_auto_recovery_notification(updated_data, action_name)
                    
                    # In a real implementation, you would check if the recovery was successful
                    # This is a placeholder for demonstration purposes
                    recovery_success = True
                    
                    if recovery_success:
                        updated_data['status'] = 'auto_recovered'
                        updated_data['resolved_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                        
                        updated_data['history'].append({
                            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            'event': 'auto_recovery_succeeded',
                            'action': action_name
                        })
                        
                        return {
                            'success': True,
                            'action': action_name,
                            'alert': updated_data
                        }
                    else:
                        updated_data['history'].append({
                            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            'event': 'auto_recovery_failed',
                            'action': action_name
                        })
                        
                        return {
                            'success': False,
                            'action': action_name,
                            'alert': updated_data,
                            'error': 'Recovery action failed'
                        }
        
        return {
            'success': False,
            'alert': alert_data,
            'error': 'No matching recovery action found'
        }
    
    def _send_auto_recovery_notification(self, alert_data: Dict, action_name: str) -> Dict:
        """
        Send a notification about an auto-recovery action.
        
        Args:
            alert_data: Dictionary containing alert data
            action_name: Name of the recovery action
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Sending auto-recovery notification for alert {alert_data.get('id')}")
        
        # Prepare the notification data
        notification_data = alert_data.copy()
        notification_data['action_name'] = action_name
        notification_data['action_timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        notification_data['action_status'] = 'in_progress'
        notification_data['action_details'] = f"Executing auto-recovery action: {action_name}"
        
        # In a real implementation, you would get the exact action details
        
        # Send to Slack (or other channels as needed)
        # In a real implementation, you would determine the appropriate targets
        targets = [{
            'role': 'auto_recovery',
            'description': 'Auto Recovery Notification',
            'notification_methods': ['slack']
        }]
        
        # Use the auto-recovery template
        return self.notification_dispatcher.send_notifications(
            notification_data, targets, 'auto_recovery'
        )
    
    def _execute_automations(self, alert_data: Dict, automations: List[str]) -> Dict:
        """
        Execute initial automations for an alert.
        
        Args:
            alert_data: Dictionary containing alert data
            automations: List of automation actions to execute
            
        Returns:
            Dictionary with automation results
        """
        results = {
            'success': [],
            'failure': []
        }
        
        for automation in automations:
            try:
                if automation == 'start_incident_timer':
                    # In a real implementation, you would start an incident timer
                    logger.info(f"Started incident timer for alert {alert_data.get('id')}")
                    results['success'].append({
                        'automation': automation,
                        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                    })
                
                elif automation == 'create_zoom_bridge':
                    # In a real implementation, you would create a Zoom bridge
                    zoom_url = "https://zoom.us/j/123456789"  # Placeholder
                    logger.info(f"Created Zoom bridge for alert {alert_data.get('id')}: {zoom_url}")
                    results['success'].append({
                        'automation': automation,
                        'result': {'zoom_url': zoom_url},
                        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                    })
                
                elif automation == 'assign_incident_id':
                    # In a real implementation, you would assign an incident ID
                    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
                    logger.info(f"Assigned incident ID for alert {alert_data.get('id')}: {incident_id}")
                    results['success'].append({
                        'automation': automation,
                        'result': {'incident_id': incident_id},
                        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                    })
                
                elif automation == 'assign_ticket_id':
                    # In a real implementation, you would assign a ticket ID
                    ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
                    logger.info(f"Assigned ticket ID for alert {alert_data.get('id')}: {ticket_id}")
                    results['success'].append({
                        'automation': automation,
                        'result': {'ticket_id': ticket_id},
                        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                    })
                
                else:
                    logger.warning(f"Unknown automation action: {automation}")
                    results['failure'].append({
                        'automation': automation,
                        'error': 'Unknown automation action',
                        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                    })
            
            except Exception as e:
                logger.error(f"Failed to execute automation {automation}: {str(e)}")
                results['failure'].append({
                    'automation': automation,
                    'error': str(e),
                    'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
        
        return results
    
    def check_and_escalate(self, alert_data: Dict) -> Dict:
        """
        Check if an alert should be escalated and escalate if needed.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            Dictionary with escalation results
        """
        logger.info(f"Checking if alert {alert_data.get('id')} should be escalated")
        
        # Skip if the alert is already resolved
        if alert_data.get('status') in ['resolved', 'auto_recovered']:
            logger.info(f"Alert {alert_data.get('id')} is already resolved, skipping escalation check")
            return {
                'action': 'skipped',
                'reason': 'alert_resolved',
                'alert': alert_data
            }
        
        # Check if the alert should be escalated
        if not self.escalation_manager.should_escalate(alert_data):
            logger.info(f"Alert {alert_data.get('id')} does not need escalation at this time")
            return {
                'action': 'skipped',
                'reason': 'escalation_not_needed',
                'alert': alert_data
            }
        
        # Escalate the alert
        updated_data = self.escalation_manager.escalate_alert(alert_data)
        
        # Send escalation notifications
        escalation_level = updated_data.get('current_escalation_level')
        notification_results = self.notification_dispatcher.send_escalation_notification(
            updated_data, escalation_level
        )
        
        logger.info(f"Alert {updated_data.get('id')} escalated to {escalation_level}")
        
        return {
            'action': 'escalated',
            'level': escalation_level,
            'alert': updated_data,
            'notifications': notification_results
        }
    
    def update_alert(self, alert_id: str, update_data: Dict) -> Dict:
        """
        Update an existing alert with new data.
        
        Args:
            alert_id: ID of the alert to update
            update_data: Dictionary containing update data
            
        Returns:
            Dictionary with update results
        """
        logger.info(f"Updating alert {alert_id}")
        
        # In a real implementation, you would retrieve the alert from a database
        # This is a placeholder for demonstration purposes
        existing_alert = {
            'id': alert_id,
            'name': 'Example Alert',
            'severity': 'P2',
            'system': 'example_system',
            'created_at': (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=30)).isoformat(),
            'status': 'pending',
            'current_escalation_level': 'initial_response'
        }
        
        # Update the alert data
        updated_data = {**existing_alert, **update_data}
        
        # Record the update in the alert history
        if 'history' not in updated_data:
            updated_data['history'] = []
        
        updated_data['history'].append({
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'event': 'alert_updated',
            'updates': list(update_data.keys())
        })
        
        # Set last_updated_at timestamp
        updated_data['last_updated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Handle specific update types
        if 'status' in update_data:
            if update_data['status'] == 'acknowledged':
                updated_data['acknowledged_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            elif update_data['status'] == 'resolved':
                updated_data['resolved_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        logger.info(f"Alert {alert_id} updated successfully")
        
        return {
            'action': 'updated',
            'alert': updated_data
        } 