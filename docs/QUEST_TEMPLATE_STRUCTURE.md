# Quest Template Structure

This document describes the structure, schema, and best practices for defining quest templates in the system.

## Overview
Quest templates define the data and logic for all quest types, including main, side, faction, combat, and exploration quests. They are validated against a JSON schema and loaded from `src/quests/templates/`.

## Schema Specification
See [`schemas/quest_template.schema.json`](schemas/quest_template.schema.json) for the full JSON schema.

### Required Fields
- `id`: Unique quest identifier (string)
- `title`: Display name (string)
- `description`: Detailed quest description (string)
- `type` / `questType`: Quest category (enum)
- `status`: Current quest status (enum)
- `difficulty`: Difficulty rating (1-5)
- `requirements`: Object specifying minimum level, reputation, items, abilities
- `objectives`: Array of objectives (see below)
- `dialogue`: Array of dialogue blocks
- `rewards`: Object specifying gold, experience, items, reputation, etc.

### Objectives
Each objective must include:
- `id`: Unique within quest
- `description`: What the player must do
- `type`: Objective type (enum)
- Optional: `target`, `amount`, `location`, `customData`, `completed`, `conditions`

### Dialogue
Each dialogue block must include:
- `text`: NPC dialogue
- `npcId`: NPC identifier
- `responses`: Array of player response options

### Rewards
- `gold`, `experience`, `items` (required)
- Optional: `reputation`, `diplomaticInfluence`

## Usage Examples
See [`templates/sample_quest_templates.json`](templates/sample_quest_templates.json) for example quests:
- Main quest: Defend the Village
- Side quest: Gather Herbs
- Faction quest: Sabotage Rival Camp
- Combat quest: Arena Champion
- Exploration quest: Map the Ancient Ruins
- Diplomatic quest: Negotiate Peace

## Extension Points
- Add new objective types by extending the `ObjectiveType` enum in `src/quests/types.ts`.
- Add new reward types by extending the `QuestRewards` interface.
- Use `customData` for quest-specific logic or metadata.

## Best Practices
- Use clear, descriptive titles and objectives.
- Keep objectives atomic and testable.
- Use dialogue to provide context and narrative depth.
- Balance rewards according to difficulty and quest significance.
- Document new quest types and patterns in this file.

## Validation
- All quest templates must validate against the JSON schema before being loaded.
- Use automated tests to verify template loading and schema compliance.

## See Also
- [`src/quests/types.ts`](types.ts) for TypeScript interfaces
- [`schemas/quest_template.schema.json`](schemas/quest_template.schema.json) for schema
- [`templates/sample_quest_templates.json`](templates/sample_quest_templates.json) for examples

## QuestGenerationService: Dynamic Quest Generation

### Overview
The `QuestGenerationService` is responsible for generating dynamic quests based on templates, player/faction context, and input parameters. It leverages the quest template system and integrates with faction logic for advanced customization.

### Generation Flow
1. **Template Selection**
   - Filters available templates by type, tags, and (optionally) faction preferences.
   - Randomizes or weights selection for variety.
2. **Parameter Injection**
   - Accepts parameters such as difficulty, type, tags, factionId, and customData.
   - Injects these into the generated quest for contextualization.
3. **Stage/Objectives Generation**
   - Clones and resets objectives from the template.
   - Future: supports branching and parameter-based stage customization.
4. **Reward Scaling**
   - Scales rewards (gold, experience) by difficulty and other parameters.
   - Extensible for faction or tag-based bonuses.
5. **Extensibility**
   - Designed for easy extension to support new quest types, branching logic, and integration with other systems (e.g., consequences, world state).

### Example Usage
```python
const service = new QuestGenerationService(factionProfiles);
const quest = service.generateQuest({
  difficulty: 2,
  type: 'COLLECT',
  tags: ['rare'],
  factionId: 'guild',
  customData: { special: true }
});
```

### Parameters
- `difficulty`: Numeric difficulty scaling factor
- `type`: Quest type (optional)
- `tags`: Array of tags for filtering (optional)
- `factionId`: Faction context for quest (optional)
- `customData`: Additional custom data to inject (optional)

### Integration Points
- **Templates**: See `src/quests/templates/sample_quest_templates.json` for examples
- **Types**: See `src/quests/types.ts` for interfaces
- **Faction Logic**: See `src/quests/factions/types.ts` and `FactionQuestSystem.ts`
- **Tests**: See `src/quests/__tests__/QuestGenerationService.test.ts` 