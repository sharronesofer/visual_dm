"""
Memory-Driven Behavioral Examples
---------------------------------

This module provides comprehensive examples of how the memory system influences 
NPC behavior and decision-making across different scenarios and systems.

These examples serve as both documentation and test scenarios for the memory
behavior influence system.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class BehaviorExample:
    """Represents a concrete example of memory-driven behavior"""
    name: str
    description: str
    scenario: str
    memory_content: str
    memory_category: str
    memory_importance: float
    behavioral_outcome: Dict[str, Any]
    systems_affected: List[str]
    decision_factors: Dict[str, float]


class MemoryBehaviorExamples:
    """
    Comprehensive collection of examples showing how memories influence behavior.
    
    This class provides concrete examples that demonstrate the memory-behavior
    integration requirements from Task 73.
    """
    
    @staticmethod
    def get_relationship_memory_examples() -> List[BehaviorExample]:
        """Examples of how past interactions affect current NPC responses"""
        
        return [
            BehaviorExample(
                name="Betrayal Memory - Trust Impact",
                description="NPC remembers being betrayed by a faction member",
                scenario="Player approaches NPC wearing faction colors that betrayed them",
                memory_content="Marcus from the Red Hawks betrayed our trust, took my family's farm deed and never returned it as promised. Left us with nothing.",
                memory_category="trauma",
                memory_importance=0.9,
                behavioral_outcome={
                    "trust_level": 0.2,  # Very low trust
                    "trade_willingness": 0.3,  # Reluctant to trade
                    "conversation_openness": 0.4,  # Guarded in conversation
                    "faction_bias": -0.8,  # Strong negative bias against Red Hawks
                    "aggression_modifier": 1.3,  # Slightly more aggressive
                    "flee_threshold": 0.4  # More likely to flee if threatened
                },
                systems_affected=["social", "economy", "faction", "combat"],
                decision_factors={
                    "past_betrayal_weight": 0.8,
                    "faction_recognition": 0.9,
                    "trust_override": -0.7
                }
            ),
            
            BehaviorExample(
                name="Helpful Memory - Trust Boost",
                description="NPC remembers player helping during a crisis",
                scenario="Player returns to NPC who they helped save from bandits",
                memory_content="The stranger fought off three bandits to save my cart. Refused payment and just asked for directions.",
                memory_category="achievement",
                memory_importance=0.8,
                behavioral_outcome={
                    "trust_level": 0.85,  # High trust
                    "trade_willingness": 0.9,  # Very willing to trade
                    "price_modifier": 0.8,  # 20% discount
                    "conversation_openness": 0.9,  # Very open to conversation
                    "rumor_sharing": 0.8,  # Willing to share information
                    "quest_offering": 0.7  # Likely to offer quests/help
                },
                systems_affected=["social", "economy", "quest", "rumor"],
                decision_factors={
                    "gratitude_weight": 0.9,
                    "personal_debt": 0.7,
                    "character_assessment": 0.8
                }
            ),
            
            BehaviorExample(
                name="Repeated Interactions - Relationship Building",
                description="NPC has multiple positive interactions with player",
                scenario="Player has traded fairly with merchant multiple times",
                memory_content="This customer always pays fair prices, never haggles unfairly, and once warned me about counterfeit coins.",
                memory_category="relationship",
                memory_importance=0.6,
                behavioral_outcome={
                    "trust_level": 0.75,
                    "preferred_customer_status": True,
                    "price_modifier": 0.9,  # 10% discount
                    "trade_priority": 0.8,  # Gets first pick of goods
                    "credit_extension": 0.6,  # Willing to offer credit
                    "information_sharing": 0.7  # Shares market info
                },
                systems_affected=["economy", "social", "rumor"],
                decision_factors={
                    "relationship_history": 0.8,
                    "consistency_bonus": 0.6,
                    "mutual_benefit": 0.7
                }
            )
        ]
    
    @staticmethod
    def get_event_memory_examples() -> List[BehaviorExample]:
        """Examples of how NPCs react differently based on witnessed events"""
        
        return [
            BehaviorExample(
                name="War Trauma - Combat Avoidance",
                description="NPC witnessed brutal battle, now avoids conflict",
                scenario="Combat breaks out near the NPC",
                memory_content="Saw the Battle of Thornfield. Bodies everywhere. Young men screaming. The smell of blood and smoke.",
                memory_category="trauma",
                memory_importance=0.95,
                behavioral_outcome={
                    "combat_participation": 0.1,  # Almost never fights
                    "flee_threshold": 0.7,  # Flees at first sign of danger
                    "aggression_modifier": 0.3,  # Very passive
                    "peace_advocacy": 0.9,  # Strongly advocates for peace
                    "weapon_aversion": 0.8,  # Uncomfortable around weapons
                    "ptsd_triggers": ["battle_sounds", "blood", "large_crowds"]
                },
                systems_affected=["combat", "social", "faction"],
                decision_factors={
                    "trauma_intensity": 0.95,
                    "self_preservation": 0.9,
                    "peace_value": 0.8
                }
            ),
            
            BehaviorExample(
                name="Market Crash Memory - Economic Caution",
                description="NPC lost everything in economic collapse, now very cautious",
                scenario="Player offers high-risk, high-reward trade opportunity",
                memory_content="Put all my savings into the Goldshore Trading Company. Collapsed overnight. Lost everything including the family shop.",
                memory_category="trauma",
                memory_importance=0.8,
                behavioral_outcome={
                    "risk_tolerance": 0.2,  # Very risk averse
                    "investment_willingness": 0.1,  # Almost never invests
                    "price_negotiation": 1.4,  # Drives hard bargains
                    "savings_hoarding": 0.9,  # Keeps large cash reserves
                    "business_expansion": 0.2,  # Reluctant to expand
                    "financial_paranoia": 0.7  # Suspicious of financial schemes
                },
                systems_affected=["economy", "social"],
                decision_factors={
                    "past_loss_weight": 0.8,
                    "financial_security": 0.9,
                    "risk_assessment": 0.85
                }
            ),
            
            BehaviorExample(
                name="Magical Disaster Witness - Magic Fear",
                description="NPC saw magical accident, now fears magic users",
                scenario="Player casts spell near the NPC",
                memory_content="The apprentice's teleportation spell went wrong. Tore a hole in reality. Three people just... vanished. Forever.",
                memory_category="trauma",
                memory_importance=0.85,
                behavioral_outcome={
                    "magic_user_trust": 0.2,  # Very low trust of magic users
                    "spell_reaction": "flee",  # Runs when magic is cast
                    "magic_item_aversion": 0.8,  # Won't use/buy magic items
                    "superstition_level": 0.9,  # Highly superstitious
                    "anti_magic_advocacy": 0.7,  # Supports magic restrictions
                    "protection_seeking": 0.8  # Seeks magical protection items
                },
                systems_affected=["magic", "social", "economy", "faction"],
                decision_factors={
                    "magical_fear": 0.9,
                    "reality_stability_concern": 0.8,
                    "protection_priority": 0.7
                }
            )
        ]
    
    @staticmethod
    def get_location_memory_examples() -> List[BehaviorExample]:
        """Examples of how NPCs behave differently in places with strong memories"""
        
        return [
            BehaviorExample(
                name="Childhood Home - Nostalgic Behavior",
                description="NPC behaves differently in their childhood village location",
                scenario="NPC returns to village where they grew up",
                memory_content="This is where I learned to fish with my father. Every stone, every tree holds a memory of simpler times.",
                memory_category="core",
                memory_importance=0.9,
                behavioral_outcome={
                    "emotional_state": "nostalgic",
                    "social_openness": 0.8,
                    "story_telling": 0.9,
                    "protective_behavior": 0.8,
                    "generosity": 1.2,
                    "movement_pace": 0.7,  # Slower, taking time to reminisce
                    "memory_triggered_actions": ["visiting_old_spots", "seeking_familiar_faces"]
                },
                systems_affected=["social", "economy", "dialogue"],
                decision_factors={
                    "emotional_attachment": 0.9,
                    "nostalgia_weight": 0.8,
                    "protective_instinct": 0.7
                }
            ),
            
            BehaviorExample(
                name="Battle Site - Solemn Respect",
                description="NPC travels through location where major battle occurred",
                scenario="NPC travels through area where major battle occurred",
                memory_content="Here fell the brave defenders of Millhaven. My brother among them. The ground is still sacred with their sacrifice.",
                memory_category="trauma",
                memory_importance=0.85,
                behavioral_outcome={
                    "movement_speed": 0.7,
                    "noise_level": 0.3,
                    "ritualistic_behavior": 0.8,
                    "emotional_state": "solemn",
                    "aggressive_response": 0.9,
                    "teaching_moment": 0.8,
                    "sacred_space_protection": 0.95
                },
                systems_affected=["social", "combat", "religion"],
                decision_factors={
                    "respect_for_dead": 0.9,
                    "personal_loss": 0.8,
                    "sacred_duty": 0.85
                }
            ),
            
            BehaviorExample(
                name="Market Success Memory - Confident Trading",
                description="NPC conducts business in the location where they first succeeded",
                scenario="NPC conducts business in the market where they first succeeded",
                memory_content="This is where I made my first big sale. Turned two silver into two gold with one clever trade. I know these streets.",
                memory_category="achievement",
                memory_importance=0.7,
                behavioral_outcome={
                    "confidence_level": 1.3,
                    "negotiation_skill": 1.2,
                    "risk_tolerance": 1.1,
                    "local_knowledge": 0.9,
                    "network_activation": 0.8,
                    "mentoring_behavior": 0.7,
                    "territory_comfort": 0.9
                },
                systems_affected=["economy", "social", "dialogue"],
                decision_factors={
                    "success_memory": 0.8,
                    "confidence_boost": 0.7,
                    "familiar_territory": 0.9
                }
            )
        ]
    
    @staticmethod
    def get_faction_memory_examples() -> List[BehaviorExample]:
        """Examples of how historical faction conflicts influence current tensions"""
        
        return [
            BehaviorExample(
                name="Ancestral Feud - Inherited Hatred",
                description="NPC carries generational hatred for opposing faction",
                scenario="NPC encounters member of historically opposing faction",
                memory_content="The Iron Wolves killed my grandfather in the Border Wars. Family honor demands we never forget, never forgive.",
                memory_category="core",
                memory_importance=0.85,
                behavioral_outcome={
                    "faction_bias": -0.9,  # Extreme negative bias
                    "automatic_hostility": 0.8,  # Immediately hostile
                    "trust_level": 0.1,  # Virtually no trust possible
                    "combat_readiness": 1.4,  # Quick to fight
                    "alliance_impossibility": 0.95,  # Almost impossible to ally
                    "honor_bound_behavior": 0.9,  # Behavior driven by honor code
                    "vendetta_pursuit": 0.7  # Actively seeks revenge opportunities
                },
                systems_affected=["faction", "combat", "social", "diplomacy"],
                decision_factors={
                    "family_honor": 0.9,
                    "generational_memory": 0.8,
                    "cultural_obligation": 0.85
                }
            ),
            
            BehaviorExample(
                name="War Alliance - Lasting Bond",
                description="NPC fought alongside faction, maintains strong loyalty",
                scenario="NPC meets member of faction they fought beside in war",
                memory_content="Stood shield-to-shield with the Blue Company at Raven's Gate. They saved our lives. That bond never breaks.",
                memory_category="achievement",
                memory_importance=0.8,
                behavioral_outcome={
                    "faction_bias": 0.85,  # Strong positive bias
                    "automatic_trust": 0.8,  # High initial trust
                    "military_respect": 0.9,  # Respects military members especially
                    "aid_willingness": 0.9,  # Very willing to help
                    "resource_sharing": 0.7,  # Shares resources freely
                    "intelligence_sharing": 0.8,  # Shares tactical information
                    "veteran_recognition": 0.95  # Recognizes and honors fellow veterans
                },
                systems_affected=["faction", "social", "economy", "military"],
                decision_factors={
                    "battlefield_bond": 0.9,
                    "shared_sacrifice": 0.8,
                    "military_honor": 0.85
                }
            ),
            
            BehaviorExample(
                name="Political Persecution - Authority Distrust",
                description="NPC was persecuted by ruling faction, now distrusts authority",
                scenario="NPC interacts with official representatives of authority",
                memory_content="The City Guard came in the night. Took my father for 'sedition'. Never saw him again. Official justice is a lie.",
                memory_category="trauma",
                memory_importance=0.9,
                behavioral_outcome={
                    "faction_bias": -0.8,  # Strong negative bias against ruling faction
                    "authority_trust": 0.2,  # Very low trust of officials
                    "law_compliance": 0.4,  # Reluctant to follow laws
                    "underground_sympathy": 0.8,  # Sympathizes with rebels
                    "secret_keeping": 0.9,  # Excellent at keeping secrets
                    "resistance_support": 0.7,  # Supports resistance movements
                    "paranoia_level": 0.7,  # Paranoid about surveillance
                    "anti_establishment": 0.8  # Generally opposes established power
                },
                systems_affected=["faction", "social", "law"],
                decision_factors={
                    "injustice_memory": 0.9,
                    "authority_fear": 0.7,
                    "resistance_ideology": 0.8
                }
            )
        ]
    
    @staticmethod
    def get_decision_making_examples() -> List[BehaviorExample]:
        """Examples of memory-driven decision making processes"""
        
        return [
            BehaviorExample(
                name="Trust-Based Merchant Decision",
                description="Merchant decides whether to extend credit based on trust memories",
                scenario="Player requests to buy expensive item on credit",
                memory_content="Multiple positive trade interactions; player returned lost items; warned about counterfeits",
                memory_category="relationship",
                memory_importance=0.7,
                behavioral_outcome={
                    "credit_decision": True,
                    "credit_amount": 1.5,  # High credit allowance multiplier
                    "interest_rate": 0.05,  # 5% (favorable)
                    "collateral_required": False,
                    "payment_terms": "flexible",
                    "trust_factor": 0.8
                },
                systems_affected=["economy", "social"],
                decision_factors={
                    "payment_history": 0.9,
                    "character_assessment": 0.8,
                    "risk_mitigation": 0.6,
                    "relationship_value": 0.7
                }
            ),
            
            BehaviorExample(
                name="Combat Ally Recognition",
                description="NPC decides to help player in combat based on past aid",
                scenario="Player is outnumbered in combat near NPC",
                memory_content="Player helped defend my family from bandits last month",
                memory_category="achievement",
                memory_importance=0.8,
                behavioral_outcome={
                    "intervention_decision": True,
                    "intervention_speed": "immediate",
                    "combat_commitment": 0.9,  # Fights to the end
                    "tactical_support": True,  # Provides strategic help
                    "resource_expenditure": 0.8,  # Uses valuable resources
                    "risk_acceptance": 0.7  # Accepts personal risk
                },
                systems_affected=["combat", "social", "alliance"],
                decision_factors={
                    "debt_of_honor": 0.9,
                    "personal_loyalty": 0.8,
                    "reciprocity_principle": 0.85,
                    "tactical_assessment": 0.6
                }
            ),
            
            BehaviorExample(
                name="Information Sharing Decision",
                description="NPC decides whether to share sensitive information",
                scenario="Player asks about secret faction movements",
                memory_content="Player kept my secret about magical ability; never betrayed confidence",
                memory_category="relationship",
                memory_importance=0.75,
                behavioral_outcome={
                    "information_sharing": True,
                    "detail_level": "moderate",  # Some details withheld
                    "verification_provided": True,  # Provides proof
                    "warning_given": True,  # Warns about dangers
                    "source_protection": 0.9,  # Protects information sources
                    "mutual_benefit_seeking": 0.7
                },
                systems_affected=["social", "intelligence", "faction"],
                decision_factors={
                    "trust_level": 0.8,
                    "reciprocal_secrecy": 0.9,
                    "risk_assessment": 0.6,
                    "relationship_depth": 0.75
                }
            )
        ]
    
    @staticmethod
    def get_cross_system_integration_examples() -> List[BehaviorExample]:
        """Examples of how memories affect multiple systems simultaneously"""
        
        return [
            BehaviorExample(
                name="Trauma-Driven Multi-System Impact",
                description="Single traumatic memory affects economy, combat, and social behavior",
                scenario="NPC who lost family to dragon attack",
                memory_content="The red dragon burned everything. My wife, my children, my shop. Nothing left but ash and the smell of death.",
                memory_category="trauma",
                memory_importance=1.0,
                behavioral_outcome={
                    # Economic impacts
                    "business_motivation": 0.3,  # Little interest in trade
                    "price_sensitivity": 0.1,  # Money means little
                    "luxury_aversion": 0.9,  # No interest in luxury goods
                    
                    # Combat impacts
                    "dragon_phobia": 1.0,  # Flees from any dragon
                    "fire_aversion": 0.8,  # Avoids fire magic/weapons
                    "protection_seeking": 0.9,  # Seeks protective equipment
                    
                    # Social impacts
                    "emotional_numbness": 0.8,  # Difficulty connecting
                    "grief_sharing": 0.7,  # Shares grief with others
                    "survivor_guilt": 0.9,  # Feels guilty for surviving
                    
                    # Faction impacts
                    "dragon_hunter_support": 0.95,  # Supports dragon hunters
                    "anti_dragon_faction_bias": 0.9  # Joins anti-dragon groups
                },
                systems_affected=["economy", "combat", "social", "faction", "magic"],
                decision_factors={
                    "trauma_intensity": 1.0,
                    "loss_magnitude": 0.95,
                    "survivor_psychology": 0.8,
                    "grief_stage": 0.7
                }
            ),
            
            BehaviorExample(
                name="Heroic Memory - Positive Multi-System Impact",
                description="Memory of being saved creates positive changes across systems",
                scenario="NPC who was rescued from slavery by adventuring party",
                memory_content="They came like heroes from the stories. Broke our chains, gave us freedom. I owe them everything.",
                memory_category="achievement",
                memory_importance=0.9,
                behavioral_outcome={
                    # Economic impacts
                    "adventurer_discounts": 0.8,  # 20% discount to adventurers
                    "freedom_premium": 1.0,  # Pays extra for freedom-related goods
                    "charity_giving": 0.7,  # Gives to help others
                    
                    # Social impacts
                    "adventurer_recognition": 0.95,  # Recognizes adventurer types
                    "story_telling": 0.9,  # Shares rescue story
                    "hope_spreading": 0.8,  # Encourages others
                    
                    # Faction impacts
                    "anti_slavery_activism": 0.9,  # Fights against slavery
                    "liberation_support": 0.8,  # Supports liberation groups
                    
                    # Quest impacts
                    "rescue_mission_support": 0.9,  # Helps rescue missions
                    "information_network": 0.7  # Provides intelligence on slavers
                },
                systems_affected=["economy", "social", "faction", "quest", "moral"],
                decision_factors={
                    "gratitude_magnitude": 0.9,
                    "freedom_value": 0.95,
                    "moral_obligation": 0.8,
                    "empathy_level": 0.85
                }
            )
        ]
    
    @staticmethod
    def get_all_examples() -> Dict[str, List[BehaviorExample]]:
        """Get all behavioral examples organized by category"""
        
        return {
            "relationship_memories": MemoryBehaviorExamples.get_relationship_memory_examples(),
            "event_memories": MemoryBehaviorExamples.get_event_memory_examples(),
            "location_memories": MemoryBehaviorExamples.get_location_memory_examples(),
            "faction_memories": MemoryBehaviorExamples.get_faction_memory_examples(),
            "decision_making": MemoryBehaviorExamples.get_decision_making_examples(),
            "cross_system_integration": MemoryBehaviorExamples.get_cross_system_integration_examples()
        }
    
    @staticmethod
    def get_examples_by_system(system_name: str) -> List[BehaviorExample]:
        """Get all examples that affect a specific system"""
        
        all_examples = []
        for category_examples in MemoryBehaviorExamples.get_all_examples().values():
            all_examples.extend(category_examples)
        
        return [example for example in all_examples if system_name in example.systems_affected]
    
    @staticmethod
    def get_examples_by_memory_category(memory_category: str) -> List[BehaviorExample]:
        """Get all examples for a specific memory category"""
        
        all_examples = []
        for category_examples in MemoryBehaviorExamples.get_all_examples().values():
            all_examples.extend(category_examples)
        
        return [example for example in all_examples if example.memory_category == memory_category]
    
    @staticmethod
    def generate_behavior_documentation() -> str:
        """Generate comprehensive documentation of memory-driven behavior"""
        
        doc = """
