using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Manages all quests in the game. Singleton pattern.
    /// </summary>
    public class QuestManager : MonoBehaviour
    {
        private static QuestManager _instance;
        public static QuestManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("QuestManager");
                    _instance = go.AddComponent<QuestManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private readonly Dictionary<string, Quest> quests = new Dictionary<string, Quest>();

        /// <summary>
        /// Adds a quest to the manager.
        /// </summary>
        public void AddQuest(Quest quest)
        {
            try
            {
                if (quest == null || string.IsNullOrEmpty(quest.Id)) return;
                quests[quest.Id] = quest;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to add quest.", "QuestManager.AddQuest");
            }
        }

        /// <summary>
        /// Removes a quest by id.
        /// </summary>
        public bool RemoveQuest(string questId)
        {
            try
            {
                return quests.Remove(questId);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to remove quest.", "QuestManager.RemoveQuest");
                return false;
            }
        }

        /// <summary>
        /// Finds a quest by id.
        /// </summary>
        public Quest FindQuest(string questId)
        {
            try
            {
                quests.TryGetValue(questId, out var quest);
                return quest;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to find quest.", "QuestManager.FindQuest");
                return null;
            }
        }

        /// <summary>
        /// Returns all quests.
        /// </summary>
        public List<Quest> GetAllQuests()
        {
            try
            {
                return new List<Quest>(quests.Values);
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to get all quests.", "QuestManager.GetAllQuests");
                return new List<Quest>();
            }
        }

        /// <summary>
        /// Clears all quests (for testing or reset).
        /// </summary>
        public void ClearQuests()
        {
            try
            {
                quests.Clear();
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to clear quests.", "QuestManager.ClearQuests");
            }
        }
    }
} 