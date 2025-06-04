# Visual DM Database Schema Documentation

## Overview

Visual DM uses PostgreSQL as its primary database with SQLAlchemy ORM for data management. The database follows a clean architecture pattern with clear separation between business logic entities (systems) and infrastructure components.

## Database Configuration

### Connection Configuration
- **Database Engine**: PostgreSQL 13+
- **Connection Pool**: QueuePool with 5 base connections, 10 max overflow
- **Connection Timeout**: 30 seconds
- **Connection Recycle**: 1800 seconds (30 minutes)
- **Async Support**: asyncpg driver for async operations

```python
# Configuration from backend/infrastructure/database/database.py
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/visualdm"
DATABASE_URL_async = "postgresql+asyncpg://postgres:postgres@localhost:5432/visualdm"
```

### Performance Optimizations
- **Connection Pooling**: Configured for optimal concurrent access
- **JSONB Indexing**: GIN indexes on all JSONB columns for fast queries
- **UUID Performance**: Uses gen_random_uuid() for better performance than uuid_generate_v4()
- **Partial Indexes**: Created on frequently queried status and type fields
- **Query Optimization**: Prepared statements and query plan caching enabled

## Base Model Architecture

### SharedBaseModel (Pydantic)
All system models inherit from `SharedBaseModel` providing:
- **id**: UUID primary key with auto-generation
- **created_at**: Automatic timestamp on creation
- **updated_at**: Automatic timestamp on modification
- **is_active**: Soft delete flag
- **metadata**: JSONB field for extensible properties

### BaseModel (SQLAlchemy)
All database entities inherit from `BaseModel` providing:
- **id**: Integer or UUID primary key
- **created_at**: DateTime with UTC default
- **updated_at**: DateTime with automatic update
- **__tablename__**: Auto-generated from class name

## Entity Relationship Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   World Data    │    │ Character Data  │    │ Economic Data   │
│                 │    │                 │    │                 │
│ • Regions       │◄──►│ • Characters    │◄──►│ • Markets       │
│ • POIs          │    │ • NPCs          │    │ • Trades        │
│ • Hexes         │    │ • Relationships │    │ • Transactions  │
│ • World State   │    │ • Factions      │    │ • Resources     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│ Event/Quest Data│◄─────────────┘
                        │                 │
                        │ • Quests        │
                        │ • Events        │
                        │ • History       │
                        │ • Consequences  │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │Inventory/Equip  │
                        │                 │
                        │ • Items         │
                        │ • Equipment     │
                        │ • Inventories   │
                        │ • Loot Tables   │
                        └─────────────────┘
```

## Core System Entities

### 1. World Data Schema

#### Regional System Tables

```sql
-- Regions table
CREATE TABLE region_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    coordinates JSONB NOT NULL, -- {"x": 0, "y": 0, "z": 0}
    biome_type VARCHAR(100) NOT NULL,
    climate_data JSONB DEFAULT '{}', -- temperature, precipitation, seasons
    resource_abundance JSONB DEFAULT '{}', -- available resources and quantities
    political_control UUID REFERENCES faction_entities(id),
    population_density INTEGER DEFAULT 0 CHECK (population_density >= 0),
    development_level VARCHAR(50) DEFAULT 'wilderness',
    trade_routes JSONB DEFAULT '[]', -- array of connected region IDs
    danger_level INTEGER DEFAULT 1 CHECK (danger_level >= 1 AND danger_level <= 10),
    magical_aura VARCHAR(50) DEFAULT 'normal', -- dead, weak, normal, strong, wild
    travel_time_modifiers JSONB DEFAULT '{}', -- movement speed adjustments
    regional_events JSONB DEFAULT '[]', -- active regional events
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for regions
CREATE INDEX idx_region_coordinates ON region_entities USING GIN (coordinates);
CREATE INDEX idx_region_biome ON region_entities (biome_type);
CREATE INDEX idx_region_political ON region_entities (political_control);
CREATE INDEX idx_region_status ON region_entities (status) WHERE status = 'active';

