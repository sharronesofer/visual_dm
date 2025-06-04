"""
Landmark Service for POI System

Manages special landmarks, monuments, and significant locations within POIs,
including their cultural, historical, and gameplay significance.
"""

from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta
import random
import math

from backend.infrastructure.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db_session
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LandmarkType(str, Enum):
    """Types of landmarks"""
    ANCIENT_RUINS = "ancient_ruins"
    MAGICAL_SITE = "magical_site"
    NATURAL_WONDER = "natural_wonder"
    HISTORICAL_SITE = "historical_site"
    RELIGIOUS_SHRINE = "religious_shrine"
    STRATEGIC_LOCATION = "strategic_location"
    RESOURCE_NODE = "resource_node"
    PORTAL = "portal"
    DUNGEON = "dungeon"
    MONUMENT = "monument"
    BATTLEFIELD = "battlefield"
    GRAVEYARD = "graveyard"
    LIBRARY = "library"
    ACADEMY = "academy"
    OBSERVATORY = "observatory"


class LandmarkRarity(str, Enum):
    """Rarity levels for landmarks"""
    COMMON = "common"           # Found relatively frequently
    UNCOMMON = "uncommon"       # Moderately rare
    RARE = "rare"              # Quite rare
    EPIC = "epic"              # Very rare
    LEGENDARY = "legendary"     # Extremely rare
    MYTHIC = "mythic"          # Almost unique


class LandmarkStatus(str, Enum):
    """Status of landmarks"""
    UNDISCOVERED = "undiscovered"    # Not yet found
    DISCOVERED = "discovered"        # Found but not explored
    EXPLORED = "explored"           # Partially explored
    FULLY_MAPPED = "fully_mapped"   # Completely explored
    CLAIMED = "claimed"             # Claimed by faction
    CONTESTED = "contested"         # Multiple claims
    ABANDONED = "abandoned"         # Previously claimed, now empty
    CORRUPTED = "corrupted"         # Magically corrupted
    SEALED = "sealed"              # Magically or physically sealed


class LandmarkEffect(str, Enum):
    """Types of effects landmarks can provide"""
    RESOURCE_BONUS = "resource_bonus"
    DEFENSE_BONUS = "defense_bonus"
    MAGIC_AMPLIFICATION = "magic_amplification"
    KNOWLEDGE_ACCESS = "knowledge_access"
    TRAVEL_NETWORK = "travel_network"
    POPULATION_ATTRACTION = "population_attraction"
    TRADE_BONUS = "trade_bonus"
    CULTURAL_INFLUENCE = "cultural_influence"
    MILITARY_TRAINING = "military_training"
    HEALING = "healing"
    VISION = "vision"
    PROTECTION = "protection"
    CURSE = "curse"
    TRANSFORMATION = "transformation"


