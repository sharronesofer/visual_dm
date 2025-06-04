"""
Faction Succession Repository

This module provides data access operations for faction succession crises
according to Task 69 requirements and repository pattern standards.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from backend.systems.faction.models.succession import (
    SuccessionCrisisEntity,
    SuccessionCrisisStatus,
    SuccessionTrigger,
    SuccessionType
)
from backend.infrastructure.shared.exceptions import FactionNotFoundError

logger = logging.getLogger(__name__)


class SuccessionRepository:
    """Repository for succession crisis data operations"""
    
    def __init__(self):
        logger.info("SuccessionRepository initialized")
    
    def create_crisis(
        self,
        db: Session,
        crisis: SuccessionCrisisEntity
    ) -> SuccessionCrisisEntity:
        """
        Create a new succession crisis
        """
        db.add(crisis)
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Created succession crisis {crisis.id} for faction {crisis.faction_name}")
        return crisis
    
    def get_crisis_by_id(
        self,
        db: Session,
        crisis_id: UUID
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Get succession crisis by ID
        """
        return db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.id == crisis_id
        ).first()
    
    def get_active_crises_for_faction(
        self,
        db: Session,
        faction_id: UUID
    ) -> List[SuccessionCrisisEntity]:
        """
        Get all active succession crises for a faction
        """
        return db.query(SuccessionCrisisEntity).filter(
            and_(
                SuccessionCrisisEntity.faction_id == faction_id,
                SuccessionCrisisEntity.status.in_(["pending", "in_progress"])
            )
        ).order_by(desc(SuccessionCrisisEntity.created_at)).all()
    
    def get_all_active_crises(
        self,
        db: Session,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get all active succession crises across all factions
        """
        query = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.status.in_(["pending", "in_progress"])
        ).order_by(desc(SuccessionCrisisEntity.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_crises_by_status(
        self,
        db: Session,
        status: SuccessionCrisisStatus,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get succession crises by status
        """
        query = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.status == status.value
        ).order_by(desc(SuccessionCrisisEntity.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_crises_by_trigger(
        self,
        db: Session,
        trigger: SuccessionTrigger,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get succession crises by trigger type
        """
        query = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.trigger == trigger.value
        ).order_by(desc(SuccessionCrisisEntity.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_crises_by_succession_type(
        self,
        db: Session,
        succession_type: SuccessionType,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get succession crises by succession type
        """
        query = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.succession_type == succession_type.value
        ).order_by(desc(SuccessionCrisisEntity.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_crises_with_external_interference(
        self,
        db: Session,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get succession crises that have external faction interference
        """
        query = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.interfering_factions.isnot(None)
        ).order_by(desc(SuccessionCrisisEntity.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_faction_split_crises(
        self,
        db: Session,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get succession crises that resulted in faction splits
        """
        query = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.faction_split == True
        ).order_by(desc(SuccessionCrisisEntity.created_at))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_low_stability_crises(
        self,
        db: Session,
        stability_threshold: float = 0.5,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get active succession crises with low faction stability
        """
        query = db.query(SuccessionCrisisEntity).filter(
            and_(
                SuccessionCrisisEntity.status.in_(["pending", "in_progress"]),
                SuccessionCrisisEntity.faction_stability < stability_threshold
            )
        ).order_by(asc(SuccessionCrisisEntity.faction_stability))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_overdue_crises(
        self,
        db: Session,
        limit: Optional[int] = None
    ) -> List[SuccessionCrisisEntity]:
        """
        Get succession crises that are overdue (past estimated duration)
        """
        current_time = datetime.utcnow()
        
        query = db.query(SuccessionCrisisEntity).filter(
            and_(
                SuccessionCrisisEntity.status.in_(["pending", "in_progress"]),
                SuccessionCrisisEntity.estimated_duration.isnot(None),
                # Crisis started + estimated duration < now
                (SuccessionCrisisEntity.crisis_start + 
                 (SuccessionCrisisEntity.estimated_duration * 86400))  # Convert days to seconds
                < current_time
            )
        ).order_by(desc(SuccessionCrisisEntity.crisis_start))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update_crisis(
        self,
        db: Session,
        crisis_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Update succession crisis with provided data
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis:
            return None
        
        # Update fields that are provided
        for field, value in update_data.items():
            if hasattr(crisis, field) and value is not None:
                setattr(crisis, field, value)
        
        # Always update timestamp
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Updated succession crisis {crisis_id}")
        return crisis
    
    def add_candidate_to_crisis(
        self,
        db: Session,
        crisis_id: UUID,
        candidate_data: Dict[str, Any]
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Add a candidate to a succession crisis
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis:
            return None
        
        # Add candidate to the list
        candidates = crisis.candidates or []
        candidates.append(candidate_data)
        crisis.candidates = candidates
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Added candidate to succession crisis {crisis_id}")
        return crisis
    
    def update_candidate_in_crisis(
        self,
        db: Session,
        crisis_id: UUID,
        candidate_id: UUID,
        candidate_updates: Dict[str, Any]
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Update a specific candidate within a succession crisis
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis or not crisis.candidates:
            return None
        
        # Find and update the candidate
        for candidate in crisis.candidates:
            if candidate.get("character_id") == str(candidate_id):
                candidate.update(candidate_updates)
                break
        
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Updated candidate {candidate_id} in crisis {crisis_id}")
        return crisis
    
    def remove_candidate_from_crisis(
        self,
        db: Session,
        crisis_id: UUID,
        candidate_id: UUID
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Remove a candidate from a succession crisis
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis or not crisis.candidates:
            return None
        
        # Remove the candidate
        crisis.candidates = [
            candidate for candidate in crisis.candidates
            if candidate.get("character_id") != str(candidate_id)
        ]
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Removed candidate {candidate_id} from crisis {crisis_id}")
        return crisis
    
    def add_interference_to_crisis(
        self,
        db: Session,
        crisis_id: UUID,
        interfering_faction_id: UUID,
        interference_data: Dict[str, Any]
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Add external interference to a succession crisis
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis:
            return None
        
        # Add to interfering factions list
        interfering_factions = crisis.interfering_factions or []
        if interfering_faction_id not in interfering_factions:
            interfering_factions.append(interfering_faction_id)
            crisis.interfering_factions = interfering_factions
        
        # Update interference details
        interference_details = crisis.interference_details or {}
        interference_details[str(interfering_faction_id)] = interference_data
        crisis.interference_details = interference_details
        
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Added interference from faction {interfering_faction_id} to crisis {crisis_id}")
        return crisis
    
    def resolve_crisis(
        self,
        db: Session,
        crisis_id: UUID,
        winner_id: Optional[UUID],
        resolution_method: str
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Mark a succession crisis as resolved
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis:
            return None
        
        crisis.status = "resolved"
        crisis.winner_id = winner_id
        crisis.resolution_method = resolution_method
        crisis.crisis_end = datetime.utcnow()
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Resolved succession crisis {crisis_id} with winner {winner_id}")
        return crisis
    
    def mark_crisis_failed(
        self,
        db: Session,
        crisis_id: UUID,
        reason: str
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Mark a succession crisis as failed
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis:
            return None
        
        crisis.status = "failed"
        crisis.resolution_method = f"Crisis failed: {reason}"
        crisis.crisis_end = datetime.utcnow()
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Marked succession crisis {crisis_id} as failed: {reason}")
        return crisis
    
    def mark_crisis_as_schism(
        self,
        db: Session,
        crisis_id: UUID,
        new_faction_ids: List[UUID]
    ) -> Optional[SuccessionCrisisEntity]:
        """
        Mark a succession crisis as resulting in faction schism/split
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis:
            return None
        
        crisis.status = "schism"
        crisis.faction_split = True
        crisis.new_factions = new_faction_ids
        crisis.resolution_method = f"Faction split into {len(new_faction_ids)} new factions"
        crisis.crisis_end = datetime.utcnow()
        crisis.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(crisis)
        
        logger.info(f"Marked succession crisis {crisis_id} as schism with {len(new_faction_ids)} new factions")
        return crisis
    
    def get_succession_metrics(self, db: Session) -> Dict[str, Any]:
        """
        Get comprehensive succession crisis metrics
        """
        total_crises = db.query(SuccessionCrisisEntity).count()
        active_crises = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.status.in_(["pending", "in_progress"])
        ).count()
        resolved_crises = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.status == "resolved"
        ).count()
        failed_crises = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.status == "failed"
        ).count()
        faction_splits = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.faction_split == True
        ).count()
        
        # Average duration calculation for resolved crises
        resolved_with_duration = db.query(SuccessionCrisisEntity).filter(
            and_(
                SuccessionCrisisEntity.status == "resolved",
                SuccessionCrisisEntity.crisis_end.isnot(None)
            )
        ).all()
        
        avg_duration = 0.0
        if resolved_with_duration:
            total_duration = sum(
                (crisis.crisis_end - crisis.crisis_start).days 
                for crisis in resolved_with_duration
            )
            avg_duration = total_duration / len(resolved_with_duration)
        
        # Average number of candidates
        crises_with_candidates = db.query(SuccessionCrisisEntity).filter(
            SuccessionCrisisEntity.candidates.isnot(None)
        ).all()
        
        avg_candidates = 0.0
        if crises_with_candidates:
            total_candidates = sum(
                len(crisis.candidates) for crisis in crises_with_candidates
            )
            avg_candidates = total_candidates / len(crises_with_candidates)
        
        # Average stability impact
        avg_stability = db.query(SuccessionCrisisEntity).with_entities(
            db.func.avg(SuccessionCrisisEntity.faction_stability)
        ).scalar() or 1.0
        
        return {
            "total_crises": total_crises,
            "active_crises": active_crises,
            "resolved_crises": resolved_crises,
            "failed_crises": failed_crises,
            "faction_splits": faction_splits,
            "average_duration_days": avg_duration,
            "average_candidates": avg_candidates,
            "average_stability_impact": float(avg_stability)
        }
    
    def delete_crisis(
        self,
        db: Session,
        crisis_id: UUID
    ) -> bool:
        """
        Delete a succession crisis (use with caution)
        """
        crisis = self.get_crisis_by_id(db, crisis_id)
        if not crisis:
            return False
        
        db.delete(crisis)
        db.commit()
        
        logger.info(f"Deleted succession crisis {crisis_id}")
        return True 