-- POI (Points of Interest) table
CREATE TABLE poi_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    poi_type VARCHAR(100) NOT NULL, -- temple, dungeon, city, settlement, landmark
    region_id UUID NOT NULL REFERENCES region_entities(id) ON DELETE CASCADE,
    coordinates JSONB NOT NULL, -- exact position within region
    size_category VARCHAR(50) DEFAULT 'medium', -- tiny, small, medium, large, huge
    accessibility VARCHAR(50) DEFAULT 'normal', -- easy, normal, difficult, impossible
    danger_level INTEGER DEFAULT 1 CHECK (danger_level >= 1 AND danger_level <= 10),
    discovery_difficulty INTEGER DEFAULT 5 CHECK (discovery_difficulty >= 1 AND discovery_difficulty <= 10),
    current_state JSONB DEFAULT '{}', -- dynamic state information
    history JSONB DEFAULT '[]', -- historical events and changes
    inhabitants JSONB DEFAULT '[]', -- current inhabitants/occupants
    resources JSONB DEFAULT '{}', -- available loot, materials
    connections JSONB DEFAULT '[]', -- connected POIs, secret passages
    services JSONB DEFAULT '{}', -- available services (shops, inns, etc.)
    defenses JSONB DEFAULT '{}', -- fortifications, guards, magical protections
    reputation JSONB DEFAULT '{}', -- reputation by faction
    economic_data JSONB DEFAULT '{}', -- wealth level, trade importance
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for POIs
CREATE INDEX idx_poi_region ON poi_entities (region_id);
CREATE INDEX idx_poi_type ON poi_entities (poi_type);
CREATE INDEX idx_poi_coordinates ON poi_entities USING GIN (coordinates);
CREATE INDEX idx_poi_danger ON poi_entities (danger_level);

-- Hexes table (detailed world grid)
CREATE TABLE hex_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES region_entities(id) ON DELETE CASCADE,
    hex_coordinates JSONB NOT NULL, -- {"q": 0, "r": 0, "s": 0} (cube coordinates)
    terrain_type VARCHAR(100) NOT NULL,
    elevation INTEGER DEFAULT 0,
    water_presence BOOLEAN DEFAULT FALSE,
    vegetation_density REAL DEFAULT 0.0 CHECK (vegetation_density >= 0.0 AND vegetation_density <= 1.0),
    resource_nodes JSONB DEFAULT '[]', -- specific resource locations
    travel_difficulty REAL DEFAULT 1.0 CHECK (travel_difficulty >= 0.1),
    visibility REAL DEFAULT 1.0 CHECK (visibility >= 0.0 AND visibility <= 1.0),
    special_features JSONB DEFAULT '[]', -- unique terrain features
    weather_modifiers JSONB DEFAULT '{}', -- local weather effects
    exploration_status VARCHAR(50) DEFAULT 'unexplored', -- unexplored, scouted, mapped, settled
    last_visited TIMESTAMP,
    encounter_probability REAL DEFAULT 0.1 CHECK (encounter_probability >= 0.0 AND encounter_probability <= 1.0),
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Constraint to ensure valid cube coordinates (q + r + s = 0)
    CONSTRAINT valid_cube_coordinates CHECK (
        (hex_coordinates->>'q')::int + (hex_coordinates->>'r')::int + (hex_coordinates->>'s')::int = 0
    )
);

