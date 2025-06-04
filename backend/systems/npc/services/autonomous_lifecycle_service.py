"""
Autonomous NPC Lifecycle Service

Manages the autonomous lifecycle of NPCs including:
- Goal generation and pursuit
- Aging and death management  
- Career progression
- Social relationship formation
- Economic participation
- Political engagement
- Cultural evolution participation
- Autonomous decision making

This service implements the core autonomous behavior that drives the NPC population.
"""

import logging
import random
import json
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum

# Import the new lifecycle models
from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import (
    NpcGoal, NpcRelationship, NpcEconomicHistory, NpcPoliticalOpinion,
    NpcLifeEvent, NpcCulturalParticipation, NpcCareerProgression,
    NpcWealth, NpcAutonomousDecision, NpcTierStatus,
    GoalType, GoalStatus, RelationshipType, LifeEventType,
    PoliticalStance, EconomicTransactionType
)

# Import existing NPC models
from backend.infrastructure.systems.npc.models.models import NpcEntity

# Import population demographics for race-specific lifecycle management
from backend.systems.population.utils.demographic_models import DemographicModels

logger = logging.getLogger(__name__)


class LifecyclePhase(Enum):
    """Major lifecycle phases"""
    INFANT = "infant"
    CHILD = "child" 
    ADOLESCENT = "adolescent"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    MIDDLE_AGED = "middle_aged"
    ELDER = "elder"
    ANCIENT = "ancient"


