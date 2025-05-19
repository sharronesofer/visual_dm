using System.Collections.Generic;

namespace VisualDM.AI
{
    public class CombatQuestTemplate : PromptTemplate
    {
        public CombatQuestTemplate() : base(
            "Defeat the {{enemy}} in the {{location}}. Reward: {{reward}}.",
            version: "1.0",
            metadata: new Dictionary<string, string> { { "type", "combat" } })
        {
            // Default context for combat quests
            Context.Add("Player is seeking a combat challenge.");
        }

        // Override Render or add combat-specific logic if needed
    }
} 