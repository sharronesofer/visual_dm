"""Service for monitoring cloud costs across providers."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import CloudProvider, CostEntry, Budget, BudgetAlert
from ..collectors import AWSCollector, GCPCollector, AzureCollector

class CostMonitorService:
    """Service for monitoring and analyzing cloud costs."""

    def __init__(self, db: Session):
        """Initialize the cost monitor service.

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

    def collect_costs(self, start_time: datetime, end_time: datetime,
                     provider_id: Optional[int] = None,
                     filters: Optional[Dict] = None) -> List[CostEntry]:
        """Collect cost data from cloud providers.

        Args:
            start_time (datetime): Start of the period to collect costs for
            end_time (datetime): End of the period to collect costs for
            provider_id (Optional[int]): Specific provider to collect from
            filters (Optional[Dict]): Optional filters to apply

        Returns:
            List[CostEntry]: List of collected cost entries
        """
        cost_entries = []
        
        # Get providers to collect from
        if provider_id:
            providers = [self.db.query(CloudProvider).get(provider_id)]
        else:
            providers = self.db.query(CloudProvider).all()
        
        # Collect costs from each provider
        for provider in providers:
            if provider.id in self._collectors:
                collector = self._collectors[provider.id]
                
                try:
                    entries = collector.get_cost_data(start_time, end_time, filters)
                    
                    # Convert to CostEntry models
                    for entry in entries:
                        cost_entry = CostEntry(
                            provider_id=provider.id,
                            service_name=entry['service_name'],
                            resource_id=entry['resource_id'],
                            cost_amount=entry['cost_amount'],
                            currency=entry['currency'],
                            start_time=entry['start_time'],
                            end_time=entry['end_time'],
                            tags=entry['tags']
                        )
                        cost_entries.append(cost_entry)
                        self.db.add(cost_entry)
                
                except Exception as e:
                    # Log error but continue with other providers
                    print(f"Error collecting costs from {provider.name}: {str(e)}")
        
        self.db.commit()
        return cost_entries

    def get_cost_summary(self, start_time: datetime, end_time: datetime,
                        group_by: Optional[str] = None,
                        provider_id: Optional[int] = None) -> List[Dict]:
        """Get summary of costs for the specified period.

        Args:
            start_time (datetime): Start of period
            end_time (datetime): End of period
            group_by (Optional[str]): Group results by ('service', 'provider', 'day', 'month')
            provider_id (Optional[int]): Filter by specific provider

        Returns:
            List[Dict]: List of cost summaries
        """
        query = self.db.query(
            func.sum(CostEntry.cost_amount).label('total_cost')
        ).filter(
            CostEntry.start_time >= start_time,
            CostEntry.end_time <= end_time
        )

        if provider_id:
            query = query.filter(CostEntry.provider_id == provider_id)

        if group_by == 'service':
            query = query.add_columns(
                CostEntry.service_name,
                CostEntry.currency
            ).group_by(
                CostEntry.service_name,
                CostEntry.currency
            )
        elif group_by == 'provider':
            query = query.add_columns(
                CloudProvider.name.label('provider_name'),
                CostEntry.currency
            ).join(
                CloudProvider
            ).group_by(
                CloudProvider.name,
                CostEntry.currency
            )
        elif group_by == 'day':
            query = query.add_columns(
                func.date_trunc('day', CostEntry.start_time).label('day'),
                CostEntry.currency
            ).group_by(
                func.date_trunc('day', CostEntry.start_time),
                CostEntry.currency
            )
        elif group_by == 'month':
            query = query.add_columns(
                func.date_trunc('month', CostEntry.start_time).label('month'),
                CostEntry.currency
            ).group_by(
                func.date_trunc('month', CostEntry.start_time),
                CostEntry.currency
            )

        results = query.all()
        summaries = []

        for result in results:
            summary = {'total_cost': float(result.total_cost)}
            
            if group_by == 'service':
                summary.update({
                    'service_name': result.service_name,
                    'currency': result.currency
                })
            elif group_by == 'provider':
                summary.update({
                    'provider_name': result.provider_name,
                    'currency': result.currency
                })
            elif group_by == 'day':
                summary.update({
                    'date': result.day.strftime('%Y-%m-%d'),
                    'currency': result.currency
                })
            elif group_by == 'month':
                summary.update({
                    'month': result.month.strftime('%Y-%m'),
                    'currency': result.currency
                })

            summaries.append(summary)

        return summaries

    def get_cost_trends(self, service_name: str, days: int = 30,
                       provider_id: Optional[int] = None) -> List[Dict]:
        """Get cost trends for a specific service.

        Args:
            service_name (str): Name of the service to get trends for
            days (int): Number of days of history to analyze
            provider_id (Optional[int]): Filter by specific provider

        Returns:
            List[Dict]: Daily cost trends with percentage changes
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        query = self.db.query(
            func.date_trunc('day', CostEntry.start_time).label('day'),
            func.sum(CostEntry.cost_amount).label('daily_cost'),
            CostEntry.currency
        ).filter(
            CostEntry.service_name == service_name,
            CostEntry.start_time >= start_time,
            CostEntry.end_time <= end_time
        ).group_by(
            func.date_trunc('day', CostEntry.start_time),
            CostEntry.currency
        ).order_by(
            func.date_trunc('day', CostEntry.start_time)
        )

        if provider_id:
            query = query.filter(CostEntry.provider_id == provider_id)

        results = query.all()
        trends = []
        prev_cost = None

        for result in results:
            daily_cost = float(result.daily_cost)
            trend = {
                'date': result.day.strftime('%Y-%m-%d'),
                'cost': daily_cost,
                'currency': result.currency
            }
            
            if prev_cost:
                pct_change = ((daily_cost - prev_cost) / prev_cost) * 100 if prev_cost > 0 else 0
                trend['percentage_change'] = round(pct_change, 2)
            
            prev_cost = daily_cost
            trends.append(trend)

        return trends

    def check_budget_alerts(self) -> List[BudgetAlert]:
        """Check all budgets and create alerts if thresholds are exceeded.

        Returns:
            List[BudgetAlert]: List of new budget alerts created
        """
        new_alerts = []
        budgets = self.db.query(Budget).all()
        
        for budget in budgets:
            # Calculate current usage for budget period
            period_start = self._get_budget_period_start(budget.period)
            current_usage = self._calculate_budget_usage(budget, period_start)
            
            # Check each threshold
            for threshold in budget.alert_thresholds:
                threshold_amount = (threshold / 100.0) * budget.amount
                
                if current_usage >= threshold_amount:
                    # Check if alert already exists for this threshold
                    existing_alert = self.db.query(BudgetAlert).filter(
                        BudgetAlert.budget_id == budget.id,
                        BudgetAlert.threshold == threshold,
                        BudgetAlert.alert_time >= period_start
                    ).first()
                    
                    if not existing_alert:
                        # Create new alert
                        alert = BudgetAlert(
                            budget_id=budget.id,
                            threshold=threshold,
                            current_usage=current_usage
                        )
                        self.db.add(alert)
                        new_alerts.append(alert)
        
        self.db.commit()
        return new_alerts

    def _get_budget_period_start(self, period: str) -> datetime:
        """Get start date for budget period.

        Args:
            period (str): Budget period type ('monthly', 'quarterly', 'yearly')

        Returns:
            datetime: Start date of current budget period
        """
        now = datetime.utcnow()
        
        if period == 'monthly':
            return datetime(now.year, now.month, 1)
        elif period == 'quarterly':
            quarter = (now.month - 1) // 3
            return datetime(now.year, quarter * 3 + 1, 1)
        elif period == 'yearly':
            return datetime(now.year, 1, 1)
        else:
            raise ValueError(f"Invalid budget period: {period}")

    def _calculate_budget_usage(self, budget: Budget, period_start: datetime) -> float:
        """Calculate current usage for a budget.

        Args:
            budget (Budget): Budget to calculate usage for
            period_start (datetime): Start of budget period

        Returns:
            float: Current usage amount
        """
        # Query cost entries for budget scope
        query = self.db.query(
            func.sum(CostEntry.cost_amount).label('total_cost')
        ).filter(
            CostEntry.start_time >= period_start,
            CostEntry.currency == budget.currency
        )
        
        # Apply scope filters
        if budget.scope_type == 'project':
            query = query.filter(CostEntry.tags['project'] == budget.scope_id)
        elif budget.scope_type == 'team':
            query = query.filter(CostEntry.tags['team'] == budget.scope_id)
        elif budget.scope_type == 'service':
            query = query.filter(CostEntry.service_name == budget.scope_id)
        
        result = query.first()
        return float(result.total_cost) if result.total_cost else 0.0 