using System.Collections.Generic;
// Explicitly import types for clarity
using VisualDM.Systems.Narrative;

namespace VisualDM.Systems.Narrative
{
    // TODO: Add using statements for GlobalArc, GlobalArcDTO, ArcStage, ArcStageDTO if not in VisualDM.Systems.Narrative
    public static class GlobalArcMapper
    {
        public static GlobalArcDTO ToDTO(GlobalArc arc)
        {
            return new GlobalArcDTO
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
                DependencyArcIds = arc.DependencyArcIds
            };
        }
        public static GlobalArc FromDTO(GlobalArcDTO dto)
        {
            var arc = new GlobalArc(dto.Title, dto.Description, dto.NarrativePurpose)
            {
                // Id is readonly, so we need a workaround for deserialization in real use
                Stages = dto.Stages?.ConvertAll(s => new ArcStage(s.Name, s.Description) { Metadata = s.Metadata }),
                // TriggerConditions and CompletionCriteria would need to be rehydrated from type info
                Relationships = dto.Relationships,
                Metadata = dto.Metadata,
                Version = dto.Version,
                DependencyArcIds = dto.DependencyArcIds,
            };
            // Set current stage index
            while (arc.CurrentStageIndex < dto.CurrentStageIndex && arc.CurrentStageIndex < arc.Stages.Count - 1)
                arc.ProgressStage();
            return arc;
        }
    }
}