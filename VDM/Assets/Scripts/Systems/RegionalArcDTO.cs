using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Narrative
{
    /// <summary>
    /// Data Transfer Object for RegionalArc.
    /// </summary>
    [Serializable]
    public class RegionalArcDTO
    {
        public string Id;
        public string Title;
        public string Description;
        public string NarrativePurpose;
        public List<ArcStageDTO> Stages;
        public int CurrentStageIndex;
        public List<string> TriggerConditionTypes;
        public string CompletionCriteriaType;
        public ArcRelationships Relationships;
        public ArcMetadata Metadata;
        public int Version;
        public List<string> DependencyArcIds;

        // Regional-specific fields
        public string RegionId;
        public string RegionName;
        public string RegionType;
        public List<RegionalStoryBeatDTO> RegionalStoryBeats;
        public List<string> RegionalCharacters;
        public List<string> RegionalLocations;
        public List<string> EntryConditionTypes;
        public List<string> ProgressionEventTypes;
        public List<string> ExitConditionTypes;
        public string ParentGlobalArcId;
        public float InfluenceLevel;
        public List<OverrideRuleDTO> OverrideRules;
        public List<RegionalStateChangeDTO> RegionalStateChanges;
        public List<string> PersistentEffects;
        public List<string> TemporaryEffects;
        public List<string> CompletionConditionTypes;
        public List<string> Rewards;
        public List<string> FollowUpArcs;
    }

    [Serializable]
    public class RegionalStoryBeatDTO
    {
        public string Id;
        public string Title;
        public string Description;
        public Dictionary<string, object> Metadata;
    }

    [Serializable]
    public class OverrideRuleDTO
    {
        public string RuleType;
        public string Description;
        public Dictionary<string, object> Parameters;
    }

    [Serializable]
    public class RegionalStateChangeDTO
    {
        public string StateKey;
        public object Value;
        public bool IsPersistent;
    }
}