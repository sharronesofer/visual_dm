"""
Population System WebSocket Integration (Infrastructure Layer)

Integrates disease system business logic with WebSocket notifications to automatically
broadcast real-time updates to Unity clients when population events occur.

This is infrastructure code that bridges business logic with external communication.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.systems.population.utils.disease_models import (
    DiseaseType,
    DiseaseStage,
    DiseaseOutbreak,
    DISEASE_ENGINE
)

logger = logging.getLogger(__name__)

# Import WebSocket manager - handle import error gracefully
try:
    from backend.infrastructure.api.population.websocket_router import ws_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    logger.warning("WebSocket manager not available - notifications will be skipped")
    ws_manager = None
    WEBSOCKET_AVAILABLE = False

# Import quest integration - handle import error gracefully  
try:
    from backend.infrastructure.api.quest.population_integration import (
        handle_disease_outbreak_quest_generation,
        handle_population_change_quest_generation,
        population_quest_generator
    )
    QUEST_INTEGRATION_AVAILABLE = True
except ImportError:
    logger.warning("Quest integration not available - quest generation will be skipped")
    handle_disease_outbreak_quest_generation = None
    handle_population_change_quest_generation = None
    population_quest_generator = None
    QUEST_INTEGRATION_AVAILABLE = False


class PopulationEventIntegrator:
    """Integrates population system business events with infrastructure notifications"""
    
    def __init__(self):
        self.websocket_enabled = WEBSOCKET_AVAILABLE
        self.quest_integration_enabled = QUEST_INTEGRATION_AVAILABLE
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
    async def notify_disease_outbreak(
        self,
        population_id: str,
        disease_type: DiseaseType,
        outbreak: DiseaseOutbreak
    ):
        """Send WebSocket notification for new disease outbreak"""
        if not self.websocket_enabled:
            return
            
        try:
            profile = outbreak.get_profile()
            outbreak_data = {
                "disease_name": profile.name,
                "stage": outbreak.stage.value,
                "infected_count": outbreak.infected_count,
                "mortality_rate": profile.mortality_rate,
                "transmission_rate": profile.transmission_rate,
                "environmental_factors": {
                    "crowding_modifier": outbreak.current_crowding_modifier,
                    "hygiene_modifier": outbreak.current_hygiene_modifier,
                    "healthcare_modifier": outbreak.current_healthcare_modifier,
                    "seasonal_modifier": outbreak.current_seasonal_modifier
                }
            }
            
            await ws_manager.broadcast_disease_outbreak(
                population_id, disease_type, outbreak_data
            )
            
            # Generate quests for the outbreak if quest integration is available
            if self.quest_integration_enabled:
                quest_opportunities = await handle_disease_outbreak_quest_generation(
                    population_id=population_id,
                    disease_type=disease_type,
                    disease_stage=outbreak.stage,
                    outbreak_data=outbreak_data,
                    location_name=f"Settlement {population_id}"
                )
                
                # Broadcast quest opportunities if any were generated
                if quest_opportunities:
                    await self.notify_quest_opportunities(population_id, quest_opportunities)
            
            # Log event
            event = {
                "type": "disease_outbreak",
                "timestamp": datetime.utcnow().isoformat(),
                "population_id": population_id,
                "disease_type": disease_type.value,
                "disease_name": profile.name,
                "quest_integration_used": self.quest_integration_enabled
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for disease outbreak: {profile.name} in {population_id}")
            
        except Exception as e:
            logger.error(f"Error sending disease outbreak notification: {str(e)}")
    
    async def notify_disease_stage_change(
        self,
        population_id: str,
        disease_type: DiseaseType,
        old_stage: DiseaseStage,
        new_stage: DiseaseStage
    ):
        """Send WebSocket notification for disease stage progression"""
        if not self.websocket_enabled:
            return
            
        try:
            await ws_manager.broadcast_disease_stage_change(
                population_id, disease_type, old_stage, new_stage
            )
            
            # Generate new quests for the new stage if quest integration is available
            if self.quest_integration_enabled and new_stage in [DiseaseStage.SPREADING, DiseaseStage.PEAK, DiseaseStage.DECLINING]:
                # Get current outbreak data
                outbreak_data = {}
                if population_id in DISEASE_ENGINE.active_outbreaks:
                    for outbreak in DISEASE_ENGINE.active_outbreaks[population_id]:
                        if outbreak.disease_type == disease_type:
                            profile = outbreak.get_profile()
                            outbreak_data = {
                                "disease_name": profile.name,
                                "stage": outbreak.stage.value,
                                "infected_count": outbreak.infected_count,
                                "mortality_rate": profile.mortality_rate,
                                "transmission_rate": profile.transmission_rate
                            }
                            break
                
                quest_opportunities = await handle_disease_outbreak_quest_generation(
                    population_id=population_id,
                    disease_type=disease_type,
                    disease_stage=new_stage,
                    outbreak_data=outbreak_data,
                    location_name=f"Settlement {population_id}"
                )
                
                if quest_opportunities:
                    await self.notify_quest_opportunities(population_id, quest_opportunities)
            
            # Log event
            event = {
                "type": "disease_stage_change",
                "timestamp": datetime.utcnow().isoformat(),
                "population_id": population_id,
                "disease_type": disease_type.value,
                "old_stage": old_stage.value,
                "new_stage": new_stage.value,
                "quest_integration_used": self.quest_integration_enabled
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for disease stage change: {disease_type.value} {old_stage.value} -> {new_stage.value}")
            
        except Exception as e:
            logger.error(f"Error sending disease stage change notification: {str(e)}")
    
    async def notify_quest_opportunities(
        self,
        population_id: str,
        quest_opportunities: List[Dict[str, Any]]
    ):
        """Send WebSocket notification for new quest opportunities"""
        if not self.websocket_enabled or not quest_opportunities:
            return
            
        try:
            await ws_manager.broadcast_quest_opportunities(population_id, quest_opportunities)
            
            # Log event
            event = {
                "type": "quest_opportunities",
                "timestamp": datetime.utcnow().isoformat(),
                "population_id": population_id,
                "quest_count": len(quest_opportunities),
                "quest_types": list(set(q.get("type", "unknown") for q in quest_opportunities))
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for {len(quest_opportunities)} quest opportunities in {population_id}")
            
        except Exception as e:
            logger.error(f"Error sending quest opportunities notification: {str(e)}")
    
    async def notify_population_change(
        self,
        population_id: str,
        old_count: int,
        new_count: int,
        change_reason: str
    ):
        """Send WebSocket notification for population changes with quest integration"""
        try:
            # Send WebSocket notification
            if self.websocket_enabled:
                message = {
                    "type": "population_change",
                    "population_id": population_id,
                    "old_count": old_count,
                    "new_count": new_count,
                    "change_amount": new_count - old_count,
                    "change_reason": change_reason,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self._send_websocket_message(message)
            
            # Generate quests for significant population changes if quest integration is enabled
            quest_opportunities = []
            if self.quest_integration_enabled and population_quest_generator:
                quest_opportunities = population_quest_generator.generate_population_change_quests(
                    population_id=population_id,
                    old_count=old_count,
                    new_count=new_count,
                    change_reason=change_reason,
                    location_name=f"Settlement {population_id}"
                )
                
                if quest_opportunities:
                    await self.notify_quest_opportunities(population_id, quest_opportunities)
            
            # Log event
            event = {
                "type": "population_change",
                "timestamp": datetime.utcnow().isoformat(),
                "population_id": population_id,
                "old_count": old_count,
                "new_count": new_count,
                "change_amount": new_count - old_count,
                "change_reason": change_reason,
                "quest_integration_used": self.quest_integration_enabled
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for population change: {old_count} -> {new_count} ({change_reason})")
            
        except Exception as e:
            logger.error(f"Error sending population change notification: {str(e)}")
    
    async def notify_economic_change(
        self,
        settlement_id: str,
        change_type: str,
        economic_data: Dict[str, Any]
    ):
        """Send WebSocket notification for economic changes"""
        try:
            if self.websocket_enabled:
                message = {
                    "type": "economic_change",
                    "settlement_id": settlement_id,
                    "change_type": change_type,
                    "economic_data": economic_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self._send_websocket_message(message)
            
            # Log event
            event = {
                "type": "economic_change",
                "timestamp": datetime.utcnow().isoformat(),
                "settlement_id": settlement_id,
                "change_type": change_type,
                "economic_data": economic_data
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for economic change: {change_type} in {settlement_id}")
            
        except Exception as e:
            logger.error(f"Error sending economic change notification: {str(e)}")
    
    async def notify_trade_route_change(
        self,
        route_id: str,
        change_type: str,
        affected_settlements: List[str],
        route_data: Dict[str, Any]
    ):
        """Send WebSocket notification for trade route changes"""
        try:
            if self.websocket_enabled:
                message = {
                    "type": "trade_route_change",
                    "route_id": route_id,
                    "change_type": change_type,
                    "affected_settlements": affected_settlements,
                    "route_data": route_data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self._send_websocket_message(message)
            
            # Log event
            event = {
                "type": "trade_route_change",
                "timestamp": datetime.utcnow().isoformat(),
                "route_id": route_id,
                "change_type": change_type,
                "affected_settlements": affected_settlements,
                "route_data": route_data
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for trade route change: {change_type} for route {route_id}")
            
        except Exception as e:
            logger.error(f"Error sending trade route change notification: {str(e)}")
    
    async def notify_resource_shortage(
        self,
        settlement_id: str,
        resource_type: str,
        shortage_level: str,
        effects: Dict[str, Any]
    ):
        """Send WebSocket notification for critical resource shortages"""
        try:
            if self.websocket_enabled:
                message = {
                    "type": "resource_shortage",
                    "settlement_id": settlement_id,
                    "resource_type": resource_type,
                    "shortage_level": shortage_level,
                    "effects": effects,
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "critical" if shortage_level == "critical_shortage" else "warning"
                }
                
                await self._send_websocket_message(message)
            
            # Generate quests for resource shortages if quest integration is enabled
            quest_opportunities = []
            if self.quest_integration_enabled and population_quest_generator:
                # This would need to be implemented in the quest system
                # For now, log that quest generation could be triggered
                logger.info(f"Resource shortage quest opportunity: {resource_type} shortage in {settlement_id}")
            
            # Log event
            event = {
                "type": "resource_shortage",
                "timestamp": datetime.utcnow().isoformat(),
                "settlement_id": settlement_id,
                "resource_type": resource_type,
                "shortage_level": shortage_level,
                "effects": effects
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for resource shortage: {resource_type} ({shortage_level}) in {settlement_id}")
            
        except Exception as e:
            logger.error(f"Error sending resource shortage notification: {str(e)}")
    
    async def notify_economic_event(
        self,
        event_id: str,
        event_type: str,
        event_name: str,
        affected_settlements: List[str],
        event_status: str,
        effects: Dict[str, Any]
    ):
        """Send WebSocket notification for economic events"""
        try:
            if self.websocket_enabled:
                message = {
                    "type": "economic_event",
                    "event_id": event_id,
                    "event_type": event_type,
                    "event_name": event_name,
                    "affected_settlements": affected_settlements,
                    "event_status": event_status,
                    "effects": effects,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await self._send_websocket_message(message)
            
            # Log event
            event = {
                "type": "economic_event",
                "timestamp": datetime.utcnow().isoformat(),
                "event_id": event_id,
                "event_type": event_type,
                "event_name": event_name,
                "affected_settlements": affected_settlements,
                "event_status": event_status,
                "effects": effects
            }
            self._add_to_history(event)
            
            logger.info(f"WebSocket notification sent for economic event: {event_name} ({event_status})")
            
        except Exception as e:
            logger.error(f"Error sending economic event notification: {str(e)}")
    
    def _add_to_history(self, event: Dict[str, Any]):
        """Add event to history with size management"""
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            # Remove oldest events
            self.event_history = self.event_history[-self.max_history_size:]
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events from history"""
        return self.event_history[-limit:] if limit > 0 else self.event_history
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        event_counts = {}
        for event in self.event_history:
            event_type = event.get("type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Include quest statistics if available
        quest_stats = {}
        if self.quest_integration_enabled and population_quest_generator:
            quest_stats = population_quest_generator.get_quest_statistics()
        
        return {
            "websocket_enabled": self.websocket_enabled,
            "quest_integration_enabled": self.quest_integration_enabled,
            "total_events_processed": len(self.event_history),
            "events_by_type": event_counts,
            "history_size_limit": self.max_history_size,
            "quest_statistics": quest_stats
        }


# Global event integrator instance
event_integrator = PopulationEventIntegrator()


# Wrapper functions to integrate with existing disease system
async def integrate_disease_outbreak_notification(
    population_id: str,
    disease_type: DiseaseType,
    outbreak: DiseaseOutbreak
):
    """Wrapper function to trigger disease outbreak notifications"""
    await event_integrator.notify_disease_outbreak(population_id, disease_type, outbreak)


async def integrate_disease_progression_notification(
    population_id: str,
    outbreak: DiseaseOutbreak,
    old_stage: DiseaseStage
):
    """Wrapper function to trigger disease progression notifications"""
    if outbreak.stage != old_stage:
        await event_integrator.notify_disease_stage_change(
            population_id, outbreak.disease_type, old_stage, outbreak.stage
        )


async def integrate_quest_generation_notification(
    population_id: str,
    quest_opportunities: List[Dict[str, Any]]
):
    """Wrapper function to trigger quest opportunity notifications"""
    if quest_opportunities:
        await event_integrator.notify_quest_opportunities(population_id, quest_opportunities)


async def integrate_population_death_notification(
    population_id: str,
    old_population: int,
    new_population: int,
    disease_deaths: int
):
    """Wrapper function to trigger population death notifications"""
    if old_population != new_population:
        change_reason = f"disease_deaths_{disease_deaths}" if disease_deaths > 0 else "population_change"
        await event_integrator.notify_population_change(
            population_id, old_population, new_population, change_reason
        )


# Helper function to run async notifications in sync contexts
def run_notification_async(coro):
    """Run async notification in sync context using event loop"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a task
            asyncio.create_task(coro)
        else:
            # If we're in sync context, run until complete
            loop.run_until_complete(coro)
    except Exception as e:
        logger.error(f"Error running async notification: {str(e)}")


# Enhanced disease system functions with WebSocket integration
class EnhancedDiseaseModelingEngine:
    """Enhanced disease modeling engine with WebSocket integration"""
    
    def __init__(self, base_engine):
        self.base_engine = base_engine
        
    async def introduce_disease_with_notification(
        self,
        population_id: str,
        disease_type: DiseaseType,
        initial_infected: int = 1,
        environmental_factors: Optional[Dict[str, float]] = None
    ) -> DiseaseOutbreak:
        """Introduce disease with automatic WebSocket notification"""
        
        # Call base disease introduction (business logic)
        outbreak = self.base_engine.introduce_disease(
            population_id, disease_type, initial_infected, environmental_factors
        )
        
        # Send WebSocket notification (infrastructure)
        await integrate_disease_outbreak_notification(population_id, disease_type, outbreak)
        
        return outbreak
    
    async def progress_disease_day_with_notification(
        self,
        population_id: str,
        total_population: int,
        environmental_factors: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Progress disease with automatic WebSocket notifications"""
        
        # Store pre-progression states for comparison
        pre_outbreaks = {}
        if population_id in self.base_engine.active_outbreaks:
            for outbreak in self.base_engine.active_outbreaks[population_id]:
                pre_outbreaks[outbreak.disease_type] = outbreak.stage
        
        # Call base disease progression (business logic)
        result = self.base_engine.progress_disease_day(
            population_id, total_population, environmental_factors
        )
        
        # Check for stage changes and notify (infrastructure)
        if population_id in self.base_engine.active_outbreaks:
            for outbreak in self.base_engine.active_outbreaks[population_id]:
                old_stage = pre_outbreaks.get(outbreak.disease_type)
                if old_stage and old_stage != outbreak.stage:
                    await integrate_disease_progression_notification(
                        population_id, outbreak, old_stage
                    )
        
        # Notify about population changes if deaths occurred
        if result.get('new_deaths', 0) > 0:
            new_population = total_population - result['new_deaths']
            await integrate_population_death_notification(
                population_id, total_population, new_population, result['new_deaths']
            )
        
        return result


# Create enhanced engine instance
enhanced_disease_engine = EnhancedDiseaseModelingEngine(DISEASE_ENGINE)

# Export functions
__all__ = [
    "event_integrator",
    "enhanced_disease_engine",
    "integrate_disease_outbreak_notification",
    "integrate_disease_progression_notification", 
    "integrate_quest_generation_notification",
    "integrate_population_death_notification",
    "run_notification_async"
] 