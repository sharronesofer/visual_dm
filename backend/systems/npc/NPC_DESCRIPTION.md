# NPC System - Plain English Description

## Overview
The NPC (Non-Player Character) system manages all computer-controlled characters in the game world. It handles their creation, behavior, relationships with players, trading interactions, movement patterns, and emotional responses. Think of it as the "brain" that makes NPCs feel alive and responsive to player actions.

---

## Logical Subsystems

### 1. Core NPC Management (Services Layer)
**Purpose:** The main engine that handles all basic NPC operations - creating, updating, finding, and removing NPCs from the game world.

**Key Components:**
- **NPCService** (`services/npc_service.py`): The master controller that coordinates all NPC operations
- **Base Service** (`services/services.py`): A simplified service layer following standard patterns

### 2. Economic & Trading System
**Purpose:** Manages how NPCs buy, sell, and value items, including sophisticated pricing that considers relationships, NPC personality, and market conditions.

**Key Components:**
- **NPCBarterService** (`services/npc_barter_service.py`): Handles trade negotiations and item exchanges
- **BarterEconomicsService** (`services/barter_economics_service.py`): Calculates smart pricing based on NPC type, relationships, and economic factors

### 3. NPC Construction & Properties
**Purpose:** Creates NPCs with realistic attributes, personalities, and background stories.

**Key Components:**
- **NPCBuilder** (`utils/npc_builder_class.py`): Procedurally generates NPCs with races, skills, and personality traits
- **LoyaltyManager** (`utils/npc_loyalty_class.py`): Manages emotional bonds and trust between NPCs and players

### 4. Location & Movement System
**Purpose:** Controls where NPCs go and why they travel around the world.

**Key Components:**
- **NpcLocationService** (`services/npc_location_service.py`): Manages NPC movement and location tracking
- **Travel Utilities** (`utils/npc_travel_utils.py`): Handles wandering behavior and migration during conflicts

### 5. AI Knowledge Integration
**Purpose:** Connects NPCs to an AI knowledge system that makes them smarter and more contextually aware.

**Key Components:**
- **NPCRAGService** (`rag_adapter.py`): Integrates with AI systems to enhance NPC personalities, backstories, and dialogue

### 6. System Integration Layer
**Purpose:** Connects the NPC system to other game systems and provides backward compatibility.

**Key Components:**
- **Main Module** (`__init__.py`): Exports all NPC functionality and maintains compatibility with older code

---

## Business Logic Breakdown

### Core NPC Management (`services/npc_service.py`)
**What it does:** This is the central command center for all NPC operations. When the game needs to create a new shopkeeper, update a guard's patrol route, or remove an NPC from the world, this service handles it.

**Key Functions:**
- **create_npc()**: Brings a new NPC into existence with all their starting properties
- **get_npc()**: Finds and retrieves information about a specific NPC
- **update_npc()**: Changes NPC properties like their status, description, or abilities
- **delete_npc()**: Removes an NPC from active play (usually by marking them as inactive rather than permanently deleting)
- **list_npcs()**: Gets lists of NPCs with filtering options (show only guards, or NPCs in a specific region)
- **Memory Management**: Stores and retrieves what NPCs remember about past events
- **Faction Relationships**: Tracks which groups or organizations NPCs belong to
- **Rumor System**: Manages gossip and information NPCs share with players
- **Location Tracking**: Updates where NPCs are and logs their movement history

**Real-world Rules:** NPCs must have unique names, can belong to multiple factions, remember interactions with players, and can have their loyalty tracked over time.

### Trading & Economics (`services/npc_barter_service.py` & `services/barter_economics_service.py`)
**What it does:** This determines how NPCs behave during trading - what they're willing to sell, how much they charge, and whether they trust the player enough to make valuable trades.

