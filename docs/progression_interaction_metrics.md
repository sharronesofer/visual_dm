# Character Progression Metrics and Their Impact on Interactions

| Metric            | Description                                      | Impact on Interactions                                 | Example Thresholds/Conditions         | Edge Cases/Notes                        |
|-------------------|--------------------------------------------------|--------------------------------------------------------|---------------------------------------|-----------------------------------------|
| Level             | Character's overall advancement                  | Unlocks advanced options, restricts some interactions  | Level >= 10 unlocks advanced dialogue | Temporary boosts, regression            |
| Skills            | Specific abilities (e.g., lockpicking, combat)   | Unlocks/modifies skill-based interactions              | Lockpicking >= 5 enables safe cracking| Temporary buffs, skill resets           |
| Attributes        | Core attributes (strength, intelligence, etc.)      | Restricts/enables attribute-gated interactions         | Strength >= 8 to move heavy object    | Penalties, temporary boosts             |
| Reputation        | Standing with factions/groups                    | Unlocks/restricts faction-specific interactions        | Reputation > 50 unlocks quest         | Reputation loss, multiple factions       |
| Quest Completion  | Progress in quests                               | Unlocks quest-dependent, restricts obsolete            | Completed "Find Artifact" unlocks vendor | Quest resets, branching questlines   |
| Achievements      | Special milestones                               | Unlocks unique/cosmetic interactions                   | "Master Thief" unlocks secret fence  | Revocation (rare), hidden triggers      |
| Equipment         | Items/gear possessed                             | Enables equipment-dependent interactions               | "Ancient Key" unlocks door           | Equipment loss, temporary equipment      |
| Faction Standing  | Relationship with factions                       | Unlocks/restricts faction-based content                | Standing >= 75 with Order of Dawn     | Betrayal, dual membership               |
| Story Milestones  | Major narrative events                           | Unlocks story-locked, restricts pre-milestone content  | After "Coronation" unlocks court      | Alternate paths, missed milestones       |
| Perks/Traits      | Special character modifiers                      | Unlocks/changes unique interactions                    | "Silver Tongue" enables bribe option | Perk removal, trait conflicts           |
| Temporary Effects | Buffs/debuffs, environmental/magical effects     | Temporarily unlocks/restricts interactions             | "Blessing of Speed" enables trial    | Expiration, stacking effects            |
| Save State/Flags  | Persistent world/character flags                 | Unlocks one-time/persistent interactions               | "Helped Villager" enables reward     | Save scumming, flag corruption           |

- Each metric should be implemented as a modular check within the Interaction System.
- Thresholds and conditions must be clearly defined and documented for each interaction type.
- Edge cases should be handled gracefully, with fallback logic where possible.
- This table will be referenced in mapping/rules documentation and API/data structure design.
- All metrics and their impacts should be reviewed and updated as new game systems are introduced. 