"""AWS cost and resource data collector."""

import boto3
from datetime import datetime
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

from .base import BaseCollector

class AWSCollector(BaseCollector):
    """Collector for AWS cost and resource data."""

    def initialize_client(self) -> None:
        """Initialize AWS API clients."""
        session = boto3.Session(
            aws_access_key_id=self.credentials.get('access_key_id'),
            aws_secret_access_key=self.credentials.get('secret_access_key'),
            region_name=self.credentials.get('region', 'us-east-1')
        )
        self._cost_explorer = session.client('ce')
        self._cloudwatch = session.client('cloudwatch')
        self._resource_groups = session.client('resource-groups')
        self._tag_api = session.client('resourcegroupstaggingapi')

    def get_cost_data(self, start_time: datetime, end_time: datetime,
                     filters: Optional[Dict] = None) -> List[Dict]:
        """Get cost data from AWS Cost Explorer.

        Args:
            start_time (datetime): Start of the period to collect costs for
            end_time (datetime): End of the period to collect costs for
            filters (Optional[Dict]): Optional filters to apply

        Returns:
            List[Dict]: List of standardized cost entries
        """
        try:
            cost_params = {
                'TimePeriod': {
                    'Start': start_time.strftime('%Y-%m-%d'),
                    'End': end_time.strftime('%Y-%m-%d')
                },
                'Granularity': 'DAILY',
                'Metrics': ['UnblendedCost'],
                'GroupBy': [
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'TAG', 'Key': 'Name'}
                ]
            }

            if filters:
                cost_params['Filter'] = self._build_filters(filters)

            paginator = self._cost_explorer.get_paginator('get_cost_and_usage')
            cost_entries = []

            for page in paginator.paginate(**cost_params):
                for result in page.get('ResultsByTime', []):
                    for group in result.get('Groups', []):
                        entry = {
                            'service_name': group['Keys'][0],  # Service name
                            'resource_id': group['Keys'][1],  # Resource name tag
                            'cost_amount': float(group['Metrics']['UnblendedCost']['Amount']),
                            'currency': group['Metrics']['UnblendedCost']['Unit'],
                            'start_time': datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d'),
                            'end_time': datetime.strptime(result['TimePeriod']['End'], '%Y-%m-%d'),
                            'tags': {'Name': group['Keys'][1]} if len(group['Keys']) > 1 else {}
                        }
                        cost_entries.append(self.standardize_cost_entry(entry))

            return cost_entries

        except ClientError as e:
            raise Exception(f"Failed to get AWS cost data: {str(e)}")

    def get_resource_inventory(self, resource_type: Optional[str] = None) -> List[Dict]:
        """Get inventory of AWS resources.

        Args:
            resource_type (Optional[str]): Optional resource type filter

        Returns:
            List[Dict]: List of standardized resource entries
        """
        try:
            resources = []
            paginator = self._tag_api.get_paginator('get_resources')
            
            params = {'ResourcesPerPage': 50}
            if resource_type:
                params['ResourceTypeFilters'] = [resource_type]

            for page in paginator.paginate(**params):
                for resource in page['ResourceTagMappingList']:
                    arn = resource['ResourceARN']
                    tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
                    
                    # Extract basic resource info from ARN
                    resource_info = self._parse_arn(arn)
                    
                    # Get additional resource details if available
                    details = self._get_resource_details(resource_info['type'], arn)
                    
                    resource_data = {
                        'id': arn,
                        'type': resource_info['type'],
                        'name': details.get('name', resource_info.get('name')),
                        'region': resource_info['region'],
                        'tags': tags,
                        'last_used': details.get('last_used')
                    }
                    resources.append(self.standardize_resource(resource_data))

            return resources

        except ClientError as e:
            raise Exception(f"Failed to get AWS resource inventory: {str(e)}")

    def get_resource_metrics(self, resource_id: str, metric_name: str,
                           start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get CloudWatch metrics for a specific resource.

        Args:
            resource_id (str): ID of the resource to get metrics for
            metric_name (str): Name of the metric to retrieve
            start_time (datetime): Start of the period to get metrics for
            end_time (datetime): End of the period to get metrics for

        Returns:
            List[Dict]: List of metric data points
        """
        try:
            # Parse resource type from ID (ARN)
            resource_info = self._parse_arn(resource_id)
            namespace = self._get_metric_namespace(resource_info['type'])

            response = self._cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=[{'Name': 'ResourceId', 'Value': resource_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour periods
                Statistics=['Average']
            )

            return [
                {
                    'timestamp': point['Timestamp'],
                    'value': point['Average'],
                    'unit': response['Unit']
                }
                for point in response['Datapoints']
            ]

        except ClientError as e:
            raise Exception(f"Failed to get AWS resource metrics: {str(e)}")

    def get_resource_tags(self, resource_id: str) -> Dict:
        """Get tags for a specific AWS resource.

        Args:
            resource_id (str): ARN of the resource to get tags for

        Returns:
            Dict: Dictionary of tag key-value pairs
        """
        try:
            response = self._tag_api.get_resources(ResourceARNList=[resource_id])
            if response['ResourceTagMappingList']:
                return {
                    tag['Key']: tag['Value']
                    for tag in response['ResourceTagMappingList'][0].get('Tags', [])
                }
            return {}

        except ClientError as e:
            raise Exception(f"Failed to get AWS resource tags: {str(e)}")

    def validate_credentials(self) -> bool:
        """Validate AWS credentials.

        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            self._cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': datetime.now().strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            return True
        except ClientError:
            return False

    def _build_filters(self, filters: Dict) -> Dict:
        """Build AWS Cost Explorer filters from generic filters.

        Args:
            filters (Dict): Generic filters

        Returns:
            Dict: AWS-specific filters
        """
        aws_filters = {'And': []}

        if 'services' in filters:
            aws_filters['And'].append({
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': filters['services']
                }
            })

        if 'tags' in filters:
            for key, value in filters['tags'].items():
                aws_filters['And'].append({
                    'Tags': {
                        'Key': key,
                        'Values': [value] if isinstance(value, str) else value
                    }
                })

        return aws_filters

    def _parse_arn(self, arn: str) -> Dict:
        """Parse AWS ARN into components.

        Args:
            arn (str): AWS ARN string

        Returns:
            Dict: Parsed ARN components
        """
        parts = arn.split(':')
        return {
            'partition': parts[1],
            'service': parts[2],
            'region': parts[3],
            'account': parts[4],
            'type': parts[5].split('/')[0] if '/' in parts[5] else parts[5],
            'name': parts[5].split('/')[-1] if '/' in parts[5] else None
        }

    def _get_resource_details(self, resource_type: str, resource_id: str) -> Dict:
        """Get additional details for specific resource types.

        Args:
            resource_type (str): Type of AWS resource
            resource_id (str): Resource identifier/ARN

        Returns:
            Dict: Additional resource details
        """
        details = {}
        
        try:
            if resource_type == 'ec2':
                ec2 = boto3.resource('ec2')
                instance = ec2.Instance(resource_id.split('/')[-1])
                details['name'] = next((tag['Value'] for tag in instance.tags or []
                                     if tag['Key'] == 'Name'), None)
                details['last_used'] = instance.launch_time
            
            elif resource_type == 'rds':
                rds = boto3.client('rds')
                response = rds.describe_db_instances(
                    DBInstanceIdentifier=resource_id.split(':')[-1]
                )
                if response['DBInstances']:
                    instance = response['DBInstances'][0]
                    details['name'] = instance['DBInstanceIdentifier']
                    details['last_used'] = instance['InstanceCreateTime']

        except ClientError:
            pass  # Return empty details if resource lookup fails

        return details

    def _get_metric_namespace(self, resource_type: str) -> str:
        """Get CloudWatch namespace for resource type.

        Args:
            resource_type (str): Type of AWS resource

        Returns:
            str: CloudWatch metric namespace
        """
        namespace_map = {
            'ec2': 'AWS/EC2',
            'rds': 'AWS/RDS',
            's3': 'AWS/S3',
            'lambda': 'AWS/Lambda',
            'dynamodb': 'AWS/DynamoDB'
        }
        return namespace_map.get(resource_type, f"AWS/{resource_type.upper()}") 