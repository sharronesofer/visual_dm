using System.Collections.Generic;
// Explicitly import types for clarity
using VisualDM.Systems.Narrative;

namespace VisualDM.Systems.Narrative
{
    // TODO: Add using statements for FactionArc, FactionArcDTO, ArcStage, ArcStageDTO, FactionArcStage, FactionArcStageDTO, FactionRelationship, FactionRelationshipDTO if not in VisualDM.Systems.Narrative
    public static class FactionArcMapper
    {
        public static FactionArcDTO ToDTO(FactionArc arc)
        {
            return new FactionArcDTO
            {
                Id = arc.Id,
                Title = arc.Title,
                Description = arc.Description,
                NarrativePurpose = arc.NarrativePurpose,
                Stages = arc.Stages?.ConvertAll(s => new ArcStageDTO
                {
                    Name = s.Name,
                    Description = s.Description,
                    Metadata = s.Metadata
                }),
                CurrentStageIndex = arc.CurrentStageIndex,
                TriggerConditionTypes = arc.TriggerConditions?.ConvertAll(c => c.GetType().FullName),
                CompletionCriteriaType = arc.CompletionCriteria?.GetType().FullName,
                Relationships = arc.Relationships,
                Metadata = arc.Metadata,
                Version = arc.Version,
                DependencyArcIds = arc.DependencyArcIds,
                // Faction-specific fields
                FactionId = arc.FactionId,
                FactionName = arc.FactionName,
                FactionDescription = arc.FactionDescription,
                FactionEmblem = arc.FactionEmblem,
                ShortTermGoals = arc.ShortTermGoals,
                LongTermGoals = arc.LongTermGoals,
                FactionStages = arc.FactionStages?.ConvertAll(s => new FactionArcStageDTO
                {
                    Name = s.Name,
                    Description = s.Description,
                    Metadata = s.Metadata
                }),
                CurrentFactionStageIndex = arc.CurrentFactionStageIndex,
                FactionTriggerConditionTypes = arc.FactionTriggerConditions?.ConvertAll(c => c.GetType().FullName),
                InterFactionRelationships = arc.InterFactionRelationships?.Values?.ConvertAll(r => new FactionRelationshipDTO
                {
                    RelatedFactionArcId = r.RelatedFactionArcId,
                    RelationshipType = r.RelationshipType,
                    Strength = r.Strength
                }),
                FactionCompletionCriteriaType = arc.FactionCompletionCriteria?.GetType().FullName,
                Rewards = arc.Rewards,
                Consequences = arc.Consequences
            };
        }

        public static FactionArc FromDTO(FactionArcDTO dto)
        {
            var arc = new FactionArc(dto.Title, dto.Description, dto.NarrativePurpose, dto.FactionId, dto.FactionName, dto.FactionDescription, dto.FactionEmblem)
            {
                Stages = dto.Stages?.ConvertAll(s => new ArcStage(s.Name, s.Description) { Metadata = s.Metadata }),
                Relationships = dto.Relationships,
                Metadata = dto.Metadata,
                Version = dto.Version,
                DependencyArcIds = dto.DependencyArcIds,
                ShortTermGoals = dto.ShortTermGoals,
                LongTermGoals = dto.LongTermGoals,
                FactionStages = dto.FactionStages?.ConvertAll(s => new FactionArcStage(s.Name, s.Description) { Metadata = s.Metadata }),
                CurrentFactionStageIndex = dto.CurrentFactionStageIndex,
                Rewards = dto.Rewards,
                Consequences = dto.Consequences
            };
            // InterFactionRelationships
            if (dto.InterFactionRelationships != null)
            {
                arc.InterFactionRelationships = new System.Collections.Generic.Dictionary<string, FactionRelationship>();
                foreach (var rel in dto.InterFactionRelationships)
                {
                    arc.InterFactionRelationships[rel.RelatedFactionArcId] = new FactionRelationship
                    {
                        RelatedFactionArcId = rel.RelatedFactionArcId,
                        RelationshipType = rel.RelationshipType,
                        Strength = rel.Strength
                    };
                }
            }
            // Set current stage index
            while (arc.CurrentStageIndex < dto.CurrentStageIndex && arc.CurrentStageIndex < arc.Stages.Count - 1)
                arc.ProgressStage();
            while (arc.CurrentFactionStageIndex < dto.CurrentFactionStageIndex && arc.CurrentFactionStageIndex < arc.FactionStages.Count - 1)
                arc.ProgressFactionStage();
            return arc;
        }
    }
}