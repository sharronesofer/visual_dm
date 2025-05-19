using System;
using System.Collections.Generic;
using VisualDM.Core;

namespace VisualDM.Systems.Narrative
{
    /// <summary>
    /// Represents a global narrative arc with progression, conditions, and relationships.
    /// </summary>
    public class GlobalArc
    {
        /// <summary>Unique identifier for the arc.</summary>
        public string Id { get; }
        /// <summary>Title of the arc.</summary>
        public string Title { get; set; }
        /// <summary>Description of the arc's narrative purpose.</summary>
        public string Description { get; set; }
        /// <summary>Narrative purpose or high-level goal.</summary>
        public string NarrativePurpose { get; set; }
        /// <summary>List of progression stages (setup, rising action, climax, resolution).</summary>
        public List<ArcStage> Stages { get; set; }
        /// <summary>Current stage index.</summary>
        public int CurrentStageIndex { get; private set; }
        /// <summary>Flexible rule-based trigger conditions for arc activation.</summary>
        public List<IArcCondition> TriggerConditions { get; set; }
        /// <summary>Completion criteria for the arc.</summary>
        public IArcCompletionCriteria CompletionCriteria { get; set; }
        /// <summary>Relationships to other systems (characters, locations, quests, items).</summary>
        public ArcRelationships Relationships { get; set; }
        /// <summary>Metadata for narrative categorization (theme, tone, intensity).</summary>
        public ArcMetadata Metadata { get; set; }
        /// <summary>Version for arc evolution/versioning.</summary>
        public int Version { get; set; }

        /// <summary>Tracks arcs this arc depends on (for circular dependency prevention).</summary>
        public List<string> DependencyArcIds { get; set; }

        // Tick system integration
        public TickConfig TickConfiguration { get; set; } // New: tick parameters per arc
        public ArcTickProgressionState ProgressionState { get; set; } // New: tick-based progression state

        public GlobalArc(string title, string description, string narrativePurpose)
        {
            Id = IdGenerator.GenerateGuid();
            Title = title;
            Description = description;
            NarrativePurpose = narrativePurpose;
            Stages = new List<ArcStage>();
            TriggerConditions = new List<IArcCondition>();
            Relationships = new ArcRelationships();
            Metadata = new ArcMetadata();
            DependencyArcIds = new List<string>();
            Version = 1;
            CurrentStageIndex = 0;
            TickConfiguration = new TickConfig();
            ProgressionState = new ArcTickProgressionState();
        }

        /// <summary>
        /// Validates the arc's properties and relationships.
        /// </summary>
        public void Validate(List<GlobalArc> allArcs)
        {
            if (string.IsNullOrWhiteSpace(Title)) throw new ArgumentException("Title is required");
            if (Stages == null || Stages.Count == 0) throw new ArgumentException("At least one stage is required");
            if (CompletionCriteria == null) throw new ArgumentException("Completion criteria is required");
            // Prevent circular dependencies
            if (HasCircularDependency(allArcs, new HashSet<string>()))
                throw new InvalidOperationException($"Circular dependency detected for arc {Id}");
        }

        private bool HasCircularDependency(List<GlobalArc> allArcs, HashSet<string> visited)
        {
            if (visited.Contains(Id)) return true;
            visited.Add(Id);
            foreach (var depId in DependencyArcIds)
            {
                var depArc = allArcs.Find(a => a.Id == depId);
                if (depArc != null && depArc.HasCircularDependency(allArcs, visited))
                    return true;
            }
            visited.Remove(Id);
            return false;
        }

        /// <summary>
        /// Progresses the arc to the next stage if possible.
        /// </summary>
        public void ProgressStage()
        {
            if (CurrentStageIndex < Stages.Count - 1)
                CurrentStageIndex++;
        }

        /// <summary>
        /// Checks if the arc is complete.
        /// </summary>
        public bool IsComplete(GameState state)
        {
            return CompletionCriteria?.IsMet(state, this) ?? false;
        }

        /// <summary>
        /// Updates the tick configuration for this arc, with validation.
        /// </summary>
        /// <param name="config">The new TickConfig to apply.</param>
        public void SetTickConfiguration(TickConfig config)
        {
            VisualDM.Systems.TickSystem.TickManager.ValidateTickConfig(config);
            TickConfiguration = config;
        }