**Key Business Rules:**
- **Item Availability Tiers**: 
  - **Never Available**: Essential work tools (a blacksmith won't sell their hammer), equipped gear, quest-critical items
  - **High Trust Required**: Valuable items, family heirlooms, backup weapons - only sold to trusted friends
  - **Always Available**: Common trade goods that anyone can buy
- **Dynamic Pricing**: Prices change based on:
  - **NPC Type**: Merchants charge differently than peasants or nobles
  - **Relationship Trust**: Friends get discounts up to 20%
  - **Item Category**: Luxury items cost more for commoners, necessities cost more for peasants
  - **Economic Context**: Regional conflicts, supply shortages, or prosperity levels affect prices
  - **Faction Relationships**: Allied factions get better deals

**Smart Economics Features:**
- **NPC Type Classification**: Automatically determines if someone is a peasant, merchant, noble, etc. based on their profession and wealth
- **Market Context**: Considers regional prosperity, conflicts, and seasonal effects
- **Relationship Integration**: Connects with the loyalty system to offer relationship-based pricing

### NPC Creation (`utils/npc_builder_class.py`)
**What it does:** Like a character creator that procedurally generates NPCs with realistic attributes, skills, and personalities.

**Key Functions:**
- **Race Assignment**: Applies racial bonuses to attributes (elves are more dexterous, dwarves are stronger)
- **Skill & Tag Assignment**: Gives NPCs relevant abilities and personality markers
- **Hidden Personality Generation**: Creates six hidden traits that influence NPC behavior:
  - Ambition, Integrity, Discipline, Impulsivity, Pragmatism, Resilience
- **Loyalty Initialization**: Sets up starting relationship potential with player characters
- **Motif System**: Assigns narrative themes that influence NPC behavior over time
- **Location Assignment**: Places NPCs in specific regions and locations

**Real-world Rules:** NPCs need coherent combinations of race, skills, and location. A blacksmith should have appropriate tools and be located where smithing makes sense.

### Loyalty & Relationships (`utils/npc_loyalty_class.py`)
**What it does:** Manages the emotional bonds between NPCs and players, simulating how trust builds or deteriorates over time.

**Core Mechanics:**
- **Loyalty Score**: Ranges from -10 (will betray/abandon) to +10 (completely loyal)
- **Goodwill Buffer**: 0-36 points that act as emotional momentum before loyalty changes
- **Special Relationship Tags**:
  - **Loyalist**: Gains loyalty easier, loses it harder
  - **Coward**: Loses loyalty faster when threatened
  - **Bestie**: Always loyal (score locked at 10)
  - **Nemesis**: Always disloyal (score locked at -10)

**Time-Based Changes:**
- High loyalty NPCs slowly regenerate goodwill over time
- Low loyalty NPCs gradually lose goodwill until they may abandon the party
- Dramatic events can directly impact loyalty or goodwill

### Movement & Travel (`utils/npc_travel_utils.py` & `services/npc_location_service.py`)
**What it does:** Controls how NPCs move around the world based on their personality and external circumstances.

**Movement Rules:**
- **Wanderlust System**: NPCs have different travel tendencies (0 = never moves, higher values = more likely to travel)
- **Home POI Concept**: Every NPC has a "home base" they return to
- **Travel Radius**: NPCs can only move within a certain distance from their home
- **War Pressure**: NPCs flee conflict zones and may permanently relocate if their home becomes dangerous
- **Faction Migration**: NPCs may move to areas controlled by friendly factions during conflicts

### AI Knowledge Integration (`rag_adapter.py`)
**What it does:** Connects NPCs to an AI knowledge system that makes them smarter about the game world and more realistic in their responses.

**Key Functions:**
- **Personality Enhancement**: Uses AI to add depth to NPC personalities based on their type and location
- **Backstory Generation**: Creates rich character histories that fit the game world
- **Dialogue Knowledge**: Helps NPCs give contextually appropriate responses about various topics
- **Behavior Learning**: Records and learns from NPC actions to improve future behavior
- **Cross-System Knowledge**: NPCs can access information from faction, quest, and lore systems

---

## Integration with Broader Codebase

### Upstream Dependencies (What the NPC System Needs)
- **Infrastructure Layer**: Uses database models, repositories, and event systems from `backend.infrastructure.systems.npc`
- **Character System**: Integrates with character relationships for loyalty and trust calculations
- **Economy System**: Uses economy manager for market context and regional economic data
- **Diplomacy System**: Accesses faction relationships to influence NPC behavior toward different factions
- **Core RAG Client**: Connects to centralized AI knowledge system for enhanced NPC intelligence

### Downstream Effects (What Uses the NPC System)
- **Quest System**: NPCs serve as quest givers, objectives, and story elements
- **Combat System**: NPCs participate in battles and conflicts
- **Dialogue System**: Uses NPC personality, knowledge, and relationships to generate appropriate responses
- **Regional Management**: NPCs populate regions and contribute to regional dynamics
- **Event System**: NPC actions and state changes trigger events that other systems can react to

### Breaking Changes Impact
If the NPC system changes significantly:
- **Quest System**: Quests involving specific NPCs would need updates
- **Dialogue System**: Would need to adapt to new personality or knowledge structures
- **Combat System**: NPC combatants might need different handling
- **Regional Systems**: Population management and regional dynamics could be affected
- **Save/Load Systems**: Player save files containing NPC relationship data might need migration

---

## Maintenance Concerns

### TODO Items & Technical Debt
1. **Database Migration**: Three critical files still reference Firebase instead of the current database system:
   - `utils/npc_travel_utils.py` - Line 0
   - `utils/npc_builder_class.py` - Line 8  
   - `utils/npc_loyalty_class.py` - Line 5

### Stub & Placeholder Code
1. **Location Service Limitations** (`services/npc_location_service.py`):
   - Lines 34, 98: Explicitly marked as stub implementations
   - Missing actual database integration for NPC location queries
   - POI (Point of Interest) generation is hardcoded rather than database-driven

2. **Economic Context Placeholders** (`services/barter_economics_service.py`):
   - Lines 307, 333, 386: Placeholder logic for faction relationships and regional conflicts
   - Real economic data integration not fully implemented

### Error Handling & Robustness Issues
1. **Variable Name Errors** (`services/services.py`):
   - Lines 90, 102, 118, 127, 137: References to undefined variable `_npc_id` instead of `npc_id`
   - Could cause runtime crashes

2. **Extensive Error Logging**: While comprehensive error logging is good, the volume suggests the system may encounter frequent issues that need investigation

### Code Quality Concerns
1. **Legacy Compatibility Layer**: The main `__init__.py` file maintains extensive backward compatibility imports, suggesting the system is mid-refactoring
2. **Deprecated Methods**: `NPCBarterService.calculate_barter_price()` is marked as deprecated in favor of the new smart economics system
3. **Hardcoded Business Logic**: Many economic rules and NPC behaviors are embedded in code rather than configurable

---

## Modular Cleanup Opportunities

### Move to JSON Configuration Files

#### 1. NPC Type Behavior Profiles (`npc-types.json`)
**Current Location**: Hardcoded in `barter_economics_service.py` lines 200-250
**Suggested Structure**:
```json
{
  "peasant": {
    "item_preferences": {
      "basic_necessity": {"multiplier": 1.5, "reason": "Desperate for essentials"},
      "luxury": {"multiplier": 0.6, "reason": "Cannot afford luxuries"}
    },
    "base_trust_threshold": 0.3,
    "haggling_tendency": 0.8
  }
}
```
**Benefits**: Game designers could easily tweak how different NPC types behave in trading without touching code. New NPC types could be added without programming.

#### 2. Economic Regional Settings (`economic-regions.json`)
**Current Location**: Scattered throughout `barter_economics_service.py`
**Suggested Structure**:
```json
{
  "regions": {
    "iron_hills": {
      "prosperity_level": 1.2,
      "conflict_status": false,
      "supply_demand": {
        "military": 1.3,
        "luxury": 0.7
      }
    }
  }
}
```
**Benefits**: Economic balancing could be done by content creators. Seasonal events could modify regional economics without code changes.

#### 3. Item Availability Rules (`item-trading-rules.json`)
**Current Location**: Hardcoded in `npc_barter_service.py` lines 60-110
**Suggested Structure**:
```json
{
  "profession_essential_items": {
    "blacksmith": ["hammer", "anvil", "forge", "tongs"],
    "guard": ["sword", "shield", "armor", "uniform"]
  },
  "availability_tiers": {
    "never_available": ["equipped", "quest_critical", "soulbound"],
    "high_trust_required": ["backup_weapon", "family_heirloom", "high_value"]
  }
}
```
**Benefits**: Game masters could customize what items NPCs are willing to trade. New professions could be added with their essential items without programming.

#### 4. Loyalty System Configuration (`loyalty-rules.json`)
**Current Location**: Hardcoded in `npc_loyalty_class.py`
**Suggested Structure**:
```json
{
  "loyalty_ranges": {
    "min_score": -10,
    "max_score": 10,
    "goodwill_max": 36,
    "abandonment_threshold": -5
  },
  "relationship_tags": {
    "loyalist": {"gain_modifier": 1.5, "loss_modifier": 0.5},
    "coward": {"gain_modifier": 0.5, "loss_modifier": 1.5}
  }
}
```
**Benefits**: Loyalty mechanics could be fine-tuned for different game campaigns. Custom relationship types could be added for specific story needs.

#### 5. NPC Movement Patterns (`travel-behaviors.json`)
**Current Location**: Hardcoded in `npc_travel_utils.py`
**Suggested Structure**:
```json
{
  "wanderlust_behaviors": {
    "0": {"travel_chance": 0, "max_distance": 0},
    "1-2": {"travel_chance": 0.2, "max_distance": 1},
    "3-4": {"travel_chance": 0.4, "max_distance": 2, "relocation_chance": 0.1}
  },
  "war_responses": {
    "loyalty_decay_rate": {"min": 1, "max": 2},
    "migration_threshold": 2
  }
}
```
**Benefits**: Different campaign settings could have different travel patterns. Special events could temporarily modify NPC movement without coding.

### Why These Changes Would Help

1. **Faster Iteration**: Game designers could tweak NPC behavior and test changes immediately without waiting for code deployment
2. **Campaign Customization**: Different game campaigns could have completely different NPC behavior profiles
3. **A/B Testing**: Multiple configuration sets could be tested to find the most engaging NPC interactions
4. **Modding Support**: Community members could create custom NPC behavior packages
5. **Debugging**: Configuration issues would be easier to spot and fix than code bugs
6. **Documentation**: JSON files serve as living documentation of game mechanics

The NPC system is quite sophisticated but would benefit significantly from extracting its hardcoded business rules into configurable data files. This would make it much more maintainable and allow non-programmers to participate in game balancing and content creation. 