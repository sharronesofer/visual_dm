"""
Arc system - Progression Tracker service.

This module implements advanced analytics and progression monitoring
with comprehensive reporting for arc progression tracking.
"""

from typing import Optional, Dict, Any, List, Tuple
import logging
from datetime import datetime, timedelta
from uuid import UUID
import statistics
from dataclasses import dataclass

from backend.infrastructure.models import BaseService
from backend.infrastructure.repositories.arc.arc_repository import ArcRepository
from backend.infrastructure.repositories.arc.arc_progression_repository import ArcProgressionRepository
from backend.systems.arc.models.arc_progression import (
    ArcProgressionModel, 
    ArcProgressionAnalytics,
    CreateArcProgressionRequest,
    UpdateArcProgressionRequest
)
from backend.systems.arc.models.arc import ArcModel, ArcStatus, ArcType
from backend.systems.arc.models.arc_step import ArcStepModel, ArcStepStatus
from backend.systems.arc.business_rules import calculate_arc_complexity_score

logger = logging.getLogger(__name__)


@dataclass
class ProgressMilestone:
    """Represents a significant progress milestone"""
    milestone_id: str
    arc_id: UUID
    milestone_type: str  # step_completion, percentage_threshold, time_based, etc.
    achieved_at: datetime
    description: str
    metadata: Dict[str, Any]


@dataclass
class ProgressionMetrics:
    """Comprehensive progression metrics for an arc"""
    arc_id: UUID
    
    # Basic progress
    completion_percentage: float
    completed_steps: int
    total_steps: int
    
    # Time metrics
    elapsed_time_hours: float
    estimated_remaining_hours: Optional[float]
    velocity_steps_per_hour: Optional[float]
    
    # Quality metrics
    average_step_completion_time: Optional[float]
    steps_completed_on_first_try: int
    steps_requiring_retries: int
    
    # Engagement metrics
    active_sessions: int
    last_activity: datetime
    longest_break_hours: Optional[float]
    
    # Milestone tracking
    milestones_achieved: List[ProgressMilestone]
    next_milestone: Optional[str]
    
    # Predictive analytics
    projected_completion_date: Optional[datetime]
    completion_confidence: float  # 0-1 score
    risk_factors: List[str]


