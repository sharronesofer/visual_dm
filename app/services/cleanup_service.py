from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models import CleanupEntry, CleanupRule
from app.api.schemas.cleanup import (
    CleanupRuleCreate, CleanupRuleUpdate,
    CleanupEntryCreate, CleanupEntryUpdate,
    CleanupSummary, ResourceCleanupStatus
)

class CleanupService:
    def __init__(self, db: Session):
        self.db = db

    def create_rule(self, rule: CleanupRuleCreate) -> CleanupRule:
        db_rule = CleanupRule(**rule.model_dump())
        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        return db_rule

    def update_rule(self, rule_id: int, rule_update: CleanupRuleUpdate) -> Optional[CleanupRule]:
        db_rule = self.db.query(CleanupRule).filter(CleanupRule.id == rule_id).first()
        if not db_rule:
            return None
        
        update_data = rule_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_rule, field, value)
        
        self.db.commit()
        self.db.refresh(db_rule)
        return db_rule

    def delete_rule(self, rule_id: int) -> bool:
        db_rule = self.db.query(CleanupRule).filter(CleanupRule.id == rule_id).first()
        if not db_rule:
            return False
        
        self.db.delete(db_rule)
        self.db.commit()
        return True

    def get_rule(self, rule_id: int) -> Optional[CleanupRule]:
        return self.db.query(CleanupRule).filter(CleanupRule.id == rule_id).first()

    def get_rules(self, provider_id: Optional[int] = None, is_active: Optional[bool] = None) -> List[CleanupRule]:
        query = self.db.query(CleanupRule)
        if provider_id is not None:
            query = query.filter(CleanupRule.provider_id == provider_id)
        if is_active is not None:
            query = query.filter(CleanupRule.is_active == is_active)
        return query.all()

    def create_entry(self, entry: CleanupEntryCreate) -> CleanupEntry:
        db_entry = CleanupEntry(**entry.model_dump())
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        return db_entry

    def update_entry(self, entry_id: int, entry_update: CleanupEntryUpdate) -> Optional[CleanupEntry]:
        db_entry = self.db.query(CleanupEntry).filter(CleanupEntry.id == entry_id).first()
        if not db_entry:
            return None
        
        update_data = entry_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_entry, field, value)
        
        self.db.commit()
        self.db.refresh(db_entry)
        return db_entry

    def get_entry(self, entry_id: int) -> Optional[CleanupEntry]:
        return self.db.query(CleanupEntry).filter(CleanupEntry.id == entry_id).first()

    def get_entries(
        self,
        provider_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        is_cleaned: Optional[bool] = None
    ) -> List[CleanupEntry]:
        query = self.db.query(CleanupEntry)
        if provider_id is not None:
            query = query.filter(CleanupEntry.provider_id == provider_id)
        if resource_type is not None:
            query = query.filter(CleanupEntry.resource_type == resource_type)
        if is_cleaned is not None:
            query = query.filter(CleanupEntry.is_cleaned == is_cleaned)
        return query.all()

    def get_cleanup_summary(self) -> CleanupSummary:
        total_resources = self.db.query(func.count(CleanupEntry.id)).scalar()
        cleaned_resources = self.db.query(func.count(CleanupEntry.id))\
            .filter(CleanupEntry.is_cleaned == True).scalar()
        estimated_savings = self.db.query(func.sum(CleanupEntry.estimated_cost))\
            .filter(CleanupEntry.is_cleaned == True).scalar() or 0.0
        active_rules = self.db.query(func.count(CleanupRule.id))\
            .filter(CleanupRule.is_active == True).scalar()

        return CleanupSummary(
            total_resources=total_resources,
            cleaned_resources=cleaned_resources,
            estimated_savings=estimated_savings,
            active_rules=active_rules
        )

    def identify_resources_for_cleanup(self) -> List[CleanupEntry]:
        """Identify resources that match cleanup rules criteria."""
        now = datetime.utcnow()
        
        # Get all active rules
        active_rules = self.db.query(CleanupRule)\
            .filter(CleanupRule.is_active == True)\
            .all()
        
        resources_to_cleanup = []
        for rule in active_rules:
            # Find resources matching rule criteria
            query = self.db.query(CleanupEntry)\
                .filter(
                    CleanupEntry.provider_id == rule.provider_id,
                    CleanupEntry.resource_type == rule.resource_type,
                    CleanupEntry.is_cleaned == False
                )
            
            # Apply idle threshold
            if rule.idle_threshold_days:
                threshold_date = now - timedelta(days=rule.idle_threshold_days)
                query = query.filter(CleanupEntry.last_accessed <= threshold_date)
            
            # Apply cost threshold
            if rule.cost_threshold:
                query = query.filter(CleanupEntry.estimated_cost >= rule.cost_threshold)
            
            matching_resources = query.all()
            resources_to_cleanup.extend(matching_resources)
        
        return resources_to_cleanup

    def mark_resource_cleaned(
        self,
        entry_id: int,
        cleanup_reason: str,
        success: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """Mark a resource as cleaned with status and reason."""
        db_entry = self.db.query(CleanupEntry).filter(CleanupEntry.id == entry_id).first()
        if not db_entry:
            return False, "Resource not found"
        
        if success:
            db_entry.is_cleaned = True
            db_entry.cleaned_at = datetime.utcnow()
            db_entry.cleanup_reason = cleanup_reason
            self.db.commit()
            return True, None
        
        return False, "Cleanup operation failed" 