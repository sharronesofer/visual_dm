using System;
using System.Collections.Generic;
using VisualDM.Core;
using VisualDM.World;

namespace VisualDM.Narrative
{
    /// <summary>
    /// Represents a faction-specific narrative arc, extending GlobalArc with faction attributes and logic.
    /// </summary>
    [Serializable]
    public class FactionArc : GlobalArc
    {
        // --- Faction Identification ---
        public string FactionId { get; set; }
        public string FactionName { get; set; }
        public string FactionDescription { get; set; }
        public string FactionEmblem { get; set; } // Path or identifier for visual

        // --- Faction Goals and Motivations ---
        public List<string> ShortTermGoals { get; set; } = new();
        public List<string> LongTermGoals { get; set; } = new();

        // --- Progression Stages ---
        public List<FactionArcStage> FactionStages { get; set; } = new();
        public int CurrentFactionStageIndex { get; private set; } = 0;

        // --- Triggering Conditions ---
        public List<IArcCondition> FactionTriggerConditions { get; set; } = new();

        // --- Inter-Faction Relationships ---
        public Dictionary<string, FactionRelationship> InterFactionRelationships { get; set; } = new();

        // --- Completion Criteria ---
        public IFactionArcCompletionCriteria FactionCompletionCriteria { get; set; }

        // --- Rewards/Consequences ---
        public List<string> Rewards { get; set; } = new();
        public List<string> Consequences { get; set; } = new();

        // --- Constructors ---
        public FactionArc(string title, string description, string narrativePurpose, string factionId, string factionName, string factionDescription, string factionEmblem)
            : base(title, description, narrativePurpose)
        {
            FactionId = factionId;
            FactionName = factionName;
            FactionDescription = factionDescription;
            FactionEmblem = factionEmblem;
        }

        // --- Validation Logic ---
        public void Validate(List<FactionArc> allFactionArcs, List<GlobalArc> allGlobalArcs)
        {
            base.Validate(allGlobalArcs);
            if (string.IsNullOrWhiteSpace(FactionId)) throw new ArgumentException("FactionId is required");
            if (string.IsNullOrWhiteSpace(FactionName)) throw new ArgumentException("FactionName is required");
            if (FactionCompletionCriteria == null) throw new ArgumentException("FactionCompletionCriteria is required");
            // Validate progression stages
            if (FactionStages == null || FactionStages.Count == 0) throw new ArgumentException("At least one FactionArcStage is required");
            // Validate relationships
            foreach (var rel in InterFactionRelationships.Values)
                rel.Validate();
            // Prevent circular dependencies
            if (HasCircularDependency(allFactionArcs, new HashSet<string>()))
                throw new InvalidOperationException($"Circular dependency detected for faction arc {Id}");
        }

        private bool HasCircularDependency(List<FactionArc> allFactionArcs, HashSet<string> visited)
        {
            if (visited.Contains(Id)) return true;
            visited.Add(Id);
            foreach (var rel in InterFactionRelationships.Values)
            {
                if (!string.IsNullOrEmpty(rel.RelatedFactionArcId))
                {
                    var depArc = allFactionArcs.Find(a => a.Id == rel.RelatedFactionArcId);
                    if (depArc != null && depArc.HasCircularDependency(allFactionArcs, visited))
                        return true;
                }
            }
            visited.Remove(Id);
            return false;
        }

        // --- Progression Logic ---
        public void ProgressFactionStage()
        {
            if (CurrentFactionStageIndex < FactionStages.Count - 1)
                CurrentFactionStageIndex++;
        }

        public bool IsFactionArcComplete(GameState state)
        {
            return FactionCompletionCriteria?.IsMet(state, this) ?? false;
        }
    }

    /// <summary>
    /// Represents a stage in a faction arc.
    /// </summary>
    [Serializable]
    public class FactionArcStage
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new();
        public FactionArcStage(string name, string description)
        {
            Name = name;
            Description = description;
        }
    }

    /// <summary>
    /// Represents a relationship to another faction arc.
    /// </summary>
    [Serializable]
    public class FactionRelationship
    {
        public string RelatedFactionArcId { get; set; }
        public string RelationshipType { get; set; } // e.g., Rivalry, Alliance
        public float Strength { get; set; }
        public void Validate()
        {
            if (string.IsNullOrWhiteSpace(RelatedFactionArcId)) throw new ArgumentException("RelatedFactionArcId is required");
            if (string.IsNullOrWhiteSpace(RelationshipType)) throw new ArgumentException("RelationshipType is required");
        }
    }

    /// <summary>
    /// Interface for faction arc completion criteria.
    /// </summary>
    public interface IFactionArcCompletionCriteria
    {
        bool IsMet(GameState state, FactionArc arc);
    }
}