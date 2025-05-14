"""Service for identifying and cleaning up unused cloud resources."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import CloudProvider, CloudResource, CleanupEntry, CostEntry
from ..collectors import AWSCollector, GCPCollector, AzureCollector

class ResourceCleanupService:
    """Service for managing cloud resource cleanup."""

    def __init__(self, db: Session):
        """Initialize the resource cleanup service.

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

    def sync_resources(self, provider_id: Optional[int] = None):
        """Sync cloud resources inventory with database.

        Args:
            provider_id (Optional[int]): Specific provider to sync
        """
        # Get providers to sync
        if provider_id:
            providers = [self.db.query(CloudProvider).get(provider_id)]
        else:
            providers = self.db.query(CloudProvider).all()
        
        # Sync each provider's resources
        for provider in providers:
            if provider.id in self._collectors:
                collector = self._collectors[provider.id]
                
                try:
                    # Get current resources from provider
                    resources = collector.get_resource_inventory()
                    
                    # Update or create resources in database
                    for resource_data in resources:
                        existing = self.db.query(CloudResource).filter(
                            CloudResource.provider_id == provider.id,
                            CloudResource.resource_id == resource_data['resource_id']
                        ).first()
                        
                        if existing:
                            # Update existing resource
                            for key, value in resource_data.items():
                                setattr(existing, key, value)
                        else:
                            # Create new resource
                            resource = CloudResource(
                                provider_id=provider.id,
                                resource_id=resource_data['resource_id'],
                                resource_type=resource_data['resource_type'],
                                name=resource_data['name'],
                                region=resource_data['region'],
                                tags=resource_data['tags'],
                                last_used=resource_data['last_used']
                            )
                            self.db.add(resource)
                    
                    self.db.commit()
                
                except Exception as e:
                    print(f"Error syncing resources from {provider.name}: {str(e)}")
                    self.db.rollback()

    def identify_unused_resources(self, age_threshold: int = 30,
                                cost_threshold: float = 100.0) -> List[CloudResource]:
        """Identify resources that are candidates for cleanup.

        Args:
            age_threshold (int): Days of inactivity to consider resource unused
            cost_threshold (float): Monthly cost threshold to flag expensive unused resources

        Returns:
            List[CloudResource]: List of resources identified for cleanup
        """
        cutoff_date = datetime.utcnow() - timedelta(days=age_threshold)
        
        # Get resources that haven't been used recently
        unused_resources = self.db.query(CloudResource).filter(
            CloudResource.last_used <= cutoff_date
        ).all()
        
        cleanup_candidates = []
        
        for resource in unused_resources:
            # Calculate monthly cost for resource
            monthly_cost = self._calculate_resource_cost(resource)
            
            if monthly_cost >= cost_threshold:
                # Check if resource already has an active cleanup entry
                existing_cleanup = self.db.query(CleanupEntry).filter(
                    CleanupEntry.resource_id == resource.id,
                    CleanupEntry.status.in_(['identified', 'notified', 'approved'])
                ).first()
                
                if not existing_cleanup:
                    # Create cleanup entry
                    cleanup_entry = CleanupEntry(
                        resource_id=resource.id,
                        reason=f"Resource unused for {age_threshold} days with monthly cost of ${monthly_cost:.2f}",
                        status='identified',
                        estimated_savings=monthly_cost
                    )
                    self.db.add(cleanup_entry)
                    cleanup_candidates.append(resource)
        
        self.db.commit()
        return cleanup_candidates

    def get_cleanup_recommendations(self, status: Optional[str] = None) -> List[Dict]:
        """Get list of cleanup recommendations with details.

        Args:
            status (Optional[str]): Filter by cleanup status

        Returns:
            List[Dict]: List of cleanup recommendations
        """
        query = self.db.query(CleanupEntry, CloudResource, CloudProvider).join(
            CloudResource
        ).join(
            CloudProvider
        )
        
        if status:
            query = query.filter(CleanupEntry.status == status)
        
        results = query.all()
        recommendations = []
        
        for cleanup, resource, provider in results:
            recommendations.append({
                'cleanup_id': cleanup.id,
                'resource_id': resource.resource_id,
                'resource_name': resource.name,
                'resource_type': resource.resource_type,
                'provider': provider.name,
                'region': resource.region,
                'reason': cleanup.reason,
                'status': cleanup.status,
                'identified_at': cleanup.identified_at,
                'estimated_savings': cleanup.estimated_savings,
                'tags': resource.tags
            })
        
        return recommendations

    def approve_cleanup(self, cleanup_id: int, approved_by: str) -> bool:
        """Approve a cleanup recommendation.

        Args:
            cleanup_id (int): ID of the cleanup entry to approve
            approved_by (str): Name/ID of person approving the cleanup

        Returns:
            bool: True if approval was successful
        """
        cleanup = self.db.query(CleanupEntry).get(cleanup_id)
        if not cleanup:
            return False
        
        cleanup.status = 'approved'
        cleanup.approved_at = datetime.utcnow()
        cleanup.approved_by = approved_by
        
        self.db.commit()
        return True

    def execute_cleanup(self, cleanup_id: int) -> bool:
        """Execute approved cleanup operation.

        Args:
            cleanup_id (int): ID of the cleanup entry to execute

        Returns:
            bool: True if cleanup was successful
        """
        cleanup = self.db.query(CleanupEntry).get(cleanup_id)
        if not cleanup or cleanup.status != 'approved':
            return False
        
        resource = cleanup.resource
        provider = resource.provider
        
        if provider.id in self._collectors:
            collector = self._collectors[provider.id]
            
            try:
                # Implement actual resource deletion here
                # This is a placeholder - actual implementation would use
                # provider-specific APIs to delete the resource
                
                cleanup.status = 'cleaned'
                cleanup.cleaned_at = datetime.utcnow()
                self.db.commit()
                return True
                
            except Exception as e:
                print(f"Error cleaning up resource: {str(e)}")
                return False
        
        return False

    def exempt_from_cleanup(self, cleanup_id: int, reason: str) -> bool:
        """Exempt a resource from cleanup.

        Args:
            cleanup_id (int): ID of the cleanup entry to exempt
            reason (str): Reason for exemption

        Returns:
            bool: True if exemption was successful
        """
        cleanup = self.db.query(CleanupEntry).get(cleanup_id)
        if not cleanup:
            return False
        
        cleanup.status = 'exempted'
        cleanup.exemption_reason = reason
        
        self.db.commit()
        return True

    def _calculate_resource_cost(self, resource: CloudResource) -> float:
        """Calculate monthly cost for a resource.

        Args:
            resource (CloudResource): Resource to calculate cost for

        Returns:
            float: Monthly cost of the resource
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)
        
        total_cost = self.db.query(
            func.sum(CostEntry.cost_amount)
        ).filter(
            CostEntry.resource_id == resource.resource_id,
            CostEntry.start_time >= start_time,
            CostEntry.end_time <= end_time
        ).scalar()
        
        return float(total_cost) if total_cost else 0.0 