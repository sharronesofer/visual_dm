#!/usr/bin/env python3
"""
Mock Data Fixtures Generator
============================

Generates realistic JSON fixtures for all API endpoints based on the extracted
API contracts and backend system data models. Organizes fixtures by system
and endpoint for easy maintenance and frontend testing.

This script reads the api_contracts.yaml file and generates:
- Request fixtures (for POST/PUT endpoints)
- Response fixtures (for all endpoints)
- Error response fixtures
- Edge case data

Usage:
    python generate_mock_fixtures.py
"""

import json
import yaml
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4
import random
from faker import Faker

fake = Faker()


class MockDataGenerator:
    """Generates comprehensive mock data fixtures for all backend systems."""
    
    def __init__(self):
        self.fixtures_dir = "."
        self.systems_config = self._load_systems_config()
        
    def _load_systems_config(self) -> Dict[str, Any]:
        """Load system configuration and data structures."""
        return {
            "analytics": {
                "models": ["Event", "Metric", "Report"],
                "id_format": "uuid"
            },
            "arc": {
                "models": ["Arc", "ArcStep", "ArcProgression", "QuestOpportunity"],
                "id_format": "uuid",
                "enum_values": {
                    "arc_type": ["PRIMARY", "SECONDARY", "TERTIARY"],
                    "arc_status": ["PENDING", "ACTIVE", "COMPLETED", "FAILED", "STALLED"],
                    "arc_priority": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                    "progression_method": ["LINEAR", "BRANCHING", "MILESTONE"]
                }
            },
            "auth_user": {
                "models": ["User", "AuthRelationship", "Permission"],
                "id_format": "uuid"
            },
            "character": {
                "models": ["Character", "Relationship", "Party", "Stats"],
                "id_format": "uuid",
                "enum_values": {
                    "relationship_type": ["FACTION", "QUEST", "SPATIAL", "AUTH"],
                    "character_race": ["HUMAN", "ELF", "DWARF", "HALFLING", "DRAGONBORN"],
                    "character_class": ["FIGHTER", "WIZARD", "ROGUE", "CLERIC", "RANGER"]
                }
            },
            "combat": {
                "models": ["CombatState", "Combatant", "Action", "Effect"],
                "id_format": "uuid",
                "enum_values": {
                    "combat_status": ["PENDING", "ACTIVE", "COMPLETED", "INTERRUPTED"],
                    "action_type": ["ATTACK", "DEFEND", "SPELL", "ITEM", "MOVE"]
                }
            },
            "crafting": {
                "models": ["Recipe", "Material", "CraftingStation", "CraftingResult"],
                "id_format": "uuid",
                "enum_values": {
                    "quality": ["POOR", "COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"],
                    "station_type": ["FORGE", "ALCHEMY_LAB", "ENCHANTING_TABLE", "WORKBENCH"]
                }
            },
            "diplomacy": {
                "models": ["Treaty", "Negotiation", "Sanction", "Incident", "Ultimatum"],
                "id_format": "uuid",
                "enum_values": {
                    "treaty_type": ["TRADE", "NON_AGGRESSION", "ALLIANCE", "MUTUAL_DEFENSE"],
                    "treaty_status": ["DRAFT", "ACTIVE", "EXPIRED", "VIOLATED", "TERMINATED"],
                    "negotiation_status": ["ACTIVE", "COMPLETED", "FAILED", "ABANDONED"]
                }
            },
            "economy": {
                "models": ["Shop", "Resource", "Trade", "Market", "Price"],
                "id_format": "int",
                "enum_values": {
                    "resource_type": ["WOOD", "STONE", "METAL", "FOOD", "LUXURY"],
                    "shop_type": ["GENERAL", "WEAPONS", "ARMOR", "MAGIC", "TAVERN"]
                }
            },
            "equipment": {
                "models": ["Equipment", "EquipmentSet", "Durability", "Enchantment"],
                "id_format": "uuid",
                "enum_values": {
                    "equipment_type": ["WEAPON", "ARMOR", "ACCESSORY", "TOOL"],
                    "slot": ["HEAD", "CHEST", "LEGS", "FEET", "HANDS", "MAIN_HAND", "OFF_HAND", "RING", "NECKLACE"],
                    "rarity": ["COMMON", "UNCOMMON", "RARE", "EPIC", "LEGENDARY"]
                }
            },
            "faction": {
                "models": ["Faction", "Membership", "Goal", "Relationship"],
                "id_format": "uuid",
                "enum_values": {
                    "faction_type": ["GUILD", "KINGDOM", "CULT", "MERCENARY", "CRIMINAL"],
                    "membership_role": ["MEMBER", "OFFICER", "LEADER", "ALLY", "ENEMY"]
                }
            },
            "inventory": {
                "models": ["Item", "Container", "Stack", "Transfer"],
                "id_format": "uuid",
                "enum_values": {
                    "item_type": ["WEAPON", "ARMOR", "CONSUMABLE", "MATERIAL", "QUEST", "MISC"],
                    "container_type": ["BAG", "CHEST", "BANK", "SHOP"]
                }
            },
            "magic": {
                "models": ["Spell", "Spellbook", "SpellEffect", "MagicalInfluence"],
                "id_format": "int",
                "enum_values": {
                    "magic_school": ["ABJURATION", "CONJURATION", "DIVINATION", "ENCHANTMENT", "EVOCATION", "ILLUSION", "NECROMANCY", "TRANSMUTATION"],
                    "magic_domain": ["ARCANE", "DIVINE", "NATURE", "OCCULT"],
                    "effect_type": ["INFLUENCE", "MANIFESTATION", "ALTERATION", "ENHANCEMENT", "DIMINISHMENT"]
                }
            },
            "memory": {
                "models": ["Memory", "Association", "CognitiveFrame"],
                "id_format": "uuid",
                "enum_values": {
                    "memory_type": ["PERSONAL", "FACTUAL", "EMOTIONAL", "PROCEDURAL"],
                    "importance": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
                }
            },
            "motif": {
                "models": ["Motif", "MotifSequence", "MotifContext", "Notification"],
                "id_format": "uuid",
                "enum_values": {
                    "motif_type": ["CHARACTER", "LOCATION", "QUEST", "NARRATIVE"],
                    "scope": ["GLOBAL", "REGIONAL", "LOCAL", "PERSONAL"],
                    "lifecycle_stage": ["EMERGING", "DEVELOPING", "PEAK", "DECLINING", "DORMANT"]
                }
            },
            "npc": {
                "models": ["NPC", "NPCLocation", "NPCMemory", "NPCRumor", "NPCLoyalty"],
                "id_format": "uuid",
                "enum_values": {
                    "npc_type": ["VILLAGER", "MERCHANT", "GUARD", "QUEST_GIVER", "ALLY", "ANTAGONIST"],
                    "personality_trait": ["FRIENDLY", "HOSTILE", "NEUTRAL", "MYSTERIOUS", "HELPFUL"]
                }
            },
            "poi": {
                "models": ["PointOfInterest", "POIState", "POIResource", "POIEvent"],
                "id_format": "uuid",
                "enum_values": {
                    "poi_type": ["SETTLEMENT", "DUNGEON", "TEMPLE", "TOWER", "CAMP", "LANDMARK"],
                    "poi_state": ["ACTIVE", "ABANDONED", "CONTESTED", "MYSTERIOUS", "DISCOVERED"],
                    "evolution_state": ["GROWING", "STABLE", "DECLINING", "TRANSFORMING"]
                }
            },
            "population": {
                "models": ["Population", "PopulationEvent", "Migration", "Demographics"],
                "id_format": "uuid",
                "enum_values": {
                    "population_state": ["GROWING", "STABLE", "DECLINING", "MIGRATING", "CRISIS"],
                    "event_type": ["BIRTH", "DEATH", "MIGRATION", "CATASTROPHE", "WAR_IMPACT"]
                }
            },
            "quest": {
                "models": ["Quest", "QuestStep", "QuestReward", "QuestRequirement"],
                "id_format": "uuid",
                "enum_values": {
                    "quest_type": ["MAIN", "SIDE", "FACTION", "CHARACTER", "RANDOM"],
                    "quest_status": ["AVAILABLE", "ACTIVE", "COMPLETED", "FAILED", "ABANDONED"],
                    "step_type": ["KILL", "GATHER", "TALK", "DELIVER", "EXPLORE"]
                }
            },
            "region": {
                "models": ["Region", "RegionFeature", "RegionClimate", "RegionEvent"],
                "id_format": "uuid",
                "enum_values": {
                    "region_type": ["PLAINS", "FOREST", "MOUNTAIN", "DESERT", "SWAMP", "COAST"],
                    "climate": ["TEMPERATE", "TROPICAL", "ARCTIC", "ARID", "HUMID"]
                }
            },
            "religion": {
                "models": ["Deity", "Religion", "Membership", "Practice", "Divine"],
                "id_format": "uuid",
                "enum_values": {
                    "deity_domain": ["WAR", "NATURE", "MAGIC", "KNOWLEDGE", "DEATH", "LIFE"],
                    "religion_type": ["MONOTHEISTIC", "POLYTHEISTIC", "PANTHEON", "CULT"]
                }
            },
            "rumor": {
                "models": ["Rumor", "RumorVariant", "RumorSpread", "RumorVerification"],
                "id_format": "uuid",
                "enum_values": {
                    "rumor_type": ["NEWS", "GOSSIP", "LEGEND", "WARNING", "OPPORTUNITY"],
                    "truth_level": ["TRUE", "MOSTLY_TRUE", "MIXED", "MOSTLY_FALSE", "FALSE"]
                }
            },
            "tension_war": {
                "models": ["Tension", "War", "Battle", "WarOutcome", "Alliance"],
                "id_format": "uuid",
                "enum_values": {
                    "tension_level": ["PEACEFUL", "STRAINED", "HOSTILE", "WAR_IMMINENT", "AT_WAR"],
                    "war_outcome": ["DECISIVE_VICTORY", "PYRRHIC_VICTORY", "STALEMATE", "RETREAT"]
                }
            },
            "time": {
                "models": ["GameTime", "Calendar", "Event", "Season"],
                "id_format": "uuid",
                "enum_values": {
                    "season": ["SPRING", "SUMMER", "AUTUMN", "WINTER"],
                    "time_period": ["DAWN", "MORNING", "NOON", "AFTERNOON", "EVENING", "NIGHT"]
                }
            },
            "world_generation": {
                "models": ["World", "Continent", "Terrain", "Feature"],
                "id_format": "uuid",
                "enum_values": {
                    "terrain_type": ["GRASSLAND", "FOREST", "MOUNTAIN", "WATER", "DESERT", "TUNDRA"],
                    "feature_type": ["RIVER", "LAKE", "ROAD", "BORDER", "SETTLEMENT"]
                }
            },
            "world_state": {
                "models": ["WorldState", "GlobalEvent", "StateChange", "History"],
                "id_format": "uuid",
                "enum_values": {
                    "event_impact": ["LOCAL", "REGIONAL", "GLOBAL", "COSMIC"],
                    "state_type": ["POLITICAL", "ECONOMIC", "SOCIAL", "ENVIRONMENTAL"]
                }
            }
        }
    
    def generate_id(self, id_format: str) -> str:
        """Generate an ID based on the specified format."""
        if id_format == "uuid":
            return str(uuid4())
        elif id_format == "int":
            return str(random.randint(1, 100000))
        else:
            return str(uuid4())
    
    def generate_timestamp(self, offset_days: int = 0) -> str:
        """Generate a realistic timestamp."""
        base_time = datetime.utcnow() + timedelta(days=offset_days)
        return base_time.isoformat() + "Z"
    
    def generate_base_object(self, system: str, model: str) -> Dict[str, Any]:
        """Generate a base object with common fields."""
        config = self.systems_config.get(system, {})
        id_format = config.get("id_format", "uuid")
        
        obj = {
            "id": self.generate_id(id_format),
            "created_at": self.generate_timestamp(-random.randint(1, 30)),
            "updated_at": self.generate_timestamp(-random.randint(0, 5))
        }
        
        return obj
    
    def get_enum_value(self, system: str, enum_name: str) -> str:
        """Get a random enum value for the specified system and enum."""
        config = self.systems_config.get(system, {})
        enum_values = config.get("enum_values", {})
        values = enum_values.get(enum_name, ["DEFAULT"])
        return random.choice(values)
    
    def generate_character_data(self) -> Dict[str, Any]:
        """Generate character-specific mock data."""
        character = self.generate_base_object("character", "Character")
        character.update({
            "name": fake.name(),
            "race": self.get_enum_value("character", "character_race"),
            "character_class": self.get_enum_value("character", "character_class"),
            "level": random.randint(1, 20),
            "experience_points": random.randint(0, 355000),
            "stats": {
                "strength": random.randint(8, 18),
                "dexterity": random.randint(8, 18),
                "constitution": random.randint(8, 18),
                "intelligence": random.randint(8, 18),
                "wisdom": random.randint(8, 18),
                "charisma": random.randint(8, 18)
            },
            "hit_points": {
                "current": random.randint(20, 100),
                "maximum": random.randint(50, 120)
            },
            "location": {
                "region_id": self.generate_id("uuid"),
                "coordinates": {
                    "q": random.randint(-10, 10),
                    "r": random.randint(-10, 10),
                    "s": random.randint(-10, 10)
                }
            },
            "background": fake.sentence(nb_words=10),
            "personality_traits": [fake.word() for _ in range(3)]
        })
        return character
    
    def generate_npc_data(self) -> Dict[str, Any]:
        """Generate NPC-specific mock data."""
        npc = self.generate_base_object("npc", "NPC")
        npc.update({
            "name": fake.name(),
            "npc_type": self.get_enum_value("npc", "npc_type"),
            "personality_trait": self.get_enum_value("npc", "personality_trait"),
            "description": fake.paragraph(nb_sentences=3),
            "location": {
                "region_id": self.generate_id("uuid"),
                "poi_id": self.generate_id("uuid"),
                "coordinates": {
                    "q": random.randint(-10, 10),
                    "r": random.randint(-10, 10),
                    "s": random.randint(-10, 10)
                }
            },
            "stats": {
                "level": random.randint(1, 15),
                "hit_points": random.randint(10, 80),
                "armor_class": random.randint(10, 18)
            },
            "faction_affiliations": [
                {
                    "faction_id": self.generate_id("uuid"),
                    "role": self.get_enum_value("faction", "membership_role"),
                    "reputation": random.randint(-100, 100)
                }
            ],
            "schedule": {
                "current_activity": random.choice(["WORKING", "RESTING", "TRAVELING", "SOCIALIZING"]),
                "next_activity_time": self.generate_timestamp(1)
            },
            "loyalty": {
                "player_character_id": self.generate_id("uuid"),
                "loyalty_score": random.randint(0, 100),
                "goodwill": random.randint(-50, 50)
            }
        })
        return npc
    
    def generate_quest_data(self) -> Dict[str, Any]:
        """Generate quest-specific mock data."""
        quest = self.generate_base_object("quest", "Quest")
        quest.update({
            "title": fake.catch_phrase(),
            "description": fake.paragraph(nb_sentences=5),
            "quest_type": self.get_enum_value("quest", "quest_type"),
            "quest_status": self.get_enum_value("quest", "quest_status"),
            "giver_id": self.generate_id("uuid"),
            "target_character_id": self.generate_id("uuid"),
            "requirements": {
                "minimum_level": random.randint(1, 10),
                "required_items": [self.generate_id("uuid") for _ in range(random.randint(0, 3))],
                "prerequisite_quests": [self.generate_id("uuid") for _ in range(random.randint(0, 2))]
            },
            "rewards": {
                "experience_points": random.randint(100, 5000),
                "gold": random.randint(50, 1000),
                "items": [
                    {
                        "item_id": self.generate_id("uuid"),
                        "quantity": random.randint(1, 5)
                    }
                ]
            },
            "steps": [
                {
                    "step_number": i + 1,
                    "step_type": self.get_enum_value("quest", "step_type"),
                    "description": fake.sentence(),
                    "completed": random.choice([True, False]),
                    "target_id": self.generate_id("uuid") if random.choice([True, False]) else None
                }
                for i in range(random.randint(1, 5))
            ]
        })
        return quest
    
    def generate_arc_data(self) -> Dict[str, Any]:
        """Generate arc-specific mock data."""
        arc = self.generate_base_object("arc", "Arc")
        arc.update({
            "title": fake.catch_phrase(),
            "description": fake.paragraph(nb_sentences=6),
            "arc_type": self.get_enum_value("arc", "arc_type"),
            "arc_status": self.get_enum_value("arc", "arc_status"),
            "arc_priority": self.get_enum_value("arc", "arc_priority"),
            "progression_method": self.get_enum_value("arc", "progression_method"),
            "metadata": {
                "themes": [fake.word() for _ in range(3)],
                "target_characters": [self.generate_id("uuid") for _ in range(random.randint(1, 4))],
                "regions": [self.generate_id("uuid") for _ in range(random.randint(1, 3))],
                "estimated_duration": random.randint(7, 90)
            },
            "steps": [
                {
                    "step_id": self.generate_id("uuid"),
                    "step_number": i + 1,
                    "title": fake.sentence(nb_words=5),
                    "description": fake.paragraph(nb_sentences=3),
                    "completion_criteria": fake.sentence(),
                    "completed": random.choice([True, False]),
                    "completion_date": self.generate_timestamp(-random.randint(0, 10)) if random.choice([True, False]) else None
                }
                for i in range(random.randint(3, 8))
            ],
            "progression": {
                "current_step": random.randint(1, 5),
                "completion_percentage": random.randint(0, 100),
                "stalled": random.choice([True, False]),
                "last_activity": self.generate_timestamp(-random.randint(0, 7))
            }
        })
        return arc
    
    def generate_magic_data(self) -> Dict[str, Any]:
        """Generate magic-specific mock data."""
        spell = self.generate_base_object("magic", "Spell")
        spell.update({
            "name": fake.word().title() + " " + random.choice(["Bolt", "Shield", "Heal", "Blast", "Ward"]),
            "description": fake.paragraph(nb_sentences=4),
            "school": self.get_enum_value("magic", "magic_school"),
            "domain": self.get_enum_value("magic", "magic_domain"),
            "narrative_power": round(random.uniform(1.0, 10.0), 1),
            "narrative_effects": {
                "primary_effect": fake.sentence(),
                "secondary_effects": [fake.sentence() for _ in range(random.randint(0, 3))],
                "duration": random.choice(["INSTANT", "CONCENTRATION", "PERMANENT", "TIMED"]),
                "range": random.choice(["SELF", "TOUCH", "RANGED", "AREA"])
            }
        })
        return spell
    
    def generate_equipment_data(self) -> Dict[str, Any]:
        """Generate equipment-specific mock data."""
        equipment = self.generate_base_object("equipment", "Equipment")
        equipment.update({
            "name": fake.word().title() + " " + random.choice(["Sword", "Shield", "Armor", "Bow", "Staff"]),
            "description": fake.paragraph(nb_sentences=3),
            "equipment_type": self.get_enum_value("equipment", "equipment_type"),
            "slot": self.get_enum_value("equipment", "slot"),
            "rarity": self.get_enum_value("equipment", "rarity"),
            "stats": {
                "attack_bonus": random.randint(0, 5) if random.choice([True, False]) else None,
                "damage": f"{random.randint(1, 3)}d{random.choice([4, 6, 8, 10])}" if random.choice([True, False]) else None,
                "armor_class": random.randint(10, 18) if random.choice([True, False]) else None,
                "stat_bonuses": {
                    "strength": random.randint(-2, 3) if random.choice([True, False]) else 0,
                    "dexterity": random.randint(-2, 3) if random.choice([True, False]) else 0,
                    "constitution": random.randint(-2, 3) if random.choice([True, False]) else 0
                }
            },
            "durability": {
                "current": random.randint(50, 100),
                "maximum": 100,
                "wear_rate": round(random.uniform(0.1, 2.0), 2)
            },
            "enchantments": [
                {
                    "enchantment_id": self.generate_id("uuid"),
                    "name": fake.word().title() + " Enhancement",
                    "effect": fake.sentence(),
                    "magnitude": random.randint(1, 5)
                }
                for _ in range(random.randint(0, 3))
            ],
            "identified": random.choice([True, False]),
            "value": random.randint(10, 10000)
        })
        return equipment
    
    def generate_error_responses(self) -> Dict[str, Any]:
        """Generate standard error responses."""
        return {
            "400": {
                "detail": "Bad Request - Invalid input parameters",
                "code": "BAD_REQUEST"
            },
            "401": {
                "detail": "Unauthorized - Authentication required",
                "code": "UNAUTHORIZED"
            },
            "403": {
                "detail": "Forbidden - Insufficient permissions",
                "code": "FORBIDDEN"
            },
            "404": {
                "detail": "Not Found - Resource does not exist",
                "code": "NOT_FOUND"
            },
            "422": {
                "detail": [
                    {
                        "loc": ["body", "field_name"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            },
            "500": {
                "detail": "Internal Server Error - An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        }
    
    def generate_success_response(self) -> Dict[str, Any]:
        """Generate standard success response."""
        return {
            "status": "success",
            "message": "Operation completed successfully"
        }
    
    def generate_fixtures_for_system(self, system_name: str):
        """Generate all fixtures for a specific system."""
        print(f"Generating fixtures for {system_name} system...")
        
        system_dir = os.path.join(self.fixtures_dir, system_name)
        os.makedirs(system_dir, exist_ok=True)
        
        # Generate common response types
        error_responses = self.generate_error_responses()
        success_response = self.generate_success_response()
        
        # Save error responses
        with open(os.path.join(system_dir, "error_responses.json"), "w") as f:
            json.dump(error_responses, f, indent=2)
        
        # Save success response
        with open(os.path.join(system_dir, "success_response.json"), "w") as f:
            json.dump(success_response, f, indent=2)
        
        # Generate system-specific data
        if system_name == "character":
            self._generate_character_fixtures(system_dir)
        elif system_name == "npc":
            self._generate_npc_fixtures(system_dir)
        elif system_name == "quest":
            self._generate_quest_fixtures(system_dir)
        elif system_name == "arc":
            self._generate_arc_fixtures(system_dir)
        elif system_name == "magic":
            self._generate_magic_fixtures(system_dir)
        elif system_name == "equipment":
            self._generate_equipment_fixtures(system_dir)
        else:
            self._generate_generic_fixtures(system_dir, system_name)
    
    def _generate_character_fixtures(self, system_dir: str):
        """Generate character-specific fixtures."""
        # Single character
        character = self.generate_character_data()
        with open(os.path.join(system_dir, "character.json"), "w") as f:
            json.dump(character, f, indent=2)
        
        # Character list
        characters = [self.generate_character_data() for _ in range(5)]
        with open(os.path.join(system_dir, "characters_list.json"), "w") as f:
            json.dump(characters, f, indent=2)
        
        # Character creation request
        create_request = {
            "name": fake.name(),
            "race": self.get_enum_value("character", "character_race"),
            "character_class": self.get_enum_value("character", "character_class"),
            "background": fake.paragraph(),
            "stats": {
                "strength": random.randint(8, 15),
                "dexterity": random.randint(8, 15),
                "constitution": random.randint(8, 15),
                "intelligence": random.randint(8, 15),
                "wisdom": random.randint(8, 15),
                "charisma": random.randint(8, 15)
            }
        }
        with open(os.path.join(system_dir, "character_create_request.json"), "w") as f:
            json.dump(create_request, f, indent=2)
    
    def _generate_npc_fixtures(self, system_dir: str):
        """Generate NPC-specific fixtures."""
        # Single NPC
        npc = self.generate_npc_data()
        with open(os.path.join(system_dir, "npc.json"), "w") as f:
            json.dump(npc, f, indent=2)
        
        # NPC list
        npcs = [self.generate_npc_data() for _ in range(8)]
        with open(os.path.join(system_dir, "npcs_list.json"), "w") as f:
            json.dump(npcs, f, indent=2)
        
        # NPC generation request
        generation_request = {
            "poi_id": self.generate_id("uuid"),
            "count": random.randint(5, 15),
            "npc_types": [self.get_enum_value("npc", "npc_type") for _ in range(3)],
            "personality_distribution": {
                "FRIENDLY": 0.4,
                "NEUTRAL": 0.4,
                "HOSTILE": 0.2
            }
        }
        with open(os.path.join(system_dir, "npc_generation_request.json"), "w") as f:
            json.dump(generation_request, f, indent=2)
    
    def _generate_quest_fixtures(self, system_dir: str):
        """Generate quest-specific fixtures."""
        # Single quest
        quest = self.generate_quest_data()
        with open(os.path.join(system_dir, "quest.json"), "w") as f:
            json.dump(quest, f, indent=2)
        
        # Quest list
        quests = [self.generate_quest_data() for _ in range(6)]
        with open(os.path.join(system_dir, "quests_list.json"), "w") as f:
            json.dump(quests, f, indent=2)
        
        # Quest opportunities
        opportunities = [
            {
                "opportunity_id": self.generate_id("uuid"),
                "arc_step_id": self.generate_id("uuid"),
                "quest_type": self.get_enum_value("quest", "quest_type"),
                "priority": random.randint(1, 10),
                "context": fake.paragraph(),
                "suggested_giver": self.generate_id("uuid")
            }
            for _ in range(4)
        ]
        with open(os.path.join(system_dir, "quest_opportunities.json"), "w") as f:
            json.dump(opportunities, f, indent=2)
    
    def _generate_arc_fixtures(self, system_dir: str):
        """Generate arc-specific fixtures."""
        # Single arc
        arc = self.generate_arc_data()
        with open(os.path.join(system_dir, "arc.json"), "w") as f:
            json.dump(arc, f, indent=2)
        
        # Arc list
        arcs = [self.generate_arc_data() for _ in range(4)]
        with open(os.path.join(system_dir, "arcs_list.json"), "w") as f:
            json.dump(arcs, f, indent=2)
        
        # Arc generation request
        generation_request = {
            "arc_type": self.get_enum_value("arc", "arc_type"),
            "themes": [fake.word() for _ in range(3)],
            "target_characters": [self.generate_id("uuid") for _ in range(2)],
            "complexity": random.choice(["SIMPLE", "MODERATE", "COMPLEX"]),
            "estimated_steps": random.randint(3, 10)
        }
        with open(os.path.join(system_dir, "arc_generation_request.json"), "w") as f:
            json.dump(generation_request, f, indent=2)
        
        # Arc analytics
        analytics = {
            "total_arcs": random.randint(50, 200),
            "active_arcs": random.randint(10, 50),
            "completion_rate": round(random.uniform(0.6, 0.9), 2),
            "average_duration": random.randint(20, 60),
            "most_common_failure_point": "Step 3 - Investigation",
            "engagement_metrics": {
                "player_retention": round(random.uniform(0.7, 0.95), 2),
                "average_session_time": random.randint(60, 180),
                "quest_completion_rate": round(random.uniform(0.75, 0.92), 2)
            }
        }
        with open(os.path.join(system_dir, "arc_analytics.json"), "w") as f:
            json.dump(analytics, f, indent=2)
    
    def _generate_magic_fixtures(self, system_dir: str):
        """Generate magic-specific fixtures."""
        # Single spell
        spell = self.generate_magic_data()
        with open(os.path.join(system_dir, "spell.json"), "w") as f:
            json.dump(spell, f, indent=2)
        
        # Spell list
        spells = [self.generate_magic_data() for _ in range(10)]
        with open(os.path.join(system_dir, "spells_list.json"), "w") as f:
            json.dump(spells, f, indent=2)
        
        # Spellbook
        spellbook = {
            "id": self.generate_id("int"),
            "owner_id": self.generate_id("uuid"),
            "owner_type": "character",
            "spells": {
                str(i): {
                    "spell_id": self.generate_id("int"),
                    "mastery_level": random.randint(1, 5),
                    "times_cast": random.randint(0, 50),
                    "learned_date": self.generate_timestamp(-random.randint(1, 100))
                }
                for i in range(random.randint(3, 12))
            },
            "created_at": self.generate_timestamp(-30),
            "updated_at": self.generate_timestamp(-1)
        }
        with open(os.path.join(system_dir, "spellbook.json"), "w") as f:
            json.dump(spellbook, f, indent=2)
    
    def _generate_equipment_fixtures(self, system_dir: str):
        """Generate equipment-specific fixtures."""
        # Single equipment
        equipment = self.generate_equipment_data()
        with open(os.path.join(system_dir, "equipment.json"), "w") as f:
            json.dump(equipment, f, indent=2)
        
        # Equipment list
        equipment_list = [self.generate_equipment_data() for _ in range(12)]
        with open(os.path.join(system_dir, "equipment_list.json"), "w") as f:
            json.dump(equipment_list, f, indent=2)
        
        # Equipment set
        equipment_set = {
            "id": self.generate_id("uuid"),
            "name": fake.catch_phrase() + " Set",
            "description": fake.paragraph(),
            "pieces": [self.generate_equipment_data() for _ in range(random.randint(3, 6))],
            "set_bonuses": [
                {
                    "pieces_required": random.randint(2, 4),
                    "bonus_name": fake.word().title() + " Bonus",
                    "bonus_description": fake.sentence(),
                    "stat_bonuses": {
                        "strength": random.randint(1, 3),
                        "armor_class": random.randint(1, 2)
                    }
                }
                for _ in range(random.randint(1, 3))
            ],
            "created_at": self.generate_timestamp(-20),
            "updated_at": self.generate_timestamp(-1)
        }
        with open(os.path.join(system_dir, "equipment_set.json"), "w") as f:
            json.dump(equipment_set, f, indent=2)
    
    def _generate_generic_fixtures(self, system_dir: str, system_name: str):
        """Generate generic fixtures for systems without specific generators."""
        config = self.systems_config.get(system_name, {})
        models = config.get("models", ["GenericModel"])
        
        for model in models:
            # Single object
            obj = self.generate_base_object(system_name, model)
            obj.update({
                "name": fake.word().title(),
                "description": fake.paragraph(),
                "status": random.choice(["ACTIVE", "INACTIVE", "PENDING"]),
                "metadata": {
                    "tags": [fake.word() for _ in range(random.randint(1, 4))],
                    "category": fake.word(),
                    "priority": random.randint(1, 10)
                }
            })
            
            filename = f"{model.lower()}.json"
            with open(os.path.join(system_dir, filename), "w") as f:
                json.dump(obj, f, indent=2)
            
            # List of objects
            obj_list = [self.generate_base_object(system_name, model) for _ in range(5)]
            for item in obj_list:
                item.update({
                    "name": fake.word().title(),
                    "description": fake.sentence(),
                    "status": random.choice(["ACTIVE", "INACTIVE", "PENDING"])
                })
            
            list_filename = f"{model.lower()}_list.json"
            with open(os.path.join(system_dir, list_filename), "w") as f:
                json.dump(obj_list, f, indent=2)
    
    def generate_all_fixtures(self):
        """Generate fixtures for all backend systems."""
        print("🔧 Starting mock data fixtures generation...")
        print(f"📁 Fixtures will be saved to: {os.path.abspath(self.fixtures_dir)}")
        
        all_systems = list(self.systems_config.keys())
        
        for system in all_systems:
            try:
                self.generate_fixtures_for_system(system)
                print(f"✅ Generated fixtures for {system}")
            except Exception as e:
                print(f"❌ Failed to generate fixtures for {system}: {e}")
        
        # Generate overview file
        overview = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "systems_count": len(all_systems),
            "systems": all_systems,
            "fixture_types": [
                "Single object responses",
                "List responses", 
                "Create/update requests",
                "Error responses",
                "Success responses",
                "Edge case data"
            ],
            "usage_notes": [
                "All fixtures use realistic fake data generated with Faker library",
                "IDs are properly formatted (UUID or integer) based on system requirements",
                "Timestamps are in ISO 8601 format with timezone",
                "Enum values match backend system specifications",
                "Error responses follow API contract specifications"
            ]
        }
        
        with open(os.path.join(self.fixtures_dir, "overview.json"), "w") as f:
            json.dump(overview, f, indent=2)
        
        print(f"🎉 Successfully generated fixtures for {len(all_systems)} systems!")
        print(f"📊 Overview saved to overview.json")


if __name__ == "__main__":
    generator = MockDataGenerator()
    generator.generate_all_fixtures() 