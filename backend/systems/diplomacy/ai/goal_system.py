"""
Diplomatic Goal System

This module defines and manages faction goals for AI-driven diplomatic decision-making.
Goals drive faction behavior and strategic decisions in the diplomatic landscape.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import random
import logging

logger = logging.getLogger(__name__)

class DiplomaticGoalType(Enum):
    """Types of diplomatic goals that factions can pursue"""
    
    # Core Strategic Goals
    EXPANSION = "expansion"              # Territorial/influence expansion
    SECURITY = "security"               # Defense and protection
    PROSPERITY = "prosperity"           # Economic growth and trade
    DOMINANCE = "dominance"             # Regional or global control
    
    # Relationship Goals  
    ISOLATION = "isolation"             # Minimize external entanglements
    ALLIANCE_BUILDING = "alliance_building"  # Form strategic partnerships
    NEUTRALITY = "neutrality"           # Maintain balanced relationships
    
    # Reactive Goals
    REVENGE = "revenge"                 # Retaliation against enemies
    SURVIVAL = "survival"               # Emergency defensive mode
    RECOVERY = "recovery"               # Rebuild after setbacks
    
    # Ideological Goals
    HONOR = "honor"                     # Maintain reputation and dignity
    JUSTICE = "justice"                 # Right wrongs and uphold principles
    CHAOS = "chaos"                     # Disrupt existing order

class GoalPriority(Enum):
    """Priority levels for faction goals"""
    
    CRITICAL = 100      # Life-or-death, overrides all else
    ESSENTIAL = 80      # Core strategic importance
    IMPORTANT = 60      # Significant but not vital
    MODERATE = 40       # Worthwhile pursuit
    MINOR = 20          # Nice to have
    NEGLIGIBLE = 5      # Barely considered

@dataclass
class FactionGoal:
    """Represents a specific goal for a faction"""
    
    id: UUID = field(default_factory=uuid4)
    faction_id: UUID = field(default=None)
    goal_type: DiplomaticGoalType = field(default=None)
    priority: GoalPriority = field(default=GoalPriority.MODERATE)
    
    # Goal details
    description: str = field(default="")
    target_faction_id: Optional[UUID] = field(default=None)  # For targeted goals like revenge
    target_region: Optional[str] = field(default=None)      # For territorial goals
    
    # Goal state
    progress: float = field(default=0.0)    # 0.0 to 1.0
    is_active: bool = field(default=True)
    is_achievable: bool = field(default=True)
    
    # Temporal aspects
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = field(default=None)
    last_evaluated: datetime = field(default_factory=datetime.utcnow)
    
    # Goal parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Success/failure tracking
    attempts_made: int = field(default=0)
    success_probability: float = field(default=0.5)
    
    def __post_init__(self):
        """Initialize goal parameters based on type"""
        if not self.parameters:
            self.parameters = self._get_default_parameters()
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for this goal type"""
        defaults = {
            DiplomaticGoalType.EXPANSION: {
                "expansion_rate": 0.1,
                "acceptable_risk": 0.3,
                "min_strength_ratio": 1.5
            },
            DiplomaticGoalType.SECURITY: {
                "threat_tolerance": 0.2,
                "alliance_preference": 0.7,
                "defensive_posture": 0.8
            },
            DiplomaticGoalType.PROSPERITY: {
                "trade_focus": 0.8,
                "economic_growth_target": 0.15,
                "resource_priority": ["gold", "food", "goods"]
            },
            DiplomaticGoalType.DOMINANCE: {
                "aggression_level": 0.6,
                "coalition_breaking": 0.7,
                "influence_expansion": 0.9
            },
            DiplomaticGoalType.ALLIANCE_BUILDING: {
                "min_partners": 2,
                "max_partners": 4,
                "trust_threshold": 0.6
            },
            DiplomaticGoalType.REVENGE: {
                "patience_level": 0.3,
                "escalation_willingness": 0.8,
                "proportional_response": 0.5
            }
        }
        
        return defaults.get(self.goal_type, {})
    
    def update_progress(self, new_progress: float) -> None:
        """Update goal progress and track changes"""
        old_progress = self.progress
        self.progress = max(0.0, min(1.0, new_progress))
        self.last_evaluated = datetime.utcnow()
        
        if self.progress >= 1.0:
            self.is_active = False
            logger.info(f"Goal {self.goal_type.value} for faction {self.faction_id} completed")
    
    def is_expired(self) -> bool:
        """Check if goal has expired"""
        if self.deadline:
            return datetime.utcnow() > self.deadline
        return False
    
    def calculate_urgency(self) -> float:
        """Calculate how urgent this goal is (0.0 to 1.0)"""
        urgency = self.priority.value / 100.0
        
        # Increase urgency if deadline is approaching
        if self.deadline:
            time_remaining = (self.deadline - datetime.utcnow()).total_seconds()
            if time_remaining > 0:
                # More urgent as deadline approaches
                urgency *= min(2.0, 86400.0 / time_remaining)  # 1 day = normal urgency
        
        # Increase urgency for low progress goals that are important
        if self.priority.value >= GoalPriority.IMPORTANT.value and self.progress < 0.3:
            urgency *= 1.5
        
        return min(1.0, urgency)

