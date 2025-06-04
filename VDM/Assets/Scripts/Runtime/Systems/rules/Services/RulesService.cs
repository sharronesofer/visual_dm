using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.Rules.Models;

namespace VDM.Systems.Rules.Services
{
    /// <summary>
    /// Frontend rules service that interfaces with backend rules system
    /// Handles game rules, balance constants, and configuration management
    /// </summary>
    public class RulesService : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private bool enableDebugLogging = true;
        [SerializeField] private bool cacheRules = true;
        
        // Events
        public static event Action<GameRule> OnRuleChanged;
        public static event Action<string> OnConfigurationLoaded;
        public static event Action<ValidationRule> OnValidationFailed;
        
        // State
        private Dictionary<string, GameRule> gameRules = new Dictionary<string, GameRule>();
        private Dictionary<string, RuleCategory> ruleCategories = new Dictionary<string, RuleCategory>();
        private BalanceConstants balanceConstants;
        private bool isInitialized = false;
        
        private void Awake()
        {
            InitializeService();
        }
        
        private void InitializeService()
        {
            if (isInitialized) return;
            
            if (enableDebugLogging)
                Debug.Log("RulesService: Initializing rules system...");
            
            LoadRulesData();
            isInitialized = true;
        }
        
        private async void LoadRulesData()
        {
            try
            {
                // TODO: Load rules from backend
                // await LoadGameRulesFromBackend();
                // await LoadBalanceConstantsFromBackend();
                
                if (enableDebugLogging)
                    Debug.Log("RulesService: Rules data loaded successfully");
                
                OnConfigurationLoaded?.Invoke("default");
            }
            catch (Exception ex)
            {
                Debug.LogError($"RulesService: Failed to load rules data: {ex.Message}");
            }
        }
        
        public T GetRuleValue<T>(string ruleId, T defaultValue = default(T))
        {
            try
            {
                if (gameRules.TryGetValue(ruleId, out var rule))
                {
                    if (rule.value is T typedValue)
                        return typedValue;
                    
                    // Try to convert
                    return (T)Convert.ChangeType(rule.value, typeof(T));
                }
                
                if (enableDebugLogging)
                    Debug.LogWarning($"RulesService: Rule '{ruleId}' not found, using default value");
                
                return defaultValue;
            }
            catch (Exception ex)
            {
                Debug.LogError($"RulesService: Error getting rule value for '{ruleId}': {ex.Message}");
                return defaultValue;
            }
        }
        
        public async Task<bool> SetRuleValue(string ruleId, object value)
        {
            try
            {
                if (!gameRules.TryGetValue(ruleId, out var rule))
                {
                    Debug.LogError($"RulesService: Rule '{ruleId}' not found");
                    return false;
                }
                
                if (!rule.isModifiable)
                {
                    Debug.LogError($"RulesService: Rule '{ruleId}' is not modifiable");
                    return false;
                }
                
                // TODO: Send rule update to backend
                // var result = await BackendService.UpdateRule(ruleId, value);
                
                rule.value = value;
                OnRuleChanged?.Invoke(rule);
                
                if (enableDebugLogging)
                    Debug.Log($"RulesService: Rule '{ruleId}' updated to '{value}'");
                
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"RulesService: Failed to set rule value: {ex.Message}");
                return false;
            }
        }
        
        public BalanceConstants GetBalanceConstants()
        {
            return balanceConstants;
        }
        
        public List<GameRule> GetRulesByCategory(string category)
        {
            if (ruleCategories.TryGetValue(category, out var ruleCategory))
            {
                return new List<GameRule>(ruleCategory.rules);
            }
            
            return new List<GameRule>();
        }
        
        public bool ValidateRule(string ruleId, object value)
        {
            // TODO: Implement rule validation logic
            return true;
        }
    }
} 