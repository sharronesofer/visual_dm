using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Manages quest stage progression, completion, and branching.
    /// </summary>
    public class QuestStageManager : MonoBehaviour
    {
        private readonly Dictionary<string, QuestStage> activeStages = new Dictionary<string, QuestStage>();

        /// <summary>
        /// Event triggered when a stage is completed.
        /// </summary>
        public event Action<QuestStage> OnStageCompleted;
        /// <summary>
        /// Event triggered when a stage is activated.
        /// </summary>
        public event Action<QuestStage> OnStageActivated;

        /// <summary>
        /// Activates a quest stage by id.
        /// </summary>
        public void ActivateStage(QuestStage stage)
        {
            if (stage == null || activeStages.ContainsKey(stage.Id)) return;
            stage.Status = QuestStageStatus.InProgress;
            activeStages[stage.Id] = stage;
            OnStageActivated?.Invoke(stage);
        }

        /// <summary>
        /// Deactivates a quest stage by id.
        /// </summary>
        public void DeactivateStage(string stageId)
        {
            if (activeStages.ContainsKey(stageId))
                activeStages.Remove(stageId);
        }

        /// <summary>
        /// Checks if a stage's completion conditions are met and completes it if so.
        /// </summary>
        public void CheckAndCompleteStage(QuestStage stage, Func<string, bool> conditionEvaluator)
        {
            if (stage == null || stage.Status != QuestStageStatus.InProgress) return;
            bool allMet = true;
            foreach (var cond in stage.CompletionConditions)
            {
                if (!conditionEvaluator(cond))
                {
                    allMet = false;
                    break;
                }
            }
            if (allMet)
            {
                stage.Status = QuestStageStatus.Completed;
                OnStageCompleted?.Invoke(stage);
                DeactivateStage(stage.Id);
                HandleBranching(stage);
            }
        }

        /// <summary>
        /// Handles branching to next stages after completion.
        /// </summary>
        private void HandleBranching(QuestStage completedStage)
        {
            // Example: Activate all next stages (customize as needed)
            foreach (var nextId in completedStage.NextStageIds)
            {
                // Lookup and activate next stage (integration with QuestManager required)
                // This is a placeholder; actual implementation should fetch the next stage from the quest
            }
        }

        /// <summary>
        /// Returns all currently active stages.
        /// </summary>
        public List<QuestStage> GetActiveStages()
        {
            return new List<QuestStage>(activeStages.Values);
        }

        /// <summary>
        /// Clears all active stages (for reset/testing).
        /// </summary>
        public void ClearActiveStages()
        {
            activeStages.Clear();
        }
    }
} 