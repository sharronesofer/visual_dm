using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Represents a requirement for a quest or quest stage.
    /// </summary>
    [Serializable]
    public class QuestRequirement
    {
        [SerializeField] private List<string> prerequisiteQuestIds;
        [SerializeField] private Dictionary<string, float> requiredPlayerStats;
        [SerializeField] private List<string> requiredWorldStates;

        /// <summary>
        /// List of prerequisite quest IDs that must be completed.
        /// </summary>
        public List<string> PrerequisiteQuestIds { get => prerequisiteQuestIds; set => prerequisiteQuestIds = value; }
        /// <summary>
        /// Required player stats (stat name to minimum value).
        /// </summary>
        public Dictionary<string, float> RequiredPlayerStats { get => requiredPlayerStats; set => requiredPlayerStats = value; }
        /// <summary>
        /// Required world state conditions (as string keys).
        /// </summary>
        public List<string> RequiredWorldStates { get => requiredWorldStates; set => requiredWorldStates = value; }

        public QuestRequirement()
        {
            prerequisiteQuestIds = new List<string>();
            requiredPlayerStats = new Dictionary<string, float>();
            requiredWorldStates = new List<string>();
        }
    }
} 