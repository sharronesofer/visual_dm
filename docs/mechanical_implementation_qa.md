# Mechanical Implementation Q&A

The following Q&A provides industry best practice solutions for key mechanical systems requiring implementation in Visual DM, aligned with established design decisions.

## Character Relationship System

**Q: How should character relationships be structured to balance narrative depth with technical performance?**

**A:** The relationship system should use a directional weighted graph with asymmetric values:

1. Each relationship is directional (A→B separate from B→A)
2. Base relationships use a -100 to +100 scale with neutral at 0
3. Secondary dimensions include trust, fear, respect (no romantic interest unless in narrative context)
4. Context-sensitive relationships (public/private/crisis)
5. No direct sharing or transfer between entities (per Memory System design)
6. Integration with the Event Dispatcher for relationship changes
7. Observable through dialogue tone and willingness to help
8. Critical thresholds (-75, -50, -25, +25, +50, +75) trigger behavior changes
9. Special relationship flags for family, rivals, and enemies

This design provides nuanced narrative interactions while keeping the system computationally efficient. The directional nature ensures realistic asymmetric relationships while the numerical scale enables clear gameplay boundaries.

## Rumor Mutation System

**Q: What approach should we use for implementing rumor mutation as rumors spread between entities?**

**A:** The rumor mutation system should use a contextual deviation model:

1. Base truth value (0.0-1.0) assigned at creation never changes
2. Each transmission has a mutation chance based on:
   - Originator's reliability/reputation
   - Transmitter's personality traits
   - Receiver's gullibility/skepticism
   - Emotional impact of rumor content
3. Mutation types include:
   - Exaggeration (increasing severity/scale)
   - Minimization (decreasing severity/scale)
   - Detail addition (non-factual elaboration)
   - Detail loss (simplification)
   - Subject shift (changing who/what is involved)
4. Proper nouns rarely mutate (people/place names stay consistent)
5. Core meaning remains traceable to original (never complete transformation)
6. No option for rumors to become core memories (per design decision)
7. Mutations tracked in rumor variants, keeping full propagation history

This approach creates organic-feeling information spread that mimics real human behavior while adhering to the design decision that rumors never become core memories or world events.

## Faction Influence System

**Q: How should faction influence be implemented to create meaningful territorial control and political dynamics?**

**A:** The faction influence system should use a regional control model with the following characteristics:

1. Influence measured from 0-100 for each faction in each region
2. Multiple factions can have influence in the same region (no exclusive control)
3. Dominant faction (highest influence) controls regional policies
4. Influence thresholds:
   - <20: Minimal presence (spies, travelers)
   - 20-40: Minor presence (small outposts, sympathizers)
   - 40-60: Established presence (settlements, active recruitment)
   - 60-80: Major presence (military installations, governance)
   - >80: Dominant presence (complete cultural/military control)
5. Influence decays naturally over time (faster for distant regions)
6. Support for faction schisms as per design decisions:
   - Triggered by exceeding internal tension thresholds
   - Results in new faction with portion of original influence
   - Maintains initial hostility toward parent faction
7. Negative tension (alliances) down to -100 as specified in design decisions
8. No direct player visibility of influence numbers (narrative only)

This system creates dynamic territorial control that shifts naturally over time while supporting the design decision for faction schisms and negative tension representing alliances.

## Multi-Region Story Arc System

**Q: How should we implement arcs that span multiple regions to create cohesive global narratives?**

**A:** The multi-region arc system should use a hub-and-spoke narrative structure:

1. Three arc types:
   - Local (single region, minimal external impact)
   - Regional (affects 2-4 connected regions)
   - Global (world-scale, affects many or all regions)
2. Hub-and-spoke design:
   - Primary arc "hub" in one region with main story beats
   - Secondary "spoke" events in connected regions
   - Progress synchronization between hub and spokes
3. No explicit dependencies between arcs (per design decision)
4. Regional factors influence arc development:
   - Biome/environmental tags from 'land_types.json'
   - Current regional motifs
   - Dominant faction identity
   - Present POI types
5. Arc failure recorded as core regional memory
6. Arcs must resolve/fail before new ones start in the same region
7. Event emission via the central event dispatcher

This design creates coherent cross-region narratives while honoring the design decision that arcs have no explicit dependencies, leaving narrative connections to GPT/LLM logic.

## War Resolution System

**Q: How should we implement war outcomes to create meaningful consequences in line with design decisions?**

