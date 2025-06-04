"""
War Impact Models for Population System (Business Logic)

Defines war-related structures that affect population dynamics including:
- War scenarios and their population impacts
- Siege effects on population survival and morale
- Refugee generation and management
- Post-war reconstruction phases
- Military recruitment impacts
- War-related economic disruption

This is business logic code that models war systems affecting populations.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)


class WarStatus(Enum):
    """War status levels"""
    PEACE = "peace"
    TENSIONS = "tensions"
    SKIRMISHES = "skirmishes"
    ACTIVE_WAR = "active_war"
    SIEGE = "siege"
    OCCUPATION = "occupation"
    RECONSTRUCTION = "reconstruction"


class SiegeStage(Enum):
    """Siege progression stages"""
    APPROACHING = "approaching"
    BESIEGED = "besieged"
    UNDER_ATTACK = "under_attack"
    BREACHED = "breached"
    CAPTURED = "captured"
    LIBERATED = "liberated"


class RefugeeStatus(Enum):
    """Refugee population status"""
    DISPLACED = "displaced"
    IN_TRANSIT = "in_transit"
    TEMPORARY_SETTLEMENT = "temporary_settlement"
    SEEKING_PERMANENT_HOME = "seeking_permanent_home"
    INTEGRATED = "integrated"
    RETURNED = "returned"


class ReconstructionPhase(Enum):
    """Post-war reconstruction phases"""
    IMMEDIATE_RELIEF = "immediate_relief"
    BASIC_INFRASTRUCTURE = "basic_infrastructure"
    ECONOMIC_RECOVERY = "economic_recovery"
    SOCIAL_REBUILDING = "social_rebuilding"
    FULL_RESTORATION = "full_restoration"


@dataclass
class WarScenario:
    """Represents an active war scenario"""
    scenario_id: str
    name: str
    war_status: WarStatus
    start_date: datetime
    estimated_duration_days: int
    intensity_level: float  # 0.0 to 1.0
    affected_settlements: List[str]
    aggressor_settlements: List[str]
    defender_settlements: List[str]
    war_type: str  # "territorial", "succession", "resources", "independence"
    
    # War effects
    population_mortality_rate: float = 0.05  # Daily mortality increase
    refugee_generation_rate: float = 0.10   # Daily population displacement
    economic_disruption_factor: float = 0.30  # Economic penalty
    morale_impact: float = -0.40  # Daily morale decrease
    recruitment_rate: float = 0.02  # Daily population recruitment to military
    
    # Siege-specific data
    siege_data: Optional['SiegeData'] = None
    
    # Status tracking
    current_phase: str = "initial"
    last_updated: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class SiegeData:
    """Detailed siege information"""
    besieged_settlement: str
    besieging_forces: List[str]
    siege_stage: SiegeStage
    siege_start_date: datetime
    estimated_duration_days: int
    
    # Siege effects
    daily_population_loss: float = 0.08  # Higher than regular war
    food_shortage_severity: float = 0.60  # Severe food shortages
    disease_outbreak_chance: float = 0.15  # Daily chance of disease
    morale_collapse_rate: float = 0.50  # Severe morale impact
    refugee_escape_rate: float = 0.05  # Some escape daily
    
    # Siege progression factors
    defensive_bonus: float = 1.0  # Settlement's defensive capabilities
    supply_line_status: float = 0.0  # 0.0 = cut off, 1.0 = fully supplied
    civilian_evacuation_percentage: float = 0.0  # How many have been evacuated
    
    # Breaking points
    surrender_threshold: float = 0.10  # Population % when surrender likely
    breakthrough_probability: float = 0.05  # Daily chance besiegers break through


@dataclass
class RefugeePopulation:
    """Refugee population group"""
    refugee_id: str
    origin_settlement: str
    current_location: str  # Settlement or "in_transit"
    destination_settlement: Optional[str]
    
    # Population data
    population_count: int
    original_population: int
    refugee_status: RefugeeStatus
    displacement_date: datetime
    
    # Characteristics
    age_distribution: Dict[str, float]  # children, adults, elderly percentages
    skill_composition: Dict[str, float]  # skilled, unskilled, artisan percentages
    health_status: float = 0.60  # Generally poor due to displacement
    morale: float = 0.30  # Generally low
    resources: float = 0.20  # Limited resources
    
    # Movement and integration
    travel_progress: float = 0.0  # 0.0 to 1.0 for journey completion
    integration_progress: float = 0.0  # 0.0 to 1.0 for settlement integration
    return_probability: float = 0.70  # Likelihood to return when safe
    
    # Needs and support
    daily_food_requirement: float = 0.8  # Food units per person
    shelter_requirement: float = 0.6  # Shelter units per person
    medical_care_need: float = 0.4  # Medical attention needed


@dataclass
class ReconstructionProject:
    """Post-war reconstruction project"""
    project_id: str
    settlement_id: str
    project_name: str
    reconstruction_phase: ReconstructionPhase
    start_date: datetime
    estimated_completion_days: int
    resource_requirements: Dict[str, float]  # materials, labor, expertise
    funding_required: float
    
    # Optional fields with defaults
    progress_percentage: float = 0.0
    priority_level: str = "medium"  # low, medium, high, critical
    funding_secured: float = 0.0
    employment_provided: int = 0  # Jobs created
    population_capacity_restored: int = 0  # Housing/infrastructure restored
    economic_boost_factor: float = 0.0  # Economic improvement
    morale_boost: float = 0.0  # Morale improvement upon completion
    prerequisite_projects: List[str] = field(default_factory=list)
    dependent_projects: List[str] = field(default_factory=list)
    is_completed: bool = False
    completion_date: Optional[datetime] = None


class WarImpactEngine:
    """Engine for managing war impacts on populations"""
    
    def __init__(self):
        self.active_wars: Dict[str, WarScenario] = {}
        self.refugee_populations: Dict[str, RefugeePopulation] = {}
        self.reconstruction_projects: Dict[str, ReconstructionProject] = {}
        self.settlement_war_status: Dict[str, WarStatus] = {}
        self.war_history: List[Dict[str, Any]] = []
        
        logger.info("War Impact Engine initialized")
    
    def create_war_scenario(
        self,
        name: str,
        war_type: str,
        aggressor_settlements: List[str],
        defender_settlements: List[str],
        intensity_level: float = 0.5,
        estimated_duration_days: int = 180
    ) -> str:
        """Create a new war scenario"""
        scenario_id = f"war_{len(self.active_wars) + 1}_{int(datetime.utcnow().timestamp())}"
        
        affected_settlements = list(set(aggressor_settlements + defender_settlements))
        
        war_scenario = WarScenario(
            scenario_id=scenario_id,
            name=name,
            war_status=WarStatus.ACTIVE_WAR,
            start_date=datetime.utcnow(),
            estimated_duration_days=estimated_duration_days,
            intensity_level=intensity_level,
            affected_settlements=affected_settlements,
            aggressor_settlements=aggressor_settlements,
            defender_settlements=defender_settlements,
            war_type=war_type,
            population_mortality_rate=0.02 + (intensity_level * 0.08),
            refugee_generation_rate=0.05 + (intensity_level * 0.15),
            economic_disruption_factor=0.20 + (intensity_level * 0.40),
            morale_impact=-0.20 - (intensity_level * 0.30),
            recruitment_rate=0.01 + (intensity_level * 0.03)
        )
        
        self.active_wars[scenario_id] = war_scenario
        
        # Update settlement war status
        for settlement_id in affected_settlements:
            self.settlement_war_status[settlement_id] = WarStatus.ACTIVE_WAR
        
        logger.info(f"Created war scenario: {name} ({scenario_id})")
        return scenario_id
    
    def initiate_siege(
        self,
        war_scenario_id: str,
        besieged_settlement: str,
        besieging_forces: List[str],
        estimated_duration_days: int = 90
    ) -> bool:
        """Initiate a siege as part of an active war"""
        if war_scenario_id not in self.active_wars:
            logger.error(f"War scenario {war_scenario_id} not found")
            return False
        
        war_scenario = self.active_wars[war_scenario_id]
        
        # Create siege data
        siege_data = SiegeData(
            besieged_settlement=besieged_settlement,
            besieging_forces=besieging_forces,
            siege_stage=SiegeStage.APPROACHING,
            siege_start_date=datetime.utcnow(),
            estimated_duration_days=estimated_duration_days,
            daily_population_loss=0.05 + (war_scenario.intensity_level * 0.05),
            food_shortage_severity=0.40 + (war_scenario.intensity_level * 0.30),
            disease_outbreak_chance=0.10 + (war_scenario.intensity_level * 0.10),
            morale_collapse_rate=0.30 + (war_scenario.intensity_level * 0.30)
        )
        
        war_scenario.siege_data = siege_data
        war_scenario.war_status = WarStatus.SIEGE
        self.settlement_war_status[besieged_settlement] = WarStatus.SIEGE
        
        logger.info(f"Siege initiated: {besieged_settlement} in war {war_scenario_id}")
        return True
    
    def generate_refugees(
        self,
        origin_settlement: str,
        population_to_displace: int,
        destination_settlement: Optional[str] = None
    ) -> str:
        """Generate a refugee population from a settlement"""
        refugee_id = f"refugees_{origin_settlement}_{len(self.refugee_populations) + 1}"
        
        # Determine age and skill distribution (displaced populations skew certain ways)
        age_distribution = {
            "children": 0.35,  # Families with children flee first
            "adults": 0.55,
            "elderly": 0.10    # Many elderly may not be able to flee
        }
        
        skill_composition = {
            "unskilled": 0.60,  # Skilled workers may have resources to stay
            "skilled": 0.25,
            "artisan": 0.15
        }
        
        refugee_population = RefugeePopulation(
            refugee_id=refugee_id,
            origin_settlement=origin_settlement,
            current_location="in_transit",
            destination_settlement=destination_settlement,
            population_count=population_to_displace,
            original_population=population_to_displace,
            refugee_status=RefugeeStatus.DISPLACED,
            displacement_date=datetime.utcnow(),
            age_distribution=age_distribution,
            skill_composition=skill_composition
        )
        
        self.refugee_populations[refugee_id] = refugee_population
        
        logger.info(f"Generated refugee population: {refugee_id} ({population_to_displace} people)")
        return refugee_id
    
    def create_reconstruction_project(
        self,
        settlement_id: str,
        project_name: str,
        reconstruction_phase: ReconstructionPhase,
        resource_requirements: Dict[str, float],
        funding_required: float,
        estimated_completion_days: int = 120
    ) -> str:
        """Create a post-war reconstruction project"""
        project_id = f"reconstruction_{settlement_id}_{len(self.reconstruction_projects) + 1}"
        
        project = ReconstructionProject(
            project_id=project_id,
            settlement_id=settlement_id,
            project_name=project_name,
            reconstruction_phase=reconstruction_phase,
            start_date=datetime.utcnow(),
            estimated_completion_days=estimated_completion_days,
            resource_requirements=resource_requirements,
            funding_required=funding_required
        )
        
        # Calculate impact based on phase
        if reconstruction_phase == ReconstructionPhase.IMMEDIATE_RELIEF:
            project.employment_provided = int(funding_required * 0.1)
            project.morale_boost = 0.20
        elif reconstruction_phase == ReconstructionPhase.BASIC_INFRASTRUCTURE:
            project.population_capacity_restored = int(funding_required * 0.05)
            project.employment_provided = int(funding_required * 0.15)
            project.morale_boost = 0.30
        elif reconstruction_phase == ReconstructionPhase.ECONOMIC_RECOVERY:
            project.economic_boost_factor = funding_required * 0.002
            project.employment_provided = int(funding_required * 0.20)
            project.morale_boost = 0.25
        
        self.reconstruction_projects[project_id] = project
        
        logger.info(f"Created reconstruction project: {project_name} ({project_id})")
        return project_id
    
    def process_daily_war_effects(self, settlement_id: str, current_population: int) -> Dict[str, Any]:
        """Process daily war effects on a settlement"""
        effects = {
            "population_change": 0,
            "morale_change": 0.0,
            "economic_impact": 0.0,
            "refugees_generated": 0,
            "military_recruited": 0,
            "events": []
        }
        
        # Check if settlement is affected by any active war
        active_war = None
        for war in self.active_wars.values():
            if settlement_id in war.affected_settlements and war.is_active:
                active_war = war
                break
        
        if not active_war:
            return effects
        
        # Apply war effects
        if active_war.war_status == WarStatus.SIEGE and active_war.siege_data:
            effects.update(self._process_siege_effects(settlement_id, current_population, active_war.siege_data))
        else:
            effects.update(self._process_general_war_effects(settlement_id, current_population, active_war))
        
        return effects
    
    def _process_siege_effects(self, settlement_id: str, current_population: int, siege_data: SiegeData) -> Dict[str, Any]:
        """Process siege-specific effects"""
        effects = {
            "population_change": 0,
            "morale_change": 0.0,
            "economic_impact": 0.0,
            "refugees_generated": 0,
            "military_recruited": 0,
            "events": []
        }
        
        if siege_data.besieged_settlement != settlement_id:
            return effects
        
        # Population loss from siege
        daily_loss = int(current_population * siege_data.daily_population_loss)
        effects["population_change"] = -daily_loss
        
        # Severe morale impact
        effects["morale_change"] = -siege_data.morale_collapse_rate
        
        # Economic collapse during siege
        effects["economic_impact"] = -0.80  # Severe economic disruption
        
        # Some refugees escape
        refugees_escaping = int(current_population * siege_data.refugee_escape_rate)
        if refugees_escaping > 0:
            refugee_id = self.generate_refugees(settlement_id, refugees_escaping)
            effects["refugees_generated"] = refugees_escaping
            effects["events"].append(f"Refugees escaped siege: {refugees_escaping} people")
        
        # Check for disease outbreak
        if random.random() < siege_data.disease_outbreak_chance:
            effects["events"].append("Disease outbreak due to siege conditions")
        
        # Check for surrender conditions
        if current_population <= siege_data.surrender_threshold * current_population:
            effects["events"].append("Settlement approaching surrender threshold")
        
        # Siege progression
        self._progress_siege_stage(siege_data)
        
        return effects
    
    def _process_general_war_effects(self, settlement_id: str, current_population: int, war: WarScenario) -> Dict[str, Any]:
        """Process general war effects"""
        effects = {
            "population_change": 0,
            "morale_change": 0.0,
            "economic_impact": 0.0,
            "refugees_generated": 0,
            "military_recruited": 0,
            "events": []
        }
        
        # Population mortality
        daily_loss = int(current_population * war.population_mortality_rate)
        effects["population_change"] = -daily_loss
        
        # Refugee generation
        refugees_generated = int(current_population * war.refugee_generation_rate)
        if refugees_generated > 0:
            refugee_id = self.generate_refugees(settlement_id, refugees_generated)
            effects["refugees_generated"] = refugees_generated
        
        # Military recruitment
        military_recruited = int(current_population * war.recruitment_rate)
        effects["military_recruited"] = military_recruited
        effects["population_change"] -= military_recruited
        
        # Morale and economic impact
        effects["morale_change"] = war.morale_impact
        effects["economic_impact"] = -war.economic_disruption_factor
        
        return effects
    
    def _progress_siege_stage(self, siege_data: SiegeData):
        """Progress siege through stages"""
        days_since_start = (datetime.utcnow() - siege_data.siege_start_date).days
        
        if siege_data.siege_stage == SiegeStage.APPROACHING and days_since_start >= 3:
            siege_data.siege_stage = SiegeStage.BESIEGED
        elif siege_data.siege_stage == SiegeStage.BESIEGED and days_since_start >= 14:
            siege_data.siege_stage = SiegeStage.UNDER_ATTACK
        elif siege_data.siege_stage == SiegeStage.UNDER_ATTACK:
            # Check for breakthrough
            if random.random() < siege_data.breakthrough_probability:
                siege_data.siege_stage = SiegeStage.BREACHED
    
    def end_war_scenario(self, war_scenario_id: str, outcome: str = "concluded") -> bool:
        """End an active war scenario"""
        if war_scenario_id not in self.active_wars:
            return False
        
        war = self.active_wars[war_scenario_id]
        war.is_active = False
        
        # Update settlement statuses
        for settlement_id in war.affected_settlements:
            self.settlement_war_status[settlement_id] = WarStatus.RECONSTRUCTION
        
        # Record in history
        self.war_history.append({
            "scenario_id": war_scenario_id,
            "name": war.name,
            "start_date": war.start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "duration_days": (datetime.utcnow() - war.start_date).days,
            "outcome": outcome,
            "affected_settlements": war.affected_settlements
        })
        
        logger.info(f"War scenario ended: {war.name} ({outcome})")
        return True
    
    def get_war_status(self, settlement_id: str) -> WarStatus:
        """Get current war status for a settlement"""
        return self.settlement_war_status.get(settlement_id, WarStatus.PEACE)
    
    def get_active_wars(self) -> List[Dict[str, Any]]:
        """Get all active war scenarios"""
        return [
            {
                "scenario_id": war.scenario_id,
                "name": war.name,
                "war_status": war.war_status.value,
                "start_date": war.start_date.isoformat(),
                "affected_settlements": war.affected_settlements,
                "intensity_level": war.intensity_level
            }
            for war in self.active_wars.values() if war.is_active
        ]
    
    def get_refugee_populations(self) -> List[Dict[str, Any]]:
        """Get all active refugee populations"""
        return [
            {
                "refugee_id": refugee.refugee_id,
                "origin_settlement": refugee.origin_settlement,
                "current_location": refugee.current_location,
                "population_count": refugee.population_count,
                "refugee_status": refugee.refugee_status.value,
                "displacement_date": refugee.displacement_date.isoformat()
            }
            for refugee in self.refugee_populations.values()
        ]
    
    def get_reconstruction_projects(self, settlement_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get reconstruction projects for a settlement or all"""
        projects = self.reconstruction_projects.values()
        if settlement_id:
            projects = [p for p in projects if p.settlement_id == settlement_id]
        
        return [
            {
                "project_id": project.project_id,
                "settlement_id": project.settlement_id,
                "project_name": project.project_name,
                "reconstruction_phase": project.reconstruction_phase.value,
                "progress_percentage": project.progress_percentage,
                "is_completed": project.is_completed
            }
            for project in projects
        ]


# Global war impact engine instance
war_engine = WarImpactEngine()

# Export functions
__all__ = [
    "WarStatus",
    "SiegeStage", 
    "RefugeeStatus",
    "ReconstructionPhase",
    "WarScenario",
    "SiegeData",
    "RefugeePopulation",
    "ReconstructionProject",
    "WarImpactEngine",
    "war_engine"
] 