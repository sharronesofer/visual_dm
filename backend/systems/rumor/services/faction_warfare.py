"""
Faction Warfare Integration System

This module integrates rumors with faction warfare, enabling coordinated
disinformation campaigns, strategic rumor deployment, and information warfare.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

from backend.systems.rumor.services.content_generator import RumorCategory
from backend.systems.rumor.services.advanced_mutation import AdvancedContentMutator, MutationContext

logger = logging.getLogger(__name__)


class WarfareStrategy(Enum):
    """Types of rumor warfare strategies"""
    DEMORALIZATION = "demoralization"
    RECRUITMENT = "recruitment"
    SABOTAGE = "sabotage"
    PROPAGANDA = "propaganda"
    COUNTER_INTELLIGENCE = "counter_intelligence"
    CONFUSION = "confusion"
    ALLIANCE_DISRUPTION = "alliance_disruption"
    REPUTATION_ATTACK = "reputation_attack"


class CampaignStatus(Enum):
    """Status of disinformation campaigns"""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"


@dataclass
class FactionProfile:
    """Profile of a faction for warfare purposes"""
    faction_id: str
    name: str
    allegiances: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    assets: Dict[str, float] = field(default_factory=dict)  # resources, influence, etc.
    reputation: float = 0.5
    information_warfare_capability: float = 0.5
    counter_intelligence: float = 0.5
    current_morale: float = 0.5
    territory: List[str] = field(default_factory=list)
    strategic_goals: List[str] = field(default_factory=list)


@dataclass
class DisinformationCampaign:
    """Represents a coordinated disinformation campaign"""
    campaign_id: str
    orchestrating_faction: str
    target_faction: str
    strategy: WarfareStrategy
    objectives: List[str]
    rumor_templates: List[str]
    duration_days: int
    resource_investment: float
    status: CampaignStatus = CampaignStatus.PLANNING
    start_date: Optional[datetime] = None
    generated_rumors: List[str] = field(default_factory=list)
    effectiveness_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.start_date is None and self.status == CampaignStatus.ACTIVE:
            self.start_date = datetime.now()


@dataclass
class WarfareAction:
    """Represents a single warfare action"""
    action_id: str
    faction_id: str
    action_type: str
    target: str
    rumor_id: Optional[str] = None
    effectiveness: float = 0.0
    timestamp: Optional[datetime] = None
    consequences: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class FactionWarfareIntegrator:
    """Manages rumor-based faction warfare and disinformation campaigns"""
    
    def __init__(self):
        self.faction_profiles: Dict[str, FactionProfile] = {}
        self.active_campaigns: Dict[str, DisinformationCampaign] = {}
        self.warfare_history: List[WarfareAction] = []
        self.content_mutator = AdvancedContentMutator()
        self.warfare_rules = self._load_warfare_rules()
        
    def _load_warfare_rules(self) -> Dict[str, Dict]:
        """Load rules for faction warfare and disinformation"""
        return {
            "strategy_templates": {
                WarfareStrategy.DEMORALIZATION.value: {
                    "rumor_types": ["military", "political"],
                    "target_themes": ["defeat", "betrayal", "weakness", "abandonment"],
                    "effectiveness_factors": ["target_morale", "source_credibility"],
                    "template_examples": [
                        "The {target_faction} leadership has abandoned their soldiers",
                        "{target_faction} forces are in full retreat from {location}",
                        "Mass desertions reported in {target_faction} ranks",
                        "{target_faction} commanders are planning to surrender"
                    ]
                },
                
                WarfareStrategy.RECRUITMENT.value: {
                    "rumor_types": ["political", "social"],
                    "target_themes": ["opportunity", "glory", "justice", "rewards"],
                    "effectiveness_factors": ["faction_reputation", "resource_display"],
                    "template_examples": [
                        "Join {faction} and receive {reward} for your service",
                        "{faction} is offering land grants to new recruits",
                        "{faction} treats their people better than {enemy_faction}",
                        "Great victories await those who serve {faction}"
                    ]
                },
                
                WarfareStrategy.SABOTAGE.value: {
                    "rumor_types": ["economic", "military"],
                    "target_themes": ["supply_disruption", "internal_conflicts", "equipment_failure"],
                    "effectiveness_factors": ["target_infrastructure", "sabotage_capability"],
                    "template_examples": [
                        "{target_faction} supply lines are completely disrupted",
                        "Weapons shipments to {target_faction} have been intercepted",
                        "Key {target_faction} strongholds are running out of supplies",
                        "{target_faction} equipment is failing due to poor maintenance"
                    ]
                },
                
                WarfareStrategy.PROPAGANDA.value: {
                    "rumor_types": ["political", "social"],
                    "target_themes": ["legitimacy", "divine_favor", "popular_support", "righteousness"],
                    "effectiveness_factors": ["cultural_alignment", "religious_influence"],
                    "template_examples": [
                        "{faction} fights for the true cause of {ideal}",
                        "The gods favor {faction} in this righteous war",
                        "The people rally behind {faction} leadership",
                        "{faction} represents the legitimate government"
                    ]
                },
                
                WarfareStrategy.ALLIANCE_DISRUPTION.value: {
                    "rumor_types": ["political", "social"],
                    "target_themes": ["betrayal", "secret_deals", "conflicting_interests"],
                    "effectiveness_factors": ["alliance_stability", "trust_levels"],
                    "template_examples": [
                        "{ally_faction} is secretly negotiating with {enemy_faction}",
                        "{ally_faction} plans to betray {target_faction} for {reward}",
                        "Disputes between {ally_faction} and {target_faction} escalating",
                        "{ally_faction} demands unfair terms from {target_faction}"
                    ]
                }
            },
            
            "effectiveness_calculations": {
                "base_factors": {
                    "resource_investment": 0.3,
                    "faction_capability": 0.2,
                    "target_vulnerability": 0.2,
                    "strategy_alignment": 0.2,
                    "execution_quality": 0.1
                },
                
                "resistance_factors": {
                    "target_counter_intelligence": 0.4,
                    "target_morale": 0.3,
                    "allied_support": 0.2,
                    "truth_exposure_risk": 0.1
                }
            },
            
            "campaign_costs": {
                WarfareStrategy.DEMORALIZATION.value: 100,
                WarfareStrategy.RECRUITMENT.value: 150,
                WarfareStrategy.SABOTAGE.value: 200,
                WarfareStrategy.PROPAGANDA.value: 120,
                WarfareStrategy.COUNTER_INTELLIGENCE.value: 180,
                WarfareStrategy.ALLIANCE_DISRUPTION.value: 160,
                WarfareStrategy.REPUTATION_ATTACK.value: 140
            }
        }
    
    def register_faction(
        self,
        faction_id: str,
        name: str,
        **kwargs
    ) -> FactionProfile:
        """Register a faction for warfare operations"""
        
        profile = FactionProfile(
            faction_id=faction_id,
            name=name,
            allegiances=kwargs.get("allegiances", []),
            enemies=kwargs.get("enemies", []),
            assets=kwargs.get("assets", {"influence": 100, "resources": 100}),
            reputation=kwargs.get("reputation", 0.5),
            information_warfare_capability=kwargs.get("warfare_capability", 0.5),
            counter_intelligence=kwargs.get("counter_intelligence", 0.5),
            current_morale=kwargs.get("morale", 0.5),
            territory=kwargs.get("territory", []),
            strategic_goals=kwargs.get("goals", [])
        )
        
        self.faction_profiles[faction_id] = profile
        logger.info(f"Registered faction for warfare: {name} ({faction_id})")
        return profile
    
    def plan_disinformation_campaign(
        self,
        orchestrating_faction: str,
        target_faction: str,
        strategy: WarfareStrategy,
        objectives: List[str],
        duration_days: int = 30,
        resource_investment: float = 100.0
    ) -> DisinformationCampaign:
        """Plan a new disinformation campaign"""
        
        if orchestrating_faction not in self.faction_profiles:
            raise ValueError(f"Faction {orchestrating_faction} not registered")
        
        if target_faction not in self.faction_profiles:
            raise ValueError(f"Target faction {target_faction} not registered")
        
        # Generate campaign ID
        campaign_id = f"{orchestrating_faction}_vs_{target_faction}_{strategy.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get strategy-specific rumor templates
        strategy_data = self.warfare_rules["strategy_templates"].get(strategy.value, {})
        rumor_templates = strategy_data.get("template_examples", [])
        
        campaign = DisinformationCampaign(
            campaign_id=campaign_id,
            orchestrating_faction=orchestrating_faction,
            target_faction=target_faction,
            strategy=strategy,
            objectives=objectives,
            rumor_templates=rumor_templates,
            duration_days=duration_days,
            resource_investment=resource_investment
        )
        
        # Validate campaign feasibility
        feasibility = self._assess_campaign_feasibility(campaign)
        if feasibility < 0.3:
            logger.warning(f"Campaign {campaign_id} has low feasibility: {feasibility:.2f}")
        
        logger.info(f"Planned disinformation campaign: {campaign_id}")
        return campaign
    
    def launch_campaign(self, campaign: DisinformationCampaign) -> bool:
        """Launch an active disinformation campaign"""
        
        orchestrating_faction = self.faction_profiles.get(campaign.orchestrating_faction)
        if not orchestrating_faction:
            logger.error(f"Cannot launch campaign - orchestrating faction not found")
            return False
        
        # Check resource availability
        required_resources = self.warfare_rules["campaign_costs"].get(
            campaign.strategy.value, 100
        ) * campaign.resource_investment
        
        available_resources = orchestrating_faction.assets.get("resources", 0)
        if available_resources < required_resources:
            logger.warning(f"Insufficient resources for campaign {campaign.campaign_id}")
            return False
        
        # Deduct resources
        orchestrating_faction.assets["resources"] -= required_resources
        
        # Activate campaign
        campaign.status = CampaignStatus.ACTIVE
        campaign.start_date = datetime.now()
        self.active_campaigns[campaign.campaign_id] = campaign
        
        # Generate initial batch of rumors
        initial_rumors = self._generate_campaign_rumors(campaign, batch_size=3)
        campaign.generated_rumors.extend(initial_rumors)
        
        logger.info(f"Launched disinformation campaign: {campaign.campaign_id}")
        return True
    
    def _assess_campaign_feasibility(self, campaign: DisinformationCampaign) -> float:
        """Assess the feasibility of a disinformation campaign"""
        
        orchestrating_faction = self.faction_profiles.get(campaign.orchestrating_faction)
        target_faction = self.faction_profiles.get(campaign.target_faction)
        
        if not orchestrating_faction or not target_faction:
            return 0.0
        
        # Base feasibility factors
        capability_score = orchestrating_faction.information_warfare_capability
        resource_score = min(1.0, orchestrating_faction.assets.get("resources", 0) / 1000)
        target_vulnerability = 1.0 - target_faction.counter_intelligence
        
        # Strategy-specific modifiers
        strategy_bonus = 0.0
        if campaign.strategy == WarfareStrategy.DEMORALIZATION and target_faction.current_morale < 0.5:
            strategy_bonus = 0.2
        elif campaign.strategy == WarfareStrategy.ALLIANCE_DISRUPTION and len(target_faction.allegiances) > 2:
            strategy_bonus = 0.15
        elif campaign.strategy == WarfareStrategy.PROPAGANDA and orchestrating_faction.reputation > 0.7:
            strategy_bonus = 0.1
        
        # Relationship penalties
        relationship_penalty = 0.0
        if target_faction.faction_id in orchestrating_faction.enemies:
            relationship_penalty = -0.1  # Harder to be believed against known enemies
        
        feasibility = (
            capability_score * 0.4 +
            resource_score * 0.3 +
            target_vulnerability * 0.2 +
            strategy_bonus +
            relationship_penalty
        )
        
        return max(0.0, min(1.0, feasibility))
    
    def _generate_campaign_rumors(
        self, 
        campaign: DisinformationCampaign, 
        batch_size: int = 1
    ) -> List[str]:
        """Generate rumors for a specific campaign"""
        
        rumors = []
        strategy_data = self.warfare_rules["strategy_templates"].get(campaign.strategy.value, {})
        templates = strategy_data.get("template_examples", [])
        
        orchestrating_faction = self.faction_profiles[campaign.orchestrating_faction]
        target_faction = self.faction_profiles[campaign.target_faction]
        
        for _ in range(batch_size):
            if not templates:
                continue
                
            # Select template
            template = random.choice(templates)
            
            # Fill template with faction-specific data
            rumor_content = self._fill_warfare_template(
                template, orchestrating_faction, target_faction, campaign
            )
            
            # Apply mutation based on faction capabilities
            mutation_context = MutationContext(
                spreader_personality="strategic",
                social_pressure=0.8,
                mutation_count=0
            )
            
            mutated_content, mutations = self.content_mutator.mutate_content(
                rumor_content,
                mutation_context,
                mutation_intensity=orchestrating_faction.information_warfare_capability
            )
            
            rumors.append(mutated_content)
        
        return rumors
    
    def _fill_warfare_template(
        self,
        template: str,
        orchestrating_faction: FactionProfile,
        target_faction: FactionProfile,
        campaign: DisinformationCampaign
    ) -> str:
        """Fill warfare rumor template with faction data"""
        
        content = template
        
        # Basic faction substitutions
        content = content.replace("{faction}", orchestrating_faction.name)
        content = content.replace("{target_faction}", target_faction.name)
        
        # Enemy substitutions
        if target_faction.enemies:
            enemy = random.choice(target_faction.enemies)
            enemy_name = self.faction_profiles.get(enemy, type('', (), {'name': enemy})()).name
            content = content.replace("{enemy_faction}", enemy_name)
        
        # Ally substitutions
        if target_faction.allegiances:
            ally = random.choice(target_faction.allegiances)
            ally_name = self.faction_profiles.get(ally, type('', (), {'name': ally})()).name
            content = content.replace("{ally_faction}", ally_name)
        
        # Location substitutions
        if target_faction.territory:
            location = random.choice(target_faction.territory)
            content = content.replace("{location}", location)
        
        # Strategy-specific substitutions
        strategy_substitutions = {
            "{reward}": "gold and land",
            "{ideal}": "freedom and justice",
            "{resource}": "weapons and supplies"
        }
        
        for placeholder, value in strategy_substitutions.items():
            content = content.replace(placeholder, value)
        
        return content
    
    def execute_warfare_action(
        self,
        faction_id: str,
        action_type: str,
        target: str,
        rumor_content: Optional[str] = None
    ) -> WarfareAction:
        """Execute a single warfare action"""
        
        faction = self.faction_profiles.get(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not registered")
        
        # Generate action ID
        action_id = f"{faction_id}_{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate effectiveness
        effectiveness = self._calculate_action_effectiveness(
            faction, action_type, target, rumor_content
        )
        
        # Create action
        action = WarfareAction(
            action_id=action_id,
            faction_id=faction_id,
            action_type=action_type,
            target=target,
            effectiveness=effectiveness
        )
        
        # Apply consequences
        consequences = self._apply_action_consequences(action, rumor_content)
        action.consequences = consequences
        
        # Record action
        self.warfare_history.append(action)
        
        logger.info(f"Executed warfare action: {action_type} by {faction_id} -> {target} (effectiveness: {effectiveness:.2f})")
        return action
    
    def _calculate_action_effectiveness(
        self,
        faction: FactionProfile,
        action_type: str,
        target: str,
        rumor_content: Optional[str]
    ) -> float:
        """Calculate the effectiveness of a warfare action"""
        
        base_effectiveness = faction.information_warfare_capability
        
        # Action type modifiers
        action_modifiers = {
            "rumor_spread": 1.0,
            "counter_propaganda": 0.8,
            "intelligence_gathering": 0.6,
            "sabotage_communications": 1.2
        }
        
        action_modifier = action_modifiers.get(action_type, 1.0)
        
        # Target analysis
        target_faction = self.faction_profiles.get(target)
        resistance = 0.5  # Default resistance
        
        if target_faction:
            resistance = target_faction.counter_intelligence
            
            # Relationship modifiers
            if target in faction.enemies:
                resistance *= 1.2  # Enemies are more resistant
            elif target in faction.allegiances:
                resistance *= 0.7  # Allies are less resistant
        
        # Content quality (if rumor-based action)
        content_quality = 0.5
        if rumor_content:
            content_quality = min(1.0, len(rumor_content) / 100)  # Longer content = higher quality
            
            # Check for strategic keywords
            strategic_keywords = ["victory", "defeat", "betrayal", "alliance", "resources"]
            keyword_bonus = sum(0.1 for keyword in strategic_keywords if keyword in rumor_content.lower())
            content_quality += keyword_bonus
        
        # Combine factors
        effectiveness = (
            base_effectiveness * action_modifier * content_quality * (1.0 - resistance * 0.5)
        )
        
        return max(0.0, min(1.0, effectiveness))
    
    def _apply_action_consequences(
        self, 
        action: WarfareAction, 
        rumor_content: Optional[str]
    ) -> Dict[str, Any]:
        """Apply consequences of a warfare action"""
        
        consequences = {}
        
        executing_faction = self.faction_profiles.get(action.faction_id)
        target_faction = self.faction_profiles.get(action.target)
        
        if not executing_faction:
            return consequences
        
        # Resource costs
        action_costs = {
            "rumor_spread": 10,
            "counter_propaganda": 15,
            "intelligence_gathering": 20,
            "sabotage_communications": 25
        }
        
        cost = action_costs.get(action.action_type, 10) * action.effectiveness
        executing_faction.assets["resources"] = max(0, executing_faction.assets.get("resources", 0) - cost)
        consequences["resource_cost"] = cost
        
        # Target faction effects
        if target_faction and action.effectiveness > 0.5:
            if action.action_type == "rumor_spread":
                # Reduce target morale
                morale_reduction = action.effectiveness * 0.1
                target_faction.current_morale = max(0, target_faction.current_morale - morale_reduction)
                consequences["target_morale_change"] = -morale_reduction
                
            elif action.action_type == "counter_propaganda":
                # Increase own faction reputation
                reputation_boost = action.effectiveness * 0.05
                executing_faction.reputation = min(1.0, executing_faction.reputation + reputation_boost)
                consequences["reputation_change"] = reputation_boost
        
        # Experience gains
        if action.effectiveness > 0.3:
            capability_increase = 0.01 * action.effectiveness
            executing_faction.information_warfare_capability = min(
                1.0, executing_faction.information_warfare_capability + capability_increase
            )
            consequences["capability_increase"] = capability_increase
        
        return consequences
    
    def process_campaign_cycle(self, campaign_id: str) -> Dict[str, Any]:
        """Process one cycle of a campaign (daily update)"""
        
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}
        
        if campaign.status != CampaignStatus.ACTIVE:
            return {"status": "Campaign not active"}
        
        # Check if campaign should end
        if campaign.start_date:
            elapsed_days = (datetime.now() - campaign.start_date).days
            if elapsed_days >= campaign.duration_days:
                return self._conclude_campaign(campaign)
        
        # Generate new rumors for the cycle
        new_rumors = self._generate_campaign_rumors(campaign, batch_size=2)
        campaign.generated_rumors.extend(new_rumors)
        
        # Update effectiveness metrics
        effectiveness = self._calculate_campaign_effectiveness(campaign)
        campaign.effectiveness_metrics[datetime.now().strftime('%Y-%m-%d')] = effectiveness
        
        # Apply campaign effects
        effects = self._apply_campaign_effects(campaign, effectiveness)
        
        return {
            "campaign_id": campaign_id,
            "new_rumors_generated": len(new_rumors),
            "current_effectiveness": effectiveness,
            "effects_applied": effects,
            "status": campaign.status.value
        }
    
    def _calculate_campaign_effectiveness(self, campaign: DisinformationCampaign) -> float:
        """Calculate current effectiveness of a campaign"""
        
        orchestrating_faction = self.faction_profiles.get(campaign.orchestrating_faction)
        target_faction = self.faction_profiles.get(campaign.target_faction)
        
        if not orchestrating_faction or not target_faction:
            return 0.0
        
        # Base effectiveness from faction capabilities
        base_effectiveness = orchestrating_faction.information_warfare_capability
        
        # Resource investment factor
        resource_factor = min(1.0, campaign.resource_investment / 100.0)
        
        # Target resistance
        resistance = target_faction.counter_intelligence
        
        # Campaign duration factor (effectiveness may decrease over time)
        if campaign.start_date:
            elapsed_days = (datetime.now() - campaign.start_date).days
            duration_factor = max(0.3, 1.0 - (elapsed_days / campaign.duration_days) * 0.3)
        else:
            duration_factor = 1.0
        
        # Strategy-specific bonuses
        strategy_multiplier = {
            WarfareStrategy.DEMORALIZATION.value: 1.0 + (1.0 - target_faction.current_morale) * 0.3,
            WarfareStrategy.PROPAGANDA.value: 1.0 + orchestrating_faction.reputation * 0.2,
            WarfareStrategy.ALLIANCE_DISRUPTION.value: 1.0 + len(target_faction.allegiances) * 0.1
        }.get(campaign.strategy.value, 1.0)
        
        effectiveness = (
            base_effectiveness * resource_factor * duration_factor * strategy_multiplier * (1.0 - resistance * 0.4)
        )
        
        return max(0.0, min(1.0, effectiveness))
    
    def _apply_campaign_effects(
        self, 
        campaign: DisinformationCampaign, 
        effectiveness: float
    ) -> Dict[str, Any]:
        """Apply the effects of a campaign based on its effectiveness"""
        
        effects = {}
        
        target_faction = self.faction_profiles.get(campaign.target_faction)
        orchestrating_faction = self.faction_profiles.get(campaign.orchestrating_faction)
        
        if not target_faction or not orchestrating_faction:
            return effects
        
        # Apply strategy-specific effects
        if campaign.strategy == WarfareStrategy.DEMORALIZATION:
            morale_impact = effectiveness * 0.05
            target_faction.current_morale = max(0, target_faction.current_morale - morale_impact)
            effects["target_morale_change"] = -morale_impact
            
        elif campaign.strategy == WarfareStrategy.RECRUITMENT:
            # Boost own faction resources
            recruitment_boost = effectiveness * 20
            orchestrating_faction.assets["influence"] = orchestrating_faction.assets.get("influence", 0) + recruitment_boost
            effects["recruitment_boost"] = recruitment_boost
            
        elif campaign.strategy == WarfareStrategy.REPUTATION_ATTACK:
            reputation_damage = effectiveness * 0.03
            target_faction.reputation = max(0, target_faction.reputation - reputation_damage)
            effects["target_reputation_change"] = -reputation_damage
            
        elif campaign.strategy == WarfareStrategy.PROPAGANDA:
            reputation_boost = effectiveness * 0.02
            orchestrating_faction.reputation = min(1.0, orchestrating_faction.reputation + reputation_boost)
            effects["own_reputation_change"] = reputation_boost
        
        return effects
    
    def _conclude_campaign(self, campaign: DisinformationCampaign) -> Dict[str, Any]:
        """Conclude a campaign and calculate final results"""
        
        campaign.status = CampaignStatus.COMPLETED
        
        # Calculate overall campaign success
        effectiveness_values = list(campaign.effectiveness_metrics.values())
        average_effectiveness = sum(effectiveness_values) / len(effectiveness_values) if effectiveness_values else 0
        
        # Determine success level
        if average_effectiveness > 0.7:
            success_level = "highly_successful"
        elif average_effectiveness > 0.5:
            success_level = "successful"
        elif average_effectiveness > 0.3:
            success_level = "partially_successful"
        else:
            success_level = "failed"
            campaign.status = CampaignStatus.FAILED
        
        # Final rewards/penalties
        orchestrating_faction = self.faction_profiles[campaign.orchestrating_faction]
        
        if success_level in ["successful", "highly_successful"]:
            # Experience and reputation gains
            capability_gain = 0.05 * average_effectiveness
            reputation_gain = 0.03 * average_effectiveness
            
            orchestrating_faction.information_warfare_capability = min(
                1.0, orchestrating_faction.information_warfare_capability + capability_gain
            )
            orchestrating_faction.reputation = min(
                1.0, orchestrating_faction.reputation + reputation_gain
            )
        
        logger.info(f"Campaign {campaign.campaign_id} concluded with {success_level} result")
        
        return {
            "campaign_id": campaign.campaign_id,
            "final_status": campaign.status.value,
            "success_level": success_level,
            "average_effectiveness": average_effectiveness,
            "total_rumors_generated": len(campaign.generated_rumors),
            "duration_actual": (datetime.now() - campaign.start_date).days if campaign.start_date else 0
        }
    
    def get_faction_warfare_status(self, faction_id: str) -> Optional[Dict[str, Any]]:
        """Get warfare status for a specific faction"""
        
        faction = self.faction_profiles.get(faction_id)
        if not faction:
            return None
        
        # Active campaigns involving this faction
        active_campaigns = []
        for campaign in self.active_campaigns.values():
            if campaign.orchestrating_faction == faction_id or campaign.target_faction == faction_id:
                active_campaigns.append({
                    "campaign_id": campaign.campaign_id,
                    "role": "orchestrator" if campaign.orchestrating_faction == faction_id else "target",
                    "strategy": campaign.strategy.value,
                    "status": campaign.status.value,
                    "opponent": campaign.target_faction if campaign.orchestrating_faction == faction_id else campaign.orchestrating_faction
                })
        
        # Recent warfare actions
        recent_actions = [
            action for action in self.warfare_history[-20:]  # Last 20 actions
            if action.faction_id == faction_id or action.target == faction_id
        ]
        
        return {
            "faction_id": faction_id,
            "faction_name": faction.name,
            "warfare_capabilities": {
                "information_warfare": faction.information_warfare_capability,
                "counter_intelligence": faction.counter_intelligence,
                "reputation": faction.reputation,
                "current_morale": faction.current_morale
            },
            "resources": faction.assets,
            "relationships": {
                "allies": faction.allegiances,
                "enemies": faction.enemies
            },
            "active_campaigns": active_campaigns,
            "recent_actions": len(recent_actions),
            "territory_controlled": len(faction.territory)
        }
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide warfare statistics"""
        
        total_factions = len(self.faction_profiles)
        active_campaigns = len([c for c in self.active_campaigns.values() if c.status == CampaignStatus.ACTIVE])
        total_actions = len(self.warfare_history)
        
        # Strategy distribution
        strategy_usage = {}
        for campaign in self.active_campaigns.values():
            strategy = campaign.strategy.value
            strategy_usage[strategy] = strategy_usage.get(strategy, 0) + 1
        
        # Success rates
        completed_campaigns = [c for c in self.active_campaigns.values() if c.status in [CampaignStatus.COMPLETED, CampaignStatus.FAILED]]
        successful_campaigns = len([c for c in completed_campaigns if c.status == CampaignStatus.COMPLETED])
        success_rate = (successful_campaigns / max(1, len(completed_campaigns))) * 100
        
        return {
            "system_overview": {
                "registered_factions": total_factions,
                "active_campaigns": active_campaigns,
                "total_warfare_actions": total_actions,
                "campaign_success_rate": round(success_rate, 2)
            },
            "strategy_distribution": strategy_usage,
            "faction_power_ranking": self._calculate_faction_rankings()
        }
    
    def _calculate_faction_rankings(self) -> List[Dict[str, Any]]:
        """Calculate power rankings for factions"""
        
        rankings = []
        
        for faction in self.faction_profiles.values():
            # Calculate overall power score
            power_score = (
                faction.information_warfare_capability * 0.3 +
                faction.reputation * 0.25 +
                faction.current_morale * 0.2 +
                min(1.0, faction.assets.get("resources", 0) / 1000) * 0.15 +
                len(faction.territory) * 0.1
            )
            
            rankings.append({
                "faction_id": faction.faction_id,
                "faction_name": faction.name,
                "power_score": round(power_score, 3),
                "active_campaigns": len([
                    c for c in self.active_campaigns.values() 
                    if c.orchestrating_faction == faction.faction_id and c.status == CampaignStatus.ACTIVE
                ])
            })
        
        # Sort by power score descending
        rankings.sort(key=lambda x: x["power_score"], reverse=True)
        
        return rankings


# Factory function
def create_faction_warfare_integrator() -> FactionWarfareIntegrator:
    """Create faction warfare integrator instance"""
    return FactionWarfareIntegrator() 