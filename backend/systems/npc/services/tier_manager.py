"""
NPC Tier Management System

Revolutionary 4-tier NPC system optimized for MMO scale with dynamic tier transitions
based on player interaction and POI activity. Designed to support 100k+ visible NPCs
while maintaining computational efficiency.

Tier System:
- Tier 1: Active NPCs (1 hour after interaction) - Full AI, conversation, all systems
- Tier 2: Background NPCs (11 hours since interaction) - Reduced systems, visual presence
- Tier 3: Dormant NPCs (12+ hours since interaction) - Statistical only, visual presence  
- Tier 3.5: Long-dormant NPCs (1+ week since interaction) - Statistical only, compressed data
- Tier 4: Statistical NPCs (never interacted) - Pure statistics, no individual data
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import logging

from backend.infrastructure.shared.database.manager import DatabaseManager
from backend.systems.poi.models.models import PoiEntity
from backend.systems.npc.models.models import NPCEntity
from backend.infrastructure.events.dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


class NPCTier(Enum):
    """NPC computational tiers for efficient MMO scaling"""
    TIER_1_ACTIVE = "tier_1_active"              # Full AI - 1 hour after interaction
    TIER_2_BACKGROUND = "tier_2_background"      # Reduced systems - up to 11 hours
    TIER_3_DORMANT = "tier_3_dormant"            # Statistical only - 12+ hours
    TIER_3_5_COMPRESSED = "tier_3_5_compressed"  # Compressed stats - 1+ week
    TIER_4_STATISTICAL = "tier_4_statistical"    # Pure statistics - never interacted


@dataclass
class NPCTierMetrics:
    """Metrics for NPC tier system performance monitoring"""
    tier_1_count: int = 0
    tier_2_count: int = 0
    tier_3_count: int = 0
    tier_3_5_count: int = 0
    tier_4_count: int = 0
    
    # Computational load estimates
    tier_1_cpu_units: float = 0.0
    tier_2_cpu_units: float = 0.0
    tier_3_cpu_units: float = 0.0
    
    # Memory usage estimates (MB)
    tier_1_memory_mb: float = 0.0
    tier_2_memory_mb: float = 0.0
    tier_3_memory_mb: float = 0.0
    
    # Performance metrics
    promotion_events_per_hour: int = 0
    demotion_events_per_hour: int = 0
    total_npcs: int = 0
    
    @property
    def visible_npcs(self) -> int:
        """Total visible NPCs (Tiers 1-3)"""
        return self.tier_1_count + self.tier_2_count + self.tier_3_count + self.tier_3_5_count
    
    @property
    def computational_load(self) -> float:
        """Total computational load in CPU units"""
        return self.tier_1_cpu_units + self.tier_2_cpu_units + self.tier_3_cpu_units
    
    @property
    def memory_usage_mb(self) -> float:
        """Total memory usage in MB"""
        return self.tier_1_memory_mb + self.tier_2_memory_mb + self.tier_3_memory_mb


@dataclass
class NPCInstance:
    """Individual NPC instance with tier management"""
    npc_id: UUID
    poi_id: UUID
    current_tier: NPCTier
    last_interaction: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    player_interactions: Dict[UUID, datetime] = field(default_factory=dict)
    
    # Core data (always preserved)
    name: str = ""
    personality_hash: str = ""
    memory_summary: str = ""
    
    # Tier-specific data (compressed/expanded based on tier)
    full_memory: Optional[Dict[str, Any]] = None
    conversation_context: Optional[Dict[str, Any]] = None
    relationship_data: Optional[Dict[str, Any]] = None
    
    # System participation flags
    participates_in_economy: bool = True
    participates_in_diplomacy: bool = False
    participates_in_tension: bool = False
    participates_in_religion: bool = False
    participates_in_espionage: bool = False
    
    def time_since_last_interaction(self) -> Optional[timedelta]:
        """Calculate time since last player interaction"""
        if not self.last_interaction:
            return None
        return datetime.utcnow() - self.last_interaction
    
    def should_be_tier(self) -> NPCTier:
        """Calculate what tier this NPC should be in based on interaction time"""
        time_since = self.time_since_last_interaction()
        
        if time_since is None:
            return NPCTier.TIER_4_STATISTICAL
        
        if time_since <= timedelta(hours=1):
            return NPCTier.TIER_1_ACTIVE
        elif time_since <= timedelta(hours=11):
            return NPCTier.TIER_2_BACKGROUND
        elif time_since <= timedelta(weeks=1):
            return NPCTier.TIER_3_DORMANT
        else:
            return NPCTier.TIER_3_5_COMPRESSED


class NPCTierManager:
    """
    Revolutionary NPC tier management system for MMO-scale efficiency.
    
    Manages 100k+ visible NPCs across 4 computational tiers, with automatic
    promotion/demotion based on player interaction patterns.
    """
    
    def __init__(self, db_manager: DatabaseManager, event_dispatcher: EventDispatcher):
        self.db_manager = db_manager
        self.event_dispatcher = event_dispatcher
        
        # NPC storage by tier for efficient access
        self.tier_1_npcs: Dict[UUID, NPCInstance] = {}
        self.tier_2_npcs: Dict[UUID, NPCInstance] = {}
        self.tier_3_npcs: Dict[UUID, NPCInstance] = {}
        self.tier_3_5_npcs: Dict[UUID, NPCInstance] = {}
        
        # POI-based NPC lookup for efficient POI queries
        self.poi_npc_mapping: Dict[UUID, Set[UUID]] = {}
        
        # Player interaction tracking
        self.active_player_pois: Dict[UUID, Set[UUID]] = {}  # player_id -> poi_ids visited in last hour
        
        # Performance metrics
        self.metrics = NPCTierMetrics()
        
        # Configuration
        self.tier_transitions_per_cycle = 1000  # Max NPCs to process per cycle
        self.cycle_interval_seconds = 60  # How often to run tier management
        
        # Computational cost constants (CPU units per NPC per hour)
        self.tier_costs = {
            NPCTier.TIER_1_ACTIVE: 10.0,      # Full AI processing
            NPCTier.TIER_2_BACKGROUND: 2.0,   # Reduced processing
            NPCTier.TIER_3_DORMANT: 0.1,      # Minimal processing
            NPCTier.TIER_3_5_COMPRESSED: 0.02, # Near-zero processing
            NPCTier.TIER_4_STATISTICAL: 0.0   # No processing
        }
        
        # Memory cost constants (MB per NPC)
        self.memory_costs = {
            NPCTier.TIER_1_ACTIVE: 2.5,       # Full memory, context, relationships
            NPCTier.TIER_2_BACKGROUND: 1.0,   # Compressed memory
            NPCTier.TIER_3_DORMANT: 0.2,      # Core data only
            NPCTier.TIER_3_5_COMPRESSED: 0.05, # Highly compressed
            NPCTier.TIER_4_STATISTICAL: 0.0   # No individual storage
        }
        
        logger.info("NPCTierManager initialized for revolutionary MMO scaling")
    
    async def register_poi_npcs(self, poi_id: UUID, npc_count: int, poi_type: str = "settlement") -> List[UUID]:
        """
        Register NPCs for a POI, creating them at appropriate tiers.
        
        Args:
            poi_id: POI identifier
            npc_count: Number of NPCs to create
            poi_type: Type of POI (affects NPC tier distribution)
            
        Returns:
            List of created NPC IDs
        """
        created_npcs = []
        
        # All new NPCs start as Tier 4 (statistical) until interacted with
        for i in range(npc_count):
            npc_id = uuid4()
            
            # Create basic NPC instance
            npc = NPCInstance(
                npc_id=npc_id,
                poi_id=poi_id,
                current_tier=NPCTier.TIER_4_STATISTICAL,
                name=f"Citizen {i+1}",  # Generate proper names later
                personality_hash=f"personality_{npc_id.hex[:8]}",
                memory_summary="A typical resident of this settlement.",
            )
            
            # Configure system participation based on POI type
            if poi_type in ["city", "town"]:
                npc.participates_in_diplomacy = True
                npc.participates_in_tension = True
                npc.participates_in_religion = True
            elif poi_type in ["fortress", "military"]:
                npc.participates_in_tension = True
                npc.participates_in_espionage = True
            
            # Add to POI mapping
            if poi_id not in self.poi_npc_mapping:
                self.poi_npc_mapping[poi_id] = set()
            self.poi_npc_mapping[poi_id].add(npc_id)
            
            created_npcs.append(npc_id)
        
        # Update metrics
        self.metrics.tier_4_count += npc_count
        self.metrics.total_npcs += npc_count
        
        logger.info(f"Registered {npc_count} NPCs for POI {poi_id} as Tier 4 (statistical)")
        return created_npcs
    
    async def player_enters_poi(self, player_id: UUID, poi_id: UUID) -> List[UUID]:
        """
        Handle player entering a POI - promote NPCs to visible tiers.
        
        Returns list of NPC IDs that were promoted to Tier 2 (become visible).
        """
        # Track player's active POI
        if player_id not in self.active_player_pois:
            self.active_player_pois[player_id] = set()
        self.active_player_pois[player_id].add(poi_id)
        
        # Get all NPCs in this POI
        poi_npcs = self.poi_npc_mapping.get(poi_id, set())
        promoted_npcs = []
        
        for npc_id in poi_npcs:
            npc = await self._get_npc_instance(npc_id)
            if npc and npc.current_tier == NPCTier.TIER_4_STATISTICAL:
                # Promote Tier 4 -> Tier 2 (skip Tier 3, they become "visible")
                await self._promote_npc(npc, NPCTier.TIER_2_BACKGROUND)
                promoted_npcs.append(npc_id)
        
        # Dispatch event for frontend
        await self.event_dispatcher.publish({
            'type': 'npcs_promoted_to_visible',
            'poi_id': str(poi_id),
            'player_id': str(player_id),
            'promoted_npc_ids': [str(npc_id) for npc_id in promoted_npcs],
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return promoted_npcs
    
    async def player_interacts_with_npc(self, player_id: UUID, npc_id: UUID) -> bool:
        """
        Handle player interaction with NPC - promote to Tier 1.
        
        Returns True if NPC was promoted.
        """
        npc = await self._get_npc_instance(npc_id)
        if not npc:
            return False
        
        # Record interaction
        npc.last_interaction = datetime.utcnow()
        npc.player_interactions[player_id] = npc.last_interaction
        
        # Promote to Tier 1 if not already there
        if npc.current_tier != NPCTier.TIER_1_ACTIVE:
            await self._promote_npc(npc, NPCTier.TIER_1_ACTIVE)
            
            # Dispatch event
            await self.event_dispatcher.publish({
                'type': 'npc_promoted_to_active',
                'npc_id': str(npc_id),
                'player_id': str(player_id),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
        
        return False
    
    async def run_tier_management_cycle(self) -> Dict[str, int]:
        """
        Run a tier management cycle - promote/demote NPCs based on interaction times.
        
        Returns dict with promotion/demotion counts.
        """
        cycle_stats = {
            'promoted': 0,
            'demoted': 0,
            'tier_changes': {}
        }
        
        # Process Tier 1 NPCs for potential demotion
        npcs_to_process = list(self.tier_1_npcs.values())[:self.tier_transitions_per_cycle // 4]
        for npc in npcs_to_process:
            target_tier = npc.should_be_tier()
            if target_tier != npc.current_tier:
                await self._demote_npc(npc, target_tier)
                cycle_stats['demoted'] += 1
                cycle_stats['tier_changes'][f"{npc.current_tier.value}_to_{target_tier.value}"] = \
                    cycle_stats['tier_changes'].get(f"{npc.current_tier.value}_to_{target_tier.value}", 0) + 1
        
        # Process Tier 2 NPCs for potential demotion
        npcs_to_process = list(self.tier_2_npcs.values())[:self.tier_transitions_per_cycle // 4]
        for npc in npcs_to_process:
            target_tier = npc.should_be_tier()
            if target_tier != npc.current_tier:
                await self._demote_npc(npc, target_tier)
                cycle_stats['demoted'] += 1
                cycle_stats['tier_changes'][f"{npc.current_tier.value}_to_{target_tier.value}"] = \
                    cycle_stats['tier_changes'].get(f"{npc.current_tier.value}_to_{target_tier.value}", 0) + 1
        
        # Process Tier 3 NPCs for potential demotion to 3.5
        npcs_to_process = list(self.tier_3_npcs.values())[:self.tier_transitions_per_cycle // 4]
        for npc in npcs_to_process:
            target_tier = npc.should_be_tier()
            if target_tier != npc.current_tier:
                await self._demote_npc(npc, target_tier)
                cycle_stats['demoted'] += 1
                cycle_stats['tier_changes'][f"{npc.current_tier.value}_to_{target_tier.value}"] = \
                    cycle_stats['tier_changes'].get(f"{npc.current_tier.value}_to_{target_tier.value}", 0) + 1
        
        # Update metrics
        await self._update_metrics()
        
        logger.info(f"Tier management cycle complete: {cycle_stats}")
        return cycle_stats
    
    async def get_poi_npcs(self, poi_id: UUID, tier_filter: Optional[List[NPCTier]] = None) -> List[NPCInstance]:
        """
        Get all NPCs in a POI, optionally filtered by tier.
        """
        poi_npcs = self.poi_npc_mapping.get(poi_id, set())
        result = []
        
        for npc_id in poi_npcs:
            npc = await self._get_npc_instance(npc_id)
            if npc and (not tier_filter or npc.current_tier in tier_filter):
                result.append(npc)
        
        return result
    
    async def get_visible_npcs_in_poi(self, poi_id: UUID) -> List[NPCInstance]:
        """Get all visible NPCs (Tiers 1-3.5) in a POI for frontend rendering."""
        return await self.get_poi_npcs(poi_id, [
            NPCTier.TIER_1_ACTIVE,
            NPCTier.TIER_2_BACKGROUND,
            NPCTier.TIER_3_DORMANT,
            NPCTier.TIER_3_5_COMPRESSED
        ])
    
    async def get_system_participants(self, system_name: str, poi_ids: Optional[List[UUID]] = None) -> List[NPCInstance]:
        """
        Get NPCs that participate in a specific system (economy, diplomacy, etc.).
        
        Args:
            system_name: Name of the system ('economy', 'diplomacy', 'tension', etc.)
            poi_ids: Optional list of POI IDs to filter by
            
        Returns:
            List of NPCs that participate in the system
        """
        participants = []
        
        # Define participation mapping
        participation_map = {
            'economy': lambda npc: npc.participates_in_economy,
            'diplomacy': lambda npc: npc.participates_in_diplomacy,
            'tension': lambda npc: npc.participates_in_tension,
            'religion': lambda npc: npc.participates_in_religion,
            'espionage': lambda npc: npc.participates_in_espionage,
        }
        
        check_participation = participation_map.get(system_name, lambda npc: False)
        
        # Search through all tiers
        all_npcs = list(self.tier_1_npcs.values()) + list(self.tier_2_npcs.values()) + \
                  list(self.tier_3_npcs.values()) + list(self.tier_3_5_npcs.values())
        
        for npc in all_npcs:
            if check_participation(npc):
                if poi_ids is None or npc.poi_id in poi_ids:
                    participants.append(npc)
        
        return participants
    
    def get_computational_budget_status(self) -> Dict[str, Any]:
        """
        Get current computational budget status for scaling decisions.
        """
        return {
            'metrics': self.metrics,
            'budget_status': {
                'cpu_units_used': self.metrics.computational_load,
                'memory_mb_used': self.metrics.memory_usage_mb,
                'npcs_by_tier': {
                    'tier_1': self.metrics.tier_1_count,
                    'tier_2': self.metrics.tier_2_count,
                    'tier_3': self.metrics.tier_3_count,
                    'tier_3_5': self.metrics.tier_3_5_count,
                    'tier_4': self.metrics.tier_4_count,
                },
                'efficiency_ratio': self.metrics.visible_npcs / max(1, self.metrics.total_npcs),
            },
            'recommendations': self._get_scaling_recommendations()
        }
    
    # ================================
    # PRIVATE METHODS
    # ================================
    
    async def _get_npc_instance(self, npc_id: UUID) -> Optional[NPCInstance]:
        """Get NPC instance from appropriate tier storage."""
        if npc_id in self.tier_1_npcs:
            return self.tier_1_npcs[npc_id]
        elif npc_id in self.tier_2_npcs:
            return self.tier_2_npcs[npc_id]
        elif npc_id in self.tier_3_npcs:
            return self.tier_3_npcs[npc_id]
        elif npc_id in self.tier_3_5_npcs:
            return self.tier_3_5_npcs[npc_id]
        else:
            # Check if it's a Tier 4 NPC (stored in database only)
            return await self._load_tier_4_npc(npc_id)
    
    async def _promote_npc(self, npc: NPCInstance, target_tier: NPCTier) -> None:
        """Promote NPC to higher tier (lower number = higher tier)."""
        old_tier = npc.current_tier
        
        # Remove from old tier storage
        await self._remove_from_tier_storage(npc.npc_id, old_tier)
        
        # Expand data as needed for new tier
        if target_tier == NPCTier.TIER_1_ACTIVE:
            # Expand to full data
            npc.full_memory = npc.full_memory or {"memories": [], "relationships": {}}
            npc.conversation_context = {"active_topics": [], "mood": "neutral"}
            npc.relationship_data = {"player_relationships": {}}
        elif target_tier == NPCTier.TIER_2_BACKGROUND:
            # Keep compressed data
            npc.conversation_context = None
            npc.relationship_data = None
        
        # Update tier and add to new storage
        npc.current_tier = target_tier
        await self._add_to_tier_storage(npc)
        
        logger.debug(f"Promoted NPC {npc.npc_id} from {old_tier.value} to {target_tier.value}")
    
    async def _demote_npc(self, npc: NPCInstance, target_tier: NPCTier) -> None:
        """Demote NPC to lower tier (higher number = lower tier)."""
        old_tier = npc.current_tier
        
        # Remove from old tier storage
        await self._remove_from_tier_storage(npc.npc_id, old_tier)
        
        # Compress data as needed for new tier
        if target_tier in [NPCTier.TIER_3_DORMANT, NPCTier.TIER_3_5_COMPRESSED]:
            # Compress to core data only
            if npc.full_memory:
                npc.memory_summary = f"Summary of {len(npc.full_memory.get('memories', []))} memories"
                npc.full_memory = None
            npc.conversation_context = None
            npc.relationship_data = None
        elif target_tier == NPCTier.TIER_4_STATISTICAL:
            # Store to database and remove from memory
            await self._store_tier_4_npc(npc)
            return
        
        # Update tier and add to new storage
        npc.current_tier = target_tier
        await self._add_to_tier_storage(npc)
        
        logger.debug(f"Demoted NPC {npc.npc_id} from {old_tier.value} to {target_tier.value}")
    
    async def _remove_from_tier_storage(self, npc_id: UUID, tier: NPCTier) -> None:
        """Remove NPC from tier-specific storage."""
        if tier == NPCTier.TIER_1_ACTIVE and npc_id in self.tier_1_npcs:
            del self.tier_1_npcs[npc_id]
        elif tier == NPCTier.TIER_2_BACKGROUND and npc_id in self.tier_2_npcs:
            del self.tier_2_npcs[npc_id]
        elif tier == NPCTier.TIER_3_DORMANT and npc_id in self.tier_3_npcs:
            del self.tier_3_npcs[npc_id]
        elif tier == NPCTier.TIER_3_5_COMPRESSED and npc_id in self.tier_3_5_npcs:
            del self.tier_3_5_npcs[npc_id]
    
    async def _add_to_tier_storage(self, npc: NPCInstance) -> None:
        """Add NPC to tier-specific storage."""
        if npc.current_tier == NPCTier.TIER_1_ACTIVE:
            self.tier_1_npcs[npc.npc_id] = npc
        elif npc.current_tier == NPCTier.TIER_2_BACKGROUND:
            self.tier_2_npcs[npc.npc_id] = npc
        elif npc.current_tier == NPCTier.TIER_3_DORMANT:
            self.tier_3_npcs[npc.npc_id] = npc
        elif npc.current_tier == NPCTier.TIER_3_5_COMPRESSED:
            self.tier_3_5_npcs[npc.npc_id] = npc
    
    async def _load_tier_4_npc(self, npc_id: UUID) -> Optional[NPCInstance]:
        """Load Tier 4 NPC from database storage."""
        # Implementation would load from database
        # For now, return None indicating NPC not found in memory
        return None
    
    async def _store_tier_4_npc(self, npc: NPCInstance) -> None:
        """Store NPC as Tier 4 in database and remove from memory."""
        # Implementation would store compressed NPC data to database
        # Update metrics
        pass
    
    async def _update_metrics(self) -> None:
        """Update performance metrics."""
        self.metrics.tier_1_count = len(self.tier_1_npcs)
        self.metrics.tier_2_count = len(self.tier_2_npcs)
        self.metrics.tier_3_count = len(self.tier_3_npcs)
        self.metrics.tier_3_5_count = len(self.tier_3_5_npcs)
        
        # Calculate computational costs
        self.metrics.tier_1_cpu_units = self.metrics.tier_1_count * self.tier_costs[NPCTier.TIER_1_ACTIVE]
        self.metrics.tier_2_cpu_units = self.metrics.tier_2_count * self.tier_costs[NPCTier.TIER_2_BACKGROUND]
        self.metrics.tier_3_cpu_units = (self.metrics.tier_3_count + self.metrics.tier_3_5_count) * \
                                      self.tier_costs[NPCTier.TIER_3_DORMANT]
        
        # Calculate memory costs
        self.metrics.tier_1_memory_mb = self.metrics.tier_1_count * self.memory_costs[NPCTier.TIER_1_ACTIVE]
        self.metrics.tier_2_memory_mb = self.metrics.tier_2_count * self.memory_costs[NPCTier.TIER_2_BACKGROUND]
        self.metrics.tier_3_memory_mb = (self.metrics.tier_3_count + self.metrics.tier_3_5_count) * \
                                      self.memory_costs[NPCTier.TIER_3_DORMANT]
    
    def _get_scaling_recommendations(self) -> List[str]:
        """Get scaling recommendations based on current metrics."""
        recommendations = []
        
        if self.metrics.tier_1_count > 100:
            recommendations.append("Consider reducing Tier 1 promotion time (< 1 hour)")
        
        if self.metrics.computational_load > 1000:
            recommendations.append("High computational load - consider aggressive tier demotion")
        
        if self.metrics.memory_usage_mb > 1000:
            recommendations.append("High memory usage - consider more aggressive compression")
        
        efficiency = self.metrics.visible_npcs / max(1, self.metrics.total_npcs)
        if efficiency > 0.1:
            recommendations.append("High visible NPC ratio - world may feel too crowded")
        
        return recommendations 