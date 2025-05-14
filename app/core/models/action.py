"""
Action mechanics system for combat with various action types and effects.
"""

from typing import Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ActionType(str, Enum):
    """Types of actions that can be performed."""
    ATTACK = "attack"
    DEFEND = "defend"
    MOVE = "move"
    USE_ITEM = "use_item"
    CAST_SPELL = "cast_spell"
    SPECIAL_ABILITY = "special_ability"
    INTERACT = "interact"
    FLEE = "flee"

class ActionTarget(str, Enum):
    """Types of targets for actions."""
    SELF = "self"
    SINGLE = "single"
    MULTIPLE = "multiple"
    AREA = "area"
    ALL = "all"

class ActionEffect(BaseModel):
    """Effect that an action can have."""
    type: str
    magnitude: float
    duration: Optional[float] = None  # in seconds
    chance: float = Field(default=1.0, ge=0.0, le=1.0)
    conditions: List[Dict] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)

class ActionCost(BaseModel):
    """Cost of performing an action."""
    stamina: float = Field(default=0.0)
    mana: float = Field(default=0.0)
    health: float = Field(default=0.0)
    items: List[Dict] = Field(default_factory=list)
    cooldown: float = Field(default=0.0)  # in seconds

class ActionRequirement(BaseModel):
    """Requirements for performing an action."""
    level: Optional[int] = None
    stats: Dict[str, float] = Field(default_factory=dict)
    skills: Dict[str, float] = Field(default_factory=dict)
    items: List[str] = Field(default_factory=list)
    conditions: List[Dict] = Field(default_factory=list)

class Action(BaseModel):
    """Base action model."""
    id: str
    name: str
    type: ActionType
    target_type: ActionTarget
    description: str
    effects: List[ActionEffect] = Field(default_factory=list)
    cost: ActionCost = Field(default_factory=ActionCost)
    requirements: ActionRequirement = Field(default_factory=ActionRequirement)
    range: float = Field(default=1.0)  # in meters
    area: Optional[float] = None  # in square meters
    cooldown: float = Field(default=0.0)  # in seconds
    animation: Optional[str] = None
    sound: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)

    def can_perform(self, actor: Dict) -> bool:
        """Check if an actor can perform this action."""
        # Check level requirement
        if self.requirements.level and actor.get("level", 0) < self.requirements.level:
            return False
            
        # Check stat requirements
        for stat, value in self.requirements.stats.items():
            if actor.get("stats", {}).get(stat, 0) < value:
                return False
                
        # Check skill requirements
        for skill, value in self.requirements.skills.items():
            if actor.get("skills", {}).get(skill, 0) < value:
                return False
                
        # Check item requirements
        for item in self.requirements.items:
            if item not in actor.get("inventory", []):
                return False
                
        # Check conditions
        for condition in self.requirements.conditions:
            if not self._check_condition(condition, actor):
                return False
                
        return True

    def _check_condition(self, condition: Dict, actor: Dict) -> bool:
        """Check if a condition is met."""
        condition_type = condition.get("type")
        if condition_type == "status_effect":
            return condition.get("effect") in actor.get("status_effects", [])
        elif condition_type == "time_of_day":
            return condition.get("time") == actor.get("time_of_day")
        elif condition_type == "location":
            return condition.get("location") == actor.get("location")
        return True

class ActionResult(BaseModel):
    """Result of performing an action."""
    action_id: str
    actor_id: str
    target_ids: List[str]
    success: bool
    effects_applied: List[Dict] = Field(default_factory=list)
    damage_dealt: float = Field(default=0.0)
    healing_done: float = Field(default=0.0)
    status_effects: List[Dict] = Field(default_factory=list)
    resources_used: Dict[str, float] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict = Field(default_factory=dict)

class ActionSystem(BaseModel):
    """System for managing actions and their execution."""
    actions: Dict[str, Action] = Field(default_factory=dict)
    action_cooldowns: Dict[str, Dict[str, datetime]] = Field(default_factory=dict)
    last_update: datetime = Field(default_factory=datetime.utcnow)

    def register_action(self, action: Action):
        """Register a new action."""
        self.actions[action.id] = action
        self.last_update = datetime.utcnow()

    def unregister_action(self, action_id: str) -> bool:
        """Unregister an action."""
        if action_id in self.actions:
            del self.actions[action_id]
            if action_id in self.action_cooldowns:
                del self.action_cooldowns[action_id]
            self.last_update = datetime.utcnow()
            return True
        return False

    def can_perform_action(self, actor_id: str, action_id: str) -> bool:
        """Check if an actor can perform an action."""
        if action_id not in self.actions:
            return False
            
        action = self.actions[action_id]
        
        # Check cooldown
        if actor_id in self.action_cooldowns.get(action_id, {}):
            last_use = self.action_cooldowns[action_id][actor_id]
            cooldown_time = datetime.utcnow() - last_use
            if cooldown_time.total_seconds() < action.cooldown:
                return False
                
        return True

    def perform_action(self, actor: Dict, action_id: str, 
                      targets: List[Dict]) -> ActionResult:
        """Perform an action and return the result."""
        if action_id not in self.actions:
            raise ValueError(f"Action {action_id} not found")
            
        action = self.actions[action_id]
        
        # Check if action can be performed
        if not self.can_perform_action(actor["id"], action_id):
            return ActionResult(
                action_id=action_id,
                actor_id=actor["id"],
                target_ids=[t["id"] for t in targets],
                success=False,
                metadata={"reason": "cannot_perform"}
            )
            
        # Apply costs
        self._apply_costs(actor, action.cost)
        
        # Apply effects to targets
        effects_applied = []
        damage_dealt = 0.0
        healing_done = 0.0
        status_effects = []
        
        for target in targets:
            for effect in action.effects:
                if self._should_apply_effect(effect, actor, target):
                    effect_result = self._apply_effect(effect, target)
                    effects_applied.append(effect_result)
                    
                    if effect.type == "damage":
                        damage_dealt += effect_result.get("amount", 0)
                    elif effect.type == "healing":
                        healing_done += effect_result.get("amount", 0)
                    elif effect.type == "status_effect":
                        status_effects.append(effect_result)
        
        # Update cooldown
        if actor["id"] not in self.action_cooldowns:
            self.action_cooldowns[actor["id"]] = {}
        self.action_cooldowns[actor["id"]][action_id] = datetime.utcnow()
        
        self.last_update = datetime.utcnow()
        
        return ActionResult(
            action_id=action_id,
            actor_id=actor["id"],
            target_ids=[t["id"] for t in targets],
            success=True,
            effects_applied=effects_applied,
            damage_dealt=damage_dealt,
            healing_done=healing_done,
            status_effects=status_effects,
            resources_used={
                "stamina": action.cost.stamina,
                "mana": action.cost.mana,
                "health": action.cost.health
            }
        )

    def _apply_costs(self, actor: Dict, cost: ActionCost):
        """Apply the costs of performing an action."""
        # This would update the actor's resources
        pass

    def _should_apply_effect(self, effect: ActionEffect, 
                           actor: Dict, target: Dict) -> bool:
        """Determine if an effect should be applied."""
        # Check chance
        if effect.chance < 1.0:
            import random
            if random.random() > effect.chance:
                return False
                
        # Check conditions
        for condition in effect.conditions:
            if not self._check_condition(condition, target):
                return False
                
        return True

    def _apply_effect(self, effect: ActionEffect, target: Dict) -> Dict:
        """Apply an effect to a target."""
        # This would update the target's state
        return {
            "type": effect.type,
            "magnitude": effect.magnitude,
            "duration": effect.duration,
            "target_id": target["id"]
        } 