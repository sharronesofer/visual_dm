"""
Core Monitoring Module

This module provides monitoring, alerting, and escalation functionality for the system.
"""

from .escalation_manager import EscalationManager
from .notification_dispatcher import NotificationDispatcher
from .alert_processor import AlertProcessor
from . import integrations

__all__ = ['EscalationManager', 'NotificationDispatcher', 'AlertProcessor', 'integrations'] 