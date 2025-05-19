using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Narrative
{
    /// <summary>
    /// Data Transfer Object for GlobalArc.
    /// </summary>
    [Serializable]
    public class GlobalArcDTO
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
    }

    [Serializable]
    public class ArcStageDTO
    {
        public string Name;
        public string Description;
        public Dictionary<string, object> Metadata;
    }
}