@dataclass 
class GoalEvolutionRule:
    """Rules for how goals change over time based on circumstances"""
    
    trigger_condition: str  # Condition that triggers evolution
    goal_type: DiplomaticGoalType
    evolution_type: str     # "priority_change", "new_goal", "goal_completion", "goal_abandonment"
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Examples of trigger conditions:
    # "faction_attacked" -> priority boost for SECURITY
    # "alliance_broken" -> new REVENGE goal
    # "territory_lost" -> new RECOVERY goal
    # "economic_crisis" -> priority boost for PROSPERITY

class FactionGoalManager:
    """Manages goals for all factions in the diplomatic system"""
    
    def __init__(self):
        self.faction_goals: Dict[UUID, List[FactionGoal]] = {}
        self.evolution_rules: List[GoalEvolutionRule] = []
        self._setup_default_evolution_rules()
    
    def _setup_default_evolution_rules(self) -> None:
        """Set up default goal evolution rules"""
        self.evolution_rules = [
            # Security escalation rules
            GoalEvolutionRule(
                trigger_condition="faction_attacked",
                goal_type=DiplomaticGoalType.SECURITY,
                evolution_type="priority_boost",
                parameters={"priority_increase": 20, "duration_days": 30}
            ),
            GoalEvolutionRule(
                trigger_condition="territory_lost",
                goal_type=DiplomaticGoalType.RECOVERY,
                evolution_type="new_goal",
                parameters={"priority": GoalPriority.ESSENTIAL, "deadline_days": 90}
            ),
            
            # Revenge rules
            GoalEvolutionRule(
                trigger_condition="treaty_betrayed",
                goal_type=DiplomaticGoalType.REVENGE,
                evolution_type="new_goal",
                parameters={"priority": GoalPriority.IMPORTANT, "deadline_days": 365}
            ),
            GoalEvolutionRule(
                trigger_condition="ally_abandoned",
                goal_type=DiplomaticGoalType.REVENGE,
                evolution_type="new_goal",
                parameters={"priority": GoalPriority.MODERATE, "deadline_days": 180}
            ),
            
            # Economic rules
            GoalEvolutionRule(
                trigger_condition="economic_crisis",
                goal_type=DiplomaticGoalType.PROSPERITY,
                evolution_type="priority_boost",
                parameters={"priority_increase": 30, "duration_days": 60}
            ),
            
            # Expansion rules
            GoalEvolutionRule(
                trigger_condition="military_victory",
                goal_type=DiplomaticGoalType.EXPANSION,
                evolution_type="priority_boost",
                parameters={"priority_increase": 15, "duration_days": 45}
            ),
            
            # Survival rules
            GoalEvolutionRule(
                trigger_condition="existential_threat",
                goal_type=DiplomaticGoalType.SURVIVAL,
                evolution_type="override_all",
                parameters={"priority": GoalPriority.CRITICAL, "suspend_other_goals": True}
            )
        ]
    
    def initialize_faction_goals(self, faction_id: UUID, faction_attributes: Dict[str, int]) -> None:
        """Initialize default goals for a new faction based on personality"""
        if faction_id in self.faction_goals:
            return  # Already initialized
        
        goals = []
        
        # Base goals influenced by personality attributes
        ambition = faction_attributes.get("hidden_ambition", 3)
        integrity = faction_attributes.get("hidden_integrity", 3)
        discipline = faction_attributes.get("hidden_discipline", 3)
        pragmatism = faction_attributes.get("hidden_pragmatism", 3)
        
        # Security goal (everyone needs basic security)
        security_priority = self._calculate_priority_from_attributes(
            base_value=60, 
            modifiers={"hidden_discipline": 5, "hidden_pragmatism": 3}
        )
        goals.append(FactionGoal(
            faction_id=faction_id,
            goal_type=DiplomaticGoalType.SECURITY,
            priority=GoalPriority(security_priority),
            description="Maintain faction security and territorial integrity"
        ))
        
        # Prosperity goal (economic development)
        prosperity_priority = self._calculate_priority_from_attributes(
            base_value=50,
            modifiers={"hidden_pragmatism": 8, "hidden_discipline": 4}
        )
        goals.append(FactionGoal(
            faction_id=faction_id,
            goal_type=DiplomaticGoalType.PROSPERITY,
            priority=GoalPriority(prosperity_priority),
            description="Develop economic strength and trade relationships"
        ))
        
        # Expansion goal (for ambitious factions)
        if ambition >= 4:
            expansion_priority = self._calculate_priority_from_attributes(
                base_value=30,
                modifiers={"hidden_ambition": 10, "hidden_discipline": 3}
            )
            goals.append(FactionGoal(
                faction_id=faction_id,
                goal_type=DiplomaticGoalType.EXPANSION,
                priority=GoalPriority(expansion_priority),
                description="Expand territorial control and regional influence"
            ))
        
        # Alliance building (for pragmatic factions)
        if pragmatism >= 4 or integrity >= 5:
            alliance_priority = self._calculate_priority_from_attributes(
                base_value=40,
                modifiers={"hidden_pragmatism": 6, "hidden_integrity": 4}
            )
            goals.append(FactionGoal(
                faction_id=faction_id,
                goal_type=DiplomaticGoalType.ALLIANCE_BUILDING,
                priority=GoalPriority(alliance_priority),
                description="Form strategic alliances and partnerships"
            ))
        
        # Honor goal (for high-integrity factions)
        if integrity >= 5:
            honor_priority = self._calculate_priority_from_attributes(
                base_value=35,
                modifiers={"hidden_integrity": 8}
            )
            goals.append(FactionGoal(
                faction_id=faction_id,
                goal_type=DiplomaticGoalType.HONOR,
                priority=GoalPriority(honor_priority),
                description="Maintain honor and reputation in all dealings"
            ))
        
        self.faction_goals[faction_id] = goals
        logger.info(f"Initialized {len(goals)} goals for faction {faction_id}")
    
    def _calculate_priority_from_attributes(self, base_value: int, modifiers: Dict[str, int]) -> int:
        """Calculate goal priority based on faction attributes"""
        priority = base_value
        
        for attr_name, modifier in modifiers.items():
            # Attribute values are 0-6, we want to map this to priority adjustments
            attribute_value = random.randint(2, 5)  # Default random if not provided
            priority += (attribute_value - 3) * modifier  # Center around 3
        
        # Ensure priority stays within valid bounds
        return max(5, min(100, priority))
    
    def get_faction_goals(self, faction_id: UUID, active_only: bool = True) -> List[FactionGoal]:
        """Get all goals for a faction"""
        goals = self.faction_goals.get(faction_id, [])
        
        if active_only:
            goals = [g for g in goals if g.is_active and not g.is_expired()]
        
        return sorted(goals, key=lambda g: g.calculate_urgency(), reverse=True)
    
    def add_goal(self, goal: FactionGoal) -> None:
        """Add a new goal for a faction"""
        if goal.faction_id not in self.faction_goals:
            self.faction_goals[goal.faction_id] = []
        
        self.faction_goals[goal.faction_id].append(goal)
        logger.info(f"Added {goal.goal_type.value} goal for faction {goal.faction_id}")
    
    def update_goal_progress(self, faction_id: UUID, goal_type: DiplomaticGoalType, progress_delta: float) -> None:
        """Update progress on a specific goal type"""
        goals = self.get_faction_goals(faction_id)
        
        for goal in goals:
            if goal.goal_type == goal_type:
                goal.update_progress(goal.progress + progress_delta)
                break
    
    def trigger_goal_evolution(self, faction_id: UUID, trigger_condition: str, context: Dict[str, Any] = None) -> List[FactionGoal]:
        """Trigger goal evolution based on events"""
        if context is None:
            context = {}
        
        new_goals = []
        
        for rule in self.evolution_rules:
            if rule.trigger_condition == trigger_condition:
                goal = self._apply_evolution_rule(faction_id, rule, context)
                if goal:
                    new_goals.append(goal)
        
        return new_goals
    
    def _apply_evolution_rule(self, faction_id: UUID, rule: GoalEvolutionRule, context: Dict[str, Any]) -> Optional[FactionGoal]:
        """Apply a specific evolution rule to a faction"""
        
        if rule.evolution_type == "new_goal":
            # Create a new goal
            priority = rule.parameters.get("priority", GoalPriority.MODERATE)
            deadline_days = rule.parameters.get("deadline_days")
            
            deadline = None
            if deadline_days:
                deadline = datetime.utcnow() + timedelta(days=deadline_days)
            
            goal = FactionGoal(
                faction_id=faction_id,
                goal_type=rule.goal_type,
                priority=priority,
                deadline=deadline,
                target_faction_id=context.get("target_faction_id"),
                target_region=context.get("target_region"),
                description=f"Goal triggered by {rule.trigger_condition}"
            )
            
            self.add_goal(goal)
            return goal
        
        elif rule.evolution_type == "priority_boost":
            # Boost priority of existing goals
            goals = self.get_faction_goals(faction_id)
            priority_increase = rule.parameters.get("priority_increase", 10)
            
            for goal in goals:
                if goal.goal_type == rule.goal_type:
                    new_priority_value = min(100, goal.priority.value + priority_increase)
                    goal.priority = GoalPriority(new_priority_value)
                    logger.info(f"Boosted {goal.goal_type.value} priority for faction {faction_id}")
                    return goal
        
        elif rule.evolution_type == "override_all":
            # Create critical goal that overrides others
            if rule.parameters.get("suspend_other_goals"):
                # Temporarily deactivate other goals
                for goal in self.get_faction_goals(faction_id):
                    if goal.goal_type != rule.goal_type:
                        goal.is_active = False
            
            # Create the override goal
            goal = FactionGoal(
                faction_id=faction_id,
                goal_type=rule.goal_type,
                priority=rule.parameters.get("priority", GoalPriority.CRITICAL),
                description=f"Critical goal triggered by {rule.trigger_condition}"
            )
            
            self.add_goal(goal)
            return goal
        
        return None
    
    def evaluate_goal_satisfaction(self, faction_id: UUID) -> Dict[DiplomaticGoalType, float]:
        """Evaluate how well faction goals are being satisfied"""
        goals = self.get_faction_goals(faction_id)
        satisfaction = {}
        
        for goal in goals:
            # Calculate satisfaction based on progress and urgency
            base_satisfaction = goal.progress
            
            # Adjust for urgency - highly urgent unfulfilled goals reduce satisfaction more
            urgency_penalty = goal.calculate_urgency() * (1.0 - goal.progress) * 0.5
            goal_satisfaction = max(0.0, base_satisfaction - urgency_penalty)
            
            satisfaction[goal.goal_type] = goal_satisfaction
        
        return satisfaction
    
    def get_dominant_goals(self, faction_id: UUID, limit: int = 3) -> List[FactionGoal]:
        """Get the most important/urgent goals for a faction"""
        goals = self.get_faction_goals(faction_id)
        
        # Sort by a combination of priority and urgency
        def goal_importance(goal: FactionGoal) -> float:
            return goal.priority.value * 0.7 + goal.calculate_urgency() * 30
        
        sorted_goals = sorted(goals, key=goal_importance, reverse=True)
        return sorted_goals[:limit]
    
    def cleanup_expired_goals(self) -> int:
        """Remove expired or completed goals"""
        removed_count = 0
        
        for faction_id, goals in self.faction_goals.items():
            original_count = len(goals)
            
            # Keep only active, non-expired, achievable goals
            goals[:] = [g for g in goals if g.is_active and not g.is_expired() and g.is_achievable]
            
            removed_count += original_count - len(goals)
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired/completed goals")
        
        return removed_count

# Global goal manager instance
_goal_manager = None

def get_goal_manager() -> FactionGoalManager:
    """Get the global goal manager instance"""
    global _goal_manager
    if _goal_manager is None:
        _goal_manager = FactionGoalManager()
    return _goal_manager 