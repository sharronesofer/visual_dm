using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using System.Threading;
using System.Linq;

namespace Core.Utils
{
    /// <summary>
    /// Type for feature flag identifiers (use string constants).
    /// </summary>
    public class FeatureFlag
    {
        // Common feature flags can be defined as constants here
        public const string EXAMPLE_FEATURE = "ExampleFeature";
    }
    
    /// <summary>
    /// Context for feature flag evaluation.
    /// </summary>
    [Serializable]
    public class FlagContext
    {
        public Dictionary<string, object> Values { get; set; } = new Dictionary<string, object>();
        
        public void Set<T>(string key, T value)
        {
            Values[key] = value;
        }
        
        public T Get<T>(string key, T defaultValue = default)
        {
            if (Values.TryGetValue(key, out object value) && value is T typedValue)
            {
                return typedValue;
            }
            return defaultValue;
        }
        
        public bool HasKey(string key)
        {
            return Values.ContainsKey(key);
        }
    }
    
    /// <summary>
    /// Delegate for feature flag evaluation functions.
    /// </summary>
    public delegate bool FlagEvaluator(string flag, FlagContext context);
    
    /// <summary>
    /// ScriptableObject that stores feature flag configurations and can be edited in Unity Editor.
    /// </summary>
    [CreateAssetMenu(fileName = "FeatureFlagConfig", menuName = "Config/Feature Flags")]
    public class FeatureFlagConfig : ScriptableObject
    {
        [Serializable]
        public class FlagEntry
        {
            public string Name;
            public bool Enabled;
            [TextArea(1, 5)]
            public string Description;
        }
        
        [SerializeField]
        private List<FlagEntry> flags = new List<FlagEntry>();
        
        public Dictionary<string, bool> GetFlagsDictionary()
        {
            return flags.ToDictionary(f => f.Name, f => f.Enabled);
        }
        
        /// <summary>
        /// Apply this configuration to the feature flag system.
        /// </summary>
        public void Apply()
        {
            FeatureFlagSystem.Instance.ApplyConfig(this);
        }
    }
    
    /// <summary>
    /// Thread-safe feature flag system similar to the Python implementation.
    /// </summary>
    public class FeatureFlagSystem
    {
        private static readonly object _lock = new object();
        private Dictionary<string, bool> _flags = new Dictionary<string, bool>();
        private Dictionary<string, FlagEvaluator> _evaluators = new Dictionary<string, FlagEvaluator>();
        private string _configFilePath;
        private float _lastReloadTime;
        private float _reloadInterval = 60f; // Seconds
        private bool _autoReload = false;
        
        // Singleton instance
        private static FeatureFlagSystem _instance;
        
