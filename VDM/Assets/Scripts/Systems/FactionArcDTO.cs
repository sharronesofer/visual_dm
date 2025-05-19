using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Narrative
{
    /// <summary>
    /// Data Transfer Object for FactionArc.
    /// </summary>
    [Serializable]
    public class FactionArcDTO
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

        // Faction-specific fields
        public string FactionId;
        public string FactionName;
        public string FactionDescription;
        public string FactionEmblem;
        public List<string> ShortTermGoals;
        public List<string> LongTermGoals;
        public List<FactionArcStageDTO> FactionStages;
        public int CurrentFactionStageIndex;
        public List<string> FactionTriggerConditionTypes;
        public List<FactionRelationshipDTO> InterFactionRelationships;
        public string FactionCompletionCriteriaType;
        public List<string> Rewards;
        public List<string> Consequences;
    }

    [Serializable]
    public class FactionArcStageDTO
    {
        public string Name;
        public string Description;
        public Dictionary<string, object> Metadata;
    }

    [Serializable]
    public class FactionRelationshipDTO
    {
        public string RelatedFactionArcId;
        public string RelationshipType;
        public float Strength;
    }
}