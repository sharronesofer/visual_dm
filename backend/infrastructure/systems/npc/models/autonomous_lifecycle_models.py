"""
Autonomous NPC Lifecycle Models

Database models for autonomous NPC lifecycle management including:
- Goals and objectives
- Social relationships
- Economic history
- Political opinions  
- Life events
- Cultural participation
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4
import enum

Base = declarative_base()


class GoalType(enum.Enum):
    """Types of goals NPCs can pursue"""
    CAREER = "career"
    RELATIONSHIP = "relationship"
    WEALTH = "wealth"
    POWER = "power"
    KNOWLEDGE = "knowledge"
    SURVIVAL = "survival"
    FAMILY = "family"
    REVENGE = "revenge"
    EXPLORATION = "exploration"
    ARTISTIC = "artistic"
    RELIGIOUS = "religious"
    SOCIAL = "social"


class GoalStatus(enum.Enum):
    """Status of NPC goals"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class RelationshipType(enum.Enum):
    """Types of relationships between NPCs"""
    FRIEND = "friend"
    ENEMY = "enemy"
    ROMANTIC = "romantic"
    SPOUSE = "spouse"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"
    COLLEAGUE = "colleague"
    RIVAL = "rival"
    MENTOR = "mentor"
    STUDENT = "student"
    ACQUAINTANCE = "acquaintance"


class LifeEventType(enum.Enum):
    """Types of life events"""
    BIRTH = "birth"
    DEATH = "death"
    MARRIAGE = "marriage"
    DIVORCE = "divorce"
    JOB_CHANGE = "job_change"
    PROMOTION = "promotion"
    RETIREMENT = "retirement"
    MOVE = "move"
    ILLNESS = "illness"
    INJURY = "injury"
    ACHIEVEMENT = "achievement"
    LOSS = "loss"
    DISCOVERY = "discovery"
    BETRAYAL = "betrayal"
    ALLIANCE = "alliance"


class PoliticalStance(enum.Enum):
    """Political stance options"""
    STRONGLY_SUPPORT = "strongly_support"
    SUPPORT = "support"
    NEUTRAL = "neutral"
    OPPOSE = "oppose"
    STRONGLY_OPPOSE = "strongly_oppose"


class EconomicTransactionType(enum.Enum):
    """Types of economic transactions"""
    PURCHASE = "purchase"
    SALE = "sale"
    EMPLOYMENT = "employment"
    INVESTMENT = "investment"
    LOAN = "loan"
    GIFT = "gift"
    THEFT = "theft"
    INHERITANCE = "inheritance"
    TAX = "tax"
    FINE = "fine"


