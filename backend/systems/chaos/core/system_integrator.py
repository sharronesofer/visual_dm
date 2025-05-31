"""
System Integrator

Manages integration between the chaos system and all other game systems,
including the event dispatcher, faction system, economy, regions, NPCs, and quests.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from uuid import UUID

from backend.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType
from backend.systems.chaos.models.pressure_data import PressureData, PressureReading, PressureSource
from backend.systems.chaos.models.chaos_state import ChaosState
from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


class SystemConnection:
    """Represents a connection to a game system"""
    
    def __init__(self, system_name: str, system_handler: Any, 
                 pressure_reader: Optional[Callable] = None,
                 event_handler: Optional[Callable] = None):
        self.system_name = system_name
        self.system_handler = system_handler
        self.pressure_reader = pressure_reader
        self.event_handler = event_handler
        self.last_connection_check = datetime.now()
        self.is_connected = False
        self.connection_attempts = 0
        
    async def test_connection(self) -> bool:
        """Test if the system connection is working"""
        try:
            if hasattr(self.system_handler, 'get_status'):
                status = await self.system_handler.get_status()
                self.is_connected = True
                return True
            elif hasattr(self.system_handler, 'health_check'):
                health = await self.system_handler.health_check()
                self.is_connected = health.get('status') == 'healthy'
                return self.is_connected
            else:
                # Assume connected if no health check method
                self.is_connected = True
                return True
        except Exception as e:
            logger.warning(f"Connection test failed for {self.system_name}: {e}")
            self.is_connected = False
            return False


class EventDispatcherIntegration:
    """Manages integration with the event dispatcher system"""
    
    def __init__(self, event_dispatcher=None):
        self.event_dispatcher = event_dispatcher
        self.chaos_event_subscribers: List[Callable] = []
        self.pressure_change_subscribers: List[Callable] = []
        self.mitigation_subscribers: List[Callable] = []
        
    async def initialize(self) -> None:
        """Initialize event dispatcher integration"""
        if self.event_dispatcher:
            # Subscribe to relevant game events
            await self._setup_event_subscriptions()
            logger.info("Event dispatcher integration initialized")
        else:
            logger.warning("No event dispatcher provided - running in standalone mode")
    
    async def _setup_event_subscriptions(self) -> None:
        """Set up subscriptions to game events that affect chaos"""
        try:
            # Subscribe to faction events
            await self.event_dispatcher.subscribe('faction.conflict_started', self._handle_faction_conflict)
            await self.event_dispatcher.subscribe('faction.war_declared', self._handle_war_declaration)
            await self.event_dispatcher.subscribe('faction.alliance_formed', self._handle_alliance_formation)
            await self.event_dispatcher.subscribe('faction.betrayal', self._handle_faction_betrayal)
            
            # Subscribe to economy events
            await self.event_dispatcher.subscribe('economy.market_crash', self._handle_market_crash)
            await self.event_dispatcher.subscribe('economy.trade_disruption', self._handle_trade_disruption)
            await self.event_dispatcher.subscribe('economy.resource_shortage', self._handle_resource_shortage)
            
            # Subscribe to quest events
            await self.event_dispatcher.subscribe('quest.completed', self._handle_quest_completion)
            await self.event_dispatcher.subscribe('quest.failed', self._handle_quest_failure)
            await self.event_dispatcher.subscribe('quest.major_milestone', self._handle_major_milestone)
            
            # Subscribe to region events
            await self.event_dispatcher.subscribe('region.disaster', self._handle_natural_disaster)
            await self.event_dispatcher.subscribe('region.population_change', self._handle_population_change)
            await self.event_dispatcher.subscribe('region.infrastructure_change', self._handle_infrastructure_change)
            
            # Subscribe to NPC events
            await self.event_dispatcher.subscribe('npc.death', self._handle_npc_death)
            await self.event_dispatcher.subscribe('npc.corruption_exposed', self._handle_corruption_exposure)
            await self.event_dispatcher.subscribe('npc.scandal', self._handle_scandal)
            
            logger.info("Event subscriptions configured")
            
        except Exception as e:
            logger.error(f"Failed to setup event subscriptions: {e}")
    
    async def publish_chaos_event(self, event: ChaosEvent) -> None:
        """Publish a chaos event to other systems"""
        if not self.event_dispatcher:
            return
            
        try:
            event_data = {
                'event_id': event.event_id,
                'event_type': event.event_type.value,
                'severity': event.severity.value,
                'title': event.title,
                'description': event.description,
                'affected_regions': [str(r) for r in event.affected_regions],
                'global_event': event.global_event,
                'triggered_at': event.triggered_at.isoformat() if event.triggered_at else None,
                'duration_hours': event.duration_hours,
                'chaos_score_at_trigger': event.chaos_score_at_trigger
            }
            
            await self.event_dispatcher.publish('chaos.event_triggered', event_data)
            
            # Notify chaos event subscribers
            for subscriber in self.chaos_event_subscribers:
                try:
                    await subscriber(event)
                except Exception as e:
                    logger.error(f"Error notifying chaos event subscriber: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to publish chaos event: {e}")
    
    async def publish_pressure_change(self, pressure_data: PressureData) -> None:
        """Publish pressure changes to interested systems"""
        if not self.event_dispatcher:
            return
            
        try:
            pressure_summary = pressure_data.global_pressure.get_pressure_summary()
            
            await self.event_dispatcher.publish('chaos.pressure_change', {
                'overall_pressure': pressure_summary.get('overall_pressure', 0.0),
                'pressure_sources': pressure_summary.get('source_breakdown', {}),
                'regional_pressure': {
                    str(region_id): pressure.get_overall_pressure()
                    for region_id, pressure in pressure_data.regional_pressures.items()
                },
                'timestamp': pressure_data.last_calculation.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to publish pressure change: {e}")
    
    # Event handlers for game events
    
    async def _handle_faction_conflict(self, event_data: Dict[str, Any]) -> None:
        """Handle faction conflict events"""
        logger.info(f"Faction conflict detected: {event_data}")
        # This would trigger pressure increases in the faction conflict source
        
    async def _handle_war_declaration(self, event_data: Dict[str, Any]) -> None:
        """Handle war declaration events"""
        logger.info(f"War declared: {event_data}")
        # Major pressure increase for military buildup and faction conflict
        
    async def _handle_alliance_formation(self, event_data: Dict[str, Any]) -> None:
        """Handle alliance formation events"""
        logger.info(f"Alliance formed: {event_data}")
        # This could be a positive mitigation factor
        
    async def _handle_faction_betrayal(self, event_data: Dict[str, Any]) -> None:
        """Handle faction betrayal events"""
        logger.info(f"Faction betrayal: {event_data}")
        # Major diplomatic tension increase
        
    async def _handle_market_crash(self, event_data: Dict[str, Any]) -> None:
        """Handle market crash events"""
        logger.info(f"Market crash: {event_data}")
        # Economic instability pressure spike
        
    async def _handle_trade_disruption(self, event_data: Dict[str, Any]) -> None:
        """Handle trade disruption events"""
        logger.info(f"Trade disruption: {event_data}")
        # Economic and resource pressure increases
        
    async def _handle_resource_shortage(self, event_data: Dict[str, Any]) -> None:
        """Handle resource shortage events"""
        logger.info(f"Resource shortage: {event_data}")
        # Resource scarcity pressure increase
        
    async def _handle_quest_completion(self, event_data: Dict[str, Any]) -> None:
        """Handle quest completion events"""
        logger.info(f"Quest completed: {event_data}")
        # Potential mitigation based on quest type
        
    async def _handle_quest_failure(self, event_data: Dict[str, Any]) -> None:
        """Handle quest failure events"""
        logger.info(f"Quest failed: {event_data}")
        # May increase pressure depending on quest importance
        
    async def _handle_major_milestone(self, event_data: Dict[str, Any]) -> None:
        """Handle major quest milestone events"""
        logger.info(f"Major milestone reached: {event_data}")
        # Significant mitigation for main quest progress
        
    async def _handle_natural_disaster(self, event_data: Dict[str, Any]) -> None:
        """Handle natural disaster events"""
        logger.info(f"Natural disaster: {event_data}")
        # Environmental pressure spike
        
    async def _handle_population_change(self, event_data: Dict[str, Any]) -> None:
        """Handle population change events"""
        logger.info(f"Population change: {event_data}")
        # Population stress adjustments
        
    async def _handle_infrastructure_change(self, event_data: Dict[str, Any]) -> None:
        """Handle infrastructure change events"""
        logger.info(f"Infrastructure change: {event_data}")
        # May affect multiple pressure sources
        
    async def _handle_npc_death(self, event_data: Dict[str, Any]) -> None:
        """Handle important NPC death events"""
        logger.info(f"Important NPC death: {event_data}")
        # May cause political upheaval or population stress
        
    async def _handle_corruption_exposure(self, event_data: Dict[str, Any]) -> None:
        """Handle corruption exposure events"""
        logger.info(f"Corruption exposed: {event_data}")
        # Corruption pressure but potential positive political outcome
        
    async def _handle_scandal(self, event_data: Dict[str, Any]) -> None:
        """Handle scandal events"""
        logger.info(f"Scandal: {event_data}")
        # Political and social pressure increases


class SystemIntegrator:
    """
    Main system integrator that manages connections to all game systems
    and coordinates cross-system communication for the chaos engine.
    """
    
    def __init__(self, config: ChaosConfig, event_dispatcher=None):
        self.config = config
        self.event_dispatcher_integration = EventDispatcherIntegration(event_dispatcher)
        
        # System connections
        self.system_connections: Dict[str, SystemConnection] = {}
        self.pressure_collection_tasks: Dict[str, asyncio.Task] = {}
        
        # Integration state
        self.is_initialized = False
        self.last_health_check = datetime.now()
        self.integration_metrics = {
            'successful_integrations': 0,
            'failed_integrations': 0,
            'pressure_collections': 0,
            'events_dispatched': 0,
            'connection_errors': 0
        }
        
        logger.info("System Integrator initialized")
    
    async def initialize(self) -> None:
        """Initialize all system integrations"""
        try:
            logger.info("Initializing system integrations...")
            
            # Initialize event dispatcher integration
            await self.event_dispatcher_integration.initialize()
            
            # Auto-discover and connect to available systems
            await self._discover_and_connect_systems()
            
            # Start pressure collection tasks
            await self._start_pressure_collection_tasks()
            
            self.is_initialized = True
            logger.info("System integration initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize system integrations: {e}")
            raise
    
    async def _discover_and_connect_systems(self) -> None:
        """Discover and connect to available game systems"""
        try:
            # This would normally scan for available system modules
            # For now, we'll define the expected system connections
            
            expected_systems = [
                'faction_system',
                'economy_system', 
                'region_system',
                'npc_system',
                'quest_system',
                'motif_system',
                'diplomacy_system',
                'population_system'
            ]
            
            for system_name in expected_systems:
                await self._attempt_system_connection(system_name)
                
        except Exception as e:
            logger.error(f"Error during system discovery: {e}")
    
    async def _attempt_system_connection(self, system_name: str) -> bool:
        """Attempt to connect to a specific system"""
        try:
            # Try to import and connect to the system
            # This is a placeholder - in reality would use dependency injection
            logger.info(f"Attempting connection to {system_name}")
            
            # Create a mock connection for now
            connection = SystemConnection(
                system_name=system_name,
                system_handler=None,  # Would be actual system instance
                pressure_reader=self._create_pressure_reader(system_name),
                event_handler=self._create_event_handler(system_name)
            )
            
            # Test the connection
            connection.is_connected = True  # Mock success
            self.system_connections[system_name] = connection
            
            self.integration_metrics['successful_integrations'] += 1
            logger.info(f"Successfully connected to {system_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {system_name}: {e}")
            self.integration_metrics['failed_integrations'] += 1
            return False
    
    def _create_pressure_reader(self, system_name: str) -> Callable:
        """Create a pressure reader function for a system"""
        async def pressure_reader() -> List[PressureReading]:
            """Read pressure data from the system"""
            try:
                # This would call the actual system's pressure monitoring
                # For now, return mock data
                readings = []
                
                if system_name == 'faction_system':
                    readings.append(PressureReading(
                        source=PressureSource.FACTION_CONFLICT,
                        value=0.3,  # Mock value
                        region_id=None,
                        metadata={'active_conflicts': 2}
                    ))
                elif system_name == 'economy_system':
                    readings.append(PressureReading(
                        source=PressureSource.ECONOMIC_INSTABILITY,
                        value=0.2,
                        region_id=None,
                        metadata={'market_volatility': 0.4}
                    ))
                # Add more system-specific pressure readings...
                
                return readings
                
            except Exception as e:
                logger.error(f"Error reading pressure from {system_name}: {e}")
                return []
        
        return pressure_reader
    
    def _create_event_handler(self, system_name: str) -> Callable:
        """Create an event handler function for a system"""
        async def event_handler(chaos_event: ChaosEvent) -> bool:
            """Handle a chaos event for this system"""
            try:
                logger.info(f"Applying chaos event {chaos_event.event_type.value} to {system_name}")
                
                # Apply event effects specific to this system
                for effect in chaos_event.immediate_effects + chaos_event.ongoing_effects:
                    if effect.target_system == system_name:
                        await self._apply_effect_to_system(effect, system_name, chaos_event)
                
                return True
                
            except Exception as e:
                logger.error(f"Error applying chaos event to {system_name}: {e}")
                return False
        
        return event_handler
    
    async def _apply_effect_to_system(self, effect, system_name: str, chaos_event: ChaosEvent) -> None:
        """Apply a specific effect to a system"""
        try:
            effect_type = effect.effect_type
            magnitude = effect.magnitude
            
            logger.debug(f"Applying {effect_type} effect (magnitude: {magnitude}) to {system_name}")
            
            # System-specific effect application
            if system_name == 'faction_system':
                await self._apply_faction_effect(effect_type, magnitude, chaos_event)
            elif system_name == 'economy_system':
                await self._apply_economy_effect(effect_type, magnitude, chaos_event)
            elif system_name == 'region_system':
                await self._apply_region_effect(effect_type, magnitude, chaos_event)
            elif system_name == 'npc_system':
                await self._apply_npc_effect(effect_type, magnitude, chaos_event)
            elif system_name == 'quest_system':
                await self._apply_quest_effect(effect_type, magnitude, chaos_event)
            # Add more system handlers...
            
        except Exception as e:
            logger.error(f"Error applying effect {effect.effect_type} to {system_name}: {e}")
    
    async def _apply_faction_effect(self, effect_type: str, magnitude: float, chaos_event: ChaosEvent) -> None:
        """Apply chaos effects to the faction system"""
        if effect_type == 'reduce_stability':
            # Reduce faction stability in affected regions
            for region_id in chaos_event.affected_regions:
                logger.debug(f"Reducing faction stability in region {region_id} by {magnitude}")
        elif effect_type == 'initiate_conflict':
            # Start conflicts between factions
            logger.debug(f"Initiating faction conflicts with magnitude {magnitude}")
        elif effect_type == 'reduce_resources':
            # Reduce faction resources
            logger.debug(f"Reducing faction resources by {magnitude}")
    
    async def _apply_economy_effect(self, effect_type: str, magnitude: float, chaos_event: ChaosEvent) -> None:
        """Apply chaos effects to the economy system"""
        if effect_type == 'reduce_stability':
            logger.debug(f"Reducing economic stability by {magnitude}")
        elif effect_type == 'disrupt_trade':
            logger.debug(f"Disrupting trade routes with magnitude {magnitude}")
        elif effect_type == 'market_volatility':
            logger.debug(f"Increasing market volatility by {magnitude}")
    
    async def _apply_region_effect(self, effect_type: str, magnitude: float, chaos_event: ChaosEvent) -> None:
        """Apply chaos effects to the region system"""
        if effect_type == 'damage_infrastructure':
            for region_id in chaos_event.affected_regions:
                logger.debug(f"Damaging infrastructure in region {region_id} by {magnitude}")
        elif effect_type == 'war_damage':
            logger.debug(f"Applying war damage with magnitude {magnitude}")
        elif effect_type == 'environmental_impact':
            logger.debug(f"Applying environmental impact with magnitude {magnitude}")
    
    async def _apply_npc_effect(self, effect_type: str, magnitude: float, chaos_event: ChaosEvent) -> None:
        """Apply chaos effects to the NPC system"""
        if effect_type == 'reduce_morale':
            logger.debug(f"Reducing NPC morale by {magnitude}")
        elif effect_type == 'increase_stress':
            logger.debug(f"Increasing NPC stress levels by {magnitude}")
        elif effect_type == 'behavior_change':
            logger.debug(f"Changing NPC behaviors with magnitude {magnitude}")
    
    async def _apply_quest_effect(self, effect_type: str, magnitude: float, chaos_event: ChaosEvent) -> None:
        """Apply chaos effects to the quest system"""
        if effect_type == 'increase_difficulty':
            logger.debug(f"Increasing quest difficulty by {magnitude}")
        elif effect_type == 'block_progress':
            logger.debug(f"Blocking quest progress with magnitude {magnitude}")
        elif effect_type == 'create_opportunity':
            logger.debug(f"Creating quest opportunities with magnitude {magnitude}")
    
    async def _start_pressure_collection_tasks(self) -> None:
        """Start background tasks to collect pressure data from systems"""
        for system_name, connection in self.system_connections.items():
            if connection.is_connected and connection.pressure_reader:
                task = asyncio.create_task(
                    self._pressure_collection_loop(system_name, connection)
                )
                self.pressure_collection_tasks[system_name] = task
                logger.debug(f"Started pressure collection task for {system_name}")
    
    async def _pressure_collection_loop(self, system_name: str, connection: SystemConnection) -> None:
        """Background loop to collect pressure data from a system"""
        while True:
            try:
                if connection.pressure_reader:
                    readings = await connection.pressure_reader()
                    if readings:
                        # Store readings for the pressure monitor to collect
                        self._store_pressure_readings(system_name, readings)
                        self.integration_metrics['pressure_collections'] += 1
                
                # Wait before next collection
                await asyncio.sleep(self.config.pressure_collection_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in pressure collection for {system_name}: {e}")
                self.integration_metrics['connection_errors'] += 1
                await asyncio.sleep(10)  # Wait before retrying
    
    def _store_pressure_readings(self, system_name: str, readings: List[PressureReading]) -> None:
        """Store pressure readings for collection by the pressure monitor"""
        # This would integrate with the pressure monitor's data collection
        logger.debug(f"Stored {len(readings)} pressure readings from {system_name}")
    
    async def dispatch_chaos_event(self, chaos_event: ChaosEvent) -> None:
        """Dispatch a chaos event to all connected systems"""
        try:
            # Publish to event dispatcher
            await self.event_dispatcher_integration.publish_chaos_event(chaos_event)
            
            # Apply to connected systems
            for system_name, connection in self.system_connections.items():
                if connection.is_connected and connection.event_handler:
                    try:
                        success = await connection.event_handler(chaos_event)
                        if success:
                            logger.debug(f"Successfully applied chaos event to {system_name}")
                        else:
                            logger.warning(f"Failed to apply chaos event to {system_name}")
                    except Exception as e:
                        logger.error(f"Error applying chaos event to {system_name}: {e}")
            
            self.integration_metrics['events_dispatched'] += 1
            
        except Exception as e:
            logger.error(f"Error dispatching chaos event: {e}")
    
    async def notify_pressure_change(self, pressure_data: PressureData) -> None:
        """Notify systems of pressure changes"""
        try:
            await self.event_dispatcher_integration.publish_pressure_change(pressure_data)
        except Exception as e:
            logger.error(f"Error notifying pressure change: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all system connections"""
        health_status = {
            'overall_health': 'healthy',
            'connected_systems': 0,
            'failed_systems': 0,
            'system_status': {},
            'integration_metrics': self.integration_metrics,
            'last_check': datetime.now().isoformat()
        }
        
        for system_name, connection in self.system_connections.items():
            try:
                is_healthy = await connection.test_connection()
                health_status['system_status'][system_name] = {
                    'status': 'healthy' if is_healthy else 'failed',
                    'last_check': connection.last_connection_check.isoformat(),
                    'connection_attempts': connection.connection_attempts
                }
                
                if is_healthy:
                    health_status['connected_systems'] += 1
                else:
                    health_status['failed_systems'] += 1
                    
            except Exception as e:
                health_status['system_status'][system_name] = {
                    'status': 'error',
                    'error': str(e),
                    'last_check': connection.last_connection_check.isoformat()
                }
                health_status['failed_systems'] += 1
        
        # Determine overall health
        if health_status['failed_systems'] == 0:
            health_status['overall_health'] = 'healthy'
        elif health_status['connected_systems'] > health_status['failed_systems']:
            health_status['overall_health'] = 'degraded'
        else:
            health_status['overall_health'] = 'unhealthy'
        
        self.last_health_check = datetime.now()
        return health_status
    
    async def shutdown(self) -> None:
        """Shutdown all system integrations"""
        try:
            # Cancel pressure collection tasks
            for task in self.pressure_collection_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.pressure_collection_tasks:
                await asyncio.gather(*self.pressure_collection_tasks.values(), return_exceptions=True)
            
            logger.info("System integrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during system integrator shutdown: {e}")
    
    def get_connected_systems(self) -> List[str]:
        """Get list of connected system names"""
        return [name for name, conn in self.system_connections.items() if conn.is_connected]
    
    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration performance metrics"""
        return {
            **self.integration_metrics,
            'connected_systems_count': len(self.get_connected_systems()),
            'total_systems': len(self.system_connections),
            'is_initialized': self.is_initialized,
            'last_health_check': self.last_health_check.isoformat()
        } 