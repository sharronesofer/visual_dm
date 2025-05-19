using System;
using System.Collections.Generic;

namespace VisualDM.Systems.Quest
{
    /// <summary>
    /// Provides a clean API for managing quests, states, progress, rewards, and archiving.
    /// </summary>
    public class QuestManagerAPI
    {
        private readonly Dictionary<string, Quest> _activeQuests = new Dictionary<string, Quest>();
        private readonly QuestArchiveManager _archiveManager = new QuestArchiveManager();
        private readonly QuestDependencyGraph _dependencyGraph = new QuestDependencyGraph();
        private readonly Dictionary<string, QuestProgress> _progress = new Dictionary<string, QuestProgress>();

        /// <summary>
        /// Adds a new quest to the system.
        /// </summary>
        public bool AddQuest(Quest quest, IEnumerable<string> objectiveIds)
        {
            if (_activeQuests.ContainsKey(quest.QuestId)) return false;
            _activeQuests[quest.QuestId] = quest;
            _progress[quest.QuestId] = new QuestProgress(quest.QuestId, objectiveIds);
            return true;
        }

        /// <summary>
        /// Removes a quest from the system and archives it.
        /// </summary>
        public bool ArchiveQuest(string questId)
        {
            if (_activeQuests.TryGetValue(questId, out var quest))
            {
                _archiveManager.ArchiveQuest(quest);
                _activeQuests.Remove(questId);
                _progress.Remove(questId);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Restores an archived quest to active quests.
        /// </summary>
        public bool RestoreQuest(string questId)
        {
            if (_archiveManager.RestoreQuest(questId, out var quest))
            {
                _activeQuests[quest.QuestId] = quest;
                // Progress restoration logic can be added here
                return true;
            }
            return false;
        }

        /// <summary>
        /// Gets the current state of a quest.
        /// </summary>
        public QuestState? GetQuestState(string questId)
        {
            if (_activeQuests.TryGetValue(questId, out var quest))
                return quest.StateMachine.CurrentState;
            return null;
        }

        /// <summary>
        /// Attempts to transition a quest to a new state.
        /// </summary>
        public bool TryTransitionQuestState(string questId, QuestState newState)
        {
            if (_activeQuests.TryGetValue(questId, out var quest))
                return quest.StateMachine.TryTransition(newState);
            return false;
        }

        /// <summary>
        /// Updates quest progress for a specific objective.
        /// </summary>
        public bool UpdateQuestProgress(string questId, string objectiveId, float progress)
        {
            if (_progress.TryGetValue(questId, out var prog))
            {
                prog.UpdateProgress(objectiveId, progress);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Claims a reward for a quest.
        /// </summary>
        public bool ClaimReward(string questId, string rewardId)
        {
            if (_activeQuests.TryGetValue(questId, out var quest))
            {
                foreach (var reward in quest.Rewards)
                {
                    if (reward.RewardId == rewardId && reward.State == QuestRewardState.Unclaimed)
                    {
                        reward.Claim();
                        return true;
                    }
                }
            }
            return false;
        }

        /// <summary>
        /// Adds a dependency between two quests.
        /// </summary>
        public bool AddDependency(string questId, string prerequisiteId)
        {
            return _dependencyGraph.AddDependency(questId, prerequisiteId);
        }

        /// <summary>
        /// Removes a dependency between two quests.
        /// </summary>
        public void RemoveDependency(string questId, string prerequisiteId)
        {
            _dependencyGraph.RemoveDependency(questId, prerequisiteId);
        }

        /// <summary>
        /// Gets all prerequisites for a quest.
        /// </summary>
        public IEnumerable<string> GetPrerequisites(string questId)
        {
            return _dependencyGraph.GetPrerequisites(questId);
        }

        /// <summary>
        /// Gets all dependents for a quest.
        /// </summary>
        public IEnumerable<string> GetDependents(string questId)
        {
            return _dependencyGraph.GetDependents(questId);
        }

        /// <summary>
        /// Purges expired archived quests based on retention policy.
        /// </summary>
        public void PurgeExpiredArchives()
        {
            _archiveManager.PurgeExpiredArchives();
        }

        // Additional extensibility points for future quest types, error handling, and integration can be added here.
    }
} 