-- Indexes for hexes
CREATE INDEX idx_hex_region ON hex_entities (region_id);
CREATE INDEX idx_hex_coordinates ON hex_entities USING GIN (hex_coordinates);
CREATE INDEX idx_hex_terrain ON hex_entities (terrain_type);
CREATE UNIQUE INDEX idx_hex_unique_coords ON hex_entities (region_id, ((hex_coordinates->>'q')::int), ((hex_coordinates->>'r')::int));
```

#### World State Management

```sql
-- World State table
CREATE TABLE world_state_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    world_name VARCHAR(255) NOT NULL,
    current_date JSONB NOT NULL, -- {"year": 1492, "month": 3, "day": 15, "hour": 14, "minute": 30}
    global_events JSONB DEFAULT '[]', -- active world-wide events
    political_landscape JSONB DEFAULT '{}', -- faction relationships, wars, alliances
    economic_conditions JSONB DEFAULT '{}', -- global trade status, currency values
    magical_phenomena JSONB DEFAULT '{}', -- active magical effects, dead magic zones
    weather_patterns JSONB DEFAULT '{}', -- seasonal weather, climate changes
    cosmic_events JSONB DEFAULT '[]', -- eclipses, meteor showers, planar alignments
    session_metadata JSONB DEFAULT '{}', -- current session information
    player_actions_history JSONB DEFAULT '[]', -- significant player decisions and consequences
    world_version INTEGER DEFAULT 1, -- for tracking major world changes
    last_major_event TIMESTAMP,
    chaos_level INTEGER DEFAULT 0 CHECK (chaos_level >= 0 AND chaos_level <= 100),
    stability_index REAL DEFAULT 1.0 CHECK (stability_index >= 0.0),
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for world state
CREATE INDEX idx_world_name ON world_state_entities (world_name);
CREATE INDEX idx_world_date ON world_state_entities USING GIN (current_date);
CREATE INDEX idx_world_chaos ON world_state_entities (chaos_level);
```

### 2. Character Data Schema

#### Character System Tables

```sql
-- Character base table
CREATE TABLE character_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    character_type VARCHAR(50) NOT NULL, -- pc, npc, monster, familiar, mount
    description TEXT,
    background_story TEXT,
    current_location UUID, -- could reference region_entities or poi_entities
    home_region UUID REFERENCES region_entities(id),
    
    -- Core Attributes (Visual DM uses direct attribute assignment from -3 to +5)
    stats JSONB DEFAULT '{}', -- {"STR": 0, "DEX": 0, "CON": 0, "INT": 0, "WIS": 0, "CHA": 0}
    skills JSONB DEFAULT '{}', -- skill proficiencies and bonuses: {"skill_name": {"proficient": true, "expertise": false, "bonus": 0}}
    level INTEGER DEFAULT 1 CHECK (level >= 1 AND level <= 20),
    experience_points INTEGER DEFAULT 0 CHECK (experience_points >= 0),
    hit_points_current INTEGER DEFAULT 1,
    hit_points_maximum INTEGER DEFAULT 1,
    armor_class INTEGER DEFAULT 10,
    
    -- Character Identity
    race VARCHAR(100),
    background VARCHAR(100),
    languages JSONB DEFAULT '[]', -- array of known languages
    proficiencies JSONB DEFAULT '{}', -- tools, weapons, armor
    
    -- Hidden Personality Attributes (0-6 scale, not directly choosable by players)
    hidden_personality JSONB DEFAULT '{}', -- {"ambition": 3, "integrity": 4, "discipline": 2, "impulsivity": 5, "pragmatism": 3, "resilience": 4}
    
    -- Relationships
    faction_memberships JSONB DEFAULT '[]', -- array of {faction_id, rank, standing}
    relationships JSONB DEFAULT '{}', -- relationships with other characters
    reputation JSONB DEFAULT '{}', -- reputation scores by faction/region
    
    -- Current State
    current_status VARCHAR(50) DEFAULT 'alive', -- alive, unconscious, dead, missing, etc.
    conditions JSONB DEFAULT '[]', -- active conditions/effects
    resources JSONB DEFAULT '{}', -- spell slots, class resources, etc.
    
    -- Behavioral Data (for NPCs)
    personality_traits JSONB DEFAULT '[]',
    goals_and_motivations JSONB DEFAULT '[]',
    fears_and_flaws JSONB DEFAULT '[]',
    
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for characters
CREATE INDEX idx_character_type ON character_entities (character_type);
CREATE INDEX idx_character_location ON character_entities (current_location);
CREATE INDEX idx_character_home ON character_entities (home_region);
CREATE INDEX idx_character_level ON character_entities (level);
CREATE INDEX idx_character_status ON character_entities (current_status);
CREATE INDEX idx_character_name ON character_entities (name);