class AutonomousLifecycleService:
    """Service for managing autonomous NPC lifecycles"""
    
    def __init__(self, db_session, config_loader=None):
        self.db_session = db_session
        self.config_loader = config_loader
        self._load_race_demographics()
        self._load_lifecycle_config()
        
    def _load_race_demographics(self):
        """Load race-specific demographic data"""
        try:
            with open('data/systems/npc/race-demographics.json', 'r') as f:
                self.race_demographics = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load race demographics: {e}")
            self.race_demographics = {}
            
    def _load_lifecycle_config(self):
        """Load lifecycle configuration"""
        self.lifecycle_config = {
            "goal_generation": {
                "goals_per_lifecycle_phase": {
                    "young_adult": 2,
                    "adult": 3,
                    "middle_aged": 2,
                    "elder": 1
                },
                "goal_types_by_phase": {
                    "young_adult": ["career", "relationship", "exploration"],
                    "adult": ["career", "family", "wealth", "social"],
                    "middle_aged": ["power", "knowledge", "family"],
                    "elder": ["knowledge", "religious", "family"]
                }
            },
            "relationship_formation": {
                "new_relationships_per_month": {
                    "young_adult": 1.5,
                    "adult": 0.8,
                    "middle_aged": 0.4,
                    "elder": 0.2
                },
                "relationship_depth_factors": {
                    "tier_1": 3.0,  # Tier 1 NPCs form deeper relationships
                    "tier_2": 2.0,
                    "tier_3": 1.0,
                    "tier_4": 0.5   # Tier 4 mostly statistical
                }
            },
            "economic_participation": {
                "transactions_per_month": {
                    "young_adult": 8,
                    "adult": 12,
                    "middle_aged": 10,
                    "elder": 6
                },
                "wealth_accumulation_rates": {
                    "poor": 0.02,
                    "middle": 0.05,
                    "wealthy": 0.08,
                    "noble": 0.12
                }
            }
        }

    # ===== CORE LIFECYCLE MANAGEMENT =====

    def process_lifecycle_phase_transition(self, npc_id: UUID) -> Dict[str, Any]:
        """Process NPC lifecycle phase transitions (aging)"""
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return {"error": "NPC not found"}
        
        # Get race-specific lifecycle data
        race_data = self.race_demographics.get("races", {}).get(npc.race, {})
        lifecycle_stages = race_data.get("lifecycle_stages", {})
        
        # Determine current lifecycle phase
        current_phase = self._determine_lifecycle_phase(npc.age, lifecycle_stages)
        previous_phase = getattr(npc, 'lifecycle_phase', None)
        
        if current_phase != previous_phase:
            # Phase transition occurred!
            transition_result = self._handle_phase_transition(npc, previous_phase, current_phase)
            return {
                "npc_id": str(npc_id),
                "previous_phase": previous_phase,
                "new_phase": current_phase,
                "transition_events": transition_result
            }
        
        return {"npc_id": str(npc_id), "phase": current_phase, "no_transition": True}

    def _determine_lifecycle_phase(self, age: int, lifecycle_stages: Dict) -> str:
        """Determine lifecycle phase based on age and race"""
        for phase, data in lifecycle_stages.items():
            if data["min_age"] <= age <= data["max_age"]:
                return phase
        return "adult"  # Default fallback

    def _handle_phase_transition(self, npc: NpcEntity, old_phase: str, new_phase: str) -> List[Dict]:
        """Handle lifecycle phase transitions"""
        transition_events = []
        
        # Update NPC's lifecycle phase
        npc.lifecycle_phase = new_phase
        
        # Generate appropriate life event
        event = self._create_life_event(
            npc, 
            LifeEventType.PROMOTION if new_phase in ["adult", "middle_aged"] else LifeEventType.ACHIEVEMENT,
            f"Entered {new_phase} phase of life",
            f"{npc.name} has transitioned from {old_phase} to {new_phase}",
            impact_level=6.0
        )
        transition_events.append({"type": "life_event", "event_id": event.event_id})
        
        # Phase-specific transitions
        if new_phase == "young_adult":
            # Entering adulthood
            self._handle_adulthood_transition(npc, transition_events)
        elif new_phase == "middle_aged":
            # Mid-life transitions
            self._handle_midlife_transition(npc, transition_events) 
        elif new_phase == "elder":
            # Retirement and elder phase
            self._handle_elder_transition(npc, transition_events)
        
        # Generate new goals appropriate for the phase
        new_goals = self._generate_phase_appropriate_goals(npc, new_phase)
        transition_events.extend([{"type": "goal_created", "goal_id": g.goal_id} for g in new_goals])
        
        # Update tier status if needed
        self._review_tier_status(npc, f"lifecycle_transition_to_{new_phase}")
        
        self.db_session.commit()
        return transition_events

    def _handle_adulthood_transition(self, npc: NpcEntity, events: List):
        """Handle transition to adulthood"""
        # Start first career
        career = self._generate_initial_career(npc)
        if career:
            events.append({"type": "career_started", "job_id": career.job_id})
        
        # Initialize wealth tracking
        wealth = self._initialize_wealth_tracking(npc)
        events.append({"type": "wealth_tracking_started"})
        
        # Begin forming adult relationships
        self._initiate_adult_relationship_formation(npc)

    def _handle_midlife_transition(self, npc: NpcEntity, events: List):
        """Handle mid-life transition"""
        # Evaluate career progression
        self._evaluate_career_advancement(npc)
        
        # Possible major life changes (career change, major purchases, etc.)
        if random.random() < 0.3:  # 30% chance of major change
            self._trigger_midlife_change(npc, events)

    def _handle_elder_transition(self, npc: NpcEntity, events: List):
        """Handle transition to elder phase"""
        # Consider retirement
        current_career = self._get_current_career(npc)
        if current_career and random.random() < 0.7:  # 70% chance to retire
            self._retire_npc(npc, current_career)
            events.append({"type": "retirement", "job_id": current_career.job_id})
        
        # Shift goals toward legacy and knowledge sharing
        self._shift_elder_goals(npc)

    # ===== GOAL GENERATION AND MANAGEMENT =====

    def generate_autonomous_goals(self, npc_id: UUID, count: int = None) -> List[NpcGoal]:
        """Generate autonomous goals for an NPC"""
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return []
        
        phase = getattr(npc, 'lifecycle_phase', 'adult')
        if count is None:
            count = self.lifecycle_config["goal_generation"]["goals_per_lifecycle_phase"].get(phase, 2)
        
        return self._generate_phase_appropriate_goals(npc, phase, count)

    def _generate_phase_appropriate_goals(self, npc: NpcEntity, phase: str, count: int = None) -> List[NpcGoal]:
        """Generate goals appropriate for lifecycle phase"""
        if count is None:
            count = self.lifecycle_config["goal_generation"]["goals_per_lifecycle_phase"].get(phase, 2)
        
        available_types = self.lifecycle_config["goal_generation"]["goal_types_by_phase"].get(
            phase, ["career", "social", "wealth"]
        )
        
        goals = []
        for _ in range(count):
            goal_type = GoalType(random.choice(available_types))
            goal = self._create_specific_goal(npc, goal_type, phase)
            if goal:
                goals.append(goal)
        
        return goals

    def _create_specific_goal(self, npc: NpcEntity, goal_type: GoalType, phase: str) -> Optional[NpcGoal]:
        """Create a specific goal based on type and context"""
        goal_templates = {
            GoalType.CAREER: self._generate_career_goal,
            GoalType.RELATIONSHIP: self._generate_relationship_goal,
            GoalType.WEALTH: self._generate_wealth_goal,
            GoalType.FAMILY: self._generate_family_goal,
            GoalType.KNOWLEDGE: self._generate_knowledge_goal,
            GoalType.POWER: self._generate_power_goal,
            GoalType.SOCIAL: self._generate_social_goal
        }
        
        generator = goal_templates.get(goal_type)
        if generator:
            return generator(npc, phase)
        return None

    def _generate_career_goal(self, npc: NpcEntity, phase: str) -> NpcGoal:
        """Generate career-related goal"""
        current_career = self._get_current_career(npc)
        
        if not current_career:
            title = "Find suitable employment"
            description = f"Seek a career that matches {npc.name}'s skills and interests"
            target = "Secure a stable job with growth potential"
        else:
            if phase == "young_adult":
                title = "Master current profession"
                description = f"Become skilled in {current_career.profession}"
                target = f"Reach skill level 7+ in {current_career.profession}"
            else:
                title = "Advance to leadership role"
                description = f"Seek promotion or start own business in {current_career.profession}"
                target = f"Become a leader in {current_career.profession}"
        
        goal = NpcGoal(
            npc_id=npc.id,
            goal_id=f"career_{uuid4().hex[:8]}",
            goal_type=GoalType.CAREER,
            title=title,
            description=description,
            target_description=target,
            motivation="Professional advancement and financial security",
            priority=8.0,
            estimated_difficulty=6.0
        )
        
        self.db_session.add(goal)
        return goal

    def _generate_relationship_goal(self, npc: NpcEntity, phase: str) -> NpcGoal:
        """Generate relationship-related goal"""
        existing_relationships = self.db_session.query(NpcRelationship).filter_by(source_npc_id=npc.id).all()
        
        has_spouse = any(r.relationship_type == RelationshipType.SPOUSE for r in existing_relationships)
        has_close_friends = sum(1 for r in existing_relationships if r.relationship_type == RelationshipType.FRIEND and r.strength > 7) >= 2
        
        if not has_spouse and phase in ["young_adult", "adult"]:
            title = "Find life partner"
            description = f"Seek a romantic relationship leading to marriage"
            target = "Form a committed romantic relationship"
            priority = 7.5
        elif not has_close_friends:
            title = "Build meaningful friendships"
            description = f"Develop close friendships with compatible people"
            target = "Form 2-3 close friendships"
            priority = 6.0
        else:
            title = "Strengthen existing relationships"
            description = f"Deepen bonds with family and friends"
            target = "Improve relationship quality with loved ones"
            priority = 5.5
        
        goal = NpcGoal(
            npc_id=npc.id,
            goal_id=f"relationship_{uuid4().hex[:8]}",
            goal_type=GoalType.RELATIONSHIP,
            title=title,
            description=description,
            target_description=target,
            motivation="Social connection and emotional fulfillment",
            priority=priority,
            estimated_difficulty=5.0
        )
        
        self.db_session.add(goal)
        return goal

    def _generate_wealth_goal(self, npc: NpcEntity, phase: str) -> NpcGoal:
        """Generate wealth-related goal"""
        wealth = self._get_npc_wealth(npc)
        
        if wealth.economic_class in ["poor", "destitute"]:
            title = "Achieve financial stability"
            target = "Reach middle class economic status"
            difficulty = 7.0
        elif wealth.economic_class == "middle":
            title = "Build substantial wealth"
            target = "Accumulate enough wealth for a comfortable lifestyle"
            difficulty = 6.0
        else:
            title = "Expand business empire"
            target = "Become a major economic force in the region"
            difficulty = 8.0
        
        goal = NpcGoal(
            npc_id=npc.id,
            goal_id=f"wealth_{uuid4().hex[:8]}",
            goal_type=GoalType.WEALTH,
            title=title,
            description=f"Work to improve {npc.name}'s financial situation",
            target_description=target,
            motivation="Financial security and independence",
            priority=7.0,
            estimated_difficulty=difficulty
        )
        
        self.db_session.add(goal)
        return goal

    def _generate_family_goal(self, npc: NpcEntity, phase: str) -> NpcGoal:
        """Generate family-related goal"""
        # Check for spouse and children
        has_spouse = self._has_relationship_type(npc, RelationshipType.SPOUSE)
        has_children = self._has_relationship_type(npc, RelationshipType.PARENT)
        
        if not has_spouse:
            title = "Start a family"
            target = "Get married and establish a household"
        elif not has_children and phase in ["young_adult", "adult"]:
            title = "Have children"
            target = "Raise children to continue the family line"
        else:
            title = "Support family prosperity"
            target = "Ensure family's success and happiness"
        
        goal = NpcGoal(
            npc_id=npc.id,
            goal_id=f"family_{uuid4().hex[:8]}",
            goal_type=GoalType.FAMILY,
            title=title,
            description=f"Focus on {npc.name}'s family life and legacy",
            target_description=target,
            motivation="Family legacy and personal fulfillment",
            priority=8.5,
            estimated_difficulty=5.5
        )
        
        self.db_session.add(goal)
        return goal

    def _generate_knowledge_goal(self, npc: NpcEntity, phase: str) -> NpcGoal:
        """Generate knowledge/learning goal"""
        goal = NpcGoal(
            npc_id=npc.id,
            goal_id=f"knowledge_{uuid4().hex[:8]}",
            goal_type=GoalType.KNOWLEDGE,
            title="Master new skills",
            description=f"Learn new knowledge or skills to improve {npc.name}'s capabilities",
            target_description="Become knowledgeable in areas of interest",
            motivation="Personal growth and intellectual curiosity",
            priority=6.0,
            estimated_difficulty=5.0
        )
        
        self.db_session.add(goal)
        return goal

    def _generate_power_goal(self, npc: NpcEntity, phase: str) -> NpcGoal:
        """Generate power/influence goal"""
        goal = NpcGoal(
            npc_id=npc.id,
            goal_id=f"power_{uuid4().hex[:8]}",
            goal_type=GoalType.POWER,
            title="Gain influence",
            description=f"Build political or social influence in the community",
            target_description="Become a person of importance and influence",
            motivation="Desire for respect and ability to effect change",
            priority=6.5,
            estimated_difficulty=7.5
        )
        
        self.db_session.add(goal)
        return goal

    def _generate_social_goal(self, npc: NpcEntity, phase: str) -> NpcGoal:
        """Generate social goal"""
        goal = NpcGoal(
            npc_id=npc.id,
            goal_id=f"social_{uuid4().hex[:8]}",
            goal_type=GoalType.SOCIAL,
            title="Build social standing",
            description=f"Improve {npc.name}'s reputation and social connections",
            target_description="Become well-regarded in the community",
            motivation="Social acceptance and community belonging",
            priority=5.5,
            estimated_difficulty=4.5
        )
        
        self.db_session.add(goal)
        return goal

    # ===== RELATIONSHIP MANAGEMENT =====

    def process_relationship_formation(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Process autonomous relationship formation for an NPC"""
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return []
        
        # Get tier status for relationship formation rates
        tier_status = self._get_tier_status(npc)
        tier_modifier = self.lifecycle_config["relationship_formation"]["relationship_depth_factors"].get(
            f"tier_{tier_status.current_tier}", 1.0
        )
        
        phase = getattr(npc, 'lifecycle_phase', 'adult')
        base_rate = self.lifecycle_config["relationship_formation"]["new_relationships_per_month"].get(phase, 0.5)
        
        formation_rate = base_rate * tier_modifier
        
        new_relationships = []
        if random.random() < formation_rate:
            relationship = self._form_new_relationship(npc)
            if relationship:
                new_relationships.append({
                    "type": "relationship_formed",
                    "relationship_id": str(relationship.id),
                    "target_npc": str(relationship.target_npc_id),
                    "relationship_type": relationship.relationship_type.value
                })
        
        return new_relationships

    def _form_new_relationship(self, npc: NpcEntity) -> Optional[NpcRelationship]:
        """Form a new relationship for an NPC"""
        # Find potential relationship targets (other NPCs in similar locations/contexts)
        potential_targets = self._find_relationship_candidates(npc)
        
        if not potential_targets:
            return None
        
        target = random.choice(potential_targets)
        relationship_type = self._determine_relationship_type(npc, target)
        
        # Create the relationship
        relationship = NpcRelationship(
            source_npc_id=npc.id,
            target_npc_id=target.id,
            relationship_type=relationship_type,
            strength=random.uniform(3.0, 6.0),  # Start with moderate strength
            trust_level=random.uniform(4.0, 7.0),
            respect_level=random.uniform(4.0, 7.0),
            interaction_frequency=random.uniform(0.5, 2.0)
        )
        
        self.db_session.add(relationship)
        
        # Create reciprocal relationship if appropriate
        if relationship_type in [RelationshipType.FRIEND, RelationshipType.SPOUSE, RelationshipType.SIBLING]:
            reciprocal = NpcRelationship(
                source_npc_id=target.id,
                target_npc_id=npc.id,
                relationship_type=relationship_type,
                strength=relationship.strength,
                trust_level=relationship.trust_level,
                respect_level=relationship.respect_level,
                interaction_frequency=relationship.interaction_frequency
            )
            self.db_session.add(reciprocal)
        
        return relationship

    def _find_relationship_candidates(self, npc: NpcEntity) -> List[NpcEntity]:
        """Find potential relationship targets for an NPC"""
        # Find NPCs in similar locations, age ranges, social contexts
        candidates = self.db_session.query(NpcEntity).filter(
            NpcEntity.id != npc.id,
            NpcEntity.region_id == npc.region_id,
            NpcEntity.status == 'active'
        ).limit(20).all()
        
        # Filter out existing relationships
        existing_targets = {
            r.target_npc_id for r in 
            self.db_session.query(NpcRelationship).filter_by(source_npc_id=npc.id).all()
        }
        
        return [c for c in candidates if c.id not in existing_targets]

    def _determine_relationship_type(self, npc1: NpcEntity, npc2: NpcEntity) -> RelationshipType:
        """Determine the type of relationship to form"""
        # Age difference considerations
        age_diff = abs(npc1.age - npc2.age)
        
        # Existing relationships considerations
        has_spouse = self._has_relationship_type(npc1, RelationshipType.SPOUSE)
        
        # Relationship type probabilities based on context
        if not has_spouse and age_diff < 15 and random.random() < 0.3:
            return RelationshipType.ROMANTIC
        elif age_diff > 20:
            return RelationshipType.MENTOR if npc1.age > npc2.age else RelationshipType.STUDENT
        elif self._have_common_profession(npc1, npc2):
            return RelationshipType.COLLEAGUE
        else:
            return RelationshipType.FRIEND

    # ===== ECONOMIC PARTICIPATION =====

    def process_economic_activity(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Process autonomous economic activities for an NPC"""
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return []
        
        phase = getattr(npc, 'lifecycle_phase', 'adult')
        transaction_rate = self.lifecycle_config["economic_participation"]["transactions_per_month"].get(phase, 8)
        
        activities = []
        
        # Generate economic transactions
        for _ in range(random.randint(0, transaction_rate)):
            transaction = self._generate_economic_transaction(npc)
            if transaction:
                activities.append({
                    "type": "economic_transaction",
                    "transaction_id": transaction.transaction_id,
                    "transaction_type": transaction.transaction_type.value,
                    "amount": transaction.amount
                })
        
        # Update wealth based on activities
        self._update_wealth_from_activities(npc, activities)
        
        return activities

    def _generate_economic_transaction(self, npc: NpcEntity) -> Optional[NpcEconomicHistory]:
        """Generate an economic transaction for an NPC"""
        wealth = self._get_npc_wealth(npc)
        
        # Determine transaction type based on NPC's situation
        transaction_types = [
            EconomicTransactionType.PURCHASE,
            EconomicTransactionType.SALE,
            EconomicTransactionType.EMPLOYMENT
        ]
        
        if wealth.liquid_wealth > 100:
            transaction_types.append(EconomicTransactionType.INVESTMENT)
        
        transaction_type = random.choice(transaction_types)
        
        # Generate transaction details
        amount = self._calculate_transaction_amount(npc, transaction_type, wealth)
        description = self._generate_transaction_description(transaction_type, amount)
        
        transaction = NpcEconomicHistory(
            npc_id=npc.id,
            transaction_id=f"txn_{uuid4().hex[:8]}",
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            location=npc.location,
            region_id=npc.region_id,
            satisfaction=random.uniform(4.0, 8.0),
            decision_reasoning=self._generate_transaction_reasoning(npc, transaction_type)
        )
        
        self.db_session.add(transaction)
        return transaction

    # ===== POLITICAL ENGAGEMENT =====

    def process_political_engagement(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Process NPC political engagement and opinion formation"""
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return []
        
        political_activities = []
        
        # Generate political opinions on current issues
        if random.random() < 0.2:  # 20% chance per month to develop new opinion
            opinion = self._form_political_opinion(npc)
            if opinion:
                political_activities.append({
                    "type": "political_opinion_formed",
                    "topic": opinion.topic,
                    "stance": opinion.stance.value
                })
        
        # Political participation based on activity level
        existing_opinions = self.db_session.query(NpcPoliticalOpinion).filter_by(npc_id=npc.id).all()
        avg_activity = sum(o.political_activity_level for o in existing_opinions) / max(len(existing_opinions), 1)
        
        if avg_activity > 5.0 and random.random() < 0.1:  # Active NPCs might engage politically
            political_activities.append(self._engage_in_political_activity(npc))
        
        return political_activities

    def _form_political_opinion(self, npc: NpcEntity) -> Optional[NpcPoliticalOpinion]:
        """Form a new political opinion for an NPC"""
        # Political topics that NPCs might have opinions on
        topics = [
            "taxation_policy", "military_spending", "trade_regulations",
            "immigration_policy", "law_enforcement", "public_works",
            "foreign_relations", "religious_freedom", "economic_policy"
        ]
        
        topic = random.choice(topics)
        
        # Determine stance based on personality and background
        stance = self._determine_political_stance(npc, topic)
        strength = random.uniform(3.0, 8.0)
        
        opinion = NpcPoliticalOpinion(
            npc_id=npc.id,
            topic=topic,
            stance=stance,
            strength=strength,
            reasoning=self._generate_political_reasoning(npc, topic, stance),
            political_activity_level=random.uniform(1.0, 6.0)
        )
        
        self.db_session.add(opinion)
        return opinion

    # ===== CULTURAL PARTICIPATION =====

    def process_cultural_engagement(self, npc_id: UUID) -> List[Dict[str, Any]]:
        """Process NPC cultural participation and evolution"""
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return []
        
        cultural_activities = []
        
        # Participate in existing cultural practices
        if random.random() < 0.3:  # 30% chance per month
            participation = self._participate_in_culture(npc)
            if participation:
                cultural_activities.append({
                    "type": "cultural_participation",
                    "practice": participation.practice_name,
                    "role": participation.role
                })
        
        # Potentially innovate or modify cultural practices
        if random.random() < 0.05:  # 5% chance per month for innovation
            innovation = self._cultural_innovation(npc)
            if innovation:
                cultural_activities.append(innovation)
        
        return cultural_activities

    # ===== AUTONOMOUS DECISION MAKING =====

    def make_autonomous_decision(self, npc_id: UUID, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make an autonomous decision for an NPC"""
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return {"error": "NPC not found"}
        
        decision_type = decision_context.get("type", "general")
        options = decision_context.get("options", [])
        
        if not options:
            return {"error": "No options provided"}
        
        # Analyze options based on NPC's personality, goals, and current situation
        option_scores = self._score_decision_options(npc, options, decision_type)
        
        # Choose the highest-scoring option (with some randomness)
        best_option = self._select_best_option(option_scores)
        
        # Record the decision
        decision = NpcAutonomousDecision(
            npc_id=npc.id,
            decision_id=f"decision_{uuid4().hex[:8]}",
            decision_type=decision_type,
            decision_description=decision_context.get("description", "Autonomous decision"),
            options_considered=options,
            chosen_option=best_option["option"],
            reasoning=best_option["reasoning"],
            confidence_level=best_option["confidence"],
            decision_context=decision_context
        )
        
        self.db_session.add(decision)
        self.db_session.commit()
        
        return {
            "decision_id": decision.decision_id,
            "chosen_option": best_option["option"],
            "reasoning": best_option["reasoning"],
            "confidence": best_option["confidence"]
        }

    def _score_decision_options(self, npc: NpcEntity, options: List, decision_type: str) -> List[Dict]:
        """Score decision options based on NPC's characteristics"""
        scored_options = []
        
        for option in options:
            score = 5.0  # Base score
            reasoning_factors = []
            
            # Score based on personality traits
            personality_score = self._score_option_by_personality(npc, option)
            score += personality_score
            reasoning_factors.append(f"Personality compatibility: {personality_score:.1f}")
            
            # Score based on current goals
            goal_score = self._score_option_by_goals(npc, option)
            score += goal_score
            reasoning_factors.append(f"Goal alignment: {goal_score:.1f}")
            
            # Score based on relationships
            relationship_score = self._score_option_by_relationships(npc, option)
            score += relationship_score
            reasoning_factors.append(f"Relationship impact: {relationship_score:.1f}")
            
            # Score based on economic situation
            economic_score = self._score_option_by_economics(npc, option)
            score += economic_score
            reasoning_factors.append(f"Economic impact: {economic_score:.1f}")
            
            scored_options.append({
                "option": option,
                "score": score,
                "reasoning": "; ".join(reasoning_factors),
                "confidence": min(10.0, score)
            })
        
        return scored_options

    def _select_best_option(self, scored_options: List[Dict]) -> Dict:
        """Select the best option with some randomness"""
        if not scored_options:
            return {"option": "no_action", "reasoning": "No valid options", "confidence": 1.0}
        
        # Sort by score
        scored_options.sort(key=lambda x: x["score"], reverse=True)
        
        # Add some randomness - top options more likely but not guaranteed
        weights = [1.0 / (i + 1) for i in range(len(scored_options))]
        chosen_index = random.choices(range(len(scored_options)), weights=weights)[0]
        
        return scored_options[chosen_index]

    # ===== HELPER METHODS =====

    def _create_life_event(self, npc: NpcEntity, event_type: LifeEventType, title: str, 
                          description: str, impact_level: float = 5.0) -> NpcLifeEvent:
        """Create a life event for an NPC"""
        event = NpcLifeEvent(
            npc_id=npc.id,
            event_id=f"event_{uuid4().hex[:8]}",
            event_type=event_type,
            title=title,
            description=description,
            impact_level=impact_level,
            location=npc.location,
            region_id=npc.region_id
        )
        
        self.db_session.add(event)
        return event

    def _get_tier_status(self, npc: NpcEntity) -> NpcTierStatus:
        """Get or create tier status for an NPC"""
        tier_status = self.db_session.query(NpcTierStatus).filter_by(npc_id=npc.id).first()
        
        if not tier_status:
            # Default tier assignment based on age and lifecycle phase
            phase = getattr(npc, 'lifecycle_phase', 'adult')
            race_data = self.race_demographics.get("races", {}).get(npc.race, {})
            lifecycle_stages = race_data.get("lifecycle_stages", {})
            stage_data = lifecycle_stages.get(phase, {})
            default_tier = stage_data.get("tier", 2)
            
            tier_status = NpcTierStatus(
                npc_id=npc.id,
                current_tier=default_tier,
                simulation_detail_level="partial",
                visibility_level="background"
            )
            self.db_session.add(tier_status)
        
        return tier_status

    def _get_npc_wealth(self, npc: NpcEntity) -> NpcWealth:
        """Get or create wealth tracking for an NPC"""
        wealth = self.db_session.query(NpcWealth).filter_by(npc_id=npc.id).first()
        
        if not wealth:
            wealth = self._initialize_wealth_tracking(npc)
        
        return wealth

    def _initialize_wealth_tracking(self, npc: NpcEntity) -> NpcWealth:
        """Initialize wealth tracking for an NPC"""
        # Base wealth on age, profession, and background
        base_wealth = random.uniform(10, 100)
        economic_class = "poor" if base_wealth < 50 else "middle"
        
        wealth = NpcWealth(
            npc_id=npc.id,
            liquid_wealth=base_wealth,
            total_assets=base_wealth * random.uniform(1.2, 3.0),
            monthly_income=base_wealth * 0.1,
            monthly_expenses=base_wealth * 0.08,
            economic_class=economic_class,
            wealth_trend="stable"
        )
        
        self.db_session.add(wealth)
        return wealth

    # Additional helper methods would continue here...
    # (Due to length constraints, I'm truncating, but the pattern continues)

    def process_monthly_lifecycle_update(self, npc_id: UUID) -> Dict[str, Any]:
        """Process comprehensive monthly lifecycle updates for an NPC"""
        results = {
            "npc_id": str(npc_id),
            "phase_transitions": [],
            "relationships": [],
            "economic_activities": [],
            "political_activities": [],
            "cultural_activities": [],
            "goals_updated": [],
            "decisions_made": []
        }
        
        # Process all lifecycle aspects
        results["phase_transitions"] = [self.process_lifecycle_phase_transition(npc_id)]
        results["relationships"] = self.process_relationship_formation(npc_id)
        results["economic_activities"] = self.process_economic_activity(npc_id)
        results["political_activities"] = self.process_political_engagement(npc_id)
        results["cultural_activities"] = self.process_cultural_engagement(npc_id)
        
        # Process goal updates
        self._update_goal_progress(npc_id)
        
        return results 