"""
Tests for Memory Behavioral Examples
-----------------------------------

Test suite for the comprehensive behavioral examples that demonstrate
how memories influence NPC behavior across different scenarios.
"""

import pytest
from typing import List, Dict, Any

from backend.systems.memory.docs.behavioral_examples import (
    MemoryBehaviorExamples,
    BehaviorExample
)


class TestBehaviorExample:
    """Test the BehaviorExample dataclass"""
    
    def test_behavior_example_creation(self):
        """Test creating a behavior example"""
        example = BehaviorExample(
            name="Test Example",
            description="A test example",
            scenario="Test scenario",
            memory_content="Test memory content",
            memory_category="test",
            memory_importance=0.8,
            behavioral_outcome={"trust": 0.7},
            systems_affected=["social"],
            decision_factors={"test_factor": 0.5}
        )
        
        assert example.name == "Test Example"
        assert example.description == "A test example"
        assert example.scenario == "Test scenario"
        assert example.memory_content == "Test memory content"
        assert example.memory_category == "test"
        assert example.memory_importance == 0.8
        assert example.behavioral_outcome == {"trust": 0.7}
        assert example.systems_affected == ["social"]
        assert example.decision_factors == {"test_factor": 0.5}


class TestRelationshipMemoryExamples:
    """Test relationship memory examples"""
    
    def test_get_relationship_memory_examples(self):
        """Test getting relationship memory examples"""
        examples = MemoryBehaviorExamples.get_relationship_memory_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check that all examples are BehaviorExample instances
        for example in examples:
            assert isinstance(example, BehaviorExample)
            assert example.name
            assert example.description
            assert example.scenario
            assert example.memory_content
            assert example.memory_category
            assert 0.0 <= example.memory_importance <= 1.0
            assert isinstance(example.behavioral_outcome, dict)
            assert isinstance(example.systems_affected, list)
            assert isinstance(example.decision_factors, dict)
    
    def test_betrayal_memory_example(self):
        """Test specific betrayal memory example"""
        examples = MemoryBehaviorExamples.get_relationship_memory_examples()
        
        # Find betrayal example
        betrayal_example = None
        for example in examples:
            if "Betrayal" in example.name:
                betrayal_example = example
                break
        
        assert betrayal_example is not None
        assert "betrayal" in betrayal_example.memory_content.lower() or "betrayed" in betrayal_example.memory_content.lower()
        assert betrayal_example.memory_importance > 0.7  # Should be high importance
        assert "trust_level" in betrayal_example.behavioral_outcome
        assert betrayal_example.behavioral_outcome["trust_level"] < 0.5  # Low trust
        assert "social" in betrayal_example.systems_affected
    
    def test_helpful_memory_example(self):
        """Test specific helpful memory example"""
        examples = MemoryBehaviorExamples.get_relationship_memory_examples()
        
        # Find helpful example
        helpful_example = None
        for example in examples:
            if "Helpful" in example.name or "help" in example.name.lower():
                helpful_example = example
                break
        
        assert helpful_example is not None
        assert helpful_example.memory_importance > 0.5
        assert "trust_level" in helpful_example.behavioral_outcome
        assert helpful_example.behavioral_outcome["trust_level"] > 0.5  # High trust
        assert "social" in helpful_example.systems_affected
    
    def test_repeated_interactions_example(self):
        """Test repeated interactions example"""
        examples = MemoryBehaviorExamples.get_relationship_memory_examples()
        
        # Find repeated interactions example
        repeated_example = None
        for example in examples:
            if "Repeated" in example.name or "multiple" in example.description.lower():
                repeated_example = example
                break
        
        assert repeated_example is not None
        assert "relationship" in repeated_example.memory_category.lower()
        assert "economy" in repeated_example.systems_affected