-- NPC-specific extended data
CREATE TABLE npc_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES character_entities(id) ON DELETE CASCADE,
    npc_type VARCHAR(100), -- merchant, guard, noble, commoner, artisan, etc.
    occupation VARCHAR(100),
    economic_status VARCHAR(50), -- destitute, poor, moderate, wealthy, noble
    social_connections JSONB DEFAULT '{}', -- family, friends, enemies, rivals
    secrets_and_rumors JSONB DEFAULT '[]', -- known secrets, rumors they spread
    dialogue_patterns JSONB DEFAULT '{}', -- speech patterns, favorite phrases
    daily_schedule JSONB DEFAULT '{}', -- routine activities and locations
    ai_behavior_profile JSONB DEFAULT '{}', -- AI behavioral parameters
    interaction_history JSONB DEFAULT '[]', -- history of player interactions
    quest_involvement JSONB DEFAULT '[]', -- quests this NPC is involved in
    merchant_data JSONB DEFAULT '{}', -- inventory, prices, trade routes (if merchant)
    combat_behavior JSONB DEFAULT '{}', -- tactics, preferred actions
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for NPCs
CREATE INDEX idx_npc_character ON npc_entities (character_id);
CREATE INDEX idx_npc_type ON npc_entities (npc_type);
CREATE INDEX idx_npc_occupation ON npc_entities (occupation);

-- Faction system
CREATE TABLE faction_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    faction_type VARCHAR(100), -- political, religious, mercantile, criminal, military
    alignment VARCHAR(50),
    headquarters_poi UUID REFERENCES poi_entities(id),
    controlled_regions JSONB DEFAULT '[]', -- array of region IDs
    influence_map JSONB DEFAULT '{}', -- influence by region
    leadership JSONB DEFAULT '{}', -- current leaders and structure
    goals JSONB DEFAULT '[]', -- faction goals and objectives
    resources JSONB DEFAULT '{}', -- wealth, military strength, etc.
    relationships JSONB DEFAULT '{}', -- relationships with other factions
    reputation JSONB DEFAULT '{}', -- reputation by region
    member_count INTEGER DEFAULT 0,
    power_level INTEGER DEFAULT 1 CHECK (power_level >= 1 AND power_level <= 10),
    secrecy_level INTEGER DEFAULT 1 CHECK (secrecy_level >= 1 AND secrecy_level <= 10),
    activity_level VARCHAR(50) DEFAULT 'moderate', -- dormant, low, moderate, high, frenzied
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for factions
CREATE INDEX idx_faction_type ON faction_entities (faction_type);
CREATE INDEX idx_faction_headquarters ON faction_entities (headquarters_poi);
CREATE INDEX idx_faction_power ON faction_entities (power_level);
CREATE INDEX idx_faction_name ON faction_entities (name);
```

### 3. Economic Data Schema

```sql
-- Market system
CREATE TABLE market_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    location_poi UUID NOT NULL REFERENCES poi_entities(id),
    market_type VARCHAR(100), -- general, specialized, black_market, auction_house
    size_category VARCHAR(50) DEFAULT 'medium', -- tiny, small, medium, large, huge
    operating_hours JSONB DEFAULT '{}', -- when the market is open
    trade_goods JSONB DEFAULT '[]', -- types of goods commonly traded
    price_modifiers JSONB DEFAULT '{}', -- price adjustments by item type
    reputation INTEGER DEFAULT 5 CHECK (reputation >= 1 AND reputation <= 10),
    security_level INTEGER DEFAULT 5 CHECK (security_level >= 1 AND security_level <= 10),
    tax_rate REAL DEFAULT 0.1 CHECK (tax_rate >= 0.0 AND tax_rate <= 1.0),
    currency_accepted JSONB DEFAULT '["gold", "silver", "copper"]',
    special_services JSONB DEFAULT '[]', -- enchanting, repairs, etc.
    market_events JSONB DEFAULT '[]', -- festivals, sales, shortages
    vendor_list JSONB DEFAULT '[]', -- list of vendor NPCs
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Trade transactions
CREATE TABLE trade_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    market_id UUID REFERENCES market_entities(id),
    buyer_id UUID REFERENCES character_entities(id),
    seller_id UUID REFERENCES character_entities(id),
    trade_type VARCHAR(50), -- purchase, sale, barter, auction
    items_traded JSONB NOT NULL, -- detailed item information
    currency_exchanged JSONB DEFAULT '{}', -- money involved
    trade_date JSONB NOT NULL, -- game world date
    trade_value DECIMAL(15,2) DEFAULT 0.00,
    tax_paid DECIMAL(15,2) DEFAULT 0.00,
    reputation_impact JSONB DEFAULT '{}', -- reputation changes
    trade_conditions JSONB DEFAULT '{}', -- special conditions or terms
    status VARCHAR(50) DEFAULT 'completed',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Economic transactions (broader than just trades)
