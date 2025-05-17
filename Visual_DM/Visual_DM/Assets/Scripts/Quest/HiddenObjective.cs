using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Base class for quest objectives.
    /// </summary>
    [Serializable]
    public class Objective
    {
        [SerializeField] private string id;
        [SerializeField] private string description;

        /// <summary>
        /// Unique identifier for the objective.
        /// </summary>
        public string Id { get => id; set => id = value; }
        /// <summary>
        /// Description of the objective.
        /// </summary>
        public string Description { get => description; set => description = value; }

        public Objective() { }
        public Objective(string id, string description)
        {
            this.id = id;
            this.description = description;
        }
    }

    /// <summary>
    /// Represents a hidden quest objective that is revealed upon meeting discovery conditions.
    /// </summary>
    [Serializable]
    public class HiddenObjective : Objective
    {
        [SerializeField] private bool isDiscovered;
        [SerializeField] private List<string> discoveryConditions;
        [SerializeField] private QuestReward bonusReward;

        /// <summary>
        /// Whether the objective has been discovered.
        /// </summary>
        public bool IsDiscovered { get => isDiscovered; set => isDiscovered = value; }
        /// <summary>
        /// List of discovery conditions (string keys for evaluation).
        /// </summary>
        public List<string> DiscoveryConditions { get => discoveryConditions; set => discoveryConditions = value; }
        /// <summary>
        /// Bonus reward for completing the hidden objective.
        /// </summary>
        public QuestReward BonusReward { get => bonusReward; set => bonusReward = value; }

        public HiddenObjective() : base()
        {
            discoveryConditions = new List<string>();
            bonusReward = new QuestReward();
            isDiscovered = false;
        }

        /// <summary>
        /// Checks if all discovery conditions are met using the provided evaluator.
        /// </summary>
        public bool CheckDiscovery(Func<string, bool> conditionEvaluator)
        {
            foreach (var cond in discoveryConditions)
            {
                if (!conditionEvaluator(cond))
                    return false;
            }
            return true;
        }

        /// <summary>
        /// Reveals the hidden objective if conditions are met.
        /// </summary>
        public bool TryReveal(Func<string, bool> conditionEvaluator)
        {
            if (!isDiscovered && CheckDiscovery(conditionEvaluator))
            {
                isDiscovered = true;
                return true;
            }
            return false;
        }
    }
} 