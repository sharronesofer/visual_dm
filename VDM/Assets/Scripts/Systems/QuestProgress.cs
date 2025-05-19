using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Quest
{
    /// <summary>
    /// Tracks quest progress for multiple objective types, supports partial completion and persistence.
    /// </summary>
    public class QuestProgress
    {
        public string QuestId { get; private set; }
        public Dictionary<string, float> ObjectiveProgress { get; private set; } // objectiveId -> progress (0.0-1.0)
        public bool IsPartiallyComplete => GetCompletionFraction() > 0f && GetCompletionFraction() < 1f;
        public bool IsComplete => GetCompletionFraction() >= 1f;
        public DateTime LastUpdated { get; private set; }

        public QuestProgress(string questId, IEnumerable<string> objectiveIds)
        {
            QuestId = questId;
            ObjectiveProgress = new Dictionary<string, float>();
            foreach (var id in objectiveIds)
                ObjectiveProgress[id] = 0f;
            LastUpdated = DateTime.UtcNow;
        }

        public void UpdateProgress(string objectiveId, float progress)
        {
            if (!ObjectiveProgress.ContainsKey(objectiveId)) return;
            ObjectiveProgress[objectiveId] = Math.Clamp(progress, 0f, 1f);
            LastUpdated = DateTime.UtcNow;
        }

        public float GetCompletionFraction()
        {
            if (ObjectiveProgress.Count == 0) return 0f;
            float sum = 0f;
            foreach (var v in ObjectiveProgress.Values) sum += v;
            return sum / ObjectiveProgress.Count;
        }

        public Dictionary<string, float> GetProgressForUI()
        {
            return new Dictionary<string, float>(ObjectiveProgress);
        }
    }
} 