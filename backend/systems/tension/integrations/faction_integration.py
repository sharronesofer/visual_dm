"""
Tension-Faction System Integration

Modifies faction relationships and diplomatic status based on tension levels:
- Dynamic faction relationship changes based on regional tension
- Diplomatic status modifications during conflicts
- Alliance formation/dissolution based on mutual threats
- Faction reputation adjustments from tension events
- Border dispute escalation mechanics
- Peace treaty effects on regional tension

This follows the integration patterns from other game systems.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass

from backend.systems.tension import UnifiedTensionManager
from backend.infrastructure.events import event_bus

logger = logging.getLogger(__name__)


class FactionRelationshipStatus(Enum):
    """Types of faction relationships"""
    ALLIANCE = "alliance"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    SUSPICIOUS = "suspicious"
    HOSTILE = "hostile"
    WAR = "war"


class DiplomaticAction(Enum):
    """Types of diplomatic actions triggered by tension"""
    PEACE_PROPOSAL = "peace_proposal"
    ALLIANCE_OFFER = "alliance_offer"
    TRADE_AGREEMENT = "trade_agreement"
    NON_AGGRESSION_PACT = "non_aggression_pact"
    DEMAND_WITHDRAWAL = "demand_withdrawal"
    ULTIMATUM = "ultimatum"
    DECLARE_WAR = "declare_war"
    BREAK_ALLIANCE = "break_alliance"


@dataclass
class FactionRelationship:
    """Relationship between two factions"""
    faction_a: str
    faction_b: str
    relationship_status: FactionRelationshipStatus
    relationship_score: float  # -1.0 (hostile) to 1.0 (allied)
    tension_impact: float  # How much tension affects this relationship
    diplomatic_immunity: bool  # Whether relationship is protected from tension
    last_modified: datetime
    recent_events: List[str]
    trust_level: float  # 0.0 to 1.0
    shared_interests: List[str]
    conflict_history: List[Dict[str, Any]]


@dataclass
class DiplomaticModifiers:
    """Diplomatic effects based on tension levels"""
    relationship_changes: Dict[str, float]  # faction_pair -> relationship_delta
    automatic_actions: List[DiplomaticAction]
    reputation_adjustments: Dict[str, float]  # faction -> reputation_delta
    alliance_stability: Dict[str, float]  # alliance_id -> stability_modifier
    trade_penalties: Dict[str, float]  # faction_pair -> trade_modifier
    border_tensions: Dict[str, float]  # border_region -> tension_modifier


@dataclass
class FactionTensionResponse:
    """How a faction responds to regional tension"""
    faction_id: str
    region_id: str
    response_type: str
    military_posture: str  # defensive, aggressive, neutral, withdrawal
    diplomatic_actions: List[DiplomaticAction]
    resource_allocation: Dict[str, float]
    public_statements: List[str]
    expected_duration: Optional[timedelta]


class TensionFactionIntegration:
    """Manages faction system integration with tension system"""
    
    def __init__(self, tension_manager: Optional[UnifiedTensionManager] = None):
        self.tension_manager = tension_manager or UnifiedTensionManager()
        self.integration_active = True
        self.faction_relationships: Dict[str, FactionRelationship] = {}
        self.diplomatic_cache: Dict[str, DiplomaticModifiers] = {}
        
        # Diplomatic parameters
        self.relationship_sensitivity = 1.2  # How much tension affects relationships
        self.trust_erosion_rate = 0.8  # How quickly trust erodes in high tension
        self.alliance_stability_threshold = 0.6  # Tension level that threatens alliances
        
        # Diplomatic thresholds
        self.war_declaration_threshold = 0.9  # Tension level that triggers war
        self.alliance_break_threshold = 0.7  # Tension level that breaks alliances
        self.hostility_threshold = 0.5  # Tension level that creates hostility
        
        # Response timing
        self.diplomatic_response_delay = timedelta(hours=6)  # Time before diplomatic responses
        self.relationship_update_interval = timedelta(hours=1)  # How often to update relationships
        
        # Register for tension and faction events
        self._register_diplomatic_handlers()
        
        logger.info("Faction-Tension integration initialized")
    
    def _register_diplomatic_handlers(self) -> None:
        """Register event handlers for diplomatic responses to tension"""
        event_bus.subscribe("tension:major_change", self._handle_tension_diplomatic_impact)
        event_bus.subscribe("tension:conflict_triggered", self._handle_conflict_diplomatic_impact)
        event_bus.subscribe("faction:relationship_query", self._handle_relationship_query)
        event_bus.subscribe("faction:diplomatic_action", self._handle_diplomatic_action)
        event_bus.subscribe("tension:peace_established", self._handle_peace_diplomatic_impact)
    
    def get_diplomatic_modifiers(self, region_id: str, involved_factions: List[str] = None) -> DiplomaticModifiers:
        """Get diplomatic modifiers for a region based on tension"""
        try:
            # Get current tension
            current_tension = self.tension_manager.calculate_tension(region_id, 'default')
            
            # Get factions in region if not provided
            if involved_factions is None:
                involved_factions = self._get_factions_in_region(region_id)
            
            # Calculate relationship changes
            relationship_changes = self._calculate_relationship_changes(current_tension, involved_factions, region_id)
            
            # Determine automatic diplomatic actions
            automatic_actions = self._determine_automatic_actions(current_tension, involved_factions, region_id)
            
            # Calculate reputation adjustments
            reputation_adjustments = self._calculate_reputation_adjustments(current_tension, involved_factions, region_id)
            
            # Calculate alliance stability effects
            alliance_stability = self._calculate_alliance_stability(current_tension, involved_factions)
            
            # Calculate trade penalties
            trade_penalties = self._calculate_trade_penalties(current_tension, involved_factions)
            
            # Calculate border tensions
            border_tensions = self._calculate_border_tensions(current_tension, region_id, involved_factions)
            
            modifiers = DiplomaticModifiers(
                relationship_changes=relationship_changes,
                automatic_actions=automatic_actions,
                reputation_adjustments=reputation_adjustments,
                alliance_stability=alliance_stability,
                trade_penalties=trade_penalties,
                border_tensions=border_tensions
            )
            
            # Cache for performance
            cache_key = f"{region_id}:{':'.join(sorted(involved_factions))}"
            self.diplomatic_cache[cache_key] = modifiers
            
            logger.debug(f"Diplomatic modifiers for {region_id}: {len(automatic_actions)} actions")
            
            return modifiers
            
        except Exception as e:
            logger.error(f"Error calculating diplomatic modifiers: {e}")
            return self._get_default_diplomatic_modifiers()
    
    def update_faction_relationship(self, faction_a: str, faction_b: str, 
                                  tension_level: float, event_context: str = None) -> FactionRelationship:
        """Update relationship between two factions based on tension"""
        try:
            relationship_key = self._get_relationship_key(faction_a, faction_b)
            
            # Get existing relationship or create new one
            if relationship_key in self.faction_relationships:
                relationship = self.faction_relationships[relationship_key]
            else:
                relationship = self._create_default_relationship(faction_a, faction_b)
            
            # Calculate tension impact on relationship
            tension_impact = self._calculate_tension_impact_on_relationship(
                relationship, tension_level, event_context
            )
            
            # Update relationship score
            old_score = relationship.relationship_score
            relationship.relationship_score += tension_impact
            relationship.relationship_score = max(-1.0, min(1.0, relationship.relationship_score))
            
            # Update relationship status based on new score
            relationship.relationship_status = self._determine_relationship_status(relationship.relationship_score)
            
            # Update trust level
            relationship.trust_level = self._calculate_trust_level(relationship, tension_level)
            
            # Add event to history
            if event_context:
                relationship.recent_events.append(f"{datetime.utcnow().isoformat()}: {event_context}")
                # Keep only recent events (last 10)
                relationship.recent_events = relationship.recent_events[-10:]
            
            # Update metadata
            relationship.last_modified = datetime.utcnow()
            relationship.tension_impact = tension_level
            
            # Store updated relationship
            self.faction_relationships[relationship_key] = relationship
            
            # Emit relationship change event if significant
            if abs(relationship.relationship_score - old_score) > 0.1:
                event_bus.emit("faction:relationship_changed", {
                    'faction_a': faction_a,
                    'faction_b': faction_b,
                    'old_score': old_score,
                    'new_score': relationship.relationship_score,
                    'old_status': self._determine_relationship_status(old_score).value,
                    'new_status': relationship.relationship_status.value,
                    'tension_level': tension_level,
                    'context': event_context
                })
            
            logger.info(f"Updated relationship {faction_a}-{faction_b}: {relationship.relationship_status.value} ({relationship.relationship_score:.2f})")
            
            return relationship
            
        except Exception as e:
            logger.error(f"Error updating faction relationship: {e}")
            return self._create_default_relationship(faction_a, faction_b)
    
    def calculate_faction_response(self, faction_id: str, region_id: str, 
                                 tension_level: float, tension_source: str = None) -> FactionTensionResponse:
        """Calculate how a faction responds to regional tension"""
        try:
            # Get faction's interests and capabilities in the region
            faction_interests = self._get_faction_interests(faction_id, region_id)
            faction_capabilities = self._get_faction_capabilities(faction_id, region_id)
            
            # Determine response type based on faction personality and tension
            response_type = self._determine_faction_response_type(faction_id, tension_level, faction_interests)
            
            # Calculate military posture
            military_posture = self._calculate_military_posture(faction_id, tension_level, response_type)
            
            # Determine diplomatic actions
            diplomatic_actions = self._determine_faction_diplomatic_actions(
                faction_id, tension_level, response_type, tension_source
            )
            
            # Calculate resource allocation changes
            resource_allocation = self._calculate_resource_allocation(
                faction_id, tension_level, response_type, faction_capabilities
            )
            
            # Generate public statements
            public_statements = self._generate_faction_statements(
                faction_id, tension_level, response_type, region_id
            )
            
            # Estimate response duration
            expected_duration = self._estimate_response_duration(tension_level, response_type)
            
            response = FactionTensionResponse(
                faction_id=faction_id,
                region_id=region_id,
                response_type=response_type,
                military_posture=military_posture,
                diplomatic_actions=diplomatic_actions,
                resource_allocation=resource_allocation,
                public_statements=public_statements,
                expected_duration=expected_duration
            )
            
            logger.info(f"Faction {faction_id} response to tension in {region_id}: {response_type}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error calculating faction response: {e}")
            return self._get_default_faction_response(faction_id, region_id)
    
    def process_diplomatic_cascade(self, initial_region: str, tension_change: float) -> List[Dict[str, Any]]:
        """Process cascade effects of tension changes on regional diplomacy"""
        try:
            cascade_effects = []
            
            # Get all factions involved in the region
            involved_factions = self._get_factions_in_region(initial_region)
            
            # Update relationships between involved factions
            for i, faction_a in enumerate(involved_factions):
                for faction_b in involved_factions[i+1:]:
                    relationship_change = self.update_faction_relationship(
                        faction_a, faction_b, tension_change, f"Regional tension in {initial_region}"
                    )
                    
                    cascade_effects.append({
                        'type': 'relationship_change',
                        'faction_a': faction_a,
                        'faction_b': faction_b,
                        'new_status': relationship_change.relationship_status.value,
                        'score_change': relationship_change.tension_impact
                    })
            
            # Calculate faction responses
            for faction_id in involved_factions:
                response = self.calculate_faction_response(faction_id, initial_region, tension_change)
                cascade_effects.append({
                    'type': 'faction_response',
                    'faction_id': faction_id,
                    'response_type': response.response_type,
                    'military_posture': response.military_posture,
                    'diplomatic_actions': [action.value for action in response.diplomatic_actions]
                })
            
            # Check for neighboring region effects
            neighboring_regions = self._get_neighboring_regions(initial_region)
            for neighbor_region in neighboring_regions:
                neighbor_tension_change = tension_change * 0.3  # Reduced effect on neighbors
                if neighbor_tension_change > 0.1:  # Only process significant cascades
                    neighbor_effects = self.process_diplomatic_cascade(neighbor_region, neighbor_tension_change)
                    cascade_effects.extend(neighbor_effects)
            
            logger.info(f"Processed diplomatic cascade: {len(cascade_effects)} effects")
            
            return cascade_effects
            
        except Exception as e:
            logger.error(f"Error processing diplomatic cascade: {e}")
            return []
    
    def apply_peace_treaty_effects(self, treaty_details: Dict[str, Any]) -> Dict[str, Any]:
        """Apply diplomatic effects of peace treaties on tension"""
        try:
            treaty_effects = {
                'treaty_id': treaty_details.get('treaty_id'),
                'signatory_factions': treaty_details.get('signatories', []),
                'affected_regions': treaty_details.get('regions', []),
                'diplomatic_changes': {},
                'tension_reductions': {},
                'applied_at': datetime.utcnow().isoformat()
            }
            
            signatories = treaty_details.get('signatories', [])
            affected_regions = treaty_details.get('regions', [])
            treaty_strength = treaty_details.get('strength', 0.5)  # 0.0 to 1.0
            
            # Improve relationships between signatories
            for i, faction_a in enumerate(signatories):
                for faction_b in signatories[i+1:]:
                    relationship = self.update_faction_relationship(
                        faction_a, faction_b, -treaty_strength * 0.5, 
                        f"Peace treaty signed: {treaty_details.get('name', 'Unnamed Treaty')}"
                    )
                    treaty_effects['diplomatic_changes'][f"{faction_a}-{faction_b}"] = {
                        'old_status': 'unknown',  # Would track this in real implementation
                        'new_status': relationship.relationship_status.value,
                        'improvement': treaty_strength * 0.5
                    }
            
            # Reduce tension in affected regions
            for region_id in affected_regions:
                tension_reduction = treaty_strength * 0.4  # Peace treaties reduce tension
                treaty_effects['tension_reductions'][region_id] = tension_reduction
                
                # Apply tension reduction (this would integrate with tension manager)
                event_bus.emit("tension:peace_treaty_applied", {
                    'region_id': region_id,
                    'tension_reduction': tension_reduction,
                    'treaty_details': treaty_details
                })
            
            # Emit treaty success event
            event_bus.emit("faction:peace_treaty_applied", treaty_effects)
            
            logger.info(f"Applied peace treaty effects: {len(signatories)} signatories, {len(affected_regions)} regions")
            
            return treaty_effects
            
        except Exception as e:
            logger.error(f"Error applying peace treaty effects: {e}")
            return {'error': str(e)}
    
    async def _handle_tension_diplomatic_impact(self, event_data: Dict[str, Any]) -> None:
        """Handle diplomatic impacts of tension changes"""
        try:
            region_id = event_data.get('region_id')
            new_tension = event_data.get('tension_level', 0.0)
            change_magnitude = event_data.get('change_magnitude', 0.0)
            
            # If significant tension change, process diplomatic cascade
            if change_magnitude > 0.15:
                cascade_effects = self.process_diplomatic_cascade(region_id, new_tension)
                
                # Emit diplomatic cascade event
                event_bus.emit("faction:diplomatic_cascade", {
                    'region_id': region_id,
                    'tension_level': new_tension,
                    'cascade_effects': cascade_effects
                })
            
        except Exception as e:
            logger.error(f"Error handling tension diplomatic impact: {e}")
    
    async def _handle_conflict_diplomatic_impact(self, event_data: Dict[str, Any]) -> None:
        """Handle diplomatic impacts of conflicts"""
        try:
            region_id = event_data.get('region_id')
            conflict_type = event_data.get('conflict_type')
            involved_factions = event_data.get('involved_factions', [])
            severity = event_data.get('severity', 1.0)
            
            # Break alliances if conflict is severe
            if severity > 0.8 and conflict_type in ['faction_war', 'civil_conflict']:
                for faction_id in involved_factions:
                    allies = self._get_faction_allies(faction_id)
                    for ally_id in allies:
                        alliance_stability = 1.0 - severity
                        if alliance_stability < 0.3:  # Alliance breaks
                            self.update_faction_relationship(
                                faction_id, ally_id, severity * 0.8,
                                f"Alliance broken due to {conflict_type}"
                            )
            
            # Trigger war declarations if tension extreme
            if severity > 0.9:
                for i, faction_a in enumerate(involved_factions):
                    for faction_b in involved_factions[i+1:]:
                        self.update_faction_relationship(
                            faction_a, faction_b, severity,
                            f"War declared due to {conflict_type}"
                        )
            
        except Exception as e:
            logger.error(f"Error handling conflict diplomatic impact: {e}")
    
    async def _handle_peace_diplomatic_impact(self, event_data: Dict[str, Any]) -> None:
        """Handle diplomatic improvements from peace establishment"""
        try:
            region_id = event_data.get('region_id')
            peace_strength = event_data.get('peace_strength', 0.5)
            
            # Improve relationships of factions in peaceful region
            involved_factions = self._get_factions_in_region(region_id)
            for i, faction_a in enumerate(involved_factions):
                for faction_b in involved_factions[i+1:]:
                    self.update_faction_relationship(
                        faction_a, faction_b, -peace_strength * 0.3,
                        f"Peace established in {region_id}"
                    )
            
        except Exception as e:
            logger.error(f"Error handling peace diplomatic impact: {e}")
    
    async def _handle_relationship_query(self, event_data: Dict[str, Any]) -> None:
        """Handle queries about faction relationships"""
        try:
            faction_a = event_data.get('faction_a')
            faction_b = event_data.get('faction_b')
            
            if faction_a and faction_b:
                relationship_key = self._get_relationship_key(faction_a, faction_b)
                relationship = self.faction_relationships.get(relationship_key)
                
                if relationship:
                    response = {
                        'faction_a': faction_a,
                        'faction_b': faction_b,
                        'relationship_status': relationship.relationship_status.value,
                        'relationship_score': relationship.relationship_score,
                        'trust_level': relationship.trust_level,
                        'recent_events': relationship.recent_events[-3:],  # Last 3 events
                        'last_modified': relationship.last_modified.isoformat()
                    }
                else:
                    response = {
                        'faction_a': faction_a,
                        'faction_b': faction_b,
                        'relationship_status': 'neutral',
                        'relationship_score': 0.0,
                        'message': 'No established relationship'
                    }
                
                event_bus.emit("faction:relationship_response", response)
            
        except Exception as e:
            logger.error(f"Error handling relationship query: {e}")
    
    async def _handle_diplomatic_action(self, event_data: Dict[str, Any]) -> None:
        """Handle diplomatic actions that might affect tension"""
        try:
            action_type = event_data.get('action_type')
            initiator = event_data.get('initiator_faction')
            target = event_data.get('target_faction')
            region_id = event_data.get('region_id')
            
            # Update relationships based on action
            if action_type == 'alliance_offer' and event_data.get('accepted'):
                self.update_faction_relationship(
                    initiator, target, -0.3, f"Alliance formed"
                )
            elif action_type == 'declare_war':
                self.update_faction_relationship(
                    initiator, target, 0.8, f"War declared"
                )
            elif action_type == 'peace_proposal' and event_data.get('accepted'):
                self.update_faction_relationship(
                    initiator, target, -0.4, f"Peace agreement"
                )
            
        except Exception as e:
            logger.error(f"Error handling diplomatic action: {e}")
    
    # Helper methods (implementation details)
    def _get_factions_in_region(self, region_id: str) -> List[str]:
        """Get factions with interests in a region"""
        # This would query actual faction data
        return ['faction_a', 'faction_b', 'faction_c']
    
    def _get_relationship_key(self, faction_a: str, faction_b: str) -> str:
        """Get consistent key for faction relationship"""
        return f"{min(faction_a, faction_b)}-{max(faction_a, faction_b)}"
    
    def _create_default_relationship(self, faction_a: str, faction_b: str) -> FactionRelationship:
        """Create default neutral relationship"""
        return FactionRelationship(
            faction_a=faction_a,
            faction_b=faction_b,
            relationship_status=FactionRelationshipStatus.NEUTRAL,
            relationship_score=0.0,
            tension_impact=0.0,
            diplomatic_immunity=False,
            last_modified=datetime.utcnow(),
            recent_events=[],
            trust_level=0.5,
            shared_interests=[],
            conflict_history=[]
        )
    
    def _determine_relationship_status(self, score: float) -> FactionRelationshipStatus:
        """Determine relationship status from score"""
        if score >= 0.7:
            return FactionRelationshipStatus.ALLIANCE
        elif score >= 0.3:
            return FactionRelationshipStatus.FRIENDLY
        elif score >= -0.3:
            return FactionRelationshipStatus.NEUTRAL
        elif score >= -0.7:
            return FactionRelationshipStatus.HOSTILE
        else:
            return FactionRelationshipStatus.WAR
    
    def _calculate_tension_impact_on_relationship(self, relationship: FactionRelationship, 
                                                tension_level: float, context: str) -> float:
        """Calculate how tension affects a specific relationship"""
        base_impact = tension_level * self.relationship_sensitivity
        
        # Adjust based on current relationship
        if relationship.relationship_status == FactionRelationshipStatus.ALLIANCE:
            return -base_impact * 0.5  # Alliances resist tension somewhat
        elif relationship.relationship_status == FactionRelationshipStatus.WAR:
            return base_impact * 0.3  # Already at war, less additional impact
        else:
            return base_impact
    
    def _calculate_trust_level(self, relationship: FactionRelationship, tension_level: float) -> float:
        """Calculate trust level between factions"""
        trust_erosion = tension_level * self.trust_erosion_rate * 0.1
        new_trust = relationship.trust_level - trust_erosion
        return max(0.0, min(1.0, new_trust))
    
    def _get_faction_interests(self, faction_id: str, region_id: str) -> Dict[str, float]:
        """Get faction's interests in a region"""
        return {'economic': 0.5, 'military': 0.3, 'political': 0.7}
    
    def _get_faction_capabilities(self, faction_id: str, region_id: str) -> Dict[str, float]:
        """Get faction's capabilities in a region"""
        return {'military_strength': 0.6, 'economic_power': 0.4, 'political_influence': 0.5}
    
    def _determine_faction_response_type(self, faction_id: str, tension_level: float, 
                                       interests: Dict[str, float]) -> str:
        """Determine how a faction responds to tension"""
        if tension_level > 0.8:
            return "crisis_response"
        elif tension_level > 0.6:
            return "defensive_posture"
        elif tension_level > 0.4:
            return "increased_vigilance"
        else:
            return "diplomatic_engagement"
    
    def _calculate_military_posture(self, faction_id: str, tension_level: float, 
                                  response_type: str) -> str:
        """Calculate faction's military posture"""
        if tension_level > 0.8:
            return "aggressive"
        elif tension_level > 0.6:
            return "defensive"
        elif tension_level > 0.3:
            return "alert"
        else:
            return "neutral"
    
    def _determine_faction_diplomatic_actions(self, faction_id: str, tension_level: float, 
                                            response_type: str, tension_source: str) -> List[DiplomaticAction]:
        """Determine diplomatic actions faction will take"""
        actions = []
        
        if tension_level > 0.8:
            actions.extend([DiplomaticAction.ULTIMATUM, DiplomaticAction.DECLARE_WAR])
        elif tension_level > 0.6:
            actions.extend([DiplomaticAction.DEMAND_WITHDRAWAL, DiplomaticAction.ALLIANCE_OFFER])
        elif tension_level > 0.3:
            actions.extend([DiplomaticAction.NON_AGGRESSION_PACT, DiplomaticAction.TRADE_AGREEMENT])
        else:
            actions.append(DiplomaticAction.PEACE_PROPOSAL)
        
        return actions
    
    def _calculate_resource_allocation(self, faction_id: str, tension_level: float, 
                                     response_type: str, capabilities: Dict[str, float]) -> Dict[str, float]:
        """Calculate how faction allocates resources in response to tension"""
        return {
            'military': min(1.0, 0.3 + tension_level * 0.5),
            'diplomacy': max(0.1, 0.4 - tension_level * 0.3),
            'intelligence': 0.2 + tension_level * 0.2,
            'economic': max(0.1, 0.4 - tension_level * 0.2)
        }
    
    def _generate_faction_statements(self, faction_id: str, tension_level: float, 
                                   response_type: str, region_id: str) -> List[str]:
        """Generate public statements faction makes"""
        statements = []
        
        if tension_level > 0.8:
            statements.append(f"{faction_id} condemns the escalating violence in {region_id}")
            statements.append(f"{faction_id} reserves the right to defend its interests")
        elif tension_level > 0.5:
            statements.append(f"{faction_id} calls for restraint in {region_id}")
            statements.append(f"{faction_id} increases security measures")
        else:
            statements.append(f"{faction_id} supports peaceful resolution in {region_id}")
        
        return statements
    
    def _estimate_response_duration(self, tension_level: float, response_type: str) -> Optional[timedelta]:
        """Estimate how long faction response will last"""
        if tension_level > 0.8:
            return timedelta(weeks=4)
        elif tension_level > 0.5:
            return timedelta(weeks=2)
        else:
            return timedelta(days=7)
    
    def _get_neighboring_regions(self, region_id: str) -> List[str]:
        """Get neighboring regions"""
        return [f"{region_id}_neighbor_1", f"{region_id}_neighbor_2"]
    
    def _get_faction_allies(self, faction_id: str) -> List[str]:
        """Get faction's current allies"""
        allies = []
        for key, relationship in self.faction_relationships.items():
            if (relationship.faction_a == faction_id or relationship.faction_b == faction_id) and \
               relationship.relationship_status == FactionRelationshipStatus.ALLIANCE:
                other_faction = relationship.faction_b if relationship.faction_a == faction_id else relationship.faction_a
                allies.append(other_faction)
        return allies
    
    def _calculate_relationship_changes(self, tension: float, factions: List[str], region_id: str) -> Dict[str, float]:
        """Calculate relationship changes for all faction pairs"""
        changes = {}
        for i, faction_a in enumerate(factions):
            for faction_b in factions[i+1:]:
                key = f"{faction_a}-{faction_b}"
                changes[key] = tension * self.relationship_sensitivity * -0.1  # Tension worsens relationships
        return changes
    
    def _determine_automatic_actions(self, tension: float, factions: List[str], region_id: str) -> List[DiplomaticAction]:
        """Determine automatic diplomatic actions triggered by tension"""
        actions = []
        
        if tension > self.war_declaration_threshold:
            actions.append(DiplomaticAction.DECLARE_WAR)
        elif tension > self.alliance_break_threshold:
            actions.append(DiplomaticAction.BREAK_ALLIANCE)
        elif tension > self.hostility_threshold:
            actions.append(DiplomaticAction.DEMAND_WITHDRAWAL)
        
        return actions
    
    def _calculate_reputation_adjustments(self, tension: float, factions: List[str], region_id: str) -> Dict[str, float]:
        """Calculate reputation adjustments for factions"""
        adjustments = {}
        for faction_id in factions:
            # Factions lose reputation in high-tension regions they're involved in
            adjustments[faction_id] = -tension * 0.2
        return adjustments
    
    def _calculate_alliance_stability(self, tension: float, factions: List[str]) -> Dict[str, float]:
        """Calculate stability of alliances under tension"""
        stability = {}
        # This would check actual alliances and calculate their stability
        stability['sample_alliance'] = max(0.0, 1.0 - tension)
        return stability
    
    def _calculate_trade_penalties(self, tension: float, factions: List[str]) -> Dict[str, float]:
        """Calculate trade penalties between faction pairs"""
        penalties = {}
        for i, faction_a in enumerate(factions):
            for faction_b in factions[i+1:]:
                key = f"{faction_a}-{faction_b}"
                penalties[key] = 1.0 + (tension * 0.5)  # Higher tension = higher trade costs
        return penalties
    
    def _calculate_border_tensions(self, tension: float, region_id: str, factions: List[str]) -> Dict[str, float]:
        """Calculate border tension effects"""
        border_tensions = {}
        neighbors = self._get_neighboring_regions(region_id)
        for neighbor in neighbors:
            border_tensions[f"{region_id}-{neighbor}"] = tension * 0.3  # Tension spreads to borders
        return border_tensions
    
    def _get_default_diplomatic_modifiers(self) -> DiplomaticModifiers:
        """Get default diplomatic modifiers when calculation fails"""
        return DiplomaticModifiers(
            relationship_changes={},
            automatic_actions=[],
            reputation_adjustments={},
            alliance_stability={},
            trade_penalties={},
            border_tensions={}
        )
    
    def _get_default_faction_response(self, faction_id: str, region_id: str) -> FactionTensionResponse:
        """Get default faction response when calculation fails"""
        return FactionTensionResponse(
            faction_id=faction_id,
            region_id=region_id,
            response_type="neutral",
            military_posture="neutral",
            diplomatic_actions=[],
            resource_allocation={'military': 0.3, 'diplomacy': 0.4, 'intelligence': 0.2, 'economic': 0.1},
            public_statements=[f"{faction_id} monitors situation in {region_id}"],
            expected_duration=timedelta(days=1)
        )
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            'integration_active': self.integration_active,
            'tracked_relationships': len(self.faction_relationships),
            'cached_diplomatic_modifiers': len(self.diplomatic_cache),
            'relationship_sensitivity': self.relationship_sensitivity,
            'thresholds': {
                'war_declaration': self.war_declaration_threshold,
                'alliance_break': self.alliance_break_threshold,
                'hostility': self.hostility_threshold
            }
        } 