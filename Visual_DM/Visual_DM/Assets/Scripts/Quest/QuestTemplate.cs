using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Represents a template for generating quests.
    /// </summary>
    [Serializable]
    public class QuestTemplate
    {
        [SerializeField] private string templateId;
        [SerializeField] private string baseTitle;
        [SerializeField] private string baseDescription;
        [SerializeField] private int baseDifficulty;
        [SerializeField] private Dictionary<string, object> parameters;

        /// <summary>
        /// Unique identifier for the template.
        /// </summary>
        public string TemplateId { get => templateId; set => templateId = value; }
        /// <summary>
        /// Base title for generated quests.
        /// </summary>
        public string BaseTitle { get => baseTitle; set => baseTitle = value; }
        /// <summary>
        /// Base description for generated quests.
        /// </summary>
        public string BaseDescription { get => baseDescription; set => baseDescription = value; }
        /// <summary>
        /// Base difficulty for generated quests.
        /// </summary>
        public int BaseDifficulty { get => baseDifficulty; set => baseDifficulty = value; }
        /// <summary>
        /// Parameters for customizing quest generation.
        /// </summary>
        public Dictionary<string, object> Parameters { get => parameters; set => parameters = value; }

        public QuestTemplate()
        {
            parameters = new Dictionary<string, object>();
            baseDifficulty = 1;
        }

        /// <summary>
        /// Generates a Quest instance from this template with the given parameters.
        /// </summary>
        /// <param name="customParams">Parameters to override or extend the template.</param>
        /// <returns>A new Quest instance.</returns>
        public Quest GenerateQuest(Dictionary<string, object> customParams = null)
        {
            var quest = new Quest
            {
                Id = System.Guid.NewGuid().ToString(),
                Title = baseTitle,
                Description = baseDescription,
                Difficulty = baseDifficulty,
                Stages = new List<QuestStage>(),
                Requirements = new List<QuestRequirement>(),
                Rewards = new List<QuestReward>(),
                Status = QuestStatus.NotStarted
            };

            // Merge parameters
            var mergedParams = new Dictionary<string, object>(parameters);
            if (customParams != null)
            {
                foreach (var kvp in customParams)
                {
                    mergedParams[kvp.Key] = kvp.Value;
                }
            }

            // Example: apply parameters to quest (expand as needed)
            if (mergedParams.TryGetValue("title", out var customTitle) && customTitle is string)
                quest.Title = (string)customTitle;
            if (mergedParams.TryGetValue("description", out var customDesc) && customDesc is string)
                quest.Description = (string)customDesc;
            if (mergedParams.TryGetValue("difficulty", out var customDiff) && customDiff is int)
                quest.Difficulty = (int)customDiff;

            // TODO: Add logic to generate stages, requirements, rewards, etc. from parameters

            return quest;
        }
    }
} 