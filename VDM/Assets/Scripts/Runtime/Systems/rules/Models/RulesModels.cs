using System;
using System.Collections.Generic;
using UnityEngine;

namespace VDM.Systems.Rules.Models
{
    /// <summary>
    /// Core rules system models for Unity frontend
    /// Mirrors backend rules system structure for game balance and configuration
    /// </summary>
    
    [Serializable]
    public class GameRule
    {
        public string id;
        public string name;
        public string category;
        public object value;
        public string description;
        public bool isModifiable;
    }
    
    [Serializable]
    public class BalanceConstants
    {
        public Dictionary<string, float> combatModifiers;
        public Dictionary<string, float> economicRates;
        public Dictionary<string, int> populationLimits;
        public Dictionary<string, float> skillProgression;
    }
    
    [Serializable]
    public class ValidationRule
    {
        public string id;
        public string targetSystem;
        public string condition;
        public string errorMessage;
        public bool isActive;
    }
    
    [Serializable]
    public class ConfigurationSet
    {
        public string id;
        public string name;
        public Dictionary<string, object> settings;
        public bool isDefault;
        public DateTime lastModified;
    }
    
    [Serializable]
    public class RuleCategory
    {
        public string name;
        public string description;
        public List<GameRule> rules;
        public bool isSystemCategory;
    }
} 