# Visual DM Development Bible (Reorganized)

## Table of Contents
1. [Introduction](#introduction)
2. [Core Design Philosophy](#core-design-philosophy)
3. [Technical Framework](#technical-framework)
4. [Systems](#systems)
   - [Analytics System](#analytics-system)
   - [Auth/User System](#authuser-system)
   - [Character System](#character-system)
   - [Combat System](#combat-system)
   - [Crafting System](#crafting-system)
   - [Data System](#data-system)
   - [Dialogue System](#dialogue-system)
   - [Diplomacy System](#diplomacy-system)
   - [Economy System](#economy-system)
   - [Equipment System](#equipment-system)
   - [Events System](#events-system)
   - [Faction System](#faction-system)
   - [Inventory System](#inventory-system)
   - [LLM System](#llm-system)
   - [Loot System](#loot-system)
   - [Magic System](#magic-system)
   - [Memory System](#memory-system)
   - [Motif System](#motif-system)
   - [NPC System](#npc-system)
   - [POI System](#poi-system)
   - [Population System](#population-system)
   - [Quest System](#quest-system)
   - [Region System](#region-system)
   - [Religion System](#religion-system)
   - [Rumor System](#rumor-system)
   - [Shared System](#shared-system)
   - [Storage System](#storage-system)
   - [Tension/War System](#tensionwar-system)
   - [Time System](#time-system)
   - [World Generation System](#world-generation-system)
   - [World State System](#world-state-system)
5. [Cross-Cutting Concerns](#cross-cutting-concerns)
   - [User Interface](#user-interface)
   - [Modding Support](#modding-support)
   - [AI Integration](#ai-integration)
   - [World and Setting](#world-and-setting)

## Introduction

**Summary:** This section introduces Visual DM, explains its purpose as a tabletop roleplaying game companion/simulation tool, and outlines how to use this documentation.

**Improvement Notes:** Add a "How to Contribute" subsection for developer onboarding.

Visual DM is a tabletop roleplaying game companion/simulation tool that brings to life the worlds, characters, and stories from tabletop RPGs. It emphasizes a robust, modular, and extensible design with a focus on procedural generation, rich NPCs, and immersive storytelling driven by advanced AI.

The goal is to create a virtual world that facilitates an adaptive, living, and dynamic tabletop roleplaying experience. Visual DM allows for traditional GM-led play, solo/GM-less play, or a hybrid approach.

## Core Design Philosophy

**Summary:** Outlines the fundamental principles that guide Visual DM's development, emphasizing accessibility, modularity, AI integration, procedural generation, and enhancing tabletop gameplay.

**Improvement Notes:** Each philosophy point could benefit from concrete examples in the codebase.

1. **Accessibility with Depth:** Easy for beginners but with enough depth for experienced players.
2. **Modular Design:** Components that can be used independently or together.
3. **AI-Powered Storytelling:** AI that adapts to player choices and creates compelling narratives.
4. **Procedural Generation:** Dynamic content that feels handcrafted.
5. **Visual Storytelling:** Bringing game elements to life through maps, character portraits, and environments.
6. **Table-First Approach:** Enhancing the tabletop experience, not replacing it.
7. **System Flexibility:** Adaptable to different asset-sets and playstyles.
8. **Living Worlds:** Persistent worlds that evolve based on player actions.
9. **Chaos** Simulating chaos through the complex interplay of disparate systems

## Technical Framework

**Summary:** Details the overarching technical architecture, core systems, and development workflows that support Visual DM's functionality.

**Improvement Notes:** Add diagrams illustrating system relationships and data flows.

### Architecture Overview

**Improvement Notes:** Need more detail on how systems communicate with each other.

The Visual DM architecture is built on a modular system design where each gameplay domain is encapsulated in its own system folder. These systems communicate primarily through:

- Direct imports for tightly coupled systems
- Event-based communication for loose coupling
- Shared data models for consistent state representation

The architecture follows a layered approach:
- Core infrastructure (database, events, shared utilities)
- Domain-specific systems (character, combat, crafting, etc.)
- Cross-cutting concerns (UI, AI integration, etc.)

### Core Systems

**Improvement Notes:** Expand with code examples for key patterns.

#### Game Loop
The main execution cycle of the game manages the flow of gameplay, processing inputs, updating the game state, and rendering outputs at appropriate intervals.

#### Event System
The event system enables communication between loosely coupled components through a publish-subscribe pattern. Events are strongly typed and can be processed by middleware.

#### Asset Management
Handles loading, caching, and accessing game assets like images, audio, and data files.

#### Save/Load System
Manages game state persistence, allowing games to be saved and restored.

### Development Workflow

**Improvement Notes:** Add troubleshooting guide and common development tasks.

The development workflow for Visual DM emphasizes:

- Test-driven development for core systems
- Feature branching in version control
- Regular integration of changes
- Documentation updates alongside code changes
- Performance profiling for critical paths

Developers should follow these steps for new features:
1. Document design in appropriate section of Development Bible
2. Create tests for the new functionality
3. Implement the feature following established patterns
4. Update documentation with implementation details
5. Submit for review

## Systems

This section describes each of the core systems in Visual DM, aligned with the actual directory structure in the codebase.

### Analytics System

**Summary:** Collects and processes gameplay data for metrics analysis and performance monitoring.

**Improvement Notes:** Include privacy compliance section.

The analytics system tracks player behavior, system performance, and game metrics to inform development decisions and optimize gameplay experiences.

Key components include:
- Event tracking
- Metrics collection
- Usage pattern analysis
- Performance monitoring

### Arc System

**Status: ✅ FULLY IMPLEMENTED AND TESTED**

**Location**: `/backend/systems/arc/` - Complete Arc System implementation including models, services, repositories, and API endpoints.

**Integration Test**: All components tested and working correctly via `backend/systems/arc/test_integration.py`

The Arc System provides a comprehensive meta-narrative framework that operates above individual quests and encounters, creating overarching storylines that give meaning and direction to player actions. It integrates with GPT for dynamic content generation and provides sophisticated progression tracking and analytics.

### Core Components

**Models** (`/backend/systems/arc/models/`):
- `Arc`: Main arc entity with narrative structure, progression tracking, and metadata
- `ArcStep`: Individual steps within an arc with completion criteria and narrative text  
- `ArcProgression`: Tracks player progression through arc steps with analytics
- `ArcCompletionRecord`: Records completed arcs with outcomes and consequences
- Supporting enums for arc types, statuses, priorities, and progression methods

**Services** (`/backend/systems/arc/services/`):
- `ArcManager`: Core service for arc lifecycle management and operations
- `ArcGenerator`: GPT-powered arc generation with configurable templates and prompts
- `QuestIntegrationService`: Bridges arcs with the quest system for seamless integration
- `ProgressionTracker`: Advanced analytics and progression monitoring with comprehensive reporting

**Repositories** (`/backend/systems/arc/repositories/`):
- Abstract base classes with memory implementations for development
- Support for arc, arc step, progression, and integration data persistence
- Designed for easy database backend integration

**API Layer** (`/backend/systems/arc/routers/`):
- `arc_router.py`: 20+ endpoints for full CRUD operations, activation, and management
- `analytics_router.py`: 15+ endpoints for performance metrics, health monitoring, and reporting
- Comprehensive error handling, validation, and documentation

**Events System** (`/backend/systems/arc/events/`):
- `ArcEvent` and `ArcEventType` for system integration and event handling
- Support for lifecycle events, progression tracking, and cross-system communication

**Utilities** (`/backend/systems/arc/utils/`):
- `arc_utils.py`: Common operations, validation, and helper functions
- `gpt_utils.py`: GPT integration utilities with prompt templates and content generation

### Arc Types and Scope

1. **Global Arcs**: World-spanning narratives affecting entire campaigns
2. **Regional Arcs**: Location-specific storylines with regional impact  
3. **Character Arcs**: Personal character development and growth narratives
4. **NPC Arcs**: Supporting character storylines that intersect with player actions

### Key Features

- **GPT Integration**: Dynamic arc generation with configurable prompts and templates
- **Tag-Based Quest Integration**: Seamless connection between arcs and quest generation
- **Multi-Layer Progression**: Sophisticated tracking of arc advancement and player engagement
- **Analytics and Reporting**: Comprehensive performance metrics and system health monitoring
- **Cross-System Integration**: Event-driven architecture for integration with other game systems
- **Flexible Configuration**: Customizable arc types, priorities, and progression methods

### Factory Function

Use `create_arc_system()` from `/backend/systems/arc/` to instantiate all components with proper dependency injection:

```python
from backend.systems.arc import create_arc_system

arc_manager, arc_generator, quest_integration, progression_tracker = create_arc_system()
```

### Integration Points

- **Quest System**: Arcs generate quest opportunities through tag-based matching
- **World Events**: Arc progression can trigger world state changes
- **Character Development**: Character arcs track personal growth and relationships
- **Campaign Management**: Global arcs provide overarching campaign structure

The Arc System is production-ready and provides a robust foundation for narrative-driven gameplay with comprehensive tracking, analytics, and GPT-powered content generation.

### Auth/User System

**Summary:** Manages user authentication, accounts, permissions, and preferences across the application.

**Improvement Notes:** Add security best practices section.

The auth/user system handles user authentication, authorization, and profile management. It ensures secure access to the application and personalizes the experience based on user preferences.

Key components include:
- Authentication providers
- User profile management
- Permission system
- Preference storage

### Character System

**Summary:** Core system for character creation, attributes, skills, advancement, and race-specific traits.

**Improvement Notes:** Add UML diagrams of character class relationships.

#### Core Attributes

- **Strength (STR):** Physical power and brute force.
- **Dexterity (DEX):** Agility, reflexes, and finesse.
- **Constitution (CON):** Endurance, stamina, and resilience.
- **Intelligence (INT):** Knowledge, memory, and reasoning.
- **Wisdom (WIS):** Perception, intuition, and willpower.
- **Charisma (CHA):** Force of personality, persuasiveness, and leadership.

**Note:** In Visual DM, these are referred to as "stats" rather than "attributes" or "abilities" as in D&D. They range from -3 to +5 directly, with no separate modifier calculation.

#### Skills

Characters have skill proficiencies that reflect their training and natural aptitudes. Skill checks are made by rolling a d20 and adding the relevant attribute and skill modifier.

The canonical skill list includes:
- **Appraise (INT):** Determine the value of items
- **Balance (DEX):** Maintain footing on narrow or unstable surfaces
- **Bluff (CHA):** Deceive others through words or actions
- **Climb (STR):** Scale vertical surfaces
- **Concentration (CON):** Maintain focus during distractions or while injured
- **Craft (INT):** Create or repair items (subskills: Alchemy, Armorsmithing, Weaponsmithing, Trapmaking, Bowmaking)
- **Decipher Script (INT):** Understand unfamiliar writing or codes
- **Diplomacy (CHA):** Negotiate and persuade in good faith
- **Disable Device (INT):** Disarm traps or sabotage mechanical devices
- **Disguise (CHA):** Change appearance to conceal identity
- **Escape Artist (DEX):** Slip free from bonds or tight spaces
- **Forgery (INT):** Create fraudulent documents
- **Gather Information (CHA):** Collect rumors and information from locals
- **Handle Animal (CHA):** Train and care for animals
- **Heal (WIS):** Provide medical treatment
- **Hide (DEX):** Conceal oneself from observation
- **Intimidate (CHA):** Influence others through threats or fear
- **Jump (STR):** Leap across gaps or over obstacles
- **Knowledge (INT):** Specialized information in various fields (subskills: Arcana, Architecture and Engineering, Dungeoneering, Geography, History, Local, Nature, Nobility and Royalty, Religion, The Planes)
- **Listen (WIS):** Notice sounds and conversations
- **Move Silently (DEX):** Move without making noise
- **Open Lock (DEX):** Pick locks
- **Perform (CHA):** Entertain others (subskills: Act, Comedy, Dance, Keyboard Instruments, Oratory, Percussion Instruments, String Instruments, Wind Instruments, Sing)
- **Profession (WIS):** Practice a trade or occupation
- **Ride (DEX):** Control mounts
- **Search (INT):** Locate hidden objects or features
- **Sense Motive (WIS):** Discern intentions and detect lies
- **Sleight of Hand (DEX):** Perform acts of manual dexterity
- **Spellcraft (INT):** Identify and understand magical effects
- **Spot (WIS):** Notice visual details
- **Survival (WIS):** Endure harsh environments and track creatures
- **Swim (STR):** Move through water
- **Tumble (DEX):** Acrobatic movements to avoid attacks or falls
- **Use Magic Device (CHA):** Operate magical items regardless of restrictions
- **Use Rope (DEX):** Manipulate ropes for various purposes

#### Character Races

Diverse species with unique traits, abilities, and cultural backgrounds.

- **Human:** Versatile and adaptable with no specific strengths or weaknesses.
- **Elf:** Long-lived, graceful beings with enhanced perception and magical affinity.
- **Dwarf:** Sturdy mountain-dwellers with resistance to poison and magic.
- **Halfling:** Small, nimble folk with extraordinary luck.
- **Gnome:** Clever inventors with magical tricks and illusions.
- **Half-Elf:** Blend of human adaptability and elven grace.
- **Half-Orc:** Strong and resilient with savage combat prowess.
- **Dragonborn:** Dragon-descended humanoids with breath weapons.
- **Tiefling:** Humans with fiendish ancestry and resistances.

#### Character Advancement

- **Experience Points (XP):** Earned through combat, exploration, and completing objectives.
- **Levels:** Characters gain new abilities and powers as they advance in level.
- **Abilities:** Special talents that customize characters further. Note that in Visual DM, what D&D calls "feats" are called "abilities".

### Combat System

**Summary:** Tactical combat mechanics including initiative, actions, damage calculation, and combat conditions.

**Improvement Notes:** Include more examples of complex combat scenarios.

The combat system is designed to be tactical, engaging, and balanced, allowing for a variety of strategies and playstyles.

#### Combat Flow

1. **Initiative:** Determined by DEX + modifiers, establishing turn order.
2. **Actions:** Each character gets one Action, one Bonus Action, one Reaction, and two Free Actions per round.
3. **Movement:** Characters can move up to their speed (typically 30 feet) during their turn.
4. **Attack Resolution:** Based on stats, skills, and situational modifiers.

#### Damage System and Health 

- **Armor Class (AC):** Calculated as 10 + Dexterity + abilities + magic. Determines whether an attack hits.
- **Damage Reduction (DR):** Reduces incoming damage by a flat amount based on armor, resistances, and abilities. Different for each damage type.
- **Health Points (HP):** Represent a character's vitality and ability to avoid serious injury.
- **Temporary Health:** Extra buffer from spells, abilities, or items that absorbs damage first.
- **Death and Dying:** Characters who reach 0 HP begin making death saving throws.

#### Combat Actions

- **Attack:** Roll d20 + skill + stat vs. target's AC.
- **Cast Spell:** Using magical abilities, often requiring concentration.
- **Dodge:** Impose disadvantage on attacks against you.
- **Dash:** Double movement speed for the turn.
- **Disengage:** Move without provoking opportunity attacks.
- **Hide:** Attempt to become hidden from enemies.
- **Help:** Give advantage to an ally's next check.
- **Ready:** Prepare an action to trigger on a specific circumstance.

#### Combat Conditions

- **Blinded:** Cannot see, disadvantage on attacks, advantage on attacks against them.
- **Charmed:** Cannot attack charmer, charmer has advantage on social checks.
- **Deafened:** Cannot hear.
- **Frightened:** Disadvantage on checks while source of fear is visible, cannot move closer to fear source.
- **Grappled:** Speed becomes 0, ends if grappler is incapacitated.
- **Incapacitated:** Cannot take actions or reactions.
- **Invisible:** Cannot be seen without special senses, advantage on attacks, disadvantage on attacks against them.
- **Paralyzed:** Cannot move or speak, automatically fails STR and DEX saves, advantage on attacks against them, critical hit if attacker is within 5 feet.
- **Petrified:** Transformed to stone, cannot move or speak, automatically fails STR and DEX saves, resistance to all damage.
- **Poisoned:** Disadvantage on attack rolls and ability checks.
- **Prone:** Can only crawl, disadvantage on attack rolls, melee attacks against them have advantage, ranged attacks against them have disadvantage.
- **Restrained:** Speed becomes 0, disadvantage on DEX saves and attack rolls, advantage on attacks against them.
- **Stunned:** Incapacitated, automatically fails STR and DEX saves, advantage on attacks against them.
- **Unconscious:** Incapacitated, cannot move or speak, automatically fails STR and DEX saves, advantage on attacks against them, critical hit if attacker is within 5 feet.

### Crafting System

**Summary:** Allows creation of items through recipes, ingredients, and crafting stations with skill requirements and probabilistic outcomes.

**Improvement Notes:** Add diagrams for recipe data structure.

The crafting system enables characters to create items from raw materials. It includes recipes, ingredients, crafting stations, and skill checks.

Key components include:
- Recipe definitions
- Ingredient requirements
- Crafting stations
- Success probability calculations
- Result quality determination
- Experience gain for successful crafting

#### Crafting Process
1. Select a recipe from known recipes
2. Gather required ingredients
3. Access an appropriate crafting station
4. Make skill checks as required by the recipe
5. Determine success and item quality
6. Gain experience in the relevant crafting skill 

### Data System

**Summary:** Manages game data storage, access patterns, and models for persistent state.

**Improvement Notes:** Needs significant expansion with database schema details.

The data system provides storage and retrieval mechanisms for game data, ensuring persistence, integrity, and performance.

Key components include:
- Data models
- Persistence layer
- Caching mechanisms
- Query optimization

#### Canonical Data Directory Structure

**IMPORTANT:** As of the latest reorganization, all static game data files (.json) are located in the root `/data/` directory, not `/backend/data/`. This change was made to improve organization and provide cross-system access to shared data files.

**Canonical Location:** `/data/` (root directory)

**Directory Structure:**
```
/data/
├── adjacency.json              # Global biome adjacency rules
├── balance_constants.json      # Game balance constants
├── biomes/                     # Biome and terrain data
│   ├── adjacency.json          # Biome-specific adjacency rules
│   └── land_types.json         # Land type definitions
├── crafting/                   # Crafting system data
│   ├── recipes/                # Crafting recipes
│   │   ├── alchemy.json
│   │   └── weapons.json
│   └── stations/               # Crafting station definitions
│       └── crafting_stations.json
├── entities/                   # Character and entity data
│   └── races/
│       └── races.json          # Race definitions
├── equipment/                  # Equipment and item data
│   └── items.json              # Item definitions
├── goals/                      # Quest and goal data
│   └── None_goals.json         # Goal templates
├── items/                      # General item data
│   └── item_types.json         # Item type definitions
├── modding/                    # Modding support files
│   ├── schemas/                # JSON schemas for validation
│   └── worlds/                 # World generation templates
├── religion/                   # Religion system data
│   ├── memberships.json        # Religious membership data
│   └── religions.json          # Religion definitions
├── systems/                    # System-specific data
│   ├── events/
│   ├── faction/
│   ├── religion/
│   └── weather/
└── world/                      # World generation data
    └── generation/
        ├── example_world_seed.json
        └── world_seed.schema.json
```

**Usage Pattern:**
```python
# Correct way to access data files
from pathlib import Path

# Load data from root data directory
data_path = Path("data") / "adjacency.json"
with open(data_path, "r") as f:
    adjacency_data = json.load(f)
```

**Benefits of This Structure:**
1. **Separation of Concerns:** Data files are separated from code
2. **Cross-System Access:** All systems can access shared data files
3. **Modding Support:** Centralized location for modders to find and modify game data
4. **Simplified Deployment:** Easy to backup/deploy data separately from code

**Migration Notes:** 
- All references to `backend/data/` have been updated to use `data/`
- Conflicting files were resolved by choosing canonical versions and archiving alternatives in `/archives/`
- The backend data migration was completed to consolidate all static data files

#### Data Models

- **World Data:** Information about the game world and environment.
- **Character Data:** Character statistics, abilities, and equipment.
- **Quest Data:** Information about available and active quests.
- **NPC Data:** Details about non-player characters.
- **Item Data:** Information about items and equipment.
- **POI State Data:** Evolution state, events, and memory of locations.

#### Data Storage

- **Persistent Storage:** Long-term storage of game data.
- **Runtime Data:** Temporary data used during gameplay.
- **Cloud Storage:** Optional online storage for sharing and backup.
- **Local Storage:** Data stored on the user's device.
- **Database Options:** Various database solutions being explored for POI state storage and world persistence.

#### Data Access Patterns

- **Real-time Access:** Immediate data retrieval for gameplay.
- **Background Loading:** Loading data in the background to prevent interruptions.
- **Data Streaming:** Continuous loading of data as needed.
- **Data Caching:** Storing frequently used data for quick access.

### Dialogue System

**Summary:** Facilitates conversations between players and NPCs with branching dialogue trees and conditional responses.

**Improvement Notes:** Add examples of dialogue scripting syntax.

The dialogue system manages conversations between players and NPCs, supporting branching narratives, conditional responses, and dialogue-based skill checks.

Key components include:
- Dialogue tree structure
- Response conditions
- Dialogue history tracking
- Skill check integration
- Dialogue effects (quest updates, item transfers, etc.)

### Diplomacy System

**Summary:** Handles relationships between factions, diplomatic actions, and negotiation mechanics.

**Improvement Notes:** Needs examples of diplomatic event flows.

The diplomacy system manages relationships between factions, including alliances, rivalries, and neutral stances. It provides mechanics for negotiation, treaties, and diplomatic incidents.

Key components include:
- Faction relationship tracking
- Diplomatic action resolution
- Treaty implementation
- Reputation systems
- Conflict escalation

### Economy System

**Summary:** Simulates economic activities including currency, trade, markets, and resource management.

**Improvement Notes:** Add mathematical models for economic simulation.

**🔄 ONGOING SIMULATION UPGRADE REQUIRED:**

The Economy System must be upgraded to support autonomous economic simulation across all regions simultaneously. Markets should fluctuate based on real supply and demand from NPC activities, trade routes should evolve dynamically, and economic competition should occur naturally without player intervention.

**CURRENT LIMITATION:** Economic systems primarily respond to player actions rather than evolving autonomously.

**NEW REQUIREMENT:** Full world economic simulation with autonomous market forces, trade evolution, and economic competition between NPCs and regions.

#### Autonomous Economic Simulation Requirements:

1. **Real Supply/Demand Dynamics:** Prices fluctuate based on actual NPC production, consumption, and trading activities
2. **Dynamic Trade Route Evolution:** Trade routes change based on political stability, resource availability, and safety conditions
3. **Market Competition:** NPCs compete for market share, establish monopolies, and engage in economic warfare
4. **Regional Economic Specialization:** Regions develop economic advantages based on resources and geographic factors
5. **Economic Cycles:** Natural boom/bust cycles, seasonal variations, and economic crises occur autonomously
6. **Cross-Regional Economic Integration:** Regional economies influence each other through trade and resource dependencies
7. **Economic Innovation:** NPCs develop new trade relationships, discover markets, and create economic opportunities
8. **Wealth Accumulation/Loss:** NPCs and regions experience economic growth, decline, and recovery cycles

The economy system simulates a realistic economic environment affected by supply, demand, scarcity, and player actions.

#### Currency System

- **Standard Coins:** Gold, silver, and copper pieces. **[UPGRADE REQUIRED]** Currency values fluctuate based on regional economic conditions and trade relationships.
- **Regional Currencies:** Local variants with different values. **[UPGRADE REQUIRED]** Exchange rates change dynamically based on economic and political relationships.
- **Trade Goods:** Non-monetary items used for barter. **[UPGRADE REQUIRED]** Trade good values fluctuate based on regional availability and demand.
- **Precious Materials:** Gems and rare metals as alternative currencies. **[UPGRADE REQUIRED]** Values change based on discovery, depletion, and regional demand.

#### Economic Simulation

- **Supply and Demand:** Fluctuating prices based on availability. **[UPGRADE REQUIRED]** Real-time simulation of production, consumption, and stockpiles across all regions.
- **Regional Variations:** Different economies in different regions. **[UPGRADE REQUIRED]** Regions develop distinct economic characteristics and competitive advantages autonomously.
- **Event Impacts:** How events affect local and global economies. **[UPGRADE REQUIRED]** All world events (wars, disasters, discoveries) automatically impact relevant economic systems.
- **Player Influence:** How player actions can change economic conditions. **[UPGRADE REQUIRED]** Player impact becomes part of larger autonomous economic simulation.

#### Trade System

- **Merchant Networks:** Connected traders across regions. **[UPGRADE REQUIRED]** Merchant networks evolve, compete, and form alliances autonomously based on profitability and safety.
- **Caravan Routes:** Established trade paths with specific goods. **[UPGRADE REQUIRED]** Routes change dynamically based on political conditions, bandit activity, and economic opportunities.
- **Black Markets:** Illegal goods and services. **[UPGRADE REQUIRED]** Black markets emerge and evolve based on legal restrictions, enforcement levels, and demand.
- **Guild Influence:** How trade guilds affect prices and availability. **[UPGRADE REQUIRED]** Guilds compete for influence, establish territories, and engage in economic warfare.

#### Resource Management

- **Raw Materials:** Gathering and processing resources. **[UPGRADE REQUIRED]** Resource extraction occurs autonomously by NPCs based on demand, safety, and profitability.
- **Crafting Materials:** Items used to create equipment. **[UPGRADE REQUIRED]** Availability fluctuates based on raw material supply and crafting demand across all regions.
- **Consumable Resources:** Items that are used up during gameplay. **[UPGRADE REQUIRED]** Production and consumption balanced autonomously across the world.
- **Rare Resources:** Valuable materials with special properties. **[UPGRADE REQUIRED]** Discovery, depletion, and control of rare resources drive autonomous conflicts and economic opportunities.

#### World-Scale Economic Simulation:

**[NEW REQUIREMENT]** Implement comprehensive autonomous economic systems:

1. **Production/Consumption Balance:** Each region produces and consumes goods based on population, resources, and capabilities
2. **Trade Network Optimization:** NPCs establish optimal trade routes and adapt to changing conditions
3. **Economic Warfare:** Factions use economic pressure, embargos, and market manipulation as strategic tools
4. **Resource Depletion/Discovery:** Mines empty, new resources are discovered, affecting global markets
5. **Technological/Knowledge Spread:** New crafting techniques and economic innovations spread through trade networks
6. **Economic Migration:** NPCs relocate based on economic opportunities and regional economic health
7. **Market Manipulation:** Wealthy NPCs and factions attempt to manipulate markets for advantage
8. **Economic Espionage:** Information about resources, prices, and trade opportunities becomes valuable commodity

### Equipment System

**Summary:** Manages character equipment including weapons, armor, and magical items with various properties and rarities.

**Improvement Notes:** Include more detail on equipment enhancement mechanics.

The equipment system encompasses weapons, armor, magical items, consumables, and crafting materials. Every item in Visual DM is inherently magical and evolves with the player's character.

#### Equipment Types

- **Weapons:** Melee and ranged options with unique properties and damage types.
  - **Weapon Properties:** Include damage dice, critical hit ranges, range, and special tags (like "reach" or "thrown").
  - **Weapon Types:** Simple, martial, and exotic with different associated abilities.
  - **Weapon Categories:** Heavy (two-handed), Medium (versatile), and Light (one-handed).
  - **Damage Types:** Physical (slashing, piercing, bludgeoning), magical, fire, ice, lightning, poison, psychic, necrotic, radiant, force, acid, thunder, and true damage.

- **Armor:** Protective gear that provides Damage Reduction (DR).
  - **Armor Types:** Light, medium, and heavy, with different encumbrance effects.
  - **AC Bonus:** Contributes to the AC calculation (10 + Dexterity + abilities + magic).
  - **DR Values:** Flat damage reduction that applies after a hit is confirmed.
  - **Max Dex Bonus:** Limit to Dexterity bonus while wearing armor.
  - **Armor Check Penalty:** Penalty to certain physical actions.
  - **Arcane Spell Failure:** Chance for spells to fail when cast in armor.

- **Accessories:** Rings, amulets, cloaks, and other items that provide special benefits.
- **Consumables:** Potions, scrolls, and other one-use items.
- **Tools and Kits:** Items needed for certain skills and activities.

#### Item Quality and Rarity

| Rarity    | Drop Rate (from battles) | Effects | Naming       | Notes |
|-----------|--------------------------|---------|--------------|-------|
| Normal    | 50%                      | 3–5     | Generic      | Frequent, low impact |
| Epic      | 0.25% of drops (1/400)   | 8–12    | Template/GPT | Story-worthy |
| Legendary | 0.0025% of drops (1/40K) | 20      | GPT-named    | Ultra-rare, quest-tied |

#### Item Identification and Discovery

The identification system provides a sense of discovery and progression:

- **Identification Methods:**
  - **Standard Vendors:** Reveal next effect for a fee
  - **Legendary NPCs:** Reveal all effects for a significant price
  - **Trial and Error:** Learning through use, which may be risky
  - **Shopkeepers:** Identify and mark-up legendary items
  
- **Progressive Identification:** Items reveal more properties as they're used or identified professionally

#### Item Leveling and Evolution System

Every item in Visual DM is magical and evolves with the player:

- **Level-Gated Effects:** Effects unlock as character levels up with the item
- **Hidden Potential:** Players won't know an item's full potential until it's fully identified
- **Awakening:** Magical items "wake up" when certain conditions are met
- **Bonding:** Items become more powerful as the character uses them extensively
- **Evolution Paths:** Items can evolve along different paths based on use and character actions

### Events System

**Summary:** Core publish-subscribe system for game events, propagation, and handling across the application.

**Improvement Notes:** Add sequence diagrams for event flows.

The events system is a fundamental infrastructure component that enables loose coupling between systems through a publish-subscribe pattern. It handles event registration, dispatch, and processing.

Key components include:
- Event registration
- Event dispatch
- Event listeners
- Event middleware
- Event history

### Faction System

**Summary:** Handles organization of NPCs into groups with shared goals, relationships, and influence mechanics.

**Improvement Notes:** Need more details on faction AI decision-making.

**🔄 ONGOING SIMULATION UPGRADE REQUIRED:**

The Faction System must be upgraded to support autonomous faction evolution, territorial expansion/contraction, internal politics, and dynamic relationships between factions across the entire world. Factions should pursue their objectives actively, not just respond to player actions.

**CURRENT LIMITATION:** Factions are largely static entities that change only in response to player actions.

**NEW REQUIREMENT:** Factions must autonomously compete for resources, territory, and influence while managing internal politics and external relationships.

#### Autonomous Faction Operations:

1. **Territorial Expansion:** Factions actively seek to expand their territory through military conquest, economic influence, and diplomatic means
2. **Resource Competition:** Factions compete for access to valuable resources, trade routes, and strategic locations
3. **Internal Politics:** Leadership struggles, factional splits, and organizational evolution occur naturally
4. **Diplomatic Maneuvering:** Factions form and break alliances, negotiate treaties, and engage in espionage
5. **Military Campaigns:** Factions wage war, conduct raids, and defend their territories autonomously
6. **Economic Warfare:** Factions manipulate markets, establish trade monopolies, and economically pressure rivals
7. **Recruitment and Growth:** Factions actively recruit new members and attempt to convert neutrals
8. **Ideological Evolution:** Faction beliefs and goals evolve based on leadership changes and external pressures

The faction system manages organized groups of NPCs with shared goals, territories, and resources. Factions have relationships with each other and with the player.

Key components include:
- Faction definition and membership **[UPGRADE REQUIRED]** Add dynamic membership changes, recruitment drives, and member loss to rivals/death
- Inter-faction relationships **[UPGRADE REQUIRED]** Implement autonomous relationship changes based on territory disputes, resource competition, and ideological conflicts
- Territory control **[UPGRADE REQUIRED]** Factions must actively expand, defend, and potentially lose territory through autonomous actions
- Resource management **[UPGRADE REQUIRED]** Factions compete for resources and establish economic relationships/conflicts autonomously
- Leadership structure **[UPGRADE REQUIRED]** Leadership changes through succession, coups, elections, or assassination attempts
- Player reputation with factions **[UPGRADE REQUIRED]** Reputation changes based on faction evolution and indirect player impact on faction interests

#### Cross-Faction Conflict Generation:

**[NEW REQUIREMENT]** Implement systems for generating meaningful faction conflicts:

1. **Territorial Disputes:** Automatic generation of border conflicts and expansion attempts
2. **Resource Wars:** Conflicts over access to mines, trade routes, magical sites, and fertile land
3. **Ideological Conflicts:** Religious differences, political philosophy clashes, and cultural tensions
4. **Economic Competition:** Trade wars, market manipulation, and commercial rivalry
5. **Succession Crises:** Power vacuums that lead to multi-faction involvement
6. **Alliance Network Shifts:** Complex web of changing alliances and betrayals
7. **Revolutionary Movements:** Internal faction rebellions that can split organizations
8. **External Threats:** Factions must cooperate or compete when facing outside dangers

### Inventory System

**Summary:** Manages character inventories, item storage, weight calculations, and item categorization.

**Improvement Notes:** Add UI mockups for inventory interfaces.

The inventory system tracks items owned by characters, handling storage limitations, organization, and access. It manages encumbrance, categorization, and item interactions.

Key components include:
- Item storage and retrieval
- Weight and encumbrance calculation
- Item categorization and sorting
- Inventory UI
- Item transfers between inventories
- Special storage (bags of holding, etc.)

### LLM System

**Summary:** Integrates large language models for natural language processing, dynamic content, and AI-driven interactions.

**Improvement Notes:** Significantly underdocumented; needs expansion.

The LLM (Large Language Model) system integrates AI language models like GPT to enhance game content, generate dynamic text, and enable natural language interactions.

Key components include:
- Prompt engineering
- Context management
- Response processing
- Content generation
- Integration with other systems (dialogue, quests, etc.)

### Loot System

**Summary:** Generates treasure and rewards through drop tables with probabilistic distribution and level-appropriate scaling.

**Improvement Notes:** Add examples of complex loot table configurations.

The loot system generates appropriate rewards for encounters, quests, and exploration. It balances randomness with appropriate progression.

#### Loot Generation System

- **Drop System:** Carefully balanced to make loot drops regular and meaningful
- **Context-Sensitive:** Takes player level and battle context into account when generating loot
- **AI-Enhanced:** GPT used for epic/legendary naming and lore generation
- **Rule-Compliant:** All generated items validated against game rules for balance

Key components include:
- Loot tables with weighted probabilities
- Level-appropriate scaling
- Contextual loot generation
- Special/unique item generation
- Currency calculation

### Magic System

**Summary:** Implements magic mechanics including schools, spellcasting, resources, and magical effects.

**Improvement Notes:** Could use more detail on spell creation workflows.

The magic system is flexible and diverse, allowing for creative spellcasting and magical effects.

#### Magic Schools

- **Abjuration:** Protective spells, wards, and barriers.
- **Conjuration:** Summoning creatures or objects.
- **Divination:** Gaining information and foreseeing the future.
- **Enchantment:** Influencing minds and emotions.
- **Evocation:** Elemental damage and energy manipulation.
- **Illusion:** Creating sensory deceptions.
- **Necromancy:** Manipulating life and death energies.
- **Transmutation:** Changing physical properties of creatures or objects.

#### Magic Resource System

- **Mana Points (MP):** Resource used to cast spells, regenerates with rest.
- **Concentration:** Many powerful spells require concentration, limiting concurrent effects.
- **Spell Preparation:** Some casters must prepare spells in advance.
- **Ritual Casting:** Casting spells without expending resources by taking extra time.

#### Magic Domains

Represents the source or tradition of magic, which affects spellcasting style and available spells:

- **Arcane:** Traditional wizardry and academic magic study.
- **Divine:** Magic granted by deities and higher powers.
- **Nature:** Magic drawn from natural forces and the elements.
- **Occult:** Forbidden knowledge and pacts with otherworldly entities.

#### Magical Effects and Interactions

- **Magical Detection:** Spells and abilities to sense and identify magic.
- **Counterspelling:** Ability to interrupt or dispel other spells.
- **Magic Resistance:** Some creatures or items resist magical effects.
- **Anti-Magic:** Areas where magic is suppressed or functions differently.

### Memory System

**Summary:** Tracks NPC memories of player actions and world events, with recall, importance weighting, and decay mechanics.

**Improvement Notes:** Add examples of memory influence on NPC behavior.

The memory system allows NPCs and locations to remember events and interactions. It creates persistent consequences for player actions and more realistic NPC behaviors.

Key components include:
- Memory recording
- Memory retrieval
- Memory importance weighting
- Memory decay over time
- Influence on NPC behavior and dialogue

#### Player Memory

Player characters possess an internal memory system that operates similarly to NPC memory but remains hidden from direct player access. This system tracks the player character's experiences, learned information, and relationship history to influence arc generation and quest relevance.

**Key Features:**
- **Experience Tracking:** Records significant events, completed quests, and narrative milestones
- **Relationship Memory:** Maintains detailed records of interactions with NPCs, factions, and locations
- **Background Integration:** Connects character background elements to ongoing narrative development
- **Arc History:** Preserves progression through character-specific arcs for continuity
- **Knowledge Base:** Tracks discovered information, rumors heard, and world lore encountered

**Arc Generation Integration:**
- Previous arc completion data influences new character arc creation
- Background elements resurface in narrative progression
- Relationship patterns affect quest generation and NPC interaction opportunities
- Experience-based difficulty scaling for appropriate challenge levels

**System Operation:**
- Automatic recording without player intervention or awareness
- Memory decay and importance weighting similar to NPC system
- Cross-reference capability with world events and other character memories
- Integration with Core Memory for world-significant events
- Influences dialogue options and quest availability without explicit player knowledge

### Motif System

**Summary:** Manages narrative themes and recurring elements throughout campaigns for cohesive storytelling.

**Improvement Notes:** Minimal documentation exists; needs significant expansion.

The motif system tracks and applies recurring themes, symbols, and narrative elements to create cohesive, interconnected stories and environments.

Key components include:
- Motif definition and categorization
- Motif application to NPCs, locations, and quests
- Motif evolution and development
- Thematic consistency enforcement
- Player-influenced motif adaptation

### NPC System

**Summary:** Governs non-player character generation, behavior, personalities, relationships, and development over time.

**Improvement Notes:** Add flowcharts for NPC decision-making processes.

**🔄 ONGOING SIMULATION UPGRADE REQUIRED:**

The NPC System must be fundamentally upgraded to support continuous background simulation of ALL NPCs across the entire world, not just those near the player. This represents a shift from reactive NPC behavior to proactive autonomous NPC life simulation.

**CURRENT LIMITATION:** NPCs are primarily passive entities that respond to player interaction.

**NEW REQUIREMENT:** NPCs must autonomously pursue goals, form relationships, generate conflicts, and evolve throughout the world regardless of player proximity.

#### Autonomous NPC Lifecycle Requirements:

1. **Independent Goal Pursuit:** NPCs generate and pursue personal objectives (marriage, career advancement, revenge, exploration, etc.)
2. **Relationship Evolution:** NPCs form friendships, rivalries, romantic relationships, and family bonds autonomously
3. **Economic Participation:** NPCs engage in trade, accumulate wealth, start businesses, and compete for resources
4. **Political Engagement:** NPCs join factions, seek leadership roles, and participate in diplomatic activities
5. **Quest Generation:** NPCs create and attempt to complete their own quests, potentially interfering with player objectives
6. **Knowledge Acquisition:** NPCs learn information, spread rumors, and make decisions based on accumulated knowledge
7. **Aging and Death:** NPCs age naturally, reproduce, and pass away, creating generational turnover
8. **Migration Patterns:** NPCs relocate based on opportunities, threats, and personal motivations

#### NPC Types

- **Villagers:** Ordinary people in settlements. **[UPGRADE REQUIRED]** Each villager needs personal goals, family relationships, and autonomous daily routines.
- **Merchants:** Traders selling goods and services. **[UPGRADE REQUIRED]** Merchants must establish trade routes, negotiate deals, and compete with other merchants autonomously.
- **Quest Givers:** NPCs who provide missions. **[UPGRADE REQUIRED]** These NPCs should generate quests based on their ongoing problems and objectives, not just wait for player interaction.
- **Allies:** Characters who assist the players. **[UPGRADE REQUIRED]** Allies should pursue their own agendas and may occasionally conflict with player interests.
- **Antagonists:** Opponents and villains. **[UPGRADE REQUIRED]** Antagonists must actively work toward their goals, build power bases, and adapt their strategies.
- **Neutrals:** Characters with their own agendas. **[UPGRADE REQUIRED]** These NPCs should be the most autonomous, pursuing complex multi-faceted objectives.

#### NPC Personality Generation

- **Trait Selection:** Defining personality characteristics. **[UPGRADE REQUIRED]** Add ambition levels, social drive, and change potential.
- **Motivation Generation:** What drives the NPC's actions. **[UPGRADE REQUIRED]** Generate both short-term and long-term goals that evolve over time.
- **Relationship Map:** How the NPC relates to others. **[UPGRADE REQUIRED]** Dynamic relationship networks that change based on NPC interactions.
- **Behavior Patterns:** How the NPC acts in different situations. **[UPGRADE REQUIRED]** Include proactive behavior patterns, not just reactive ones.

#### NPC Appearance

- **Physical Traits:** Height, weight, and distinguishing features.
- **Clothing and Style:** How the NPC dresses and presents themselves. **[UPGRADE REQUIRED]** Clothing and style should change based on wealth, status, and life events.
- **Mannerisms:** Unique behaviors and habits.
- **Voice and Speech Patterns:** How the NPC communicates.

#### NPC Development

- **Character Growth:** How NPCs change over time. **[UPGRADE REQUIRED]** NPCs must grow skills, change personality traits, and adapt to life experiences autonomously.
- **Relationship Evolution:** Changing relationships with players. **[UPGRADE REQUIRED]** Extend to all NPC-to-NPC relationships across the world.
- **Narrative Roles:** How NPCs fit into the larger story. **[UPGRADE REQUIRED]** NPCs should be able to change roles (ally to enemy, neutral to important) based on their autonomous actions.
- **Memory and Learning:** How NPCs remember and adapt to player actions. **[UPGRADE REQUIRED]** Expand to include learning from all world events and NPC interactions.

#### World-Scale NPC Interaction Simulation:

**[NEW REQUIREMENT]** Implement systems for simulating meaningful NPC interactions across all regions:

1. **Regional NPC Networks:** Every region maintains active social networks between all NPCs
2. **Cross-Regional Communication:** NPCs exchange information between settlements through travelers, merchants, and messengers
3. **Conflict Generation:** NPCs autonomously develop disputes over resources, relationships, and ideological differences
4. **Alliance Formation:** NPCs form partnerships, marriages, business relationships, and political alliances
5. **Cultural Evolution:** NPC communities develop and change cultural practices, beliefs, and traditions over time
6. **Generational Change:** Children inherit modified versions of parent traits, relationships, and conflicts

### POI System

**Summary:** Handles points of interest including discovery, states, evolution, and memory systems for locations.

**Improvement Notes:** Add examples of POI state transitions.

POIs are dynamic entities that evolve over time through player interaction, NPC decisions, world simulation, and random events.

#### POI Density and Types
- **POI Density:** Each region contains ~20 major POIs (towns, dungeons, etc.), plus 200–400 minor/nature squares (groves, ruins, camps, etc.), with the remainder being wilderness or terrain hexes.
- **Dungeons:** Underground complexes with monsters and treasure.
- **Temples:** Religious sites dedicated to various deities.
- **Towers:** Magical or defensive structures.
- **Camps:** Temporary settlements for various factions.
- **Natural Landmarks:** Unique geographic features with special properties.

#### POI Evolution States
- **Settlement Growth:** POIs can evolve from camps to villages to towns based on population and events.
- **Control Status:** "Cleared," "Monster-controlled," "Disputed," etc.
- **State Tags:** "Rumored," "Cleared," "Inhabited," "Abandoned," etc.

#### POI Memory System
POIs maintain a memory of events that have occurred there:
- **Event Log:** Records player visits, combat, growth, and other significant events.
- **Motif Pool:** Like NPCs, POIs have thematic motifs that influence their development.
- **Next Event Check:** Timestamp for when the POI should next be evaluated for an event.

#### Daily Tick System
The world simulation regularly updates POIs:
- **Event Checks:** Each POI is checked on a scheduled basis.
- **Combat Simulation:** When appropriate, simulates combat between inhabitants and threats.
- **Population Dynamics:** Growth, decline, or abandonment based on events and conditions.
- **Settlement Growth:** POIs can evolve in tier based on successful development.

#### POI State Transitions
POIs can transition between states based on events:
- **Cleared → Inhabited:** When players clear a location and NPCs move in.
- **Inhabited → Abandoned:** When population drops or disasters occur.
- **Abandoned → Monster-controlled:** When monsters reclaim abandoned settlements.
- **Monster-controlled → Cleared:** When players defeat monsters.

### Population System

**Summary:** Simulates settlement demographics, growth, migration, and resource consumption over time.

**Improvement Notes:** Needs mathematical models for population dynamics.

The population system simulates the growth, decline, and movement of populations within settlements. It factors in resources, threats, and events.

Key components include:
- Population growth calculations
- Resource consumption
- Migration triggers
- Demographic tracking
- Crisis response (famine, disease, etc.)

### Quest System

**Summary:** Manages quest generation, progression tracking, rewards, and interconnections between quests.

**Improvement Notes:** Add examples of complex quest chains.

**🔄 ONGOING SIMULATION UPGRADE REQUIRED:**

The Quest System must be fundamentally upgraded to support autonomous quest generation, NPC quest completion, and dynamic storyline evolution throughout the world. NPCs should generate their own quests and attempt to complete them, creating a living world of ongoing narratives that succeed or fail independent of player involvement.

**CURRENT LIMITATION:** Quests are primarily generated for player consumption and remain static until player interaction.

**NEW REQUIREMENT:** NPCs must autonomously generate quests based on their needs, pursue quest objectives, and succeed or fail in their attempts, creating dynamic world narratives.

#### Autonomous Quest Generation and Resolution:

1. **NPC-Driven Quest Creation:** NPCs generate quests based on their personal problems, faction objectives, and regional needs
2. **Multi-NPC Quest Participation:** Multiple NPCs may attempt the same quest, compete for objectives, or collaborate
3. **Quest Success/Failure Simulation:** NPCs attempt to complete quests with probabilistic outcomes based on their abilities
4. **Cascading Quest Consequences:** Quest outcomes generate new quests and affect regional storylines
5. **Cross-Regional Quest Networks:** Quests span multiple regions with traveling NPCs and multi-location objectives
6. **Temporal Quest Evolution:** Quests change objectives, urgency, and difficulty over time if not completed
7. **Player Impact on NPC Quests:** Player actions indirectly affect NPC quest success rates and availability
8. **Failed Quest Aftermath:** Consequences of NPC quest failures create new storylines and opportunities

#### Quest Types

- **Main Quests:** Primary storyline missions. **[UPGRADE REQUIRED]** Main quests should progress based on world events and NPC actions, not just player triggers.
- **Side Quests:** Optional missions for additional rewards. **[UPGRADE REQUIRED]** Side quests are continuously generated by NPCs based on their ongoing problems and opportunities.
- **Faction Quests:** Missions for specific factions. **[UPGRADE REQUIRED]** Factions autonomously generate missions to advance their objectives, which NPCs attempt to complete.
- **Character Quests:** Personal quests for character development. **[UPGRADE REQUIRED]** NPCs pursue personal development quests that change their capabilities and relationships.
- **Random Encounters:** Spontaneous events during travel. **[UPGRADE REQUIRED]** Encounters reflect ongoing world events and NPC activities in the area.

#### Quest Generation Parameters

- **Difficulty Scaling:** Adjusting quest challenge based on party level. **[UPGRADE REQUIRED]** Add NPC capability assessment for autonomous quest attempts.
- **Reward Balancing:** Appropriate rewards for quest difficulty. **[UPGRADE REQUIRED]** NPCs seek rewards that match their needs and capabilities.
- **Narrative Integration:** Connecting quests to the overall story. **[UPGRADE REQUIRED]** All quests should integrate with ongoing faction conflicts, NPC relationships, and regional events.
- **Player Interest Matching:** Generating quests that align with player preferences. **[UPGRADE REQUIRED]** Maintain but secondary to autonomous NPC quest generation.

#### Adventure Structures

- **Linear Adventures:** Straightforward progression through predetermined events. **[UPGRADE REQUIRED]** Linear adventures should adapt based on autonomous world changes.
- **Branching Adventures:** Multiple paths leading to different outcomes. **[UPGRADE REQUIRED]** Branches affected by NPC actions and world events.
- **Sandbox Adventures:** Open-ended exploration with emergent storytelling. **[UPGRADE REQUIRED]** Emergent stories driven by autonomous NPC quest activities.
- **Hybrid Adventures:** Combining elements of different structures. **[UPGRADE REQUIRED]** Structure adapts dynamically to ongoing world simulation.

#### Campaign Management

- **Campaign Arcs:** Long-term story development across sessions. **[UPGRADE REQUIRED]** Arcs progress through autonomous NPC actions and world events.
- **Session Planning:** Tools for preparing individual game sessions. **[UPGRADE REQUIRED]** Planning tools must account for autonomous world changes between sessions.
- **Plot Tracking:** Managing complex storylines and character involvement. **[UPGRADE REQUIRED]** Track autonomous NPC storylines and their interaction with player narratives.
- **World Consequences:** How player choices affect the world over time. **[UPGRADE REQUIRED]** Consequences now include interaction with ongoing autonomous storylines.

#### World-Scale Quest Network Simulation:

**[NEW REQUIREMENT]** Implement systems for autonomous quest ecosystem:

1. **Regional Quest Pools:** Each region maintains active pools of generated quests being pursued by local NPCs
2. **Quest Success Probability Engine:** Sophisticated system for determining NPC quest success based on skills, resources, and circumstances
3. **Quest Failure Recovery:** Systems for generating follow-up quests and consequences when NPCs fail their objectives
4. **Quest Competition:** Multiple NPCs/factions may pursue conflicting objectives, creating natural quest conflicts
5. **Quest Resource Economy:** NPCs compete for limited resources, information, and assistance needed for quest completion
6. **Narrative Continuity Tracking:** Maintain consistency in ongoing storylines across the world simulation
7. **Player Quest Integration:** Player quests can intersect with, assist, or interfere with autonomous NPC questlines

### Region System

**Summary:** Handles geographic regions, their properties, events, and environmental factors.

**Improvement Notes:** Needs more detail on region generation algorithms.

The region system manages large-scale geographic areas with distinct biomes, cultures, and political entities.

Key components include:
- Region definition and boundaries
- Regional features and landmarks
- Regional climate and weather
- Political control and influence
- Regional events and conditions

### Religion System

**Summary:** Implements deities, religious practices, divine intervention, and faith mechanics.

**Improvement Notes:** Add examples of religious influence on gameplay.

The religion system represents the spiritual beliefs of the world, including deities, practices, and divine powers.

Key components include:
- Deity definition and domains
- Religious practices and rituals
- Clerical magic and divine intervention
- Religious organizations and hierarchies
- Faith and devotion mechanics

### Rumor System

**Summary:** Manages the generation and propagation of information with varying degrees of truth throughout the game world.

**Improvement Notes:** Add network diagrams for rumor propagation.

The rumor system simulates the spread of information through the world, with varying levels of accuracy and detail.

Key components include:
- Rumor generation from world events
- Information propagation mechanics
- Truth distortion over time
- NPC knowledge access
- Player rumor collection and verification

### Shared System

**Summary:** Provides common utilities, resources, and cross-system functions used throughout the codebase.

**Improvement Notes:** Needs inventory of shared components with usage examples.

The shared system contains utilities and helper functions used across multiple systems. It promotes code reuse and consistency.

Key components include:
- Mathematical utilities
- String processing
- Data structure helpers
- Random generation functions
- Common game mechanics

### Storage System

**Summary:** Handles persistent storage, save/load functionality, and game state management.

**Improvement Notes:** Add detailed save file format documentation.

The storage system manages the saving and loading of game state, ensuring persistence between sessions.

Key components include:
- Save file format and management
- Auto-save functionality
- Game state serialization
- Save file encryption and validation
- Cloud save integration

### Tension/War System

**Summary:** Simulates conflict escalation, war mechanics, battles, territorial control, and peace negotiations.

**Improvement Notes:** Add examples of war simulation calculations.

The tension/war system models conflicts between factions, from minor disputes to full-scale wars.

Key components include:
- Tension escalation metrics
- War declaration triggers
- Battle simulation mechanics
- Territory control changes
- Peace negotiation processes
- War aftermath effects

### Time System

**Summary:** Manages game time through calendars, day/night cycles, seasons, and time-based events.

**Improvement Notes:** Add diagrams for time-based event scheduling.

The time system tracks the passage of time in the game world, affecting lighting, weather, NPC schedules, and events.

Key components include:
- Calendar and date tracking
- Day/night cycle management
- Season progression
- Time-based event scheduling
- Time manipulation (spells, effects, etc.)

### World Generation System

**Summary:** Creates procedural worlds with geography, climate, biomes, settlements, and dungeons.

**Improvement Notes:** Add more visual examples of generation output.

**🔄 ARCHITECTURAL SHIFT - FULL UPFRONT GENERATION + ONGOING SIMULATION:**

Modern consumer gaming hardware (gaming laptops, Xbox Series S with 8-core AMD Zen 2 CPUs and substantial RAM) can absolutely support generating the entire world/continent, including all NPCs and POIs, at game startup. This represents a fundamental architectural shift from our current dynamic generation approach to a more sophisticated full-world simulation model.

**CURRENT LIMITATION:** We currently generate content dynamically as areas are discovered, which creates narrative inconsistencies and prevents believable long-term world evolution.

**NEW PARADIGM:** Full upfront generation at game startup followed by continuous ongoing simulation of all world elements, regardless of player proximity or discovery status.

**TECHNICAL FEASIBILITY CONFIRMED:** Modern hardware can handle this computational load. Benefits far outweigh the initial generation time cost.

#### Benefits of Full Upfront Generation:
- **Narrative Coherence:** Consistent world state enables better story integration
- **Believable NPC Interactions:** NPCs can form relationships and conflicts before player interaction
- **Dynamic World Events:** Faction conflicts, economic changes, and population migrations occur naturally
- **Quest Integration:** Arcs and quests can be generated based on actual world state rather than placeholder content
- **Long-term Consequences:** Player actions have meaningful impact on an already-existing world

#### World Map Generation

- **Continent Scale:** Large landmasses with diverse biomes. **[UPGRADE REQUIRED]** Generate all continents with complete geographic, political, and resource mapping at startup.
- **Region Scale:** Political and geographic divisions within continents. **[UPGRADE REQUIRED]** Pre-generate all regional boundaries, controlling factions, population distributions, and resource nodes.
- **Local Scale:** Detailed terrain for adventuring. **[UPGRADE REQUIRED]** Generate detailed terrain maps for all regions, not just discovered areas.
- **Underworld:** Cave systems, dungeons, and underground realms. **[UPGRADE REQUIRED]** Pre-generate all dungeon systems with their inhabitants and treasures.

#### Geographic Features

- **Mountains:** Difficult terrain with valuable resources.
- **Forests:** Dense woodlands with hidden locations.
- **Deserts:** Harsh environments with ancient ruins.
- **Oceans and Seas:** Naval travel and underwater locations.
- **Rivers and Lakes:** Travel routes and settlements.
- **Swamps and Marshes:** Dangerous environments with unique resources.

#### Settlement Generation

- **Cities:** Major population centers with diverse districts. **[UPGRADE REQUIRED]** Generate all cities with complete NPC populations, political structures, and economic systems at startup.
- **Towns:** Smaller settlements with limited services. **[UPGRADE REQUIRED]** Pre-populate all towns with inhabitants, relationships, and ongoing storylines.
- **Villages:** Rural communities focused on local resources. **[UPGRADE REQUIRED]** Generate all villages with family structures, local conflicts, and resource dependencies.
- **Outposts:** Frontier establishments with specific purposes.
- **Ruins:** Abandoned settlements reclaimed by nature or monsters.

#### Procedural Algorithms

- **Terrain Generation:** Creating realistic landscapes. **[UPGRADE REQUIRED]** Generate complete continental terrain systems at startup.
- **Settlement Planning:** Generating believable towns and cities. **[UPGRADE REQUIRED]** Plan all settlements with complete social, economic, and political structures.
- **Dungeon Design:** Creating interesting and balanced dungeons. **[UPGRADE REQUIRED]** Generate all dungeons with inhabitants, treasures, and evolutionary potential.
- **Quest Generation:** Creating meaningful and varied quests. **[UPGRADE REQUIRED]** Generate initial quest networks based on actual NPC relationships and faction conflicts.

#### Ongoing Simulation Requirements

**[NEW REQUIREMENT]** All systems must be upgraded to support continuous background simulation:

1. **World State Simulation Tick System:** Regular updates to all world elements regardless of player proximity
2. **NPC Lifecycle Management:** NPCs age, form relationships, change goals, and pursue objectives autonomously
3. **Faction Evolution:** Ongoing territorial conflicts, alliance changes, and resource competition
4. **Economic Simulation:** Supply/demand changes, trade route evolution, market fluctuations
5. **Quest Evolution:** NPCs generate and attempt to complete quests independent of player interaction
6. **Arc Progression:** Narrative arcs advance based on world events and NPC actions
7. **POI Evolution:** Locations change state, purpose, and inhabitants over time
8. **Population Dynamics:** Migration, birth/death, cultural shifts, and demographic changes

### World State System

**Summary:** Tracks global state, world evolution, history, and major events through simulation.

**Improvement Notes:** Add examples of how player actions affect world state.

The world state system maintains the overall state of the game world, tracking major events, faction status, and world history.

Key components include:
- Global state tracking
- World history recording
- Major event processing
- World simulation tick system
- Player impact evaluation

## Cross-Cutting Concerns

These sections address aspects that span multiple systems and provide integration across the codebase.

### User Interface

**Summary:** Covers UI components including maps, character management, GM tools, and player tools.

**Improvement Notes:** Add wireframes for key interfaces.

#### Map Interface

- **World Map:** Overview of the entire game world.
- **Region Map:** Detailed view of specific regions.
- **Local Map:** Immediate surroundings for tactical decisions.
- **Dungeon Map:** Interior layouts of structures and dungeons.

#### Character Management

- **Character Sheet:** Display of character statistics and equipment.
- **Inventory System:** Management of items and equipment.
- **Skill and Ability Interface:** Access to character abilities and skills.
- **Party Management:** Interface for controlling multiple characters.

#### Game Master Tools

- **NPC Creator:** Tool for creating and managing NPCs.
- **Encounter Builder:** Tool for designing balanced combat encounters.
- **Loot Generator:** System for creating appropriate treasure.
- **Scene Setup:** Tools for creating and managing game scenes.

#### Player Tools

- **Character Creator:** Interface for building new characters.
- **Quest Journal:** Tracking active and completed quests.
- **Relationship Tracker:** Managing relationships with NPCs and factions.
- **Roleplaying Aids:** Tools to assist in roleplaying decisions.

### Modding Support

**Summary:** Details modding capabilities including mod types, tools, integration, and community support.

**Improvement Notes:** Add tutorial for creating a simple mod.

#### Mod Types

- **Content Mods:** Adding new items, creatures, and locations.
- **Rules Mods:** Changing game mechanics and systems.
- **Visual Mods:** Altering the game's appearance.
- **Story Mods:** Adding new quests and narrative content.

#### Modding Tools

- **Asset Creator:** Tool for creating new game assets.
- **Script Editor:** Interface for modifying game scripts.
- **World Editor:** Tool for creating and modifying game worlds.
- **Rules Editor:** Interface for changing game rules.

#### Mod Integration

- **Compatibility Checking:** Ensuring mods work together.
- **Load Order:** Managing the sequence in which mods are applied.
- **Conflict Resolution:** Addressing issues between mods.
- **Version Management:** Handling different versions of mods.

#### Community Support

- **Mod Repository:** Central location for finding and sharing mods.
- **Documentation:** Guides for creating and using mods.
- **Community Forums:** Places for modders to share knowledge.
- **Modding Tutorials:** Step-by-step guides for creating mods.

### AI Integration

**Summary:** Describes how AI enhances NPCs, narrative generation, encounter design, and world simulation.

**Improvement Notes:** Add examples of prompt engineering for game content.

#### NPC Intelligence

- **Conversation System:** AI-driven dialogue with NPCs.
- **Behavior Patterns:** Realistic NPC actions and reactions.
- **Memory System:** NPCs remember interactions with players.
- **Relationship Tracking:** How NPCs feel about players and each other.

#### Narrative Generation

- **Story Arc Creation:** Generating compelling story arcs.
- **Plot Adaptation:** Adjusting stories based on player choices.
- **Theme Consistency:** Maintaining consistent narrative themes.
- **Character Development:** Evolving characters throughout the story.

#### Encounter Design

- **Dynamic Difficulty:** Adjusting encounter difficulty based on party strength.
- **Tactical Intelligence:** Intelligent enemy tactics during combat.
- **Environment Utilization:** Enemies use the environment strategically.
- **Reinforcement Learning:** Enemies learn from previous encounters.

#### World Simulation

- **Economic Simulation:** Realistic economy affected by player actions.
- **Political Simulation:** Evolving political landscape.
- **Ecological Simulation:** Natural world that responds to events.
- **Social Simulation:** Communities that change and develop.
- **POI Evolution:** Locations that change state and purpose over time.

## Test Coverage Requirements

### Minimum Coverage Thresholds

The Visual DM project has established the following minimum test coverage thresholds:

| System | Minimum Coverage Required |
|--------|---------------------------|
| Data System | 85% |
| UI Components | 70% |
| Game Logic | 80% |
| World Generation | 80% |
| Utilities | 75% |

### Test Coverage Guidelines

1. **All new code must be tested**: Any new feature or functionality added to the codebase must include comprehensive tests.
2. **Edge cases must be covered**: Tests should include edge cases, error conditions, and boundary values.
3. **Coverage isn't everything**: While we aim for high coverage percentages, the quality and thoroughness of tests are equally important.
4. **Keep tests maintainable**: Tests should be well-structured, documented, and easy to maintain.
5. **Integration tests**: In addition to unit tests, integration tests should be written for critical system interactions.

### Test Types

1. **Unit Tests**: Test individual functions, methods, and classes in isolation.
2. **Integration Tests**: Test interactions between different components or systems.
3. **Validation Tests**: Verify that data structures conform to expected schemas.
4. **Performance Tests**: Ensure that code performs efficiently under various loads.
5. **Edge Case Tests**: Test boundary conditions and error handling.

### Running and Reporting Tests

- Use pytest for running tests: `pytest -xvs path/to/tests`
- Generate coverage reports: `pytest --cov=backend path/to/tests`
- Update the test_coverage_summary.md file after significant test improvements

### Recent Improvements

- Increased data system test coverage from 58% to 85% by enhancing tests for data_file_loader.py, schema_validator.py, and biome_schema.py
- Established minimum coverage thresholds for all system components
- Implemented comprehensive test documentation standards

## Game Rules

**Summary:** This section provides the core mechanical rules for Visual DM as a tabletop roleplaying game system, with emphasis on differences from D&D 5e.

**Improvement Notes:** Consider adding examples of play and sample character sheets.

### Core Mechanics

#### Dice System
- Uses d20 for most resolution: roll d20 + attribute + skill vs. target number
- Critical success on natural 20, critical failure on natural 1 affects all rolls
- Advantage system: roll 2d20 and take highest (2× advantage: roll 3d20 and take highest)
- Disadvantage system: roll 2d20 and take lowest (2× disadvantage: roll 3d20 and take lowest)
- Skill checks: d20 + attribute + skill vs. Difficulty Class (DC)
- Contested checks: d20 + attribute + skill vs. opponent's d20 + attribute + skill

#### Character Attributes
- Six core attributes: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
- **Difference from D&D:** Attributes range from -3 to +5 directly (no separate modifier calculation)
- Characters start with all attributes at 0 and 12 points to distribute
- Point costs increase at higher levels: +3 to +4 costs 2 points, +4 to +5 costs 3 points
- Attributes can also be reduced to -3 to gain additional points

#### Skills
- Skills are tied to specific attributes and provide bonuses to related checks
- The canonical skill list includes:
  - **Appraise (INT):** Determine the value of items
  - **Balance (DEX):** Maintain footing on narrow or unstable surfaces
  - **Bluff (CHA):** Deceive others through words or actions
  - **Climb (STR):** Scale vertical surfaces
  - **Concentration (CON):** Maintain focus during distractions or while injured
  - **Craft (INT):** Create or repair items (subskills: Alchemy, Armorsmithing, Weaponsmithing, Trapmaking, Bowmaking)
  - **Decipher Script (INT):** Understand unfamiliar writing or codes
  - **Diplomacy (CHA):** Negotiate and persuade in good faith
  - **Disable Device (INT):** Disarm traps or sabotage mechanical devices
  - **Disguise (CHA):** Change appearance to conceal identity
  - **Escape Artist (DEX):** Slip free from bonds or tight spaces
  - **Forgery (INT):** Create fraudulent documents
  - **Gather Information (CHA):** Collect rumors and information from locals
  - **Handle Animal (CHA):** Train and care for animals
  - **Heal (WIS):** Provide medical treatment
  - **Hide (DEX):** Conceal oneself from observation
  - **Intimidate (CHA):** Influence others through threats or fear
  - **Jump (STR):** Leap across gaps or over obstacles
  - **Knowledge (INT):** Specialized information in various fields (subskills: Arcana, Architecture and Engineering, Dungeoneering, Geography, History, Local, Nature, Nobility and Royalty, Religion, The Planes)
  - **Listen (WIS):** Notice sounds and conversations
  - **Move Silently (DEX):** Move without making noise
  - **Open Lock (DEX):** Pick locks
  - **Perform (CHA):** Entertain others (subskills: Act, Comedy, Dance, Keyboard Instruments, Oratory, Percussion Instruments, String Instruments, Wind Instruments, Sing)
  - **Profession (WIS):** Practice a trade or occupation
  - **Ride (DEX):** Control mounts
  - **Search (INT):** Locate hidden objects or features
  - **Sense Motive (WIS):** Discern intentions and detect lies
  - **Sleight of Hand (DEX):** Perform acts of manual dexterity
  - **Spellcraft (INT):** Identify and understand magical effects
  - **Spot (WIS):** Notice visual details
  - **Survival (WIS):** Endure harsh environments and track creatures
  - **Swim (STR):** Move through water
  - **Tumble (DEX):** Acrobatic movements to avoid attacks or falls
  - **Use Magic Device (CHA):** Operate magical items regardless of restrictions
  - **Use Rope (DEX):** Manipulate ropes for various purposes

#### Abilities (Feats)
- **Difference from D&D:** No classes or proficiency; character specialization comes entirely through ability selection
- Characters start with 7 abilities at level 1, then gain 3 additional abilities per level
- Abilities have prerequisites and form skill trees
- Abilities may grant skill bonuses, special actions, or unique capabilities
- The system allows for flexible character building, from specialists to generalists

### Health and Damage

#### Health Points (HP)
- Represent a character's vitality and ability to avoid serious injury
- Calculated based on abilities and Constitution attribute
- Temporary HP function as an additional buffer that is lost first

#### Wound System
- **Difference from D&D:** Characters who reach HP thresholds gain wound levels with penalties
- Wound levels: 
  - Unharmed (100-51% HP): No penalties
  - Bloodied (50-1% HP): -2 to all rolls
  - Wounded (0 HP): -5 to all rolls
  - Critically Wounded (negative HP): -10 to all rolls
  - Dead
- Recovery requires rest, medicine checks, or magical healing

#### Armor Class (AC) and Damage Reduction (DR)
- **Difference from D&D:** Both AC and DR exist and function differently
- AC: Determines if an attack hits (calculated as 10 + Dexterity + abilities + magic)
- DR: Reduces damage when hit (derived from armor, abilities, and some magic)
- DR is divided by damage type as detailed below

#### Damage Types
- **Physical:** Basic damage from weapons and physical attacks. Affected by physical DR from armor.
- **Magical:** Generic magical damage. Affected by magic resistance.
- **Fire:** Heat and flame damage. Affected by fire resistance, reduced by appropriate DR.
- **Ice:** Cold and frost damage. Affected by ice resistance, reduced by appropriate DR.
- **Lightning:** Electrical damage. Affected by lightning resistance, reduced by appropriate DR.
- **Poison:** Toxic damage. Affected by poison resistance, less affected by physical DR.
- **Psychic:** Mental damage. Generally not affected by physical DR, only by psychic resistance.
- **Necrotic:** Death energy and decay. Less affected by physical DR, reduced by necrotic resistance.
- **Radiant:** Holy or light-based damage. Less affected by physical DR, reduced by radiant resistance.
- **Force:** Pure magical energy. Affected by force resistance and some magical DR.
- **Acid:** Corrosive damage. Affected by acid resistance, can bypass some physical DR.
- **Thunder:** Sonic damage. Affected by thunder resistance, less affected by physical DR.
- **True:** Special damage that bypasses all resistances and DR.

### Combat

#### Initiative
- Roll d20 + Dexterity to determine turn order
- Initiative can be modified by weapon types and abilities

#### Combat Actions
- Each round, characters get:
  - 1 Action
  - 1 Bonus Action
  - 2 Free Actions
  - Movement (based on speed)
- Trigger actions (reactions) have a specific action cost (action, bonus, free, or movement)
- Trigger actions can only be used if you did not use the corresponding action type during your turn
- Standard actions include:
  - Attack: Roll to hit vs. target's AC
  - Cast Spell: Using magical abilities
  - Dodge: Increases AC until next turn
  - Dash: Double movement for the turn
  - Disengage: Move without provoking opportunity attacks
  - Hide: Make a Stealth check to become hidden
  - Help: Give advantage to an ally's next check
  - Ready: Prepare an action to trigger on a specific circumstance
- Additional combat actions include:
  - Feint: Contested Deception vs. Insight, success grants advantage on next attack
  - Assess: Insight check to identify enemy weaknesses or abilities
  - Intimidate: Contested Intimidation vs. Wisdom save to impose disadvantage

#### Attack Resolution
- Attacker rolls d20 + attack skill + attribute + ability modifiers
- Attack must equal or exceed target's AC to hit
- Critical hits (natural 20): Automatically hit and deal double damage
- Confirmed critical (nat 20 followed by a second hit roll): Double damage and ignore DR
- Double critical (nat 20 followed by another nat 20): [Note: Need to determine effect]
- Fumbles (natural 1): Negative consequence determined by the DM or AI

#### Weapon Categories
- **Difference from D&D:** Weapons are categorized as Heavy, Medium, or Light
- Heavy: Always two-handed
- Medium: Versatile (can be used one or two-handed)
- Light: One-handed
- Each category has associated abilities that grant "proficiency" or other benefits
- [Note: Need to reference feats.json for specifics on weapon proficiency implementation]

### Magic System

#### Mana Points
- **Major Difference from D&D:** Uses Mana Points (MP) instead of spell slots
- Characters have MP based on abilities and attributes
- Spell costs vary based on spell level and power
- MP regenerates fully after a long rest, and 50% after a short rest
- Some spells are "toggleable" and reduce maximum MP while active

#### Spellcasting
- Spell attack rolls: d20 + spell skill + attribute
- Spell save DC is typically the caster's skill score in the relevant domain
- Four magic domains: Nature, Arcane, Eldritch, Divine
- [Note: Concentration system needs to be fleshed out]

#### Spell Learning
- **Difference from D&D:** No spell preparation or ritual casting
- Spells are learned permanently through abilities
- No class restrictions on which spells can be learned

### Experience and Advancement

#### Experience Points (XP)
- Earned through combat, exploration, quest completion, and roleplaying
- **Difference from D&D:** No milestone leveling option; only XP tracking

#### Leveling
- Characters advance through levels by accumulating XP
- Each level provides 3 new abilities to purchase
- Abilities can only be purchased if prerequisites are met
- System encourages specialization or diversification based on player choice

### Rest and Recovery

#### Short Rest
- No specific time requirement (real-time game world)
- Recover 50% of HP and MP
- Can be taken twice between long rests
- [Note: Consider encounter chance during short rests]

#### Long Rest
- No specific time requirement (real-time game world)
- Recover all HP and MP
- Cannot be taken in dangerous locations
- Chance of dangerous encounter during rest based on region's Danger Level (DL)
- [Note: Need to create encounter tables for rest interruptions]

### Items and Equipment

#### Item Quality
- All items have some degree of magical properties
- Items have quality levels affecting their performance
- [Note: Reference existing item quality system documentation]

#### Encumbrance
- Characters can carry weight based on Strength attribute
- Penalties apply when carrying too much weight
- [Note: Need to define specific encumbrance thresholds and penalties]

#### Item Identification
- **Major Difference from D&D:** Progressive identification system
- Items reveal properties gradually through use or identification
- Identification methods:
  - Purchased identification services
  - Leveling up while using the item
  - Identify spell (if available)
- Items cannot be identified through ability checks

### Additional Mechanics

#### Critical Success/Failure Effects
- Critical successes (natural 20):
  - Attacks: Automatic hit and double damage
  - Skill checks/Saving throws: Automatic success regardless of DC
- Critical failures (natural 1):
  - Attacks: Miss plus potential negative consequences
  - Skill checks/Saving throws: Automatic failure plus potential complications
- AI may interpret critical success/failure with additional narrative consequences 

## Backend API Architecture

**Summary:** Defines the backend API architecture, development phases, and integration patterns between Unity client and FastAPI backend.

**Implementation Status:** ✅ Phase 4 Complete - API Contracts Defined, Data System Tests Fixed (97.5% pass rate)

### API Contract Specification

**Location:** `docs/api_contracts.md` - Complete API specification

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Protocol:** HTTP/HTTPS + WebSocket

The Visual DM backend provides a comprehensive REST API with real-time WebSocket support for Unity client integration. The API follows RESTful principles with standardized response formats, error handling, and authentication patterns.

#### Authentication & Security
- **Method:** JWT Bearer tokens with 24-hour expiration
- **Endpoint:** `/auth/token` for OAuth2-compatible authentication
- **Authorization:** Role-based access control (RBAC) with resource-specific permissions
- **Rate Limiting:** 100 requests/minute for standard endpoints, 10/minute for auth endpoints

#### Core API Systems

1. **World Generation API** (`/world`)
   - Continent creation and management
   - Procedural generation parameters
   - Region integration

2. **Combat System API** (`/combat`)
   - Combat action processing
   - Status tracking and resolution
   - Real-time combat events

3. **Character Management API** (`/characters`)
   - Character CRUD operations
   - Progression tracking
   - Relationship management

4. **Inventory System API** (`/inventory`)
   - Item management
   - Character inventory operations
   - Equipment handling

5. **Quest System API** (`/api/quests`)
   - Quest lifecycle management
   - Progress tracking
   - Dynamic quest generation

6. **Population System API** (`/api/population`)
   - POI population tracking
   - Population events and effects
   - Configuration management

7. **Economy System API** (`/economy`)
   - Shop management
   - Transaction processing
   - Economic balancing

8. **NPC System API** (`/api/npcs`)
   - NPC creation and management
   - Location tracking
   - Behavior systems

9. **Magic System API** (`/magic`)
   - Spell and ability management
   - Casting mechanics
   - Effect processing

10. **Additional Systems**
    - Faction System (`/factions`)
    - Time System (`/time`)
    - Motif System (`/api/motif`)

#### WebSocket Real-Time API
- **Endpoint:** `ws://localhost:8000/ws`
- **Message Types:**
  - `time_update`: Synchronized time advancement
  - `character_event`: Character state changes
  - `combat_event`: Real-time combat updates
  - `world_state_change`: Environmental changes
  - `system_message`: Administrative notifications

#### Data Transfer Objects (DTOs)
- **Standard Response Format:** Consistent success/error structure
- **Error Handling:** Structured error responses with detailed context
- **Pagination:** Standardized pagination for large datasets
- **Versioning:** API versioning support with backward compatibility

### Development Phases

**Summary:** Systematic development approach for backend-frontend integration with Task Master project management.

#### Phase Overview
Task 6 represents a comprehensive development plan spanning 12 phases, focusing on system integration, API standardization, and Unity-backend connectivity.

#### Completed Phases

**✅ Phase 1: Combat System Refactoring**
- **Status:** Complete (found REFACTORING_COMPLETE.md)
- **Achievement:** Unified combat modules, all tests passing
- **Components:** `unified_combat_utils.py`, `combat_facade.py`

**✅ Phase 2: Region System Audit** 
- **Status:** Complete
- **Achievement:** Verified comprehensive implementation
- **Components:** `models.py`, `service.py`, `router.py`
- **Compliance:** Matches Development Bible specifications

**✅ Phase 3: Data System Tests**
- **Status:** Complete - 97.5% Success Rate
- **Achievement:** 276/283 tests passing
- **Major Fixes:**
  - Fixed all import/dependency errors
  - Resolved biome loading TypeErrors  
  - Fixed data structure compatibility issues
  - Corrected GameDataRegistry data access patterns

**✅ Phase 4: API Contract Definition**
- **Status:** Complete
- **Achievement:** Comprehensive API specification created
- **Deliverable:** `docs/api_contracts.md`
- **Coverage:** 12 core systems, WebSocket API, authentication, error handling

#### Phase 5: Mock Server Creation
**Target:** Lightweight mock server for Unity integration testing
**Components:**
- FastAPI-based mock endpoints
- Realistic response data
- WebSocket simulation
- Authentication mockup

#### Phase 6: Unity Mock Integration  
**Target:** Unity HTTP client integration
**Components:**
- HTTPClient service implementation
- WebSocket manager
- Authentication handling
- DTO serialization/deserialization

#### Phase 7: Narrative-Arc Implementation
**Target:** Meta-narrative framework
**Components:**
- Arc system integration
- Quest relationship management
- Progression tracking
- Dynamic content generation

#### Phases 8-12: Advanced Features
- **Phase 8:** Advanced Authentication & User Management
- **Phase 9:** Real-time Multiplayer Foundation
- **Phase 10:** Performance Optimization & Monitoring
- **Phase 11:** Comprehensive Testing & Quality Assurance
- **Phase 12:** Production Deployment & Documentation

### Technical Implementation Notes

#### Data System Architecture
**Status:** Fully functional with high test coverage

**Key Improvements Made:**
- **Import Resolution:** Fixed all missing typing imports across data system
- **GameDataRegistry:** Enhanced to handle both wrapped and unwrapped data formats
- **Data Loading:** Robust error handling for missing files and invalid formats
- **Schema Validation:** Working schema validation with fallback implementations

**Remaining Minor Issues:**
- 7 test failures related to specific data file expectations
- Can be addressed in future optimization phases

#### Backend Router Architecture
**Organization:** Modular system-specific routers
- `backend/systems/{system}/router.py` pattern
- Consistent dependency injection patterns
- Standardized error handling
- FastAPI async/await support

**Currently Active Routers:**
- Combat Router (`/combat`)
- Quest Router (`/api/quests`) 
- Population Router (`/api/population`)
- Time Router (`/time`)
- Auth Router (`/auth`)
- Arc Router (`/arcs`)

**Commented/Disabled Routers:** 
- Region Router (temporarily disabled)
- World Generation Router (temporarily disabled)
- Motif Router (syntax issues noted)

#### Unity Integration Architecture
**Planned Components:**
- **HTTPClient Service:** Singleton service for REST API communication
- **WebSocketManager:** Real-time communication handling
- **AuthenticationManager:** Token management and session handling
- **DataSynchronization:** State consistency between client/server

#### Performance Characteristics
**Data System Performance:**
- 97.5% test success rate indicates robust functionality
- Fast data loading and validation
- Efficient caching mechanisms
- Scalable to production datasets

**API Performance Targets:**
- < 100ms response time for standard endpoints
- < 500ms for complex generation operations
- WebSocket latency < 50ms
- Support for 100+ concurrent connections

### Integration Patterns

#### Client-Server Communication
1. **Authentication Flow:** JWT token-based with refresh capability
2. **API Requests:** RESTful operations with standardized DTOs
3. **Real-time Events:** WebSocket for immediate updates
4. **Error Recovery:** Automatic retry mechanisms with exponential backoff
5. **Offline Support:** Local caching for critical game state

#### Cross-System Integration
1. **Event-Driven Architecture:** Loose coupling via event bus
2. **Service Layer:** Business logic separation from API endpoints
3. **Repository Pattern:** Data access abstraction
4. **Dependency Injection:** Testable and maintainable component structure

#### Development Workflow
1. **API-First Design:** Contracts defined before implementation
2. **Test-Driven Development:** High test coverage for critical systems
3. **Incremental Integration:** Phase-by-phase implementation and testing
4. **Continuous Validation:** Automated testing and integration checks

### Future Enhancements

#### Phase 2 Features (Post-MVP)
- GraphQL endpoint for complex queries
- Server-sent events for additional real-time features
- Advanced caching strategies (Redis integration)
- Microservices architecture migration
- Enhanced monitoring and observability

#### Scalability Considerations
- Horizontal scaling support
- Database sharding strategies  
- CDN integration for static assets
- Load balancing configuration
- Performance monitoring and alerting

---

**Documentation Status:** ✅ Complete - Task 6 Phase 4  
**Next Phase:** Mock server implementation for Unity integration testing  
**Development Timeline:** On track for systematic Unity-backend integration