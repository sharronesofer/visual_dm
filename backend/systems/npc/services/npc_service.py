"""
Enhanced NPC Service with Autonomous Lifecycle Integration

Integrates with:
- Autonomous Lifecycle Service for goal generation and lifecycle management
- JSON configuration files for sophisticated behavior patterns
- Type-based NPC generation and behavior
- Tier-based performance optimization
"""

import json
import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta

# Import autonomous lifecycle system
from .autonomous_lifecycle_service import AutonomousLifecycleService
from ..utils.type_generator import NpcTypeGenerator
from ..utils.loyalty_engine import LoyaltyEngine
from ..utils.travel_decision_engine import TravelDecisionEngine
from ..utils.economic_decision_engine import EconomicDecisionEngine

# Import existing infrastructure
from backend.infrastructure.systems.npc.repositories.npc_repository import NpcRepository
from backend.infrastructure.systems.npc.models.models import NpcEntity, CreateNpcRequest, UpdateNpcRequest
from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import (
    NpcGoal, NpcRelationship, NpcTierStatus, GoalType, RelationshipType
)

logger = logging.getLogger(__name__)


class EnhancedNpcService:
    """Enhanced NPC Service with autonomous lifecycle management"""
    
    def __init__(self, db_session, config_loader=None, event_publisher=None):
        self.db_session = db_session
        self.config_loader = config_loader
        self.event_publisher = event_publisher
        
        # Initialize core services
        self.npc_repository = NpcRepository(db_session)
        self.lifecycle_service = AutonomousLifecycleService(db_session, config_loader)
        
        # Initialize specialized engines
        self.type_generator = NpcTypeGenerator()
        self.loyalty_engine = LoyaltyEngine()
        self.travel_engine = TravelDecisionEngine()
        self.economic_engine = EconomicDecisionEngine()
        
        # Load configuration files
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all JSON configuration files"""
        try:
            # Load NPC types for sophisticated generation
            with open('data/systems/npc/npc-types.json', 'r') as f:
                self.npc_types_config = json.load(f)
            
            # Load loyalty rules for relationship management
            with open('data/systems/npc/loyalty-rules.json', 'r') as f:
                self.loyalty_config = json.load(f)
            
            # Load travel behaviors for movement decisions
            with open('data/systems/npc/travel-behaviors.json', 'r') as f:
                self.travel_config = json.load(f)
            
            # Load trading rules for economic decisions
            with open('data/systems/npc/item-trading-rules.json', 'r') as f:
                self.trading_config = json.load(f)
            
            # Load economic regions for regional behavior
            with open('data/systems/npc/economic-regions.json', 'r') as f:
                self.economic_regions_config = json.load(f)
            
            # Load autonomous behavior patterns
            with open('data/systems/npc/autonomous-behavior-config.json', 'r') as f:
                self.autonomous_config = json.load(f)
            
            # Load race demographics
            with open('data/systems/npc/race-demographics.json', 'r') as f:
                self.race_demographics = json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to load NPC configurations: {e}")
            # Initialize with empty configs as fallback
            self.npc_types_config = {}
            self.loyalty_config = {}
            self.travel_config = {}
            self.trading_config = {}
            self.economic_regions_config = {}
            self.autonomous_config = {}
            self.race_demographics = {}

    # ===== ENHANCED NPC CREATION =====

    async def create_npc_with_type(self, npc_type: str, region_id: str, **overrides) -> Dict[str, Any]:
        """Create NPC using sophisticated type-based generation"""
        try:
            # Get type configuration
            type_config = self.npc_types_config.get("npc_types", {}).get(npc_type)
            if not type_config:
                return {"error": f"Unknown NPC type: {npc_type}"}
            
            # Generate NPC using type generator
            npc_data = await self.type_generator.generate_npc_from_type(
                npc_type, type_config, region_id, **overrides
            )
            
            # Create the base NPC entity
            create_request = CreateNpcRequest(**npc_data)
            npc = await self.npc_repository.create_npc(create_request)
            
            if not npc:
                return {"error": "Failed to create NPC"}
            
            # Initialize autonomous lifecycle components
            await self._initialize_autonomous_components(npc, npc_type, type_config)
            
            # Set initial tier status
            await self._set_initial_tier_status(npc, npc_type)
            
            self.db_session.commit()
            
            return {
                "npc_id": str(npc.id),
                "name": npc.name,
                "npc_type": npc_type,
                "region_id": region_id,
                "tier": await self._get_npc_tier(npc.id),
                "autonomous_components_initialized": True
            }
            
        except Exception as e:
            logger.error(f"Error creating NPC with type {npc_type}: {e}")
            self.db_session.rollback()
            return {"error": str(e)}

    async def _initialize_autonomous_components(self, npc: NpcEntity, npc_type: str, type_config: Dict):
        """Initialize autonomous lifecycle components for new NPC"""
        
        # Generate initial goals based on type
        goals = await self._generate_type_based_goals(npc, npc_type, type_config)
        
        # Initialize wealth tracking
        wealth = self.lifecycle_service._initialize_wealth_tracking(npc)
        
        # Set up initial cultural participation
        if npc.age >= 18:  # Adults only
            await self._initialize_cultural_participation(npc, npc_type)
        
        # Initialize political opinions for adults
        if npc.age >= 18 and random.random() < 0.5:  # 50% chance
            await self._initialize_political_opinions(npc, npc_type)
        
        # Start career if adult
        if npc.age >= 18:
            career = await self._initialize_career(npc, npc_type, type_config)

    async def _generate_type_based_goals(self, npc: NpcEntity, npc_type: str, type_config: Dict) -> List[NpcGoal]:
        """Generate goals based on NPC type configuration"""
        behavior_config = self.autonomous_config.get("autonomous_behavior_patterns", {})
        goal_config = behavior_config.get("goal_generation_by_type", {}).get(npc_type, {})
        
        primary_goals = goal_config.get("primary_goals", ["career", "wealth"])
        secondary_goals = goal_config.get("secondary_goals", ["social", "family"])
        
        goals = []
        
        # Generate 1-2 primary goals
        for goal_type_str in random.sample(primary_goals, min(2, len(primary_goals))):
            goal_type = GoalType(goal_type_str)
            goal = self.lifecycle_service._create_specific_goal(npc, goal_type, "adult")
            if goal:
                goals.append(goal)
        
        # Generate 1 secondary goal
        if secondary_goals:
            goal_type_str = random.choice(secondary_goals)
            goal_type = GoalType(goal_type_str)
            goal = self.lifecycle_service._create_specific_goal(npc, goal_type, "adult")
            if goal:
                goals.append(goal)
        
        return goals

    # ===== LOYALTY SYSTEM INTEGRATION =====

    async def process_loyalty_changes(self, npc_id: UUID, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process loyalty changes based on sophisticated loyalty rules"""
        try:
            npc = await self.npc_repository.get_npc_by_id(npc_id)
            if not npc:
                return {"error": "NPC not found"}
            
            # Use loyalty engine to process changes
            loyalty_result = await self.loyalty_engine.process_interaction(
                npc, interaction_data, self.loyalty_config
            )
            
            # Update NPC loyalty score
            if "loyalty_change" in loyalty_result:
                new_loyalty = max(0, min(100, npc.loyalty_score + loyalty_result["loyalty_change"]))
                await self.npc_repository.update_npc_loyalty(npc_id, new_loyalty)
            
            # Create memory of the interaction
            if loyalty_result.get("create_memory"):
                memory_data = {
                    "memory_id": f"loyalty_{uuid4().hex[:8]}",
                    "content": loyalty_result["memory_content"],
                    "memory_type": "loyalty_interaction",
                    "importance": abs(loyalty_result["loyalty_change"]) / 10.0,
                    "emotion": loyalty_result.get("emotion", "neutral")
                }
                await self.add_memory_to_npc(npc_id, memory_data)
            
            return loyalty_result
            
        except Exception as e:
            logger.error(f"Error processing loyalty changes for NPC {npc_id}: {e}")
            return {"error": str(e)}

    # ===== TRAVEL DECISION INTEGRATION =====

    async def make_travel_decision(self, npc_id: UUID, available_destinations: List[str]) -> Dict[str, Any]:
        """Make sophisticated travel decisions based on goals and behavior patterns"""
        try:
            npc = await self.npc_repository.get_npc_by_id(npc_id)
            if not npc:
                return {"error": "NPC not found"}
            
            # Get NPC's current goals
            goals = self.db_session.query(NpcGoal).filter_by(
                npc_id=npc_id, status='active'
            ).all()
            
            # Use travel engine for decision making
            travel_decision = await self.travel_engine.make_travel_decision(
                npc, goals, available_destinations, self.travel_config, self.autonomous_config
            )
            
            # If decision is to travel, update location
            if travel_decision.get("decision") == "travel" and travel_decision.get("destination"):
                await self.update_npc_location(
                    npc_id, 
                    travel_decision["destination"],
                    travel_decision.get("reason", "autonomous_travel")
                )
            
            return travel_decision
            
        except Exception as e:
            logger.error(f"Error making travel decision for NPC {npc_id}: {e}")
            return {"error": str(e)}

    # ===== ECONOMIC DECISION INTEGRATION =====

    async def make_economic_decision(self, npc_id: UUID, economic_context: Dict[str, Any]) -> Dict[str, Any]:
        """Make sophisticated economic decisions using trading rules and regional data"""
        try:
            npc = await self.npc_repository.get_npc_by_id(npc_id)
            if not npc:
                return {"error": "NPC not found"}
            
            # Get NPC's wealth and goals
            wealth = self.lifecycle_service._get_npc_wealth(npc)
            goals = self.db_session.query(NpcGoal).filter_by(
                npc_id=npc_id, status='active'
            ).all()
            
            # Get regional economic data
            region_data = self.economic_regions_config.get("regions", {}).get(npc.region_id, {})
            
            # Use economic engine for decision making
            economic_decision = await self.economic_engine.make_economic_decision(
                npc, wealth, goals, economic_context, region_data, 
                self.trading_config, self.autonomous_config
            )
            
            # Record the economic transaction
            if economic_decision.get("action") != "no_action":
                transaction = self.lifecycle_service._generate_economic_transaction(npc)
                economic_decision["transaction_id"] = transaction.transaction_id if transaction else None
            
            return economic_decision
            
        except Exception as e:
            logger.error(f"Error making economic decision for NPC {npc_id}: {e}")
            return {"error": str(e)}

    # ===== AUTONOMOUS LIFECYCLE MANAGEMENT =====

    async def process_monthly_lifecycle_updates(self, npc_ids: List[UUID] = None) -> Dict[str, Any]:
        """Process comprehensive monthly lifecycle updates for NPCs"""
        try:
            if npc_ids is None:
                # Get all active NPCs, prioritized by tier
                npc_ids = await self._get_npcs_for_lifecycle_processing()
            
            results = {
                "processed_count": 0,
                "tier_1_updates": [],
                "tier_2_updates": [],
                "tier_3_updates": [],
                "tier_4_updates": [],
                "errors": []
            }
            
            for npc_id in npc_ids:
                try:
                    tier = await self._get_npc_tier(npc_id)
                    update_result = self.lifecycle_service.process_monthly_lifecycle_update(npc_id)
                    
                    results[f"tier_{tier}_updates"].append(update_result)
                    results["processed_count"] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing lifecycle for NPC {npc_id}: {e}")
                    results["errors"].append({"npc_id": str(npc_id), "error": str(e)})
            
            self.db_session.commit()
            return results
            
        except Exception as e:
            logger.error(f"Error in monthly lifecycle processing: {e}")
            self.db_session.rollback()
            return {"error": str(e)}

    async def _get_npcs_for_lifecycle_processing(self) -> List[UUID]:
        """Get NPCs prioritized for lifecycle processing based on tier"""
        # Get tier 1 and 2 NPCs first (full processing)
        high_priority = self.db_session.query(NpcEntity.id).join(NpcTierStatus).filter(
            NpcTierStatus.current_tier <= 2,
            NpcEntity.status == 'active'
        ).all()
        
        # Get sample of tier 3 NPCs (partial processing)
        medium_priority = self.db_session.query(NpcEntity.id).join(NpcTierStatus).filter(
            NpcTierStatus.current_tier == 3,
            NpcEntity.status == 'active'
        ).limit(100).all()  # Process only 100 tier 3 NPCs per cycle
        
        # Tier 4 NPCs are handled statistically, not individually
        
        return [npc.id for npc in high_priority + medium_priority]

    # ===== TIER MANAGEMENT =====

    async def _get_npc_tier(self, npc_id: UUID) -> int:
        """Get NPC's current tier"""
        tier_status = self.db_session.query(NpcTierStatus).filter_by(npc_id=npc_id).first()
        return tier_status.current_tier if tier_status else 3  # Default to tier 3

    async def _set_initial_tier_status(self, npc: NpcEntity, npc_type: str):
        """Set initial tier status for new NPC"""
        # Determine initial tier based on type and lifecycle phase
        phase = getattr(npc, 'lifecycle_phase', 'adult')
        race_data = self.race_demographics.get("races", {}).get(npc.race, {})
        lifecycle_stages = race_data.get("lifecycle_stages", {})
        stage_data = lifecycle_stages.get(phase, {})
        
        # Children are always tier 4
        if phase in ["infant", "child", "adolescent"]:
            tier = 4
        else:
            # Adults start at tier 2 or 3 based on type importance
            important_types = ["noble", "merchant", "scholar", "warrior"]
            tier = 2 if npc_type in important_types else 3
        
        tier_status = NpcTierStatus(
            npc_id=npc.id,
            current_tier=tier,
            simulation_detail_level="partial" if tier <= 2 else "statistical",
            visibility_level="background" if tier <= 3 else "statistical"
        )
        
        self.db_session.add(tier_status)

    async def review_and_update_npc_tiers(self) -> Dict[str, Any]:
        """Review and update NPC tiers based on criteria"""
        try:
            tier_criteria = self.autonomous_config.get("tier_management", {}).get("tier_transition_criteria", {})
            
            promotions = []
            demotions = []
            
            # Review tier 3 NPCs for promotion to tier 2
            tier_3_npcs = self.db_session.query(NpcEntity).join(NpcTierStatus).filter(
                NpcTierStatus.current_tier == 3
            ).all()
            
            for npc in tier_3_npcs:
                criteria_met = await self._evaluate_tier_promotion_criteria(npc, tier_criteria["promotion_to_tier_2"])
                if criteria_met:
                    await self._promote_npc_tier(npc.id, 2, "criteria_met")
                    promotions.append(str(npc.id))
            
            # Review tier 2 NPCs for promotion to tier 1
            tier_2_npcs = self.db_session.query(NpcEntity).join(NpcTierStatus).filter(
                NpcTierStatus.current_tier == 2
            ).all()
            
            for npc in tier_2_npcs:
                criteria_met = await self._evaluate_tier_promotion_criteria(npc, tier_criteria["promotion_to_tier_1"])
                if criteria_met:
                    await self._promote_npc_tier(npc.id, 1, "high_importance")
                    promotions.append(str(npc.id))
            
            # Review for demotions (inactive NPCs)
            # ... demotion logic here ...
            
            self.db_session.commit()
            
            return {
                "promotions": len(promotions),
                "demotions": len(demotions),
                "promoted_npcs": promotions,
                "demoted_npcs": demotions
            }
            
        except Exception as e:
            logger.error(f"Error reviewing NPC tiers: {e}")
            self.db_session.rollback()
            return {"error": str(e)}

    # ===== ENHANCED INTERACTION METHODS =====

    async def get_npc_with_autonomous_data(self, npc_id: UUID) -> Dict[str, Any]:
        """Get NPC with full autonomous lifecycle data"""
        try:
            npc = await self.npc_repository.get_npc_by_id(npc_id)
            if not npc:
                return {"error": "NPC not found"}
            
            # Get tier status
            tier_status = self.db_session.query(NpcTierStatus).filter_by(npc_id=npc_id).first()
            
            # Build response based on tier level
            response = {
                "npc": {
                    "id": str(npc.id),
                    "name": npc.name,
                    "race": npc.race,
                    "age": npc.age,
                    "location": npc.location,
                    "region_id": npc.region_id,
                    "loyalty_score": npc.loyalty_score,
                    "tier": tier_status.current_tier if tier_status else 3
                }
            }
            
            # Add detailed data for higher tier NPCs
            if tier_status and tier_status.current_tier <= 2:
                # Get goals
                goals = self.db_session.query(NpcGoal).filter_by(npc_id=npc_id).all()
                response["goals"] = [
                    {
                        "goal_id": g.goal_id,
                        "type": g.goal_type.value,
                        "title": g.title,
                        "status": g.status.value,
                        "priority": g.priority,
                        "progress": g.progress
                    }
                    for g in goals
                ]
                
                # Get relationships
                relationships = self.db_session.query(NpcRelationship).filter_by(source_npc_id=npc_id).all()
                response["relationships"] = [
                    {
                        "target_npc_id": str(r.target_npc_id),
                        "type": r.relationship_type.value,
                        "strength": r.strength,
                        "trust_level": r.trust_level
                    }
                    for r in relationships
                ]
                
                # Get wealth for tier 1 NPCs
                if tier_status.current_tier == 1:
                    wealth = self.lifecycle_service._get_npc_wealth(npc)
                    response["wealth"] = {
                        "liquid_wealth": wealth.liquid_wealth,
                        "total_assets": wealth.total_assets,
                        "economic_class": wealth.economic_class,
                        "monthly_income": wealth.monthly_income
                    }
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting NPC autonomous data for {npc_id}: {e}")
            return {"error": str(e)}

    # ===== LEGACY COMPATIBILITY METHODS =====
    
    # Keep existing methods for backwards compatibility, but enhance them
    async def create_npc(self, create_request: CreateNpcRequest) -> Dict[str, Any]:
        """Legacy create method - enhanced with autonomous components"""
        npc = await self.npc_repository.create_npc(create_request)
        if npc:
            # Initialize basic autonomous components
            await self._initialize_autonomous_components(npc, "general", {})
            await self._set_initial_tier_status(npc, "general")
            self.db_session.commit()
        return {"npc_id": str(npc.id)} if npc else {"error": "Failed to create NPC"}

    async def get_npc_by_id(self, npc_id: UUID) -> Optional[NpcEntity]:
        """Legacy get method"""
        return await self.npc_repository.get_npc_by_id(npc_id)

    async def update_npc(self, npc_id: UUID, update_request: UpdateNpcRequest) -> Dict[str, Any]:
        """Legacy update method"""
        success = await self.npc_repository.update_npc(npc_id, update_request)
        return {"success": success}

    async def delete_npc(self, npc_id: UUID) -> Dict[str, Any]:
        """Legacy delete method"""
        success = await self.npc_repository.delete_npc(npc_id)
        return {"success": success}

    # ... Additional existing methods enhanced with autonomous features ... 