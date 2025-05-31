"""
Arc system - Progression Tracker service.

This module implements advanced analytics and progression monitoring
with comprehensive reporting for arc progression tracking.
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from uuid import UUID

from backend.infrastructure.models import BaseService
from backend.systems.arc.models.arc_progression import (
    ArcProgressionModel, 
    ArcProgressionAnalytics,
    CreateArcProgressionRequest,
    UpdateArcProgressionRequest
)

logger = logging.getLogger(__name__)


class ProgressionTracker(BaseService):
    """Service for tracking and analyzing arc progression"""
    
    def __init__(self, db_session=None, arc_repository=None, progression_repository=None):
        super().__init__(db_session, ArcProgressionModel)
        self.arc_repository = arc_repository
        self.progression_repository = progression_repository
        
    async def start_progression(
        self,
        arc_id: UUID,
        player_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Start tracking progression for an arc"""
        try:
            # Create new progression record
            progression_data = CreateArcProgressionRequest(
                arc_id=arc_id,
                player_id=player_id,
                session_id=session_id
            )
            
            # Initialize progression tracking
            progression = {
                "id": "generated_id",  # Would generate actual UUID
                "arc_id": str(arc_id),
                "player_id": str(player_id) if player_id else None,
                "session_id": str(session_id) if session_id else None,
                "current_step": 0,
                "completed_steps": [],
                "progress_percentage": 0.0,
                "start_time": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "status": "active",
                "analytics_data": {
                    "session_start": datetime.utcnow().isoformat(),
                    "steps_attempted": 0,
                    "choices_made": 0,
                    "time_spent_per_step": {}
                },
                "choices_made": [],
                "time_spent": 0.0
            }
            
            logger.info(f"Started progression tracking for arc {arc_id}")
            return progression
            
        except Exception as e:
            logger.error(f"Error starting progression: {e}")
            raise
    
    async def update_progression(
        self,
        progression_id: UUID,
        update_data: UpdateArcProgressionRequest
    ) -> Dict[str, Any]:
        """Update progression data"""
        try:
            # Calculate progress percentage if steps completed
            if update_data.completed_steps is not None:
                # Would get total steps from arc data
                total_steps = 5  # Placeholder
                progress_percentage = (len(update_data.completed_steps) / total_steps) * 100
                update_data.progress_percentage = progress_percentage
            
            # Update last activity
            current_time = datetime.utcnow()
            
            # Build updated progression data
            updated_progression = {
                "id": str(progression_id),
                "last_activity": current_time.isoformat(),
                "updated_at": current_time.isoformat()
            }
            
            # Add provided updates
            if update_data.current_step is not None:
                updated_progression["current_step"] = update_data.current_step
            if update_data.completed_steps is not None:
                updated_progression["completed_steps"] = update_data.completed_steps
            if update_data.progress_percentage is not None:
                updated_progression["progress_percentage"] = update_data.progress_percentage
            if update_data.status is not None:
                updated_progression["status"] = update_data.status
            if update_data.analytics_data is not None:
                updated_progression["analytics_data"] = update_data.analytics_data
            if update_data.choices_made is not None:
                updated_progression["choices_made"] = update_data.choices_made
            if update_data.time_spent is not None:
                updated_progression["time_spent"] = update_data.time_spent
            
            logger.info(f"Updated progression {progression_id}")
            return updated_progression
            
        except Exception as e:
            logger.error(f"Error updating progression: {e}")
            raise
    
    async def complete_step(
        self,
        progression_id: UUID,
        step_number: int,
        completion_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mark a step as completed and update progression"""
        try:
            # Get current progression (would fetch from repository)
            current_progression = await self._get_progression(progression_id)
            
            # Update completed steps
            completed_steps = current_progression.get("completed_steps", [])
            if step_number not in completed_steps:
                completed_steps.append(step_number)
                completed_steps.sort()
            
            # Update current step to next uncompleted step
            current_step = step_number + 1
            
            # Calculate new progress percentage
            total_steps = 5  # Would get from arc data
            progress_percentage = (len(completed_steps) / total_steps) * 100
            
            # Update analytics
            analytics_data = current_progression.get("analytics_data", {})
            analytics_data["steps_completed"] = len(completed_steps)
            analytics_data["last_step_completed"] = step_number
            analytics_data["last_completion_time"] = datetime.utcnow().isoformat()
            
            if completion_data:
                analytics_data[f"step_{step_number}_data"] = completion_data
            
            # Create update request
            update_request = UpdateArcProgressionRequest(
                current_step=current_step,
                completed_steps=completed_steps,
                progress_percentage=progress_percentage,
                analytics_data=analytics_data
            )
            
            # Update progression
            updated_progression = await self.update_progression(progression_id, update_request)
            
            logger.info(f"Completed step {step_number} for progression {progression_id}")
            return updated_progression
            
        except Exception as e:
            logger.error(f"Error completing step: {e}")
            raise
    
    async def record_choice(
        self,
        progression_id: UUID,
        choice_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record a player choice in the progression"""
        try:
            # Get current progression
            current_progression = await self._get_progression(progression_id)
            
            # Add choice to choices made
            choices_made = current_progression.get("choices_made", [])
            choice_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "step": current_progression.get("current_step", 0),
                **choice_data
            }
            choices_made.append(choice_record)
            
            # Update analytics
            analytics_data = current_progression.get("analytics_data", {})
            analytics_data["choices_made"] = len(choices_made)
            analytics_data["last_choice_time"] = datetime.utcnow().isoformat()
            
            # Update progression
            update_request = UpdateArcProgressionRequest(
                choices_made=choices_made,
                analytics_data=analytics_data
            )
            
            updated_progression = await self.update_progression(progression_id, update_request)
            
            logger.info(f"Recorded choice for progression {progression_id}")
            return updated_progression
            
        except Exception as e:
            logger.error(f"Error recording choice: {e}")
            raise
    
    async def complete_arc(
        self,
        progression_id: UUID,
        completion_type: str = "success",
        final_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Complete an arc progression"""
        try:
            # Get current progression
            current_progression = await self._get_progression(progression_id)
            
            # Calculate final metrics
            start_time = datetime.fromisoformat(current_progression.get("start_time", datetime.utcnow().isoformat()))
            completion_time = datetime.utcnow()
            total_time_spent = (completion_time - start_time).total_seconds() / 60  # minutes
            
            # Update progression to completed
            update_request = UpdateArcProgressionRequest(
                status="completed",
                progress_percentage=100.0,
                time_spent=total_time_spent
            )
            
            updated_progression = await self.update_progression(progression_id, update_request)
            
            # Create completion record (would save to completion records repository)
            completion_record = {
                "progression_id": str(progression_id),
                "completion_type": completion_type,
                "completion_date": completion_time.isoformat(),
                "total_time_spent": total_time_spent,
                "final_data": final_data or {}
            }
            
            logger.info(f"Completed arc progression {progression_id} with type {completion_type}")
            return {
                "progression": updated_progression,
                "completion_record": completion_record
            }
            
        except Exception as e:
            logger.error(f"Error completing arc: {e}")
            raise
    
    async def get_progression_analytics(
        self,
        arc_id: Optional[UUID] = None,
        player_id: Optional[UUID] = None,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> ArcProgressionAnalytics:
        """Get analytics for arc progressions"""
        try:
            # This would query the database for progression data
            # For now, return mock analytics
            
            total_progressions = 10
            active_progressions = 3
            completed_progressions = 7
            
            analytics = ArcProgressionAnalytics(
                total_progressions=total_progressions,
                active_progressions=active_progressions,
                completed_progressions=completed_progressions,
                average_completion_time=45.5,  # minutes
                average_progress_percentage=75.2,
                average_difficulty_rating=6.8,
                average_satisfaction_rating=8.1,
                most_common_stopping_points=[
                    {"step": 3, "count": 4, "percentage": 40.0},
                    {"step": 2, "count": 3, "percentage": 30.0}
                ],
                completion_rate=70.0,
                engagement_metrics={
                    "average_session_length": 35.2,
                    "return_rate": 85.0,
                    "choice_engagement": 92.5
                }
            )
            
            logger.info("Generated progression analytics")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            raise
    
    async def get_player_progression_history(
        self,
        player_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get progression history for a player"""
        try:
            # This would query the database for player progression history
            # For now, return mock data
            
            history = []
            for i in range(min(limit, 5)):  # Mock 5 progressions
                history.append({
                    "id": f"progression_{i}",
                    "arc_id": f"arc_{i}",
                    "arc_name": f"Arc {i + 1}",
                    "status": "completed" if i < 3 else "active",
                    "progress_percentage": 100.0 if i < 3 else 60.0 + (i * 10),
                    "start_time": (datetime.utcnow() - timedelta(days=i * 7)).isoformat(),
                    "completion_time": (datetime.utcnow() - timedelta(days=i * 7 - 2)).isoformat() if i < 3 else None,
                    "time_spent": 30.0 + (i * 10),
                    "difficulty_rating": 5.0 + i,
                    "satisfaction_rating": 7.0 + i
                })
            
            logger.info(f"Retrieved progression history for player {player_id}")
            return history
            
        except Exception as e:
            logger.error(f"Error getting player progression history: {e}")
            raise
    
    async def _get_progression(self, progression_id: UUID) -> Dict[str, Any]:
        """Get progression data (mock implementation)"""
        # This would fetch from the repository
        return {
            "id": str(progression_id),
            "arc_id": "mock_arc_id",
            "current_step": 2,
            "completed_steps": [1],
            "progress_percentage": 20.0,
            "start_time": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "status": "active",
            "analytics_data": {},
            "choices_made": [],
            "time_spent": 15.0
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "status": "healthy",
            "service": "ProgressionTracker",
            "repositories_available": {
                "arc_repository": self.arc_repository is not None,
                "progression_repository": self.progression_repository is not None
            }
        }
