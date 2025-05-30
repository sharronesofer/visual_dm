"""Azure cost and resource data collector."""

from datetime import datetime
from typing import Dict, List, Optional
from azure.identity import ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.core.exceptions import AzureError
import json

from .base import BaseCollector

class AzureCollector(BaseCollector):
    """Collector for Azure cost and resource data."""

    def initialize_client(self) -> None:
        """Initialize Azure API clients."""
        # Get credentials from dict
        creds = self.credentials
        credential = ClientSecretCredential(
            tenant_id=creds['tenant_id'],
            client_id=creds['client_id'],
            client_secret=creds['client_secret']
        )
        
        subscription_id = creds['subscription_id']
        
        # Initialize clients
        self._cost_client = CostManagementClient(credential, subscription_id)
        self._resource_client = ResourceManagementClient(credential, subscription_id)
        self._monitor_client = MonitorManagementClient(credential, subscription_id)
        
        self.subscription_id = subscription_id
        self.scope = f"/subscriptions/{subscription_id}"

    def get_cost_data(self, start_time: datetime, end_time: datetime,
                     filters: Optional[Dict] = None) -> List[Dict]:
        """Get cost data from Azure Cost Management API.

        Args:
            start_time (datetime): Start of the period to collect costs for
            end_time (datetime): End of the period to collect costs for
            filters (Optional[Dict]): Optional filters to apply

        Returns:
            List[Dict]: List of standardized cost entries
        """
        try:
            # Build query parameters
            parameters = {
                "type": "ActualCost",
                "timeframe": "Custom",
                "timePeriod": {
                    "from": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "to": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                "dataset": {
                    "granularity": "Daily",
                    "aggregation": {
                        "totalCost": {
                            "name": "Cost",
                            "function": "Sum"
                        }
                    },
                    "grouping": [
                        {"type": "Dimension", "name": "ServiceName"},
                        {"type": "Tag", "name": "Environment"}
                    ]
                }
            }

            if filters:
                parameters["dataset"]["filter"] = self._build_cost_filter(filters)

            # Query costs
            cost_entries = []
            query_result = self._cost_client.query.usage(scope=self.scope, parameters=parameters)

            for row in query_result.rows:
                entry = {
                    'service': row[0],  # ServiceName
                    'amount': float(row[2]),  # Cost
                    'currency': query_result.properties.columns[2].unit,
                    'start_time': start_time,
                    'end_time': end_time,
                    'tags': {'Environment': row[1]} if len(row) > 1 else {}
                }
                cost_entries.append(self.standardize_cost_entry(entry))

            return cost_entries

        except AzureError as e:
            raise Exception(f"Failed to get Azure cost data: {str(e)}")

    def get_resource_inventory(self, resource_type: Optional[str] = None) -> List[Dict]:
        """Get inventory of Azure resources.

        Args:
            resource_type (Optional[str]): Optional resource type filter

        Returns:
            List[Dict]: List of standardized resource entries
        """
        try:
            resources = []
            
            # List resources
            resource_list = self._resource_client.resources.list()
            if resource_type:
                resource_list = [r for r in resource_list if r.type.lower() == resource_type.lower()]

            for resource in resource_list:
                # Get resource details
                details = self._get_resource_details(resource)
                
                resource_data = {
                    'id': resource.id,
                    'type': resource.type,
                    'name': resource.name,
                    'region': resource.location,
                    'tags': resource.tags or {},
                    'last_used': details.get('last_used')
                }
                resources.append(self.standardize_resource(resource_data))

            return resources

        except AzureError as e:
            raise Exception(f"Failed to get Azure resource inventory: {str(e)}")

    def get_resource_metrics(self, resource_id: str, metric_name: str,
                           start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get Azure Monitor metrics for a specific resource.

        Args:
            resource_id (str): ID of the resource to get metrics for
            metric_name (str): Name of the metric to retrieve
            start_time (datetime): Start of the period to get metrics for
            end_time (datetime): End of the period to get metrics for

        Returns:
            List[Dict]: List of metric data points
        """
        try:
            # Get metric data
            metrics = self._monitor_client.metrics.list(
                resource_id,
                timespan=f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}",
                interval='PT1H',  # 1 hour intervals
                metricnames=metric_name,
                aggregation='Average'
            )

            metric_data = []
            for metric in metrics.value:
                for timeseries in metric.timeseries:
                    for data in timeseries.data:
                        if data.average is not None:
                            metric_data.append({
                                'timestamp': data.time_stamp,
                                'value': data.average,
                                'unit': metric.unit
                            })

            return metric_data

        except AzureError as e:
            raise Exception(f"Failed to get Azure resource metrics: {str(e)}")

    def get_resource_tags(self, resource_id: str) -> Dict:
        """Get tags for a specific Azure resource.

        Args:
            resource_id (str): ID of the resource to get tags for

        Returns:
            Dict: Dictionary of tag key-value pairs
        """
        try:
            resource = self._resource_client.resources.get_by_id(resource_id, api_version="2021-04-01")
            return resource.tags or {}

        except AzureError as e:
            raise Exception(f"Failed to get Azure resource tags: {str(e)}")

    def validate_credentials(self) -> bool:
        """Validate Azure credentials.

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Try to list resource groups
            next(self._resource_client.resource_groups.list())
            return True
        except Exception:
            return False

    def _build_cost_filter(self, filters: Dict) -> Dict:
        """Build Azure Cost Management API filter.

        Args:
            filters (Dict): Filter parameters

        Returns:
            Dict: Azure Cost Management API filter
        """
        filter_parts = []

        if 'services' in filters:
            services = [f"ServiceName eq '{service}'" for service in filters['services']]
            filter_parts.append(f"({' or '.join(services)})")

        if 'tags' in filters:
            for key, value in filters['tags'].items():
                if isinstance(value, list):
                    values = [f"tags['{key}'] eq '{v}'" for v in value]
                    filter_parts.append(f"({' or '.join(values)})")
                else:
                    filter_parts.append(f"tags['{key}'] eq '{value}'")

        return {
            "and": [{"dimensions": {"name": "ServiceName", "operator": "In", "values": filters['services']}}]
        } if 'services' in filters else None

    def _get_resource_details(self, resource) -> Dict:
        """Get additional details for specific resource types.

        Args:
            resource: Azure resource object

        Returns:
            Dict: Additional resource details
        """
        details = {}
        
        try:
            # Get resource-specific details based on type
            if resource.type.lower() == 'microsoft.compute/virtualmachines':
                vm_client = self._resource_client.resources.get_by_id(
                    resource.id,
                    api_version="2021-07-01"
                )
                details['last_used'] = vm_client.properties.get('timeCreated')
                
            elif resource.type.lower() == 'microsoft.sql/servers/databases':
                sql_client = self._resource_client.resources.get_by_id(
                    resource.id,
                    api_version="2021-02-01-preview"
                )
                details['last_used'] = sql_client.properties.get('creationDate')

        except AzureError:
            pass  # Return empty details if resource lookup fails

        return details

    def get_resource_usage(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict:
        """Get usage metrics for a specific Azure resource.

        Args:
            resource_id (str): ID of the resource
            start_time (datetime): Start of the period
            end_time (datetime): End of the period

        Returns:
            Dict: Resource usage metrics
        """
        # TODO: Implement Azure resource usage collection
        return {
            'resource_id': resource_id,
            'metrics': {},
            'period_start': start_time.isoformat(),
            'period_end': end_time.isoformat()
        } 