**A:** The war resolution system should use an impact-driven aftermath model:

1. Wars triggered at defined tension thresholds (70+)
2. War duration determined by military actions and countdown timer
3. Resolution types:
   - Decisive Victory (one side dominates)
   - Pyrrhic Victory (winner suffers significant losses)
   - Stalemate (no clear winner)
   - Negotiated Settlement (diplomatic resolution)
4. Mechanical consequences (per design decision request):
   - Population shifts (refugees to allied regions)
   - Resource production penalties in affected regions
   - Temporary POI type changes (cities become ruins/combat zones)
   - Faction influence redistribution
   - New core memories for involved regions and factions
5. War resolution creates new motifs in affected regions
6. Tension reset mechanism between involved factions
7. Cities can be abandoned or ruined (per design decision)
8. Events logged for analytics and AI training

This system creates meaningful war consequences while supporting the design decisions around tension mechanics, city transformation, and event logging.

## Religion System Scaffold

**Q: How should we scaffold the religion system to support cross-faction membership as specified in design decisions?**

**A:** The religion system should use a belief network model:

1. Religions as separate entities from factions (can overlap)
2. Characters can belong to both a faction and a religion
3. Religions have:
   - Core belief set (determine compatibility with other religions)
   - Influence levels per region (separate from faction influence)
   - Sacred sites within existing POIs
   - Hierarchical leadership structure
4. Religious membership affects:
   - Character decision-making and dialogue
   - Relationship modifiers between adherents
   - Faction membership compatibility
5. Religion can sometimes be a faction type
6. Cross-faction interactions:
   - Religions can unite characters across factional lines
   - Religious conflicts can cross-cut faction alliances
   - Shared religion reduces negative relationship impacts
7. No direct player visibility of religious mechanics (narrative only)

This scaffold supports the design decision that religion should cross faction barriers and be primarily narrative-driven, while allowing some religions to function as factions.

## Diplomacy System Scaffold

**Q: How should we implement the diplomacy system to integrate with factions as outlined in design decisions?**

**A:** The diplomacy system should use a negotiation-based agreement model:

1. Treaty types:
   - Non-aggression pacts (tension ceiling)
   - Trade agreements (resource benefits)
   - Military alliances (mutual defense)
   - Vassalage (hierarchical relationship)
2. Negotiation mechanics:
   - Based on faction affinity levels
   - Influenced by faction leader traits
   - Modified by historical relationships
   - Affected by resource needs
3. Treaty effects:
   - Tension modification between signatories
   - Resource sharing or trade bonuses
   - Military support triggers
   - Influence exchange in border regions
4. Diplomatic events:
   - Scheduled formal negotiations
   - Crisis-triggered emergency summits
   - Cultural exchanges and ceremonies
5. Integration with faction system:
   - Treaties persist through leadership changes
   - Breaking treaties has significant tension penalties
   - Treaties can include multiple factions

This system creates a framework for formal faction interactions that integrates with the existing faction system while providing narrative hooks for diplomatic events and negotiations.

## POI State Transition System

**Q: How should we implement POI state transitions to support cities becoming ruins and dungeons becoming settlements?**

**A:** The POI state transition system should use a condition-based transformation model:

1. Transition triggers:
   - Population thresholds (depopulation, repopulation)
   - Military events (sieges, raids, occupation)
   - Narrative events (disasters, discoveries)
   - Time-based decay or development
2. State types with transition paths:
   - Social → Combat (city becomes ruins)
   - Social → Neutral (city becomes abandoned)
   - Combat → Social (dungeon becomes settlement)
   - Neutral → Combat (abandoned becomes dangerous)
   - Neutral → Social (abandoned becomes repopulated)
3. NPC (re)generation logic:
   - Population scaling based on POI size
   - Demographic shifts during transitions
   - Relationship preservation for returning NPCs
4. Physical transformation:
   - Environment descriptors change
   - Points of interest within POI update
   - Access paths modify
5. Reserved slots for future systems:
   - Religious centers
   - Diplomatic outposts
   - Economic hubs

This system supports the design decision that POIs can change state based on world events, while scaffolding for future system integration as specified.

## Population Control Mechanics

**Q: How should we implement population control to manage NPC numbers across POIs?**

**A:** The population control system should use a percentage-based birth rate model:

1. Core mechanics:
   - Each POI has a configurable base birth rate
   - Actual birth rate calculated as a percentage of current population
   - System-wide multiplier for global adjustments
   - Target population ranges defined per POI type
2. Population balance formula:
   - Monthly NPC generation = Base Rate × (Current Population ÷ Target Population) × Global Multiplier
   - Negative multipliers possible for population reduction
3. Adjustment triggers:
   - Regular interval checks (monthly game time)
   - Manual adjustment via admin controls
   - Event-based modifications (plagues, wars, prosperity)
4. Population caps:
   - Soft cap (reduced birth rate) at 90% of maximum
   - Hard cap at defined maximum per POI type
   - Minimum population threshold to prevent ghost towns
5. Integration with other systems:
   - Resource consumption tied to population
   - Faction influence affected by population size
   - POI state transitions triggered by population thresholds

This system provides fine-grained control over NPC populations while maintaining believable world dynamics through percentage-based scaling that can be manually adjusted when needed.

## World Motif System

**Q: How should global motifs be implemented to affect all regions and NPCs as specified in the design decisions?**

**A:** The world motif system should use a randomized rotation model:

1. Global motif mechanics:
   - Single global motif active at any time
   - Fixed duration of 28 days ± 10 days (randomly determined)
   - Always at maximum intensity (7)
   - Stronger than any individual regional motifs (which cap at 6)
   - Selected completely at random from predefined list
   - No overwriting of motifs, only synthesis with regional motifs
2. Regional motif mechanics:
   - Lower-order motifs with variable durations based on intensity
   - Multiple regional motifs can coexist
   - No conflicting motifs (synthesis happens instead)
   - Duration proportional to intensity for regional motifs only
3. Motif effects:
   - Influence NPC behavior and dialogue
   - Affect nature of random events
   - Modify relationship development
   - Shape story arc development
4. Motif examples:
   - Heroism, Grief, Vanity, Justice, Mystery, Betrayal
5. No influence factors:
   - Motifs are not influenced by world events
   - No correlation with faction activities
   - No connection to prior motifs
   - No player visibility of motif mechanics

This implementation follows the design decisions that motifs are randomly selected, never influenced by other factors, have no conflicts (only synthesis), and that global motifs maintain a fixed duration with maximum strength while regional motifs have variable durations based on intensity.

## Resource and Economy Scaffold

**Q: How should the economy scaffold be implemented to support future economic systems as noted in design decisions?**

**A:** The economy scaffold should use a node-based resource flow model:

1. Resource fundamentals:
   - 8-10 primary resources with regional distribution
   - Production and consumption rates per region
   - Resource quality tiers affecting value
   - Seasonal availability variation
2. Economic structures:
   - Trade routes between regions (with distance costs)
   - Production centers tied to specific POIs
   - Market hubs in metropolis locations
   - Supply/demand algorithms for price fluctuation
3. Faction interaction:
   - Resource control as source of tension
   - Trade agreements affecting resource movement
   - Resource theft as conflict trigger
4. War impact mechanics:
   - Production disruption during conflicts
   - Resource seizure on territory capture
   - Post-war economic penalties
5. Hidden from player view (narrative-driven)

This scaffold provides the economic foundation mentioned in the design decisions, creating a system that can be expanded upon and integrated with other mechanics like war outcomes and faction relations.

## Memory Categorization System

**Q: How should we implement memory categorization to support analytics and narrative coherence as suggested in design decisions?**

**A:** The memory categorization system should use a multi-tag classification model:

1. Primary categories (as suggested in design decisions):
   - WAR (conflicts, battles, military events)
   - POLITICS (governance, faction events, diplomacy)
   - ARC (narrative arc participation)
   - CATASTROPHE (disasters, plagues, environmental events)
   - PERSONAL (individual experiences, relationships)
   - SOCIAL (community events, celebrations)
   - RELIGIOUS (spiritual experiences, rituals)
   - ECONOMIC (trade, resource events)
2. Implementation features:
   - Multiple categories per memory where appropriate
   - Category-based relevance modifiers
   - Memory retrieval filtering by category
   - Analytics grouping by category
3. Integration with core memories:
   - Categories affect memory persistence
   - No direct memory sharing (per design decision)
   - No explicit pinning (per design decision)
4. Analytics capabilities:
   - Category distribution analysis
   - Memory type frequency tracking
   - Category correlation detection

This system implements the suggested categorization while maintaining compliance with design decisions that memories are entity-local and not directly transferred between entities. 