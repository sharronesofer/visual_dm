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
            if (quest == null || string.IsNullOrEmpty(quest.Id)) return;
            quests[quest.Id] = quest;
        }

        /// <summary>
        /// Removes a quest by id.
        /// </summary>
        public bool RemoveQuest(string questId)
        {
            return quests.Remove(questId);
        }

        /// <summary>
        /// Finds a quest by id.
        /// </summary>
        public Quest FindQuest(string questId)
        {
            quests.TryGetValue(questId, out var quest);
            return quest;
        }

        /// <summary>
        /// Returns all quests.
        /// </summary>
        public List<Quest> GetAllQuests()
        {
            return new List<Quest>(quests.Values);
        }

        /// <summary>
        /// Clears all quests (for testing or reset).
        /// </summary>
        public void ClearQuests()
        {
            quests.Clear();
        }
    }
} 