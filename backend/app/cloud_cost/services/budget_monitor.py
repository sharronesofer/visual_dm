"""Service for monitoring cloud costs against budgets."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Budget, BudgetAlert, CostEntry

class BudgetMonitorService:
    """Service for managing and monitoring cloud cost budgets."""

    def __init__(self, db: Session):
        """Initialize the budget monitor service.

        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db

    def create_budget(self, name: str, amount: float, currency: str,
                     period: str, scope_type: str, scope_id: str,
                     alert_thresholds: List[float] = [80.0, 90.0, 100.0]) -> Budget:
        """Create a new budget.

        Args:
            name (str): Name of the budget
            amount (float): Budget amount
            currency (str): Currency code (e.g., 'USD')
            period (str): Budget period ('monthly', 'quarterly', 'yearly')
            scope_type (str): Type of scope ('project', 'team', 'service')
            scope_id (str): ID of the scope
            alert_thresholds (List[float]): Percentage thresholds for alerts

        Returns:
            Budget: Created budget object
        """
        budget = Budget(
            name=name,
            amount=amount,
            currency=currency,
            period=period,
            scope_type=scope_type,
            scope_id=scope_id,
            alert_thresholds=alert_thresholds
        )
        
        self.db.add(budget)
        self.db.commit()
        
        return budget

    def update_budget(self, budget_id: int, **kwargs) -> Optional[Budget]:
        """Update an existing budget.

        Args:
            budget_id (int): ID of the budget to update
            **kwargs: Fields to update

        Returns:
            Optional[Budget]: Updated budget object or None if not found
        """
        budget = self.db.query(Budget).get(budget_id)
        if not budget:
            return None
        
        for key, value in kwargs.items():
            if hasattr(budget, key):
                setattr(budget, key, value)
        
        self.db.commit()
        return budget

    def delete_budget(self, budget_id: int) -> bool:
        """Delete a budget.

        Args:
            budget_id (int): ID of the budget to delete

        Returns:
            bool: True if deletion was successful
        """
        budget = self.db.query(Budget).get(budget_id)
        if not budget:
            return False
        
        self.db.delete(budget)
        self.db.commit()
        return True

    def get_budget_status(self, budget_id: int) -> Dict:
        """Get current status of a budget.

        Args:
            budget_id (int): ID of the budget to check

        Returns:
            Dict: Budget status information
        """
        budget = self.db.query(Budget).get(budget_id)
        if not budget:
            return {}
        
        period_start = self._get_period_start(budget.period)
        current_usage = self._calculate_usage(budget, period_start)
        percentage_used = (current_usage / budget.amount) * 100 if budget.amount > 0 else 0
        
        return {
            'budget_id': budget.id,
            'name': budget.name,
            'period': budget.period,
            'amount': budget.amount,
            'currency': budget.currency,
            'current_usage': current_usage,
            'percentage_used': round(percentage_used, 2),
            'remaining': budget.amount - current_usage,
            'period_start': period_start,
            'period_end': self._get_period_end(budget.period),
            'status': 'exceeded' if current_usage > budget.amount else 'within_budget'
        }

    def get_all_budget_statuses(self, active_only: bool = True) -> List[Dict]:
        """Get status of all budgets.

        Args:
            active_only (bool): Only include active budgets

        Returns:
            List[Dict]: List of budget statuses
        """
        query = self.db.query(Budget)
        if active_only:
            query = query.filter(Budget.is_active == True)
        
        budgets = query.all()
        return [self.get_budget_status(budget.id) for budget in budgets]

    def check_budget_alerts(self) -> List[BudgetAlert]:
        """Check all budgets and create alerts if thresholds are exceeded.

        Returns:
            List[BudgetAlert]: List of new alerts created
        """
        new_alerts = []
        budgets = self.db.query(Budget).filter(Budget.is_active == True).all()
        
        for budget in budgets:
            period_start = self._get_period_start(budget.period)
            current_usage = self._calculate_usage(budget, period_start)
            percentage_used = (current_usage / budget.amount) * 100 if budget.amount > 0 else 0
            
            for threshold in budget.alert_thresholds:
                if percentage_used >= threshold:
                    # Check if alert already exists for this threshold in current period
                    existing_alert = self.db.query(BudgetAlert).filter(
                        BudgetAlert.budget_id == budget.id,
                        BudgetAlert.threshold == threshold,
                        BudgetAlert.alert_time >= period_start
                    ).first()
                    
                    if not existing_alert:
                        alert = BudgetAlert(
                            budget_id=budget.id,
                            threshold=threshold,
                            current_usage=current_usage,
                            percentage_used=percentage_used
                        )
                        self.db.add(alert)
                        new_alerts.append(alert)
        
        self.db.commit()
        return new_alerts

    def get_budget_forecast(self, budget_id: int) -> Dict:
        """Get spending forecast for a budget.

        Args:
            budget_id (int): ID of the budget to forecast

        Returns:
            Dict: Forecast information
        """
        budget = self.db.query(Budget).get(budget_id)
        if not budget:
            return {}
        
        period_start = self._get_period_start(budget.period)
        current_usage = self._calculate_usage(budget, period_start)
        days_elapsed = (datetime.utcnow() - period_start).days
        days_in_period = (self._get_period_end(budget.period) - period_start).days
        
        if days_elapsed > 0:
            daily_rate = current_usage / days_elapsed
            projected_usage = daily_rate * days_in_period
            projected_percentage = (projected_usage / budget.amount) * 100 if budget.amount > 0 else 0
            
            return {
                'budget_id': budget.id,
                'current_usage': current_usage,
                'projected_usage': projected_usage,
                'projected_percentage': round(projected_percentage, 2),
                'daily_rate': daily_rate,
                'days_remaining': days_in_period - days_elapsed,
                'status': 'over_budget' if projected_usage > budget.amount else 'within_budget'
            }
        
        return {
            'budget_id': budget.id,
            'current_usage': current_usage,
            'projected_usage': current_usage,
            'projected_percentage': 0.0,
            'daily_rate': 0.0,
            'days_remaining': days_in_period,
            'status': 'within_budget'
        }

    def get_budget_history(self, budget_id: int, months: int = 12) -> List[Dict]:
        """Get historical budget performance.

        Args:
            budget_id (int): ID of the budget
            months (int): Number of months of history to return

        Returns:
            List[Dict]: List of historical budget periods
        """
        budget = self.db.query(Budget).get(budget_id)
        if not budget:
            return []
        
        history = []
        end_date = datetime.utcnow()
        
        for i in range(months):
            if budget.period == 'monthly':
                period_start = datetime(end_date.year, end_date.month, 1)
                period_end = self._get_period_end(budget.period, period_start)
            elif budget.period == 'quarterly':
                quarter = (end_date.month - 1) // 3
                period_start = datetime(end_date.year, quarter * 3 + 1, 1)
                period_end = self._get_period_end(budget.period, period_start)
            else:  # yearly
                period_start = datetime(end_date.year, 1, 1)
                period_end = self._get_period_end(budget.period, period_start)
            
            usage = self._calculate_usage(budget, period_start, period_end)
            percentage = (usage / budget.amount) * 100 if budget.amount > 0 else 0
            
            history.append({
                'period_start': period_start,
                'period_end': period_end,
                'budget_amount': budget.amount,
                'actual_usage': usage,
                'percentage_used': round(percentage, 2),
                'status': 'exceeded' if usage > budget.amount else 'within_budget'
            })
            
            # Move to previous period
            if budget.period == 'monthly':
                end_date = end_date.replace(day=1) - timedelta(days=1)
            elif budget.period == 'quarterly':
                end_date = end_date.replace(month=quarter * 3 + 1, day=1) - timedelta(days=1)
            else:  # yearly
                end_date = end_date.replace(month=1, day=1) - timedelta(days=1)
        
        return history

    def _get_period_start(self, period: str, reference_date: Optional[datetime] = None) -> datetime:
        """Get start date for budget period.

        Args:
            period (str): Budget period type
            reference_date (Optional[datetime]): Reference date for calculation

        Returns:
            datetime: Period start date
        """
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        if period == 'monthly':
            return datetime(reference_date.year, reference_date.month, 1)
        elif period == 'quarterly':
            quarter = (reference_date.month - 1) // 3
            return datetime(reference_date.year, quarter * 3 + 1, 1)
        elif period == 'yearly':
            return datetime(reference_date.year, 1, 1)
        else:
            raise ValueError(f"Invalid budget period: {period}")

    def _get_period_end(self, period: str, start_date: Optional[datetime] = None) -> datetime:
        """Get end date for budget period.

        Args:
            period (str): Budget period type
            start_date (Optional[datetime]): Start date of the period

        Returns:
            datetime: Period end date
        """
        if start_date is None:
            start_date = self._get_period_start(period)
        
        if period == 'monthly':
            if start_date.month == 12:
                return datetime(start_date.year + 1, 1, 1) - timedelta(seconds=1)
            return datetime(start_date.year, start_date.month + 1, 1) - timedelta(seconds=1)
        elif period == 'quarterly':
            if start_date.month >= 10:
                return datetime(start_date.year + 1, 1, 1) - timedelta(seconds=1)
            return datetime(start_date.year, start_date.month + 3, 1) - timedelta(seconds=1)
        elif period == 'yearly':
            return datetime(start_date.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            raise ValueError(f"Invalid budget period: {period}")

    def _calculate_usage(self, budget: Budget, start_time: datetime,
                        end_time: Optional[datetime] = None) -> float:
        """Calculate usage for a budget in a specific period.

        Args:
            budget (Budget): Budget to calculate usage for
            start_time (datetime): Start of period
            end_time (Optional[datetime]): End of period

        Returns:
            float: Total usage amount
        """
        if end_time is None:
            end_time = datetime.utcnow()
        
        query = self.db.query(
            func.sum(CostEntry.cost_amount).label('total_cost')
        ).filter(
            CostEntry.start_time >= start_time,
            CostEntry.end_time <= end_time,
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