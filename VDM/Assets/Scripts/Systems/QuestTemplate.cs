using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.Quest
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
        [SerializeField] private string arcType; // "Global", "Regional", "Faction", "Character"
        [SerializeField] private string questType; // "Collection", "Elimination", "Exploration", etc.
        [SerializeField] private List<string> objectiveTemplates; // Parameterized objectives

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
        public string ArcType { get => arcType; set => arcType = value; }
        public string QuestType { get => questType; set => questType = value; }
        public List<string> ObjectiveTemplates { get => objectiveTemplates; set => objectiveTemplates = value; }

        public QuestTemplate()
        {
            parameters = new Dictionary<string, object>();
            baseDifficulty = 1;
            objectiveTemplates = new List<string>();
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

            // Apply arc and quest type
            if (mergedParams.TryGetValue("arcType", out var arcTypeVal) && arcTypeVal is string)
                quest.Description += $"\n[Arc Type: {arcTypeVal}]";
            if (mergedParams.TryGetValue("questType", out var questTypeVal) && questTypeVal is string)
                quest.Description += $"\n[Quest Type: {questTypeVal}]";

            // Handle parameterized objectives by quest type
            if (mergedParams.TryGetValue("objectives", out var objObj) && objObj is List<string> objectives)
            {
                var stage = new QuestStage { Id = Guid.NewGuid().ToString(), Objectives = new List<string>(objectives) };
                quest.Stages.Add(stage);
            }
            else if (objectiveTemplates != null && objectiveTemplates.Count > 0)
            {
                var stage = new QuestStage { Id = Guid.NewGuid().ToString(), Objectives = new List<string>(objectiveTemplates) };
                quest.Stages.Add(stage);
            }

            // Existing parameter handling (title, description, difficulty, stages, requirements, rewards)
            if (mergedParams.TryGetValue("title", out var customTitle) && customTitle is string)
                quest.Title = (string)customTitle;
            if (mergedParams.TryGetValue("description", out var customDesc) && customDesc is string)
                quest.Description = (string)customDesc;
            if (mergedParams.TryGetValue("difficulty", out var customDiff) && customDiff is int)
                quest.Difficulty = (int)customDiff;

            if (mergedParams.TryGetValue("stages", out var stagesObj) && stagesObj is List<string> stageNames)
            {
                foreach (var stageName in stageNames)
                {
                    quest.Stages.Add(new QuestStage { Id = Guid.NewGuid().ToString(), Objectives = new List<string> { stageName } });
                }
            }
            if (mergedParams.TryGetValue("requirements", out var reqsObj) && reqsObj is List<string> reqs)
            {
                foreach (var req in reqs)
                {
                    quest.Requirements.Add(new QuestRequirement { Requirement = req });
                }
            }
            if (mergedParams.TryGetValue("rewards", out var rewardsObj) && rewardsObj is List<string> rewards)
            {
                foreach (var reward in rewards)
                {
                    quest.Rewards.Add(new QuestReward { Reward = reward });
                }
            }

            return quest;
        }
    }
}