CREATE TABLE transaction_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_type VARCHAR(100), -- trade, tax, tribute, theft, reward, etc.
    from_entity UUID, -- character, faction, or organization
    to_entity UUID,
    amount DECIMAL(15,2) NOT NULL,
    currency_type VARCHAR(50) DEFAULT 'gold',
    description TEXT,
    location_poi UUID REFERENCES poi_entities(id),
    transaction_date JSONB NOT NULL,
    related_quest UUID, -- if part of a quest
    related_event UUID, -- if part of an event
    economic_impact JSONB DEFAULT '{}', -- broader economic effects
    status VARCHAR(50) DEFAULT 'completed',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for economic data
CREATE INDEX idx_market_location ON market_entities (location_poi);
CREATE INDEX idx_market_type ON market_entities (market_type);
CREATE INDEX idx_trade_market ON trade_entities (market_id);
CREATE INDEX idx_trade_buyer ON trade_entities (buyer_id);
CREATE INDEX idx_trade_seller ON trade_entities (seller_id);
CREATE INDEX idx_trade_date ON trade_entities USING GIN (trade_date);
CREATE INDEX idx_transaction_type ON transaction_entities (transaction_type);
CREATE INDEX idx_transaction_from ON transaction_entities (from_entity);
CREATE INDEX idx_transaction_to ON transaction_entities (to_entity);
CREATE INDEX idx_transaction_date ON transaction_entities USING GIN (transaction_date);
```

### 4. Event and Quest Data Schema

```sql
-- Quest system
CREATE TABLE quest_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    quest_type VARCHAR(100), -- main, side, personal, faction, random
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 10),
    recommended_level INTEGER DEFAULT 1,
    quest_giver UUID REFERENCES character_entities(id),
    location_region UUID REFERENCES region_entities(id),
    location_poi UUID REFERENCES poi_entities(id),
    
    -- Quest Structure
    objectives JSONB DEFAULT '[]', -- list of quest objectives
    rewards JSONB DEFAULT '{}', -- experience, gold, items, reputation
    prerequisites JSONB DEFAULT '[]', -- required quests, levels, items
    time_limit JSONB DEFAULT '{}', -- deadline information
    
    -- Quest State
    current_status VARCHAR(50) DEFAULT 'available', -- available, active, completed, failed, abandoned
    progress JSONB DEFAULT '{}', -- progress on objectives
    participants JSONB DEFAULT '[]', -- characters involved
    completion_date JSONB,
    
    -- Quest Relationships
    parent_quest UUID REFERENCES quest_entities(id), -- for quest chains
    related_quests JSONB DEFAULT '[]', -- related or conflicting quests
    faction_involvement JSONB DEFAULT '{}', -- faction relationships affected
    
    -- Narrative Elements
    narrative_hooks JSONB DEFAULT '[]', -- story elements and motivations
    consequences JSONB DEFAULT '{}', -- world changes from completion
    failure_consequences JSONB DEFAULT '{}', -- what happens if failed
    
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Event system (broader than quests)
CREATE TABLE event_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(100), -- political, natural, magical, economic, social, combat
    scope VARCHAR(50), -- local, regional, global
    severity INTEGER DEFAULT 1 CHECK (severity >= 1 AND severity <= 10),
    
    -- Event Timing
    start_date JSONB NOT NULL,
    end_date JSONB,
    duration_type VARCHAR(50), -- instant, short, ongoing, permanent
    
    -- Event Location
    affected_regions JSONB DEFAULT '[]',
    affected_pois JSONB DEFAULT '[]',
    epicenter_location JSONB, -- specific coordinates if applicable
    
    -- Event Effects
    immediate_effects JSONB DEFAULT '{}', -- instant changes
    ongoing_effects JSONB DEFAULT '{}', -- continuous effects
    long_term_consequences JSONB DEFAULT '{}', -- permanent changes
    
    -- Event Participants
    instigators JSONB DEFAULT '[]', -- who/what caused this
    affected_characters JSONB DEFAULT '[]', -- characters directly affected
    affected_factions JSONB DEFAULT '[]', -- factions involved
    
    -- Event Resolution
    resolution_conditions JSONB DEFAULT '[]', -- how event can be resolved
    player_involvement JSONB DEFAULT '{}', -- how players can interact
    current_status VARCHAR(50) DEFAULT 'active', -- pending, active, resolved, failed
    
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Historical record system
CREATE TABLE history_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_name VARCHAR(255) NOT NULL,
    event_description TEXT,
    event_date JSONB NOT NULL,
    event_type VARCHAR(100),
    significance_level INTEGER DEFAULT 1 CHECK (significance_level >= 1 AND significance_level <= 10),
    
    -- Historical Context
    participants JSONB DEFAULT '[]', -- key figures involved
    locations JSONB DEFAULT '[]', -- where it happened
    causes JSONB DEFAULT '[]', -- what led to this event
    consequences JSONB DEFAULT '[]', -- what resulted from this event
    
    -- Documentation
    sources JSONB DEFAULT '[]', -- who recorded this information
    reliability INTEGER DEFAULT 5 CHECK (reliability >= 1 AND reliability <= 10),
    public_knowledge BOOLEAN DEFAULT TRUE, -- is this common knowledge
    
    -- Relationships
    related_events JSONB DEFAULT '[]', -- connected historical events
    related_quests JSONB DEFAULT '[]', -- quests that reference this
    related_characters JSONB DEFAULT '[]', -- characters connected to this
    
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for events and quests
CREATE INDEX idx_quest_type ON quest_entities (quest_type);
CREATE INDEX idx_quest_giver ON quest_entities (quest_giver);
CREATE INDEX idx_quest_status ON quest_entities (current_status);
CREATE INDEX idx_quest_location_region ON quest_entities (location_region);
CREATE INDEX idx_quest_location_poi ON quest_entities (location_poi);
CREATE INDEX idx_quest_difficulty ON quest_entities (difficulty_level);
CREATE INDEX idx_event_type ON event_entities (event_type);
CREATE INDEX idx_event_scope ON event_entities (scope);
CREATE INDEX idx_event_status ON event_entities (current_status);
CREATE INDEX idx_event_start_date ON event_entities USING GIN (start_date);
CREATE INDEX idx_history_date ON history_entities USING GIN (event_date);
CREATE INDEX idx_history_type ON history_entities (event_type);
CREATE INDEX idx_history_significance ON history_entities (significance_level);
```

### 5. Inventory and Equipment Schema

```sql
-- Item definitions
CREATE TABLE item_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    item_type VARCHAR(100), -- weapon, armor, consumable, tool, treasure, etc.
    item_subtype VARCHAR(100), -- sword, potion, ring, etc.
    rarity VARCHAR(50) DEFAULT 'common', -- common, uncommon, rare, very_rare, legendary, artifact
    
    -- Physical Properties
    weight DECIMAL(8,3) DEFAULT 0.0,
    size_category VARCHAR(50) DEFAULT 'medium',
    material JSONB DEFAULT '[]', -- materials used in construction
    durability INTEGER DEFAULT 100 CHECK (durability >= 0 AND durability <= 100),
    
    -- Economic Properties
    base_value DECIMAL(15,2) DEFAULT 0.00,
    market_availability VARCHAR(50) DEFAULT 'common', -- common, uncommon, rare, unique
    
    -- Mechanical Properties
    properties JSONB DEFAULT '{}', -- game mechanical properties
    requirements JSONB DEFAULT '{}', -- requirements to use
    effects JSONB DEFAULT '[]', -- magical or special effects
    
    -- Crafting Information
    crafting_recipe JSONB DEFAULT '{}', -- how to craft this item
    crafting_skill VARCHAR(100), -- required skill
    crafting_difficulty INTEGER DEFAULT 10,
    
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Individual item instances
CREATE TABLE item_instance_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES item_entities(id),
    owner_id UUID REFERENCES character_entities(id), -- null if not owned
    location_type VARCHAR(50), -- inventory, equipped, container, ground, market
    location_id UUID, -- specific location (container, market, etc.)
    
    -- Instance Properties
    quantity INTEGER DEFAULT 1 CHECK (quantity >= 0),
    current_durability INTEGER DEFAULT 100,
    enchantments JSONB DEFAULT '[]', -- applied enchantments
    modifications JSONB DEFAULT '[]', -- physical modifications
    history JSONB DEFAULT '[]', -- ownership and event history
    
    -- State Information
    identified BOOLEAN DEFAULT TRUE, -- has item been identified
    cursed BOOLEAN DEFAULT FALSE,
    attuned_to UUID REFERENCES character_entities(id), -- if requires attunement
    
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Equipment slots and loadouts
CREATE TABLE equipment_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES character_entities(id),
    equipment_slot VARCHAR(100), -- head, chest, legs, main_hand, off_hand, etc.
    item_instance_id UUID REFERENCES item_instance_entities(id),
    equipped_date JSONB,
    
    -- Equipment State
    is_equipped BOOLEAN DEFAULT TRUE,
    proficient BOOLEAN DEFAULT TRUE, -- is character proficient with this item
    
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Inventory containers
CREATE TABLE inventory_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES character_entities(id), -- null for location-based containers
    container_type VARCHAR(100), -- character, chest, bag, vault, etc.
    location_poi UUID REFERENCES poi_entities(id), -- if container is at a location
    
    -- Container Properties
    capacity_weight DECIMAL(10,3) DEFAULT 0.0, -- weight limit
    capacity_volume DECIMAL(10,3) DEFAULT 0.0, -- volume limit
    capacity_slots INTEGER DEFAULT 0, -- slot limit
    current_weight DECIMAL(10,3) DEFAULT 0.0,
    current_volume DECIMAL(10,3) DEFAULT 0.0,
    current_slots INTEGER DEFAULT 0,
    
    -- Access Control
    access_permissions JSONB DEFAULT '{}', -- who can access this container
    locked BOOLEAN DEFAULT FALSE,
    lock_difficulty INTEGER DEFAULT 10,
    
    status VARCHAR(50) DEFAULT 'active',
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes for inventory system
CREATE INDEX idx_item_type ON item_entities (item_type);
CREATE INDEX idx_item_rarity ON item_entities (rarity);
CREATE INDEX idx_item_name ON item_entities (name);
CREATE INDEX idx_item_instance_item ON item_instance_entities (item_id);
CREATE INDEX idx_item_instance_owner ON item_instance_entities (owner_id);
CREATE INDEX idx_item_instance_location ON item_instance_entities (location_type, location_id);
CREATE INDEX idx_equipment_character ON equipment_entities (character_id);
CREATE INDEX idx_equipment_slot ON equipment_entities (equipment_slot);
CREATE INDEX idx_equipment_equipped ON equipment_entities (is_equipped) WHERE is_equipped = TRUE;
CREATE INDEX idx_inventory_owner ON inventory_entities (owner_id);
CREATE INDEX idx_inventory_location ON inventory_entities (location_poi);
```

## Data Flow Patterns

### 1. Character Creation Flow
```
Player Input → Character Validation → Character Entity Creation → 
Initial Equipment Assignment → Starting Location Assignment → 
Faction Relationship Initialization → World State Update
```

### 2. Quest Progression Flow
```
Quest Trigger → Quest Availability Check → Quest Assignment → 
Objective Tracking → Progress Validation → Reward Distribution → 
World State Impact → History Recording
```

### 3. Economic Transaction Flow
```
Trade Initiation → Market Validation → Price Calculation → 
Inventory Transfer → Currency Exchange → Tax Processing → 
Reputation Update → Economic Impact Analysis
```

### 4. World Event Flow
```
Event Trigger → Scope Determination → Effect Calculation → 
Entity Impact Assessment → State Changes → Notification System → 
Consequence Propagation → Historical Recording
```

## Performance Optimization Strategies

### Indexing Strategy
- **Primary Indexes**: All UUID primary keys with B-tree indexes
- **Foreign Key Indexes**: All foreign key relationships indexed
- **JSONB Indexes**: GIN indexes on all JSONB columns for fast queries
- **Partial Indexes**: Status-based partial indexes for active records
- **Composite Indexes**: Multi-column indexes for common query patterns

### Query Optimization
- **Prepared Statements**: All queries use prepared statements
- **Connection Pooling**: Optimized pool sizes for concurrent access
- **Query Plan Caching**: Enabled for frequently executed queries
- **Batch Operations**: Bulk insert/update operations for large datasets

### Data Archival Strategy
- **Soft Deletes**: Use is_active flag instead of hard deletes
- **Historical Partitioning**: Partition large tables by date ranges
- **Archive Tables**: Move old data to separate archive tables
- **Compression**: Use PostgreSQL compression for archived data

## Security Considerations

### Data Protection
- **Encryption**: Sensitive data encrypted at rest
- **Access Control**: Row-level security for multi-tenant scenarios
- **Audit Logging**: All data changes logged with timestamps
- **Backup Security**: Encrypted backups with secure key management

### Performance Monitoring
- **Query Performance**: Track slow queries and optimization opportunities
- **Index Usage**: Monitor index effectiveness and unused indexes
- **Connection Health**: Monitor connection pool utilization
- **Data Growth**: Track table sizes and growth patterns

## Migration and Versioning

### Schema Versioning
- **Alembic Integration**: Database migrations managed through Alembic
- **Version Tracking**: Migration history tracked in dedicated table
- **Rollback Support**: All migrations include rollback procedures
- **Data Validation**: Post-migration data integrity checks

### Deployment Strategy
- **Blue-Green Deployments**: Zero-downtime schema updates
- **Gradual Rollouts**: Phased deployment of schema changes
- **Monitoring**: Real-time monitoring during migrations
- **Rollback Plans**: Automated rollback procedures for failed migrations