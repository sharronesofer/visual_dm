using System.Linq;

namespace VisualDM.Systems.Narrative
{
    public static class RegionalArcMapper
    {
        public static RegionalArcDTO ToDTO(RegionalArc arc)
        {
            return new RegionalArcDTO
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
                // Regional-specific fields
                RegionId = arc.RegionId,
                RegionName = arc.RegionName,
                RegionType = arc.RegionType,
                RegionalStoryBeats = arc.RegionalStoryBeats?.ConvertAll(b => new RegionalStoryBeatDTO
                {
                    Id = b.Id,
                    Title = b.Title,
                    Description = b.Description,
                    Metadata = b.Metadata
                }),
                RegionalCharacters = arc.RegionalCharacters,
                RegionalLocations = arc.RegionalLocations,
                EntryConditionTypes = arc.EntryConditions?.ConvertAll(c => c.GetType().FullName),
                ProgressionEventTypes = arc.ProgressionEvents?.ConvertAll(c => c.GetType().FullName),
                ExitConditionTypes = arc.ExitConditions?.ConvertAll(c => c.GetType().FullName),
                ParentGlobalArcId = arc.ParentGlobalArcId,
                InfluenceLevel = arc.InfluenceLevel,
                OverrideRules = arc.OverrideRules?.ConvertAll(r => new OverrideRuleDTO
                {
                    RuleType = r.RuleType,
                    Description = r.Description,
                    Parameters = r.Parameters
                }),
                RegionalStateChanges = arc.RegionalStateChanges?.ConvertAll(s => new RegionalStateChangeDTO
                {
                    StateKey = s.StateKey,
                    Value = s.Value,
                    IsPersistent = s.IsPersistent
                }),
                PersistentEffects = arc.PersistentEffects,
                TemporaryEffects = arc.TemporaryEffects,
                CompletionConditionTypes = arc.CompletionConditions?.ConvertAll(c => c.GetType().FullName),
                Rewards = arc.Rewards,
                FollowUpArcs = arc.FollowUpArcs
            };
        }

        public static RegionalArc FromDTO(RegionalArcDTO dto)
        {
            var arc = new RegionalArc(dto.Title, dto.Description, dto.NarrativePurpose, dto.RegionId, dto.RegionName, dto.RegionType, dto.ParentGlobalArcId)
            {
                // Id is readonly, so workaround for deserialization if needed
                Stages = dto.Stages?.ConvertAll(s => new ArcStage(s.Name, s.Description) { Metadata = s.Metadata }),
                Relationships = dto.Relationships,
                Metadata = dto.Metadata,
                Version = dto.Version,
                DependencyArcIds = dto.DependencyArcIds,
                RegionalStoryBeats = dto.RegionalStoryBeats?.ConvertAll(b => new RegionalStoryBeat
                {
                    Id = b.Id,
                    Title = b.Title,
                    Description = b.Description,
                    Metadata = b.Metadata
                }),
                RegionalCharacters = dto.RegionalCharacters,
                RegionalLocations = dto.RegionalLocations,
                ParentGlobalArcId = dto.ParentGlobalArcId,
                InfluenceLevel = dto.InfluenceLevel,
                OverrideRules = dto.OverrideRules?.ConvertAll(r => new OverrideRule
                {
                    RuleType = r.RuleType,
                    Description = r.Description,
                    Parameters = r.Parameters
                }),
                RegionalStateChanges = dto.RegionalStateChanges?.ConvertAll(s => new RegionalStateChange
                {
                    StateKey = s.StateKey,
                    Value = s.Value,
                    IsPersistent = s.IsPersistent
                }),
                PersistentEffects = dto.PersistentEffects,
                TemporaryEffects = dto.TemporaryEffects,
                Rewards = dto.Rewards,
                FollowUpArcs = dto.FollowUpArcs
            };
            // Note: EntryConditions, ProgressionEvents, ExitConditions, CompletionConditions would need to be rehydrated from type info
            // Set current stage index
            while (arc.CurrentStageIndex < dto.CurrentStageIndex && arc.CurrentStageIndex < arc.Stages.Count - 1)
                arc.ProgressStage();
            return arc;
        }
    }
}