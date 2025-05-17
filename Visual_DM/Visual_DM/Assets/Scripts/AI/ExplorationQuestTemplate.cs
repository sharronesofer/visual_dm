using System.Collections.Generic;

namespace AI
{
    public class ExplorationQuestTemplate : PromptTemplate
    {
        public ExplorationQuestTemplate() : base(
            "Explore the {{location}} and discover the {{discovery}}. Reward: {{reward}}.",
            version: "1.0",
            metadata: new Dictionary<string, string> { { "type", "exploration" } })
        {
            // Default context for exploration quests
            Context.Add("Player is interested in exploration and discovery.");
        }

        // Override Render or add exploration-specific logic if needed
    }
} 