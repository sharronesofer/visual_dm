"""Service for monitoring and managing cloud resource cleanup."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.cleanup import CleanupRule, CleanupEntry
from ..models import CloudProvider
from ..collectors import AWSCollector, GCPCollector, AzureCollector

class CleanupMonitorService:
    """Service for monitoring and managing cloud resource cleanup."""

    def __init__(self, db: Session):
        """Initialize the cleanup monitor service.

        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
        self._collectors = {}

    def initialize_collectors(self):
        """Initialize collectors for all configured cloud providers."""
        providers = self.db.query(CloudProvider).all()
        
        collector_map = {
            'aws': AWSCollector,
            'gcp': GCPCollector,
            'azure': AzureCollector
        }
        
        for provider in providers:
            if provider.name.lower() in collector_map:
                collector = collector_map[provider.name.lower()](provider.api_credentials)
                collector.initialize_client()
                self._collectors[provider.id] = collector

    def create_cleanup_rule(self, name: str, provider_id: int, resource_type: str,
                          conditions: Dict, action: str) -> CleanupRule:
        """Create a new cleanup rule.

        Args:
            name (str): Name of the rule
            provider_id (int): ID of the cloud provider
            resource_type (str): Type of resource to monitor
            conditions (Dict): Conditions that trigger cleanup
            action (str): Action to take ('notify', 'stop', 'terminate')

        Returns:
            CleanupRule: Created rule object
        """
        rule = CleanupRule(
            name=name,
            provider_id=provider_id,
            resource_type=resource_type,
            conditions=conditions,
            action=action
        )
        
        self.db.add(rule)
        self.db.commit()
        
        return rule

    def check_resources(self, provider_id: Optional[int] = None) -> List[CleanupEntry]:
        """Check resources against cleanup rules.

        Args:
            provider_id (Optional[int]): Specific provider to check

        Returns:
            List[CleanupEntry]: List of resources that match cleanup rules
        """
        # Get providers to check
        if provider_id:
            providers = [self.db.query(CloudProvider).get(provider_id)]
        else:
            providers = self.db.query(CloudProvider).filter_by(is_active=True).all()
        
        cleanup_entries = []
        
        for provider in providers:
            if provider.id not in self._collectors:
                continue
                
            # Get rules for this provider
            rules = self.db.query(CleanupRule).filter_by(
                provider_id=provider.id,
                is_active=True
            ).all()
            
            for rule in rules:
                try:
                    # Get resources that match the rule conditions
                    matching_resources = self._check_rule_conditions(
                        provider.id,
                        rule.resource_type,
                        rule.conditions
                    )
                    
                    # Create cleanup entries for matching resources
                    for resource in matching_resources:
                        entry = CleanupEntry(
                            rule_id=rule.id,
                            provider_id=provider.id,
                            resource_id=resource['id'],
                            resource_type=rule.resource_type,
                            resource_name=resource.get('name', ''),
                            cleanup_action=rule.action,
                            scheduled_time=datetime.utcnow() + timedelta(days=1)  # Schedule for tomorrow
                        )
                        cleanup_entries.append(entry)
                        self.db.add(entry)
                
                except Exception as e:
                    # Log error but continue with other rules
                    print(f"Error checking rule {rule.name}: {str(e)}")
        
        self.db.commit()
        return cleanup_entries

    def _check_rule_conditions(self, provider_id: int, resource_type: str,
                             conditions: Dict) -> List[Dict]:
        """Check resources against rule conditions.

        Args:
            provider_id (int): Cloud provider ID
            resource_type (str): Type of resource to check
            conditions (Dict): Conditions to check against

        Returns:
            List[Dict]: Resources that match the conditions
        """
        collector = self._collectors.get(provider_id)
        if not collector:
            return []
            
        # This would call provider-specific methods to list resources
        # and check them against the conditions
        # For now, return empty list as actual implementation depends on provider APIs
        return []

    def execute_cleanup(self, entry_id: int) -> bool:
        """Execute a cleanup action.

        Args:
            entry_id (int): ID of the cleanup entry to execute

        Returns:
            bool: True if cleanup was successful
        """
        entry = self.db.query(CleanupEntry).get(entry_id)
        if not entry or entry.status != 'pending':
            return False
            
        collector = self._collectors.get(entry.provider_id)
        if not collector:
            return False
            
        try:
            # This would call provider-specific methods to execute the cleanup action
            # For now, just mark as completed as actual implementation depends on provider APIs
            entry.status = 'completed'
            entry.completed_time = datetime.utcnow()
            self.db.commit()
            return True
            
        except Exception as e:
            entry.status = 'failed'
            entry.error_message = str(e)
            self.db.commit()
            return False

    def get_pending_cleanups(self) -> List[CleanupEntry]:
        """Get list of pending cleanup entries.

        Returns:
            List[CleanupEntry]: List of pending cleanup entries
        """
        return self.db.query(CleanupEntry).filter_by(status='pending').all()

    def get_cleanup_history(self, days: int = 30) -> List[CleanupEntry]:
        """Get cleanup history.

        Args:
            days (int): Number of days of history to return

        Returns:
            List[CleanupEntry]: List of cleanup entries
        """
        start_time = datetime.utcnow() - timedelta(days=days)
        return self.db.query(CleanupEntry).filter(
            CleanupEntry.created_at >= start_time
        ).order_by(
            CleanupEntry.created_at.desc()
        ).all() 