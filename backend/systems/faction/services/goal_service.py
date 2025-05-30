"""
Goal service for factions in the Visual DM system.

This module handles the creation, updating, and management of faction goals,
which drive faction behavior and narrative.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.systems.faction.models.faction import Faction
from backend.systems.faction.models.faction_goal import FactionGoal
from backend.systems.faction.services.faction_service import FactionNotFoundError


class GoalNotFoundError(Exception):
    """Raised when a goal cannot be found."""
    pass


class GoalDependencyError(Exception):
    """Raised when there is an issue with goal dependencies."""
    pass


class FactionGoalService:
    """Service for managing faction goals."""
    
    @staticmethod
    def create_goal(
        db: Session,
        faction_id: int,
        title: str,
        description: str,
        goal_type: str,
        priority: int = 5,
        completion_criteria: Optional[Dict[str, Any]] = None,
        rewards: Optional[Dict[str, Any]] = None,
        failure_criteria: Optional[Dict[str, Any]] = None,
        penalties: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[int]] = None,
        targets: Optional[Dict[str, Any]] = None,
        steps: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FactionGoal:
        """
        Create a new goal for a faction.
        
        Args:
            db: Database session
            faction_id: ID of the faction this goal belongs to
            title: Title of the goal
            description: Detailed description of the goal
            goal_type: Type of goal (conquest, economic, political, etc.)
            priority: How important this goal is (1-10, higher = more important)
            completion_criteria: Criteria for determining when the goal is complete
            rewards: Benefits gained upon completion
            failure_criteria: Conditions that cause the goal to fail
            penalties: Negative consequences on failure
            dependencies: IDs of other goals that must be completed first
            targets: Specific entities targeted by this goal (faction, region, etc.)
            steps: List of steps required to achieve the goal
            metadata: Additional data for the goal
            
        Returns:
            The newly created FactionGoal
            
        Raises:
            FactionNotFoundError: If the faction doesn't exist
            GoalDependencyError: If a dependency doesn't exist
        """
        # Verify faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Validate dependencies (if any)
        if dependencies:
            for dep_id in dependencies:
                dependency = db.query(FactionGoal).filter(FactionGoal.id == dep_id).first()
                if not dependency:
                    raise GoalDependencyError(f"Dependency goal with ID {dep_id} not found")
                    
        # Create new goal
        goal = FactionGoal(
            faction_id=faction_id,
            title=title,
            description=description,
            type=goal_type,
            priority=priority,
            completion_criteria=completion_criteria or {},
            rewards=rewards or {},
            failure_criteria=failure_criteria or {},
            penalties=penalties or {},
            dependencies=dependencies or [],
            targets=targets or {},
            steps=steps or [],
            metadata=metadata or {},
            history=[{
                "timestamp": datetime.utcnow().isoformat(),
                "event": "created",
                "details": "Goal created"
            }]
        )
        
        db.add(goal)
        db.commit()
        db.refresh(goal)
        
        # Update faction state to track active goals
        if "active_goals" not in faction.state:
            faction.state["active_goals"] = []
            
        faction.state["active_goals"].append(goal.id)
        db.commit()
        
        return goal
    
    @staticmethod
    def update_goal_progress(
        db: Session,
        goal_id: int,
        progress: float,
        note: str = None,
        check_completion: bool = True
    ) -> Dict[str, Any]:
        """
        Update a goal's progress toward completion.
        
        Args:
            db: Database session
            goal_id: ID of the goal to update
            progress: New progress value (0-100)
            note: Optional note about this progress update
            check_completion: Whether to check if the goal is now complete
            
        Returns:
            Dict with updated goal details
            
        Raises:
            GoalNotFoundError: If the goal doesn't exist
        """
        goal = db.query(FactionGoal).filter(FactionGoal.id == goal_id).first()
        if not goal:
            raise GoalNotFoundError(f"Goal with ID {goal_id} not found")
            
        # Can't update completed, failed, or abandoned goals
        if goal.status not in ["active", "in_progress"]:
            return {
                "goal_id": goal_id,
                "success": False,
                "message": f"Cannot update progress for goal with status '{goal.status}'"
            }
            
        previous_progress = goal.progress
        
        # Update progress (capped at 0-100)
        goal.progress = max(0.0, min(100.0, progress))
        
        # Add to history
        goal.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": "progress_update",
            "previous_progress": previous_progress,
            "new_progress": goal.progress,
            "note": note or "Progress updated"
        })
        
        # If not in progress yet, set to in_progress
        if goal.status == "active" and goal.progress > 0:
            goal.status = "in_progress"
            goal.history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event": "status_change",
                "previous_status": "active",
                "new_status": "in_progress"
            })
        
        # Check for completion if requested
        completion_result = None
        if check_completion and goal.progress >= 100:
            completion_result = FactionGoalService.complete_goal(db, goal_id)
        
        db.commit()
        
        return {
            "goal_id": goal_id,
            "previous_progress": previous_progress,
            "current_progress": goal.progress,
            "status": goal.status,
            "success": True,
            "completion_result": completion_result
        }
    
    @staticmethod
    def complete_goal(
        db: Session,
        goal_id: int,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Mark a goal as completed and apply rewards.
        
        Args:
            db: Database session
            goal_id: ID of the goal to complete
            force: Whether to force completion regardless of progress
            
        Returns:
            Dict with completion details
            
        Raises:
            GoalNotFoundError: If the goal doesn't exist
        """
        goal = db.query(FactionGoal).filter(FactionGoal.id == goal_id).first()
        if not goal:
            raise GoalNotFoundError(f"Goal with ID {goal_id} not found")
            
        # Can't complete already completed, failed, or abandoned goals
        if goal.status in ["completed", "failed", "abandoned"]:
            return {
                "goal_id": goal_id,
                "success": False,
                "message": f"Cannot complete goal with status '{goal.status}'"
            }
            
        # Check if goal has enough progress (unless forced)
        if not force and goal.progress < 100:
            return {
                "goal_id": goal_id,
                "success": False,
                "message": f"Goal has not reached 100% progress (current: {goal.progress}%)"
            }
        
        # Update goal status
        previous_status = goal.status
        goal.status = "completed"
        goal.completed_at = datetime.utcnow()
        goal.progress = 100  # Ensure progress is at 100%
        
        # Add to history
        goal.history.append({
            "timestamp": goal.completed_at.isoformat(),
            "event": "completed",
            "previous_status": previous_status,
            "forced": force
        })
        
        # Get the faction
        faction = db.query(Faction).filter(Faction.id == goal.faction_id).first()
        
        # Apply rewards (simplified implementation)
        applied_rewards = []
        rewards = goal.rewards
        
        if rewards:
            # Handle resources
            if "resources" in rewards:
                for resource, amount in rewards["resources"].items():
                    if resource in faction.resources:
                        faction.resources[resource] += amount
                    else:
                        faction.resources[resource] = amount
                        
                    applied_rewards.append({
                        "type": "resource",
                        "resource": resource,
                        "amount": amount
                    })
            
            # Handle influence gain
            if "influence" in rewards:
                influence_gain = rewards["influence"]
                previous_influence = faction.influence
                faction.influence = min(100, faction.influence + influence_gain)
                
                applied_rewards.append({
                    "type": "influence",
                    "previous": previous_influence,
                    "gain": influence_gain,
                    "new": faction.influence
                })
        
        # Update faction state
        if "active_goals" in faction.state and goal_id in faction.state["active_goals"]:
            faction.state["active_goals"].remove(goal_id)
            
        if "completed_goals" not in faction.state:
            faction.state["completed_goals"] = []
            
        faction.state["completed_goals"].append(goal_id)
        
        # Record completion in faction history
        if "goal_history" not in faction.state:
            faction.state["goal_history"] = []
            
        faction.state["goal_history"].append({
            "timestamp": goal.completed_at.isoformat(),
            "goal_id": goal_id,
            "title": goal.title,
            "status": "completed",
            "rewards_applied": applied_rewards
        })
        
        db.commit()
        
        return {
            "goal_id": goal_id,
            "title": goal.title,
            "success": True,
            "status": "completed",
            "completed_at": goal.completed_at.isoformat(),
            "rewards_applied": applied_rewards
        }
    
    @staticmethod
    def fail_goal(
        db: Session,
        goal_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """
        Mark a goal as failed and apply penalties.
        
        Args:
            db: Database session
            goal_id: ID of the goal to fail
            reason: Reason for the failure
            
        Returns:
            Dict with failure details
            
        Raises:
            GoalNotFoundError: If the goal doesn't exist
        """
        goal = db.query(FactionGoal).filter(FactionGoal.id == goal_id).first()
        if not goal:
            raise GoalNotFoundError(f"Goal with ID {goal_id} not found")
            
        # Can't fail already completed, failed, or abandoned goals
        if goal.status in ["completed", "failed", "abandoned"]:
            return {
                "goal_id": goal_id,
                "success": False,
                "message": f"Cannot fail goal with status '{goal.status}'"
            }
        
        # Update goal status
        previous_status = goal.status
        goal.status = "failed"
        goal.failed_at = datetime.utcnow()
        
        # Add to history
        goal.history.append({
            "timestamp": goal.failed_at.isoformat(),
            "event": "failed",
            "previous_status": previous_status,
            "reason": reason
        })
        
        # Get the faction
        faction = db.query(Faction).filter(Faction.id == goal.faction_id).first()
        
        # Apply penalties (simplified implementation)
        applied_penalties = []
        penalties = goal.penalties
        
        if penalties:
            # Handle resource losses
            if "resources" in penalties:
                for resource, amount in penalties["resources"].items():
                    if resource in faction.resources:
                        faction.resources[resource] = max(0, faction.resources[resource] - amount)
                        
                        applied_penalties.append({
                            "type": "resource_loss",
                            "resource": resource,
                            "amount": amount,
                            "remaining": faction.resources[resource]
                        })
            
            # Handle influence loss
            if "influence" in penalties:
                influence_loss = penalties["influence"]
                previous_influence = faction.influence
                faction.influence = max(0, faction.influence - influence_loss)
                
                applied_penalties.append({
                    "type": "influence_loss",
                    "previous": previous_influence,
                    "loss": influence_loss,
                    "new": faction.influence
                })
        
        # Update faction state
        if "active_goals" in faction.state and goal_id in faction.state["active_goals"]:
            faction.state["active_goals"].remove(goal_id)
            
        if "failed_goals" not in faction.state:
            faction.state["failed_goals"] = []
            
        faction.state["failed_goals"].append(goal_id)
        
        db.commit()
        
        return {
            "goal_id": goal_id,
            "title": goal.title,
            "success": True,
            "status": "failed",
            "reason": reason,
            "failed_at": goal.failed_at.isoformat(),
            "penalties_applied": applied_penalties
        }
    
    @staticmethod
    def get_faction_goals(
        db: Session,
        faction_id: int,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all goals for a faction, optionally filtered by status.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            status: Optional status filter (active, in_progress, completed, failed, abandoned)
            
        Returns:
            List of goals as dictionaries
            
        Raises:
            FactionNotFoundError: If the faction doesn't exist
        """
        # Verify faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction with ID {faction_id} not found")
            
        # Query goals
        query = db.query(FactionGoal).filter(FactionGoal.faction_id == faction_id)
        
        if status:
            query = query.filter(FactionGoal.status == status)
            
        goals = query.all()
        
        return [goal.to_dict() for goal in goals] 