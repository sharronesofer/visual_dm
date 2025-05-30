"""Base class for cloud cost collectors."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

class BaseCollector(ABC):
    """Base class for cloud cost collectors."""

    def __init__(self, credentials: Dict):
        """Initialize the collector.

        Args:
            credentials (Dict): Provider-specific credentials
        """
        self.credentials = credentials
        self.client = None

    @abstractmethod
    def initialize_client(self):
        """Initialize the cloud provider client."""
        pass

    @abstractmethod
    def get_cost_data(
        self,
        start_time: datetime,
        end_time: datetime,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Get cost data from the cloud provider.

        Args:
            start_time (datetime): Start of the period to get costs for
            end_time (datetime): End of the period to get costs for
            filters (Optional[Dict]): Optional filters to apply

        Returns:
            List[Dict]: List of cost entries with standardized fields:
                - service_name (str): Name of the service
                - resource_id (str): ID of the resource
                - cost_amount (float): Cost amount
                - currency (str): Currency code
                - start_time (datetime): Start of the cost period
                - end_time (datetime): End of the cost period
                - tags (Dict): Resource tags
        """
        pass

    @abstractmethod
    def get_resource_usage(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict:
        """Get usage metrics for a specific resource.

        Args:
            resource_id (str): ID of the resource
            start_time (datetime): Start of the period
            end_time (datetime): End of the period

        Returns:
            Dict: Resource usage metrics
        """
        pass

    @abstractmethod
    def get_resource_inventory(self, resource_type: Optional[str] = None) -> List[Dict]:
        """Get inventory of cloud resources.

        Args:
            resource_type (Optional[str]): Optional resource type filter

        Returns:
            List[Dict]: List of resources with standardized structure
        """
        pass

    @abstractmethod
    def get_resource_metrics(self, resource_id: str, metric_name: str,
                           start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get metrics for a specific resource.

        Args:
            resource_id (str): ID of the resource to get metrics for
            metric_name (str): Name of the metric to retrieve
            start_time (datetime): Start of the period to get metrics for
            end_time (datetime): End of the period to get metrics for

        Returns:
            List[Dict]: List of metric data points
        """
        pass

    @abstractmethod
    def get_resource_tags(self, resource_id: str) -> Dict:
        """Get tags for a specific resource.

        Args:
            resource_id (str): ID of the resource to get tags for

        Returns:
            Dict: Dictionary of tag key-value pairs
        """
        pass

    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate that the provided credentials are valid and have required permissions.

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        pass

    def standardize_cost_entry(self, raw_entry: Dict) -> Dict:
        """Convert provider-specific cost entry to standardized format.

        Args:
            raw_entry (Dict): Raw cost entry from provider API

        Returns:
            Dict: Standardized cost entry
        """
        return {
            'service_name': raw_entry.get('service'),
            'resource_id': raw_entry.get('resource_id'),
            'cost_amount': float(raw_entry.get('amount', 0.0)),
            'currency': raw_entry.get('currency', 'USD'),
            'start_time': raw_entry.get('start_time'),
            'end_time': raw_entry.get('end_time'),
            'tags': raw_entry.get('tags', {}),
        }

    def standardize_resource(self, raw_resource: Dict) -> Dict:
        """Convert provider-specific resource to standardized format.

        Args:
            raw_resource (Dict): Raw resource data from provider API

        Returns:
            Dict: Standardized resource data
        """
        return {
            'resource_id': raw_resource.get('id'),
            'resource_type': raw_resource.get('type'),
            'name': raw_resource.get('name'),
            'region': raw_resource.get('region'),
            'tags': raw_resource.get('tags', {}),
            'last_used': raw_resource.get('last_used'),
        } 