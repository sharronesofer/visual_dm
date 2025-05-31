"""
Faction Influence Service

Handles faction control, influence mechanics, and political dynamics
affecting Points of Interest in the POI system.
"""

from typing import Dict, List, Optional, Tuple, Set, Any
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta
import random
import math

from backend.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db
from backend.infrastructure.events import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class InfluenceType(str, Enum):
    """Types of faction influence"""
    MILITARY = "military"           # Direct military control
    ECONOMIC = "economic"          # Trade and economic influence
    CULTURAL = "cultural"          # Cultural and religious influence
    POLITICAL = "political"        # Political and diplomatic influence
    COVERT = "covert"             # Spy networks and subterfuge
    MAGICAL = "magical"           # Magical influence and control


class FactionRelation(str, Enum):
    """Relations between factions"""
    ALLIED = "allied"             # Strong positive relationship
    FRIENDLY = "friendly"         # Positive relationship
    NEUTRAL = "neutral"          # No strong relationship
    UNFRIENDLY = "unfriendly"    # Negative relationship
    HOSTILE = "hostile"          # Strong negative relationship
    AT_WAR = "at_war"           # Active warfare


class InfluenceAction(str, Enum):
    """Actions factions can take to influence POIs"""
    ESTABLISH_PRESENCE = "establish_presence"
    EXPAND_INFLUENCE = "expand_influence"
    UNDERMINE_RIVALS = "undermine_rivals"
    FORTIFY_CONTROL = "fortify_control"
    LAUNCH_CAMPAIGN = "launch_campaign"
    NEGOTIATE_TREATY = "negotiate_treaty"
    SPY_OPERATION = "spy_operation"
    CULTURAL_CONVERSION = "cultural_conversion"
    TRADE_EMBARGO = "trade_embargo"
    DIPLOMATIC_PRESSURE = "diplomatic_pressure"


class ControlLevel(str, Enum):
    """Levels of faction control over a POI"""
    NONE = "none"                # No control (0-10%)
    MINIMAL = "minimal"          # Minimal presence (10-25%)
    MINOR = "minor"             # Minor influence (25-40%)
    MODERATE = "moderate"       # Moderate control (40-60%)
    MAJOR = "major"             # Major control (60-80%)
    DOMINANT = "dominant"       # Dominant control (80-95%)
    ABSOLUTE = "absolute"       # Complete control (95-100%)


@dataclass
class Faction:
    """Represents a faction in the game world"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    faction_type: str = "kingdom"  # kingdom, merchant_guild, religious_order, etc.
    color: str = "#FFFFFF"  # Hex color for UI representation
    emblem: str = ""
    leader: str = ""
    capital_poi_id: Optional[UUID] = None
    
    # Faction characteristics
    military_strength: float = 0.5   # 0.0 to 1.0
    economic_power: float = 0.5      # 0.0 to 1.0
    cultural_influence: float = 0.5   # 0.0 to 1.0
    magical_affinity: float = 0.5    # 0.0 to 1.0
    diplomatic_skill: float = 0.5    # 0.0 to 1.0
    
    # Resources and capabilities
    treasury: int = 1000
    armies: int = 1
    spies: int = 0
    trade_routes: List[UUID] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    founded_date: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FactionInfluence:
    """Represents a faction's influence over a specific POI"""
    faction_id: UUID
    poi_id: UUID
    influence_type: InfluenceType
    strength: float = 0.0  # 0.0 to 1.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    established_date: datetime = field(default_factory=datetime.utcnow)
    actions_taken: List[str] = field(default_factory=list)
    
    def get_control_level(self) -> ControlLevel:
        """Get the control level based on influence strength"""
        if self.strength < 0.1:
            return ControlLevel.NONE
        elif self.strength < 0.25:
            return ControlLevel.MINIMAL
        elif self.strength < 0.4:
            return ControlLevel.MINOR
        elif self.strength < 0.6:
            return ControlLevel.MODERATE
        elif self.strength < 0.8:
            return ControlLevel.MAJOR
        elif self.strength < 0.95:
            return ControlLevel.DOMINANT
        else:
            return ControlLevel.ABSOLUTE


