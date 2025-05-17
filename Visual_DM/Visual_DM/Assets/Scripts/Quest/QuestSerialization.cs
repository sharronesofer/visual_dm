using System;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Provides serialization and deserialization helpers for Quest and QuestTemplate objects.
    /// </summary>
    public static class QuestSerialization
    {
        /// <summary>
        /// Serializes a Quest object to JSON.
        /// </summary>
        public static string SerializeQuest(Quest quest)
        {
            return JsonUtility.ToJson(quest, true);
        }

        /// <summary>
        /// Deserializes a Quest object from JSON.
        /// </summary>
        public static Quest DeserializeQuest(string json)
        {
            return JsonUtility.FromJson<Quest>(json);
        }

        /// <summary>
        /// Serializes a QuestTemplate object to JSON.
        /// </summary>
        public static string SerializeQuestTemplate(QuestTemplate template)
        {
            return JsonUtility.ToJson(template, true);
        }

        /// <summary>
        /// Deserializes a QuestTemplate object from JSON.
        /// </summary>
        public static QuestTemplate DeserializeQuestTemplate(string json)
        {
            return JsonUtility.FromJson<QuestTemplate>(json);
        }
    }
} 