# Memory-Driven Behavior Examples

This document provides comprehensive examples of how the memory system influences
NPC behavior and decision-making across all game systems.

## Overview

The memory system affects NPC behavior through several mechanisms:

1. **Trust Calculations**: Past interactions determine trust levels
2. **Risk Assessment**: Previous experiences influence risk perception
3. **Emotional Triggers**: Traumatic/positive memories affect emotional state
4. **Faction Bias**: Historical events shape political alignment
5. **Cross-System Integration**: Memories impact multiple systems simultaneously

## System Integration

### Economy System
- Price modifications based on trust and relationship
- Trade willingness affected by past experiences
- Credit decisions based on payment history
- Risk premiums for perceived threats

### Faction System
- Political alignment based on historical experiences
- Loyalty shifts from traumatic events
- Diplomatic stance from past faction interactions
- Resistance to propaganda based on trust levels

### Combat System
- Aggression levels modified by past trauma
- Flee thresholds based on fear memories
- Ally recognition from positive interactions
- Enemy prioritization from negative experiences

### Social System
- Conversation openness based on trust levels
- Topic preferences from past experiences
- Rumor credibility based on source trust
- Social influence modified by confidence

## Examples by Category
"""
        
        all_examples = MemoryBehaviorExamples.get_all_examples()
        
        for category, examples in all_examples.items():
            doc += f"\n### {category.replace('_', ' ').title()}\n\n"
            
            for example in examples:
                doc += f"**{example.name}**\n"
                doc += f"- *Scenario*: {example.scenario}\n"
                doc += f"- *Memory*: {example.memory_content}\n"
                doc += f"- *Systems Affected*: {', '.join(example.systems_affected)}\n"
                doc += f"- *Key Behavioral Changes*:\n"
                
                for behavior, value in example.behavioral_outcome.items():
                    doc += f"  - {behavior}: {value}\n"
                
                doc += "\n"
        
        return doc 