"""
AI Framework Integration Service

This service provides integration between the diplomatic AI framework and existing
game systems (faction, economy, chaos, etc.) to enable comprehensive decision-making.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import AI framework components
from .goal_system import FactionGoalManager, DiplomaticGoalType, get_goal_manager
from .relationship_evaluator import RelationshipEvaluator, get_relationship_evaluator
from .strategic_analyzer import StrategicAnalyzer, get_strategic_analyzer
from .personality_integration import PersonalityIntegrator, get_personality_integrator
from .decision_engine import DiplomaticDecisionEngine, DecisionContext, get_decision_engine
from .decision_scheduler import DiplomaticAIScheduler, ScheduleType, SchedulePriority, get_ai_scheduler
from .outcome_tracker import DiplomaticOutcomeTracker, get_outcome_tracker

# Import diplomacy system components
from ..services.unified_diplomacy_service import UnifiedDiplomacyService

logger = logging.getLogger(__name__)

@dataclass
class SystemIntegrationConfig:
    """Configuration for system integrations"""
    
    # Service availability
    faction_service_available: bool = False
    economy_service_available: bool = False
    chaos_service_available: bool = False
    tension_service_available: bool = False
    
    # AI framework settings
    enable_autonomous_decisions: bool = True
    enable_goal_evolution: bool = True
    enable_learning: bool = True
    enable_event_reactions: bool = True
    
    # Performance settings
    max_concurrent_evaluations: int = 5
    decision_cooldown_minutes: int = 30
    batch_processing_size: int = 10
    
    # Integration intervals
    goal_sync_interval: timedelta = field(default=timedelta(hours=2))
    relationship_sync_interval: timedelta = field(default=timedelta(hours=1))
    economic_sync_interval: timedelta = field(default=timedelta(hours=4))
    
    # Event handling
    event_processing_delay: timedelta = field(default=timedelta(minutes=5))
    crisis_response_delay: timedelta = field(default=timedelta(minutes=1))

class DiplomaticAIIntegrationService:
    """Main integration service for the diplomatic AI framework"""
    
    def __init__(
        self,
        diplomacy_service: Optional[UnifiedDiplomacyService] = None,
        faction_service = None,
        economy_service = None,
        chaos_service = None,
        config: Optional[SystemIntegrationConfig] = None
    ):
        """Initialize the integration service"""
        self.config = config or SystemIntegrationConfig()
        
        # Core services
        self.diplomacy_service = diplomacy_service
        self.faction_service = faction_service
        self.economy_service = economy_service
        self.chaos_service = chaos_service
        
        # Update config based on service availability
        self._update_service_availability()
        
        # Initialize AI framework components
        self.goal_manager = get_goal_manager()
        self.relationship_evaluator = get_relationship_evaluator(diplomacy_service, faction_service)
        self.strategic_analyzer = get_strategic_analyzer(diplomacy_service, faction_service, economy_service)
        self.personality_integrator = get_personality_integrator(faction_service)
        self.decision_engine = get_decision_engine(diplomacy_service, faction_service, economy_service)
        self.scheduler = get_ai_scheduler(self.decision_engine, diplomacy_service, faction_service, economy_service)
        self.outcome_tracker = get_outcome_tracker(diplomacy_service, faction_service)
        
        # Integration state
        self.is_running = False
        self.last_sync_times: Dict[str, datetime] = {}
        self.registered_factions: List[UUID] = []
        self.event_queue: List[Dict[str, Any]] = []
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.config.max_concurrent_evaluations)
        
        logger.info("Diplomatic AI Integration Service initialized")
    
    def start(self) -> None:
        """Start the integration service"""
        if self.is_running:
            logger.warning("Integration service already running")
            return
        
        self.is_running = True
        
        # Start AI scheduler
        self.scheduler.start()
        
        # Initialize faction data if faction service available
        if self.config.faction_service_available:
            self._initialize_faction_data()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Start background sync processes
        asyncio.create_task(self._background_sync_loop())
        
        logger.info("Diplomatic AI Integration Service started")
    
    def stop(self) -> None:
        """Stop the integration service"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Stop AI scheduler
        self.scheduler.stop()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Diplomatic AI Integration Service stopped")
    
    def register_faction(self, faction_id: UUID, force_sync: bool = False) -> None:
        """Register a faction for AI decision-making"""
        if faction_id in self.registered_factions:
            if not force_sync:
                return
        else:
            self.registered_factions.append(faction_id)
        
        # Initialize faction goals if not already done
        if self.config.faction_service_available:
            faction_attributes = self._get_faction_attributes(faction_id)
            if faction_attributes:
                self.goal_manager.initialize_faction_goals(faction_id, faction_attributes)
        
        # Register with scheduler
        self.scheduler.register_faction(faction_id)
        
        logger.info(f"Registered faction {faction_id} for AI decision-making")
    
    def unregister_faction(self, faction_id: UUID) -> None:
        """Unregister a faction from AI decision-making"""
        if faction_id in self.registered_factions:
            self.registered_factions.remove(faction_id)
        
        # Unregister from scheduler
        self.scheduler.unregister_faction(faction_id)
        
        logger.info(f"Unregistered faction {faction_id} from AI decision-making")
    
    def handle_game_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle game events that may trigger diplomatic responses"""
        if not self.config.enable_event_reactions:
            return
        
        # Add to event queue for processing
        event = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.utcnow()
        }
        self.event_queue.append(event)
        
        # Process immediately for crisis events
        if event_type in ['faction_attacked', 'war_declared', 'alliance_broken']:
            asyncio.create_task(self._process_event_immediate(event))
        
        logger.debug(f"Queued event {event_type} for processing")
    
    def get_faction_ai_status(self, faction_id: UUID) -> Dict[str, Any]:
        """Get comprehensive AI status for a faction"""
        if faction_id not in self.registered_factions:
            return {'registered': False}
        
        # Get current goals
        goals = self.goal_manager.get_faction_goals(faction_id)
        
        # Get scheduler status
        schedule_status = self.scheduler.get_faction_schedule_status(faction_id)
        
        # Get recent decision outcomes
        recent_outcomes = self.outcome_tracker.get_faction_learning_summary(faction_id)
        
        return {
            'registered': True,
            'active_goals': len(goals),
            'goal_types': [g.goal_type.value for g in goals],
            'scheduled_decisions': schedule_status.get('pending_decisions', 0),
            'last_decision': schedule_status.get('last_decision_time'),
            'success_rate': recent_outcomes.get('success_rate', 0.0),
            'learning_progress': recent_outcomes.get('learning_progress', {}),
            'next_routine_decision': schedule_status.get('next_routine_decision')
        }
    
    def trigger_faction_decision_evaluation(self, faction_id: UUID, priority: str = 'normal') -> List[Dict[str, Any]]:
        """Manually trigger decision evaluation for a faction"""
        if faction_id not in self.registered_factions:
            logger.warning(f"Faction {faction_id} not registered for AI decisions")
            return []
        
        # Evaluate all possible decisions
        decisions = self.decision_engine.evaluate_all_decisions(faction_id)
        
        # Schedule high-priority decisions
        schedule_priority = SchedulePriority.HIGH if priority == 'high' else SchedulePriority.NORMAL
        
        for decision in decisions:
            if decision.recommended and decision.confidence >= 0.7:
                context_data = {
                    'manual_trigger': True,
                    'decision_details': decision.proposal_details,
                    'expected_outcome': decision.expected_outcome
                }
                
                self.scheduler.schedule_decision(
                    faction_id=faction_id,
                    schedule_type=ScheduleType.GOAL_DRIVEN,
                    priority=schedule_priority,
                    delay=timedelta(minutes=1),
                    notes=f"Manual evaluation trigger: {decision.decision_type.value}"
                )
        
        # Return decision summaries
        return [
            {
                'decision_type': d.decision_type.value,
                'recommended': d.recommended,
                'confidence': d.confidence,
                'priority': d.priority,
                'reasoning': d.reasoning
            }
            for d in decisions
        ]
    
    def update_faction_goals(self, faction_id: UUID, trigger_condition: str, context: Dict[str, Any] = None) -> None:
        """Update faction goals based on changing circumstances"""
        if faction_id not in self.registered_factions:
            return
        
        if not self.config.enable_goal_evolution:
            return
        
        # Trigger goal evolution
        new_goals = self.goal_manager.trigger_goal_evolution(
            faction_id, trigger_condition, context or {}
        )
        
        if new_goals:
            logger.info(f"Updated goals for faction {faction_id}: {len(new_goals)} new goals from trigger '{trigger_condition}'")
            
            # Schedule goal-driven decisions
            self.scheduler.schedule_decision(
                faction_id=faction_id,
                schedule_type=ScheduleType.GOAL_DRIVEN,
                priority=SchedulePriority.HIGH,
                delay=timedelta(minutes=10),
                notes=f"Goal evolution triggered by {trigger_condition}"
            )
    
    # Private methods for system integration
    
    def _update_service_availability(self) -> None:
        """Update config based on available services"""
        self.config.faction_service_available = self.faction_service is not None
        self.config.economy_service_available = self.economy_service is not None
        self.config.chaos_service_available = self.chaos_service is not None
    
    def _initialize_faction_data(self) -> None:
        """Initialize data for all factions"""
        if not self.faction_service:
            return
        
        try:
            # Get all active factions
            all_factions = self._get_all_factions()
            
            for faction_id in all_factions:
                # Initialize goals if not already done
                faction_attributes = self._get_faction_attributes(faction_id)
                if faction_attributes:
                    self.goal_manager.initialize_faction_goals(faction_id, faction_attributes)
            
            logger.info(f"Initialized AI data for {len(all_factions)} factions")
            
        except Exception as e:
            logger.error(f"Error initializing faction data: {e}")
    
    def _get_all_factions(self) -> List[UUID]:
        """Get list of all faction IDs"""
        # This would interface with the faction service
        # For now, return empty list - needs faction service integration
        return []
    
    def _get_faction_attributes(self, faction_id: UUID) -> Optional[Dict[str, int]]:
        """Get faction personality attributes"""
        if not self.faction_service:
            return None
        
        try:
            # This would call faction service to get hidden attributes
            # For now, return default attributes
            return {
                'hidden_ambition': 3,
                'hidden_integrity': 3,
                'hidden_discipline': 3,
                'hidden_impulsivity': 3,
                'hidden_pragmatism': 3,
                'hidden_resilience': 3
            }
        except Exception as e:
            logger.error(f"Error getting faction attributes for {faction_id}: {e}")
            return None
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for game events"""
        # Register event handlers with game systems
        event_handlers = {
            'faction_attacked': self._handle_faction_attacked,
            'treaty_proposed': self._handle_treaty_proposed,
            'treaty_violated': self._handle_treaty_violated,
            'alliance_broken': self._handle_alliance_broken,
            'economic_crisis': self._handle_economic_crisis,
            'chaos_event': self._handle_chaos_event,
            'faction_created': self._handle_faction_created,
            'faction_destroyed': self._handle_faction_destroyed
        }
        
        for event_type, handler in event_handlers.items():
            # Register with scheduler's event system
            self.scheduler.register_event_handler(event_type, handler)
    
    async def _background_sync_loop(self) -> None:
        """Background loop for syncing data with other systems"""
        while self.is_running:
            try:
                # Sync faction data
                if self._should_sync('faction'):
                    await self._sync_faction_data()
                
                # Sync economic data
                if self._should_sync('economy'):
                    await self._sync_economic_data()
                
                # Process event queue
                await self._process_event_queue()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                # Wait before next cycle
                await asyncio.sleep(60)  # 1 minute cycle
                
            except Exception as e:
                logger.error(f"Error in background sync loop: {e}")
                await asyncio.sleep(60)
    
    def _should_sync(self, system: str) -> bool:
        """Check if system data should be synced"""
        sync_intervals = {
            'faction': self.config.goal_sync_interval,
            'economy': self.config.economic_sync_interval,
            'relationships': self.config.relationship_sync_interval
        }
        
        interval = sync_intervals.get(system, timedelta(hours=1))
        last_sync = self.last_sync_times.get(system, datetime.min)
        
        return (datetime.utcnow() - last_sync) >= interval
    
    async def _sync_faction_data(self) -> None:
        """Sync data with faction system"""
        if not self.config.faction_service_available:
            return
        
        try:
            # Update faction goals based on current state
            for faction_id in self.registered_factions:
                faction_attributes = self._get_faction_attributes(faction_id)
                if faction_attributes:
                    # Check if goals need updating
                    current_goals = self.goal_manager.get_faction_goals(faction_id)
                    if not current_goals:
                        self.goal_manager.initialize_faction_goals(faction_id, faction_attributes)
            
            self.last_sync_times['faction'] = datetime.utcnow()
            logger.debug("Completed faction data sync")
            
        except Exception as e:
            logger.error(f"Error syncing faction data: {e}")
    
    async def _sync_economic_data(self) -> None:
        """Sync data with economy system"""
        if not self.config.economy_service_available:
            return
        
        try:
            # Update economic considerations for strategic analysis
            # This would interface with the economy system to get current economic state
            # and update faction goals related to prosperity
            
            self.last_sync_times['economy'] = datetime.utcnow()
            logger.debug("Completed economic data sync")
            
        except Exception as e:
            logger.error(f"Error syncing economic data: {e}")
    
    async def _process_event_queue(self) -> None:
        """Process queued events"""
        if not self.event_queue:
            return
        
        # Process events in batches
        batch_size = self.config.batch_processing_size
        events_to_process = self.event_queue[:batch_size]
        self.event_queue = self.event_queue[batch_size:]
        
        for event in events_to_process:
            try:
                await self._process_event(event)
            except Exception as e:
                logger.error(f"Error processing event {event['type']}: {e}")
    
    async def _process_event(self, event: Dict[str, Any]) -> None:
        """Process a single event"""
        event_type = event['type']
        event_data = event['data']
        
        # Delegate to scheduler's event handling
        self.scheduler.handle_event(event_type, event_data)
    
    async def _process_event_immediate(self, event: Dict[str, Any]) -> None:
        """Process high-priority events immediately"""
        try:
            await self._process_event(event)
        except Exception as e:
            logger.error(f"Error processing immediate event {event['type']}: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Cleanup old data and expired decisions"""
        try:
            # Cleanup expired goals
            if hasattr(self.goal_manager, 'cleanup_expired_goals'):
                expired_count = self.goal_manager.cleanup_expired_goals()
                if expired_count > 0:
                    logger.debug(f"Cleaned up {expired_count} expired goals")
            
            # Cleanup old outcome tracking data (keep last 30 days)
            # This would be implemented in the outcome tracker
            
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")
    
    # Event handlers
    
    def _handle_faction_attacked(self, event_data: Dict[str, Any]) -> None:
        """Handle faction being attacked"""
        victim_id = event_data.get('victim_faction_id')
        attacker_id = event_data.get('attacker_faction_id')
        
        if victim_id in self.registered_factions:
            # Update goals to prioritize security
            self.update_faction_goals(victim_id, 'faction_attacked', {
                'attacker': attacker_id,
                'severity': event_data.get('severity', 'moderate')
            })
    
    def _handle_treaty_proposed(self, event_data: Dict[str, Any]) -> None:
        """Handle treaty proposal"""
        proposer_id = event_data.get('proposer_faction_id')
        target_id = event_data.get('target_faction_id')
        
        if target_id in self.registered_factions:
            # Schedule decision to evaluate treaty
            self.scheduler.schedule_decision(
                faction_id=target_id,
                schedule_type=ScheduleType.REACTIVE,
                priority=SchedulePriority.HIGH,
                delay=timedelta(hours=1),
                notes=f"Treaty proposal from faction {proposer_id}"
            )
    
    def _handle_treaty_violated(self, event_data: Dict[str, Any]) -> None:
        """Handle treaty violation"""
        violator_id = event_data.get('violator_faction_id')
        victim_id = event_data.get('victim_faction_id')
        
        if victim_id in self.registered_factions:
            # Update goals to consider retaliation
            self.update_faction_goals(victim_id, 'treaty_violated', {
                'violator': violator_id,
                'treaty_type': event_data.get('treaty_type')
            })
    
    def _handle_alliance_broken(self, event_data: Dict[str, Any]) -> None:
        """Handle alliance being broken"""
        faction_a_id = event_data.get('faction_a_id')
        faction_b_id = event_data.get('faction_b_id')
        
        for faction_id in [faction_a_id, faction_b_id]:
            if faction_id in self.registered_factions:
                self.update_faction_goals(faction_id, 'alliance_broken', {
                    'former_ally': faction_b_id if faction_id == faction_a_id else faction_a_id
                })
    
    def _handle_economic_crisis(self, event_data: Dict[str, Any]) -> None:
        """Handle economic crisis"""
        affected_factions = event_data.get('affected_factions', [])
        
        for faction_id in affected_factions:
            if faction_id in self.registered_factions:
                self.update_faction_goals(faction_id, 'economic_crisis', {
                    'severity': event_data.get('severity', 'moderate'),
                    'type': event_data.get('crisis_type')
                })
    
    def _handle_chaos_event(self, event_data: Dict[str, Any]) -> None:
        """Handle chaos system events"""
        affected_regions = event_data.get('affected_regions', [])
        
        # Find factions in affected regions and update their goals
        for faction_id in self.registered_factions:
            # This would check if faction is in affected regions
            # For now, assume all factions may be affected
            self.update_faction_goals(faction_id, 'chaos_event', {
                'event_type': event_data.get('event_type'),
                'severity': event_data.get('severity', 'moderate')
            })
    
    def _handle_faction_created(self, event_data: Dict[str, Any]) -> None:
        """Handle new faction creation"""
        faction_id = event_data.get('faction_id')
        if faction_id:
            self.register_faction(faction_id)
    
    def _handle_faction_destroyed(self, event_data: Dict[str, Any]) -> None:
        """Handle faction destruction"""
        faction_id = event_data.get('faction_id')
        if faction_id:
            self.unregister_faction(faction_id)


# Global instance management
_integration_service_instance = None

def get_integration_service(
    diplomacy_service=None,
    faction_service=None,
    economy_service=None,
    chaos_service=None,
    config=None
) -> DiplomaticAIIntegrationService:
    """Get or create the global integration service instance"""
    global _integration_service_instance
    if _integration_service_instance is None:
        _integration_service_instance = DiplomaticAIIntegrationService(
            diplomacy_service, faction_service, economy_service, chaos_service, config
        )
    return _integration_service_instance

def create_integration_service(
    diplomacy_service=None,
    faction_service=None,
    economy_service=None,
    chaos_service=None,
    config=None
) -> DiplomaticAIIntegrationService:
    """Create a new integration service instance"""
    return DiplomaticAIIntegrationService(
        diplomacy_service, faction_service, economy_service, chaos_service, config
    ) 