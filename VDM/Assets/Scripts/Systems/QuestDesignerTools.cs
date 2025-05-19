using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems.Quest
{
    [Serializable]
    public class RewardTemplate
    {
        public string Name;
        public float BaseXP;
        public int BaseGold;
        public List<string> ItemIds = new();
        public Dictionary<string, float> Reputation = new();
    }

    [Serializable]
    public class ConsequenceTemplate
    {
        public string Name;
        public ConsequenceSeverity Severity;
        public ConsequenceCategory Category;
        public string Description;
        public object Payload;
    }

    public class ValidationResult
    {
        public bool IsValid;
        public List<string> Errors = new();
        public List<string> Warnings = new();
    }

    public static class QuestDesignerTools
    {
        public static ValidationResult ValidateRewardTemplate(RewardTemplate template)
        {
            var result = new ValidationResult { IsValid = true };
            if (string.IsNullOrEmpty(template.Name))
            {
                result.IsValid = false;
                result.Errors.Add("RewardTemplate must have a name.");
            }
            if (template.BaseXP < 0)
            {
                result.IsValid = false;
                result.Errors.Add("BaseXP cannot be negative.");
            }
            if (template.BaseGold < 0)
            {
                result.IsValid = false;
                result.Errors.Add("BaseGold cannot be negative.");
            }
            // Add more validation as needed
            return result;
        }

        public static ValidationResult ValidateConsequenceTemplate(ConsequenceTemplate template)
        {
            var result = new ValidationResult { IsValid = true };
            if (string.IsNullOrEmpty(template.Name))
            {
                result.IsValid = false;
                result.Errors.Add("ConsequenceTemplate must have a name.");
            }
            if (string.IsNullOrEmpty(template.Description))
            {
                result.Warnings.Add("ConsequenceTemplate should have a description.");
            }
            // Add more validation as needed
            return result;
        }

        public static string PreviewReward(RewardTemplate template)
        {
            return $"Preview: {template.Name} - XP: {template.BaseXP}, Gold: {template.BaseGold}, Items: [{string.Join(", ", template.ItemIds)}], Reputation: [{string.Join(", ", template.Reputation)}]";
        }

        public static string PreviewConsequence(ConsequenceTemplate template)
        {
            return $"Preview: {template.Name} - Severity: {template.Severity}, Category: {template.Category}, Desc: {template.Description}";
        }

        public static void LogRewardApplication(RewardTemplate template)
        {
            Debug.Log($"[Reward Applied] {template.Name} - XP: {template.BaseXP}, Gold: {template.BaseGold}, Items: [{string.Join(", ", template.ItemIds)}], Reputation: [{string.Join(", ", template.Reputation)}]");
        }

        public static void LogConsequenceApplication(ConsequenceTemplate template)
        {
            Debug.Log($"[Consequence Applied] {template.Name} - Severity: {template.Severity}, Category: {template.Category}, Desc: {template.Description}");
        }

        public static void VisualizeWorldState(Dictionary<string, object> state)
        {
            Debug.Log($"[World State] {string.Join(", ", state)}");
        }

        public static void VisualizeConsequenceChain(List<ConsequenceTemplate> chain)
        {
            foreach (var c in chain)
                Debug.Log($"[Consequence Chain] {c.Name} -> Severity: {c.Severity}, Category: {c.Category}");
        }
    }
} 