@dataclass
class FactionRelationship:
    """Represents relationship between two factions"""
    faction_a_id: UUID
    faction_b_id: UUID
    relation: FactionRelation = FactionRelation.NEUTRAL
    strength: float = 0.0  # -1.0 (hostile) to 1.0 (allied)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    treaties: List[str] = field(default_factory=list)
    trade_agreements: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    
    def update_relation_from_strength(self):
        """Update relation enum based on strength value"""
        if self.strength >= 0.8:
            self.relation = FactionRelation.ALLIED
        elif self.strength >= 0.4:
            self.relation = FactionRelation.FRIENDLY
        elif self.strength >= -0.4:
            self.relation = FactionRelation.NEUTRAL
        elif self.strength >= -0.8:
            self.relation = FactionRelation.UNFRIENDLY
        else:
            self.relation = FactionRelation.HOSTILE


@dataclass
class InfluenceEvent:
    """Represents an event affecting faction influence"""
    id: UUID = field(default_factory=uuid4)
    faction_id: UUID = field(default_factory=uuid4)
    poi_id: UUID = field(default_factory=uuid4)
    action: InfluenceAction = InfluenceAction.ESTABLISH_PRESENCE
    success: bool = False
    influence_change: float = 0.0
    cost: int = 0
    description: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class FactionInfluenceService:
    """Service for managing faction influence and political dynamics"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db()
        self.event_dispatcher = EventDispatcher()
        
        # Faction and influence data
        self.factions: Dict[UUID, Faction] = {}
        self.poi_influences: Dict[UUID, Dict[UUID, FactionInfluence]] = {}  # poi_id -> faction_id -> influence
        self.faction_relationships: Dict[Tuple[UUID, UUID], FactionRelationship] = {}
        self.influence_events: List[InfluenceEvent] = []
        
        # Configuration
        self.daily_influence_decay = 0.01  # 1% daily decay without maintenance
        self.max_influence_actions_per_day = 2
        self.influence_action_costs = {
            InfluenceAction.ESTABLISH_PRESENCE: 100,
            InfluenceAction.EXPAND_INFLUENCE: 200,
            InfluenceAction.UNDERMINE_RIVALS: 300,
            InfluenceAction.FORTIFY_CONTROL: 250,
            InfluenceAction.LAUNCH_CAMPAIGN: 500,
            InfluenceAction.SPY_OPERATION: 150,
            InfluenceAction.CULTURAL_CONVERSION: 300,
            InfluenceAction.TRADE_EMBARGO: 200,
            InfluenceAction.DIPLOMATIC_PRESSURE: 100
        }
    
    def create_faction(self, name: str, faction_type: str = "kingdom", 
                      capital_poi_id: Optional[UUID] = None, 
                      characteristics: Dict[str, float] = None) -> Faction:
        """Create a new faction"""
        try:
            faction = Faction(
                name=name,
                faction_type=faction_type,
                capital_poi_id=capital_poi_id,
                color=f"#{random.randint(0, 0xFFFFFF):06x}"  # Random color
            )
            
            # Apply custom characteristics
            if characteristics:
                faction.military_strength = characteristics.get('military_strength', faction.military_strength)
                faction.economic_power = characteristics.get('economic_power', faction.economic_power)
                faction.cultural_influence = characteristics.get('cultural_influence', faction.cultural_influence)
                faction.magical_affinity = characteristics.get('magical_affinity', faction.magical_affinity)
                faction.diplomatic_skill = characteristics.get('diplomatic_skill', faction.diplomatic_skill)
            
            self.factions[faction.id] = faction
            
            # If capital is specified, establish strong influence there
            if capital_poi_id:
                self.establish_influence(faction.id, capital_poi_id, InfluenceType.POLITICAL, 0.9)
            
            logger.info(f"Created faction: {name} ({faction.id})")
            
            # Dispatch faction creation event
            self.event_dispatcher.publish({
                'type': 'faction_created',
                'faction_id': str(faction.id),
                'name': name,
                'faction_type': faction_type,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return faction
            
        except Exception as e:
            logger.error(f"Error creating faction: {e}")
            return None
    
    def establish_influence(self, faction_id: UUID, poi_id: UUID, 
                           influence_type: InfluenceType, initial_strength: float = 0.1) -> bool:
        """Establish faction influence over a POI"""
        try:
            if poi_id not in self.poi_influences:
                self.poi_influences[poi_id] = {}
            
            # Check if influence already exists
            if faction_id in self.poi_influences[poi_id]:
                existing = self.poi_influences[poi_id][faction_id]
                if existing.influence_type == influence_type:
                    # Strengthen existing influence
                    existing.strength = min(1.0, existing.strength + initial_strength)
                    existing.last_updated = datetime.utcnow()
                    return True
            
            # Create new influence
            influence = FactionInfluence(
                faction_id=faction_id,
                poi_id=poi_id,
                influence_type=influence_type,
                strength=initial_strength
            )
            
            self.poi_influences[poi_id][faction_id] = influence
            
            # Dispatch influence established event
            self.event_dispatcher.publish({
                'type': 'faction_influence_established',
                'faction_id': str(faction_id),
                'poi_id': str(poi_id),
                'influence_type': influence_type.value,
                'strength': initial_strength,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error establishing influence: {e}")
            return False
    
    def execute_influence_action(self, faction_id: UUID, poi_id: UUID, 
                                action: InfluenceAction, target_faction_id: Optional[UUID] = None) -> InfluenceEvent:
        """Execute a faction influence action"""
        try:
            faction = self.factions.get(faction_id)
            if not faction:
                return None
            
            # Check if faction can afford the action
            cost = self.influence_action_costs.get(action, 100)
            if faction.treasury < cost:
                logger.warning(f"Faction {faction_id} cannot afford action {action}")
                return None
            
            # Execute the action
            event = InfluenceEvent(
                faction_id=faction_id,
                poi_id=poi_id,
                action=action,
                cost=cost
            )
            
            success_chance = self._calculate_action_success_chance(faction, poi_id, action, target_faction_id)
            event.success = random.random() < success_chance
            
            if event.success:
                influence_change = self._calculate_influence_change(faction, action, event.success)
                event.influence_change = influence_change
                
                # Apply influence change
                self._apply_influence_change(faction_id, poi_id, influence_change, action)
                
                # Deduct cost
                faction.treasury -= cost
                
                event.description = f"Successfully executed {action.value} at POI {poi_id}"
            else:
                # Failed actions may still have some cost or consequences
                faction.treasury -= cost // 2  # Half cost for failed attempts
                event.description = f"Failed to execute {action.value} at POI {poi_id}"
            
            self.influence_events.append(event)
            
            # Dispatch influence action event
            self.event_dispatcher.publish({
                'type': 'faction_influence_action',
                'faction_id': str(faction_id),
                'poi_id': str(poi_id),
                'action': action.value,
                'success': event.success,
                'influence_change': event.influence_change,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return event
            
        except Exception as e:
            logger.error(f"Error executing influence action: {e}")
            return None
    
    def process_daily_influence(self) -> Dict[str, Any]:
        """Process daily influence changes and decay"""
        try:
            results = {
                'factions_processed': 0,
                'pois_processed': 0,
                'influence_decayed': 0,
                'conflicts_resolved': 0
            }
            
            # Process influence decay
            for poi_id, faction_influences in self.poi_influences.items():
                for faction_id, influence in faction_influences.items():
                    # Apply daily decay
                    old_strength = influence.strength
                    influence.strength = max(0.0, influence.strength - self.daily_influence_decay)
                    
                    if influence.strength < old_strength:
                        results['influence_decayed'] += 1
                    
                    influence.last_updated = datetime.utcnow()
                
                results['pois_processed'] += 1
            
            # Process faction actions and conflicts
            for faction_id, faction in self.factions.items():
                if not faction.is_active:
                    continue
                
                # AI-driven faction actions (simplified)
                self._process_ai_faction_actions(faction)
                results['factions_processed'] += 1
            
            # Clean up zero influences
            self._cleanup_zero_influences()
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing daily influence: {e}")
            return {'error': str(e)}
    
    def get_poi_control_status(self, poi_id: UUID) -> Dict[str, Any]:
        """Get complete control status for a POI"""
        try:
            poi_influences = self.poi_influences.get(poi_id, {})
            
            if not poi_influences:
                return {
                    'dominant_faction': None,
                    'control_level': ControlLevel.NONE.value,
                    'total_influences': 0,
                    'influences': []
                }
            
            # Find dominant faction
            dominant_faction_id = None
            max_strength = 0.0
            
            influences = []
            for faction_id, influence in poi_influences.items():
                faction = self.factions.get(faction_id)
                if faction:
                    influence_data = {
                        'faction_id': str(faction_id),
                        'faction_name': faction.name,
                        'influence_type': influence.influence_type.value,
                        'strength': influence.strength,
                        'control_level': influence.get_control_level().value
                    }
                    influences.append(influence_data)
                    
                    if influence.strength > max_strength:
                        max_strength = influence.strength
                        dominant_faction_id = faction_id
            
            # Sort by strength
            influences.sort(key=lambda x: x['strength'], reverse=True)
            
            dominant_faction = self.factions.get(dominant_faction_id) if dominant_faction_id else None
            
            return {
                'dominant_faction': {
                    'id': str(dominant_faction_id),
                    'name': dominant_faction.name,
                    'strength': max_strength
                } if dominant_faction else None,
                'control_level': ControlLevel.NONE.value if max_strength < 0.1 else influences[0]['control_level'],
                'total_influences': len(influences),
                'influences': influences
            }
            
        except Exception as e:
            logger.error(f"Error getting POI control status: {e}")
            return {}
    
    def get_faction_influence_summary(self, faction_id: UUID) -> Dict[str, Any]:
        """Get summary of a faction's influence across all POIs"""
        try:
            faction = self.factions.get(faction_id)
            if not faction:
                return {}
            
            controlled_pois = []
            total_influence = 0.0
            influence_by_type = {}
            
            for poi_id, faction_influences in self.poi_influences.items():
                if faction_id in faction_influences:
                    influence = faction_influences[faction_id]
                    
                    controlled_pois.append({
                        'poi_id': str(poi_id),
                        'influence_type': influence.influence_type.value,
                        'strength': influence.strength,
                        'control_level': influence.get_control_level().value
                    })
                    
                    total_influence += influence.strength
                    
                    # Track by type
                    inf_type = influence.influence_type.value
                    if inf_type not in influence_by_type:
                        influence_by_type[inf_type] = 0
                    influence_by_type[inf_type] += influence.strength
            
            return {
                'faction_id': str(faction_id),
                'faction_name': faction.name,
                'total_controlled_pois': len(controlled_pois),
                'total_influence_strength': total_influence,
                'average_influence': total_influence / len(controlled_pois) if controlled_pois else 0,
                'influence_by_type': influence_by_type,
                'controlled_pois': controlled_pois,
                'treasury': faction.treasury,
                'military_strength': faction.military_strength,
                'economic_power': faction.economic_power
            }
            
        except Exception as e:
            logger.error(f"Error getting faction influence summary: {e}")
            return {}
    
    def set_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID, 
                                relation: FactionRelation, strength: float = None) -> bool:
        """Set relationship between two factions"""
        try:
            # Ensure consistent ordering
            if faction_a_id > faction_b_id:
                faction_a_id, faction_b_id = faction_b_id, faction_a_id
            
            relationship_key = (faction_a_id, faction_b_id)
            
            if relationship_key not in self.faction_relationships:
                self.faction_relationships[relationship_key] = FactionRelationship(
                    faction_a_id=faction_a_id,
                    faction_b_id=faction_b_id
                )
            
            relationship = self.faction_relationships[relationship_key]
            relationship.relation = relation
            
            if strength is not None:
                relationship.strength = max(-1.0, min(1.0, strength))
            else:
                # Set default strength based on relation
                strength_map = {
                    FactionRelation.ALLIED: 0.8,
                    FactionRelation.FRIENDLY: 0.4,
                    FactionRelation.NEUTRAL: 0.0,
                    FactionRelation.UNFRIENDLY: -0.4,
                    FactionRelation.HOSTILE: -0.8,
                    FactionRelation.AT_WAR: -1.0
                }
                relationship.strength = strength_map.get(relation, 0.0)
            
            relationship.last_updated = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting faction relationship: {e}")
            return False
    
    def _calculate_action_success_chance(self, faction: Faction, poi_id: UUID, 
                                       action: InfluenceAction, target_faction_id: Optional[UUID] = None) -> float:
        """Calculate success chance for an influence action"""
        base_chance = 0.5
        
        # Factor in faction characteristics
        if action in [InfluenceAction.LAUNCH_CAMPAIGN, InfluenceAction.FORTIFY_CONTROL]:
            base_chance += faction.military_strength * 0.3
        elif action in [InfluenceAction.ESTABLISH_PRESENCE, InfluenceAction.EXPAND_INFLUENCE]:
            base_chance += faction.economic_power * 0.2
            base_chance += faction.diplomatic_skill * 0.2
        elif action == InfluenceAction.SPY_OPERATION:
            base_chance += faction.diplomatic_skill * 0.4
        elif action == InfluenceAction.CULTURAL_CONVERSION:
            base_chance += faction.cultural_influence * 0.4
        
        # Factor in existing influence
        existing_influence = self.poi_influences.get(poi_id, {}).get(faction.id)
        if existing_influence:
            base_chance += existing_influence.strength * 0.2
        
        # Factor in opposition
        if target_faction_id and poi_id in self.poi_influences:
            target_influence = self.poi_influences[poi_id].get(target_faction_id)
            if target_influence:
                base_chance -= target_influence.strength * 0.3
        
        return max(0.1, min(0.9, base_chance))
    
    def _calculate_influence_change(self, faction: Faction, action: InfluenceAction, success: bool) -> float:
        """Calculate influence change from an action"""
        if not success:
            return 0.0
        
        base_change = {
            InfluenceAction.ESTABLISH_PRESENCE: 0.1,
            InfluenceAction.EXPAND_INFLUENCE: 0.15,
            InfluenceAction.UNDERMINE_RIVALS: -0.1,  # Reduces rival influence
            InfluenceAction.FORTIFY_CONTROL: 0.05,
            InfluenceAction.LAUNCH_CAMPAIGN: 0.25,
            InfluenceAction.SPY_OPERATION: 0.08,
            InfluenceAction.CULTURAL_CONVERSION: 0.12,
            InfluenceAction.DIPLOMATIC_PRESSURE: 0.06
        }.get(action, 0.05)
        
        # Factor in faction characteristics
        multiplier = 1.0
        if action in [InfluenceAction.LAUNCH_CAMPAIGN, InfluenceAction.FORTIFY_CONTROL]:
            multiplier += faction.military_strength * 0.5
        elif action in [InfluenceAction.ESTABLISH_PRESENCE, InfluenceAction.EXPAND_INFLUENCE]:
            multiplier += faction.economic_power * 0.3
        
        return base_change * multiplier
    
    def _apply_influence_change(self, faction_id: UUID, poi_id: UUID, 
                               influence_change: float, action: InfluenceAction):
        """Apply influence change to POI"""
        try:
            if poi_id not in self.poi_influences:
                self.poi_influences[poi_id] = {}
            
            # Apply positive influence to faction
            if influence_change > 0:
                if faction_id not in self.poi_influences[poi_id]:
                    # Determine influence type based on action
                    influence_type = InfluenceType.POLITICAL
                    if action in [InfluenceAction.LAUNCH_CAMPAIGN, InfluenceAction.FORTIFY_CONTROL]:
                        influence_type = InfluenceType.MILITARY
                    elif action in [InfluenceAction.CULTURAL_CONVERSION]:
                        influence_type = InfluenceType.CULTURAL
                    elif action in [InfluenceAction.SPY_OPERATION]:
                        influence_type = InfluenceType.COVERT
                    
                    self.establish_influence(faction_id, poi_id, influence_type, influence_change)
                else:
                    influence = self.poi_influences[poi_id][faction_id]
                    influence.strength = min(1.0, influence.strength + influence_change)
                    influence.last_updated = datetime.utcnow()
            
            # Apply negative influence (undermining) to rivals
            elif action == InfluenceAction.UNDERMINE_RIVALS:
                for other_faction_id, influence in self.poi_influences[poi_id].items():
                    if other_faction_id != faction_id:
                        influence.strength = max(0.0, influence.strength + influence_change)  # influence_change is negative
                        influence.last_updated = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error applying influence change: {e}")
    
    def _process_ai_faction_actions(self, faction: Faction):
        """Process AI-driven faction actions (simplified)"""
        try:
            # Simple AI: factions try to expand influence to nearby POIs
            if faction.treasury < 200:
                return  # Not enough resources for actions
            
            # Find POIs where faction has some influence
            influenced_pois = []
            for poi_id, faction_influences in self.poi_influences.items():
                if faction.id in faction_influences:
                    influenced_pois.append(poi_id)
            
            if influenced_pois:
                # Randomly choose to expand influence at one POI
                target_poi = random.choice(influenced_pois)
                action = random.choice([
                    InfluenceAction.EXPAND_INFLUENCE,
                    InfluenceAction.FORTIFY_CONTROL
                ])
                
                self.execute_influence_action(faction.id, target_poi, action)
            
        except Exception as e:
            logger.error(f"Error processing AI faction actions: {e}")
    
    def _cleanup_zero_influences(self):
        """Remove influences with zero strength"""
        try:
            for poi_id, faction_influences in list(self.poi_influences.items()):
                for faction_id, influence in list(faction_influences.items()):
                    if influence.strength <= 0.0:
                        del faction_influences[faction_id]
                
                if not faction_influences:
                    del self.poi_influences[poi_id]
            
        except Exception as e:
            logger.error(f"Error cleaning up zero influences: {e}")


# Factory function for dependency injection
def get_faction_influence_service(db_session: Optional[Session] = None) -> FactionInfluenceService:
    """Factory function to create FactionInfluenceService instance"""
    return FactionInfluenceService(db_session) 