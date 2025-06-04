"""
Disease and Plague Models for Population System

Implements realistic disease modeling including:
- Disease types with unique characteristics
- Environmental factors affecting transmission
- Disease progression through stages
- Population impact calculations
- Quest generation based on disease outbreaks
"""

import logging
import random
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import math

logger = logging.getLogger(__name__)


class DiseaseType(Enum):
    """Types of diseases that can affect populations"""
    PLAGUE = "plague"
    FEVER = "fever"
    POX = "pox"
    WASTING = "wasting"
    FLUX = "flux"
    SWEATING_SICKNESS = "sweating_sickness"
    LUNG_ROT = "lung_rot"
    BONE_FEVER = "bone_fever"


class DiseaseStage(Enum):
    """Stages of disease progression in populations"""
    EMERGING = "emerging"
    SPREADING = "spreading"
    PEAK = "peak"
    DECLINING = "declining"
    ENDEMIC = "endemic"
    ERADICATED = "eradicated"


@dataclass
class DiseaseProfile:
    """Profile defining characteristics of a specific disease"""
    name: str
    disease_type: DiseaseType
    mortality_rate: float  # Percentage who die from infection (0.0-1.0)
    transmission_rate: float  # Base transmission rate per day (0.0-1.0)
    incubation_days: int  # Days before symptoms appear
    recovery_days: int  # Days to recovery or death
    immunity_duration_days: int  # Days of immunity after recovery (0 = permanent)
    
    # Environmental factors (multipliers)
    crowding_factor: float = 1.5  # Multiplier for crowded conditions
    hygiene_factor: float = 1.3  # Multiplier for poor hygiene
    healthcare_factor: float = 0.7  # Multiplier with good healthcare
    
    # Seasonal preferences
    seasonal_preference: Optional[str] = None  # "winter", "summer", "spring", "autumn"
    seasonal_multiplier: float = 1.5  # Multiplier during preferred season
    
    # Population targeting
    targets_young: bool = False  # Preferentially affects children
    targets_old: bool = False    # Preferentially affects elderly
    targets_weak: bool = False   # Preferentially affects sick/malnourished


