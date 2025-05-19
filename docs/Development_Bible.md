# Visual DM Development Bible

## System Overview
Visual DM is a narrative-driven game world simulation built on a modular, event-driven architecture. The system orchestrates multiple specialized subsystems through a central event dispatcher following a publish-subscribe pattern. Core mechanical systems—including memory, rumors, motifs, population control, and faction dynamics—are interconnected but maintain clear responsibility boundaries. The game emphasizes hidden mechanical systems that influence narrative elements without direct player visibility or manipulation. All systems prioritize extensibility, allowing for future additions like religion and diplomacy, while maintaining loose coupling through standardized event interfaces. Data persistence uses JSON storage with versioning, while the technical implementation leverages singleton pattern managers for centralized control of subsystem operations.

## Table of Contents
- [System Architecture](#system-architecture)
- [Events System](#events-system)
- [Analytics System](#analytics-system)
- [Memory System](#memory-system)
    - [Canonical Memory Type List](#canonical-memory-type-list)
    - [MemoryManager.cs Implementation](../VDM/Assets/Scripts/Systems/Memory/MemoryManager.cs)
- [Rumor System](#rumor-system)
- [World State System](#world-state-system)
- [Time System, Calendar, and Recurring Events](#time-system-calendar-and-recurring-events)
- [Population Control System](#population-control-system)
- [Motif System](#motif-system)
    - [Canonical Motif List](#canonical-motif-list)
    - [MotifManager.cs Implementation](../VDM/Assets/Scripts/Systems/Motif/MotifManager.cs)
- [Region System](#region-system)
- [POI System](#poi-system)
- [Faction System](#faction-system)
- [Tension and War System](#tension-and-war-system)
- [Arc and Quest System](#arc-and-quest-system)
- [Religion System](#religion-system)
- [Diplomacy System](#diplomacy-system)
- [Economy System](#economy-system)
- [Technical Implementation References](#technical-implementation-references)
- [Character Builder & Persistence Integration (2024)](#character-builder--persistence-integration-2024)
- [VDM Advanced Combat System](#vdm-advanced-combat-system)
- [World Generation & Geography Canonicalization](#world-generation--geography-canonicalization)
- [POI State Transition System](#poi-state-transition-system)
- [Character Relationship System (Canonical)](#character-relationship-system-canonical)
- [Storage System (2025 Update)](#storage-system-2025-update)
- [Backend WebSocket Integration (2025)](#backend-websocket-integration-2025)
- [Continent Generation (2025 Update)](#continent-generation-2025-update)
- [Modular Biome Adjacency, Coastline, and River Generation Systems](#modular-biome-adjacency-coastline-and-river-generation-systems)

## System Architecture

### Summary
The system architecture employs an Event Bus pattern with a central dispatcher for loose coupling between components. Key architectural decisions include using singleton manager classes, standardizing on typed events via Pydantic models, supporting both synchronous and asynchronous interfaces, and maintaining separation of concerns while allowing systems to influence each other through events. The architecture prioritizes extensibility for future systems like religion and diplomacy.

### Technical Implementation Decisions

**Q: What architecture should we use for implementing the central event dispatcher?**

**A:** The central event dispatcher will use an Event Bus pattern with a publish-subscribe model. This provides loose coupling between components and flexibility for future extensions. Key features of the implementation include:

1. A singleton `EventDispatcher` class that maintains subscriptions
2. Support for typed events via Pydantic BaseModel
3. Async event handling with prioritization
4. Middleware chain for logging, filtering, and other cross-cutting concerns
5. Both async and sync interfaces for various contexts
6. Thread-safe operation for concurrent event handling

The design allows for easy addition of new event types and subscribers without modifying existing code, following the Open/Closed Principle. Events are strongly typed for better maintainability and type safety.

**Q: Should there be a formal event bus/dispatcher?**

**A:** Prefer to have a dispatcher for custom event crafting/injection. Scaffold a central event dispatcher for narrative/mechanical events.

**Q: Should there be a central event bus/dispatcher for all narrative/mechanical events, or is the current event hook system sufficient?**

**A:** Either is fine. A central event bus could be added, but the current event hook system is sufficient for now. Use your best judgment.

**Q: Should there be a standardized way for new/future systems (e.g., economy, religion, diplomacy) to hook into memory/motif/arc logging?**

**A:** None of these need to hook *into* motifs, but motifs might influence them. Anywhere a GPT is called, motifs should probably be involved. Religion is not yet implemented but should be. For now, new systems do not hook directly into motifs/memory/arcs except via GPT context. If you want to add more hooks, that's fine. A central event bus/dispatcher is not required but could be added if needed.

**Q: Are there any planned future systems that will need reserved integration points?**

**A:** Diplomacy/politics and religion are planned but not yet implemented. More systems may be added in the future, so keep extensibility in mind.

## Events System

### Canonical Event Type List

| ID | Event Type         | Description                                      |
|----|--------------------|--------------------------------------------------|
| 1  | MemoryCreated      | A new memory is created for an entity            |
| 2  | MemoryReinforced   | An existing memory is reinforced                 |
| 3  | MemoryDeleted      | A memory is forgotten or removed                 |
| 4  | RumorSpread        | A rumor is spread to one or more entities        |
| 5  | MotifChanged       | The global or regional motif changes             |
| 6  | PopulationChanged  | Population metrics change for a POI              |
| 7  | POIStateChanged    | A POI changes state (e.g., city to ruins)        |
| 8  | FactionChanged     | Faction membership or reputation changes         |
| 9  | QuestUpdated       | Quest status or progress changes                 |
| 10 | CombatEvent        | Combat-related event (start, end, effect)        |
| 11 | TimeAdvanced       | In-game time advances (tick, day, etc.)          |
| 12 | EventLogged        | Generic event logged for analytics               |
| 13 | RelationshipChanged| Character relationship changes                   |
| 14 | StorageEvent       | Save/load, autosave, or checkpoint event         |
| 15 | WorldStateChanged  | World state variable changes                     |

### Events System Summary
The Events System implements a publish-subscribe event bus with middleware support. Events are strongly typed, dispatched via a singleton EventDispatcher, and support both sync and async handlers. Middleware enables logging, filtering, and analytics integration.

- **Event Types:** See canonical list above.
- **Dispatch:** Events are dispatched to all registered subscribers.
- **Middleware:** Middleware can intercept, log, or modify events.
- **Integration:** All major systems emit and subscribe to events for decoupled communication.

### Event Dispatching Pseudocode
```csharp
// Dispatching an event:
EventDispatcher.Instance.Dispatch(eventObj);

// EventDispatcher logic:
foreach (middleware in Middlewares)
    eventObj = middleware.Process(eventObj);
foreach (subscriber in Subscribers[eventObj.Type])
    subscriber.Handle(eventObj);
```

### Middleware Example
- Analytics middleware logs all events for LLM training.
- Filtering middleware blocks or modifies events as needed.

### Narrative Integration Example
- Narrative systems subscribe to MemoryCreated, RumorSpread, and MotifChanged events for context updates.

**See also:** [EventDispatcher.cs](../VDM/Assets/Scripts/Systems/Events/EventDispatcher.cs)

## Analytics System

### Canonical Analytics Event Type List

| ID | Analytics Event Type | Description                                      |
|----|---------------------|--------------------------------------------------|
| 1  | GameStart           | Game session begins                              |
| 2  | GameEnd             | Game session ends                                |
| 3  | MemoryEvent         | Memory created, reinforced, or deleted           |
| 4  | RumorEvent          | Rumor spread or mutated                          |
| 5  | MotifEvent          | Motif changes                                    |
| 6  | PopulationEvent     | Population metrics change                        |
| 7  | POIStateEvent       | POI state transitions                            |
| 8  | FactionEvent        | Faction membership or reputation changes         |
| 9  | QuestEvent          | Quest status or progress changes                 |
| 10 | CombatEvent         | Combat-related analytics                         |
| 11 | TimeEvent           | Time advances, calendar events                   |
| 12 | StorageEvent        | Save/load, autosave, or checkpoint analytics     |
| 13 | RelationshipEvent   | Character relationship analytics                 |
| 14 | WorldStateEvent     | World state variable analytics                   |
| 15 | CustomEvent         | Custom or user-defined analytics event           |

### Analytics System Summary
The Analytics System captures, stores, and processes game events for analysis and LLM training. It is implemented as a singleton AnalyticsService with event-driven architecture, structured event storage, and dataset generation capabilities.

- **Event Types:** See canonical list above.
- **Logging:** Events are logged to JSON files organized by date and category.
- **Dataset Generation:** Supports aggregation and filtering for LLM training datasets.
- **Integration:** Middleware hooks into the event dispatcher for non-intrusive analytics collection.

### Analytics Logging Pseudocode
```csharp
// On event received:
AnalyticsService.Instance.LogEvent(eventObj);

// AnalyticsService logic:
string filePath = GetFilePath(eventObj);
AppendEventToJsonFile(filePath, eventObj);

// Dataset generation:
var dataset = AnalyticsService.Instance.GenerateDataset(filter: byEventType, dateRange);
```

### Middleware Example
- Analytics middleware subscribes to all major events and logs them for analysis and LLM training.

### Dataset Generation Example
- Generate a dataset of all MemoryEvents in the last 30 days for LLM fine-tuning.

**See also:** [AnalyticsService.cs](../VDM/Assets/Scripts/Systems/Analytics/AnalyticsService.cs)

## Memory System

### Summary
The Memory System simulates entity-level memory with relevance scoring and decay mechanics. It uses a repository pattern to manage "core memories" (permanent) and regular memories (decaying over time), with JSON-based persistence organized by entity. Memories remain entity-local (never directly shared), can be categorized for analytics, and feature customizable GPT summarization for narrative generation. All memory mechanics remain hidden from player view.

**Q: How should we design the memory system for storing and retrieving entity memories?**

**A:** The memory system will be implemented using a repository pattern with relevance scoring and decay. Key features include:

1. A singleton `MemoryManager` class for central memory operations
2. `Memory` objects with metadata, categories, relevance scores
3. Support for "core memories" that don't decay over time
4. Contextual relationships between memories (memory graphs)
5. Event emission for memory operations via the event dispatcher
6. Persistence with JSON storage organized by entity
7. Memory decay mechanisms to simulate forgetting
8. Methods for generating memory summaries for LLM context

This design provides a scalable, flexible memory system that simulates realistic memory patterns while maintaining good performance and integration with other systems.

**Q: Are core memories shareable or transferrable?**

**A:** No. Core memories are always entity-local. Sharing only occurs via dialogue/GPT, not direct transfer.

**Q: Should certain memories be pinned for narrative importance?**

**A:** Leave to GPT/LLM logic; no explicit 'pinning' system.

**Q: Should core memories be categorized (e.g., "war", "politics", "arc", "catastrophe") for easier querying/analytics, or is this left to GPT/narrative logic?**

**A:** Might as well categorize them. "More is more." No strong opinion, but categories can be added for analytics.

**Q: Should GPT summarization be tunable (e.g., more/less detail, different narrative styles)?**

**A:** Yes. The plan is to build custom LLMs for this, possibly multiple models for different styles/levels of detail.

**Q: Should any of these systems (motifs, core memories, arc status) ever be partially visible to the player, or are they always fully hidden?**

**A:** They are always fully hidden. All are narrative-driven and not directly manipulable or visible to the player.

## Rumor System

### Canonical Rumor Type List

| ID | Rumor Type         | Description                                      |
|----|--------------------|--------------------------------------------------|
| 1  | Scandal            | Gossip about personal or political misdeeds      |
| 2  | Secret             | Hidden information, often with high stakes       |
| 3  | Prophecy           | Predictions about future events                  |
| 4  | Discovery          | News of new lands, resources, or inventions      |
| 5  | Catastrophe        | Warnings of disaster, war, or plague             |
| 6  | Miracle            | Reports of supernatural or miraculous events     |
| 7  | Betrayal           | Accusations of treachery or broken trust         |
| 8  | Romance            | Tales of love affairs or forbidden relationships |
| 9  | Treasure           | Hints of hidden wealth or valuable items         |
| 10 | Monster            | Sightings or rumors of dangerous creatures       |
| 11 | Political          | Shifts in power, alliances, or intrigue          |
| 12 | Economic           | Market crashes, booms, or trade opportunities    |
| 13 | Invention          | New technologies or magical discoveries          |
| 14 | Disappearance      | Missing persons or unexplained vanishings        |
| 15 | Uprising           | Rebellions, revolts, or civil unrest             |

### Rumor System Summary
The Rumor System models the spread of information using an Information Diffusion model with mutation. Each rumor has a type, truth value, severity, and category. Rumors mutate as they spread, and believability is tracked per entity. Rumors never become core memories or world events, and decay naturally unless repeated.

- **Rumor Types:** See canonical list above.
- **Propagation:** Rumors spread via entity interactions, with mutation and believability tracking.
- **Mutation:** Each spread may alter details, severity, or truth value.
- **Decay:** Rumors fade unless reinforced by repetition.
- **Integration:** Rumor events are emitted for analytics and narrative systems.

### Rumor Propagation Pseudocode
```csharp
// On rumor spread:
for each recipient:
    if (RandomChance(mutationRate))
        rumor = MutateRumor(rumor)
    recipient.ReceiveRumor(rumor)
    recipient.UpdateBelievability(rumor)
// On time advance:
    rumor.Decay()
```

### Narrative Integration Example
- Narrative systems call `RumorSystem.GetRumorContext()` to retrieve current rumor context for GPT or event generation.

**See also:** [RumorSystem.cs](../VDM/Assets/Scripts/Systems/Rumor/RumorSystem.cs)

## World State System

### Canonical World State Variable Type List

| ID | Variable Type   | Description                                      |
|----|-----------------|--------------------------------------------------|
| 1  | Population      | Population count or metrics for a region/POI      |
| 2  | Resource        | Resource quantity or status (food, gold, etc.)    |
| 3  | Motif           | Current motif for region or global                |
| 4  | FactionStatus   | Faction control, influence, or reputation         |
| 5  | POIState        | State of a POI (city, ruins, dungeon, etc.)       |
| 6  | Weather         | Weather state for a region                        |
| 7  | Time            | Current in-game time, date, or season             |
| 8  | QuestStatus     | Status/progress of a quest or arc                 |
| 9  | WarStatus       | Status of war/conflict between factions           |
| 10 | EventFlag       | Boolean or counter for triggered events            |
| 11 | Economy         | Economic metrics (trade, prices, etc.)            |
| 12 | Law             | Law, edict, or policy status                      |
| 13 | Custom          | User/system-defined custom variable               |

### World State System Summary
The World State System implements a hierarchical, versioned key-value store for all game state variables, with full historical tracking and query capabilities. Supports categorization, region tagging, and event emission on state changes.

- **Variable Types:** See canonical list above.
- **Versioning:** All state changes are versioned and timestamped for historical queries.
- **Query:** Supports queries by category, region, time, and prefix.
- **Integration:** Emits events on state changes for analytics and system integration.

### Versioned Key-Value Storage Pseudocode
```csharp
// Setting a state variable:
WorldStateManager.Instance.SetState(key, value, category, region);

// Internal logic:
var entry = new StateEntry { Key = key, Value = value, Version = ++version, Timestamp = now, Category = category, Region = region };
stateHistory[key].Add(entry);
Emit WorldStateChanged event;

// Querying historical state:
var history = WorldStateManager.Instance.GetHistory(key);
var valueAtTime = WorldStateManager.Instance.GetValueAtTime(key, timestamp);
```

### Historical Query Example
- Retrieve all population values for a region in the last 30 days.
- Reconstruct world state at a specific point in time for rollback or analytics.

**See also:** [WorldStateManager.cs](../VDM/Assets/Scripts/Systems/World/WorldStateManager.cs)

## Time System, Calendar, and Recurring Events

### Canonical Time Unit and Event Type List

| ID | Time Unit   | Description                                      |
|----|-------------|--------------------------------------------------|
| 1  | Tick        | Smallest discrete time step (simulation tick)     |
| 2  | Second      | In-game second                                   |
| 3  | Minute      | In-game minute                                   |
| 4  | Hour        | In-game hour                                     |
| 5  | Day         | In-game day                                      |
| 6  | Month       | In-game month                                    |
| 7  | Year        | In-game year                                     |
| 8  | Season      | In-game season (spring, summer, etc.)            |

| ID | Event Type      | Description                                      |
|----|-----------------|--------------------------------------------------|
| 1  | OneTime         | Single scheduled event (e.g., festival)           |
| 2  | RecurringDaily  | Event repeats every day                           |
| 3  | RecurringWeekly | Event repeats every week                          |
| 4  | RecurringMonthly| Event repeats every month                         |
| 5  | RecurringYearly | Event repeats every year                          |
| 6  | SeasonChange    | Season changes (triggers environmental effects)   |
| 7  | SpecialDate     | Custom/holiday event                              |

### Time System Summary
The Time System provides flexible, extensible in-game time progression, calendar management, and event scheduling. Supports variable time scaling, custom calendars, recurring/one-time events, and integration with other systems.

- **Time Units:** See canonical list above.
- **Event Types:** See canonical list above.
- **Advancement:** Supports pausing, scaling, and custom tick rates.
- **Calendar:** Configurable day/month/year structure, leap years, and holidays.
- **Event Scheduling:** Priority queue for one-time and recurring events, with catch-up logic.
- **Integration:** Emits events for time advancement and event triggers.

### Time Advancement and Event Scheduling Pseudocode
```csharp
// Advancing time:
timeSystem.Tick(deltaTime);

// Internal logic:
currentTime += deltaTime * timeScale;
if (currentTime >= nextEventTime)
    TriggerEvent(nextEvent);
    ScheduleNextOccurrence(nextEvent);

// Scheduling an event:
timeSystem.ScheduleEvent(eventType, date, recurrence, callback, priority);

// Calendar configuration:
timeSystem.ConfigureCalendar(daysPerMonth, monthsPerYear, leapYearInterval);
```

### Calendar and Event Example
- Add a custom holiday: `timeSystem.AddImportantDate("Founders' Day", year, month, day);`
- Subscribe to event notifications: `timeSystem.OnEventTriggered += handler;`

**See also:** [TimeSystemFacade.cs](../VDM/Assets/Scripts/World/Time/TimeSystemFacade.cs)

## Population Control System

### Canonical POI Type List

| ID | POI Type      | Description                                      |
|----|---------------|--------------------------------------------------|
| 1  | City          | Major population center, social hub               |
| 2  | Town          | Smaller population center                         |
| 3  | Village       | Rural, low-population settlement                  |
| 4  | Ruins         | Abandoned or destroyed location                   |
| 5  | Dungeon       | Hostile, combat-focused location                  |
| 6  | Religious     | Temple, shrine, or religious center               |
| 7  | Embassy       | Diplomatic or political POI                       |
| 8  | Outpost       | Military or frontier location                     |
| 9  | Market        | Economic/trade hub                                |
| 10 | Custom        | User/system-defined POI type                      |

### Population Control Formula

Monthly NPC Generation = BaseRate × (CurrentPopulation ÷ TargetPopulation) × GlobalMultiplier

- **BaseRate:** Configurable per POI type
- **CurrentPopulation:** Current NPC count in POI
- **TargetPopulation:** Desired/maximum NPC count for POI
- **GlobalMultiplier:** System-wide adjustment (admin control)

### Population Control System Summary
The Population Control System manages NPC generation and population thresholds for all POIs. Implements dynamic birth rate adjustment, soft/hard caps, and integration with state transitions and resource mechanics.

- **POI Types:** See canonical list above.
- **Formula:** See above for monthly NPC generation calculation.
- **Thresholds:**
  - Soft cap: Reduced birth rate at 90% of max
  - Hard cap: No growth above max
  - Minimum: Prevents ghost towns
- **Adjustment:** Admin controls for manual tuning, global multiplier
- **Integration:** Triggers POI state transitions, resource checks, and event emission

### Population Adjustment Pseudocode
```csharp
// On monthly update:
foreach (POI in allPOIs)
    if (POI.CurrentPopulation < POI.TargetPopulation)
        var rate = BaseRate * (POI.CurrentPopulation / POI.TargetPopulation) * GlobalMultiplier;
        if (POI.CurrentPopulation >= 0.9 * POI.TargetPopulation)
            rate *= 0.5f; // Soft cap
        POI.CurrentPopulation += Mathf.FloorToInt(rate);
        if (POI.CurrentPopulation > POI.TargetPopulation)
            POI.CurrentPopulation = POI.TargetPopulation; // Hard cap
    if (POI.CurrentPopulation < POI.MinPopulation)
        POI.CurrentPopulation = POI.MinPopulation; // Prevent ghost towns
    // Emit PopulationChanged event
```

### Manual Adjustment Example
- Admin sets GlobalMultiplier to 0.8 to slow population growth
- Designer sets BaseRate for cities to 10, villages to 2

**See also:** [PopulationManager.cs](../VDM/Assets/Scripts/Systems/Population/PopulationManager.cs)

## Motif System

### Canonical Motif List

| ID | Motif Type      | Description |
|----|----------------|-------------|
| 1  | Ascension      | TBD         |
| 2  | Betrayal       | TBD         |
| 3  | Chaos          | TBD         |
| 4  | Collapse       | TBD         |
| 5  | Compulsion     | TBD         |
| 6  | Control        | TBD         |
| 7  | Death          | TBD         |
| 8  | Deception      | TBD         |
| 9  | Defiance       | TBD         |
| 10 | Desire         | TBD         |
| 11 | Destiny        | TBD         |
| 12 | Echo           | TBD         |
| 13 | Expansion      | TBD         |
| 14 | Faith          | TBD         |
| 15 | Fear           | TBD         |
| 16 | Futility       | TBD         |
| 17 | Grief          | TBD         |
| 18 | Guilt          | TBD         |
| 19 | Hope           | TBD         |
| 20 | Hunger         | TBD         |
| 21 | Innocence      | TBD         |
| 22 | Invention      | TBD         |
| 23 | Isolation      | TBD         |
| 24 | Justice        | TBD         |
| 25 | Loyalty        | TBD         |
| 26 | Madness        | TBD         |
| 27 | Obsession      | TBD         |
| 28 | Paranoia       | TBD         |
| 29 | Power          | TBD         |
| 30 | Pride          | TBD         |
| 31 | Protection     | TBD         |
| 32 | Rebirth        | TBD         |
| 33 | Redemption     | TBD         |
| 34 | Regret         | TBD         |
| 35 | Revelation     | TBD         |
| 36 | Ruin           | TBD         |
| 37 | Sacrifice      | TBD         |
| 38 | Silence        | TBD         |
| 39 | Shadow         | TBD         |
| 40 | Stagnation     | TBD         |
| 41 | Temptation     | TBD         |
| 42 | Time           | TBD         |
| 43 | Transformation | TBD         |
| 44 | Truth          | TBD         |
| 45 | Unity          | TBD         |
| 46 | Vengeance      | TBD         |
| 47 | Worship        | TBD         |

### Motif System Summary
The Motif System manages global and regional narrative motifs that influence world events, NPC behavior, and narrative context. Motifs are selected randomly, have fixed durations, and never conflict—only synthesize. The system is fully hidden from players and is used for narrative flavor and GPT context.

- **Global Motif:** One active at a time, intensity 7, duration 28±10 days.
- **Regional Motifs:** Multiple, intensity 1–6, duration proportional to intensity.
- **Rotation:** Motifs rotate automatically after their duration expires.
- **Integration:** Narrative systems and GPT context can query current motifs for flavor.

### Motif Rotation Pseudocode
```csharp
// On day advance:
if (GlobalMotif expired)
    GlobalMotif = PickRandomMotif(intensity: 7, duration: 28±10 days)
for each region:
    if (RegionalMotif expired)
        RegionalMotif = PickRandomMotif(intensity: 1–6, duration: intensity * random(3–6) days)
```

### Narrative Integration Example
- Narrative systems call `MotifManager.GetMotifContext()` to retrieve current motif context for GPT or event generation.

**See also:** [MotifManager.cs](../VDM/Assets/Scripts/Systems/Motif/MotifManager.cs)

### Canonical Motif Effect List

| ID | Motif Effect         | Description                                      |
|----|----------------------|--------------------------------------------------|
| 1  | NPCBehavior          | Alters NPC routines, aggression, or mood         |
| 2  | EventFrequency       | Modifies frequency of random/world events         |
| 3  | ResourceYield        | Changes resource production or scarcity           |
| 4  | RelationshipChange   | Affects relationship gain/loss rates              |
| 5  | ArcDevelopment       | Influences story arc or quest progression         |
| 6  | FactionTension       | Modifies faction tension or alliance rates        |
| 7  | WeatherPattern       | Alters weather or environmental effects           |
| 8  | EconomicShift        | Impacts trade, prices, or economic events         |
| 9  | NarrativeFlavor      | Provides context for GPT/narrative generation     |
| 10 | Custom               | User/system-defined motif effect                  |

### Motif System Integration Summary
The Motif System applies global and regional motif effects to world state, NPCs, and narrative systems. Effects are synthesized, never conflicting, and are used for both mechanical and narrative flavor.

- **Motif Effects:** See canonical list above.
- **Application:** Effects are applied to NPCs, world state, and narrative context.
- **Synthesis:** Multiple motifs combine effects; no direct conflicts.
- **Integration:** Hooks for event system, world state, and GPT context.

### Motif Effect Application Pseudocode
```csharp
// On motif change:
foreach (effect in ActiveMotif.Effects)
    ApplyEffectToWorldState(effect);
    ApplyEffectToNPCs(effect);
    ApplyEffectToNarrative(effect);
// On narrative request:
var context = MotifManager.GetMotifContext();
// On event generation:
if (ActiveMotif.ModifiesEventFrequency)
    AdjustEventSpawnRate();
```

### Example Integration
- War motif increases NPC aggression, event frequency, and tension between factions
- Prosperity motif boosts resource yield and economic events
- Narrative systems query motif context for GPT prompt flavor

**See also:** [MotifManager.cs](../VDM/Assets/Scripts/Systems/Motif/MotifManager.cs)

## Region System

### Summary
The Region System utilizes biome and environmental tags from 'land_types.json' to influence city/POI generation, motif assignment, and arc types within distinct geographical areas. These tags help ensure thematic consistency across a region's contents.

**Q: Do regions have biome/environmental tags that influence generation?**

**A:** Yes. Regions use biome/environmental tags from 'land_types.json' to influence city/POI generation, motif assignment, and arc types. Ensure 'land_types.json' exists and is referenced in generation logic.

### Canonical Biome/Environment Tag List

| ID | Biome/Tag      | Description                                      |
|----|----------------|--------------------------------------------------|
| 1  | Plains         | Open grasslands, fertile, moderate climate        |
| 2  | Forest         | Dense woodland, high biodiversity                 |
| 3  | Desert         | Arid, low rainfall, extreme temperatures          |
| 4  | Mountain       | High elevation, rocky, cold                       |
| 5  | Swamp          | Wetlands, high humidity, difficult terrain        |
| 6  | Tundra         | Cold, treeless, permafrost                        |
| 7  | Jungle         | Dense tropical forest, high rainfall              |
| 8  | Coast          | Adjacent to ocean/lake, moderate climate          |
| 9  | Steppe         | Semi-arid grassland, sparse trees                 |
| 10 | Volcanic       | Active/inactive volcano, geothermal activity      |
| 11 | Urban          | Heavily developed, city/metropolis                |
| 12 | River          | Major river system, fertile banks                 |
| 13 | Lake           | Large inland body of water                        |
| 14 | Custom         | User/system-defined biome or tag                  |

### Region System Integration Summary
The Region System uses biome/environment tags to drive city/POI generation, motif assignment, and arc types. Ensures thematic consistency and supports procedural world generation.

- **Biomes/Tags:** See canonical list above and land_types.json.
- **Generation:** Biome tags influence POI types, motif selection, and arc generation.
- **Integration:** Used by world/region generation, motif system, and narrative logic.

### Biome-Driven Generation Pseudocode
```csharp
// On region generation:
region.Biome = PickBiomeFromTable();
AssignPOITypes(region, region.Biome);
AssignMotifs(region, region.Biome);
AssignArcTypes(region, region.Biome);
// On motif/arc assignment:
if (region.Biome == Desert)
    Prefer motifs/arcs related to scarcity, survival, or trade
```

### Example Integration
- Forest regions generate more village/town POIs, favor motifs of discovery or prosperity
- Volcanic regions favor catastrophe motifs and rare resource arcs
- Narrative systems use biome tags for context flavor

**See also:** [land_types.json], region generation code

## POI System

### Summary
The POI (Point of Interest) System enables dynamic state transitions, allowing cities to become ruins or dungeons when depopulated, and combat/neutral locations to become social spaces when repopulated. The system integrates with NPC generation logic and includes scaffold support for future specialized POI types like religious centers and embassies.

**Q: Can cities/POIs be abandoned, ruined, or transformed?**

**A:** Yes. If a city is depopulated, it becomes a 'city' POI but changes from 'social' to 'combat' or 'neutral' (e.g., ruins, dungeons). Dungeon/exploration POIs can become 'social' if repopulated. Implement POI state transitions and NPC (re)generation logic for dynamic world repopulation.

**Q: Should there be reserved POI slots for future systems?**

**A:** Not currently, but initial procgen should scaffold for future reserved slots (e.g., religious centers, embassies). Add reserved POI slot logic to initial world/region generation.

### Canonical POI State List

| ID | POI State     | Description                                      |
|----|---------------|--------------------------------------------------|
| 1  | Normal        | Fully populated, functional POI                   |
| 2  | Declining     | Population dropping, at risk of abandonment       |
| 3  | Abandoned     | No active population, not yet ruins               |
| 4  | Ruins         | Destroyed/abandoned, hostile or neutral           |
| 5  | Dungeon       | Hostile, repopulated by monsters                  |
| 6  | Repopulating  | Population returning, transitioning to Normal     |
| 7  | Special       | Custom/narrative state (e.g., festival, siege)    |

### POI System Integration Summary
The POI System enables dynamic state transitions for all POIs, integrating with population, war, and narrative systems. Supports runtime NPC (re)generation and event emission on state changes.

- **POI States:** See canonical list above.
- **Transitions:** Driven by population, war damage, and narrative triggers.
- **NPC Generation:** Regenerates or removes NPCs based on state.
- **Integration:** Emits events for analytics, narrative, and system hooks.

### State Transition and NPC Generation Pseudocode
```csharp
// On population/war update:
foreach (POI in allPOIs)
    var newState = EvaluateState(POI);
    if (newState != POI.State)
        POI.State = newState;
        if (newState == Ruins || newState == Dungeon)
            RemoveAllNPCs(POI);
        else if (newState == Repopulating || newState == Normal)
            RegenerateNPCs(POI);
        Emit POIStateChanged event;
```

### Example Integration
- City becomes Declining as population drops below threshold
- Declining city becomes Abandoned, then Ruins if not repopulated
- Dungeon can become Repopulating if population returns
- Narrative systems can trigger Special states (e.g., festival)

**See also:** [POIStateManager.cs], state transition rules

## Faction System

### Canonical Faction Type List

| ID | Faction Type   | Description                                      |
|----|----------------|--------------------------------------------------|
| 1  | Political      | Government, city-state, or political group        |
| 2  | Religious      | Organized religion, cult, or spiritual group      |
| 3  | Guild          | Trade, craft, or professional guild               |
| 4  | Criminal       | Underworld, thieves, or criminal organization     |
| 5  | Military       | Army, mercenary, or defense force                 |
| 6  | Academic       | University, school, or knowledge society          |
| 7  | Arcane         | Magic, wizard, or supernatural group              |
| 8  | Custom         | User/system-defined faction type                  |

### Faction System Integration Summary
The Faction System manages dynamic membership, schisms, and reputation for all entities. Integrates with relationship, quest, and narrative systems. Supports cross-faction membership and affinity-based switching.

- **Faction Types:** See canonical list above.
- **Schism:** Factions can split based on tension, ideology, or events.
- **Switching:** Affinity-based, immediate switching with contextual restrictions.
- **Reputation:** Tracks standing and reputation with all factions.
- **Integration:** Hooks for relationship, quest, and narrative systems.

### Schism, Switching, and Reputation Pseudocode
```csharp
// On tension/ideology event:
if (Faction.Tension > SchismThreshold)
    CreateNewFactionFromSchism(Faction);
    ReassignMembersByAffinity();
// On switch request:
if (CanSwitchFaction(entity, targetFaction))
    entity.Faction = targetFaction;
    UpdateReputation(entity, targetFaction);
// On reputation event:
UpdateReputation(entity, faction, delta);
if (Reputation < HostileThreshold)
    RestrictSwitching(entity, faction);
```

### Example Integration
- Faction schism creates a new faction, splits members by ideology
- Character switches to a new faction if affinity is high and not restricted
- Reputation changes affect quest availability and NPC interactions

**See also:** [FactionManager.cs], relationship model

## Tension and War System

### Summary
The Tension and War System tracks relationship values between factions on a -100 to +100 scale, where negative values represent alliances/trust and positive values represent conflict potential. Tension decays naturally over time in both directions, and war outcomes can have mechanical consequences like resource changes or population shifts.

**Q: Can tension go negative (alliances)?**

**A:** Yes. Allow tension to go as low as -100 for alliances/trust, decaying over time like positive tension.

**Q: Should war outcomes have mechanical consequences?**

**A:** Open to suggestions for mechanical consequences (e.g., resource changes, population shifts). Propose and implement mechanical effects for war outcomes.

### Canonical Tension/War State List

| ID | State         | Description                                      |
|----|---------------|--------------------------------------------------|
| 1  | Alliance      | Strong positive relationship, mutual trust        |
| 2  | Neutral       | No significant tension or alliance                |
| 3  | Rivalry       | Moderate negative tension, potential for conflict |
| 4  | War           | Active conflict between factions                  |
| 5  | Truce         | Temporary cessation of hostilities                |
| 6  | Hostile       | Deep negative tension, likely to escalate         |

### Tension and War System Integration Summary
The Tension and War System tracks relationship values between factions, manages tension decay, and handles war declaration and outcomes. Integrates with faction, resource, and population systems.

- **States:** See canonical list above.
- **Tension:** Value from -100 (alliance) to +100 (war/hostile), decays over time.
- **War Declaration:** Triggered by tension threshold or events.
- **Outcome Effects:** War outcomes affect resources, population, and world state.
- **Integration:** Hooks for analytics, narrative, and event systems.

### Tension Decay, War Declaration, and Outcome Pseudocode
```csharp
// On time advance:
foreach (pair in allFactionPairs)
    pair.Tension = DecayTension(pair.Tension);
    if (pair.Tension >= WarThreshold && !pair.IsAtWar)
        DeclareWar(pair);
    else if (pair.Tension <= AllianceThreshold && !pair.IsAllied)
        FormAlliance(pair);
// On war outcome:
if (WarEnded)
    ApplyWarOutcomeEffects(pair, outcome);
    pair.Tension = PostWarTension(outcome);
```

### Example Integration
- Tension decays toward neutral over time
- War declared when tension exceeds threshold
- War outcome reduces population, changes resources, and updates world state
- Analytics and narrative systems log and react to war events

**See also:** [FactionManager.cs], war event logic

## Arc and Quest System

### Canonical Arc/Quest Type List

| ID | Type         | Description                                      |
|----|--------------|--------------------------------------------------|
| 1  | RegionalArc  | Multi-step narrative spanning a single region      |
| 2  | GlobalArc    | World event or story spanning multiple regions     |
| 3  | PersonalArc  | Character-driven, personal story arc               |
| 4  | FactionArc   | Faction-driven, affects group or organization      |
| 5  | SideQuest    | Optional, non-critical quest                       |
| 6  | MainQuest    | Critical path, main storyline quest                |
| 7  | EventQuest   | Triggered by world/narrative event                 |
| 8  | Custom       | User/system-defined arc or quest type              |

### Arc and Quest System Integration Summary
The Arc and Quest System manages narrative arcs and quests, supporting regional/global scope, character/faction links, and event-driven progression. Integrates with motif, region, and relationship systems.

- **Arc/Quest Types:** See canonical list above.
- **Assignment:** Arcs/quests assigned based on region, character, or event triggers.
- **Progression:** Tracks status, progress, and dependencies.
- **Integration:** Hooks for motif, region, and relationship systems.

### Arc/Quest Assignment and Progression Pseudocode
```csharp
// On event/trigger:
if (TriggerMatchesArcType(event, arcType))
    AssignArcToRegionOrCharacter(arcType, target);
// On quest progress:
UpdateQuestStatus(quest, progress);
if (quest.Completed)
    UnlockNextQuestOrArc(quest);
    Emit QuestUpdated event;
```

### Example Integration
- Regional arc assigned when region motif changes
- Faction arc triggered by schism or war event
- Personal arc progresses as character relationships change
- Main quest unlocks side quests or event quests

**See also:** [arc/quest manager code]

## Religion System

### Canonical Religion Type List

| ID | Religion Type  | Description                                      |
|----|----------------|--------------------------------------------------|
| 1  | Polytheistic   | Multiple deities, pantheon-based                  |
| 2  | Monotheistic   | Single deity, centralized doctrine                |
| 3  | Animistic      | Spirits inhabit natural objects/phenomena         |
| 4  | Ancestor       | Ancestor worship, lineage-based                   |
| 5  | Cult           | Small, secretive, or heretical group              |
| 6  | Syncretic      | Blends elements from multiple religions           |
| 7  | Custom         | User/system-defined religion type                 |

### Religion System Integration Summary
The Religion System supports cross-faction membership, narrative-driven mechanics, and integration with faction and quest systems. Provides narrative hooks for events and story arcs.

- **Religion Types:** See canonical list above.
- **Membership:** Entities can belong to multiple religions and factions.
- **Narrative Hooks:** Religion events trigger narrative arcs, quests, and motif changes.
- **Integration:** Hooks for faction, quest, and narrative systems.

### Cross-Faction Membership and Narrative Hook Pseudocode
```csharp
// On religion event:
if (ReligionEventOccurs(entity, religionType))
    AddReligionMembership(entity, religionType);
    TriggerNarrativeArcOrQuest(entity, religionType);
// On faction/religion overlap:
if (entity.Faction.Type == Religious)
    SyncFactionAndReligionMembership(entity);
```

### Example Integration
- Character joins a cult, triggering a secret quest arc
- Religion event causes motif change and new narrative arc
- Faction schism creates a new religion or cult

**See also:** [FactionManager.cs], narrative integration points

## Diplomacy System

### Canonical Diplomacy Event Type List

| ID | Event Type     | Description                                      |
|----|----------------|--------------------------------------------------|
| 1  | Negotiation    | Formal negotiation between factions                |
| 2  | Treaty         | Treaty or agreement signed                        |
| 3  | AllianceFormed | New alliance established                          |
| 4  | TruceDeclared  | Temporary truce or ceasefire                      |
| 5  | Ultimatum      | Demand or threat issued                           |
| 6  | DiplomaticIncident | Event causing tension or conflict              |
| 7  | Custom         | User/system-defined diplomatic event              |

### Diplomacy System Integration Summary
The Diplomacy System manages formal negotiations, treaties, and diplomatic events between factions. Integrates with faction, tension/war, and narrative systems.

- **Event Types:** See canonical list above.
- **Negotiation:** Supports multi-step negotiation with offers, counter-offers, and outcomes.
- **Treaties:** Tracks treaty terms, duration, and enforcement.
- **Integration:** Hooks for faction, tension/war, and event systems.

### Negotiation, Treaty, and Diplomatic Event Pseudocode
```csharp
// On negotiation start:
StartNegotiation(factionA, factionB);
while (!NegotiationComplete)
    ExchangeOffers(factionA, factionB);
    if (AgreementReached)
        SignTreaty(factionA, factionB, terms);
        Emit Treaty event;
    else if (NegotiationBreakdown)
        Emit DiplomaticIncident event;
// On treaty expiration:
if (TreatyExpired)
    RemoveTreaty(factionA, factionB);
    UpdateTension(factionA, factionB);
```

### Example Integration
- Factions negotiate a truce, resulting in a temporary ceasefire
- Alliance formed after successful negotiation and treaty
- Diplomatic incident increases tension, may trigger war

**See also:** [FactionManager.cs], event system

## Economy System

### Summary
The Economy System should already have basic scaffolding in place, with no immediate need for new magical or technological systems. Any existing economic framework should be verified and extended as needed, while keeping flexibility for future region and faction type integration.

**Q: Should other systems (economy, magic, technology) be scaffolded now?**

**A:** Economy should already have a scaffold; check and add if missing. Magic: no new system needed beyond current implications. Technology: not needed now, but keep in mind for region/faction types.

### Canonical Economy Metric List

| ID | Metric         | Description                                      |
|----|----------------|--------------------------------------------------|
| 1  | Gold           | Standard currency, used for trade and value       |
| 2  | Food           | Essential resource, affects population and trade  |
| 3  | Goods          | Manufactured or crafted items                     |
| 4  | RawMaterials   | Ore, wood, stone, and other base resources        |
| 5  | TradeVolume    | Amount of goods traded between regions/factions   |
| 6  | PriceIndex     | Average price of goods/resources                  |
| 7  | Supply         | Current supply of a resource                      |
| 8  | Demand         | Current demand for a resource                     |
| 9  | TaxRate        | Taxation level for a region or faction            |
| 10 | Custom         | User/system-defined economic metric               |

### Economy System Integration Summary
The Economy System manages resources, trade, and pricing across regions and factions. Integrates with population, region, and event systems. Supports dynamic price adjustment and resource flow.

- **Metrics:** See canonical list above.
- **Resource Flow:** Tracks supply, demand, and trade between regions/factions.
- **Price Adjustment:** Prices adjust based on supply/demand and events.
- **Integration:** Hooks for population, region, and event systems.

### Resource, Trade, and Price Adjustment Pseudocode
```csharp
// On resource update:
foreach (resource in allResources)
    UpdateSupplyDemand(resource);
    AdjustPrice(resource);
// On trade event:
if (TradeOccurs(regionA, regionB, resource, amount))
    TransferResource(regionA, regionB, resource, amount);
    UpdateTradeVolume(regionA, regionB, resource, amount);
    AdjustPrice(resource);
// On event (e.g., famine, war):
if (EventAffectsResource(event, resource))
    ModifySupplyDemand(resource, event.effect);
    AdjustPrice(resource);
```

### Example Integration
- Famine event reduces food supply, increases price
- Trade route established increases trade volume and stabilizes prices
- Tax rate changes affect gold flow and region wealth

**See also:** [economy manager code], resource models

## Technical Implementation References

For detailed implementation information about core systems, see the following sections:

### Events System Implementation

**Q: What architecture should we use for implementing the central event dispatcher?**

**A:** The central event dispatcher will use an Event Bus pattern with a publish-subscribe model. This provides loose coupling between components and flexibility for future extensions. Key features of the implementation include:

1. A singleton `EventDispatcher` class that maintains subscriptions
2. Support for typed events via Pydantic BaseModel
3. Async event handling with prioritization
4. Middleware chain for logging, filtering, and other cross-cutting concerns
5. Both async and sync interfaces for various contexts
6. Thread-safe operation for concurrent event handling

The design allows for easy addition of new event types and subscribers without modifying existing code, following the Open/Closed Principle. Events are strongly typed for better maintainability and type safety.

### Analytics Service Implementation

**Q: How should we structure the analytics service for event capture and analysis?**

**A:** The analytics service will be implemented as a singleton with an event-driven architecture that integrates with the central event dispatcher. Key aspects include:

1. A dedicated `AnalyticsService` class that registers middleware with the event dispatcher
2. Structured event storage using JSON files organized by date and category
3. Configurable storage paths and retention policies
4. Automatic metadata enrichment (timestamps, session IDs, etc.)
5. Support for aggregation and filtering for analysis
6. LLM training dataset generation capabilities
7. Both async and sync interfaces

This approach allows non-intrusive analytics collection that doesn't impact core gameplay, while maintaining a structured format for later analysis and model training.

### Memory System Implementation

**Q: How should we design the memory system for storing and retrieving entity memories?**

**A:** The memory system will be implemented using a repository pattern with relevance scoring and decay. Key features include:

1. A singleton `MemoryManager` class for central memory operations
2. `Memory` objects with metadata, categories, relevance scores
3. Support for "core memories" that don't decay over time
4. Contextual relationships between memories (memory graphs)
5. Event emission for memory operations via the event dispatcher
6. Persistence with JSON storage organized by entity
7. Memory decay mechanisms to simulate forgetting
8. Methods for generating memory summaries for LLM context

This design provides a scalable, flexible memory system that simulates realistic memory patterns while maintaining good performance and integration with other systems.

### Rumor System Implementation

**Q: What's the best approach for implementing the rumor creation and propagation system?**

**A:** The rumor system will be implemented using a variant of the Information Diffusion model with mutations. Key design elements include:

1. A singleton `RumorSystem` class for managing rumor operations
2. `Rumor` objects with truth values, severity, and categories
3. Support for rumor variants/mutations as they spread
4. Entity-specific believability tracking
5. Natural mutation capabilities via configurable handlers
6. Persistence with JSON storage organized by rumor ID
7. Integration with event system for rumor events
8. Believability calculations based on entity relationships and bias

This approach allows realistic rumor propagation with mutations while maintaining traceability of how information spreads and changes throughout the world.

### World State Implementation

**Q: How should we implement the world state system with historical tracking?**

**A:** The world state system will be implemented using a key-value store with temporal versioning. Key aspects include:

1. A singleton `WorldStateManager` class with hierarchical state organization
2. Support for categorization, regions, and tagging of state variables
3. Complete history tracking of all state changes
4. Query capabilities by category, region, time period, and prefix
5. Event emission for state changes via event dispatcher
6. Persistence with JSON storage and automatic saving
7. Historical state reconstruction at any point in time
8. Thread-safe operations for concurrent access

This design provides a flexible foundation for tracking world state with full history, enabling features like state rollback, historical queries, and change analysis.

### Time System Implementation

**Q: How should we design the time system with calendar support and scheduled events?**

**A:** The time system will be implemented as a discrete-time simulation with variable time scaling. Key features include:

1. A singleton `TimeManager` class for central time management
2. Support for different time units (tick, minute, hour, day, etc.)
3. Variable time progression speeds (paused, slow, normal, fast)
4. Calendar system with seasons, months, years, and eras
5. Event scheduling at specific game times
6. Recurring events with configurable intervals
7. Event emission for time changes via event dispatcher
8. Time-based conditions (day/night, seasons, etc.)
9. Persistence with JSON storage for time state and scheduled events

This approach provides a flexible time system that can run at various speeds, supports scheduling, and integrates with other game systems through the event dispatcher.

### Population Control System Implementation

**Q: How should we implement NPC population control for POIs?**

**A:** The population control system will be implemented using a percentage-based birth rate model that can be manually adjusted. Key features include:

1. A `PopulationManager` class for centralized population control
2. Configurable base birth rates for each POI type
3. Population calculation formula:
   - Monthly NPC generation = Base Rate × (Current Population ÷ Target Population) × Global Multiplier
4. Adjustment mechanisms:
   - Admin controls for manual birth rate adjustment
   - Global multiplier for system-wide population control
   - Negative multipliers for population reduction
5. Population thresholds:
   - Soft cap (reduced birth rate) at 90% of maximum
   - Hard cap at defined maximum per POI type
   - Minimum threshold to prevent ghost towns
6. Integration with:
   - POI state transition system
   - Resource consumption mechanics
   - Faction influence calculations
   - Event system for population changes

This system ensures realistic population dynamics while providing manual control levers to adjust NPC numbers if they become too populous or too sparse across the game world.

### World Motif System Implementation

**Q: How should we implement the global and regional motif systems?**

**A:** The motif system will be implemented using a randomized rotation model with synthesis between overlapping motifs. Key features include:

1. A `MotifManager` class for centralized motif management
2. Global motif implementation:
   - Single global motif active at any time
   - Fixed duration of 28 days ± 10 days (randomly determined)
   - Always at maximum intensity (7)
   - Stronger than any individual regional motifs (which cap at 6)
   - Selected completely at random from predefined list
3. Regional motif implementation:
   - Lower-order motifs with variable durations based on intensity
   - Multiple regional motifs can coexist
   - No conflicting motifs (only synthesis between motifs)
   - Duration proportional to intensity for regional motifs
4. Motif effects implementation:
   - Influence on NPC behavior and dialogue via GPT context
   - Influence on random event generation
   - Influence on relationship development rates
   - Influence on story arc development
5. Integration with:
   - Event system for motif changes
   - Time system for duration tracking
   - NPC and region systems for applying effects

This implementation follows the design decisions that motifs are randomly selected, never influenced by other factors, have no conflicts (only synthesis), and that global motifs maintain a fixed duration with maximum strength while regional motifs have variable durations based on intensity.

### Inventory System: Multi-Inventory Transfer & Weight Validation (2024)

- The backend now supports atomic, validated transfers between any two inventories via a FastAPI endpoint (`/inventory/transfer`).
- Transfers are validated for source quantity, target capacity, and weight limits.
- All transfer operations are logged and will emit pre/post event hooks for analytics, SFX, and UI integration (see TODOs in code).
- Use the provided utility (`transfer_item_between_inventories`) for all backend transfer logic to ensure consistency and atomicity.
- All new inventory-related endpoints must include authentication and permission checks (see TODOs).
- For UI and integration, use the `/inventory/{inventory_id}` endpoint to fetch inventory contents.
- Follow best practices for error handling: failed transfers return HTTP 400 with a clear message.
- See backend/api2/routes/inventory_api_fastapi.py and backend/inventory/inventory_utils.py for implementation details and extension points.

## Character Builder & Persistence Integration (2024)

- The canonical way to create, save, and load characters is via the CharacterBuilder and CharacterService integration.
- Use the builder for all construction logic; use the service for all persistence logic.
- Serialization and deserialization between builder and model is handled by `to_dict`, `from_dict`, `to_builder`, and `from_builder` methods.
- Always use `builder.save(db_session)` to persist, and `CharacterBuilder.load(character_id, db_session)` to reconstruct a builder from the database.
- The Character model provides `to_builder()` and `from_builder()` for seamless conversion.
- All new code should follow this pattern for character creation and persistence.
- See backend/app/characters/README.md for code examples and further documentation.

# VDM Advanced Combat System

## Overview
The VDM combat system is a modular, extensible runtime-only framework for tactical turn-based encounters, designed for Unity 2D and Python/FastAPI backend integration. All logic is generated at runtime—no scene, prefab, or drag-and-drop dependencies.

---

## Architecture
- **CombatManager**: Orchestrates combat state, turn queue, and effect pipeline. Exposes runtime hooks for turn start/end, combatant management, and UI integration.
- **TurnQueue**: Maintains a sorted, flexible list of combatants. Supports dynamic join/leave, reordering, and advancing turns.
- **EffectPipeline**: Manages application, stacking, timing, and removal of combat effects. Integrates with turn system for start/end hooks.
- **CombatEffect**: Abstract base for all effects (buffs, debuffs, statuses). Supports stacking, resistance, immunity, and custom timing.
- **EffectVisualizer**: Displays effect icons above combatants at runtime using SpriteRenderer and pooled GameObjects. No scene/prefab dependencies.
- **ObjectPool<T>**: Generic pooling for MonoBehaviour objects, improving performance and memory usage.
- **CombatDebugInterface**: Provides runtime debug controls for rapid iteration and testing.

---

## Unity Integration
- All scripts are in `VDM/Assets/Scripts/Combat/`.
- 100% runtime-generated: no UnityEditor code, no scene/prefab/tag dependencies.
- Entry point: `GameLoader.cs` in `Bootstrap.unity` scene.
- Use `CombatManager` as the main orchestrator. Attach to a runtime GameObject.
- Use `EffectVisualizer` for effect icons. Assign an icon prefab at runtime.
- Use `CombatDebugInterface` for in-editor testing (OnGUI-based, no UI dependencies).
- All combatants must implement `ICombatant`.

---

## Backend API (FastAPI)
- Python backend in `/backend/` provides serialization for combat state.
- Endpoints:
  - `GET /combat/state`: Get current combat state (combatants, effects, turn order, etc.)
  - `POST /combat/state`: Set current combat state
- Uses Pydantic models for type safety and extensibility.
- In-memory storage for rapid prototyping; swap for persistent storage as needed.

---

## Extensibility & Best Practices
- Add new effect types by subclassing `CombatEffect` and extending `EffectType` enum.
- Use `ObjectPool<T>` for all runtime-instantiated MonoBehaviours (icons, projectiles, etc.).
- Avoid scene/prefab dependencies—instantiate everything at runtime.
- Use the backend API for save/load, analytics, or multiplayer state sync.
- Follow SOLID and DRY principles for all new code.
- Document new systems in this file.

---

## Example: Adding a New Effect
1. Subclass `CombatEffect` (e.g., `PoisonEffect`).
2. Add to `EffectType` enum.
3. Use `EffectPipeline.ApplyEffect` to apply to a combatant.
4. Assign a new icon sprite/color in `EffectVisualizer`.

---

## Example: Saving Combat State
- Use the backend API:
  - `GET /combat/state` to fetch current state
  - `POST /combat/state` to save new state
- Integrate with Unity via `UnityWebRequest` or Python client.

---

## References
- See code in `VDM/Assets/Scripts/Combat/` and `/backend/` for implementation details.
- For questions, follow industry best practices and update this document as the system evolves.

# World Generation & Geography Canonicalization

## Region, City, and Metropolis Footprint
- **Region:** Canonical region is a hex grid of 225 tiles (flat-to-flat).
- **City/Metropolis:**
  - Cities/metropolises "claim" one or more region hexes for visual impact.
  - Metropolises claim 2–3 adjacent region hexes (if available) for sprawl.
  - Each city/metropolis POI stores a list of claimed region hexes.
- **Zoom-in Logic:**
  - On the region map, city/metropolis icons fill all claimed hexes.
  - On selection, the game animates a zoom-in to the detailed city map, instantiating buildings, streets, and NPCs based on POI data.

## Canonical Sizes
- **Region:** 225 hex tiles (flat-to-flat)
- **Continent:** 20–40 regions per continent (procedurally generated)
- **City (non-metropolis):** Fills 1 region hex visually
- **Metropolis:** Fills 2–3 region hexes visually
- **Population:**
  - Region: 300–600 NPCs
  - Metropolis: 100–200 NPCs (active), with virtual population for flavor

## Procedural Continent Generation
- **Algorithm:**
  - Continents are generated as a set of regions using a random walk (see `generate_continent`).
  - Each continent has a unique `continent_id`, a set of region coordinates, and a list of region IDs.
  - Each region is assigned a `continent_id`.
- **Constants:**
  - `CONTINENT_SIZE_RANGE = (20, 40)`
  - `REGION_HEXES_PER_REGION = 225`

## Region-to-Lat/Lon Mapping
- **Origin:** Ushuaia, Argentina (`-54.8019, -68.3030`) is the canonical world origin.
- **Mapping:**
  - Each region grid coordinate is mapped to a real-world lat/lon using a scale factor (`REGION_LATLON_SCALE`).
  - Example: `lat = ORIGIN_LAT + region_y * REGION_LATLON_SCALE`, `lon = ORIGIN_LON + region_x * REGION_LATLON_SCALE`
- **Purpose:**
  - Enables real-world weather integration and geographic flavor.

## Weather System Integration
- **Design:**
  - Each region hex is mapped to a real-world lat/lon.
  - Weather is fetched from OpenWeatherMap API (or similar) for each region hex.
  - Fallback to procedural weather if API fails or for performance.
  - In-game distances can be "stretched" so the world feels large, but weather queries are spaced out to avoid excessive API calls.
- **API Hook:**
  - See `get_region_weather(region_x, region_y)` in backend for stub/API call example.
  - Unity or backend can call this to fetch weather for a region.

## Visual/Gameplay Notes
- **Region Map:**
  - Cities/metropolises are visually large, filling claimed hexes.
  - On zoom-in, the city map is instantiated with buildings/NPCs matching the simulation.
- **Continent Boundaries:**
  - Procedurally generated, with each region assigned to a continent.
  - Each continent is a unique, contiguous set of regions.

## Tuning & Future Work
- All constants and algorithms are documented in `region_generation_utils.py` and here for easy tuning.
- Weather system can be further refined for performance and realism.
- Continent/region/city sizes can be adjusted as needed for gameplay or technical reasons.

## POI State Transition System

The POI State Transition System enables Points of Interest (POIs) to dynamically change states (e.g., city, ruins, dungeon) based on population metrics and war damage. It is event-driven, designer-configurable, and fully runtime for Unity 2D projects.

### Architecture
- **POIStateManager**: Manages state transitions for a POI, tracks population, and triggers events. Emits a POIStateChangedEvent via the EventBus whenever a POI changes state.
- **PopulationMetricsTracker**: Tracks current/max population, change rates, and significant events.
- **POIStateTransitionRuleSet**: ScriptableObject for designer-configurable transition thresholds and rules, including one-way transitions and exemptions.
- **POIStateIndicator**: MonoBehaviour for runtime visual feedback (color, label, and threshold warnings) on POI state.

### Configuration
- **Transition Rules**: Use POIStateTransitionRuleSet ScriptableObject to define population thresholds for each state transition (Normal→Declining, Declining→Abandoned, etc.), one-way transitions, and exemptions.
- **Manual Overrides**: Use POIStateManager public methods to set state manually or exempt POIs from automatic transitions.

### Event System
- **POIStateChangedEvent**: Emitted via EventBus whenever a POI changes state. Contains POIId, OldState, NewState, and Timestamp. Other systems can subscribe to this event for analytics, narrative triggers, or integration.
- **OnStateChanged**: `public event Action<POIState, POIState> OnStateChanged;` fires whenever a POI changes state.
- **Population Events**: PopulationMetricsTracker fires events for significant changes (e.g., disasters, migrations).
- **Integration**: Other systems (e.g., WarManager) can call `OnWarDamage(float severity)` to trigger state changes due to war.

### Visual Indicators
- **POIStateIndicator**: Attach at runtime to any POI GameObject. Uses SpriteRenderer color coding:
  - Normal: Green
  - Declining: Yellow
  - Abandoned: Orange
  - Ruins: Gray
  - Dungeon: Red
- **Floating Label**: TextMeshPro label above POI shows current state and population.
- **Threshold Warning**: When a POI's population is within 10% of a transition threshold, the indicator flashes and the label displays a warning message.

### Example Usage
```csharp
// Attach POIStateManager and POIStateIndicator at runtime
var poi = new GameObject("POI");
var stateManager = poi.AddComponent<POIStateManager>();
poi.AddComponent<POIStateIndicator>();

// Set population and trigger state evaluation
stateManager.SetPopulation(50);
stateManager.SetMaxPopulation(100);
stateManager.GetPopulationMetricsTracker().UpdateMetrics();

// Listen for state changes
stateManager.OnStateChanged += (oldState, newState) => Debug.Log($"State changed: {oldState?.Type} → {newState.Type}");
EventBus.Instance.Subscribe<POIStateManager.POIStateChangedEvent>(evt => Debug.Log($"POI {evt.POIId} changed from {evt.OldState} to {evt.NewState} at {evt.Timestamp}"));

// Trigger war damage
stateManager.OnWarDamage(0.8f); // Likely transitions to Ruins
```

### Testing Scenarios
- Simulate population growth/decline and verify state transitions at correct thresholds.
- Trigger war damage and confirm correct state changes.
- Attach POIStateIndicator and verify color/label updates in real time.
- Test manual overrides and exemption logic.
- Use unit tests for PopulationMetricsTracker calculations and event triggers.
- Subscribe to POIStateChangedEvent and verify event emission.

### Extension Points
- Add custom visual effects or icons for threshold warnings.
- Integrate with analytics by subscribing to POIStateChangedEvent.
- Expand transition rules for narrative or gameplay needs.

---
For more details, see the code in `VDM/Assets/Scripts/POI/` and contact the system architect for advanced integration.

## Character Relationship System (Canonical)

The character relationship system is the canonical method for representing all inter-entity relationships in the game. It is implemented via the `Relationship` model (`backend/app/models/relationship.py`) and is fully integrated with the Character model and service layer.

### Supported Relationship Types
- **Faction**: Membership, reputation, and standing with factions. Data: `{ "reputation": int, "standing": str }`
- **Quest**: Links to quests, with status and progress. Data: `{ "status": "active|completed|failed", "progress": float }`
- **Spatial**: Proximity and territory relationships. Data: `{ "distance": float, "location_id": int }`
- **Authentication**: User-character links, permissions, and ownership. Data: `{ "permissions": [...], "owner": bool }`

### Canonical Data Structure
```
Relationship {
  source_id: int,         # ID of the source entity (character, user, etc.)
  target_id: int,         # ID of the target entity (faction, quest, location, character, etc.)
  type: str,              # Relationship type ("faction", "quest", "spatial", "auth", ...)
  data: dict,             # Type-specific payload (see above)
  created_at: datetime,
  updated_at: datetime
}
```

### API Usage
- List: `GET /characters/{character_id}/relationships/`
- Add: `POST /characters/{character_id}/relationships/`
- Remove: `DELETE /characters/{character_id}/relationships/`
- Update Faction Reputation: `POST /characters/{character_id}/relationships/faction/{faction_id}/reputation`
- Set Quest Status: `POST /characters/{character_id}/relationships/quest/{quest_id}/status`
- Update Spatial Proximity: `POST /characters/{character_id}/relationships/spatial/{location_id}/proximity`
- Set Auth Link: `POST /characters/{character_id}/relationships/auth/{user_id}/link`

All endpoints accept and return canonical data structures. See OpenAPI schema for details.

### Design Rationale
- **Extensibility**: The system supports arbitrary relationship types and payloads for future expansion.
- **Consistency**: All relationships are managed via a single model and API, simplifying integration and maintenance.
- **Integration**: The system is fully integrated with the Character model, builder pattern, and service layer. See `backend/app/characters/README.md` for integration details.
- **Synchronization**: Follows the same backend/frontend sync patterns as the inventory system.

### Usage Examples
- To update a character's reputation with a faction:
  - `POST /characters/123/relationships/faction/5/reputation?reputation_change=10`
- To set a quest as completed:
  - `POST /characters/123/relationships/quest/42/status?status=completed&progress=1.0`
- To update spatial proximity:
  - `POST /characters/123/relationships/spatial/7/proximity?distance=12.5`
- To link a user to a character with permissions:
  - `POST /characters/123/relationships/auth/99/link?permissions=["play","edit"]&owner=true`

### See Also
- [backend/app/characters/README.md](../backend/app/characters/README.md) for integration and usage details.
- [backend/app/models/relationship.py](../backend/app/models/relationship.py) for the canonical model.

## Storage System (2025 Update)

The Visual DM storage system now supports:
- **Autosave and Checkpointing:** Timed autosaves and event-based checkpoints for all major game state objects. Configurable interval and retention policy. See AutosaveManager.
- **Cloud Sync (Planned):** CloudStorageProvider stub for future cross-device save data (Steam Cloud, iCloud, Google Drive, etc.).
- **Encryption:** AES-256 encryption with HMAC integrity, secure key derivation, and platform-specific key storage (see EncryptionService).
- **Migration & Versioning:** All IStorable objects must increment DataVersion on breaking changes. Use SerializationHelper.Migrate for backward compatibility.
- **UI Integration (Planned):** SaveLoadUIController for progress indicators, error dialogs, and autosave notifications.
- **Test Strategy:** Comprehensive unit, integration, performance, security, and regression tests. See README for best practices.

**Reference:** See [VDM/Assets/Scripts/Systems/Storage/README.md](../VDM/Assets/Scripts/Systems/Storage/README.md) for technical details, usage, and extension points.

## Backend WebSocket Integration (2025)

### Overview
The backend now supports a canonical WebSocket endpoint at `/ws/metrics/stream` for real-time communication with the frontend. All messages use a standardized envelope for type safety, extensibility, and robust error handling.

### Message Envelope
See `/docs/websocket_protocol.md` for the full protocol specification, including required fields, error handling, and example payloads.

### Test Coverage
- Unit tests for Pydantic models and handler logic (`test_websocket_schema.py`, `test_websocket_service.py`)
- Integration tests for endpoint behavior (`test_websocket_endpoint.py`)
- All message types, error cases, and connection events are covered
- Minimum 85% coverage for all WebSocket-related code

### Extensibility Guidelines
- Add new message types by extending the schema and handler logic
- Maintain backward compatibility by versioning the protocol
- Document all changes in `/docs/websocket_protocol.md`

### Rationale
- The canonical message envelope ensures consistent communication between backend and frontend, simplifies validation, and supports future expansion (e.g., sprite mapping, new event types).
- The test suite ensures reliability and maintainability as the system evolves.

### References
- `/docs/websocket_protocol.md` (protocol details)
- `backend/tests/unit/app/core/schemas/test_websocket_schema.py`
- `backend/tests/unit/app/core/schemas/test_websocket_service.py`
- `backend/tests/api/test_websocket_endpoint.py`

---

# Event-Driven Architecture and Canonical Event Bus

## Canonical EventDispatcher

Visual DM uses a single, canonical event bus for all narrative and mechanical events: `EventDispatcher` (see `backend/app/core/events/event_dispatcher.py`).

- Implements the publish-subscribe pattern for loose coupling between all subsystems.
- All major subsystems (memory, rumors, world state, time, analytics, etc.) emit and subscribe to events via this dispatcher.
- Promotes modularity, testability, and extensibility.

### Usage Example

```python
from backend.app.core.events.event_dispatcher import EventDispatcher, EventBase

class MyEvent(EventBase):
    data: str

def my_handler(event):
    print(f"Received: {event.data}")

dispatcher = EventDispatcher.get_instance()
dispatcher.subscribe(MyEvent, my_handler)
dispatcher.publish_sync(MyEvent(event_type="my.event", data="Hello!"))
```

### Best Practices
- Always use `EventDispatcher.get_instance()` to access the event bus.
- Define new event types by subclassing `EventBase` (using Pydantic for payloads).
- Use events for all cross-service communication unless there is a strong reason for direct calls.
- Add middleware for logging, error handling, or cross-cutting concerns.
- Write tests that subscribe a mock handler and assert event emission.

### Major Event Types
- `MemoryEvent` (memory created, accessed, decayed, etc.)
- `RumorEvent` (rumor created, spread, mutated, etc.)
- `WorldStateEvent` (state created, updated, deleted, etc.)
- `TimeEvent` (time advanced, dawn, dusk, etc.)
- `QuestEvent`, `InventoryEvent`, `ProgressionEvent`, `NPCEvent`, `MapEvent`, `WorldEvent`, `CampaignEvent` (see respective service modules)

### Migration Note
- The old `EventBus` is deprecated. All new code must use `EventDispatcher`.
- See `backend/app/core/events/event_dispatcher.py` for implementation and API.
- See `backend/tests/core/events/test_event_dispatcher.py` for canonical tests.

---

## Canonical Region and POI Hex Sizes

- **POI Hex:** The smallest map unit, representing a 5-foot-per-side hexagon (~65 sq ft).
- **Region Hex:** A large-scale hexagon representing 15 square miles (~39 sq km), composed of ~6,436,000 POI hexes (radius ≈ 1,464 POI hexes, width ≈ 2,929 POI hexes).
- **POI Density:** Each region contains ~20 major POIs (towns, dungeons, etc.), plus 200–400 minor/nature POIs (groves, ruins, camps, etc.), with the remainder being wilderness or terrain hexes.
- **Real-World Analogy:** Each region is about the size of a medium city or a 4x4 mile area.

---

## Continent Generation (2025 Update)

- Each continent is procedurally generated with a random number of regions (50–70), forming a contiguous landmass.
- The generation algorithm ensures explicit continent boundaries (bounding box: min/max region_x and region_y).
- Each continent is assigned a unique seed (randomly generated if not provided), enabling deterministic regeneration.
- Continent metadata includes: region coordinates, region IDs, origin, boundary, seed, and creation timestamp.
- Regions outside the boundary are not part of the continent.
- The system is scaffolded for future multi-continent support: each continent can be generated from its own seed, and all metadata is stored for later expansion.

---

## Modular Data & Modding Architecture

To maximize modding flexibility and future-proofing, all core game-defining data should be stored in JSON files. This enables modders to create new worlds, continents, or servers with custom content, while using the same core simulation and logic. The following categories are recommended for JSON modularization:

| Category         | JSON File(s)                | Purpose/Notes                                 |
|------------------|----------------------------|-----------------------------------------------|
| Biomes/Regions   | land_types, adjacency      | World geography, biome rules                  |
| Items/Equipment  | weapons, armor, items      | All gear, loot, crafting                      |
| Creatures/NPCs   | races, npcs, factions      | All living entities, relationships            |
| Buildings/POIs   | building_types, poi_types  | Structures, dungeons, towns                   |
| Economy/Trade    | resources, trade_goods     | Economy, resources, prices                    |
| Magic/Abilities  | spells, abilities, effects | Magic, skills, status effects                 |
| Quests/Narrative | quest_templates, motifs    | Story, quests, world events                   |
| Visuals          | sprite_manifest, animation | Sprites, animations, visual mapping           |
| Dialogue         | dialogue_templates         | NPC/player dialogue, language                 |
| Combat/Rules     | combat_rules, effect_types | Mechanics, combat, special effects            |
| Worldgen         | worldgen_rules, spawn      | Procedural generation, spawn tables           |
| Religion/Diplom. | religion, diplomacy        | Religion, diplomacy, politics                 |
| Tech/Custom      | technology, custom_rules   | Tech trees, modder overrides                  |

**Long-term vision:**
- Build a UI with sliders, visual options, and fields for non-technical modders to create worlds.
- All modder-created assets (sprites, templates, etc.) should be stored in a central repository for reuse in future worlds.
- The core engine should read these JSONs at world/server creation and use them for all procedural and narrative generation.
- GPT/AI can be used to power-balance new content and ensure compatibility with the base world.

---

## Modular Biome Adjacency, Coastline, and River Generation Systems

### Modular Biome Adjacency Matrix
- Biome adjacency rules are now defined in `backend/data/adjacency.json`.
- The adjacency matrix is fully modular: modders can edit/add rules to control which biomes can be adjacent, which require transitions, and what transitions are allowed.
- Each rule specifies two biomes, a rule type (`compatible`, `incompatible`, `transition_needed`), and optional transition biomes, minimum transition width, and weight.
- The system loads adjacency rules from JSON at runtime, falling back to defaults if not present.
- See `docs/modular_data_for_modding.md` and `backend/data/adjacency.json` for details and modding guidelines.

### Coastline Smoothing and Beach Placement
- Coastlines are smoothed using a cellular automata approach after initial biome assignment.
- Beaches are always placed between water and land biomes, ensuring natural transitions.
- The smoothing logic references the modular adjacency matrix to ensure compatibility and extensibility.
- Modders can adjust adjacency rules to affect coastline and beach generation.

### Modular River Generation
- Rivers are generated from high-elevation sources (mountain, hills, alpine, peaks) to the nearest ocean/lake.
- The river pathfinding algorithm always moves downhill and checks adjacency compatibility using the modular adjacency matrix.
- River tiles are only placed if compatible with the underlying biome, as defined in `adjacency.json`.
- The system supports future extension for river branching, deltas, and custom river logic via the modular data system.

### Integration and Extensibility
- All worldgen adjacency, coastline, and river logic is now modular and supports full modding via JSON files.
- Modders can add new biomes, transitions, or rules without code changes.
- See `docs/modular_data_for_modding.md` for a full list of modular data files and guidelines for extending worldgen systems.

---

## Canonical World Seed Schema

A canonical, extensible 'seeded world' JSON schema is now the primary entry point for defining worlds, continents, or servers. This schema:
- Aggregates references to all modular data categories (biomes, items, races, etc.)
- Supports all must-have fields for world metadata, settings, factions, religions, regions, canon lists, narrative hooks, and extensibility
- Allows partial seeds and procedural/GPT fallback for missing fields
- Is fully documented and validated (see `backend/data/modding/worlds/world_seed.schema.json`)
- Example file: `backend/data/modding/worlds/example_world.json`

See [modular_data_for_modding.md](modular_data_for_modding.md) for full schema documentation, field-by-field explanations, and modder workflow.