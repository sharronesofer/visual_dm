"""
Rumor Campaign Management System

This module provides coordinated rumor campaign management with strategic
deployment, analytics, and multi-phase campaign orchestration.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

from backend.systems.rumor.services.content_generator import ProceduralRumorGenerator, RumorCategory
from backend.systems.rumor.services.advanced_mutation import AdvancedContentMutator, MutationContext
from backend.systems.rumor.services.autonomous_spreader import AutonomousRumorSpreader

logger = logging.getLogger(__name__)


class CampaignType(Enum):
    """Types of rumor campaigns"""
    REPUTATION_BUILDING = "reputation_building"
    REPUTATION_DESTRUCTION = "reputation_destruction"
    INFORMATION_SEEDING = "information_seeding"
    DISINFORMATION = "disinformation"
    COUNTER_NARRATIVE = "counter_narrative"
    SOCIAL_MANIPULATION = "social_manipulation"
    POLITICAL_INFLUENCE = "political_influence"
    ECONOMIC_DISRUPTION = "economic_disruption"


class CampaignPhase(Enum):
    """Phases of campaign execution"""
    PLANNING = "planning"
    PREPARATION = "preparation"
    SEEDING = "seeding"
    AMPLIFICATION = "amplification"
    MAINTENANCE = "maintenance"
    CONCLUSION = "conclusion"
    ANALYSIS = "analysis"


class CampaignPriority(Enum):
    """Campaign priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CampaignObjective:
    """Specific objective within a campaign"""
    objective_id: str
    description: str
    target_entity: str
    success_metrics: Dict[str, float]
    priority: CampaignPriority = CampaignPriority.MEDIUM
    completed: bool = False
    completion_date: Optional[datetime] = None


@dataclass
class CampaignPhaseConfig:
    """Configuration for a campaign phase"""
    phase: CampaignPhase
    duration_hours: float
    rumor_generation_rate: float  # rumors per hour
    target_spread_rate: float     # spread attempts per rumor per hour
    content_themes: List[str]
    mutation_intensity: float = 0.5
    geographic_focus: List[str] = field(default_factory=list)
    demographic_focus: List[str] = field(default_factory=list)


@dataclass
class RumorCampaign:
    """Comprehensive rumor campaign definition"""
    campaign_id: str
    name: str
    campaign_type: CampaignType
    orchestrator_id: str
    objectives: List[CampaignObjective]
    phases: List[CampaignPhaseConfig]
    
    # Campaign parameters
    total_budget: float
    spent_budget: float = 0.0
    target_audience: List[str] = field(default_factory=list)
    blacklisted_targets: List[str] = field(default_factory=list)
    
    # Status tracking
    current_phase: CampaignPhase = CampaignPhase.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = False
    
    # Generated content
    generated_rumors: List[str] = field(default_factory=list)
    rumor_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Analytics
    effectiveness_metrics: Dict[str, float] = field(default_factory=dict)
    phase_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.phases:
            self.phases = self._generate_default_phases()
    
    def _generate_default_phases(self) -> List[CampaignPhaseConfig]:
        """Generate default phase configuration"""
        return [
            CampaignPhaseConfig(
                phase=CampaignPhase.SEEDING,
                duration_hours=24,
                rumor_generation_rate=0.5,
                target_spread_rate=2.0,
                content_themes=["introduction", "setup"]
            ),
            CampaignPhaseConfig(
                phase=CampaignPhase.AMPLIFICATION,
                duration_hours=72,
                rumor_generation_rate=1.0,
                target_spread_rate=4.0,
                content_themes=["amplification", "evidence"]
            ),
            CampaignPhaseConfig(
                phase=CampaignPhase.MAINTENANCE,
                duration_hours=120,
                rumor_generation_rate=0.3,
                target_spread_rate=1.5,
                content_themes=["reinforcement", "variation"]
            )
        ]


