"""
AI Decision Scheduler

This module manages the scheduling and execution of autonomous diplomatic decisions.
It triggers AI decision-making at appropriate intervals, executes decisions through
the decision engine, and tracks outcomes for learning.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import asyncio
import threading
import time
import logging
import random

# Import our AI components
from .decision_engine import (
    DiplomaticDecisionEngine, DecisionContext, DecisionOption, DecisionResult,
    get_decision_engine
)
from .goal_system import get_goal_manager

logger = logging.getLogger(__name__)

class ScheduleType(Enum):
    """Types of decision scheduling"""
    
    ROUTINE = "routine"                 # Regular diplomatic activities
    REACTIVE = "reactive"               # Response to events
    GOAL_DRIVEN = "goal_driven"         # Pursuing specific goals
    CRISIS_RESPONSE = "crisis_response" # Emergency decision making
    OPPORTUNITY = "opportunity"         # Capitalizing on opportunities

class SchedulePriority(Enum):
    """Priority levels for scheduled decisions"""
    
    LOW = 1         # Can wait, low importance
    NORMAL = 2      # Standard priority
    HIGH = 3        # Important, should be processed soon
    URGENT = 4      # Very important, process quickly
    CRITICAL = 5    # Emergency, process immediately

@dataclass
class ScheduledDecision:
    """A scheduled diplomatic decision"""
    
    schedule_id: UUID = field(default_factory=uuid4)
    faction_id: UUID = None
    schedule_type: ScheduleType = ScheduleType.ROUTINE
    priority: SchedulePriority = SchedulePriority.NORMAL
    
    # Scheduling details
    scheduled_time: datetime = field(default_factory=datetime.utcnow)
    execution_window: timedelta = field(default=timedelta(hours=1))
    max_delay: timedelta = field(default=timedelta(hours=6))
    
    # Decision context
    context: Optional[DecisionContext] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    
    # Execution tracking
    attempts: int = 0
    max_attempts: int = 3
    last_attempt: Optional[datetime] = None
    executed: bool = False
    execution_result: Optional[DecisionResult] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "ai_scheduler"
    notes: str = ""
    
    def is_ready_for_execution(self) -> bool:
        """Check if the decision is ready to be executed"""
        now = datetime.utcnow()
        
        # Check if it's time to execute
        if now < self.scheduled_time:
            return False
        
        # Check if we're within the execution window or past max delay
        time_since_scheduled = now - self.scheduled_time
        if time_since_scheduled > self.max_delay:
            return True  # Execute even if past window due to max delay
        
        if time_since_scheduled <= self.execution_window:
            return True
        
        return False
    
    def is_expired(self) -> bool:
        """Check if the decision has expired and should be cancelled"""
        now = datetime.utcnow()
        return (now - self.scheduled_time) > (self.max_delay + timedelta(hours=24))
    
    def should_retry(self) -> bool:
        """Check if the decision should be retried after failure"""
        if self.executed:
            return False
        
        if self.attempts >= self.max_attempts:
            return False
        
        # Wait at least 30 minutes between attempts
        if self.last_attempt:
            time_since_attempt = datetime.utcnow() - self.last_attempt
            if time_since_attempt < timedelta(minutes=30):
                return False
        
        return True

@dataclass
class FactionScheduleConfig:
    """Configuration for faction-specific scheduling"""
    
    faction_id: UUID
    
    # Routine decision intervals
    routine_interval: timedelta = field(default=timedelta(hours=6))
    goal_check_interval: timedelta = field(default=timedelta(hours=4))
    relationship_review_interval: timedelta = field(default=timedelta(hours=8))
    
    # Decision frequency modifiers
    activity_level: float = 1.0         # 0.5 = half as active, 2.0 = twice as active
    reactivity: float = 1.0             # How quickly to respond to events
    planning_horizon: timedelta = field(default=timedelta(days=7))
    
    # Scheduling preferences
    preferred_decision_times: List[int] = field(default_factory=lambda: [9, 14, 18])  # Hours
    avoid_decision_times: List[int] = field(default_factory=list)
    
    # Last activity tracking
    last_routine_decision: Optional[datetime] = None
    last_goal_review: Optional[datetime] = None
    last_relationship_review: Optional[datetime] = None
    
    # Personality-based modifiers
    impulsivity_modifier: float = 1.0   # Affects how quickly decisions are made
    patience_modifier: float = 1.0      # Affects willingness to wait for better timing

class DiplomaticAIScheduler:
    """Manages scheduling and execution of autonomous diplomatic decisions"""
    
    def __init__(
        self, 
        decision_engine: Optional[DiplomaticDecisionEngine] = None,
        diplomacy_service=None,
        faction_service=None,
        economy_service=None
    ):
        """Initialize the AI scheduler"""
        self.decision_engine = decision_engine or get_decision_engine(
            diplomacy_service, faction_service, economy_service
        )
        
        # Scheduling data
        self.scheduled_decisions: Dict[UUID, ScheduledDecision] = {}
        self.faction_configs: Dict[UUID, FactionScheduleConfig] = {}
        
        # Execution tracking
        self.execution_history: List[DecisionResult] = []
        self.active_factions: set[UUID] = set()
        
        # Scheduler control
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Configuration
        self.execution_interval = 60  # Check for decisions every minute
        self.max_concurrent_decisions = 10
        self.decision_timeout = 300  # 5 minutes timeout for decision execution
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        logger.info("Diplomatic AI Scheduler initialized")
    
    def start(self) -> None:
        """Start the AI scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.stop_event.clear()
        
        # Start the scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Diplomatic AI Scheduler started")
    
    def stop(self) -> None:
        """Stop the AI scheduler"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)
        
        logger.info("Diplomatic AI Scheduler stopped")
    
    def register_faction(
        self, 
        faction_id: UUID, 
        config: Optional[FactionScheduleConfig] = None
    ) -> None:
        """Register a faction for AI decision making"""
        
        if config is None:
            config = FactionScheduleConfig(faction_id=faction_id)
        
        # Apply personality-based modifications to config
        self._apply_personality_to_config(faction_id, config)
        
        self.faction_configs[faction_id] = config
        self.active_factions.add(faction_id)
        
        # Schedule initial routine decision
        self._schedule_routine_decisions(faction_id)
        
        logger.info(f"Registered faction {faction_id} for AI scheduling")
    
    def unregister_faction(self, faction_id: UUID) -> None:
        """Unregister a faction from AI decision making"""
        
        self.active_factions.discard(faction_id)
        
        # Cancel pending decisions for this faction
        to_cancel = [
            schedule_id for schedule_id, decision in self.scheduled_decisions.items()
            if decision.faction_id == faction_id and not decision.executed
        ]
        
        for schedule_id in to_cancel:
            del self.scheduled_decisions[schedule_id]
        
        logger.info(f"Unregistered faction {faction_id} from AI scheduling")
    
    def schedule_decision(
        self, 
        faction_id: UUID, 
        schedule_type: ScheduleType,
        context: Optional[DecisionContext] = None,
        context_data: Dict[str, Any] = None,
        priority: SchedulePriority = SchedulePriority.NORMAL,
        delay: timedelta = None,
        notes: str = ""
    ) -> UUID:
        """Schedule a specific decision for a faction"""
        
        if context_data is None:
            context_data = {}
        
        if delay is None:
            delay = self._calculate_decision_delay(faction_id, schedule_type, priority)
        
        scheduled_decision = ScheduledDecision(
            faction_id=faction_id,
            schedule_type=schedule_type,
            priority=priority,
            scheduled_time=datetime.utcnow() + delay,
            context=context,
            context_data=context_data,
            notes=notes
        )
        
        # Adjust execution window based on priority
        if priority == SchedulePriority.CRITICAL:
            scheduled_decision.execution_window = timedelta(minutes=5)
            scheduled_decision.max_delay = timedelta(minutes=15)
        elif priority == SchedulePriority.URGENT:
            scheduled_decision.execution_window = timedelta(minutes=30)
            scheduled_decision.max_delay = timedelta(hours=1)
        elif priority == SchedulePriority.HIGH:
            scheduled_decision.execution_window = timedelta(hours=1)
            scheduled_decision.max_delay = timedelta(hours=3)
        
        self.scheduled_decisions[scheduled_decision.schedule_id] = scheduled_decision
        
        logger.debug(f"Scheduled {schedule_type.value} decision for faction {faction_id} "
                    f"at {scheduled_decision.scheduled_time}")
        
        return scheduled_decision.schedule_id
    
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle external events that may trigger decisions"""
        
        logger.debug(f"Handling event: {event_type}")
        
        # Faction-specific events
        if event_type == "faction_attacked":
            self._handle_faction_attacked(event_data)
        elif event_type == "treaty_proposed":
            self._handle_treaty_proposed(event_data)
        elif event_type == "treaty_violated":
            self._handle_treaty_violated(event_data)
        elif event_type == "faction_weakened":
            self._handle_faction_weakened(event_data)
        elif event_type == "alliance_opportunity":
            self._handle_alliance_opportunity(event_data)
        elif event_type == "economic_crisis":
            self._handle_economic_crisis(event_data)
        
        # Call registered event handlers
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register a custom event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def get_faction_schedule_status(self, faction_id: UUID) -> Dict[str, Any]:
        """Get scheduling status for a faction"""
        
        config = self.faction_configs.get(faction_id)
        if not config:
            return {"error": "Faction not registered"}
        
        # Count pending decisions
        pending_decisions = [
            d for d in self.scheduled_decisions.values()
            if d.faction_id == faction_id and not d.executed
        ]
        
        # Get recent execution history
        recent_executions = [
            result for result in self.execution_history[-50:]
            if result.decision_option.parameters.get('faction_id') == faction_id
        ]
        
        return {
            "faction_id": faction_id,
            "active": faction_id in self.active_factions,
            "config": {
                "routine_interval": config.routine_interval.total_seconds() / 3600,
                "activity_level": config.activity_level,
                "reactivity": config.reactivity
            },
            "pending_decisions": len(pending_decisions),
            "recent_executions": len(recent_executions),
            "last_routine_decision": config.last_routine_decision,
            "last_goal_review": config.last_goal_review
        }
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        
        logger.info("Scheduler loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Process scheduled decisions
                self._process_scheduled_decisions()
                
                # Schedule new routine decisions
                self._schedule_routine_decisions_for_all()
                
                # Clean up expired decisions
                self._cleanup_expired_decisions()
                
                # Wait for next iteration
                self.stop_event.wait(self.execution_interval)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        logger.info("Scheduler loop ended")
    
    def _process_scheduled_decisions(self) -> None:
        """Process decisions that are ready for execution"""
        
        ready_decisions = [
            decision for decision in self.scheduled_decisions.values()
            if decision.is_ready_for_execution() and not decision.executed
        ]
        
        # Sort by priority and scheduled time
        ready_decisions.sort(
            key=lambda d: (d.priority.value, d.scheduled_time), 
            reverse=True
        )
        
        # Limit concurrent executions
        ready_decisions = ready_decisions[:self.max_concurrent_decisions]
        
        for decision in ready_decisions:
            try:
                self._execute_scheduled_decision(decision)
            except Exception as e:
                logger.error(f"Error executing decision {decision.schedule_id}: {e}")
                decision.attempts += 1
                decision.last_attempt = datetime.utcnow()
    
    def _execute_scheduled_decision(self, scheduled_decision: ScheduledDecision) -> None:
        """Execute a single scheduled decision"""
        
        logger.debug(f"Executing scheduled decision {scheduled_decision.schedule_id} "
                    f"for faction {scheduled_decision.faction_id}")
        
        scheduled_decision.attempts += 1
        scheduled_decision.last_attempt = datetime.utcnow()
        
        try:
            # Make the decision using the decision engine
            decision_option = self.decision_engine.make_autonomous_decision(
                scheduled_decision.faction_id,
                scheduled_decision.context,
                scheduled_decision.context_data
            )
            
            if decision_option:
                # Execute the decision
                result = self.decision_engine.execute_decision(
                    scheduled_decision.faction_id,
                    decision_option
                )
                
                # Store the result
                scheduled_decision.execution_result = result
                scheduled_decision.executed = True
                self.execution_history.append(result)
                
                # Update faction config timestamps
                self._update_faction_activity_timestamps(
                    scheduled_decision.faction_id, 
                    scheduled_decision.schedule_type
                )
                
                logger.info(f"Successfully executed decision for faction {scheduled_decision.faction_id}: "
                           f"{decision_option.decision_type.value}")
                
            else:
                logger.debug(f"No viable decision found for faction {scheduled_decision.faction_id}")
                scheduled_decision.executed = True  # Mark as processed even if no decision made
                
        except Exception as e:
            logger.error(f"Error executing decision for faction {scheduled_decision.faction_id}: {e}")
            
            # Check if we should retry
            if not scheduled_decision.should_retry():
                scheduled_decision.executed = True  # Give up after max attempts
    
    def _schedule_routine_decisions_for_all(self) -> None:
        """Schedule routine decisions for all active factions"""
        
        for faction_id in self.active_factions:
            self._schedule_routine_decisions(faction_id)
    
    def _schedule_routine_decisions(self, faction_id: UUID) -> None:
        """Schedule routine decisions for a specific faction"""
        
        config = self.faction_configs.get(faction_id)
        if not config:
            return
        
        now = datetime.utcnow()
        
        # Schedule routine diplomatic activities
        if (config.last_routine_decision is None or 
            now - config.last_routine_decision >= config.routine_interval):
            
            # Check if we already have a pending routine decision
            has_pending_routine = any(
                d.faction_id == faction_id and 
                d.schedule_type == ScheduleType.ROUTINE and 
                not d.executed
                for d in self.scheduled_decisions.values()
            )
            
            if not has_pending_routine:
                self.schedule_decision(
                    faction_id,
                    ScheduleType.ROUTINE,
                    DecisionContext.ROUTINE,
                    priority=SchedulePriority.NORMAL,
                    notes="Routine diplomatic activity"
                )
        
        # Schedule goal-driven decisions
        if (config.last_goal_review is None or 
            now - config.last_goal_review >= config.goal_check_interval):
            
            has_pending_goal = any(
                d.faction_id == faction_id and 
                d.schedule_type == ScheduleType.GOAL_DRIVEN and 
                not d.executed
                for d in self.scheduled_decisions.values()
            )
            
            if not has_pending_goal:
                self.schedule_decision(
                    faction_id,
                    ScheduleType.GOAL_DRIVEN,
                    DecisionContext.GOAL_PURSUIT,
                    priority=SchedulePriority.NORMAL,
                    notes="Goal-driven decision making"
                )
    
    def _cleanup_expired_decisions(self) -> None:
        """Remove expired decisions from the schedule"""
        
        expired_ids = [
            schedule_id for schedule_id, decision in self.scheduled_decisions.items()
            if decision.is_expired()
        ]
        
        for schedule_id in expired_ids:
            decision = self.scheduled_decisions[schedule_id]
            logger.debug(f"Removing expired decision {schedule_id} for faction {decision.faction_id}")
            del self.scheduled_decisions[schedule_id]
    
    def _calculate_decision_delay(
        self, 
        faction_id: UUID, 
        schedule_type: ScheduleType, 
        priority: SchedulePriority
    ) -> timedelta:
        """Calculate appropriate delay for a decision"""
        
        config = self.faction_configs.get(faction_id)
        
        # Base delays by priority
        base_delays = {
            SchedulePriority.CRITICAL: timedelta(minutes=1),
            SchedulePriority.URGENT: timedelta(minutes=15),
            SchedulePriority.HIGH: timedelta(hours=1),
            SchedulePriority.NORMAL: timedelta(hours=2),
            SchedulePriority.LOW: timedelta(hours=6)
        }
        
        delay = base_delays.get(priority, timedelta(hours=2))
        
        if config:
            # Apply personality modifiers
            if hasattr(config, 'impulsivity_modifier'):
                delay = timedelta(seconds=delay.total_seconds() / config.impulsivity_modifier)
            
            # Apply activity level
            delay = timedelta(seconds=delay.total_seconds() / config.activity_level)
            
            # Prefer certain times of day
            if config.preferred_decision_times:
                current_hour = datetime.utcnow().hour
                if current_hour not in config.preferred_decision_times:
                    # Delay until next preferred time
                    next_preferred = min(
                        h for h in config.preferred_decision_times 
                        if h > current_hour
                    ) if any(h > current_hour for h in config.preferred_decision_times) else min(config.preferred_decision_times)
                    
                    hours_to_wait = (next_preferred - current_hour) % 24
                    delay = max(delay, timedelta(hours=hours_to_wait))
        
        # Add some randomness to avoid predictable patterns
        randomness = random.uniform(0.8, 1.2)
        delay = timedelta(seconds=delay.total_seconds() * randomness)
        
        return delay
    
    def _apply_personality_to_config(self, faction_id: UUID, config: FactionScheduleConfig) -> None:
        """Apply faction personality traits to scheduling configuration"""
        
        try:
            personality_profile = self.decision_engine.personality_integrator.get_personality_profile(faction_id)
            
            # Adjust activity level based on ambition
            ambition_factor = personality_profile.ambition / 6.0
            config.activity_level *= (0.5 + ambition_factor)
            
            # Adjust reactivity based on impulsivity
            impulsivity_factor = personality_profile.impulsivity / 6.0
            config.reactivity *= (0.5 + impulsivity_factor * 1.5)
            
            # Adjust intervals based on discipline
            discipline_factor = personality_profile.discipline / 6.0
            interval_modifier = 0.5 + discipline_factor
            config.routine_interval = timedelta(
                seconds=config.routine_interval.total_seconds() / interval_modifier
            )
            
            # Store personality modifiers
            config.impulsivity_modifier = 0.5 + impulsivity_factor * 1.5
            config.patience_modifier = 0.5 + discipline_factor
            
        except Exception as e:
            logger.warning(f"Could not apply personality to config for faction {faction_id}: {e}")
    
    def _update_faction_activity_timestamps(
        self, 
        faction_id: UUID, 
        schedule_type: ScheduleType
    ) -> None:
        """Update faction activity timestamps"""
        
        config = self.faction_configs.get(faction_id)
        if not config:
            return
        
        now = datetime.utcnow()
        
        if schedule_type == ScheduleType.ROUTINE:
            config.last_routine_decision = now
        elif schedule_type == ScheduleType.GOAL_DRIVEN:
            config.last_goal_review = now
    
    # Event handlers
    def _handle_faction_attacked(self, event_data: Dict[str, Any]) -> None:
        """Handle faction being attacked"""
        
        victim_id = event_data.get('victim_faction_id')
        attacker_id = event_data.get('attacker_faction_id')
        
        if victim_id and victim_id in self.active_factions:
            # Schedule crisis response for the victim
            self.schedule_decision(
                victim_id,
                ScheduleType.CRISIS_RESPONSE,
                DecisionContext.CRISIS,
                context_data={
                    'threat_source': attacker_id,
                    'event_type': 'under_attack'
                },
                priority=SchedulePriority.CRITICAL,
                notes=f"Response to attack from {attacker_id}"
            )
        
        # Other factions might react to the conflict
        for faction_id in self.active_factions:
            if faction_id not in [victim_id, attacker_id]:
                # Schedule opportunity assessment
                self.schedule_decision(
                    faction_id,
                    ScheduleType.OPPORTUNITY,
                    DecisionContext.OPPORTUNITY,
                    context_data={
                        'opportunity_type': 'conflict_nearby',
                        'conflict_parties': [victim_id, attacker_id]
                    },
                    priority=SchedulePriority.HIGH,
                    delay=timedelta(hours=1),
                    notes="Assess opportunities from nearby conflict"
                )
    
    def _handle_treaty_proposed(self, event_data: Dict[str, Any]) -> None:
        """Handle treaty proposal"""
        
        proposer_id = event_data.get('proposer_faction_id')
        target_id = event_data.get('target_faction_id')
        treaty_type = event_data.get('treaty_type')
        
        if target_id and target_id in self.active_factions:
            # Schedule response decision for the target
            self.schedule_decision(
                target_id,
                ScheduleType.REACTIVE,
                DecisionContext.RESPONSE,
                context_data={
                    'action_type': 'treaty_proposal',
                    'source_faction': proposer_id,
                    'proposal_details': event_data
                },
                priority=SchedulePriority.HIGH,
                delay=timedelta(hours=2),
                notes=f"Response to {treaty_type} proposal from {proposer_id}"
            )
    
    def _handle_treaty_violated(self, event_data: Dict[str, Any]) -> None:
        """Handle treaty violation"""
        
        violator_id = event_data.get('violator_faction_id')
        victim_id = event_data.get('victim_faction_id')
        
        if victim_id and victim_id in self.active_factions:
            # Schedule crisis response
            self.schedule_decision(
                victim_id,
                ScheduleType.CRISIS_RESPONSE,
                DecisionContext.CRISIS,
                context_data={
                    'threat_source': violator_id,
                    'event_type': 'treaty_violation'
                },
                priority=SchedulePriority.URGENT,
                notes=f"Response to treaty violation by {violator_id}"
            )
    
    def _handle_faction_weakened(self, event_data: Dict[str, Any]) -> None:
        """Handle faction becoming weakened"""
        
        weakened_faction_id = event_data.get('faction_id')
        
        # Other factions might see this as an opportunity
        for faction_id in self.active_factions:
            if faction_id != weakened_faction_id:
                self.schedule_decision(
                    faction_id,
                    ScheduleType.OPPORTUNITY,
                    DecisionContext.OPPORTUNITY,
                    context_data={
                        'opportunity_type': 'weak_neighbor',
                        'target_faction': weakened_faction_id
                    },
                    priority=SchedulePriority.HIGH,
                    delay=timedelta(hours=3),
                    notes=f"Opportunity assessment: {weakened_faction_id} weakened"
                )
    
    def _handle_alliance_opportunity(self, event_data: Dict[str, Any]) -> None:
        """Handle alliance formation opportunity"""
        
        involved_factions = event_data.get('factions', [])
        
        for faction_id in involved_factions:
            if faction_id in self.active_factions:
                self.schedule_decision(
                    faction_id,
                    ScheduleType.OPPORTUNITY,
                    DecisionContext.OPPORTUNITY,
                    context_data={
                        'opportunity_type': 'alliance_formation',
                        'potential_partners': [f for f in involved_factions if f != faction_id]
                    },
                    priority=SchedulePriority.HIGH,
                    delay=timedelta(hours=1),
                    notes="Alliance formation opportunity"
                )
    
    def _handle_economic_crisis(self, event_data: Dict[str, Any]) -> None:
        """Handle economic crisis"""
        
        affected_factions = event_data.get('affected_factions', [])
        
        for faction_id in self.active_factions:
            if faction_id in affected_factions:
                # Crisis response for affected factions
                self.schedule_decision(
                    faction_id,
                    ScheduleType.CRISIS_RESPONSE,
                    DecisionContext.CRISIS,
                    context_data={
                        'event_type': 'economic_crisis',
                        'crisis_details': event_data
                    },
                    priority=SchedulePriority.URGENT,
                    notes="Response to economic crisis"
                )
            else:
                # Opportunity for unaffected factions
                self.schedule_decision(
                    faction_id,
                    ScheduleType.OPPORTUNITY,
                    DecisionContext.OPPORTUNITY,
                    context_data={
                        'opportunity_type': 'economic_advantage',
                        'affected_factions': affected_factions
                    },
                    priority=SchedulePriority.NORMAL,
                    delay=timedelta(hours=6),
                    notes="Economic opportunity from crisis"
                )

# Global scheduler instance
_ai_scheduler = None

def get_ai_scheduler(
    decision_engine=None,
    diplomacy_service=None,
    faction_service=None,
    economy_service=None
) -> DiplomaticAIScheduler:
    """Get the global AI scheduler instance"""
    global _ai_scheduler
    if _ai_scheduler is None:
        _ai_scheduler = DiplomaticAIScheduler(
            decision_engine, diplomacy_service, faction_service, economy_service
        )
    return _ai_scheduler 