class TestEventMemoryExamples:
    """Test event memory examples"""
    
    def test_get_event_memory_examples(self):
        """Test getting event memory examples"""
        examples = MemoryBehaviorExamples.get_event_memory_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check that all examples are BehaviorExample instances
        for example in examples:
            assert isinstance(example, BehaviorExample)
            assert example.memory_importance > 0.0
            assert len(example.systems_affected) > 0
    
    def test_war_trauma_example(self):
        """Test war trauma example"""
        examples = MemoryBehaviorExamples.get_event_memory_examples()
        
        # Find war trauma example
        war_example = None
        for example in examples:
            if "War" in example.name or "battle" in example.memory_content.lower():
                war_example = example
                break
        
        assert war_example is not None
        assert "trauma" in war_example.memory_category.lower()
        assert war_example.memory_importance > 0.8  # Very high importance
        assert "combat" in war_example.systems_affected
        assert "flee_threshold" in war_example.behavioral_outcome
        assert war_example.behavioral_outcome["flee_threshold"] > 0.5  # High flee threshold
    
    def test_economic_trauma_example(self):
        """Test economic trauma example"""
        examples = MemoryBehaviorExamples.get_event_memory_examples()
        
        # Find economic trauma example
        economic_example = None
        for example in examples:
            if "Market" in example.name or "economic" in example.description.lower():
                economic_example = example
                break
        
        assert economic_example is not None
        assert "economy" in economic_example.systems_affected
        assert "risk_tolerance" in economic_example.behavioral_outcome
        assert economic_example.behavioral_outcome["risk_tolerance"] < 0.5  # Risk averse
    
    def test_magical_disaster_example(self):
        """Test magical disaster example"""
        examples = MemoryBehaviorExamples.get_event_memory_examples()
        
        # Find magical disaster example
        magic_example = None
        for example in examples:
            if "Magic" in example.name or "magical" in example.description.lower():
                magic_example = example
                break
        
        assert magic_example is not None
        assert "magic" in magic_example.systems_affected
        assert "magic_user_trust" in magic_example.behavioral_outcome
        assert magic_example.behavioral_outcome["magic_user_trust"] < 0.5  # Low trust of magic users


class TestLocationMemoryExamples:
    """Test location memory examples"""
    
    def test_get_location_memory_examples(self):
        """Test getting location memory examples"""
        examples = MemoryBehaviorExamples.get_location_memory_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check that all examples are BehaviorExample instances
        for example in examples:
            assert isinstance(example, BehaviorExample)
            assert "location" in example.description.lower() or "place" in example.description.lower()
    
    def test_childhood_home_example(self):
        """Test childhood home example"""
        examples = MemoryBehaviorExamples.get_location_memory_examples()
        
        # Find childhood home example
        childhood_example = None
        for example in examples:
            if "Childhood" in example.name or "childhood" in example.memory_content.lower():
                childhood_example = example
                break
        
        assert childhood_example is not None
        assert "core" in childhood_example.memory_category.lower()
        assert childhood_example.memory_importance > 0.8  # Very high importance
        # Should have positive behavioral outcomes in familiar location


class TestFactionMemoryExamples:
    """Test faction memory examples"""
    
    def test_get_faction_memory_examples(self):
        """Test getting faction memory examples"""
        examples = MemoryBehaviorExamples.get_faction_memory_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check that all examples are BehaviorExample instances
        for example in examples:
            assert isinstance(example, BehaviorExample)
            assert "faction" in example.systems_affected
    
    def test_faction_examples_have_faction_bias(self):
        """Test that faction examples include faction bias in behavioral outcomes"""
        examples = MemoryBehaviorExamples.get_faction_memory_examples()
        
        for example in examples:
            # Should have some faction-related behavioral outcome
            has_faction_outcome = any(
                key for key in example.behavioral_outcome.keys()
                if "faction" in key.lower() or "loyalty" in key.lower() or "bias" in key.lower()
            )
            assert has_faction_outcome or "diplomatic_stance" in example.behavioral_outcome


class TestDecisionMakingExamples:
    """Test decision-making examples"""
    
    def test_get_decision_making_examples(self):
        """Test getting decision-making examples"""
        examples = MemoryBehaviorExamples.get_decision_making_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check that all examples are BehaviorExample instances
        for example in examples:
            assert isinstance(example, BehaviorExample)
            assert len(example.decision_factors) > 0  # Should have decision factors
    
    def test_decision_examples_have_clear_outcomes(self):
        """Test that decision examples have clear behavioral outcomes"""
        examples = MemoryBehaviorExamples.get_decision_making_examples()
        
        for example in examples:
            assert len(example.behavioral_outcome) > 0
            assert len(example.decision_factors) > 0
            # Decision factors should be numeric
            for factor_value in example.decision_factors.values():
                assert isinstance(factor_value, (int, float))
                assert -1.0 <= factor_value <= 1.0  # Should be normalized


class TestCrossSystemIntegrationExamples:
    """Test cross-system integration examples"""
    
    def test_get_cross_system_integration_examples(self):
        """Test getting cross-system integration examples"""
        examples = MemoryBehaviorExamples.get_cross_system_integration_examples()
        
        assert isinstance(examples, list)
        assert len(examples) > 0
        
        # Check that all examples are BehaviorExample instances
        for example in examples:
            assert isinstance(example, BehaviorExample)
            assert len(example.systems_affected) > 1  # Should affect multiple systems
    
    def test_cross_system_examples_affect_multiple_systems(self):
        """Test that cross-system examples affect multiple game systems"""
        examples = MemoryBehaviorExamples.get_cross_system_integration_examples()
        
        for example in examples:
            assert len(example.systems_affected) >= 2  # At least 2 systems
            
            # Should have behavioral outcomes that relate to multiple systems
            outcome_keys = list(example.behavioral_outcome.keys())
            assert len(outcome_keys) > 1


