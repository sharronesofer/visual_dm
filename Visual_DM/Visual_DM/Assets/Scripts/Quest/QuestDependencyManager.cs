using System;
using System.Collections.Generic;

namespace VisualDM.Quest
{
    /// <summary>
    /// Manages quest prerequisites, chains, and mutual exclusivity.
    /// </summary>
    public class QuestDependencyManager
    {
        private readonly Dictionary<string, List<string>> prerequisites = new Dictionary<string, List<string>>();
        private readonly Dictionary<string, List<string>> questChains = new Dictionary<string, List<string>>();
        private readonly Dictionary<string, List<string>> mutualExclusives = new Dictionary<string, List<string>>();

        /// <summary>
        /// Registers prerequisite quest IDs for a quest.
        /// </summary>
        public void RegisterPrerequisites(string questId, List<string> prereqIds)
        {
            prerequisites[questId] = prereqIds ?? new List<string>();
        }

        /// <summary>
        /// Registers a quest chain (quests unlocked after this quest is completed).
        /// </summary>
        public void RegisterQuestChain(string questId, List<string> nextQuestIds)
        {
            questChains[questId] = nextQuestIds ?? new List<string>();
        }

        /// <summary>
        /// Registers mutually exclusive quests.
        /// </summary>
        public void RegisterMutualExclusives(string questId, List<string> exclusiveIds)
        {
            mutualExclusives[questId] = exclusiveIds ?? new List<string>();
        }

        /// <summary>
        /// Checks if a quest is available for the player.
        /// </summary>
        public bool IsQuestAvailable(string questId, Func<string, bool> isQuestCompleted, Func<string, bool> playerStatCheck = null, Func<string, bool> worldStateCheck = null)
        {
            // Check prerequisites
            if (prerequisites.TryGetValue(questId, out var prereqs))
            {
                foreach (var prereq in prereqs)
                {
                    if (!isQuestCompleted(prereq))
                        return false;
                }
            }
            // Check player stat requirements if provided
            if (playerStatCheck != null && !playerStatCheck(questId))
                return false;
            // Check world state requirements if provided
            if (worldStateCheck != null && !worldStateCheck(questId))
                return false;
            // Check mutual exclusivity
            if (mutualExclusives.TryGetValue(questId, out var exclusives))
            {
                foreach (var excl in exclusives)
                {
                    if (isQuestCompleted(excl))
                        return false;
                }
            }
            return true;
        }

        /// <summary>
        /// Unlocks quests in a chain after a quest is completed.
        /// </summary>
        public List<string> UnlockQuestsInChain(string completedQuestId)
        {
            if (questChains.TryGetValue(completedQuestId, out var nextQuests))
                return new List<string>(nextQuests);
            return new List<string>();
        }

        /// <summary>
        /// Locks mutually exclusive quests when one is accepted.
        /// </summary>
        public List<string> LockIncompatibleQuests(string acceptedQuestId)
        {
            if (mutualExclusives.TryGetValue(acceptedQuestId, out var exclusives))
                return new List<string>(exclusives);
            return new List<string>();
        }
    }
} 