# Disease profiles for different disease types
DISEASE_PROFILES = {
    DiseaseType.PLAGUE: DiseaseProfile(
        name="Black Death",
        disease_type=DiseaseType.PLAGUE,
        mortality_rate=0.6,  # 60% mortality
        transmission_rate=0.25,
        incubation_days=3,
        recovery_days=7,
        immunity_duration_days=365,
        crowding_factor=2.0,
        hygiene_factor=1.8,
        healthcare_factor=0.5,
        seasonal_preference="autumn",
        targets_weak=True
    ),
    
    DiseaseType.FEVER: DiseaseProfile(
        name="Marsh Fever",
        disease_type=DiseaseType.FEVER,
        mortality_rate=0.15,  # 15% mortality
        transmission_rate=0.35,
        incubation_days=2,
        recovery_days=5,
        immunity_duration_days=180,
        crowding_factor=1.3,
        hygiene_factor=1.5,
        healthcare_factor=0.6,
        seasonal_preference="summer",
        targets_young=True
    ),
    
    DiseaseType.POX: DiseaseProfile(
        name="Red Pox",
        disease_type=DiseaseType.POX,
        mortality_rate=0.25,  # 25% mortality
        transmission_rate=0.4,
        incubation_days=4,
        recovery_days=10,
        immunity_duration_days=0,  # Permanent immunity
        crowding_factor=1.8,
        hygiene_factor=1.2,
        healthcare_factor=0.7,
        targets_young=True
    ),
    
    DiseaseType.WASTING: DiseaseProfile(
        name="Wasting Sickness",
        disease_type=DiseaseType.WASTING,
        mortality_rate=0.8,  # 80% mortality
        transmission_rate=0.1,
        incubation_days=7,
        recovery_days=30,
        immunity_duration_days=0,
        crowding_factor=1.2,
        hygiene_factor=1.4,
        healthcare_factor=0.4,
        targets_old=True,
        targets_weak=True
    ),
    
    DiseaseType.FLUX: DiseaseProfile(
        name="Bloody Flux",
        disease_type=DiseaseType.FLUX,
        mortality_rate=0.3,  # 30% mortality
        transmission_rate=0.3,
        incubation_days=1,
        recovery_days=8,
        immunity_duration_days=90,
        crowding_factor=1.6,
        hygiene_factor=2.0,
        healthcare_factor=0.5,
        seasonal_preference="summer",
        targets_young=True,
        targets_old=True
    ),
    
    DiseaseType.SWEATING_SICKNESS: DiseaseProfile(
        name="Sweating Sickness",
        disease_type=DiseaseType.SWEATING_SICKNESS,
        mortality_rate=0.4,  # 40% mortality
        transmission_rate=0.6,
        incubation_days=1,
        recovery_days=3,
        immunity_duration_days=30,
        crowding_factor=1.7,
        hygiene_factor=1.1,
        healthcare_factor=0.8,
        seasonal_preference="summer"
    ),
    
    DiseaseType.LUNG_ROT: DiseaseProfile(
        name="Lung Rot",
        disease_type=DiseaseType.LUNG_ROT,
        mortality_rate=0.45,  # 45% mortality
        transmission_rate=0.2,
        incubation_days=5,
        recovery_days=21,
        immunity_duration_days=0,  # Permanent immunity
        crowding_factor=1.9,
        hygiene_factor=1.3,
        healthcare_factor=0.6,
        seasonal_preference="winter",
        targets_old=True
    ),
    
    DiseaseType.BONE_FEVER: DiseaseProfile(
        name="Bone Fever",
        disease_type=DiseaseType.BONE_FEVER,
        mortality_rate=0.05,  # 5% mortality but very infectious
        transmission_rate=0.8,
        incubation_days=2,
        recovery_days=14,
        immunity_duration_days=365,
        crowding_factor=1.4,
        hygiene_factor=1.2,
        healthcare_factor=0.9,
        seasonal_preference="spring"
    )
}


@dataclass
class DiseaseOutbreak:
    """Represents an active disease outbreak in a population"""
    disease_type: DiseaseType
    stage: DiseaseStage
    infected_count: int
    total_deaths: int
    days_active: int
    infection_rate: float  # Current rate of new infections per day
    
    # Environmental modifiers currently affecting outbreak
    current_crowding_modifier: float = 1.0
    current_hygiene_modifier: float = 1.0
    current_healthcare_modifier: float = 1.0
    current_seasonal_modifier: float = 1.0
    
    # Tracking
    peak_infected: int = 0
    start_date: datetime = field(default_factory=datetime.now)
    
    def get_profile(self) -> DiseaseProfile:
        """Get the disease profile for this outbreak"""
        return DISEASE_PROFILES[self.disease_type]


