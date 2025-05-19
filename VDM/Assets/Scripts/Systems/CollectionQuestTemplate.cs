using System.Collections.Generic;

namespace VisualDM.AI
{
    public class CollectionQuestTemplate : PromptTemplate
    {
        public CollectionQuestTemplate() : base(
            "Collect {{itemCount}} {{item}} from the {{location}}. Reward: {{reward}}.",
            version: "1.0",
            metadata: new Dictionary<string, string> { { "type", "collection" } })
        {
            // Default context for collection quests
            Context.Add("Player is tasked with gathering items.");
        }

        // Override Render or add collection-specific logic if needed
    }
} 