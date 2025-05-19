using System.Collections.Generic;

namespace VisualDM.AI
{
    public class TemplateSelector
    {
        private readonly TemplateRepository _repository;

        public TemplateSelector(TemplateRepository repository)
        {
            _repository = repository;
        }

        public PromptTemplate SelectTemplate(PlayerProfile profile, QuestHistory history, string category, List<string> contextTags)
        {
            // Example: weight by player preferences, history, and context
            var candidates = _repository.GetTemplatesByCategory(category);
            PromptTemplate best = null;
            double bestScore = double.MinValue;
            foreach (var template in candidates)
            {
                double score = ScoreTemplate(template, profile, history, contextTags);
                if (score > bestScore)
                {
                    best = template;
                    bestScore = score;
                }
            }
            // Fallback: return any if none found
            return best ?? (candidates.Count > 0 ? candidates[0] : null);
        }

        private double ScoreTemplate(PromptTemplate template, PlayerProfile profile, QuestHistory history, List<string> contextTags)
        {
            double score = 0;
            // Example: +1 for each matching tag
            foreach (var tag in contextTags)
            {
                if (template.Metadata != null && template.Metadata.ContainsKey(tag))
                    score += 1;
            }
            // Example: +2 if player prefers this category
            if (profile.PreferredCategories.Contains(template.Metadata.GetValueOrDefault("type")))
                score += 2;
            // Example: -1 if template was used recently
            if (history.RecentTemplates.Contains(template))
                score -= 1;
            // Extend with more sophisticated logic as needed
            return score;
        }
    }

    // Example supporting classes
    public class PlayerProfile
    {
        public List<string> PreferredCategories { get; set; } = new List<string>();
    }
    public class QuestHistory
    {
        public List<PromptTemplate> RecentTemplates { get; set; } = new List<PromptTemplate>();
    }
} 