        /// <summary>
        /// Singleton access to the FeatureFlagSystem.
        /// </summary>
        public static FeatureFlagSystem Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = new FeatureFlagSystem();
                }
                return _instance;
            }
        }
        
        public FeatureFlagSystem()
        {
            LoadFromPlayerPrefs();
        }
        
        /// <summary>
        /// Applies feature flag configuration from a ScriptableObject.
        /// </summary>
        public void ApplyConfig(FeatureFlagConfig config)
        {
            if (config == null) return;
            
            lock (_lock)
            {
                Dictionary<string, bool> flagsDict = config.GetFlagsDictionary();
                foreach (var kvp in flagsDict)
                {
                    _flags[kvp.Key] = kvp.Value;
                }
            }
            
            // Save to PlayerPrefs for persistence between sessions
            SaveToPlayerPrefs();
        }
        
        /// <summary>
        /// Loads feature flags from JSON string.
        /// </summary>
        public bool LoadFromJson(string json)
        {
            try
            {
                var configObj = JsonUtility.FromJson<Wrapper<Dictionary<string, bool>>>(json);
                if (configObj != null && configObj.Value != null)
                {
                    lock (_lock)
                    {
                        foreach (var kvp in configObj.Value)
                        {
                            _flags[kvp.Key] = kvp.Value;
                        }
                    }
                    return true;
                }
                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error loading feature flags from JSON: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Loads feature flags from a JSON file.
        /// </summary>
        public bool LoadFromFile(string filePath)
        {
            if (string.IsNullOrEmpty(filePath) || !File.Exists(filePath))
            {
                Debug.LogWarning($"Feature flag config file does not exist: {filePath}");
                return false;
            }
            
            try
            {
                string json = File.ReadAllText(filePath);
                bool result = LoadFromJson(json);
                if (result)
                {
                    _configFilePath = filePath;
                    _lastReloadTime = Time.realtimeSinceStartup;
                }
                return result;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error loading feature flags from file: {ex.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Saves current feature flags to PlayerPrefs.
        /// </summary>
        private void SaveToPlayerPrefs()
        {
            string json = JsonUtility.ToJson(new Wrapper<Dictionary<string, bool>>(_flags));
            PlayerPrefs.SetString("FeatureFlags", json);
            PlayerPrefs.Save();
        }
        
        /// <summary>
        /// Loads feature flags from PlayerPrefs.
        /// </summary>
        private void LoadFromPlayerPrefs()
        {
            if (PlayerPrefs.HasKey("FeatureFlags"))
            {
                string json = PlayerPrefs.GetString("FeatureFlags");
                LoadFromJson(json);
            }
        }
        
        /// <summary>
        /// Helper class for JSON serialization of dictionary.
        /// </summary>
        [Serializable]
        private class Wrapper<T>
        {
            public T Value;
            
            public Wrapper(T value)
            {
                Value = value;
            }
        }
        
        /// <summary>
        /// Sets automatic reload interval and enables/disables auto reload.
        /// </summary>
        public void SetReloadInterval(float seconds, bool enableAutoReload = true)
        {
            if (seconds < 1f) seconds = 1f;
            lock (_lock)
            {
                _reloadInterval = seconds;
                _autoReload = enableAutoReload;
            }
        }
        
        /// <summary>
        /// Reloads flags from config file if reload interval has passed.
        /// </summary>
        public bool ReloadIfNeeded()
        {
            if (string.IsNullOrEmpty(_configFilePath) || !_autoReload) return false;
            
            float now = Time.realtimeSinceStartup;
            if (now - _lastReloadTime > _reloadInterval)
            {
                return LoadFromFile(_configFilePath);
            }
            return false;
        }
        
        /// <summary>
        /// Checks if a feature flag is enabled, optionally considering a context.
        /// </summary>
        public bool IsFeatureEnabled(string flag, FlagContext context = null)
        {
            // Reload from file if needed
            ReloadIfNeeded();
            
            // If a custom evaluator exists for this flag, use it with the context
            if (context != null)
            {
                lock (_lock)
                {
                    if (_evaluators.TryGetValue(flag, out FlagEvaluator evaluator))
                    {
                        try
                        {
                            return evaluator(flag, context);
                        }
                        catch (Exception ex)
                        {
                            Debug.LogError($"Error in custom evaluator for flag '{flag}': {ex.Message}");
                            // Fall back to static flag value
                        }
                    }
                }
            }
            
            // Otherwise use the static flag value
            lock (_lock)
            {
                if (_flags.TryGetValue(flag, out bool enabled))
                {
                    return enabled;
                }
                return false;
            }
        }
        
        /// <summary>
        /// Sets a feature flag value.
        /// </summary>
        public void SetFeatureFlag(string flag, bool enabled)
        {
            lock (_lock)
            {
                _flags[flag] = enabled;
            }
            SaveToPlayerPrefs();
        }
        
        /// <summary>
        /// Registers a custom evaluator function for context-based flag evaluation.
        /// </summary>
        public void RegisterEvaluator(string flag, FlagEvaluator evaluator)
        {
            lock (_lock)
            {
                _evaluators[flag] = evaluator;
            }
        }
        
        /// <summary>
        /// Gets all feature flags and their current values.
        /// </summary>
        public Dictionary<string, bool> GetAllFeatureFlags()
        {
            lock (_lock)
            {
                return new Dictionary<string, bool>(_flags);
            }
        }
    }
    
    /// <summary>
    /// Static helper class for feature flags that uses the singleton FeatureFlagSystem.
    /// </summary>
    public static class FeatureFlagHelper
    {
        /// <summary>
        /// Checks if a feature flag is enabled.
        /// </summary>
        public static bool IsFeatureEnabled(string flag, FlagContext context = null)
        {
            return FeatureFlagSystem.Instance.IsFeatureEnabled(flag, context);
        }
        
        /// <summary>
        /// Sets a feature flag value.
        /// </summary>
        public static void SetFeatureFlag(string flag, bool enabled)
        {
            FeatureFlagSystem.Instance.SetFeatureFlag(flag, enabled);
        }
        
        /// <summary>
        /// Gets all feature flags and their values.
        /// </summary>
        public static Dictionary<string, bool> GetAllFeatureFlags()
        {
            return FeatureFlagSystem.Instance.GetAllFeatureFlags();
        }
        
        /// <summary>
        /// Loads feature flags from a JSON file.
        /// </summary>
        public static bool LoadFromFile(string filePath)
        {
            return FeatureFlagSystem.Instance.LoadFromFile(filePath);
        }
        
        /// <summary>
        /// Registers a custom context-based evaluator for a flag.
        /// </summary>
        public static void RegisterEvaluator(string flag, FlagEvaluator evaluator)
        {
            FeatureFlagSystem.Instance.RegisterEvaluator(flag, evaluator);
        }
        
        /// <summary>
        /// Sets automatic file reload interval and enables/disables auto reload.
        /// </summary>
        public static void SetReloadInterval(float seconds, bool enableAutoReload = true)
        {
            FeatureFlagSystem.Instance.SetReloadInterval(seconds, enableAutoReload);
        }
    }
    
#if UNITY_EDITOR
    /// <summary>
    /// Custom editor for FeatureFlagConfig to provide a better editing experience.
    /// </summary>
    [UnityEditor.CustomEditor(typeof(FeatureFlagConfig))]
    public class FeatureFlagConfigEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            base.OnInspectorGUI();
            
            FeatureFlagConfig config = (FeatureFlagConfig)target;
            
            UnityEditor.EditorGUILayout.Space();
            if (GUILayout.Button("Apply Configuration"))
            {
                config.Apply();
                Debug.Log("Feature flag configuration applied to runtime system");
            }
            
            if (GUILayout.Button("Export to JSON"))
            {
                string path = UnityEditor.EditorUtility.SaveFilePanel(
                    "Export Feature Flags",
                    Application.dataPath,
                    "featureFlags.json",
                    "json");
                    
                if (!string.IsNullOrEmpty(path))
                {
                    try
                    {
                        var wrapper = new { featureFlags = config.GetFlagsDictionary() };
                        string json = JsonUtility.ToJson(wrapper, true);
                        File.WriteAllText(path, json);
                        Debug.Log($"Feature flags exported to {path}");
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Error exporting feature flags: {ex.Message}");
                    }
                }
            }
        }
    }
#endif
} 