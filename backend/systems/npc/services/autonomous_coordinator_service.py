"""
Autonomous NPC System Coordinator Service

Orchestrates all autonomous NPC services including:
- Emotional state management
- Personality evolution
- Crisis response
- Real-world economic integration
- System health monitoring
- Bulk processing operations
- Dependency management between services
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from uuid import UUID
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
import json

from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import NpcTierStatus
from backend.infrastructure.systems.npc.models.personality_evolution_models import (
    NpcPersonalityEvolution, NpcCrisisResponse
)
from backend.infrastructure.systems.npc.models.emotional_state_models import NpcEmotionalState

from backend.systems.npc.services.emotional_state_service import EmotionalStateService
from backend.systems.npc.services.personality_evolution_service import PersonalityEvolutionService
from backend.systems.npc.services.crisis_response_service import CrisisResponseService
from backend.systems.npc.services.autonomous_lifecycle_service import AutonomousLifecycleService
from backend.systems.economy.services.real_world_economy_service import RealWorldEconomyService

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of a processing operation"""
    npc_id: UUID
    success: bool
    processing_time: float
    operations_completed: List[str]
    errors: List[str]
    data_changes: Dict[str, Any]


@dataclass
class SystemHealthMetrics:
    """System health metrics"""
    total_npcs: int
    active_emotional_states: int
    ongoing_personality_evolutions: int
    active_crisis_responses: int
    processing_queue_size: int
    average_processing_time: float
    error_rate: float
    memory_usage: float


