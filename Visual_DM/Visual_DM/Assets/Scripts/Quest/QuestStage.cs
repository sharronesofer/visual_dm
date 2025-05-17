using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Status of a quest stage.
    /// </summary>
    public enum QuestStageStatus
    {
        NotStarted,
        InProgress,
        Completed,
        Failed
    }

    /// <summary>
    /// Represents a single stage within a quest.
    /// </summary>
    [Serializable]
    public class QuestStage
    {
        [SerializeField] private string id;
        [SerializeField] private List<string> objectives;
        [SerializeField] private List<string> completionConditions;
        [SerializeField] private List<string> nextStageIds;
        [SerializeField] private QuestStageStatus status;
        [SerializeField] private List<HiddenObjective> hiddenObjectives;

        /// <summary>
        /// Unique identifier for the stage.
        /// </summary>
        public string Id { get => id; set => id = value; }
        /// <summary>
        /// List of objectives for this stage.
        /// </summary>
        public List<string> Objectives { get => objectives; set => objectives = value; }
        /// <summary>
        /// List of completion conditions for this stage.
        /// </summary>
        public List<string> CompletionConditions { get => completionConditions; set => completionConditions = value; }
        /// <summary>
        /// List of next stage IDs for branching.
        /// </summary>
        public List<string> NextStageIds { get => nextStageIds; set => nextStageIds = value; }
        /// <summary>
        /// List of hidden objectives for this stage.
        /// </summary>
        public List<HiddenObjective> HiddenObjectives { get => hiddenObjectives; set => hiddenObjectives = value; }
        /// <summary>
        /// Current status of the stage.
        /// </summary>
        public QuestStageStatus Status { get => status; set => status = value; }

        public QuestStage()
        {
            objectives = new List<string>();
            completionConditions = new List<string>();
            nextStageIds = new List<string>();
            hiddenObjectives = new List<HiddenObjective>();
            status = QuestStageStatus.NotStarted;
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