@dataclass
class LandmarkFeature:
    """Represents a special feature of a landmark"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    effect_type: LandmarkEffect = LandmarkEffect.RESOURCE_BONUS
    magnitude: float = 1.0  # Effect strength multiplier
    radius: float = 0.0  # Area of effect (0 = landmark only)
    duration: Optional[int] = None  # Duration in days (None = permanent)
    activation_requirements: List[str] = field(default_factory=list)
    active: bool = True
    discovered: bool = False
    
    def can_activate(self, context: Dict[str, Any]) -> bool:
        """Check if feature can be activated given context"""
        if not self.active or not self.discovered:
            return False
        
        for requirement in self.activation_requirements:
            if not self._check_requirement(requirement, context):
                return False
        
        return True
    
    def _check_requirement(self, requirement: str, context: Dict[str, Any]) -> bool:
        """Check if a specific requirement is met"""
        # Parse requirement string (simplified)
        if requirement.startswith("population:"):
            required_pop = int(requirement.split(":")[1])
            return context.get("population", 0) >= required_pop
        elif requirement.startswith("faction:"):
            required_faction = requirement.split(":")[1]
            return context.get("controlling_faction") == required_faction
        elif requirement.startswith("season:"):
            required_season = requirement.split(":")[1]
            return context.get("current_season") == required_season
        elif requirement.startswith("time:"):
            required_time = requirement.split(":")[1]
            return context.get("time_of_day") == required_time
        
        return True


@dataclass
class Landmark:
    """Represents a landmark POI with special properties"""
    id: UUID = field(default_factory=uuid4)
    poi_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    landmark_type: LandmarkType = LandmarkType.ANCIENT_RUINS
    rarity: LandmarkRarity = LandmarkRarity.COMMON
    status: LandmarkStatus = LandmarkStatus.UNDISCOVERED
    
    # Properties
    age: int = 1000  # Age in years
    origin_culture: str = "unknown"
    historical_significance: str = ""
    magical_resonance: float = 0.0  # 0.0 to 1.0
    
    # Features and effects
    features: List[LandmarkFeature] = field(default_factory=list)
    unique_resources: Dict[str, int] = field(default_factory=dict)
    
    # Discovery and exploration
    discovery_date: Optional[datetime] = None
    discovered_by: Optional[UUID] = None  # Faction or character ID
    exploration_progress: float = 0.0  # 0.0 to 1.0
    required_exploration_points: int = 100
    
    # Control and claims
    controlling_faction: Optional[UUID] = None
    contested_by: List[UUID] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def get_discovery_difficulty(self) -> float:
        """Calculate how difficult this landmark is to discover"""
        base_difficulty = {
            LandmarkRarity.COMMON: 0.2,
            LandmarkRarity.UNCOMMON: 0.4,
            LandmarkRarity.RARE: 0.6,
            LandmarkRarity.EPIC: 0.8,
            LandmarkRarity.LEGENDARY: 0.9,
            LandmarkRarity.MYTHIC: 0.95
        }.get(self.rarity, 0.5)
        
        # Modify based on type
        type_modifier = {
            LandmarkType.NATURAL_WONDER: -0.1,  # Easier to spot
            LandmarkType.ANCIENT_RUINS: 0.1,   # Hidden by time
            LandmarkType.MAGICAL_SITE: 0.2,    # Hidden by magic
            LandmarkType.DUNGEON: 0.3,         # Deliberately hidden
            LandmarkType.PORTAL: 0.25          # Unstable/hard to find
        }.get(self.landmark_type, 0.0)
        
        return min(0.99, max(0.01, base_difficulty + type_modifier))
    
    def get_active_effects(self, context: Dict[str, Any] = None) -> List[LandmarkFeature]:
        """Get currently active landmark effects"""
        context = context or {}
        return [f for f in self.features if f.can_activate(context)]


@dataclass
class LandmarkQuest:
    """Represents a quest or challenge associated with a landmark"""
    id: UUID = field(default_factory=uuid4)
    landmark_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    difficulty: float = 0.5  # 0.0 to 1.0
    time_limit: Optional[int] = None  # Days
    prerequisites: List[str] = field(default_factory=list)
    status: str = "available"  # available, active, completed, failed
    assigned_to: Optional[UUID] = None  # Faction or character
    created_at: datetime = field(default_factory=datetime.utcnow)


class LandmarkService:
    """Service for managing landmarks and their special properties"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        self.event_dispatcher = EventDispatcher()
        
        # Landmark data
        self.landmarks: Dict[UUID, Landmark] = {}
        self.landmark_quests: Dict[UUID, LandmarkQuest] = {}
        self.poi_landmarks: Dict[UUID, UUID] = {}  # poi_id -> landmark_id
        
        # Discovery and exploration tracking
        self.discovery_attempts: Dict[UUID, List[datetime]] = {}  # poi_id -> attempt dates
        self.exploration_teams: Dict[UUID, Dict[str, Any]] = {}  # landmark_id -> team info
        
        # Configuration
        self.base_discovery_chance = 0.05  # 5% chance per exploration attempt
        self.exploration_points_per_day = 10
        self.max_exploration_teams_per_landmark = 3
        
        # Initialize landmark templates
        self.landmark_templates = self._initialize_landmark_templates()
    
    def _initialize_landmark_templates(self) -> Dict[LandmarkType, Dict[str, Any]]:
        """Initialize templates for different landmark types"""
        return {
            LandmarkType.ANCIENT_RUINS: {
                'base_features': [
                    LandmarkFeature(
                        name="Ancient Knowledge",
                        description="Ruins contain scrolls and artifacts with ancient wisdom",
                        effect_type=LandmarkEffect.KNOWLEDGE_ACCESS,
                        magnitude=1.5
                    ),
                    LandmarkFeature(
                        name="Historical Resonance",
                        description="The site amplifies cultural influence",
                        effect_type=LandmarkEffect.CULTURAL_INFLUENCE,
                        magnitude=1.2,
                        radius=50.0
                    )
                ],
                'typical_age_range': (500, 3000),
                'exploration_difficulty': 0.6
            },
            
            LandmarkType.MAGICAL_SITE: {
                'base_features': [
                    LandmarkFeature(
                        name="Magical Amplification",
                        description="Magic is stronger in this area",
                        effect_type=LandmarkEffect.MAGIC_AMPLIFICATION,
                        magnitude=2.0,
                        radius=25.0
                    ),
                    LandmarkFeature(
                        name="Ley Line Node",
                        description="Connection point for magical travel",
                        effect_type=LandmarkEffect.TRAVEL_NETWORK,
                        magnitude=1.0,
                        activation_requirements=["faction:magic_users"]
                    )
                ],
                'typical_age_range': (100, 2000),
                'exploration_difficulty': 0.8
            },
            
            LandmarkType.NATURAL_WONDER: {
                'base_features': [
                    LandmarkFeature(
                        name="Natural Beauty",
                        description="Attracts visitors and settlers",
                        effect_type=LandmarkEffect.POPULATION_ATTRACTION,
                        magnitude=1.3,
                        radius=100.0
                    ),
                    LandmarkFeature(
                        name="Unique Resources",
                        description="Provides rare natural resources",
                        effect_type=LandmarkEffect.RESOURCE_BONUS,
                        magnitude=1.5
                    )
                ],
                'typical_age_range': (10000, 100000),
                'exploration_difficulty': 0.3
            },
            
            LandmarkType.STRATEGIC_LOCATION: {
                'base_features': [
                    LandmarkFeature(
                        name="Defensive Position",
                        description="Provides military advantages",
                        effect_type=LandmarkEffect.DEFENSE_BONUS,
                        magnitude=2.0,
                        radius=30.0
                    ),
                    LandmarkFeature(
                        name="Trade Crossroads",
                        description="Boosts trade and commerce",
                        effect_type=LandmarkEffect.TRADE_BONUS,
                        magnitude=1.4,
                        radius=75.0
                    )
                ],
                'typical_age_range': (0, 1000),
                'exploration_difficulty': 0.2
            },
            
            LandmarkType.DUNGEON: {
                'base_features': [
                    LandmarkFeature(
                        name="Hidden Treasures",
                        description="Contains valuable treasures and artifacts",
                        effect_type=LandmarkEffect.RESOURCE_BONUS,
                        magnitude=3.0,
                        activation_requirements=["exploration:complete"]
                    ),
                    LandmarkFeature(
                        name="Ancient Guardians",
                        description="Dangerous creatures protect the dungeon",
                        effect_type=LandmarkEffect.CURSE,
                        magnitude=0.8,
                        active=True
                    )
                ],
                'typical_age_range': (200, 2000),
                'exploration_difficulty': 0.9
            }
        }
    
    def create_landmark(self, poi_id: UUID, landmark_type: LandmarkType, 
                       rarity: LandmarkRarity = LandmarkRarity.COMMON,
                       custom_properties: Dict[str, Any] = None) -> Optional[Landmark]:
        """Create a new landmark at a POI"""
        try:
            # Check if POI already has a landmark
            if poi_id in self.poi_landmarks:
                logger.warning(f"POI {poi_id} already has a landmark")
                return None
            
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                logger.error(f"POI {poi_id} not found")
                return None
            
            # Get template
            template = self.landmark_templates.get(landmark_type, {})
            
            # Create landmark
            landmark = Landmark(
                poi_id=poi_id,
                name=f"{landmark_type.value.replace('_', ' ').title()} at {poi.name}",
                description=f"A {rarity.value} {landmark_type.value.replace('_', ' ')} with mysterious properties",
                landmark_type=landmark_type,
                rarity=rarity
            )
            
            # Set age
            age_range = template.get('typical_age_range', (100, 1000))
            landmark.age = random.randint(*age_range)
            
            # Add base features from template
            base_features = template.get('base_features', [])
            for feature_template in base_features:
                feature = LandmarkFeature(
                    name=feature_template.name,
                    description=feature_template.description,
                    effect_type=feature_template.effect_type,
                    magnitude=feature_template.magnitude * self._get_rarity_multiplier(rarity),
                    radius=feature_template.radius,
                    activation_requirements=feature_template.activation_requirements.copy()
                )
                landmark.features.append(feature)
            
            # Apply custom properties
            if custom_properties:
                for key, value in custom_properties.items():
                    if hasattr(landmark, key):
                        setattr(landmark, key, value)
            
            # Set exploration requirements based on difficulty
            exploration_difficulty = template.get('exploration_difficulty', 0.5)
            landmark.required_exploration_points = int(100 * exploration_difficulty * self._get_rarity_multiplier(rarity))
            
            # Store landmark
            self.landmarks[landmark.id] = landmark
            self.poi_landmarks[poi_id] = landmark.id
            
            # Dispatch landmark creation event
            self.event_dispatcher.publish({
                'type': 'landmark_created',
                'landmark_id': str(landmark.id),
                'poi_id': str(poi_id),
                'landmark_type': landmark_type.value,
                'rarity': rarity.value,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Created {rarity.value} {landmark_type.value} landmark at POI {poi_id}")
            return landmark
            
        except Exception as e:
            logger.error(f"Error creating landmark: {e}")
            return None
    
    def attempt_discovery(self, poi_id: UUID, explorer_faction_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Attempt to discover a landmark at a POI"""
        try:
            result = {
                'success': False,
                'landmark_discovered': None,
                'message': ""
            }
            
            # Check if there's a landmark here
            landmark_id = self.poi_landmarks.get(poi_id)
            if not landmark_id:
                result['message'] = "No landmark exists at this location"
                return result
            
            landmark = self.landmarks.get(landmark_id)
            if not landmark or landmark.status != LandmarkStatus.UNDISCOVERED:
                result['message'] = "Landmark already discovered or inaccessible"
                return result
            
            # Track discovery attempts
            if poi_id not in self.discovery_attempts:
                self.discovery_attempts[poi_id] = []
            
            self.discovery_attempts[poi_id].append(datetime.utcnow())
            
            # Calculate discovery chance
            discovery_difficulty = landmark.get_discovery_difficulty()
            success_chance = self.base_discovery_chance * (1.0 - discovery_difficulty)
            
            # Bonus for repeated attempts (learning from failures)
            attempt_count = len(self.discovery_attempts[poi_id])
            if attempt_count > 1:
                success_chance += (attempt_count - 1) * 0.02  # 2% per previous attempt
            
            # Roll for discovery
            if random.random() < success_chance:
                landmark.status = LandmarkStatus.DISCOVERED
                landmark.discovery_date = datetime.utcnow()
                landmark.discovered_by = explorer_faction_id
                landmark.last_updated = datetime.utcnow()
                
                # Make basic features discoverable
                for feature in landmark.features:
                    if not feature.activation_requirements or random.random() < 0.3:
                        feature.discovered = True
                
                result['success'] = True
                result['landmark_discovered'] = {
                    'id': str(landmark.id),
                    'name': landmark.name,
                    'type': landmark.landmark_type.value,
                    'rarity': landmark.rarity.value,
                    'description': landmark.description
                }
                result['message'] = f"Successfully discovered {landmark.name}!"
                
                # Dispatch discovery event
                self.event_dispatcher.publish({
                    'type': 'landmark_discovered',
                    'landmark_id': str(landmark.id),
                    'poi_id': str(poi_id),
                    'discovered_by': str(explorer_faction_id) if explorer_faction_id else None,
                    'discovery_date': landmark.discovery_date.isoformat(),
                    'timestamp': datetime.utcnow().isoformat()
                })
                
            else:
                result['message'] = f"Discovery attempt failed. {attempt_count} total attempts made."
            
            return result
            
        except Exception as e:
            logger.error(f"Error attempting discovery: {e}")
            return {'success': False, 'message': f"Error during discovery: {e}"}
    
    def start_exploration(self, landmark_id: UUID, team_info: Dict[str, Any]) -> bool:
        """Start exploring a discovered landmark"""
        try:
            landmark = self.landmarks.get(landmark_id)
            if not landmark:
                return False
            
            if landmark.status not in [LandmarkStatus.DISCOVERED, LandmarkStatus.EXPLORED]:
                return False
            
            # Check team limit
            current_teams = self.exploration_teams.get(landmark_id, {})
            if len(current_teams) >= self.max_exploration_teams_per_landmark:
                return False
            
            # Add exploration team
            team_id = str(uuid4())
            team_data = {
                'id': team_id,
                'faction_id': team_info.get('faction_id'),
                'team_size': team_info.get('team_size', 10),
                'equipment_level': team_info.get('equipment_level', 1.0),
                'start_date': datetime.utcnow(),
                'daily_progress': 0.0
            }
            
            if landmark_id not in self.exploration_teams:
                self.exploration_teams[landmark_id] = {}
            
            self.exploration_teams[landmark_id][team_id] = team_data
            
            # Update landmark status
            if landmark.status == LandmarkStatus.DISCOVERED:
                landmark.status = LandmarkStatus.EXPLORED
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting exploration: {e}")
            return False
    
    def process_daily_exploration(self, landmark_id: UUID) -> Dict[str, Any]:
        """Process daily exploration progress for a landmark"""
        try:
            results = {
                'progress_made': 0.0,
                'features_discovered': 0,
                'exploration_complete': False,
                'events': []
            }
            
            landmark = self.landmarks.get(landmark_id)
            if not landmark:
                return results
            
            teams = self.exploration_teams.get(landmark_id, {})
            if not teams:
                return results
            
            total_daily_progress = 0.0
            
            for team_id, team_data in teams.items():
                # Calculate team's daily progress
                base_progress = self.exploration_points_per_day
                team_modifier = team_data['team_size'] * team_data['equipment_level']
                daily_progress = base_progress * team_modifier / 100.0  # Normalize
                
                total_daily_progress += daily_progress
                team_data['daily_progress'] = daily_progress
            
            # Apply progress to landmark
            landmark.exploration_progress += total_daily_progress
            landmark.last_updated = datetime.utcnow()
            
            results['progress_made'] = total_daily_progress
            
            # Check for feature discoveries
            progress_ratio = landmark.exploration_progress / landmark.required_exploration_points
            for feature in landmark.features:
                if not feature.discovered and random.random() < progress_ratio * 0.1:
                    feature.discovered = True
                    results['features_discovered'] += 1
                    results['events'].append(f"Discovered feature: {feature.name}")
            
            # Check if exploration is complete
            if landmark.exploration_progress >= landmark.required_exploration_points:
                landmark.status = LandmarkStatus.FULLY_MAPPED
                results['exploration_complete'] = True
                results['events'].append("Landmark fully explored!")
                
                # Activate all features
                for feature in landmark.features:
                    feature.discovered = True
                    if "exploration:complete" in feature.activation_requirements:
                        feature.active = True
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing daily exploration: {e}")
            return {'error': str(e)}
    
    def claim_landmark(self, landmark_id: UUID, faction_id: UUID) -> bool:
        """Attempt to claim a landmark for a faction"""
        try:
            landmark = self.landmarks.get(landmark_id)
            if not landmark:
                return False
            
            if landmark.status not in [LandmarkStatus.FULLY_MAPPED, LandmarkStatus.EXPLORED]:
                return False
            
            # Check if already claimed
            if landmark.controlling_faction == faction_id:
                return True
            
            if landmark.controlling_faction is not None:
                # Landmark is contested
                if faction_id not in landmark.contested_by:
                    landmark.contested_by.append(faction_id)
                landmark.status = LandmarkStatus.CONTESTED
            else:
                # First claim
                landmark.controlling_faction = faction_id
                landmark.status = LandmarkStatus.CLAIMED
            
            # Dispatch claim event
            self.event_dispatcher.publish({
                'type': 'landmark_claimed',
                'landmark_id': str(landmark_id),
                'faction_id': str(faction_id),
                'contested': landmark.status == LandmarkStatus.CONTESTED,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error claiming landmark: {e}")
            return False
    
    def get_landmark_info(self, landmark_id: UUID, viewer_faction_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get comprehensive information about a landmark"""
        try:
            landmark = self.landmarks.get(landmark_id)
            if not landmark:
                return {}
            
            # Base information
            info = {
                'id': str(landmark.id),
                'poi_id': str(landmark.poi_id),
                'name': landmark.name,
                'description': landmark.description,
                'type': landmark.landmark_type.value,
                'rarity': landmark.rarity.value,
                'status': landmark.status.value,
                'age': landmark.age,
                'magical_resonance': landmark.magical_resonance
            }
            
            # Discovery information
            if landmark.status != LandmarkStatus.UNDISCOVERED:
                info['discovery_date'] = landmark.discovery_date.isoformat() if landmark.discovery_date else None
                info['discovered_by'] = str(landmark.discovered_by) if landmark.discovered_by else None
            
            # Exploration information
            if landmark.status in [LandmarkStatus.EXPLORED, LandmarkStatus.FULLY_MAPPED]:
                info['exploration_progress'] = landmark.exploration_progress
                info['required_exploration_points'] = landmark.required_exploration_points
                info['exploration_percentage'] = min(100, (landmark.exploration_progress / landmark.required_exploration_points) * 100)
            
            # Control information
            if landmark.controlling_faction:
                info['controlling_faction'] = str(landmark.controlling_faction)
            if landmark.contested_by:
                info['contested_by'] = [str(f) for f in landmark.contested_by]
            
            # Features (only show discovered ones unless viewer owns the landmark)
            show_all_features = (viewer_faction_id and 
                               (viewer_faction_id == landmark.controlling_faction or 
                                landmark.status == LandmarkStatus.FULLY_MAPPED))
            
            features = []
            for feature in landmark.features:
                if feature.discovered or show_all_features:
                    feature_info = {
                        'name': feature.name,
                        'description': feature.description,
                        'effect_type': feature.effect_type.value,
                        'magnitude': feature.magnitude,
                        'radius': feature.radius,
                        'active': feature.active,
                        'discovered': feature.discovered
                    }
                    
                    if show_all_features:
                        feature_info['activation_requirements'] = feature.activation_requirements
                    
                    features.append(feature_info)
            
            info['features'] = features
            
            # Unique resources
            if landmark.unique_resources and (show_all_features or landmark.status == LandmarkStatus.FULLY_MAPPED):
                info['unique_resources'] = landmark.unique_resources
            
            # Active exploration teams
            teams = self.exploration_teams.get(landmark_id, {})
            if teams:
                info['active_exploration_teams'] = len(teams)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting landmark info: {e}")
            return {}
    
    def get_poi_landmark(self, poi_id: UUID) -> Optional[Landmark]:
        """Get the landmark associated with a POI"""
        landmark_id = self.poi_landmarks.get(poi_id)
        if landmark_id:
            return self.landmarks.get(landmark_id)
        return None
    
    def generate_random_landmark(self, poi_id: UUID, force_type: Optional[LandmarkType] = None) -> Optional[Landmark]:
        """Generate a random landmark at a POI"""
        try:
            # Choose landmark type
            if force_type:
                landmark_type = force_type
            else:
                # Weight landmark types by rarity and POI characteristics
                poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
                if not poi:
                    return None
                
                landmark_type = self._choose_landmark_type_for_poi(poi)
            
            # Choose rarity
            rarity = self._choose_landmark_rarity()
            
            # Create landmark
            return self.create_landmark(poi_id, landmark_type, rarity)
            
        except Exception as e:
            logger.error(f"Error generating random landmark: {e}")
            return None
    
    def _get_rarity_multiplier(self, rarity: LandmarkRarity) -> float:
        """Get effect multiplier based on rarity"""
        multipliers = {
            LandmarkRarity.COMMON: 1.0,
            LandmarkRarity.UNCOMMON: 1.2,
            LandmarkRarity.RARE: 1.5,
            LandmarkRarity.EPIC: 2.0,
            LandmarkRarity.LEGENDARY: 3.0,
            LandmarkRarity.MYTHIC: 5.0
        }
        return multipliers.get(rarity, 1.0)
    
    def _choose_landmark_type_for_poi(self, poi: PoiEntity) -> LandmarkType:
        """Choose appropriate landmark type for a POI"""
        weights = {
            LandmarkType.NATURAL_WONDER: 20,
            LandmarkType.ANCIENT_RUINS: 15,
            LandmarkType.STRATEGIC_LOCATION: 15,
            LandmarkType.HISTORICAL_SITE: 10,
            LandmarkType.MAGICAL_SITE: 8,
            LandmarkType.RELIGIOUS_SHRINE: 8,
            LandmarkType.RESOURCE_NODE: 8,
            LandmarkType.DUNGEON: 5,
            LandmarkType.MONUMENT: 5,
            LandmarkType.PORTAL: 3,
            LandmarkType.LIBRARY: 2,
            LandmarkType.OBSERVATORY: 1
        }
        
        # Modify weights based on POI type
        if poi.poi_type == POIType.CITY.value:
            weights[LandmarkType.MONUMENT] *= 3
            weights[LandmarkType.LIBRARY] *= 5
            weights[LandmarkType.ACADEMY] = 3
        elif poi.poi_type == POIType.TEMPLE.value:
            weights[LandmarkType.RELIGIOUS_SHRINE] *= 5
            weights[LandmarkType.MAGICAL_SITE] *= 2
        elif poi.poi_type == POIType.FORTRESS.value:
            weights[LandmarkType.STRATEGIC_LOCATION] *= 4
            weights[LandmarkType.BATTLEFIELD] = 10
        
        # Choose weighted random
        types = list(weights.keys())
        weight_values = list(weights.values())
        return random.choices(types, weights=weight_values)[0]
    
    def _choose_landmark_rarity(self) -> LandmarkRarity:
        """Choose landmark rarity based on probability distribution"""
        weights = {
            LandmarkRarity.COMMON: 40,
            LandmarkRarity.UNCOMMON: 30,
            LandmarkRarity.RARE: 20,
            LandmarkRarity.EPIC: 7,
            LandmarkRarity.LEGENDARY: 2,
            LandmarkRarity.MYTHIC: 1
        }
        
        rarities = list(weights.keys())
        weight_values = list(weights.values())
        return random.choices(rarities, weights=weight_values)[0]


# Factory function for dependency injection
def get_landmark_service(db_session: Optional[Session] = None) -> LandmarkService:
    """Factory function to create LandmarkService instance"""
    return LandmarkService(db_session) 