class TestAllExamples:
    """Test the collection of all examples"""
    
    def test_get_all_examples(self):
        """Test getting all examples organized by category"""
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        assert isinstance(all_examples, dict)
        assert len(all_examples) > 0
        
        # Check expected categories
        expected_categories = [
            "relationship_memories",
            "event_memories", 
            "location_memories",
            "faction_memories",
            "decision_making",
            "cross_system_integration"
        ]
        
        for category in expected_categories:
            assert category in all_examples
            assert isinstance(all_examples[category], list)
            assert len(all_examples[category]) > 0
    
    def test_all_examples_are_valid(self):
        """Test that all examples in the collection are valid"""
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        for category, examples in all_examples.items():
            for example in examples:
                assert isinstance(example, BehaviorExample)
                assert example.name
                assert example.description
                assert example.scenario
                assert example.memory_content
                assert example.memory_category
                assert 0.0 <= example.memory_importance <= 1.0
                assert isinstance(example.behavioral_outcome, dict)
                assert isinstance(example.systems_affected, list)
                assert isinstance(example.decision_factors, dict)
                assert len(example.systems_affected) > 0


class TestExamplesBySystem:
    """Test filtering examples by system"""
    
    def test_get_examples_by_system_social(self):
        """Test getting examples that affect the social system"""
        social_examples = MemoryBehaviorExamples.get_examples_by_system("social")
        
        assert isinstance(social_examples, list)
        assert len(social_examples) > 0
        
        for example in social_examples:
            assert "social" in example.systems_affected
    
    def test_get_examples_by_system_economy(self):
        """Test getting examples that affect the economy system"""
        economy_examples = MemoryBehaviorExamples.get_examples_by_system("economy")
        
        assert isinstance(economy_examples, list)
        assert len(economy_examples) > 0
        
        for example in economy_examples:
            assert "economy" in example.systems_affected
    
    def test_get_examples_by_system_combat(self):
        """Test getting examples that affect the combat system"""
        combat_examples = MemoryBehaviorExamples.get_examples_by_system("combat")
        
        assert isinstance(combat_examples, list)
        assert len(combat_examples) > 0
        
        for example in combat_examples:
            assert "combat" in example.systems_affected
    
    def test_get_examples_by_system_faction(self):
        """Test getting examples that affect the faction system"""
        faction_examples = MemoryBehaviorExamples.get_examples_by_system("faction")
        
        assert isinstance(faction_examples, list)
        assert len(faction_examples) > 0
        
        for example in faction_examples:
            assert "faction" in example.systems_affected
    
    def test_get_examples_by_system_nonexistent(self):
        """Test getting examples for a non-existent system"""
        nonexistent_examples = MemoryBehaviorExamples.get_examples_by_system("nonexistent")
        
        assert isinstance(nonexistent_examples, list)
        assert len(nonexistent_examples) == 0


class TestExamplesByMemoryCategory:
    """Test filtering examples by memory category"""
    
    def test_get_examples_by_memory_category_trauma(self):
        """Test getting examples with trauma memory category"""
        trauma_examples = MemoryBehaviorExamples.get_examples_by_memory_category("trauma")
        
        assert isinstance(trauma_examples, list)
        assert len(trauma_examples) > 0
        
        for example in trauma_examples:
            assert "trauma" in example.memory_category.lower()
            assert example.memory_importance > 0.7  # Trauma should be high importance
    
    def test_get_examples_by_memory_category_achievement(self):
        """Test getting examples with achievement memory category"""
        achievement_examples = MemoryBehaviorExamples.get_examples_by_memory_category("achievement")
        
        assert isinstance(achievement_examples, list)
        assert len(achievement_examples) > 0
        
        for example in achievement_examples:
            assert "achievement" in example.memory_category.lower()
    
    def test_get_examples_by_memory_category_relationship(self):
        """Test getting examples with relationship memory category"""
        relationship_examples = MemoryBehaviorExamples.get_examples_by_memory_category("relationship")
        
        assert isinstance(relationship_examples, list)
        assert len(relationship_examples) > 0
        
        for example in relationship_examples:
            assert "relationship" in example.memory_category.lower()
            assert "social" in example.systems_affected  # Should affect social system
    
    def test_get_examples_by_memory_category_core(self):
        """Test getting examples with core memory category"""
        core_examples = MemoryBehaviorExamples.get_examples_by_memory_category("core")
        
        assert isinstance(core_examples, list)
        assert len(core_examples) > 0
        
        for example in core_examples:
            assert "core" in example.memory_category.lower()
            assert example.memory_importance > 0.8  # Core memories should be very important


