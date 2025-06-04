"""
Tension Integration Manager

Coordinates all tension system integrations with other game systems:
- Manages NPC, quest, combat, economy, and faction integrations
- Orchestrates cross-system interactions
- Provides unified integration interface
- Handles integration event routing and coordination
- Manages ML analytics integration

This module provides a single entry point for all tension system integrations.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from backend.systems.tension import UnifiedTensionManager
from backend.infrastructure.events import event_bus

# Import integrations
from .npc_integration import TensionNPCIntegration
from .quest_integration import TensionQuestIntegration
from .combat_integration import TensionCombatIntegration
from .economy_integration import TensionEconomyIntegration
from .faction_integration import TensionFactionIntegration

# Import ML integration
from ..ml.prediction_engine import TensionPredictionEngine
from ..ml.pattern_analyzer import TensionPatternAnalyzer

logger = logging.getLogger(__name__)


class TensionIntegrationManager:
    """Coordinates all tension system integrations with other game systems"""
    
    def __init__(self, tension_manager: Optional[UnifiedTensionManager] = None):
        self.tension_manager = tension_manager or UnifiedTensionManager()
        
        # Initialize all integrations
        self.npc_integration = TensionNPCIntegration(self.tension_manager)
        self.quest_integration = TensionQuestIntegration(self.tension_manager)
        self.combat_integration = TensionCombatIntegration(self.tension_manager)
        self.economy_integration = TensionEconomyIntegration(self.tension_manager)
        self.faction_integration = TensionFactionIntegration(self.tension_manager)
        
        # Initialize ML capabilities
        self.prediction_engine = TensionPredictionEngine(self.tension_manager)
        self.pattern_analyzer = TensionPatternAnalyzer(self.tension_manager)
        
        # Integration registry
        self.integrations = {
            'npc': self.npc_integration,
            'quest': self.quest_integration, 
            'combat': self.combat_integration,
            'economy': self.economy_integration,
            'faction': self.faction_integration,
            'prediction': self.prediction_engine,
            'pattern_analysis': self.pattern_analyzer
        }
        
        # Cross-system coordination
        self.coordination_active = True
        self.event_history: List[Dict[str, Any]] = []
        
        # Register for coordinated events
        self._register_coordination_handlers()
        
        logger.info("Tension Integration Manager initialized with 7 integrations")
    
    def _register_coordination_handlers(self) -> None:
        """Register handlers for cross-system coordination"""
        event_bus.subscribe("tension:major_change", self._coordinate_system_responses)
        event_bus.subscribe("tension:conflict_triggered", self._handle_cross_system_conflict)
        event_bus.subscribe("tension:integration_request", self._handle_integration_request)
        
    def get_comprehensive_analysis(self, region_id: str, poi_id: str = 'default') -> Dict[str, Any]:
        """Get comprehensive analysis from all integrated systems"""
        try:
            current_tension = self.tension_manager.calculate_tension(region_id, poi_id)
            
            analysis = {
                'region_id': region_id,
                'poi_id': poi_id,
                'current_tension': current_tension,
                'timestamp': datetime.utcnow().isoformat(),
                'system_impacts': {},
                'predictions': {},
                'recommendations': []
            }
            
            # Get impacts from each system
            analysis['system_impacts']['npc'] = self.npc_integration.get_npc_behavior_modifiers(region_id, poi_id)
            analysis['system_impacts']['quest'] = self.quest_integration.get_dynamic_quests(region_id, current_tension)
            analysis['system_impacts']['combat'] = self.combat_integration.get_combat_modifiers(region_id, poi_id)
            analysis['system_impacts']['economy'] = self.economy_integration.get_economic_modifiers(region_id, poi_id)
            analysis['system_impacts']['faction'] = self.faction_integration.get_diplomatic_modifiers(region_id)
            
            # Get ML predictions
            analysis['predictions']['escalation'] = self.prediction_engine.predict_tension_escalation(
                region_id, poi_id, timedelta(hours=24)
            )
            analysis['predictions']['patterns'] = self.pattern_analyzer.analyze_tension_patterns(
                region_id, days_back=7
            )
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_comprehensive_recommendations(analysis)
            
            logger.info(f"Generated comprehensive analysis for {region_id}/{poi_id}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {e}")
            return {'error': str(e)}
    
    def trigger_coordinated_response(self, region_id: str, event_type: str, 
                                   event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger coordinated response across all integrated systems"""
        try:
            response = {
                'region_id': region_id,
                'event_type': event_type,
                'triggered_at': datetime.utcnow().isoformat(),
                'system_responses': {},
                'coordination_effects': []
            }
            
            current_tension = self.tension_manager.calculate_tension(region_id, 'default')
            
            # Trigger responses from each system
            if event_type == 'conflict_outbreak':
                response['system_responses']['npc'] = self._trigger_npc_conflict_response(region_id, current_tension, event_data)
                response['system_responses']['quest'] = self._trigger_quest_conflict_response(region_id, current_tension, event_data)
                response['system_responses']['combat'] = self._trigger_combat_conflict_response(region_id, current_tension, event_data)
                response['system_responses']['economy'] = self._trigger_economy_conflict_response(region_id, current_tension, event_data)
                response['system_responses']['faction'] = self._trigger_faction_conflict_response(region_id, current_tension, event_data)
            
            elif event_type == 'peace_establishment':
                response['system_responses']['npc'] = self._trigger_npc_peace_response(region_id, current_tension, event_data)
                response['system_responses']['quest'] = self._trigger_quest_peace_response(region_id, current_tension, event_data)
                response['system_responses']['economy'] = self._trigger_economy_peace_response(region_id, current_tension, event_data)
                response['system_responses']['faction'] = self._trigger_faction_peace_response(region_id, current_tension, event_data)
            
            # Calculate coordination effects
            response['coordination_effects'] = self._calculate_coordination_effects(response['system_responses'])
            
            # Store in event history
            self.event_history.append({
                'timestamp': response['triggered_at'],
                'region_id': region_id,
                'event_type': event_type,
                'response_summary': len(response['system_responses'])
            })
            
            # Emit coordination complete event
            event_bus.emit("tension:coordination_complete", response)
            
            logger.info(f"Coordinated {event_type} response in {region_id}: {len(response['system_responses'])} systems")
            
            return response
            
        except Exception as e:
            logger.error(f"Error triggering coordinated response: {e}")
            return {'error': str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get health status of all integrated systems"""
        try:
            health = {
                'overall_status': 'operational',
                'integration_manager': {
                    'coordination_active': self.coordination_active,
                    'event_history_size': len(self.event_history),
                    'registered_integrations': len(self.integrations)
                },
                'integrations': {}
            }
            
            # Check each integration
            for name, integration in self.integrations.items():
                if hasattr(integration, 'get_integration_status'):
                    health['integrations'][name] = integration.get_integration_status()
                else:
                    health['integrations'][name] = {'status': 'unknown'}
            
            # Determine overall health
            failed_integrations = []
            for name, status in health['integrations'].items():
                if 'error' in status or not status.get('integration_active', True):
                    failed_integrations.append(name)
            
            if failed_integrations:
                health['overall_status'] = 'degraded'
                health['failed_integrations'] = failed_integrations
            
            return health
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {'overall_status': 'error', 'error': str(e)}
    
    async def _coordinate_system_responses(self, event_data: Dict[str, Any]) -> None:
        """Coordinate responses across systems for major tension changes"""
        try:
            region_id = event_data.get('region_id')
            tension_level = event_data.get('tension_level', 0.0)
            change_magnitude = event_data.get('change_magnitude', 0.0)
            
            # Only coordinate for significant changes
            if change_magnitude > 0.2:
                coordination_response = self.trigger_coordinated_response(
                    region_id, 'major_tension_change', event_data
                )
                
                logger.info(f"Coordinated system responses for major tension change in {region_id}")
            
        except Exception as e:
            logger.error(f"Error coordinating system responses: {e}")
    
    async def _handle_cross_system_conflict(self, event_data: Dict[str, Any]) -> None:
        """Handle conflicts that affect multiple systems"""
        try:
            region_id = event_data.get('region_id')
            conflict_type = event_data.get('conflict_type')
            
            # Trigger coordinated conflict response
            coordination_response = self.trigger_coordinated_response(
                region_id, 'conflict_outbreak', event_data
            )
            
            logger.info(f"Handled cross-system conflict: {conflict_type} in {region_id}")
            
        except Exception as e:
            logger.error(f"Error handling cross-system conflict: {e}")
    
    async def _handle_integration_request(self, event_data: Dict[str, Any]) -> None:
        """Handle requests for specific integration data"""
        try:
            requester = event_data.get('requester')
            integration_type = event_data.get('integration_type')
            region_id = event_data.get('region_id')
            
            if integration_type in self.integrations:
                integration = self.integrations[integration_type]
                
                # Provide requested integration data
                if integration_type == 'npc':
                    data = integration.get_npc_behavior_modifiers(region_id, 'default')
                elif integration_type == 'economy':
                    data = integration.get_economic_modifiers(region_id, 'default')
                elif integration_type == 'faction':
                    data = integration.get_diplomatic_modifiers(region_id)
                else:
                    data = {'status': 'integration_available'}
                
                event_bus.emit("tension:integration_response", {
                    'requester': requester,
                    'integration_type': integration_type,
                    'region_id': region_id,
                    'data': data
                })
            
        except Exception as e:
            logger.error(f"Error handling integration request: {e}")
    
    def _generate_comprehensive_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on comprehensive analysis"""
        recommendations = []
        current_tension = analysis['current_tension']
        
        if current_tension > 0.8:
            recommendations.extend([
                "URGENT: Implement immediate conflict resolution measures",
                "Consider faction-mediated peace negotiations",
                "Increase security presence to protect civilians",
                "Prepare emergency economic measures"
            ])
        elif current_tension > 0.6:
            recommendations.extend([
                "Deploy additional NPCs for peacekeeping",
                "Generate diplomatic quests to ease tensions",
                "Monitor trade routes for disruptions",
                "Prepare contingency plans"
            ])
        elif current_tension > 0.4:
            recommendations.extend([
                "Increase diplomatic engagement between factions",
                "Generate community-building quests",
                "Monitor economic indicators"
            ])
        else:
            recommendations.extend([
                "Maintain current peaceful status",
                "Focus on economic development quests",
                "Strengthen inter-faction relationships"
            ])
        
        return recommendations
    
    # Helper methods for system-specific responses
    def _trigger_npc_conflict_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger NPC system response to conflict"""
        return self.npc_integration.apply_emergency_behavior_changes(region_id, tension, "conflict")
    
    def _trigger_quest_conflict_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger quest system response to conflict"""
        return self.quest_integration.generate_emergency_quests(region_id, tension, "conflict_resolution")
    
    def _trigger_combat_conflict_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger combat system response to conflict"""
        return self.combat_integration.apply_conflict_combat_changes(region_id, tension)
    
    def _trigger_economy_conflict_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger economy system response to conflict"""
        return self.economy_integration.apply_economic_sanctions(region_id, [], tension)
    
    def _trigger_faction_conflict_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger faction system response to conflict"""
        return self.faction_integration.process_diplomatic_cascade(region_id, tension)
    
    def _trigger_npc_peace_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger NPC system response to peace"""
        return self.npc_integration.apply_emergency_behavior_changes(region_id, -tension * 0.5, "peace")
    
    def _trigger_quest_peace_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger quest system response to peace"""
        return self.quest_integration.generate_emergency_quests(region_id, tension, "reconstruction")
    
    def _trigger_economy_peace_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger economy system response to peace"""
        # Generate recovery economic modifiers
        return {'economic_recovery': True, 'recovery_rate': 1.0 - tension}
    
    def _trigger_faction_peace_response(self, region_id: str, tension: float, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger faction system response to peace"""
        peace_treaty = {
            'signatories': event_data.get('involved_factions', []),
            'regions': [region_id],
            'strength': 1.0 - tension
        }
        return self.faction_integration.apply_peace_treaty_effects(peace_treaty)
    
    def _calculate_coordination_effects(self, system_responses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate effects of system coordination"""
        effects = []
        
        # Count successful responses
        successful_responses = len([r for r in system_responses.values() if 'error' not in r])
        
        if successful_responses >= 4:
            effects.append({
                'type': 'synergy_bonus',
                'description': 'Multiple systems working in coordination provide enhanced effectiveness',
                'magnitude': 0.2
            })
        
        if successful_responses >= 6:
            effects.append({
                'type': 'total_coordination',
                'description': 'All systems coordinating provides maximum stability',
                'magnitude': 0.3
            })
        
        return effects
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'coordination_active': self.coordination_active,
            'registered_integrations': len(self.integrations),
            'event_history_size': len(self.event_history),
            'integrations': {name: 'active' for name in self.integrations.keys()}
        } 