class AutonomousNpcCoordinator:
    """Coordinator service for all autonomous NPC systems"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        
        # Initialize component services
        self.emotional_service = EmotionalStateService(db_session)
        self.personality_service = PersonalityEvolutionService(db_session)
        self.crisis_service = CrisisResponseService(db_session, self.personality_service, self.emotional_service)
        self.lifecycle_service = AutonomousLifecycleService(db_session)
        self.economy_service = RealWorldEconomyService(db_session)
        
        # Processing configuration
        self.processing_config = {
            "max_concurrent_threads": 4,
            "batch_size": 100,
            "error_retry_attempts": 3,
            "processing_timeout": 300,  # 5 minutes
            "tier_priority_weights": {1: 1.0, 2: 0.7, 3: 0.4, 4: 0.1}
        }
        
        # Thread pools for concurrent processing
        self.thread_pool = ThreadPoolExecutor(max_workers=self.processing_config["max_concurrent_threads"])
        
        # System health tracking
        self.last_health_check = datetime.utcnow()
        self.processing_stats = {"operations": 0, "errors": 0, "total_time": 0.0}
    
    async def process_daily_updates(self, npc_batch_size: int = 100) -> Dict[str, Any]:
        """Process comprehensive daily updates for all autonomous NPC systems"""
        start_time = datetime.utcnow()
        
        # Get all NPCs ordered by tier priority
        npcs_by_tier = await self._get_npcs_by_tier_priority()
        
        results = {
            "start_time": start_time.isoformat(),
            "total_npcs": sum(len(npcs) for npcs in npcs_by_tier.values()),
            "tier_results": {},
            "system_wide_operations": {},
            "errors": [],
            "performance_metrics": {}
        }
        
        # Process each tier with appropriate priority
        for tier, npc_ids in npcs_by_tier.items():
            if not npc_ids:
                continue
                
            tier_start = datetime.utcnow()
            logger.info(f"Processing tier {tier} NPCs: {len(npc_ids)} NPCs")
            
            # Process in batches to manage memory and performance
            tier_results = await self._process_tier_batch(tier, npc_ids, npc_batch_size)
            
            tier_duration = (datetime.utcnow() - tier_start).total_seconds()
            results["tier_results"][tier] = {
                **tier_results,
                "processing_time_seconds": tier_duration,
                "npcs_per_second": len(npc_ids) / max(tier_duration, 1)
            }
        
        # Process system-wide operations
        results["system_wide_operations"] = await self._process_system_wide_operations()
        
        # Calculate final metrics
        total_duration = (datetime.utcnow() - start_time).total_seconds()
        results["performance_metrics"] = {
            "total_processing_time_seconds": total_duration,
            "average_npc_processing_time": total_duration / max(results["total_npcs"], 1),
            "operations_per_second": results["total_npcs"] / max(total_duration, 1)
        }
        
        return results
    
    async def _get_npcs_by_tier_priority(self) -> Dict[int, List[UUID]]:
        """Get NPCs organized by tier with proper priority ordering"""
        npcs_by_tier = {1: [], 2: [], 3: [], 4: []}
        
        # Query all NPCs with their tier status
        npcs_with_tiers = self.db_session.query(NpcEntity, NpcTierStatus).outerjoin(
            NpcTierStatus, NpcEntity.id == NpcTierStatus.npc_id
        ).all()
        
        for npc, tier_status in npcs_with_tiers:
            if tier_status:
                tier = tier_status.current_tier
            else:
                # Default tier assignment for NPCs without tier status
                tier = 4
            
            npcs_by_tier[tier].append(npc.id)
        
        return npcs_by_tier
    
    async def _process_tier_batch(self, tier: int, npc_ids: List[UUID], batch_size: int) -> Dict[str, Any]:
        """Process a batch of NPCs for a specific tier"""
        
        results = {
            "tier": tier,
            "total_npcs": len(npc_ids),
            "successful_processes": 0,
            "failed_processes": 0,
            "operations_summary": {
                "emotional_updates": 0,
                "personality_evolutions": 0,
                "crisis_responses": 0,
                "lifecycle_updates": 0
            },
            "errors": []
        }
        
        # Process in batches
        for i in range(0, len(npc_ids), batch_size):
            batch = npc_ids[i:i + batch_size]
            batch_results = await self._process_npc_batch(tier, batch)
            
            # Aggregate results
            results["successful_processes"] += batch_results["successful_processes"]
            results["failed_processes"] += batch_results["failed_processes"]
            results["errors"].extend(batch_results["errors"])
            
            # Aggregate operation counts
            for operation, count in batch_results["operations_summary"].items():
                results["operations_summary"][operation] += count
        
        return results
    
    async def _process_npc_batch(self, tier: int, npc_ids: List[UUID]) -> Dict[str, Any]:
        """Process a single batch of NPCs"""
        
        batch_results = {
            "successful_processes": 0,
            "failed_processes": 0,
            "operations_summary": {
                "emotional_updates": 0,
                "personality_evolutions": 0,
                "crisis_responses": 0,
                "lifecycle_updates": 0
            },
            "errors": []
        }
        
        # Create processing tasks
        processing_tasks = []
        for npc_id in npc_ids:
            task = self._process_single_npc(npc_id, tier)
            processing_tasks.append(task)
        
        # Execute batch concurrently
        if tier <= 2:  # High priority NPCs get concurrent processing
            batch_results_list = await asyncio.gather(*processing_tasks, return_exceptions=True)
        else:  # Lower priority NPCs get sequential processing
            batch_results_list = []
            for task in processing_tasks:
                result = await task
                batch_results_list.append(result)
        
        # Aggregate individual results
        for result in batch_results_list:
            if isinstance(result, Exception):
                batch_results["failed_processes"] += 1
                batch_results["errors"].append(str(result))
            elif result.success:
                batch_results["successful_processes"] += 1
                # Count operations
                for operation in result.operations_completed:
                    if operation in batch_results["operations_summary"]:
                        batch_results["operations_summary"][operation] += 1
            else:
                batch_results["failed_processes"] += 1
                batch_results["errors"].extend(result.errors)
        
        return batch_results
    
    async def _process_single_npc(self, npc_id: UUID, tier: int) -> ProcessingResult:
        """Process all autonomous systems for a single NPC"""
        start_time = datetime.utcnow()
        operations_completed = []
        errors = []
        data_changes = {}
        
        try:
            # 1. Process emotional decay (daily)
            try:
                emotional_result = self.emotional_service.process_daily_emotional_decay(npc_id)
                operations_completed.append("emotional_updates")
                data_changes["emotional_changes"] = emotional_result
            except Exception as e:
                errors.append(f"Emotional processing error: {str(e)}")
            
            # 2. Process personality evolution (daily)
            try:
                personality_result = self.personality_service.process_daily_personality_evolution(npc_id)
                operations_completed.append("personality_evolutions")
                data_changes["personality_changes"] = personality_result
            except Exception as e:
                errors.append(f"Personality processing error: {str(e)}")
            
            # 3. Check for ongoing crisis responses
            try:
                crisis_responses = self.db_session.query(NpcCrisisResponse).filter(
                    NpcCrisisResponse.npc_id == npc_id,
                    NpcCrisisResponse.response_completed == False
                ).all()
                
                for crisis_response in crisis_responses:
                    crisis_result = self.crisis_service.process_ongoing_crisis(crisis_response.id)
                    operations_completed.append("crisis_responses")
                    data_changes[f"crisis_{crisis_response.id}"] = crisis_result
            except Exception as e:
                errors.append(f"Crisis processing error: {str(e)}")
            
            # 4. Process lifecycle updates (for tier 1-2 NPCs only)
            if tier <= 2:
                try:
                    lifecycle_result = self.lifecycle_service.process_monthly_lifecycle_update(npc_id)
                    operations_completed.append("lifecycle_updates")
                    data_changes["lifecycle_changes"] = lifecycle_result
                except Exception as e:
                    errors.append(f"Lifecycle processing error: {str(e)}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ProcessingResult(
                npc_id=npc_id,
                success=len(errors) == 0,
                processing_time=processing_time,
                operations_completed=operations_completed,
                errors=errors,
                data_changes=data_changes
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            return ProcessingResult(
                npc_id=npc_id,
                success=False,
                processing_time=processing_time,
                operations_completed=operations_completed,
                errors=[f"Critical error: {str(e)}"],
                data_changes={}
            )
    
    async def _process_system_wide_operations(self) -> Dict[str, Any]:
        """Process system-wide operations like economic cycles"""
        
        operations_results = {}
        
        try:
            # Update economic cycles based on real-world data
            economy_result = self.economy_service.update_game_economic_cycles()
            operations_results["economic_cycle_update"] = economy_result
            
            # Check for economic crises
            crisis_detection = self.economy_service.create_crisis_from_real_world_event()
            if crisis_detection:
                operations_results["economic_crisis_detected"] = crisis_detection
            
            # System health assessment
            health_status = self.get_system_health_status()
            operations_results["system_health"] = health_status
            
        except Exception as e:
            operations_results["system_wide_errors"] = [str(e)]
        
        return operations_results
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        
        # Count active entities
        total_npcs = self.db_session.query(NpcEntity).count()
        
        active_emotional_states = self.db_session.query(NpcEmotionalState).filter(
            NpcEmotionalState.last_updated >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        ongoing_personality_evolutions = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.is_complete == False
        ).count()
        
        active_crisis_responses = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.response_completed == False
        ).count()
        
        # Economic cycle status
        from backend.infrastructure.database.economy.advanced_models import EconomicCycle
        active_economic_cycles = self.db_session.query(EconomicCycle).filter(
            EconomicCycle.is_active == True
        ).count()
        
        # Performance metrics
        error_rate = 0.0
        if self.processing_stats["operations"] > 0:
            error_rate = self.processing_stats["errors"] / self.processing_stats["operations"]
        
        average_processing_time = 0.0
        if self.processing_stats["operations"] > 0:
            average_processing_time = self.processing_stats["total_time"] / self.processing_stats["operations"]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_npcs": total_npcs,
            "active_emotional_states": active_emotional_states,
            "ongoing_personality_evolutions": ongoing_personality_evolutions,
            "active_crisis_responses": active_crisis_responses,
            "economic_cycles_status": {
                "active_cycles": active_economic_cycles,
                "last_update": datetime.utcnow().isoformat()
            },
            "system_performance": {
                "error_rate": error_rate,
                "average_processing_time_seconds": average_processing_time,
                "total_operations_processed": self.processing_stats["operations"]
            }
        }
    
    def get_comprehensive_statistics(self, time_range_days: int = 30) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=time_range_days)
        
        # Personality evolution statistics
        personality_changes = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.started_at >= start_date
        ).count()
        
        completed_evolutions = self.db_session.query(NpcPersonalityEvolution).filter(
            NpcPersonalityEvolution.started_at >= start_date,
            NpcPersonalityEvolution.is_complete == True
        ).count()
        
        # Crisis response statistics
        crisis_responses = self.db_session.query(NpcCrisisResponse).filter(
            NpcCrisisResponse.crisis_start_date >= start_date
        ).count()
        
        # Emotional state statistics
        emotional_triggers = self.db_session.query(NpcEmotionalState).filter(
            NpcEmotionalState.last_updated >= start_date
        ).count()
        
        # Economic activity statistics
        from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import NpcEconomicHistory
        economic_transactions = self.db_session.query(NpcEconomicHistory).filter(
            NpcEconomicHistory.transaction_date >= start_date
        ).count()
        
        return {
            "time_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": time_range_days
            },
            "personality_evolution": {
                "total_changes_initiated": personality_changes,
                "completed_evolutions": completed_evolutions,
                "completion_rate": completed_evolutions / max(personality_changes, 1)
            },
            "crisis_responses": {
                "total_crisis_events": crisis_responses,
                "crisis_frequency_per_day": crisis_responses / time_range_days
            },
            "emotional_activity": {
                "emotional_state_updates": emotional_triggers,
                "average_updates_per_day": emotional_triggers / time_range_days
            },
            "economic_activity": {
                "total_transactions": economic_transactions,
                "transactions_per_day": economic_transactions / time_range_days
            }
        }
    
    async def bulk_process_emotional_decay(self, npc_ids: Optional[List[UUID]] = None) -> Dict[str, Any]:
        """Process emotional decay for multiple NPCs in bulk"""
        
        if npc_ids is None:
            # Get all NPCs with active emotional states
            emotional_states = self.db_session.query(NpcEmotionalState).all()
            npc_ids = [state.npc_id for state in emotional_states]
        
        results = {"processed_count": 0, "errors": []}
        
        # Process in batches for performance
        batch_size = self.processing_config["batch_size"]
        for i in range(0, len(npc_ids), batch_size):
            batch = npc_ids[i:i + batch_size]
            
            for npc_id in batch:
                try:
                    self.emotional_service.process_daily_emotional_decay(npc_id)
                    results["processed_count"] += 1
                except Exception as e:
                    results["errors"].append({"npc_id": str(npc_id), "error": str(e)})
        
        self.db_session.commit()
        return results
    
    async def bulk_process_personality_evolution(self, npc_ids: Optional[List[UUID]] = None) -> Dict[str, Any]:
        """Process personality evolution for multiple NPCs in bulk"""
        
        if npc_ids is None:
            # Get all NPCs with ongoing personality evolutions
            evolutions = self.db_session.query(NpcPersonalityEvolution).filter(
                NpcPersonalityEvolution.is_complete == False
            ).all()
            npc_ids = list(set([evolution.npc_id for evolution in evolutions]))
        
        results = {"processed_count": 0, "errors": []}
        
        # Process in batches for performance
        batch_size = self.processing_config["batch_size"]
        for i in range(0, len(npc_ids), batch_size):
            batch = npc_ids[i:i + batch_size]
            
            for npc_id in batch:
                try:
                    self.personality_service.process_daily_personality_evolution(npc_id)
                    results["processed_count"] += 1
                except Exception as e:
                    results["errors"].append({"npc_id": str(npc_id), "error": str(e)})
        
        self.db_session.commit()
        return results
    
    async def trigger_mass_crisis_event(self, crisis_type: str, crisis_description: str, 
                                      crisis_severity: float, affected_regions: List[str] = None,
                                      npc_selection_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger a crisis event affecting multiple NPCs"""
        
        # Determine affected NPCs
        affected_npcs = self._select_npcs_for_crisis(affected_regions, npc_selection_criteria)
        
        results = {
            "crisis_type": crisis_type,
            "total_affected_npcs": len(affected_npcs),
            "successful_triggers": 0,
            "failed_triggers": 0,
            "errors": []
        }
        
        # Trigger crisis for each affected NPC
        for npc_id in affected_npcs:
            try:
                crisis_result = self.crisis_service.trigger_crisis_response(
                    npc_id, crisis_type, crisis_description, crisis_severity,
                    {"mass_event": True, "affected_regions": affected_regions}
                )
                
                if crisis_result.get("success", False):
                    results["successful_triggers"] += 1
                else:
                    results["failed_triggers"] += 1
                    results["errors"].append({
                        "npc_id": str(npc_id),
                        "error": crisis_result.get("error", "Unknown error")
                    })
                    
            except Exception as e:
                results["failed_triggers"] += 1
                results["errors"].append({"npc_id": str(npc_id), "error": str(e)})
        
        return results
    
    def _select_npcs_for_crisis(self, affected_regions: List[str] = None, 
                               selection_criteria: Dict[str, Any] = None) -> List[UUID]:
        """Select NPCs to be affected by a crisis event"""
        
        query = self.db_session.query(NpcEntity)
        
        # Filter by regions if specified
        if affected_regions:
            query = query.filter(NpcEntity.region_id.in_(affected_regions))
        
        # Apply additional selection criteria
        if selection_criteria:
            if "min_age" in selection_criteria:
                query = query.filter(NpcEntity.age >= selection_criteria["min_age"])
            if "max_age" in selection_criteria:
                query = query.filter(NpcEntity.age <= selection_criteria["max_age"])
            if "races" in selection_criteria:
                query = query.filter(NpcEntity.race.in_(selection_criteria["races"]))
        
        npcs = query.all()
        return [npc.id for npc in npcs] 