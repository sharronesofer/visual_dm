"""
Alert Escalation Manager

This module provides the core functionality for managing alert escalations based on
configured policies and timeframes.
"""

import os
import yaml
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class EscalationManager:
    """
    Manages alert escalations based on configured policies and timeframes.
    Responsible for determining when and how to escalate alerts, and to whom.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the escalation manager with configuration.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), 'config')
        self.escalation_config = self._load_config('escalation_config.yaml')
        self.notification_templates = self._load_config('notification_templates.yaml')
        
        self.default_timeframes = self.escalation_config.get('defaults', {}).get('escalation_timeframes', {})
        self.roles = self.escalation_config.get('roles', {})
        self.escalation_paths = self.escalation_config.get('escalation_paths', {})
        self.system_overrides = self.escalation_config.get('system_overrides', {})
        
        logger.info(f"Escalation Manager initialized with {len(self.escalation_paths)} escalation paths")
    
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
    
    def get_escalation_path(self, severity: str, system: Optional[str] = None) -> Dict:
        """
        Get the escalation path for a specific alert severity and system.
        
        Args:
            severity: Alert severity (e.g., "P1", "P2")
            system: Optional system name for system-specific overrides
            
        Returns:
            Dictionary containing the escalation path configuration
        """
        # Get the base escalation path for the severity
        base_path = self.escalation_paths.get(severity, {})
        
        # If no system-specific override, return the base path
        if not system or system not in self.system_overrides:
            return base_path
        
        # Apply system-specific overrides if they exist
        system_override = self.system_overrides.get(system, {})
        system_path_override = system_override.get('escalation_paths', {}).get(severity, {})
        
        # Merge the base path with the system-specific override
        result = self._deep_merge(base_path, system_path_override)
        
        return result
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries, with override values taking precedence.
        
        Args:
            base: Base dictionary
            override: Override dictionary with values to merge
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def get_escalation_timeframe(self, severity: str, level: str, system: Optional[str] = None) -> Optional[int]:
        """
        Get the escalation timeframe for a specific severity and level.
        
        Args:
            severity: Alert severity (e.g., "P1", "P2")
            level: Escalation level (e.g., "acknowledgment", "first_level")
            system: Optional system name for system-specific overrides
            
        Returns:
            Timeframe in minutes, or None if not configured
        """
        # Get default timeframe for the severity and level
        timeframe = self.default_timeframes.get(level, {}).get(severity)
        
        # If no system-specific override, return the default timeframe
        if not system or system not in self.system_overrides:
            return timeframe
        
        # Apply system-specific override if it exists
        system_override = self.system_overrides.get(system, {})
        system_timeframe_override = system_override.get('escalation_timeframes', {}).get(level, {}).get(severity)
        
        # Return the system-specific override if it exists, otherwise the default
        return system_timeframe_override if system_timeframe_override is not None else timeframe
    
    def should_escalate(self, alert_data: Dict) -> bool:
        """
        Determine if an alert should be escalated based on its data and configuration.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            True if the alert should be escalated, False otherwise
        """
        severity = alert_data.get('severity')
        level = alert_data.get('current_escalation_level', 'initial_response')
        system = alert_data.get('system')
        
        # Determine the next level
        next_level = self._get_next_level(level)
        if not next_level:
            logger.info(f"No next escalation level after {level} for {severity} alert")
            return False
        
        # Get the escalation path for the severity and level
        escalation_path = self.get_escalation_path(severity, system)
        if not escalation_path or next_level not in escalation_path:
            logger.info(f"No escalation path defined for {severity} alert, level {next_level}")
            return False
        
        # Check escalation conditions
        conditions = escalation_path.get(next_level, {}).get('conditions', [])
        return self._check_conditions(conditions, alert_data)
    
    def _get_next_level(self, current_level: str) -> Optional[str]:
        """
        Get the next escalation level after the current one.
        
        Args:
            current_level: Current escalation level
            
        Returns:
            Next escalation level, or None if there is no next level
        """
        level_order = ['initial_response', 'first_level', 'second_level', 'management_level']
        try:
            current_index = level_order.index(current_level)
            if current_index < len(level_order) - 1:
                return level_order[current_index + 1]
        except ValueError:
            logger.error(f"Unknown escalation level: {current_level}")
        
        return None
    
    def _check_conditions(self, conditions: List[Dict], alert_data: Dict) -> bool:
        """
        Check if escalation conditions are met.
        
        Args:
            conditions: List of condition dictionaries
            alert_data: Dictionary containing alert data
            
        Returns:
            True if conditions are met, False otherwise
        """
        if not conditions:
            return False
        
        for condition in conditions:
            if 'no_acknowledgment_within' in condition:
                minutes = condition['no_acknowledgment_within']
                if not self._check_time_condition(alert_data, 'created_at', minutes, 'acknowledged_at'):
                    return True
            
            elif 'no_update_within' in condition:
                minutes = condition['no_update_within']
                if not self._check_time_condition(alert_data, 'created_at', minutes, 'last_updated_at'):
                    return True
            
            elif 'no_resolution_within' in condition:
                minutes = condition['no_resolution_within']
                escalation_time_key = f"{alert_data.get('current_escalation_level')}_at"
                if escalation_time_key in alert_data and not self._check_time_condition(alert_data, escalation_time_key, minutes, 'resolved_at'):
                    return True
        
        return False
    
    def _check_time_condition(self, alert_data: Dict, start_key: str, minutes: int, end_key: str) -> bool:
        """
        Check if a time-based condition is met.
        
        Args:
            alert_data: Dictionary containing alert data
            start_key: Key for the start time
            minutes: Number of minutes
            end_key: Key for the end time
            
        Returns:
            True if the condition is met (end time exists and is within the timeframe), False otherwise
        """
        if start_key not in alert_data:
            return False
        
        start_time = self._parse_time(alert_data[start_key])
        if not start_time:
            return False
        
        # If the end time exists, check if it's within the timeframe
        if end_key in alert_data and alert_data[end_key]:
            end_time = self._parse_time(alert_data[end_key])
            if end_time:
                return (end_time - start_time).total_seconds() <= minutes * 60
            
        # If the end time doesn't exist, check if we're past the timeframe
        current_time = datetime.datetime.now(datetime.timezone.utc)
        return (current_time - start_time).total_seconds() <= minutes * 60
    
    def _parse_time(self, time_str: str) -> Optional[datetime.datetime]:
        """
        Parse a time string into a datetime object.
        
        Args:
            time_str: Time string
            
        Returns:
            Datetime object, or None if parsing fails
        """
        try:
            return datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.error(f"Failed to parse time string: {time_str}")
            return None
    
    def get_escalation_targets(self, alert_data: Dict) -> List[Dict]:
        """
        Get the targets for escalation based on alert data.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            List of dictionaries containing target information
        """
        severity = alert_data.get('severity')
        level = alert_data.get('current_escalation_level', 'initial_response')
        system = alert_data.get('system')
        
        # Determine the next level
        next_level = self._get_next_level(level)
        if not next_level:
            return []
        
        # Get the escalation path for the severity and level
        escalation_path = self.get_escalation_path(severity, system)
        if not escalation_path or next_level not in escalation_path:
            return []
        
        # Get the roles for the next level
        roles = escalation_path.get(next_level, {}).get('roles', [])
        
        # Build the target list
        targets = []
        for role_name in roles:
            role_info = self.roles.get(role_name, {})
            if role_info:
                notification_methods = role_info.get('notification_methods', [])
                targets.append({
                    'role': role_name,
                    'description': role_info.get('description', ''),
                    'notification_methods': notification_methods
                })
        
        # Check for system-specific additional notifications
        if system and system in self.system_overrides:
            system_override = self.system_overrides.get(system, {})
            additional_roles = system_override.get('notify_additional', {}).get('roles', [])
            
            for role_name in additional_roles:
                role_info = self.roles.get(role_name, {})
                if role_info:
                    notification_methods = role_info.get('notification_methods', [])
                    targets.append({
                        'role': role_name,
                        'description': role_info.get('description', ''),
                        'notification_methods': notification_methods
                    })
        
        return targets
    
    def get_escalation_actions(self, alert_data: Dict) -> List[str]:
        """
        Get the actions to take for escalation based on alert data.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            List of action strings
        """
        severity = alert_data.get('severity')
        level = alert_data.get('current_escalation_level', 'initial_response')
        system = alert_data.get('system')
        
        # Determine the next level
        next_level = self._get_next_level(level)
        if not next_level:
            return []
        
        # Get the escalation path for the severity and level
        escalation_path = self.get_escalation_path(severity, system)
        if not escalation_path or next_level not in escalation_path:
            return []
        
        # Get the actions for the next level
        return escalation_path.get(next_level, {}).get('actions', [])
    
    def get_notification_template(self, channel: str, severity: str, template_type: str = 'default',
                                 alert_type: Optional[str] = None) -> Dict:
        """
        Get the notification template for a specific channel and severity.
        
        Args:
            channel: Notification channel (e.g., "slack", "email")
            severity: Alert severity (e.g., "P1", "P2")
            template_type: Template type (e.g., "default", "escalation_first_level")
            alert_type: Optional alert type for alert-specific templates
            
        Returns:
            Dictionary containing the template configuration
        """
        # Check for alert-specific template
        if alert_type and alert_type in self.notification_templates.get('alert_specific_templates', {}):
            alert_templates = self.notification_templates['alert_specific_templates'][alert_type]
            if channel in alert_templates:
                return alert_templates[channel]
        
        # Check for severity-specific template
        channel_templates = self.notification_templates.get('templates', {}).get(channel, {})
        if severity in channel_templates:
            severity_template = channel_templates[severity]
            if template_type in severity_template:
                return severity_template[template_type]
            return severity_template
        
        # Fall back to default template
        if template_type in channel_templates.get('default', {}):
            return channel_templates['default'][template_type]
        
        return channel_templates.get('default', {})
    
    def escalate_alert(self, alert_data: Dict) -> Dict:
        """
        Process an alert for escalation.
        
        Args:
            alert_data: Dictionary containing alert data
            
        Returns:
            Updated alert data with escalation information
        """
        if not self.should_escalate(alert_data):
            return alert_data
        
        # Determine the next level
        current_level = alert_data.get('current_escalation_level', 'initial_response')
        next_level = self._get_next_level(current_level)
        
        # Update the alert data
        updated_data = alert_data.copy()
        updated_data['current_escalation_level'] = next_level
        updated_data[f'{next_level}_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # Get the escalation targets and actions
        escalation_targets = self.get_escalation_targets(updated_data)
        escalation_actions = self.get_escalation_actions(updated_data)
        
        updated_data['escalation_targets'] = escalation_targets
        updated_data['escalation_actions'] = escalation_actions
        
        # Record the escalation in the alert history
        if 'history' not in updated_data:
            updated_data['history'] = []
        
        updated_data['history'].append({
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'event': f'escalated_to_{next_level}',
            'targets': [target['role'] for target in escalation_targets],
            'actions': escalation_actions
        })
        
        logger.info(f"Escalated alert {updated_data.get('id')} from {current_level} to {next_level}")
        return updated_data 