class CampaignManager:
    """Manages rumor campaigns and orchestrates their execution"""
    
    def __init__(self):
        self.active_campaigns: Dict[str, RumorCampaign] = {}
        self.completed_campaigns: Dict[str, RumorCampaign] = {}
        self.campaign_templates: Dict[str, Dict] = {}
        
        # Integration with other systems
        self.content_generator = ProceduralRumorGenerator()
        self.content_mutator = AdvancedContentMutator()
        self.autonomous_spreader = AutonomousRumorSpreader()
        
        self.campaign_rules = self._load_campaign_rules()
        
    def _load_campaign_rules(self) -> Dict[str, Dict]:
        """Load campaign management rules and templates"""
        return {
            "campaign_templates": {
                CampaignType.REPUTATION_BUILDING.value: {
                    "default_phases": [
                        {
                            "phase": CampaignPhase.SEEDING.value,
                            "duration_hours": 48,
                            "themes": ["positive_actions", "achievements", "reliability"],
                            "mutation_intensity": 0.3
                        },
                        {
                            "phase": CampaignPhase.AMPLIFICATION.value,
                            "duration_hours": 96,
                            "themes": ["success_stories", "endorsements", "community_support"],
                            "mutation_intensity": 0.4
                        },
                        {
                            "phase": CampaignPhase.MAINTENANCE.value,
                            "duration_hours": 240,
                            "themes": ["consistency", "ongoing_good_works"],
                            "mutation_intensity": 0.2
                        }
                    ],
                    "success_metrics": ["reputation_increase", "positive_sentiment", "credibility_boost"]
                },
                
                CampaignType.REPUTATION_DESTRUCTION.value: {
                    "default_phases": [
                        {
                            "phase": CampaignPhase.SEEDING.value,
                            "duration_hours": 24,
                            "themes": ["minor_failures", "questionable_decisions"],
                            "mutation_intensity": 0.5
                        },
                        {
                            "phase": CampaignPhase.AMPLIFICATION.value,
                            "duration_hours": 72,
                            "themes": ["scandals", "betrayals", "incompetence"],
                            "mutation_intensity": 0.7
                        },
                        {
                            "phase": CampaignPhase.MAINTENANCE.value,
                            "duration_hours": 168,
                            "themes": ["ongoing_problems", "pattern_reinforcement"],
                            "mutation_intensity": 0.6
                        }
                    ],
                    "success_metrics": ["reputation_decrease", "negative_sentiment", "trust_erosion"]
                },
                
                CampaignType.DISINFORMATION.value: {
                    "default_phases": [
                        {
                            "phase": CampaignPhase.PREPARATION.value,
                            "duration_hours": 12,
                            "themes": ["groundwork", "context_building"],
                            "mutation_intensity": 0.4
                        },
                        {
                            "phase": CampaignPhase.SEEDING.value,
                            "duration_hours": 36,
                            "themes": ["false_information", "misleading_context"],
                            "mutation_intensity": 0.6
                        },
                        {
                            "phase": CampaignPhase.AMPLIFICATION.value,
                            "duration_hours": 84,
                            "themes": ["supporting_evidence", "confirmation"],
                            "mutation_intensity": 0.8
                        }
                    ],
                    "success_metrics": ["false_belief_adoption", "confusion_level", "truth_displacement"]
                }
            },
            
            "effectiveness_factors": {
                "content_quality": 0.25,
                "timing": 0.20,
                "target_receptivity": 0.20,
                "resource_investment": 0.15,
                "execution_skill": 0.10,
                "environmental_factors": 0.10
            },
            
            "budget_allocation": {
                "content_generation": 0.30,
                "distribution": 0.40,
                "monitoring": 0.15,
                "contingency": 0.15
            }
        }
    
    def create_campaign(
        self,
        name: str,
        campaign_type: CampaignType,
        orchestrator_id: str,
        objectives: List[CampaignObjective],
        budget: float,
        **kwargs
    ) -> RumorCampaign:
        """Create a new rumor campaign"""
        
        # Generate unique campaign ID
        campaign_id = f"{campaign_type.value}_{orchestrator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate phases from template if not provided
        custom_phases = kwargs.get("phases")
        if not custom_phases:
            custom_phases = self._generate_phases_from_template(campaign_type)
        
        campaign = RumorCampaign(
            campaign_id=campaign_id,
            name=name,
            campaign_type=campaign_type,
            orchestrator_id=orchestrator_id,
            objectives=objectives,
            phases=custom_phases,
            total_budget=budget,
            target_audience=kwargs.get("target_audience", []),
            blacklisted_targets=kwargs.get("blacklisted_targets", [])
        )
        
        logger.info(f"Created campaign: {name} ({campaign_id})")
        return campaign
    
    def _generate_phases_from_template(self, campaign_type: CampaignType) -> List[CampaignPhaseConfig]:
        """Generate campaign phases from template"""
        
        template = self.campaign_rules["campaign_templates"].get(campaign_type.value, {})
        phase_templates = template.get("default_phases", [])
        
        phases = []
        for phase_template in phase_templates:
            phase_config = CampaignPhaseConfig(
                phase=CampaignPhase(phase_template["phase"]),
                duration_hours=phase_template["duration_hours"],
                rumor_generation_rate=phase_template.get("rumor_generation_rate", 0.5),
                target_spread_rate=phase_template.get("target_spread_rate", 2.0),
                content_themes=phase_template["themes"],
                mutation_intensity=phase_template.get("mutation_intensity", 0.5)
            )
            phases.append(phase_config)
        
        return phases
    
    def launch_campaign(self, campaign: RumorCampaign) -> bool:
        """Launch an active campaign"""
        
        # Validate campaign
        if not self._validate_campaign(campaign):
            logger.error(f"Campaign validation failed: {campaign.campaign_id}")
            return False
        
        # Activate campaign
        campaign.is_active = True
        campaign.start_date = datetime.now()
        campaign.current_phase = campaign.phases[0].phase if campaign.phases else CampaignPhase.PLANNING
        
        # Store in active campaigns
        self.active_campaigns[campaign.campaign_id] = campaign
        
        # Initialize first phase
        self._initialize_campaign_phase(campaign, campaign.current_phase)
        
        logger.info(f"Launched campaign: {campaign.campaign_id}")
        return True
    
    def _validate_campaign(self, campaign: RumorCampaign) -> bool:
        """Validate campaign configuration"""
        
        # Check basic requirements
        if not campaign.objectives:
            logger.error("Campaign must have at least one objective")
            return False
        
        if campaign.total_budget <= 0:
            logger.error("Campaign must have positive budget")
            return False
        
        if not campaign.phases:
            logger.error("Campaign must have at least one phase")
            return False
        
        # Check budget allocation
        estimated_cost = self._estimate_campaign_cost(campaign)
        if estimated_cost > campaign.total_budget * 1.1:  # 10% buffer
            logger.warning(f"Campaign estimated cost ({estimated_cost}) exceeds budget ({campaign.total_budget})")
        
        return True
    
    def _estimate_campaign_cost(self, campaign: RumorCampaign) -> float:
        """Estimate total campaign cost"""
        
        total_cost = 0.0
        budget_rules = self.campaign_rules["budget_allocation"]
        
        for phase in campaign.phases:
            # Calculate phase duration cost
            phase_duration_hours = phase.duration_hours
            rumor_generation_cost = phase_duration_hours * phase.rumor_generation_rate * 10  # $10 per rumor
            distribution_cost = phase_duration_hours * phase.target_spread_rate * 5  # $5 per spread attempt
            
            phase_cost = rumor_generation_cost + distribution_cost
            total_cost += phase_cost
        
        # Add overhead costs
        overhead_multiplier = 1.0 + budget_rules["monitoring"] + budget_rules["contingency"]
        total_cost *= overhead_multiplier
        
        return total_cost
    
    def _initialize_campaign_phase(self, campaign: RumorCampaign, phase: CampaignPhase):
        """Initialize a new campaign phase"""
        
        # Find phase configuration
        phase_config = None
        for config in campaign.phases:
            if config.phase == phase:
                phase_config = config
                break
        
        if not phase_config:
            logger.error(f"Phase configuration not found: {phase.value}")
            return
        
        # Record phase start
        phase_record = {
            "phase": phase.value,
            "start_time": datetime.now().isoformat(),
            "configuration": {
                "duration_hours": phase_config.duration_hours,
                "rumor_generation_rate": phase_config.rumor_generation_rate,
                "target_spread_rate": phase_config.target_spread_rate,
                "content_themes": phase_config.content_themes,
                "mutation_intensity": phase_config.mutation_intensity
            }
        }
        
        campaign.phase_history.append(phase_record)
        
        # Generate initial batch of rumors for the phase
        initial_rumors = self._generate_phase_rumors(campaign, phase_config, batch_size=3)
        campaign.generated_rumors.extend(initial_rumors)
        
        logger.info(f"Initialized phase {phase.value} for campaign {campaign.campaign_id}")
    
    def _generate_phase_rumors(
        self,
        campaign: RumorCampaign,
        phase_config: CampaignPhaseConfig,
        batch_size: int = 1
    ) -> List[str]:
        """Generate rumors for a specific campaign phase"""
        
        rumors = []
        
        for _ in range(batch_size):
            # Select theme for this rumor
            theme = random.choice(phase_config.content_themes) if phase_config.content_themes else "general"
            
            # Generate base rumor content
            base_rumor = self._generate_thematic_rumor(campaign, theme)
            
            # Apply mutation based on phase configuration
            mutation_context = MutationContext(
                spreader_personality=self._get_campaign_personality(campaign),
                social_pressure=0.7,
                mutation_count=0
            )
            
            mutated_rumor, mutations = self.content_mutator.mutate_content(
                base_rumor,
                mutation_context,
                mutation_intensity=phase_config.mutation_intensity
            )
            
            rumors.append(mutated_rumor)
        
        return rumors
    
    def _generate_thematic_rumor(self, campaign: RumorCampaign, theme: str) -> str:
        """Generate rumor content based on campaign and theme"""
        
        # Theme-based rumor templates
        theme_templates = {
            "positive_actions": [
                "{target} has been secretly helping the poor in {location}",
                "{target} donated a large sum to rebuild {location}",
                "{target} saved {location} from disaster through quick thinking"
            ],
            "negative_actions": [
                "{target} was seen taking bribes in {location}",
                "{target} abandoned their duties during the crisis at {location}",
                "{target} is plotting against the people of {location}"
            ],
            "scandals": [
                "{target} is having a secret affair with {person}",
                "{target} has been embezzling funds meant for {cause}",
                "{target} betrayed their closest ally for personal gain"
            ],
            "achievements": [
                "{target} single-handedly negotiated the peace treaty",
                "{target} discovered the cure for the plague affecting {location}",
                "{target} led the successful defense of {location}"
            ],
            "failures": [
                "{target} failed to prevent the attack on {location}",
                "{target}'s poor planning led to the loss at {location}",
                "{target} ignored warnings about the threat to {location}"
            ]
        }
        
        # Get primary objective target
        primary_target = "someone"
        if campaign.objectives:
            primary_target = campaign.objectives[0].target_entity
        
        # Select template based on theme
        templates = theme_templates.get(theme, [
            "{target} is involved in mysterious activities",
            "Strange things are happening around {target}",
            "{target} has been acting suspiciously lately"
        ])
        
        template = random.choice(templates)
        
        # Fill template
        content = template.replace("{target}", primary_target)
        content = content.replace("{location}", random.choice(["the marketplace", "the castle", "the village", "the border"]))
        content = content.replace("{person}", random.choice(["a merchant", "a noble", "a commoner", "a stranger"]))
        content = content.replace("{cause}", random.choice(["orphans", "the military", "infrastructure", "education"]))
        
        return content
    
    def _get_campaign_personality(self, campaign: RumorCampaign) -> str:
        """Determine personality style for campaign content"""
        
        personality_mapping = {
            CampaignType.REPUTATION_BUILDING: "diplomatic",
            CampaignType.REPUTATION_DESTRUCTION: "vindictive",
            CampaignType.DISINFORMATION: "strategic",
            CampaignType.SOCIAL_MANIPULATION: "gossipy",
            CampaignType.POLITICAL_INFLUENCE: "authoritative",
            CampaignType.COUNTER_NARRATIVE: "defensive"
        }
        
        return personality_mapping.get(campaign.campaign_type, "neutral")
    
    def process_campaign_cycle(self, campaign_id: str) -> Dict[str, Any]:
        """Process one cycle of campaign execution (hourly)"""
        
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}
        
        if not campaign.is_active:
            return {"status": "Campaign not active"}
        
        # Check if current phase should end
        current_phase_config = self._get_current_phase_config(campaign)
        if not current_phase_config:
            return {"error": "No current phase configuration"}
        
        # Check phase duration
        phase_start_time = self._get_current_phase_start_time(campaign)
        if phase_start_time:
            elapsed_hours = (datetime.now() - phase_start_time).total_seconds() / 3600
            
            if elapsed_hours >= current_phase_config.duration_hours:
                # Move to next phase
                next_phase_result = self._advance_to_next_phase(campaign)
                if next_phase_result.get("campaign_completed"):
                    return next_phase_result
        
        # Generate new rumors for current cycle
        new_rumors = self._generate_phase_rumors(campaign, current_phase_config, batch_size=1)
        campaign.generated_rumors.extend(new_rumors)
        
        # Process rumor spreading
        spread_results = self._process_rumor_spreading(campaign, current_phase_config)
        
        # Update campaign metrics
        cycle_metrics = self._calculate_cycle_effectiveness(campaign, spread_results)
        
        # Update budget
        cycle_cost = self._calculate_cycle_cost(current_phase_config)
        campaign.spent_budget += cycle_cost
        
        return {
            "campaign_id": campaign_id,
            "current_phase": campaign.current_phase.value,
            "new_rumors_generated": len(new_rumors),
            "rumors_spread": spread_results.get("total_spreads", 0),
            "cycle_effectiveness": cycle_metrics,
            "budget_spent": cycle_cost,
            "remaining_budget": campaign.total_budget - campaign.spent_budget
        }
    
    def _get_current_phase_config(self, campaign: RumorCampaign) -> Optional[CampaignPhaseConfig]:
        """Get configuration for current campaign phase"""
        
        for config in campaign.phases:
            if config.phase == campaign.current_phase:
                return config
        return None
    
    def _get_current_phase_start_time(self, campaign: RumorCampaign) -> Optional[datetime]:
        """Get start time of current phase"""
        
        if not campaign.phase_history:
            return campaign.start_date
        
        # Find the most recent phase entry
        for phase_record in reversed(campaign.phase_history):
            if phase_record["phase"] == campaign.current_phase.value:
                return datetime.fromisoformat(phase_record["start_time"])
        
        return campaign.start_date
    
    def _advance_to_next_phase(self, campaign: RumorCampaign) -> Dict[str, Any]:
        """Advance campaign to next phase"""
        
        # Find current phase index
        current_index = -1
        for i, config in enumerate(campaign.phases):
            if config.phase == campaign.current_phase:
                current_index = i
                break
        
        # Check if campaign is complete
        if current_index >= len(campaign.phases) - 1:
            return self._complete_campaign(campaign)
        
        # Move to next phase
        next_phase_config = campaign.phases[current_index + 1]
        campaign.current_phase = next_phase_config.phase
        
        # Initialize next phase
        self._initialize_campaign_phase(campaign, next_phase_config.phase)
        
        logger.info(f"Advanced campaign {campaign.campaign_id} to phase {next_phase_config.phase.value}")
        
        return {
            "phase_advanced": True,
            "new_phase": next_phase_config.phase.value,
            "campaign_completed": False
        }
    
    def _complete_campaign(self, campaign: RumorCampaign) -> Dict[str, Any]:
        """Complete a campaign and move to analysis"""
        
        campaign.is_active = False
        campaign.end_date = datetime.now()
        campaign.current_phase = CampaignPhase.ANALYSIS
        
        # Calculate final metrics
        final_metrics = self._calculate_final_campaign_metrics(campaign)
        campaign.effectiveness_metrics.update(final_metrics)
        
        # Evaluate objectives
        objective_results = self._evaluate_campaign_objectives(campaign)
        
        # Move to completed campaigns
        self.completed_campaigns[campaign.campaign_id] = campaign
        del self.active_campaigns[campaign.campaign_id]
        
        logger.info(f"Completed campaign: {campaign.campaign_id}")
        
        return {
            "campaign_completed": True,
            "final_metrics": final_metrics,
            "objective_results": objective_results,
            "total_duration": (campaign.end_date - campaign.start_date).total_seconds() / 3600,
            "total_rumors_generated": len(campaign.generated_rumors),
            "budget_utilization": (campaign.spent_budget / campaign.total_budget) * 100
        }
    
    def _process_rumor_spreading(
        self, 
        campaign: RumorCampaign, 
        phase_config: CampaignPhaseConfig
    ) -> Dict[str, Any]:
        """Process rumor spreading for current cycle"""
        
        spread_results = {
            "total_spreads": 0,
            "successful_spreads": 0,
            "target_reactions": {}
        }
        
        # Get recent rumors (last 10)
        recent_rumors = campaign.generated_rumors[-10:] if len(campaign.generated_rumors) > 10 else campaign.generated_rumors
        
        for rumor in recent_rumors:
            # Calculate spread attempts for this cycle
            spread_attempts = int(phase_config.target_spread_rate)
            
            for _ in range(spread_attempts):
                # Simulate rumor spread
                spread_success = random.random() < 0.7  # 70% base success rate
                
                spread_results["total_spreads"] += 1
                if spread_success:
                    spread_results["successful_spreads"] += 1
        
        return spread_results
    
    def _calculate_cycle_effectiveness(
        self, 
        campaign: RumorCampaign, 
        spread_results: Dict[str, Any]
    ) -> float:
        """Calculate effectiveness for current cycle"""
        
        # Base effectiveness from spread success
        spread_rate = spread_results["successful_spreads"] / max(1, spread_results["total_spreads"])
        
        # Factor in campaign type effectiveness
        type_multipliers = {
            CampaignType.REPUTATION_BUILDING: 0.8,      # Slower but steady
            CampaignType.REPUTATION_DESTRUCTION: 1.2,   # Faster negative spread
            CampaignType.DISINFORMATION: 1.0,           # Standard spread
            CampaignType.SOCIAL_MANIPULATION: 1.1,      # Slightly enhanced
            CampaignType.POLITICAL_INFLUENCE: 0.9       # More resistance
        }
        
        type_multiplier = type_multipliers.get(campaign.campaign_type, 1.0)
        
        effectiveness = spread_rate * type_multiplier
        
        # Apply budget constraints
        budget_factor = min(1.0, (campaign.total_budget - campaign.spent_budget) / campaign.total_budget)
        effectiveness *= (0.5 + budget_factor * 0.5)  # Effectiveness decreases as budget depletes
        
        return min(1.0, max(0.0, effectiveness))
    
    def _calculate_cycle_cost(self, phase_config: CampaignPhaseConfig) -> float:
        """Calculate cost for current cycle"""
        
        # Base costs
        rumor_generation_cost = phase_config.rumor_generation_rate * 10  # $10 per rumor
        spreading_cost = phase_config.target_spread_rate * 5             # $5 per spread attempt
        
        # Phase-specific multipliers
        phase_multipliers = {
            CampaignPhase.PREPARATION: 0.8,
            CampaignPhase.SEEDING: 1.0,
            CampaignPhase.AMPLIFICATION: 1.5,
            CampaignPhase.MAINTENANCE: 0.7,
            CampaignPhase.CONCLUSION: 0.5
        }
        
        multiplier = phase_multipliers.get(phase_config.phase, 1.0)
        
        total_cost = (rumor_generation_cost + spreading_cost) * multiplier
        
        return total_cost
    
    def _calculate_final_campaign_metrics(self, campaign: RumorCampaign) -> Dict[str, float]:
        """Calculate final campaign effectiveness metrics"""
        
        if not campaign.start_date or not campaign.end_date:
            return {}
        
        total_duration_hours = (campaign.end_date - campaign.start_date).total_seconds() / 3600
        
        metrics = {
            "total_duration_hours": total_duration_hours,
            "rumors_per_hour": len(campaign.generated_rumors) / max(1, total_duration_hours),
            "budget_efficiency": len(campaign.generated_rumors) / max(1, campaign.spent_budget),
            "phase_completion_rate": len([p for p in campaign.phase_history]) / max(1, len(campaign.phases)),
            "overall_effectiveness": self._calculate_overall_effectiveness(campaign)
        }
        
        return metrics
    
    def _calculate_overall_effectiveness(self, campaign: RumorCampaign) -> float:
        """Calculate overall campaign effectiveness"""
        
        # Factors contributing to effectiveness
        factors = {
            "objective_completion": self._calculate_objective_completion_rate(campaign),
            "budget_utilization": min(1.0, campaign.spent_budget / campaign.total_budget),
            "content_generation": min(1.0, len(campaign.generated_rumors) / 50),  # Normalize to 50 rumors
            "phase_execution": len(campaign.phase_history) / max(1, len(campaign.phases))
        }
        
        # Weighted combination
        weights = self.campaign_rules["effectiveness_factors"]
        
        effectiveness = (
            factors["objective_completion"] * weights.get("content_quality", 0.25) +
            factors["budget_utilization"] * weights.get("resource_investment", 0.25) +
            factors["content_generation"] * weights.get("execution_skill", 0.25) +
            factors["phase_execution"] * weights.get("timing", 0.25)
        )
        
        return min(1.0, max(0.0, effectiveness))
    
    def _calculate_objective_completion_rate(self, campaign: RumorCampaign) -> float:
        """Calculate what percentage of objectives were completed"""
        
        if not campaign.objectives:
            return 0.0
        
        completed_objectives = sum(1 for obj in campaign.objectives if obj.completed)
        return completed_objectives / len(campaign.objectives)
    
    def _evaluate_campaign_objectives(self, campaign: RumorCampaign) -> Dict[str, Any]:
        """Evaluate whether campaign objectives were met"""
        
        results = {
            "total_objectives": len(campaign.objectives),
            "completed_objectives": 0,
            "objective_details": []
        }
        
        for objective in campaign.objectives:
            # Simulate objective evaluation (in real implementation, this would check actual metrics)
            completion_probability = 0.7  # Base 70% chance
            
            # Adjust based on campaign effectiveness
            overall_effectiveness = campaign.effectiveness_metrics.get("overall_effectiveness", 0.5)
            completion_probability *= (0.5 + overall_effectiveness * 0.5)
            
            # Adjust based on priority
            priority_multipliers = {
                CampaignPriority.CRITICAL: 1.2,
                CampaignPriority.HIGH: 1.1,
                CampaignPriority.MEDIUM: 1.0,
                CampaignPriority.LOW: 0.9
            }
            completion_probability *= priority_multipliers.get(objective.priority, 1.0)
            
            completed = random.random() < completion_probability
            
            if completed:
                objective.completed = True
                objective.completion_date = campaign.end_date
                results["completed_objectives"] += 1
            
            results["objective_details"].append({
                "objective_id": objective.objective_id,
                "description": objective.description,
                "completed": completed,
                "priority": objective.priority.value,
                "target_entity": objective.target_entity
            })
        
        return results
    
    def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive status of a campaign"""
        
        campaign = self.active_campaigns.get(campaign_id) or self.completed_campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # Current phase information
        current_phase_info = None
        if campaign.is_active:
            current_phase_config = self._get_current_phase_config(campaign)
            phase_start_time = self._get_current_phase_start_time(campaign)
            
            if current_phase_config and phase_start_time:
                elapsed_hours = (datetime.now() - phase_start_time).total_seconds() / 3600
                current_phase_info = {
                    "phase": campaign.current_phase.value,
                    "elapsed_hours": round(elapsed_hours, 2),
                    "total_duration_hours": current_phase_config.duration_hours,
                    "progress_percentage": min(100, (elapsed_hours / current_phase_config.duration_hours) * 100),
                    "rumor_generation_rate": current_phase_config.rumor_generation_rate,
                    "themes": current_phase_config.content_themes
                }
        
        return {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "type": campaign.campaign_type.value,
            "orchestrator": campaign.orchestrator_id,
            "status": {
                "is_active": campaign.is_active,
                "current_phase": campaign.current_phase.value,
                "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                "end_date": campaign.end_date.isoformat() if campaign.end_date else None
            },
            "current_phase_info": current_phase_info,
            "objectives": {
                "total": len(campaign.objectives),
                "completed": sum(1 for obj in campaign.objectives if obj.completed),
                "details": [
                    {
                        "id": obj.objective_id,
                        "description": obj.description,
                        "target": obj.target_entity,
                        "priority": obj.priority.value,
                        "completed": obj.completed
                    }
                    for obj in campaign.objectives
                ]
            },
            "resources": {
                "total_budget": campaign.total_budget,
                "spent_budget": campaign.spent_budget,
                "remaining_budget": campaign.total_budget - campaign.spent_budget,
                "budget_utilization_percentage": (campaign.spent_budget / campaign.total_budget) * 100
            },
            "content": {
                "total_rumors_generated": len(campaign.generated_rumors),
                "phases_completed": len(campaign.phase_history),
                "total_phases": len(campaign.phases)
            },
            "effectiveness_metrics": campaign.effectiveness_metrics
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide campaign management statistics"""
        
        total_active = len(self.active_campaigns)
        total_completed = len(self.completed_campaigns)
        
        # Campaign type distribution
        type_distribution = {}
        for campaign in list(self.active_campaigns.values()) + list(self.completed_campaigns.values()):
            campaign_type = campaign.campaign_type.value
            type_distribution[campaign_type] = type_distribution.get(campaign_type, 0) + 1
        
        # Success rate analysis
        successful_campaigns = 0
        for campaign in self.completed_campaigns.values():
            if campaign.effectiveness_metrics.get("overall_effectiveness", 0) > 0.6:
                successful_campaigns += 1
        
        success_rate = (successful_campaigns / max(1, total_completed)) * 100
        
        # Phase distribution
        phase_distribution = {}
        for campaign in self.active_campaigns.values():
            phase = campaign.current_phase.value
            phase_distribution[phase] = phase_distribution.get(phase, 0) + 1
        
        return {
            "system_overview": {
                "active_campaigns": total_active,
                "completed_campaigns": total_completed,
                "total_campaigns": total_active + total_completed,
                "success_rate_percentage": round(success_rate, 2)
            },
            "campaign_type_distribution": type_distribution,
            "active_phase_distribution": phase_distribution,
            "performance_metrics": {
                "average_campaign_duration_hours": self._calculate_average_duration(),
                "average_rumors_per_campaign": self._calculate_average_rumor_count(),
                "average_budget_utilization": self._calculate_average_budget_utilization()
            }
        }
    
    def _calculate_average_duration(self) -> float:
        """Calculate average campaign duration"""
        
        durations = []
        for campaign in self.completed_campaigns.values():
            if campaign.start_date and campaign.end_date:
                duration = (campaign.end_date - campaign.start_date).total_seconds() / 3600
                durations.append(duration)
        
        return sum(durations) / max(1, len(durations))
    
    def _calculate_average_rumor_count(self) -> float:
        """Calculate average number of rumors per campaign"""
        
        all_campaigns = list(self.active_campaigns.values()) + list(self.completed_campaigns.values())
        if not all_campaigns:
            return 0.0
        
        total_rumors = sum(len(campaign.generated_rumors) for campaign in all_campaigns)
        return total_rumors / len(all_campaigns)
    
    def _calculate_average_budget_utilization(self) -> float:
        """Calculate average budget utilization percentage"""
        
        utilizations = []
        for campaign in list(self.active_campaigns.values()) + list(self.completed_campaigns.values()):
            if campaign.total_budget > 0:
                utilization = (campaign.spent_budget / campaign.total_budget) * 100
                utilizations.append(utilization)
        
        return sum(utilizations) / max(1, len(utilizations))


# Factory function
def create_campaign_manager() -> CampaignManager:
    """Create campaign manager instance"""
    return CampaignManager() 