class NpcGoal(Base):
    """NPC goals and objectives"""
    __tablename__ = 'npc_goals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    goal_id = Column(String(100), nullable=False)
    goal_type = Column(Enum(GoalType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_description = Column(Text)  # What they're trying to achieve
    motivation = Column(Text)  # Why they want this
    priority = Column(Float, default=5.0)  # 0-10 scale
    status = Column(Enum(GoalStatus), default=GoalStatus.ACTIVE)
    progress = Column(Float, default=0.0)  # 0-1 completion percentage
    deadline = Column(DateTime)  # Optional deadline
    estimated_difficulty = Column(Float, default=5.0)  # 0-10 scale
    required_resources = Column(JSON)  # Resources needed
    current_plan = Column(JSON)  # Current action plan steps
    obstacles = Column(JSON)  # Known obstacles and challenges
    dependencies = Column(JSON)  # Other goals this depends on
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    npc = relationship("NpcEntity", backref="goals")


class NpcRelationship(Base):
    """Social relationships between NPCs"""
    __tablename__ = 'npc_relationships'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    target_npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    relationship_type = Column(Enum(RelationshipType), nullable=False)
    strength = Column(Float, default=5.0)  # 0-10 scale of relationship strength
    trust_level = Column(Float, default=5.0)  # 0-10 scale of trust
    respect_level = Column(Float, default=5.0)  # 0-10 scale of respect
    romantic_attraction = Column(Float, default=0.0)  # 0-10 scale of attraction
    status = Column(String(50), default='active')  # active, inactive, complicated
    duration_months = Column(Integer, default=0)
    last_interaction = Column(DateTime)
    interaction_frequency = Column(Float, default=1.0)  # interactions per month
    relationship_history = Column(JSON)  # Key events in relationship
    shared_experiences = Column(JSON)  # Common experiences
    conflicts = Column(JSON)  # Past conflicts
    mutual_friends = Column(JSON)  # Shared social connections
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_npc = relationship("NpcEntity", foreign_keys=[source_npc_id], backref="relationships_out")
    target_npc = relationship("NpcEntity", foreign_keys=[target_npc_id], backref="relationships_in")


class NpcEconomicHistory(Base):
    """Economic transaction history for NPCs"""
    __tablename__ = 'npc_economic_history'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    transaction_id = Column(String(100), nullable=False)
    transaction_type = Column(Enum(EconomicTransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # Monetary value
    currency = Column(String(20), default='gold')
    description = Column(Text)
    other_party = Column(String(200))  # Who they transacted with
    other_party_npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'))
    items_involved = Column(JSON)  # Items bought/sold
    location = Column(String(200))
    region_id = Column(String(100))
    success = Column(Boolean, default=True)
    satisfaction = Column(Float, default=5.0)  # 0-10 how happy they were
    economic_impact = Column(Float)  # Impact on their wealth
    decision_reasoning = Column(Text)  # Why they made this transaction
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    npc = relationship("NpcEntity", foreign_keys=[npc_id], backref="economic_history")
    other_npc = relationship("NpcEntity", foreign_keys=[other_party_npc_id])


class NpcPoliticalOpinion(Base):
    """Political opinions and stances"""
    __tablename__ = 'npc_political_opinions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    topic = Column(String(200), nullable=False)  # What political issue
    stance = Column(Enum(PoliticalStance), nullable=False)
    strength = Column(Float, default=5.0)  # 0-10 how strongly they feel
    reasoning = Column(Text)  # Why they hold this opinion
    influenced_by = Column(JSON)  # People/events that shaped this view
    faction_alignment = Column(String(100))  # Which faction they support
    faction_id = Column(UUID(as_uuid=True), ForeignKey('faction_entities.id'))
    voting_behavior = Column(String(100))  # How they vote
    political_activity_level = Column(Float, default=1.0)  # 0-10 how active
    leadership_aspirations = Column(Boolean, default=False)
    corruption_tolerance = Column(Float, default=5.0)  # 0-10 tolerance for corruption
    change_resistance = Column(Float, default=5.0)  # 0-10 resistance to change
    formed_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    npc = relationship("NpcEntity", backref="political_opinions")


class NpcLifeEvent(Base):
    """Major life events for NPCs"""
    __tablename__ = 'npc_life_events'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    event_id = Column(String(100), nullable=False)
    event_type = Column(Enum(LifeEventType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    impact_level = Column(Float, default=5.0)  # 0-10 how significant
    emotional_impact = Column(Float, default=0.0)  # -10 to +10 emotional effect
    involved_npcs = Column(JSON)  # Other NPCs involved
    location = Column(String(200))
    region_id = Column(String(100))
    witnesses = Column(JSON)  # NPCs who witnessed the event
    consequences = Column(JSON)  # Results/changes from this event
    memories_created = Column(JSON)  # Memories formed from this event
    goals_affected = Column(JSON)  # Goals created/modified/completed
    relationships_affected = Column(JSON)  # Relationships changed
    public_knowledge = Column(Boolean, default=False)  # Is this publicly known
    reputation_change = Column(Float, default=0.0)  # Impact on reputation
    occurred_at = Column(DateTime, default=datetime.utcnow)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    npc = relationship("NpcEntity", backref="life_events")


class NpcCulturalParticipation(Base):
    """NPC participation in cultural practices"""
    __tablename__ = 'npc_cultural_participation'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    cultural_practice_id = Column(String(100), nullable=False)
    practice_name = Column(String(200), nullable=False)
    practice_type = Column(String(100))  # festival, ritual, tradition, etc.
    participation_level = Column(Float, default=5.0)  # 0-10 how actively they participate
    role = Column(String(100))  # participant, organizer, leader, observer
    frequency = Column(String(50))  # daily, weekly, monthly, yearly
    importance_to_npc = Column(Float, default=5.0)  # 0-10 how important to them
    influence_on_practice = Column(Float, default=0.0)  # 0-10 how much they influence it
    innovation_contribution = Column(JSON)  # How they've changed/improved it
    cultural_connections = Column(JSON)  # Other related practices
    transmission_to_others = Column(JSON)  # Who they've taught/influenced
    last_participation = Column(DateTime)
    participation_history = Column(JSON)  # Historical participation record
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    npc = relationship("NpcEntity", backref="cultural_participation")


class NpcCareerProgression(Base):
    """Career advancement and job history"""
    __tablename__ = 'npc_career_progression'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    job_id = Column(String(100), nullable=False)
    profession = Column(String(100), nullable=False)
    job_title = Column(String(200), nullable=False)
    employer = Column(String(200))
    employer_npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'))
    sector = Column(String(100))  # agriculture, craft, trade, military, etc.
    skill_level = Column(Float, default=1.0)  # 0-10 skill in this profession
    experience_years = Column(Float, default=0.0)
    income_level = Column(Float, default=1.0)  # 0-10 relative income
    job_satisfaction = Column(Float, default=5.0)  # 0-10 satisfaction
    advancement_potential = Column(Float, default=5.0)  # 0-10 potential for growth
    responsibilities = Column(JSON)  # List of job responsibilities
    achievements = Column(JSON)  # Notable achievements in this role
    training_received = Column(JSON)  # Training and education
    mentors = Column(JSON)  # People who taught them
    apprentices = Column(JSON)  # People they've trained
    reputation_in_field = Column(Float, default=5.0)  # 0-10 professional reputation
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    is_current = Column(Boolean, default=True)
    termination_reason = Column(String(200))  # Why they left/were fired
    
    # Relationships
    npc = relationship("NpcEntity", foreign_keys=[npc_id], backref="career_history")
    employer_npc = relationship("NpcEntity", foreign_keys=[employer_npc_id])


class NpcWealth(Base):
    """Current wealth and asset tracking"""
    __tablename__ = 'npc_wealth'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    liquid_wealth = Column(Float, default=0.0)  # Cash on hand
    total_assets = Column(Float, default=0.0)  # Total estimated worth
    property_value = Column(Float, default=0.0)  # Real estate value
    business_interests = Column(JSON)  # Business ownership
    investments = Column(JSON)  # Investment portfolio
    debts = Column(JSON)  # Outstanding debts
    monthly_income = Column(Float, default=0.0)  # Regular income
    monthly_expenses = Column(Float, default=0.0)  # Regular expenses
    economic_class = Column(String(50))  # poor, middle, wealthy, noble
    wealth_trend = Column(String(50))  # rising, stable, declining
    financial_goals = Column(JSON)  # Wealth-related goals
    risk_tolerance = Column(Float, default=5.0)  # 0-10 investment risk tolerance
    generosity_level = Column(Float, default=5.0)  # 0-10 willingness to spend on others
    last_calculated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    npc = relationship("NpcEntity", uselist=False, backref="wealth")


class NpcAutonomousDecision(Base):
    """Record of autonomous decisions made by NPCs"""
    __tablename__ = 'npc_autonomous_decisions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    decision_id = Column(String(100), nullable=False)
    decision_type = Column(String(100), nullable=False)  # career, relationship, goal, etc.
    decision_description = Column(Text, nullable=False)
    options_considered = Column(JSON)  # Options they considered
    chosen_option = Column(String(200), nullable=False)
    reasoning = Column(Text)  # Why they chose this option
    influences = Column(JSON)  # What/who influenced the decision
    confidence_level = Column(Float, default=5.0)  # 0-10 confidence in decision
    expected_outcomes = Column(JSON)  # What they expect to happen
    actual_outcomes = Column(JSON)  # What actually happened
    satisfaction_with_outcome = Column(Float)  # 0-10 satisfaction after
    decision_context = Column(JSON)  # Situational context
    personality_factors = Column(JSON)  # Personality traits that influenced decision
    goals_related = Column(JSON)  # Goals this decision relates to
    made_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)  # When they reconsidered the decision
    
    # Relationships
    npc = relationship("NpcEntity", backref="autonomous_decisions")


# Additional models for tier-based management

class NpcTierStatus(Base):
    """Track NPC tier status and transition history"""
    __tablename__ = 'npc_tier_status'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    npc_id = Column(UUID(as_uuid=True), ForeignKey('npc_entities.id'), nullable=False)
    current_tier = Column(Integer, nullable=False)  # 1-4 tier level
    previous_tier = Column(Integer)
    tier_change_reason = Column(String(200))  # Why tier changed
    promotion_criteria_met = Column(JSON)  # What criteria led to promotion
    simulation_detail_level = Column(String(50))  # full, partial, statistical
    visibility_level = Column(String(50))  # visible, background, statistical
    interaction_importance = Column(Float, default=1.0)  # 0-10 importance to players
    last_tier_review = Column(DateTime, default=datetime.utcnow)
    tier_change_history = Column(JSON)  # History of tier changes
    
    # Relationships
    npc = relationship("NpcEntity", uselist=False, backref="tier_status") 