"""Google Cloud Platform cost and resource data collector."""

from datetime import datetime
from typing import Dict, List, Optional
from google.cloud import billing_v1
from google.cloud import monitoring_v3
from google.cloud import resourcemanager_v3
from google.cloud.billing_v1 import BillingAccount
from google.cloud.billing_v1 import CloudBillingClient
from google.cloud.monitoring_v3 import MetricServiceClient
from google.cloud.resourcemanager_v3 import ProjectsClient
from google.api_core import exceptions
import json

from .base import BaseCollector

class GCPCollector(BaseCollector):
    """Collector for GCP cost and resource data."""

    def initialize_client(self) -> None:
        """Initialize GCP API clients."""
        # Load credentials from JSON string
        creds_dict = json.loads(self.credentials.get('service_account_json'))
        
        # Initialize clients
        self._billing_client = billing_v1.CloudBillingClient.from_service_account_info(creds_dict)
        self._monitoring_client = monitoring_v3.MetricServiceClient.from_service_account_info(creds_dict)
        self._resource_client = resourcemanager_v3.ProjectsClient.from_service_account_info(creds_dict)
        
        # Store project and billing account info
        self.project_id = creds_dict.get('project_id')
        self.project_name = f"projects/{self.project_id}"

    def get_cost_data(self, start_time: datetime, end_time: datetime,
                     filters: Optional[Dict] = None) -> List[Dict]:
        """Get cost data from GCP Billing API.

        Args:
            start_time (datetime): Start of the period to collect costs for
            end_time (datetime): End of the period to collect costs for
            filters (Optional[Dict]): Optional filters to apply

        Returns:
            List[Dict]: List of standardized cost entries
        """
        try:
            # Get billing account
            billing_accounts = self._billing_client.list_billing_accounts()
            billing_account = next(iter(billing_accounts))
            
            # Build request
            request = billing_v1.QueryCostsRequest(
                billing_account=billing_account.name,
                time_period=billing_v1.TimeInterval(
                    start_time=start_time.isoformat() + "Z",
                    end_time=end_time.isoformat() + "Z"
                )
            )

            if filters:
                request.filter = self._build_cost_filter(filters)

            cost_entries = []
            
            # Query costs
            try:
                response = self._billing_client.query_costs(request)
                
                for row in response.rows:
                    entry = {
                        'service': row.dimensions.get('service', {}).get('name', 'Unknown'),
                        'amount': float(row.metrics[0].cost_amount.amount or 0),
                        'currency': row.metrics[0].cost_amount.currency_code or 'USD',
                        'start_time': start_time,
                        'end_time': end_time,
                        'tags': {
                            label.key: label.value
                            for label in row.dimensions.get('labels', [])
                        }
                    }
                    cost_entries.append(self.standardize_cost_entry(entry))

            except exceptions.PermissionDenied:
                raise Exception("Permission denied accessing GCP Billing API")

            return cost_entries

        except Exception as e:
            raise Exception(f"Failed to get GCP cost data: {str(e)}")

    def get_resource_inventory(self, resource_type: Optional[str] = None) -> List[Dict]:
        """Get inventory of GCP resources.

        Args:
            resource_type (Optional[str]): Optional resource type filter

        Returns:
            List[Dict]: List of standardized resource entries
        """
        try:
            resources = []
            
            # Get project details
            project = self._resource_client.get_project(name=self.project_name)
            
            # List resources using Asset API
            request = {
                'parent': self.project_name,
                'content_type': 'RESOURCE',
            }
            
            if resource_type:
                request['asset_types'] = [f"compute.googleapis.com/{resource_type}"]
            
            try:
                # Note: This is a simplified version. In practice, you'd use the Asset API
                # Here we're simulating with basic project resources
                resource_data = {
                    'id': project.project_id,
                    'type': 'project',
                    'name': project.display_name,
                    'region': 'global',
                    'tags': {
                        label.key: label.value
                        for label in project.labels
                    },
                    'last_used': None
                }
                resources.append(self.standardize_resource(resource_data))

            except exceptions.PermissionDenied:
                raise Exception("Permission denied accessing GCP Resource API")

            return resources

        except Exception as e:
            raise Exception(f"Failed to get GCP resource inventory: {str(e)}")

    def get_resource_metrics(self, resource_id: str, metric_name: str,
                           start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get Cloud Monitoring metrics for a specific resource.

        Args:
            resource_id (str): ID of the resource to get metrics for
            metric_name (str): Name of the metric to retrieve
            start_time (datetime): Start of the period to get metrics for
            end_time (datetime): End of the period to get metrics for

        Returns:
            List[Dict]: List of metric data points
        """
        try:
            # Build time interval
            interval = monitoring_v3.TimeInterval({
                'start_time': {'seconds': int(start_time.timestamp())},
                'end_time': {'seconds': int(end_time.timestamp())}
            })

            # Build metric query
            metric_type = f"custom.googleapis.com/{metric_name}"
            request = monitoring_v3.ListTimeSeriesRequest(
                name=self.project_name,
                filter=f'metric.type = "{metric_type}"',
                interval=interval,
                view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
            )

            # Get metrics
            time_series = self._monitoring_client.list_time_series(request)
            
            metrics = []
            for series in time_series:
                for point in series.points:
                    metrics.append({
                        'timestamp': point.interval.end_time.timestamp(),
                        'value': point.value.double_value,
                        'unit': series.metric.unit
                    })

            return metrics

        except Exception as e:
            raise Exception(f"Failed to get GCP resource metrics: {str(e)}")

    def get_resource_tags(self, resource_id: str) -> Dict:
        """Get tags (labels) for a specific GCP resource.

        Args:
            resource_id (str): ID of the resource to get tags for

        Returns:
            Dict: Dictionary of tag key-value pairs
        """
        try:
            # For simplicity, we're just getting project labels
            # In practice, you'd need to determine the resource type and use appropriate API
            project = self._resource_client.get_project(name=self.project_name)
            return {
                label.key: label.value
                for label in project.labels
            }

        except Exception as e:
            raise Exception(f"Failed to get GCP resource tags: {str(e)}")

    def validate_credentials(self) -> bool:
        """Validate GCP credentials.

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            # Try to get project info
            self._resource_client.get_project(name=self.project_name)
            return True
        except Exception:
            return False

    def _build_cost_filter(self, filters: Dict) -> str:
        """Build GCP Billing API filter string.

        Args:
            filters (Dict): Filter parameters

        Returns:
            str: GCP Billing API filter string
        """
        filter_parts = []

        if 'services' in filters:
            services = [f'service.name = "{service}"' for service in filters['services']]
            filter_parts.append(f"({' OR '.join(services)})")

        if 'tags' in filters:
            for key, value in filters['tags'].items():
                if isinstance(value, list):
                    values = [f'labels.{key} = "{v}"' for v in value]
                    filter_parts.append(f"({' OR '.join(values)})")
                else:
                    filter_parts.append(f'labels.{key} = "{value}"')

        return ' AND '.join(filter_parts) if filter_parts else ""

    def get_resource_usage(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict:
        """Get usage metrics for a specific GCP resource.

        Args:
            resource_id (str): ID of the resource
            start_time (datetime): Start of the period
            end_time (datetime): End of the period

        Returns:
            Dict: Resource usage metrics
        """
        # TODO: Implement GCP resource usage collection
        return {
            'resource_id': resource_id,
            'metrics': {},
            'period_start': start_time.isoformat(),
            'period_end': end_time.isoformat()
        } 