using System;
using System.Collections.Generic;
using VisualDM.Narrative;
using VisualDM.MotifSystem;

namespace VisualDM.Quest
{
    /// <summary>
    /// Context for arc-to-quest generation, containing all relevant data for mapping.
    /// </summary>
    public class ArcQuestGenerationContext
    {
        public GlobalArc Arc { get; set; }
        public object ArcStage { get; set; } // Can be ArcStage, FactionArcStage, etc.
        public string ArcType { get; set; } // "Global", "Regional", "Faction", "Character"
        public Dictionary<string, object> PlayerState { get; set; }
        public Dictionary<string, object> WorldState { get; set; }
        public string Motif { get; set; }
        public Motif MotifData { get; set; } // Motif object for narrative coherence
        public ArcQuestGenerationContext()
        {
            PlayerState = new Dictionary<string, object>();
            WorldState = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Interface for mapping arcs to quests.
    /// </summary>
    public interface IArcToQuestMapper
    {
        /// <summary>
        /// Generates one or more quests from an arc stage/objective.
        /// </summary>
        List<Quest> GenerateQuests(ArcQuestGenerationContext context);
    }

    /// <summary>
    /// Abstract base class for arc-to-quest mapping rules.
    /// </summary>
    public abstract class ArcQuestMappingRule
    {
        public string RuleName { get; set; }
        public abstract bool IsApplicable(ArcQuestGenerationContext context);
        public abstract void Apply(ArcQuestGenerationContext context, List<Quest> quests);
    }

    /// <summary>
    /// Concrete implementation for mapping GlobalArc to quests.
    /// </summary>
    public class GlobalArcToQuestMapper : IArcToQuestMapper
    {
        private readonly List<ArcQuestMappingRule> mappingRules;

        public GlobalArcToQuestMapper(IEnumerable<ArcQuestMappingRule> rules = null)
        {
            mappingRules = rules != null ? new List<ArcQuestMappingRule>(rules) : new List<ArcQuestMappingRule> { new DefaultGlobalArcMappingRule() };
        }

        public List<Quest> GenerateQuests(ArcQuestGenerationContext context)
        {
            var quests = new List<Quest>();
            foreach (var rule in mappingRules)
            {
                if (rule.IsApplicable(context))
                {
                    rule.Apply(context, quests);
                }
            }
            return quests;
        }
    }

    /// <summary>
    /// Example mapping rule: generates a basic quest for each stage in a GlobalArc.
    /// </summary>
    public class DefaultGlobalArcMappingRule : ArcQuestMappingRule
    {
        public DefaultGlobalArcMappingRule() { RuleName = "DefaultGlobalArcStageToQuest"; }

        public override bool IsApplicable(ArcQuestGenerationContext context)
        {
            return context.ArcType == "Global" && context.Arc is GlobalArc && context.ArcStage is ArcStage;
        }

        public override void Apply(ArcQuestGenerationContext context, List<Quest> quests)
        {
            var arc = context.Arc as GlobalArc;
            var stage = context.ArcStage as ArcStage;
            if (arc == null || stage == null) return;

            // Motif-aware quest generation
            string motifTheme = context.MotifData?.Theme ?? context.Motif;
            string motifTag = motifTheme != null ? $"[Motif: {motifTheme}]" : string.Empty;
            string motifDesc = context.MotifData?.Metadata != null && context.MotifData.Metadata.TryGetValue("description", out var descObj) ? descObj as string : null;

            var template = new QuestTemplate
            {
                ArcType = "Global",
                QuestType = "Story",
                BaseTitle = $"{arc.Title}: {stage.Name} {motifTag}",
                BaseDescription = stage.Description + (motifDesc != null ? $"\nMotif: {motifDesc}" : string.Empty),
                ObjectiveTemplates = new List<string> { $"Complete stage: {stage.Name} {motifTag}" }
            };
            var quest = template.GenerateQuest();
            quests.Add(quest);
        }
    }

    /// <summary>
    /// Utility for integrating arc dependencies into quest dependency management.
    /// </summary>
    public static class ArcQuestDependencyIntegrator
    {
        /// <summary>
        /// Registers quest dependencies and chains based on arc dependencies and stage progression.
        /// </summary>
        /// <param name="arc">The source arc.</param>
        /// <param name="arcStageToQuestId">Mapping from arc stage index to generated quest ID.</param>
        /// <param name="arcDependencyIds">IDs of arcs this arc depends on.</param>
        /// <param name="questDependencyManager">The quest dependency manager instance.</param>
        public static void IntegrateArcDependencies(GlobalArc arc, Dictionary<int, string> arcStageToQuestId, List<string> arcDependencyIds, QuestDependencyManager questDependencyManager)
        {
            // For each arc stage, set up quest chains to next stage's quest
            for (int i = 0; i < arc.Stages.Count - 1; i++)
            {
                if (arcStageToQuestId.TryGetValue(i, out var currentQuestId) && arcStageToQuestId.TryGetValue(i + 1, out var nextQuestId))
                {
                    questDependencyManager.RegisterQuestChain(currentQuestId, new List<string> { nextQuestId });
                    questDependencyManager.RegisterPrerequisites(nextQuestId, new List<string> { currentQuestId });
                }
            }
            // For arc dependencies, lock first quest of this arc until dependent arcs are complete
            if (arcDependencyIds != null && arcDependencyIds.Count > 0 && arcStageToQuestId.TryGetValue(0, out var firstQuestId))
            {
                // Here, you would look up the final quest IDs of dependent arcs and set as prerequisites
                // For demonstration, assume arcDependencyIds are quest IDs (in practice, map arc ID to quest ID)
                questDependencyManager.RegisterPrerequisites(firstQuestId, new List<string>(arcDependencyIds));
            }
        }
    }

    /// <summary>
    /// Utility for fetching motif data for quest generation.
    /// </summary>
    public static class MotifIntegrationUtility
    {
        public static Motif GetMotifForTheme(MotifPool motifPool, string theme)
        {
            if (motifPool == null || string.IsNullOrEmpty(theme)) return null;
            return motifPool.GetMotif(theme);
        }
    }
}