class DiseaseModelingEngine:
    """Engine for modeling disease spread and impact on populations"""
    
    def __init__(self):
        self.active_outbreaks: Dict[str, List[DiseaseOutbreak]] = {}
        
    def introduce_disease(
        self,
        population_id: str,
        disease_type: DiseaseType,
        initial_infected: int = 1,
        environmental_factors: Optional[Dict[str, float]] = None
    ) -> DiseaseOutbreak:
        """
        Introduce a disease to a population
        
        Args:
            population_id: ID of the population
            disease_type: Type of disease to introduce
            initial_infected: Number of initially infected individuals
            environmental_factors: Dict with keys: crowding, hygiene, healthcare, season
            
        Returns:
            DiseaseOutbreak object representing the new outbreak
        """
        if population_id not in self.active_outbreaks:
            self.active_outbreaks[population_id] = []
            
        # Check if this disease type is already active
        for outbreak in self.active_outbreaks[population_id]:
            if outbreak.disease_type == disease_type:
                # Increase existing outbreak
                outbreak.infected_count += initial_infected
                return outbreak
        
        # Create new outbreak
        profile = DISEASE_PROFILES[disease_type]
        
        # Calculate environmental modifiers
        env_factors = environmental_factors or {}
        crowding_mod = env_factors.get('crowding', 1.0)
        hygiene_mod = env_factors.get('hygiene', 1.0)  
        healthcare_mod = env_factors.get('healthcare', 1.0)
        seasonal_mod = self._calculate_seasonal_modifier(profile, env_factors.get('season'))
        
        outbreak = DiseaseOutbreak(
            disease_type=disease_type,
            stage=DiseaseStage.EMERGING,
            infected_count=initial_infected,
            total_deaths=0,
            days_active=0,
            infection_rate=profile.transmission_rate,
            current_crowding_modifier=crowding_mod,
            current_hygiene_modifier=hygiene_mod,
            current_healthcare_modifier=healthcare_mod,
            current_seasonal_modifier=seasonal_mod,
            peak_infected=initial_infected
        )
        
        self.active_outbreaks[population_id].append(outbreak)
        
        logger.info(f"Disease outbreak started: {profile.name} in population {population_id}")
        return outbreak
    
    def progress_disease_day(
        self,
        population_id: str,
        total_population: int,
        environmental_factors: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Progress all diseases in a population by one day
        
        Args:
            population_id: ID of the population
            total_population: Current total population
            environmental_factors: Current environmental conditions
            
        Returns:
            Dict with outbreak status and effects
        """
        if population_id not in self.active_outbreaks:
            return {"active_outbreaks": 0, "total_infected": 0, "new_deaths": 0}
        
        outbreaks = self.active_outbreaks[population_id]
        total_infected = 0
        total_new_deaths = 0
        
        # Update environmental factors
        env_factors = environmental_factors or {}
        
        outbreaks_to_remove = []
        
        for outbreak in outbreaks:
            profile = outbreak.get_profile()
            
            # Update environmental modifiers
            outbreak.current_crowding_modifier = env_factors.get('crowding', 1.0)
            outbreak.current_hygiene_modifier = env_factors.get('hygiene', 1.0)
            outbreak.current_healthcare_modifier = env_factors.get('healthcare', 1.0)
            outbreak.current_seasonal_modifier = self._calculate_seasonal_modifier(
                profile, env_factors.get('season')
            )
            
            # Calculate effective transmission rate
            transmission_modifier = (
                outbreak.current_crowding_modifier * profile.crowding_factor +
                outbreak.current_hygiene_modifier * profile.hygiene_factor +
                outbreak.current_healthcare_modifier * profile.healthcare_factor +
                outbreak.current_seasonal_modifier
            ) / 4.0
            
            effective_transmission = profile.transmission_rate * transmission_modifier
            
            # Calculate new infections
            susceptible_population = max(0, total_population - outbreak.infected_count)
            infection_probability = min(0.95, effective_transmission * (outbreak.infected_count / total_population))
            new_infections = int(susceptible_population * infection_probability)
            
            # Update outbreak
            outbreak.infected_count += new_infections
            outbreak.days_active += 1
            outbreak.peak_infected = max(outbreak.peak_infected, outbreak.infected_count)
            
            # Calculate deaths
            if outbreak.days_active >= profile.incubation_days:
                # People start dying after incubation period
                days_since_incubation = outbreak.days_active - profile.incubation_days
                if days_since_incubation < profile.recovery_days:
                    # Deaths occur during recovery period
                    death_rate_per_day = profile.mortality_rate / profile.recovery_days
                    healthcare_death_modifier = outbreak.current_healthcare_modifier * profile.healthcare_factor
                    effective_death_rate = death_rate_per_day / healthcare_death_modifier
                    
                    new_deaths = int(outbreak.infected_count * effective_death_rate)
                    outbreak.total_deaths += new_deaths
                    outbreak.infected_count = max(0, outbreak.infected_count - new_deaths)
                    total_new_deaths += new_deaths
            
            # Update disease stage
            outbreak.stage = self._calculate_disease_stage(outbreak, total_population)
            
            # Check if outbreak should end
            if (outbreak.stage == DiseaseStage.ERADICATED or 
                (outbreak.infected_count == 0 and outbreak.days_active > profile.recovery_days)):
                outbreaks_to_remove.append(outbreak)
            
            total_infected += outbreak.infected_count
        
        # Remove ended outbreaks
        for outbreak in outbreaks_to_remove:
            outbreaks.remove(outbreak)
            logger.info(f"Disease outbreak ended: {outbreak.get_profile().name} in population {population_id}")
        
        return {
            "active_outbreaks": len(outbreaks),
            "total_infected": total_infected,
            "new_deaths": total_new_deaths,
            "outbreaks": [
                {
                    "disease_type": outbreak.disease_type.value,
                    "stage": outbreak.stage.value,
                    "infected_count": outbreak.infected_count,
                    "total_deaths": outbreak.total_deaths,
                    "days_active": outbreak.days_active
                }
                for outbreak in outbreaks
            ]
        }
    
    def get_disease_status(self, population_id: str) -> Dict[str, Any]:
        """Get current disease status for a population"""
        if population_id not in self.active_outbreaks:
            return {"has_diseases": False, "outbreaks": []}
        
        outbreaks = self.active_outbreaks[population_id]
        if not outbreaks:
            return {"has_diseases": False, "outbreaks": []}
        
        return {
            "has_diseases": True,
            "outbreak_count": len(outbreaks),
            "outbreaks": [
                {
                    "disease_type": outbreak.disease_type.value,
                    "disease_name": outbreak.get_profile().name,
                    "stage": outbreak.stage.value,
                    "infected_count": outbreak.infected_count,
                    "total_deaths": outbreak.total_deaths,
                    "days_active": outbreak.days_active,
                    "mortality_rate": outbreak.get_profile().mortality_rate,
                    "peak_infected": outbreak.peak_infected
                }
                for outbreak in outbreaks
            ]
        }
    
    def generate_quest_opportunities(self, population_id: str) -> List[Dict[str, Any]]:
        """
        Generate quest opportunities based on active disease outbreaks
        
        Returns:
            List of quest opportunity dictionaries
        """
        if population_id not in self.active_outbreaks:
            return []
        
        quest_opportunities = []
        
        for outbreak in self.active_outbreaks[population_id]:
            profile = outbreak.get_profile()
            
            # Generate quests based on outbreak stage
            if outbreak.stage == DiseaseStage.EMERGING:
                quest_opportunities.extend([
                    {
                        "type": "investigation",
                        "title": f"Strange Illness Investigation",
                        "description": f"Reports of a mysterious illness resembling {profile.name} have emerged. Investigate the source.",
                        "urgency": "medium",
                        "reward_type": "knowledge",
                        "requirements": ["investigation_skill", "medical_knowledge"]
                    },
                    {
                        "type": "gathering",
                        "title": f"Medicinal Herbs Collection",
                        "description": f"Gather herbs that might help treat the emerging {profile.name} outbreak.",
                        "urgency": "medium",
                        "reward_type": "items",
                        "requirements": ["herbalism", "foraging"]
                    }
                ])
            
            elif outbreak.stage == DiseaseStage.SPREADING:
                quest_opportunities.extend([
                    {
                        "type": "delivery",
                        "title": f"Emergency Medicine Delivery",
                        "description": f"Rush medical supplies to contain the spreading {profile.name} outbreak.",
                        "urgency": "high",
                        "reward_type": "reputation",
                        "requirements": ["fast_travel", "disease_resistance"]
                    },
                    {
                        "type": "protection",
                        "title": f"Quarantine Enforcement",
                        "description": f"Help enforce quarantine measures to prevent {profile.name} from spreading further.",
                        "urgency": "high",
                        "reward_type": "authority",
                        "requirements": ["combat_skill", "persuasion"]
                    }
                ])
            
            elif outbreak.stage == DiseaseStage.PEAK:
                quest_opportunities.extend([
                    {
                        "type": "evacuation",
                        "title": f"Emergency Evacuation",
                        "description": f"Help evacuate healthy citizens from areas devastated by {profile.name}.",
                        "urgency": "critical",
                        "reward_type": "heroic_deed",
                        "requirements": ["leadership", "logistics"]
                    },
                    {
                        "type": "extermination",
                        "title": f"Source Elimination",
                        "description": f"Find and eliminate the source of the {profile.name} outbreak.",
                        "urgency": "critical",
                        "reward_type": "legendary_reward",
                        "requirements": ["combat_skill", "magic_resistance", "disease_immunity"]
                    }
                ])
            
            elif outbreak.stage == DiseaseStage.DECLINING:
                quest_opportunities.extend([
                    {
                        "type": "rebuilding",
                        "title": f"Community Recovery",
                        "description": f"Help rebuild the community after the devastating {profile.name} outbreak.",
                        "urgency": "low",
                        "reward_type": "social_standing",
                        "requirements": ["crafting", "leadership", "resources"]
                    },
                    {
                        "type": "memorial",
                        "title": f"Memorial Construction",
                        "description": f"Build a memorial for those lost to the {profile.name} outbreak.",
                        "urgency": "low",
                        "reward_type": "honor",
                        "requirements": ["crafting", "stone_working", "artistic_skill"]
                    }
                ])
        
        return quest_opportunities
    
    def calculate_population_effects(self, population_id: str, base_population: int) -> Dict[str, float]:
        """
        Calculate the effects of diseases on population metrics
        
        Returns:
            Dict with effect multipliers for various population metrics
        """
        if population_id not in self.active_outbreaks:
            return {
                "productivity_multiplier": 1.0,
                "morale_multiplier": 1.0,
                "growth_rate_multiplier": 1.0,
                "migration_pressure": 0.0
            }
        
        total_infected = sum(outbreak.infected_count for outbreak in self.active_outbreaks[population_id])
        total_deaths = sum(outbreak.total_deaths for outbreak in self.active_outbreaks[population_id])
        
        if base_population == 0:
            return {
                "productivity_multiplier": 0.0,
                "morale_multiplier": 0.0,
                "growth_rate_multiplier": 0.0,
                "migration_pressure": 1.0
            }
        
        infection_rate = total_infected / base_population
        death_rate = total_deaths / base_population
        
        # Calculate effects
        productivity_multiplier = max(0.1, 1.0 - (infection_rate * 0.8) - (death_rate * 0.5))
        morale_multiplier = max(0.1, 1.0 - (infection_rate * 0.6) - (death_rate * 0.9))
        growth_rate_multiplier = max(0.0, 1.0 - (infection_rate * 0.4) - (death_rate * 1.2))
        
        # Migration pressure increases with outbreak severity
        migration_pressure = min(1.0, (infection_rate * 0.7) + (death_rate * 0.8))
        
        # Check for panic-inducing outbreaks
        for outbreak in self.active_outbreaks[population_id]:
            if outbreak.stage in [DiseaseStage.PEAK] and outbreak.get_profile().mortality_rate > 0.3:
                migration_pressure = min(1.0, migration_pressure + 0.3)
        
        return {
            "productivity_multiplier": productivity_multiplier,
            "morale_multiplier": morale_multiplier,
            "growth_rate_multiplier": growth_rate_multiplier,
            "migration_pressure": migration_pressure
        }
    
    def _calculate_seasonal_modifier(self, profile: DiseaseProfile, current_season: Optional[str]) -> float:
        """Calculate seasonal modifier for disease transmission"""
        if not profile.seasonal_preference or not current_season:
            return 1.0
        
        if current_season.lower() == profile.seasonal_preference.lower():
            return profile.seasonal_multiplier
        
        return 1.0
    
    def _calculate_disease_stage(self, outbreak: DiseaseOutbreak, total_population: int) -> DiseaseStage:
        """Calculate the current stage of a disease outbreak"""
        profile = outbreak.get_profile()
        infection_rate = outbreak.infected_count / max(1, total_population)
        
        if outbreak.days_active < 3:
            return DiseaseStage.EMERGING
        elif infection_rate < 0.01:  # Less than 1% infected
            if outbreak.days_active > profile.recovery_days * 2:
                return DiseaseStage.ERADICATED
            else:
                return DiseaseStage.DECLINING
        elif infection_rate < 0.05:  # Less than 5% infected
            return DiseaseStage.SPREADING
        elif infection_rate < 0.15:  # Less than 15% infected
            return DiseaseStage.PEAK
        else:  # More than 15% infected
            return DiseaseStage.PEAK


# Global disease engine instance
DISEASE_ENGINE = DiseaseModelingEngine()


def introduce_random_disease_outbreak(
    population_id: str,
    population_size: int,
    environmental_factors: Optional[Dict[str, float]] = None
) -> Optional[DiseaseOutbreak]:
    """
    Randomly introduce a disease outbreak based on population conditions
    
    Args:
        population_id: ID of the population
        population_size: Size of the population
        environmental_factors: Environmental conditions affecting disease chance
        
    Returns:
        DiseaseOutbreak if one was introduced, None otherwise
    """
    # Base chance of disease outbreak (per day)
    base_chance = 0.001  # 0.1% chance per day
    
    # Modify chance based on environmental factors
    env_factors = environmental_factors or {}
    chance_modifier = 1.0
    
    # Poor conditions increase chance
    if env_factors.get('crowding', 1.0) > 1.0:
        chance_modifier *= env_factors['crowding']
    if env_factors.get('hygiene', 1.0) > 1.0:
        chance_modifier *= env_factors['hygiene']
    if env_factors.get('healthcare', 1.0) < 1.0:
        chance_modifier *= (2.0 - env_factors['healthcare'])
    
    # Larger populations have higher chance
    population_modifier = math.log10(max(10, population_size)) / 4.0
    
    final_chance = base_chance * chance_modifier * population_modifier
    
    if random.random() < final_chance:
        # Choose random disease type
        disease_type = random.choice(list(DiseaseType))
        
        # Calculate initial infected based on population size
        initial_infected = max(1, int(population_size * random.uniform(0.001, 0.01)))
        
        return DISEASE_ENGINE.introduce_disease(
            population_id, disease_type, initial_infected, environmental_factors
        )
    
    return None


def apply_disease_effects_to_population(
    population_id: str,
    base_population: int,
    time_days: int = 1,
    environmental_factors: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Apply disease effects to a population over time
    
    Args:
        population_id: ID of the population
        base_population: Base population count
        time_days: Number of days to simulate
        environmental_factors: Environmental conditions
        
    Returns:
        Dict with population changes and disease status
    """
    total_deaths = 0
    daily_reports = []
    
    current_population = base_population
    
    for day in range(time_days):
        # Progress existing diseases
        day_result = DISEASE_ENGINE.progress_disease_day(
            population_id, current_population, environmental_factors
        )
        
        # Apply deaths to population
        current_population = max(0, current_population - day_result['new_deaths'])
        total_deaths += day_result['new_deaths']
        
        daily_reports.append({
            "day": day + 1,
            "population": current_population,
            "new_deaths": day_result['new_deaths'],
            "total_infected": day_result['total_infected'],
            "active_outbreaks": day_result['active_outbreaks']
        })
        
        # Chance for new disease outbreak
        if random.random() < 0.01:  # 1% chance per day for new outbreak
            new_outbreak = introduce_random_disease_outbreak(
                population_id, current_population, environmental_factors
            )
            if new_outbreak:
                logger.info(f"New disease outbreak: {new_outbreak.get_profile().name}")
    
    # Get final disease status
    disease_status = DISEASE_ENGINE.get_disease_status(population_id)
    population_effects = DISEASE_ENGINE.calculate_population_effects(population_id, current_population)
    quest_opportunities = DISEASE_ENGINE.generate_quest_opportunities(population_id)
    
    return {
        "starting_population": base_population,
        "ending_population": current_population,
        "total_deaths": total_deaths,
        "population_change": current_population - base_population,
        "daily_reports": daily_reports,
        "disease_status": disease_status,
        "population_effects": population_effects,
        "quest_opportunities": quest_opportunities,
        "simulation_days": time_days
    } 