class ProgressionTracker(BaseService):
    """Service for tracking and analyzing arc progression"""
    
    def __init__(self, db_session=None, arc_repository=None, progression_repository=None):
        super().__init__(db_session, ArcProgressionModel)
        self.arc_repository = arc_repository or ArcRepository(db_session)
        self.progression_repository = progression_repository or ArcProgressionRepository(db_session)
        self.milestone_definitions = self._initialize_milestone_definitions()
    
    def _initialize_milestone_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Define standard milestone types and their criteria."""
        return {
            "first_step": {
                "description": "Completed first step of the arc",
                "criteria": lambda metrics: metrics.completed_steps >= 1,
                "significance": "low"
            },
            "quarter_complete": {
                "description": "Reached 25% completion",
                "criteria": lambda metrics: metrics.completion_percentage >= 25,
                "significance": "medium"
            },
            "half_complete": {
                "description": "Reached 50% completion (halfway point)",
                "criteria": lambda metrics: metrics.completion_percentage >= 50,
                "significance": "high"
            },
            "three_quarters": {
                "description": "Reached 75% completion",
                "criteria": lambda metrics: metrics.completion_percentage >= 75,
                "significance": "high"
            },
            "final_stretch": {
                "description": "Reached 90% completion (final stretch)",
                "criteria": lambda metrics: metrics.completion_percentage >= 90,
                "significance": "medium"
            },
            "speed_demon": {
                "description": "Completed arc faster than estimated",
                "criteria": lambda metrics: (
                    metrics.completion_percentage == 100 and 
                    metrics.elapsed_time_hours < (metrics.estimated_remaining_hours or float('inf')) * 0.8
                ),
                "significance": "special"
            },
            "perfectionist": {
                "description": "Completed all steps on first try",
                "criteria": lambda metrics: (
                    metrics.completion_percentage == 100 and 
                    metrics.steps_requiring_retries == 0
                ),
                "significance": "special"
            },
            "persistent": {
                "description": "Overcame multiple step failures",
                "criteria": lambda metrics: metrics.steps_requiring_retries >= 3,
                "significance": "special"
            }
        }
    
    async def _get_arc_total_steps(self, arc_id: UUID) -> int:
        """Get the total number of steps for an arc from the database."""
        try:
            arc_entity = self.arc_repository.get_by_id(arc_id)
            if arc_entity:
                return arc_entity.total_steps or 5  # fallback to 5 if not set
            else:
                logger.warning(f"Arc {arc_id} not found, using default step count of 5")
                return 5
        except Exception as e:
            logger.error(f"Error getting arc total steps for {arc_id}: {e}")
            return 5  # fallback value
        
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
                # Get current progression to find arc_id
                current_progression = await self._get_progression(progression_id)
                arc_id = UUID(current_progression.get("arc_id"))
                
                # Get actual total steps from arc data
                total_steps = await self._get_arc_total_steps(arc_id)
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
            
            # Get actual total steps from arc data
            arc_id = UUID(current_progression.get("arc_id"))
            total_steps = await self._get_arc_total_steps(arc_id)
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

    def calculate_comprehensive_metrics(
        self,
        arc: ArcModel,
        steps: List[ArcStepModel],
        session_data: List[Dict[str, Any]] = None,
        existing_milestones: List[ProgressMilestone] = None
    ) -> ProgressionMetrics:
        """
        Calculate comprehensive progression metrics for an arc.
        
        Args:
            arc: The arc to analyze
            steps: All steps for the arc
            session_data: Player session data
            existing_milestones: Previously achieved milestones
            
        Returns:
            Comprehensive progression metrics
        """
        # Basic progress calculations
        completed_steps = len([s for s in steps if s.status == ArcStepStatus.COMPLETED.value])
        total_steps = len(steps)
        completion_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        # Time metrics
        elapsed_time_hours = self._calculate_elapsed_time(arc, session_data)
        velocity = self._calculate_velocity(steps, session_data)
        estimated_remaining = self._estimate_remaining_time(
            arc, steps, completion_percentage, velocity
        )
        
        # Quality metrics
        avg_step_time = self._calculate_average_step_completion_time(steps, session_data)
        first_try_count, retry_count = self._analyze_step_completion_quality(steps, session_data)
        
        # Engagement metrics
        session_count, last_activity, longest_break = self._analyze_engagement_patterns(
            session_data or []
        )
        
        # Milestone tracking
        current_milestones = existing_milestones or []
        new_milestones = self._check_for_new_milestones(
            arc, current_milestones, {
                'completion_percentage': completion_percentage,
                'completed_steps': completed_steps,
                'total_steps': total_steps,
                'elapsed_time_hours': elapsed_time_hours,
                'estimated_remaining_hours': estimated_remaining,
                'steps_requiring_retries': retry_count
            }
        )
        
        # Predictive analytics
        projected_completion = self._project_completion_date(
            arc, completion_percentage, velocity, estimated_remaining
        )
        confidence_score, risk_factors = self._assess_completion_risk(
            arc, steps, session_data, completion_percentage, velocity
        )
        
        return ProgressionMetrics(
            arc_id=arc.id,
            completion_percentage=completion_percentage,
            completed_steps=completed_steps,
            total_steps=total_steps,
            elapsed_time_hours=elapsed_time_hours,
            estimated_remaining_hours=estimated_remaining,
            velocity_steps_per_hour=velocity,
            average_step_completion_time=avg_step_time,
            steps_completed_on_first_try=first_try_count,
            steps_requiring_retries=retry_count,
            active_sessions=session_count,
            last_activity=last_activity or datetime.utcnow(),
            longest_break_hours=longest_break,
            milestones_achieved=current_milestones + new_milestones,
            next_milestone=self._get_next_milestone(completion_percentage, current_milestones),
            projected_completion_date=projected_completion,
            completion_confidence=confidence_score,
            risk_factors=risk_factors
        )
    
    def _calculate_elapsed_time(
        self,
        arc: ArcModel,
        session_data: List[Dict[str, Any]] = None
    ) -> float:
        """Calculate total elapsed time for an arc."""
        if not arc.start_date:
            return 0.0
        
        end_time = arc.end_date or datetime.utcnow()
        total_hours = (end_time - arc.start_date).total_seconds() / 3600
        
        # If we have session data, use actual play time
        if session_data:
            actual_play_time = sum(
                session.get('duration_hours', 0) for session in session_data
            )
            return actual_play_time
        
        return total_hours
    
    def _calculate_velocity(
        self,
        steps: List[ArcStepModel],
        session_data: List[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Calculate steps completion velocity (steps per hour)."""
        completed_steps = [s for s in steps if s.status == ArcStepStatus.COMPLETED.value]
        
        if not completed_steps or not session_data:
            return None
        
        # Calculate time spent on completed steps
        total_time_hours = 0
        for step in completed_steps:
            # Find sessions that worked on this step
            step_sessions = [
                s for s in session_data 
                if step.id in s.get('steps_worked_on', [])
            ]
            step_time = sum(s.get('duration_hours', 0) for s in step_sessions)
            total_time_hours += step_time
        
        if total_time_hours == 0:
            return None
        
        return len(completed_steps) / total_time_hours
    
    def _estimate_remaining_time(
        self,
        arc: ArcModel,
        steps: List[ArcStepModel],
        completion_percentage: float,
        velocity: Optional[float]
    ) -> Optional[float]:
        """Estimate remaining time to complete the arc."""
        remaining_steps = len([s for s in steps if s.status == ArcStepStatus.PENDING.value])
        
        if completion_percentage >= 100:
            return 0.0
        
        # Use velocity if available
        if velocity and velocity > 0:
            return remaining_steps / velocity
        
        # Fallback to original estimate adjusted by progress
        if arc.estimated_duration_hours:
            progress_ratio = completion_percentage / 100
            elapsed_estimate = arc.estimated_duration_hours * progress_ratio
            return arc.estimated_duration_hours - elapsed_estimate
        
        # Last resort: estimate based on step complexity
        complexity_score, _ = calculate_arc_complexity_score(arc.dict())
        estimated_hours_per_step = max(0.5, complexity_score / 20)  # 0.5-5 hours per step
        return remaining_steps * estimated_hours_per_step
    
    def _calculate_average_step_completion_time(
        self,
        steps: List[ArcStepModel],
        session_data: List[Dict[str, Any]] = None
    ) -> Optional[float]:
        """Calculate average time to complete a step."""
        completed_steps = [s for s in steps if s.status == ArcStepStatus.COMPLETED.value]
        
        if not completed_steps or not session_data:
            return None
        
        completion_times = []
        for step in completed_steps:
            # Find sessions for this step
            step_sessions = [
                s for s in session_data 
                if step.id in s.get('steps_worked_on', [])
            ]
            if step_sessions:
                total_time = sum(s.get('duration_hours', 0) for s in step_sessions)
                completion_times.append(total_time)
        
        return statistics.mean(completion_times) if completion_times else None
    
    def _analyze_step_completion_quality(
        self,
        steps: List[ArcStepModel],
        session_data: List[Dict[str, Any]] = None
    ) -> Tuple[int, int]:
        """Analyze step completion quality (first try vs retries)."""
        completed_steps = [s for s in steps if s.status == ArcStepStatus.COMPLETED.value]
        
        first_try_count = 0
        retry_count = 0
        
        for step in completed_steps:
            if session_data:
                # Count how many sessions worked on this step
                step_sessions = [
                    s for s in session_data 
                    if step.id in s.get('steps_worked_on', [])
                ]
                
                # Check for failure indicators in session data
                had_failures = any(
                    'step_failed' in s.get('events', []) and step.id in s.get('failed_steps', [])
                    for s in step_sessions
                )
                
                if had_failures:
                    retry_count += 1
                else:
                    first_try_count += 1
            else:
                # Without session data, assume first try
                first_try_count += 1
        
        return first_try_count, retry_count
    
    def _analyze_engagement_patterns(
        self,
        session_data: List[Dict[str, Any]]
    ) -> Tuple[int, Optional[datetime], Optional[float]]:
        """Analyze player engagement patterns."""
        if not session_data:
            return 0, None, None
        
        session_count = len(session_data)
        
        # Find last activity
        last_activity = None
        if session_data:
            last_session = max(
                session_data, 
                key=lambda s: s.get('end_time', datetime.min),
                default=None
            )
            if last_session:
                last_activity = last_session.get('end_time')
        
        # Calculate longest break between sessions
        longest_break = None
        if len(session_data) > 1:
            # Sort sessions by start time
            sorted_sessions = sorted(
                session_data, 
                key=lambda s: s.get('start_time', datetime.min)
            )
            
            breaks = []
            for i in range(1, len(sorted_sessions)):
                prev_end = sorted_sessions[i-1].get('end_time')
                current_start = sorted_sessions[i].get('start_time')
                
                if prev_end and current_start and current_start > prev_end:
                    break_duration = (current_start - prev_end).total_seconds() / 3600
                    breaks.append(break_duration)
            
            longest_break = max(breaks) if breaks else None
        
        return session_count, last_activity, longest_break
    
    def _check_for_new_milestones(
        self,
        arc: ArcModel,
        existing_milestones: List[ProgressMilestone],
        metrics: Dict[str, Any]
    ) -> List[ProgressMilestone]:
        """Check for newly achieved milestones."""
        new_milestones = []
        achieved_milestone_types = {m.milestone_type for m in existing_milestones}
        
        for milestone_type, definition in self.milestone_definitions.items():
            if (milestone_type not in achieved_milestone_types and
                definition["criteria"](type('Metrics', (), metrics)())):
                
                milestone = ProgressMilestone(
                    milestone_id=f"{arc.id}_{milestone_type}_{int(datetime.utcnow().timestamp())}",
                    arc_id=arc.id,
                    milestone_type=milestone_type,
                    achieved_at=datetime.utcnow(),
                    description=definition["description"],
                    metadata={
                        "significance": definition["significance"],
                        "arc_title": arc.title,
                        "completion_percentage": metrics["completion_percentage"],
                        "completed_steps": metrics["completed_steps"]
                    }
                )
                new_milestones.append(milestone)
        
        return new_milestones
    
    def _get_next_milestone(
        self,
        completion_percentage: float,
        existing_milestones: List[ProgressMilestone]
    ) -> Optional[str]:
        """Determine the next milestone to achieve."""
        achieved_types = {m.milestone_type for m in existing_milestones}
        
        # Standard progression milestones
        if completion_percentage < 25 and "quarter_complete" not in achieved_types:
            return "quarter_complete"
        elif completion_percentage < 50 and "half_complete" not in achieved_types:
            return "half_complete"
        elif completion_percentage < 75 and "three_quarters" not in achieved_types:
            return "three_quarters"
        elif completion_percentage < 90 and "final_stretch" not in achieved_types:
            return "final_stretch"
        elif completion_percentage < 100:
            return "completion"
        
        return None
    
    def _project_completion_date(
        self,
        arc: ArcModel,
        completion_percentage: float,
        velocity: Optional[float],
        estimated_remaining_hours: Optional[float]
    ) -> Optional[datetime]:
        """Project when the arc will be completed."""
        if completion_percentage >= 100:
            return arc.end_date
        
        if not estimated_remaining_hours:
            return None
        
        # Assume reasonable play schedule (8 hours per week)
        hours_per_week = 8
        weeks_remaining = estimated_remaining_hours / hours_per_week
        
        return datetime.utcnow() + timedelta(weeks=weeks_remaining)
    
    def _assess_completion_risk(
        self,
        arc: ArcModel,
        steps: List[ArcStepModel],
        session_data: List[Dict[str, Any]] = None,
        completion_percentage: float = 0,
        velocity: Optional[float] = None
    ) -> Tuple[float, List[str]]:
        """Assess risk factors that might prevent completion."""
        risk_factors = []
        risk_score = 1.0  # Start with high confidence
        
        # Check for stalled progress
        if session_data:
            last_session = max(
                session_data,
                key=lambda s: s.get('end_time', datetime.min),
                default=None
            )
            if last_session:
                days_since_last = (datetime.utcnow() - last_session.get('end_time', datetime.utcnow())).days
                if days_since_last > 14:
                    risk_factors.append(f"No activity for {days_since_last} days")
                    risk_score *= 0.7
                elif days_since_last > 7:
                    risk_factors.append(f"Reduced activity ({days_since_last} days)")
                    risk_score *= 0.9
        
        # Check velocity trends
        if velocity is not None and velocity < 0.1:  # Very slow progress
            risk_factors.append("Low completion velocity")
            risk_score *= 0.8
        
        # Check for blocked steps
        blocked_steps = [s for s in steps if s.status == ArcStepStatus.BLOCKED.value]
        if blocked_steps:
            risk_factors.append(f"{len(blocked_steps)} blocked steps")
            risk_score *= 0.85
        
        # Check for failed steps
        failed_steps = [s for s in steps if s.status == ArcStepStatus.FAILED.value]
        if failed_steps:
            risk_factors.append(f"{len(failed_steps)} failed steps")
            risk_score *= 0.9
        
        # Check arc complexity vs progress
        complexity_score, _ = calculate_arc_complexity_score(arc.dict())
        if complexity_score > 70 and completion_percentage < 30:
            risk_factors.append("High complexity arc with low progress")
            risk_score *= 0.8
        
        # Check for overdue estimated completion
        if arc.estimated_duration_hours and arc.start_date:
            estimated_completion = arc.start_date + timedelta(hours=arc.estimated_duration_hours)
            if datetime.utcnow() > estimated_completion and completion_percentage < 100:
                risk_factors.append("Past estimated completion date")
                risk_score *= 0.7
        
        # Check for prerequisite issues
        pending_steps = [s for s in steps if s.status == ArcStepStatus.PENDING.value]
        for step in pending_steps:
            if step.prerequisites:
                # Check if prerequisites are met
                prereq_steps = [s for s in steps if s.id in step.prerequisites]
                unmet_prereqs = [s for s in prereq_steps if s.status != ArcStepStatus.COMPLETED.value]
                if unmet_prereqs:
                    risk_factors.append("Unmet step prerequisites")
                    risk_score *= 0.95
                    break
        
        return max(0.0, min(1.0, risk_score)), risk_factors
    
    def generate_progress_insights(
        self,
        metrics: ProgressionMetrics,
        arc: ArcModel
    ) -> Dict[str, Any]:
        """Generate actionable insights from progression metrics."""
        insights = {
            "summary": self._generate_progress_summary(metrics, arc),
            "recommendations": self._generate_recommendations(metrics, arc),
            "achievements": self._format_achievements(metrics.milestones_achieved),
            "predictions": self._generate_predictions(metrics),
            "alerts": self._generate_alerts(metrics)
        }
        
        return insights
    
    def _generate_progress_summary(
        self,
        metrics: ProgressionMetrics,
        arc: ArcModel
    ) -> str:
        """Generate a human-readable progress summary."""
        if metrics.completion_percentage >= 100:
            return f"🎉 Arc '{arc.title}' completed! Well done!"
        
        progress_desc = f"Arc '{arc.title}' is {metrics.completion_percentage:.1f}% complete"
        
        if metrics.velocity_steps_per_hour:
            rate_desc = f" (completing ~{metrics.velocity_steps_per_hour:.1f} steps/hour)"
        else:
            rate_desc = ""
        
        remaining_desc = ""
        if metrics.estimated_remaining_hours:
            if metrics.estimated_remaining_hours < 2:
                remaining_desc = " - almost finished!"
            elif metrics.estimated_remaining_hours < 8:
                remaining_desc = f" - about {metrics.estimated_remaining_hours:.1f} hours remaining"
            else:
                days = metrics.estimated_remaining_hours / 8  # Assume 8 hours per day
                remaining_desc = f" - about {days:.1f} days remaining"
        
        return progress_desc + rate_desc + remaining_desc
    
    def _generate_recommendations(
        self,
        metrics: ProgressionMetrics,
        arc: ArcModel
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Activity-based recommendations
        if metrics.longest_break_hours and metrics.longest_break_hours > 72:  # 3+ days
            recommendations.append("Consider setting aside regular time for this arc to maintain momentum")
        
        # Progress-based recommendations
        if metrics.completion_percentage > 75:
            recommendations.append("You're in the final stretch! Push through to completion")
        elif metrics.completion_percentage > 50:
            recommendations.append("Great progress! You're past the halfway point")
        elif metrics.completion_percentage < 25 and metrics.elapsed_time_hours > 10:
            recommendations.append("Consider breaking down remaining steps into smaller tasks")
        
        # Velocity-based recommendations
        if metrics.velocity_steps_per_hour and metrics.velocity_steps_per_hour < 0.2:
            recommendations.append("Progress seems slow - consider if you need help or resources")
        
        # Risk-based recommendations
        if metrics.completion_confidence < 0.7:
            recommendations.append("This arc may be at risk - consider reviewing the plan or seeking assistance")
        
        if "blocked" in [rf.lower() for rf in metrics.risk_factors]:
            recommendations.append("Address blocked steps to continue progress")
        
        return recommendations
    
    def _format_achievements(
        self,
        milestones: List[ProgressMilestone]
    ) -> List[Dict[str, Any]]:
        """Format milestones as achievements."""
        return [
            {
                "title": milestone.description,
                "achieved_at": milestone.achieved_at.isoformat(),
                "significance": milestone.metadata.get("significance", "medium"),
                "type": milestone.milestone_type
            }
            for milestone in sorted(milestones, key=lambda m: m.achieved_at, reverse=True)
        ]
    
    def _generate_predictions(
        self,
        metrics: ProgressionMetrics
    ) -> Dict[str, Any]:
        """Generate predictions about arc completion."""
        predictions = {}
        
        if metrics.projected_completion_date:
            predictions["completion_date"] = metrics.projected_completion_date.isoformat()
            days_to_completion = (metrics.projected_completion_date - datetime.utcnow()).days
            predictions["days_remaining"] = max(0, days_to_completion)
        
        predictions["confidence_level"] = metrics.completion_confidence
        predictions["confidence_description"] = (
            "high" if metrics.completion_confidence > 0.8 else
            "medium" if metrics.completion_confidence > 0.6 else
            "low"
        )
        
        return predictions
    
    def _generate_alerts(
        self,
        metrics: ProgressionMetrics
    ) -> List[Dict[str, Any]]:
        """Generate alerts for issues requiring attention."""
        alerts = []
        
        # High-risk completion
        if metrics.completion_confidence < 0.5:
            alerts.append({
                "type": "warning",
                "message": "Arc completion at risk",
                "details": f"Risk factors: {', '.join(metrics.risk_factors)}"
            })
        
        # Long inactivity
        if metrics.longest_break_hours and metrics.longest_break_hours > 168:  # 1 week
            alerts.append({
                "type": "info",
                "message": "Extended break detected",
                "details": f"Longest break: {metrics.longest_break_hours:.1f} hours"
            })
        
        # Velocity concerns
        if metrics.velocity_steps_per_hour and metrics.velocity_steps_per_hour < 0.1:
            alerts.append({
                "type": "warning",
                "message": "Very slow progress",
                "details": f"Current velocity: {metrics.velocity_steps_per_hour:.2f} steps/hour"
            })
        
        return alerts