        /// <summary>
        /// Resets the tick-based progression state for this arc.
        /// </summary>
        public void ResetTickProgressionState()
        {
            ProgressionState = new ArcTickProgressionState();
        }

        /// <summary>
        /// Checks if the arc is eligible for progression (not complete, not at final stage).
        /// </summary>
        public bool CanProgress()
        {
            return !IsComplete(null) && CurrentStageIndex < (Stages?.Count ?? 0) - 1;
        }
    }

    /// <summary>
    /// Represents a stage in a narrative arc.
    /// </summary>
    public class ArcStage
    {
        public string Name { get; set; }
        public string Description { get; set; }
        public Dictionary<string, object> Metadata { get; set; }
        public ArcStage(string name, string description)
        {
            Name = name;
            Description = description;
            Metadata = new Dictionary<string, object>();
        }
    }

    /// <summary>
    /// Interface for arc trigger conditions.
    /// </summary>
    public interface IArcCondition
    {
        bool IsMet(GameState state, GlobalArc arc);
    }

    /// <summary>
    /// Interface for arc completion criteria.
    /// </summary>
    public interface IArcCompletionCriteria
    {
        bool IsMet(GameState state, GlobalArc arc);
    }

    /// <summary>
    /// Relationships to other systems.
    /// </summary>
    public class ArcRelationships
    {
        public List<string> CharacterIds { get; set; } = new();
        public List<string> LocationIds { get; set; } = new();
        public List<string> QuestIds { get; set; } = new();
        public List<string> ItemIds { get; set; } = new();
    }

    /// <summary>
    /// Metadata for narrative categorization.
    /// </summary>
    public class ArcMetadata
    {
        public string Theme { get; set; }
        public string Tone { get; set; }
        public int Intensity { get; set; }
    }

    /// <summary>
    /// Configuration for tick-based progression of a Global Arc.
    /// </summary>
    public class TickConfig
    {
        /// <summary>Enable time-based progression for this arc.</summary>
        public bool EnableTimeBased { get; set; } = true;
        /// <summary>Interval in seconds between ticks (default: daily).</summary>
        public float TickIntervalSeconds { get; set; } = 86400f;
        /// <summary>Use in-game time (true) or real time (false).</summary>
        public bool UseGameTime { get; set; } = true;
        /// <summary>Enable event-based progression for this arc.</summary>
        public bool EnableEventBased { get; set; } = false;
        /// <summary>List of event types to listen for.</summary>
        public List<string> EventTypes { get; set; } = new();
        /// <summary>Number of events required to trigger progression.</summary>
        public int EventThreshold { get; set; } = 1;
        /// <summary>Enable compound event trigger (multiple events in sequence).</summary>
        public bool CompoundEventTrigger { get; set; } = false;
        /// <summary>Number of events required for compound trigger.</summary>
        public int CompoundEventCount { get; set; } = 0;
        /// <summary>Progression acceleration factor (based on player engagement).</summary>
        public float AccelerationFactor { get; set; } = 1.0f;
        /// <summary>Progression deceleration factor (based on player engagement).</summary>
        public float DecelerationFactor { get; set; } = 1.0f;
        /// <summary>Variable progression thresholds per arc stage (stage index -> threshold).</summary>
        public Dictionary<int, float> StageThresholds { get; set; } = new();
    }

    /// <summary>
    /// Tracks tick-based progression state for a Global Arc.
    /// </summary>
    public class ArcTickProgressionState
    {
        /// <summary>Time in seconds since the last tick.</summary>
        public float TimeSinceLastTick { get; set; } = 0f;
        /// <summary>Number of events since the last tick.</summary>
        public int EventsSinceLastTick { get; set; } = 0;
        /// <summary>Total number of ticks for this arc.</summary>
        public int TotalTicks { get; set; } = 0;
        /// <summary>Stage index at the last tick.</summary>
        public int LastTickedStage { get; set; } = 0;
        /// <summary>Timestamp of the last tick.</summary>
        public DateTime LastTickTime { get; set; } = DateTime.MinValue;
    }
}