class TestBehaviorDocumentation:
    """Test behavior documentation generation"""
    
    def test_generate_behavior_documentation(self):
        """Test generating comprehensive behavior documentation"""
        documentation = MemoryBehaviorExamples.generate_behavior_documentation()
        
        assert isinstance(documentation, str)
        assert len(documentation) > 0
        
        # Should contain key sections
        assert "Memory-Driven Behavior Examples" in documentation
        assert "Relationship Memories" in documentation
        assert "Event Memories" in documentation
        assert "Location Memories" in documentation
        assert "Faction Memories" in documentation
        assert "Decision Making" in documentation
        assert "Cross-System Integration" in documentation
    
    def test_documentation_includes_all_examples(self):
        """Test that documentation includes all example categories"""
        documentation = MemoryBehaviorExamples.generate_behavior_documentation()
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        # Check that each category is represented in the documentation
        for category in all_examples.keys():
            # Convert category name to a readable format that should appear in docs
            readable_category = category.replace("_", " ").title()
            assert readable_category in documentation or category in documentation
    
    def test_documentation_includes_example_details(self):
        """Test that documentation includes specific example details"""
        documentation = MemoryBehaviorExamples.generate_behavior_documentation()
        
        # Should include some specific example names or content
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        # Check that at least some example names appear in the documentation
        example_names_found = 0
        for category, examples in all_examples.items():
            for example in examples[:2]:  # Check first 2 examples from each category
                if example.name in documentation:
                    example_names_found += 1
        
        assert example_names_found > 0  # At least some examples should be in the docs


class TestExampleValidation:
    """Test validation of example data integrity"""
    
    def test_all_examples_have_required_fields(self):
        """Test that all examples have required fields populated"""
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        for category, examples in all_examples.items():
            for example in examples:
                # Required string fields
                assert example.name and len(example.name.strip()) > 0
                assert example.description and len(example.description.strip()) > 0
                assert example.scenario and len(example.scenario.strip()) > 0
                assert example.memory_content and len(example.memory_content.strip()) > 0
                assert example.memory_category and len(example.memory_category.strip()) > 0
                
                # Required numeric fields
                assert isinstance(example.memory_importance, (int, float))
                assert 0.0 <= example.memory_importance <= 1.0
                
                # Required collection fields
                assert isinstance(example.behavioral_outcome, dict)
                assert len(example.behavioral_outcome) > 0
                assert isinstance(example.systems_affected, list)
                assert len(example.systems_affected) > 0
                assert isinstance(example.decision_factors, dict)
                assert len(example.decision_factors) > 0
    
    def test_behavioral_outcomes_are_numeric(self):
        """Test that behavioral outcomes contain numeric values"""
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        for category, examples in all_examples.items():
            for example in examples:
                for key, value in example.behavioral_outcome.items():
                    if isinstance(value, (int, float)):
                        # Numeric values should be in reasonable ranges
                        assert -2.0 <= value <= 2.0  # Allow some flexibility for modifiers
                    elif isinstance(value, bool):
                        # Boolean values are acceptable
                        pass
                    elif isinstance(value, str):
                        # String values are acceptable for categorical outcomes
                        assert len(value.strip()) > 0
                    elif isinstance(value, list):
                        # List values are acceptable for multiple items
                        assert len(value) > 0
                    else:
                        # Other types should be documented if needed
                        assert False, f"Unexpected behavioral outcome type: {type(value)} for {key}"
    
    def test_decision_factors_are_numeric(self):
        """Test that decision factors contain numeric values in valid ranges"""
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        for category, examples in all_examples.items():
            for example in examples:
                for key, value in example.decision_factors.items():
                    assert isinstance(value, (int, float)), f"Decision factor {key} should be numeric"
                    assert -1.0 <= value <= 1.0, f"Decision factor {key} should be in range [-1.0, 1.0]"
    
    def test_systems_affected_are_valid(self):
        """Test that systems affected contain valid system names"""
        valid_systems = {
            "social", "economy", "faction", "combat", "magic", 
            "quest", "dialogue", "rumor", "diplomacy", "religion",
            "crafting", "inventory", "equipment", "loot", "intelligence",
            "law", "military", "alliance", "moral"
        }
        
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        for category, examples in all_examples.items():
            for example in examples:
                for system in example.systems_affected:
                    assert isinstance(system, str)
                    assert system.lower() in valid_systems, f"Unknown system: {system}"
    
    def test_memory_categories_are_consistent(self):
        """Test that memory categories use consistent naming"""
        valid_categories = {
            "trauma", "achievement", "relationship", "core", 
            "mundane", "faction", "location", "event"
        }
        
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        for category, examples in all_examples.items():
            for example in examples:
                assert example.memory_category.lower() in valid_categories, \
                    f"Unknown memory category: {example.memory_category}" 