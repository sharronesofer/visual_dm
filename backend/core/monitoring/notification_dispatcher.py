"""
Notification Dispatcher

This module provides the functionality for sending alert notifications to various channels
based on escalation decisions.
"""

import os
import yaml
import json
import logging
import datetime
import smtplib
import requests
from typing import Dict, List, Any, Optional, Union
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

logger = logging.getLogger(__name__)

class NotificationDispatcher:
    """
    Handles sending alert notifications to various channels based on escalation decisions.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the notification dispatcher with configuration.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), 'config')
        self.escalation_config = self._load_config('escalation_config.yaml')
        self.notification_templates = self._load_config('notification_templates.yaml')
        
        self.default_channels = self.escalation_config.get('defaults', {}).get('notification_channels', [])
        self.global_variables = self.notification_templates.get('global_variables', {})
        
        # Initialize notification channel handlers
        self.channel_handlers = {
            'pagerduty': self._send_pagerduty,
            'slack': self._send_slack,
            'email': self._send_email,
            'sms': self._send_sms,
            'status_page': self._update_status_page
        }
        
        logger.info(f"Notification Dispatcher initialized with {len(self.channel_handlers)} channel handlers")
    
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
    
    def send_notifications(self, alert_data: Dict, targets: List[Dict], template_type: str = 'default') -> Dict:
        """
        Send notifications to all targets for an alert.
        
        Args:
            alert_data: Dictionary containing alert data
            targets: List of dictionaries containing target information
            template_type: Template type to use (e.g., 'default', 'escalation_first_level')
            
        Returns:
            Dictionary with notification results
        """
        results = {
            'success': [],
            'failure': []
        }
        
        severity = alert_data.get('severity')
        alert_type = alert_data.get('alert_type')
        
        # Determine which notification channels to use
        channels_to_use = set()
        for target in targets:
            for method in target.get('notification_methods', []):
                # Methods might be like "pagerduty_primary", so extract the base channel
                base_channel = method.split('_')[0]
                if base_channel in self.channel_handlers:
                    channels_to_use.add(base_channel)
        
        # Send notifications to each channel
        for channel in channels_to_use:
            try:
                # Get the template for this channel and severity
                template = self._get_template(channel, severity, template_type, alert_type)
                
                # Render the template with alert data
                rendered_content = self._render_template(template, alert_data)
                
                # Send the notification
                handler = self.channel_handlers.get(channel)
                if handler:
                    handler_result = handler(alert_data, targets, rendered_content)
                    if handler_result.get('success'):
                        results['success'].append({
                            'channel': channel,
                            'targets': handler_result.get('targets', []),
                            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                        })
                    else:
                        results['failure'].append({
                            'channel': channel,
                            'error': handler_result.get('error', 'Unknown error'),
                            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                        })
            except Exception as e:
                logger.error(f"Failed to send notification to channel {channel}: {str(e)}")
                results['failure'].append({
                    'channel': channel,
                    'error': str(e),
                    'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
                })
        
        return results
    
    def _get_template(self, channel: str, severity: str, template_type: str = 'default',
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
        
        # Check for template type in channel templates
        channel_templates = self.notification_templates.get('templates', {}).get(channel, {})
        
        # Check for severity-specific template with the template type
        if severity in channel_templates and template_type in channel_templates[severity]:
            return channel_templates[severity][template_type]
        
        # Check for severity-specific template
        if severity in channel_templates:
            return channel_templates[severity]
        
        # Check for template type in default templates
        if template_type in channel_templates.get('default', {}):
            return channel_templates['default'][template_type]
        
        # Fall back to default template
        return channel_templates.get('default', {})
    
    def _render_template(self, template: Dict, data: Dict) -> Dict:
        """
        Render a template with data.
        
        This is a simple placeholder for template rendering. In a real implementation,
        you would use a template engine like Jinja2.
        
        Args:
            template: Template dictionary
            data: Data to render the template with
            
        Returns:
            Dictionary with rendered content
        """
        # Combine global variables with alert data
        context = {**self.global_variables, **data}
        
        result = {}
        for key, value in template.items():
            if isinstance(value, str):
                # Simple string replacement for placeholders
                rendered = value
                for ctx_key, ctx_value in context.items():
                    placeholder = '{{' + ctx_key + '}}'
                    if placeholder in rendered:
                        rendered = rendered.replace(placeholder, str(ctx_value))
                result[key] = rendered
            else:
                result[key] = value
        
        return result
    
    def _send_pagerduty(self, alert_data: Dict, targets: List[Dict], content: Dict) -> Dict:
        """
        Send a notification to PagerDuty.
        
        Args:
            alert_data: Dictionary containing alert data
            targets: List of dictionaries containing target information
            content: Rendered template content
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Sending PagerDuty notification for alert {alert_data.get('id')}")
        
        # In a real implementation, you would use the PagerDuty API
        # This is a placeholder for demonstration purposes
        
        # Determine which PagerDuty services to notify based on target roles
        pd_services = []
        for target in targets:
            for method in target.get('notification_methods', []):
                if method.startswith('pagerduty_'):
                    pd_services.append(method)
        
        # Log the notification that would be sent
        logger.info(f"Would send PagerDuty notification with title: {content.get('title')}")
        logger.info(f"Would send PagerDuty notification to services: {pd_services}")
        
        # In a real implementation, you would make API calls to PagerDuty here
        
        return {
            'success': True,
            'targets': pd_services
        }
    
    def _send_slack(self, alert_data: Dict, targets: List[Dict], content: Dict) -> Dict:
        """
        Send a notification to Slack.
        
        Args:
            alert_data: Dictionary containing alert data
            targets: List of dictionaries containing target information
            content: Rendered template content
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Sending Slack notification for alert {alert_data.get('id')}")
        
        # In a real implementation, you would use the Slack API
        # This is a placeholder for demonstration purposes
        
        # Determine which Slack channels and users to notify
        slack_targets = set()
        for target in targets:
            for method in target.get('notification_methods', []):
                if method == 'slack_dm':
                    slack_targets.add(f"@{target.get('role')}")
        
        # Add the default Slack channel from configuration
        for channel in self.default_channels:
            if channel.get('type') == 'slack':
                slack_targets.add(channel.get('channel', '#incidents'))
        
        # Log the notification that would be sent
        if 'blocks' in content:
            logger.info(f"Would send Slack notification with blocks: {content.get('blocks')[:100]}...")
        else:
            logger.info("Would send Slack notification with default format")
        
        logger.info(f"Would send Slack notification to: {slack_targets}")
        
        # In a real implementation, you would make API calls to Slack here
        
        return {
            'success': True,
            'targets': list(slack_targets)
        }
    
    def _send_email(self, alert_data: Dict, targets: List[Dict], content: Dict) -> Dict:
        """
        Send a notification via email.
        
        Args:
            alert_data: Dictionary containing alert data
            targets: List of dictionaries containing target information
            content: Rendered template content
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Sending email notification for alert {alert_data.get('id')}")
        
        # In a real implementation, you would use an email library or service
        # This is a placeholder for demonstration purposes
        
        # Determine email recipients
        recipients = set()
        for target in targets:
            for method in target.get('notification_methods', []):
                if method == 'email':
                    recipients.add(f"{target.get('role')}@example.com")
        
        # Add the default email recipients from configuration
        for channel in self.default_channels:
            if channel.get('type') == 'email':
                for recipient in channel.get('recipients', []):
                    recipients.add(recipient)
        
        # Log the notification that would be sent
        logger.info(f"Would send email with subject: {content.get('subject')}")
        logger.info(f"Would send email to: {recipients}")
        
        # In a real implementation, you would send emails here
        
        return {
            'success': True,
            'targets': list(recipients)
        }
    
    def _send_sms(self, alert_data: Dict, targets: List[Dict], content: Dict) -> Dict:
        """
        Send a notification via SMS.
        
        Args:
            alert_data: Dictionary containing alert data
            targets: List of dictionaries containing target information
            content: Rendered template content
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Sending SMS notification for alert {alert_data.get('id')}")
        
        # In a real implementation, you would use an SMS service
        # This is a placeholder for demonstration purposes
        
        # Check if SMS is enabled for this severity
        severity = alert_data.get('severity')
        sms_enabled = False
        for channel in self.default_channels:
            if channel.get('type') == 'sms':
                if channel.get('enabled', False):
                    # Check if this severity meets the threshold
                    threshold = channel.get('priority_threshold')
                    if threshold:
                        # Simple severity comparison (assumes P1 > P2 > P3 > P4)
                        severity_level = int(severity[1])
                        threshold_level = int(threshold[1])
                        sms_enabled = severity_level <= threshold_level
                    else:
                        sms_enabled = True
        
        if not sms_enabled:
            logger.info(f"SMS notifications not enabled for severity {severity}")
            return {
                'success': True,
                'targets': []
            }
        
        # Determine SMS recipients
        recipients = set()
        for target in targets:
            for method in target.get('notification_methods', []):
                if method == 'sms':
                    recipients.add(f"{target.get('role')}")
        
        # Log the notification that would be sent
        logger.info(f"Would send SMS with body: {content.get('body')}")
        logger.info(f"Would send SMS to: {recipients}")
        
        # In a real implementation, you would send SMS messages here
        
        return {
            'success': True,
            'targets': list(recipients)
        }
    
    def _update_status_page(self, alert_data: Dict, targets: List[Dict], content: Dict) -> Dict:
        """
        Update the status page.
        
        Args:
            alert_data: Dictionary containing alert data
            targets: List of dictionaries containing target information
            content: Rendered template content
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Updating status page for alert {alert_data.get('id')}")
        
        # In a real implementation, you would use the status page API
        # This is a placeholder for demonstration purposes
        
        # Determine the status page template to use
        status_template = 'default'
        if alert_data.get('status') == 'identified':
            status_template = 'identified'
        elif alert_data.get('status') == 'resolved':
            status_template = 'resolved'
        
        # Get the status page update content
        status_update = {
            'title': content.get('title', f"Issue with {alert_data.get('system')}"),
            'body': content.get('body', f"We're investigating an issue with {alert_data.get('system')}")
        }
        
        # Log the status page update that would be sent
        logger.info(f"Would update status page with title: {status_update.get('title')}")
        logger.info(f"Would update status page with template: {status_template}")
        
        # In a real implementation, you would make API calls to the status page here
        
        return {
            'success': True,
            'targets': ['status_page']
        }
    
    def send_escalation_notification(self, alert_data: Dict, escalation_level: str) -> Dict:
        """
        Send a notification for an escalated alert.
        
        Args:
            alert_data: Dictionary containing alert data
            escalation_level: Escalation level (e.g., "first_level")
            
        Returns:
            Dictionary with notification results
        """
        logger.info(f"Sending escalation notification for alert {alert_data.get('id')} at level {escalation_level}")
        
        # Get the targets for this escalation level
        targets = alert_data.get('escalation_targets', [])
        
        # Add escalation-specific data
        alert_data_with_escalation = alert_data.copy()
        alert_data_with_escalation['escalation_timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        alert_data_with_escalation['escalation_level'] = escalation_level
        alert_data_with_escalation['escalated_to'] = ", ".join([target.get('role', '') for target in targets])
        
        # Determine the reason for escalation
        escalation_reason = "Alert requires attention"
        if 'history' in alert_data and alert_data['history']:
            last_event = alert_data['history'][-1]
            if 'event' in last_event and last_event['event'].startswith('escalated_to_'):
                if 'no_acknowledgment_within' in last_event.get('reason', {}):
                    minutes = last_event['reason']['no_acknowledgment_within']
                    escalation_reason = f"Alert not acknowledged within {minutes} minutes"
                elif 'no_update_within' in last_event.get('reason', {}):
                    minutes = last_event['reason']['no_update_within']
                    escalation_reason = f"Alert not updated within {minutes} minutes"
                elif 'no_resolution_within' in last_event.get('reason', {}):
                    minutes = last_event['reason']['no_resolution_within']
                    escalation_reason = f"Alert not resolved within {minutes} minutes"
        
        alert_data_with_escalation['escalation_reason'] = escalation_reason
        
        # Send the notifications
        template_type = f"escalation_{escalation_level}"
        return self.send_notifications(alert_data_with_escalation, targets, template_type) 