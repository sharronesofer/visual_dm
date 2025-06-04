# FactionArc System Documentation

## Overview
`FactionArc` is a robust data structure for representing faction-specific narrative arcs in the Dreamforge Arcs System. It extends the `GlobalArc` architecture, adding properties and logic for faction identity, goals, progression, inter-faction relationships, and completion criteria.

---

## Class Diagram

```
FactionArc : GlobalArc
  - FactionId : string
  - FactionName : string
  - FactionDescription : string
  - FactionEmblem : string
  - ShortTermGoals : List<string>
  - LongTermGoals : List<string>
  - FactionStages : List<FactionArcStage>
  - CurrentFactionStageIndex : int
  - FactionTriggerConditions : List<IArcCondition>
  - InterFactionRelationships : Dictionary<string, FactionRelationship>
  - FactionCompletionCriteria : IFactionArcCompletionCriteria
  - Rewards : List<string>
  - Consequences : List<string>

FactionArcStage
  - Name : string
  - Description : string
  - Metadata : Dictionary<string, object>

FactionRelationship
  - RelatedFactionArcId : string
  - RelationshipType : string
  - Strength : float

IFactionArcCompletionCriteria
  - bool IsMet(GameState, FactionArc)
```

---

## Usage Example

```csharp
var factionArc = new FactionArc(
    title: "Rise of the Iron Legion",
    description: "The Iron Legion seeks to dominate the northern territories.",
    narrativePurpose: "Faction expansion and rivalry arc.",
    factionId: "iron_legion",
    factionName: "Iron Legion",
    factionDescription: "A militaristic faction focused on conquest.",
    factionEmblem: "iron_legion_emblem.png"
);

factionArc.ShortTermGoals.Add("Capture the Frosthold region");
factionArc.LongTermGoals.Add("Control all northern provinces");
factionArc.FactionStages.Add(new FactionArcStage("Mobilization", "The Iron Legion gathers its forces."));
factionArc.FactionStages.Add(new FactionArcStage("Invasion", "Launches an assault on Frosthold."));
factionArc.InterFactionRelationships["frost_clan"] = new FactionRelationship {
    RelatedFactionArcId = "frost_clan_arc",
    RelationshipType = "Rivalry",
    Strength = 0.8f
};
// ...
```

---

## Validation Rules
- `FactionId`, `FactionName`, and `FactionCompletionCriteria` are required.
- At least one `FactionArcStage` must be defined.
- All `InterFactionRelationships` must have valid `RelatedFactionArcId` and `RelationshipType`.
- Circular dependencies between faction arcs are detected and prevented.
- Completion criteria must be achievable (no impossible conditions).

---

## Error Handling
- Throws `ArgumentException` for missing required fields.
- Throws `InvalidOperationException` for circular dependencies.
- Validation methods should be called before serialization or integration.

---

## Integration Guidelines
- FactionArc is compatible with the existing GlobalArc and RegionalArc systems.
- Use `FactionArcMapper` and `FactionArcDTO` for serialization/deserialization.
- Integrate with the Tick System for progression (see TickConfig in GlobalArc).
- Connect to the Region system for territory-based interactions.
- Use extension points for future faction features (e.g., diplomacy, alliances).

---

## Example Scenario
- **Rivalry:** Two factions compete for the same territory, with relationship strength affecting arc progression.
- **Alliance:** Factions form alliances, unlocking new stages or rewards.
- **Territory Dispute:** Faction arcs interact with the Region system to reflect conquests or losses.

---

## See Also
- `GlobalArc`, `RegionalArc`, `FactionArcDTO`, `FactionArcMapper`
- `Tick System`, `Region System`, `FactionSystem`, `FactionRelationshipSystem` 