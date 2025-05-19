using UnityEngine;
using System.Collections;
using VisualDM.Data;

namespace VisualDM.Core
{
    public class GameManager : MonoBehaviour
    {
        [Header("Mod Data Settings")]
        [SerializeField] 
        private bool _enableModding = true;
        
        [SerializeField]
        private bool _autoSyncMods = true;
        
        [SerializeField]
        private string[] _requiredModCategories = new[]
        {
            "biomes",
            "weapons",
            "races",
            "land_types"
        };
        
        private ModDataManager _modDataManager;
        private ModSynchronizer _modSynchronizer;
        private bool _isModDataLoaded = false;
        
        private void InitializeModData()
        {
            if (!_enableModding)
            {
                UnityEngine.Debug.Log("Modding is disabled. Skipping mod data initialization.");
                return;
            }
            
            // Get or create the ModDataManager singleton
            _modDataManager = ModDataManager.Instance;
            
            // Initialize the mod data system
            _modDataManager.Initialize();
            
            // Add ModSynchronizer component if auto-sync is enabled
            if (_autoSyncMods)
            {
                _modSynchronizer = gameObject.AddComponent<ModSynchronizer>();
                _modSynchronizer.SyncCompleted += OnModSyncCompleted;
            }
            else
            {
                // Load required mod categories even without syncing
                StartCoroutine(LoadRequiredModCategories());
            }
        }
        
        private void OnModSyncCompleted(bool success)
        {
            UnityEngine.Debug.Log($"Mod synchronization completed with result: {success}");
            
            if (success)
            {
                StartCoroutine(LoadRequiredModCategories());
            }
            else
            {
                UnityEngine.Debug.LogWarning("Mod synchronization failed. Loading mod data from local files only.");
                StartCoroutine(LoadRequiredModCategories());
            }
        }
        
        private IEnumerator LoadRequiredModCategories()
        {
            foreach (string category in _requiredModCategories)
            {
                bool success = _modDataManager.LoadCategory(category);
                if (!success)
                {
                    UnityEngine.Debug.LogWarning($"Failed to load required mod category: {category}");
                }
                yield return null;
            }
            
            _isModDataLoaded = true;
            OnModDataLoaded();
        }
        
        private void OnModDataLoaded()
        {
            // Notify other systems that mod data is ready
            UnityEngine.Debug.Log("All required mod data loaded.");
            
            // Example: Get all weapons
            var weapons = _modDataManager.GetAllItems("weapons");
            UnityEngine.Debug.Log($"Loaded {weapons.Count} weapons.");
            
            // Example: Get all races
            var races = _modDataManager.GetAllItems("races");
            UnityEngine.Debug.Log($"Loaded {races.Count} races.");
            
            // You can now continue with game initialization that depends on mod data
            // ... additional initialization code ...
        }
        
        public ModDataManager GetModDataManager()
        {
            return _modDataManager;
        }
        
        public bool IsModDataLoaded()
        {
            return _isModDataLoaded;
        }
        
        public void ReloadModData()
        {
            if (_modSynchronizer != null)
            {
                _modSynchronizer.TriggerSync();
            }
            else
            {
                _isModDataLoaded = false;
                StartCoroutine(LoadRequiredModCategories());
            }
        }
    }
} 