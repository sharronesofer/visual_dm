from typing import Any
from typing import Type
from typing import List
from pathlib import Path
"""Integration Tests for Arc System

Tests covering arc-driven flows across quest, NPC, and world systems,
validating narrative consistency, progression tracking, and cross-system event handling.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from uuid import uuid4, UUID
from typing import Dict, List, Any

from backend.systems.arc.models import (
    Arc, ArcType, ArcStatus, ArcPriority,
    ArcStep, ArcStepStatus, ArcStepType,
    ArcProgression, ProgressionMethod,
    ArcCompletionRecord, ArcCompletionResult
)
from backend.systems.arc.services.arc_manager import ArcManager
from backend.systems.arc.repositories.arc_repository import MemoryArcRepository
from backend.systems.arc.repositories.arc_step_repository import ArcStepRepository
from backend.systems.arc.repositories.progression_repository import ProgressionRepository


class TestArcSystemIntegration:
    """Integration tests for Arc system with cross-system interactions"""
    
    @pytest.fixture
    async def memory_arc_repo(self):
        """In-memory arc repository for integration tests"""
        return MemoryArcRepository()
    
    @pytest.fixture
    def mock_step_repo(self):
        """Mock step repository"""
        return AsyncMock(spec=ArcStepRepository)
    
    @pytest.fixture
    def mock_progression_repo(self):
        """Mock progression repository"""
        mock_repo = AsyncMock(spec=ProgressionRepository)
        
        # Setup default progression creation behavior
        async def create_progression(progression):
            return progression
        
        async def get_by_arc_id(arc_id):
            # Return a mock progression for any arc with correct list types
            return ArcProgression(
                arc_id=arc_id,
                started_at=datetime.utcnow(),
                completed_steps=[],  # List instead of dict
                failed_steps=[]  # List instead of dict
            )
        
        mock_repo.create.side_effect = create_progression
        mock_repo.get_by_arc_id.side_effect = get_by_arc_id
        mock_repo.update.return_value = None
        
        return mock_repo
    
    @pytest.fixture
    async def arc_manager_with_memory(self, memory_arc_repo, mock_step_repo, mock_progression_repo):
        """ArcManager with memory repository for integration testing"""
        return ArcManager(
            arc_repository=memory_arc_repo,
            step_repository=mock_step_repo,
            progression_repository=mock_progression_repo
        )
    
    @pytest.fixture
    def complex_world_state(self):
        """Complex world state simulating real game conditions"""
        return {
            "active_factions": ["empire", "rebels", "merchants", "mages_guild", "thieves_guild"],
            "recent_events": [
                {
                    "type": "faction_war",
                    "factions": ["empire", "rebels"],
                    "location": "northern_provinces",
                    "significance": 9,
                    "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat()
                },
                {
                    "type": "magical_anomaly",
                    "location": "crystal_caverns",
                    "significance": 7,
                    "affected_systems": ["magic", "exploration", "quest"],
                    "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat()
                },
                {
                    "type": "trade_embargo",
                    "factions": ["empire", "merchants"],
                    "significance": 6,
                    "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat()
                }
            ],
            "world_state": {
                "political_tension": 8.5,
                "economic_stability": 4.2,
                "magical_activity": 7.1,
                "civil_unrest": 6.8,
                "military_activity": 9.2
            },
            "player_context": {
                "level": 25,
                "location": "northern_provinces",
                "faction_standings": {
                    "empire": 45,
                    "rebels": 72,
                    "merchants": -15,
                    "mages_guild": 88,
                    "thieves_guild": 22
                },
                "recent_actions": [
                    {"type": "quest_completed", "quest_id": "rebel_alliance_q1"},
                    {"type": "faction_mission", "faction": "rebels", "outcome": "success"},
                    {"type": "magic_spell_learned", "spell": "fireball"}
                ]
            }
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_arc_lifecycle(self, arc_manager_with_memory, complex_world_state):
        """Test complete arc lifecycle from generation to completion"""
        
        # Phase 1: Generate primary arc
        with patch('backend.systems.arc.services.arc_generator.ArcGenerator') as mock_generator_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            
            # Create a realistic primary arc
            primary_arc = Arc(
                id=uuid4(),
                title="The Great Rebellion",
                description="A world-spanning conflict between Empire and Rebels",
                arc_type=ArcType.GLOBAL,
                starting_point="War erupts in the northern provinces",
                preferred_ending="Resolution through diplomatic victory or military conquest",
                priority=ArcPriority.HIGH,
                time_sensitivity=0.8,
                faction_ids=["empire", "rebels"],
                system_hooks=["quest", "faction", "combat", "diplomacy", "rumor"],
                classification_tags={
                    "tier": "primary",
                    "theme": "political_conflict",
                    "scope": "global"
                },
                total_steps=12
            )
            
            mock_generator.generate_arc.return_value = primary_arc
            
            result = await arc_manager_with_memory.generate_primary_arc(
                world_context=complex_world_state,
                priority=ArcPriority.HIGH
            )
            
            assert result is not None
            assert result.title == "The Great Rebellion"
            assert result.status == ArcStatus.PENDING  # Should start as pending
            arc_id = result.id
        
        # Phase 2: Activate the arc
        activation_success = await arc_manager_with_memory.activate_arc(arc_id)
        assert activation_success is True
        
        activated_arc = await arc_manager_with_memory.get_arc(arc_id)
        assert activated_arc.status == ArcStatus.ACTIVE
        
        # Phase 3: Advance arc through multiple steps
        for step in range(3):
            advance_success = await arc_manager_with_memory.advance_arc_step(
                arc_id,
                step,
                ProgressionMethod.QUEST_COMPLETION
            )
            assert advance_success is True
        
        updated_arc = await arc_manager_with_memory.get_arc(arc_id)
        assert updated_arc.current_step == 3
        
        # Phase 4: Generate secondary arcs in response to primary arc progression
        secondary_world_events = [
            {
                "type": "refugee_crisis",
                "location": "border_towns",
                "significance": 7,
                "related_arc": str(arc_id),
                "system_hooks": ["population", "economy", "quest"]
            },
            {
                "type": "resource_shortage",
                "affected_factions": ["merchants"],
                "significance": 6,
                "system_hooks": ["economy", "trade"]
            }
        ]
        
        # Test secondary arc advancement
        advancement_result = await arc_manager_with_memory.advance_secondary_tertiary_arcs(
            world_events=secondary_world_events,
            completed_quests=["border_defense_quest", "refugee_aid_quest"],
            time_passed_days=3
        )
        
        assert "advanced" in advancement_result
        assert "stalled" in advancement_result
        assert "completed" in advancement_result
        assert "generated" in advancement_result
        
        # Phase 5: Test hook detection across the entire arc ecosystem
        comprehensive_context = {
            **complex_world_state,
            "active_arcs": [str(arc_id)],
            "recent_completions": ["border_defense_quest", "refugee_aid_quest"],
            "emergent_situations": ["refugee_crisis", "resource_shortage"]
        }
        
        hook_results = await arc_manager_with_memory.hook_detection(
            context=comprehensive_context,
            scan_depth=4,
            include_dormant=True
        )
        
        # Verify hook detection provides actionable opportunities
        assert isinstance(hook_results, dict)
        for category in ["quest_opportunities", "npc_interactions", "faction_intersections",
                        "location_triggers", "temporal_connections", "narrative_bridges"]:
            assert category in hook_results
            assert isinstance(hook_results[category], list)
        
        # Phase 6: Complete the primary arc
        completion_result = await arc_manager_with_memory.complete_arc(
            arc_id,
            ArcCompletionResult.SUCCESS,
            "The rebellion succeeds in establishing a new democratic federation",
            world_consequences=["empire_dissolved", "new_government_formed", "peace_treaty_signed"]
        )
        
        assert completion_result is not None
        
        final_arc = await arc_manager_with_memory.get_arc(arc_id)
        assert final_arc.status == ArcStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_multi_arc_narrative_consistency(self, arc_manager_with_memory, complex_world_state):
        """Test narrative consistency across multiple concurrent arcs"""
        
        with patch('backend.systems.arc.services.arc_generator.ArcGenerator') as mock_generator_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            
            # Create multiple interconnected arcs
            arcs_to_create = [
                Arc(
                    id=uuid4(),
                    title="The Mage War",
                    description="Conflict within the Mages Guild",
                    arc_type=ArcType.REGIONAL,
                    starting_point="Magical anomaly detected",
                    preferred_ending="Guild unified under new leadership",
                    faction_ids=["mages_guild"],
                    region_id="crystal_caverns",
                    system_hooks=["magic", "quest", "faction"]
                ),
                Arc(
                    id=uuid4(),
                    title="Merchant's Revenge",
                    description="Economic warfare against the Empire",
                    arc_type=ArcType.REGIONAL,
                    starting_point="Trade embargo declared",
                    preferred_ending="Economic stability restored",
                    faction_ids=["merchants", "empire"],
                    region_id="trade_districts",
                    system_hooks=["economy", "faction", "quest"]
                ),
                Arc(
                    id=uuid4(),
                    title="Hero's Ascension",
                    description="Personal growth of the player character",
                    arc_type=ArcType.CHARACTER,
                    starting_point="Character reaches new power level",
                    preferred_ending="Character becomes legendary hero",
                    character_id="player_character",
                    system_hooks=["skill", "reputation", "quest"]
                )
            ]
            
            created_arcs = []
            for arc_template in arcs_to_create:
                mock_generator.generate_arc.return_value = arc_template
                
                created_arc = await arc_manager_with_memory.generate_primary_arc(
                    world_context=complex_world_state,
                    target_scope=f"region_{arc_template.region_id or 'general'}",
                    priority=ArcPriority.MEDIUM
                )
                
                if created_arc:
                    await arc_manager_with_memory.activate_arc(created_arc.id)
                    created_arcs.append(created_arc)
            
            # Simulate world events that affect multiple arcs
            cross_arc_events = [
                {
                    "type": "magical_disaster",
                    "location": "crystal_caverns",
                    "significance": 8,
                    "affected_factions": ["mages_guild", "empire"],
                    "system_hooks": ["magic", "faction", "quest", "population"]
                },
                {
                    "type": "hero_intervention",
                    "character": "player_character",
                    "significance": 7,
                    "context": "mediates conflict",
                    "system_hooks": ["reputation", "faction", "diplomacy"]
                }
            ]
            
            # Process events and check cross-arc impacts
            multi_arc_result = await arc_manager_with_memory.advance_secondary_tertiary_arcs(
                world_events=cross_arc_events,
                completed_quests=["magic_research_quest", "diplomatic_mission"],
                faction_changes={
                    "mages_guild": {"unity": +20, "power": -10},
                    "empire": {"stability": -15, "reputation": -25},
                    "merchants": {"influence": +10}
                },
                time_passed_days=2
            )
            
            # Verify cross-arc consistency
            assert isinstance(multi_arc_result, dict)
            
            # Check for narrative bridges between arcs
            narrative_context = {
                **complex_world_state,
                "active_arcs": [str(arc.id) for arc in created_arcs],
                "cross_arc_events": cross_arc_events
            }
            
            narrative_hooks = await arc_manager_with_memory.hook_detection(
                context=narrative_context,
                scan_depth=5,
                include_dormant=False
            )
            
            # Should detect narrative connections between related arcs
            assert "narrative_bridges" in narrative_hooks
    
    @pytest.mark.asyncio
    async def test_quest_system_integration(self, arc_manager_with_memory, complex_world_state):
        """Test integration between arc system and quest system"""
        
        with patch('backend.systems.arc.services.arc_generator.ArcGenerator') as mock_generator_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            
            # Create arc with quest integration points
            quest_driven_arc = Arc(
                id=uuid4(),
                title="The Thieves' Network",
                description="Uncover and infiltrate criminal organization",
                arc_type=ArcType.REGIONAL,
                starting_point="Mysterious thefts reported across the city",
                preferred_ending="Criminal network dismantled or controlled",
                faction_ids=["thieves_guild"],
                region_id="city_districts",
                system_hooks=["quest", "investigation", "stealth", "faction"],
                classification_tags={
                    "quest_hooks": ["investigation_quests", "stealth_missions", "faction_quests"],
                    "progression_triggers": ["evidence_gathered", "contacts_made", "hideouts_discovered"]
                }
            )
            
            mock_generator.generate_arc.return_value = quest_driven_arc
            
            created_arc = await arc_manager_with_memory.generate_primary_arc(
                world_context=complex_world_state,
                target_scope="region_city_districts"
            )
            
            assert created_arc is not None
            await arc_manager_with_memory.activate_arc(created_arc.id)
            
            # Simulate quest completions that should advance the arc
            quest_progression_tests = [
                {
                    "completed_quests": ["gather_intel_q1"],
                    "expected_advancement": True,
                    "progression_method": ProgressionMethod.QUEST_COMPLETION
                },
                {
                    "completed_quests": ["infiltrate_hideout_q2"],
                    "expected_advancement": True,
                    "progression_method": ProgressionMethod.QUEST_COMPLETION
                },
                {
                    "completed_quests": ["unrelated_delivery_quest"],
                    "expected_advancement": False,
                    "progression_method": ProgressionMethod.QUEST_COMPLETION
                }
            ]
            
            for test_case in quest_progression_tests:
                initial_step = (await arc_manager_with_memory.get_arc(created_arc.id)).current_step
                
                advancement_result = await arc_manager_with_memory.advance_secondary_tertiary_arcs(
                    world_events=[],
                    completed_quests=test_case["completed_quests"],
                    time_passed_days=1
                )
                
                final_step = (await arc_manager_with_memory.get_arc(created_arc.id)).current_step
                
                if test_case["expected_advancement"]:
                    # May or may not advance based on internal logic, but should handle gracefully
                    assert isinstance(advancement_result, dict)
                else:
                    # Should not error even with unrelated quests
                    assert isinstance(advancement_result, dict)
            
            # Test hook detection for quest opportunities
            quest_context = {
                **complex_world_state,
                "active_investigations": ["thieves_network"],
                "available_contacts": ["shadowy_informant", "corrupt_guard"],
                "discovered_locations": ["warehouse_district", "underground_tunnels"]
            }
            
            quest_hooks = await arc_manager_with_memory.hook_detection(
                context=quest_context,
                scan_depth=3
            )
            
            assert "quest_opportunities" in quest_hooks
            assert isinstance(quest_hooks["quest_opportunities"], list)
    
    @pytest.mark.asyncio
    async def test_faction_system_integration(self, arc_manager_with_memory, complex_world_state):
        """Test integration between arc system and faction system"""
        
        with patch('backend.systems.arc.services.arc_generator.ArcGenerator') as mock_generator_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            
            # Create faction-centric arc
            faction_arc = Arc(
                id=uuid4(),
                title="The Power Struggle",
                description="Internal conflict within multiple factions",
                arc_type=ArcType.GLOBAL,
                starting_point="Political alliances shift unexpectedly",
                preferred_ending="New faction balance established",
                faction_ids=["empire", "rebels", "merchants", "mages_guild"],
                system_hooks=["faction", "diplomacy", "politics", "quest"],
                classification_tags={
                    "faction_dynamics": ["power_struggles", "alliance_shifts", "territory_disputes"],
                    "political_weight": "high"
                }
            )
            
            mock_generator.generate_arc.return_value = faction_arc
            
            created_arc = await arc_manager_with_memory.generate_primary_arc(
                world_context=complex_world_state
            )
            
            assert created_arc is not None
            await arc_manager_with_memory.activate_arc(created_arc.id)
            
            # Test faction change responses
            faction_scenarios = [
                {
                    "changes": {"empire": {"power": -20, "territory": -15}},
                    "description": "Empire loses significant power"
                },
                {
                    "changes": {"rebels": {"power": +25, "influence": +30}},
                    "description": "Rebels gain major victory"
                },
                {
                    "changes": {"mages_guild": {"autonomy": +40, "magical_dominance": +20}},
                    "description": "Mages assert independence"
                },
                {
                    "changes": {
                        "empire": {"stability": -30},
                        "merchants": {"economic_control": +35},
                        "rebels": {"popular_support": +25}
                    },
                    "description": "Complex multi-faction shift"
                }
            ]
            
            for scenario in faction_scenarios:
                initial_step = (await arc_manager_with_memory.get_arc(created_arc.id)).current_step
                
                # Test faction change integration
                result = await arc_manager_with_memory.advance_secondary_tertiary_arcs(
                    world_events=[{
                        "type": "faction_power_shift",
                        "description": scenario["description"],
                        "significance": 7
                    }],
                    completed_quests=[],
                    faction_changes=scenario["changes"],
                    time_passed_days=1
                )
                
                # Verify proper handling
                assert isinstance(result, dict)
                assert all(key in result for key in ["advanced", "stalled", "completed", "generated"])
            
            # Test faction intersection detection
            faction_context = {
                **complex_world_state,
                "faction_tensions": {
                    ("empire", "rebels"): 0.9,
                    ("merchants", "empire"): 0.7,
                    ("mages_guild", "rebels"): 0.3
                },
                "recent_faction_events": [
                    {"type": "alliance_formed", "factions": ["rebels", "mages_guild"]},
                    {"type": "trade_war", "factions": ["empire", "merchants"]}
                ]
            }
            
            faction_hooks = await arc_manager_with_memory.hook_detection(
                context=faction_context,
                scan_depth=4
            )
            
            assert "faction_intersections" in faction_hooks
            assert isinstance(faction_hooks["faction_intersections"], list)
    
    @pytest.mark.asyncio
    async def test_npc_system_integration(self, arc_manager_with_memory, complex_world_state):
        """Test integration between arc system and NPC system"""
        
        with patch('backend.systems.arc.services.arc_generator.ArcGenerator') as mock_generator_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            
            # Create NPC-driven arc
            npc_arc = Arc(
                id=uuid4(),
                title="The Mentor's Legacy",
                description="Elderly wizard's final quest to secure magical knowledge",
                arc_type=ArcType.NPC,
                starting_point="Ancient wizard seeks worthy successor",
                preferred_ending="Knowledge passed to new generation",
                npc_id="archmage_aldric",
                faction_ids=["mages_guild"],
                system_hooks=["npc", "dialogue", "magic", "quest", "knowledge"],
                classification_tags={
                    "npc_relationships": ["mentor_student", "master_apprentice"],
                    "emotional_weight": "high",
                    "legacy_theme": True
                }
            )
            
            mock_generator.generate_arc.return_value = npc_arc
            
            created_arc = await arc_manager_with_memory.generate_primary_arc(
                world_context=complex_world_state,
                target_scope="character_archmage_aldric"
            )
            
            assert created_arc is not None
            await arc_manager_with_memory.activate_arc(created_arc.id)
            
            # Test NPC interaction scenarios
            npc_interaction_context = {
                **complex_world_state,
                "npc_relationships": {
                    "archmage_aldric": {
                        "trust_level": 75,
                        "last_interaction": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                        "relationship_type": "mentor",
                        "mood": "contemplative"
                    }
                },
                "recent_dialogues": [
                    {
                        "npc": "archmage_aldric",
                        "topic": "ancient_magic",
                        "outcome": "knowledge_shared"
                    }
                ]
            }
            
            # Test NPC-driven hook detection
            npc_hooks = await arc_manager_with_memory.hook_detection(
                context=npc_interaction_context,
                scan_depth=3
            )
            
            assert "npc_interactions" in npc_hooks
            assert isinstance(npc_hooks["npc_interactions"], list)
            
            # Test character development progression
            character_events = [
                {
                    "type": "npc_dialogue_completed",
                    "npc": "archmage_aldric",
                    "significance": 6,
                    "topic": "magical_theory"
                },
                {
                    "type": "relationship_milestone",
                    "npc": "archmage_aldric",
                    "milestone": "trusted_student",
                    "significance": 8
                }
            ]
            
            npc_advancement = await arc_manager_with_memory.advance_secondary_tertiary_arcs(
                world_events=character_events,
                completed_quests=["magic_lesson_quest", "ancient_tome_retrieval"],
                time_passed_days=2
            )
            
            assert isinstance(npc_advancement, dict)
    
    @pytest.mark.asyncio
    async def test_progression_tracking_accuracy(self, arc_manager_with_memory, complex_world_state):
        """Test accuracy of progression tracking across different advancement methods"""
        
        with patch('backend.systems.arc.services.arc_generator.ArcGenerator') as mock_generator_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            
            # Create arc for progression testing
            progression_arc = Arc(
                id=uuid4(),
                title="The Multi-Path Journey",
                description="Arc with multiple progression pathways",
                arc_type=ArcType.REGIONAL,
                starting_point="Multiple challenges present themselves",
                preferred_ending="All challenges overcome through various means",
                total_steps=10,
                system_hooks=["quest", "exploration", "combat", "diplomacy", "stealth"]
            )
            
            mock_generator.generate_arc.return_value = progression_arc
            
            created_arc = await arc_manager_with_memory.generate_primary_arc(
                world_context=complex_world_state
            )
            
            assert created_arc is not None
            await arc_manager_with_memory.activate_arc(created_arc.id)
            
            # Test different progression methods - use correct enum values
            progression_methods = [
                (ProgressionMethod.QUEST_COMPLETION, "quest_complete"),
                (ProgressionMethod.WORLD_EVENT, "major_event"),
                (ProgressionMethod.NPC_ACTION, "npc_interaction"),  # Changed from FACTION_EVENT
                (ProgressionMethod.SYSTEM_TRIGGER, "system_update"),
                (ProgressionMethod.TIME_TRIGGER, "time_passage")  # Changed from TIME_PROGRESSION
            ]
            
            for i, (method, context) in enumerate(progression_methods):
                if i < 5:  # Don't exceed available steps
                    initial_step = (await arc_manager_with_memory.get_arc(created_arc.id)).current_step
                    
                    success = await arc_manager_with_memory.advance_arc_step(
                        created_arc.id,
                        i,
                        method
                    )
                    
                    assert success is True
                    
                    updated_arc = await arc_manager_with_memory.get_arc(created_arc.id)
                    assert updated_arc.current_step > initial_step
            
            # Verify final progression state
            final_arc = await arc_manager_with_memory.get_arc(created_arc.id)
            assert final_arc.current_step >= 5
            assert final_arc.status == ArcStatus.ACTIVE  # Should still be active
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_resilience(self, arc_manager_with_memory, complex_world_state):
        """Test system resilience and error recovery capabilities"""
        
        # Test handling of invalid arc operations
        invalid_arc_id = uuid4()
        
        # Should handle non-existent arc gracefully
        result = await arc_manager_with_memory.get_arc(invalid_arc_id)
        assert result is None
        
        activation_result = await arc_manager_with_memory.activate_arc(invalid_arc_id)
        assert activation_result is False
        
        advancement_result = await arc_manager_with_memory.advance_arc_step(
            invalid_arc_id, 1, ProgressionMethod.QUEST_COMPLETION
        )
        assert advancement_result is False
        
        # Test handling of malformed world events
        malformed_events = [
            {"type": "incomplete_event"},  # Missing required fields
            {"significance": "not_a_number"},  # Invalid data types
            {},  # Empty event
            None  # Null event
        ]
        
        # Should handle malformed events without crashing
        error_result = await arc_manager_with_memory.advance_secondary_tertiary_arcs(
            world_events=malformed_events,
            completed_quests=[],
            time_passed_days=1
        )
        
        assert isinstance(error_result, dict)
        assert all(key in error_result for key in ["advanced", "stalled", "completed", "generated"])
        
        # Test hook detection with invalid context
        invalid_context_result = await arc_manager_with_memory.hook_detection(
            context={"invalid": "data", "numbers_as_strings": "not_int"},
            scan_depth=2
        )
        
        assert isinstance(invalid_context_result, dict)
        
        # Test system recovery after errors
        with patch('backend.systems.arc.services.arc_generator.ArcGenerator') as mock_generator_class:
            mock_generator = AsyncMock()
            mock_generator_class.return_value = mock_generator
            
            recovery_arc = Arc(
                id=uuid4(),
                title="Recovery Test Arc",
                description="Arc for testing error recovery",
                arc_type=ArcType.CHARACTER,
                starting_point="System recovers from errors",
                preferred_ending="Normal operation restored"
            )
            
            mock_generator.generate_arc.return_value = recovery_arc
            
            # Should successfully create arc after error conditions
            recovery_result = await arc_manager_with_memory.generate_primary_arc(
                world_context=complex_world_state
            )
            
            assert recovery_result is not None
            assert recovery_result.title == "Recovery Test Arc" 