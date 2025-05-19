using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.Quest
{
    /// <summary>
    /// Represents the status of a quest.
    /// </summary>
    public enum QuestStatus
    {
        NotStarted,
        InProgress,
        Completed,
        Failed
    }

    /// <summary>
    /// Placeholder for world impact data.
    /// </summary>
    [Serializable]
    public struct WorldImpact
    {
        // Add fields for world state changes, e.g., affected factions, locations, etc.
    }

    /// <summary>
    /// Represents a quest entity with state, versioning, and timestamps.
    /// </summary>
    /// <remarks>
    /// Quests manage their own state transitions and can trigger world impacts and rewards. Integrates with quest manager and event systems.
    /// </remarks>
    /// <example>
    /// <code>
    /// var quest = new Quest { Id = "quest_001", Title = "Find the Artifact" };
    /// quest.Status = QuestStatus.InProgress;
    /// quest.RevealHiddenObjectives(condition => PlayerHasItem(condition));
    /// </code>
    /// </example>
    [Serializable]
    public class Quest
    {
        [SerializeField] private string id;
        [SerializeField] private string title;
        [SerializeField] private string description;
        [SerializeField] private List<QuestStage> stages;
        [SerializeField] private List<QuestRequirement> requirements;
        [SerializeField] private List<QuestReward> rewards;
        [SerializeField] private WorldImpact worldImpact;
        [SerializeField] private QuestStatus status;
        [SerializeField] private int difficulty;
        [SerializeField] private List<HiddenObjective> hiddenObjectives;
        [SerializeField] private Dictionary<string, object> metadata;
        [SerializeField] public string QuestId { get => id; set => id = value; }
        [SerializeField] public string Title { get => title; set => title = value; }
        [SerializeField] public string Description { get => description; set => description = value; }
        [SerializeField] public List<QuestStage> Stages { get => stages; set => stages = value; }
        [SerializeField] public List<QuestRequirement> Requirements { get => requirements; set => requirements = value; }
        [SerializeField] public List<QuestReward> Rewards { get => rewards; set => rewards = value; }
        [SerializeField] public WorldImpact WorldImpactData { get => worldImpact; set => worldImpact = value; }
        [SerializeField] public QuestStatus Status { get => status; set => status = value; }
        [SerializeField] public int Difficulty { get => difficulty; set => difficulty = value; }
        [SerializeField] public List<HiddenObjective> HiddenObjectives { get => hiddenObjectives; set => hiddenObjectives = value; }
        [SerializeField] public QuestStateMachine StateMachine { get; private set; }
        [SerializeField] public int Version { get; set; }
        [SerializeField] public DateTime CreatedAt { get; set; }
        [SerializeField] public DateTime UpdatedAt { get; set; }
        [SerializeField] public DateTime? ExpiresAt { get; set; }
        [SerializeField] public QuestVersionHistory VersionHistory { get; private set; }
        [SerializeField] public Dictionary<string, object> Metadata { get => metadata; set => metadata = value; }

        public Quest(string questId, string title, string description, QuestState initialState = QuestState.Locked)
        {
            QuestId = questId;
            Title = title;
            Description = description;
            StateMachine = new QuestStateMachine(initialState);
            Version = 1;
            CreatedAt = DateTime.UtcNow;
            UpdatedAt = DateTime.UtcNow;
            ExpiresAt = null;
            VersionHistory = new QuestVersionHistory();
            VersionHistory.AddVersion(this);
            stages = new List<QuestStage>();
            requirements = new List<QuestRequirement>();
            rewards = new List<QuestReward>();
            hiddenObjectives = new List<HiddenObjective>();
            status = QuestStatus.NotStarted;
            difficulty = 1;
            metadata = new Dictionary<string, object>();
        }

        public void Update(string newTitle, string newDescription)
        {
            Title = newTitle;
            Description = newDescription;
            Version++;
            UpdatedAt = DateTime.UtcNow;
            VersionHistory.AddVersion(this);
        }

        /// <summary>
        /// Checks and reveals hidden objectives if their discovery conditions are met.
        /// </summary>
        /// <param name="conditionEvaluator">A function that evaluates discovery conditions for hidden objectives.</param>
        /// <remarks>
        /// This method should be called after quest state changes or player actions that may reveal new objectives.
        /// </remarks>
        /// <example>
        /// <code>
        /// quest.RevealHiddenObjectives(condition => PlayerHasItem(condition));
        /// </code>
        /// </example>
        public void RevealHiddenObjectives(Func<string, bool> conditionEvaluator)
        {
            foreach (var hidden in hiddenObjectives)
            {
                hidden.TryReveal(conditionEvaluator);
            }
        }

        public bool RollbackToVersion(int version)
        {
            return VersionHistory.Rollback(this, version);
        }

        public bool IsExpired()
        {
            return ExpiresAt.HasValue && DateTime.UtcNow > ExpiresAt.Value;
        }

        public void ScheduleExpiration(DateTime expiresAt)
        {
            ExpiresAt = expiresAt.ToUniversalTime();
        }
    }
} 