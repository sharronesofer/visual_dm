using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    public enum QuestRewardType
    {
        Item,
        Currency,
        Experience,
        Ability,
        Other
    }

    public enum QuestRewardState
    {
        Unclaimed,
        Claimed,
        Expired
    }

    /// <summary>
    /// Represents a reward for completing a quest or quest stage.
    /// </summary>
    [Serializable]
    public class QuestReward
    {
        [SerializeField] private List<string> itemIds;
        [SerializeField] private Dictionary<string, float> reputationRewards;
        [SerializeField] private float experience;
        [SerializeField] private List<string> specialRewards;
        public QuestRewardType Type { get; set; }
        public string RewardId { get; set; }
        public int Amount { get; set; }
        public QuestRewardState State { get; set; }
        public DateTime? Expiry { get; set; }

        /// <summary>
        /// List of item IDs rewarded.
        /// </summary>
        public List<string> ItemIds { get => itemIds; set => itemIds = value; }
        /// <summary>
        /// Reputation rewards (faction name to value).
        /// </summary>
        public Dictionary<string, float> ReputationRewards { get => reputationRewards; set => reputationRewards = value; }
        /// <summary>
        /// Experience points rewarded.
        /// </summary>
        public float Experience { get => experience; set => experience = value; }
        /// <summary>
        /// List of special rewards (e.g., abilities, unlocks).
        /// </summary>
        public List<string> SpecialRewards { get => specialRewards; set => specialRewards = value; }

        public QuestReward()
        {
            itemIds = new List<string>();
            reputationRewards = new Dictionary<string, float>();
            specialRewards = new List<string>();
            experience = 0f;
            State = QuestRewardState.Unclaimed;
            Expiry = null;
        }

        public void Claim()
        {
            if (State == QuestRewardState.Unclaimed && !IsExpired())
                State = QuestRewardState.Claimed;
        }

        public bool IsExpired()
        {
            return Expiry.HasValue && DateTime.UtcNow > Expiry.Value;
        }
    }
} 