using System;
using UnityEngine;

namespace VisualDM.Systems.Quest
{
    /// <summary>
    /// Represents a reward for completing a quest or objective.
    /// </summary>
    [Serializable]
    public class QuestReward
    {
        [SerializeField] public int Experience { get; set; }
        [SerializeField] public int Gold { get; set; }
        [SerializeField] public string ItemId { get; set; }
        // Extend with more reward types as needed

        public QuestReward()
        {
            Experience = 0;
            Gold = 0;
            ItemId = string.Empty;
        }
    }
} 