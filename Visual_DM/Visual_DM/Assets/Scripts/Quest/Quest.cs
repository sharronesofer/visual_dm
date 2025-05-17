using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
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
    /// Represents a quest in the game.
    /// </summary>
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

        /// <summary>
        /// Unique identifier for the quest.
        /// </summary>
        public string Id { get => id; set => id = value; }
        /// <summary>
        /// Title of the quest.
        /// </summary>
        public string Title { get => title; set => title = value; }
        /// <summary>
        /// Description of the quest.
        /// </summary>
        public string Description { get => description; set => description = value; }
        /// <summary>
        /// List of quest stages.
        /// </summary>
        public List<QuestStage> Stages { get => stages; set => stages = value; }
        /// <summary>
        /// List of quest requirements.
        /// </summary>
        public List<QuestRequirement> Requirements { get => requirements; set => requirements = value; }
        /// <summary>
        /// List of quest rewards.
        /// </summary>
        public List<QuestReward> Rewards { get => rewards; set => rewards = value; }
        /// <summary>
        /// World impact of completing the quest.
        /// </summary>
        public WorldImpact WorldImpactData { get => worldImpact; set => worldImpact = value; }
        /// <summary>
        /// Current status of the quest.
        /// </summary>
        public QuestStatus Status { get => status; set => status = value; }
        /// <summary>
        /// Difficulty rating of the quest.
        /// </summary>
        public int Difficulty { get => difficulty; set => difficulty = value; }
        /// <summary>
        /// List of hidden objectives for the quest (global, not per stage).
        /// </summary>
        public List<HiddenObjective> HiddenObjectives { get => hiddenObjectives; set => hiddenObjectives = value; }

        public Quest()
        {
            stages = new List<QuestStage>();
            requirements = new List<QuestRequirement>();
            rewards = new List<QuestReward>();
            hiddenObjectives = new List<HiddenObjective>();
            status = QuestStatus.NotStarted;
            difficulty = 1;
        }

        /// <summary>
        /// Checks and reveals hidden objectives if their discovery conditions are met.
        /// </summary>
        public void RevealHiddenObjectives(Func<string, bool> conditionEvaluator)
        {
            foreach (var hidden in hiddenObjectives)
            {
                hidden.TryReveal(conditionEvaluator);
            }
        }
    }
} 