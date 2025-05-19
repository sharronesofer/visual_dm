using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace VisualDM.Systems
{
    /// <summary>
    /// Manages loading and synchronizing game data from mods
    /// </summary>
    public class ModDataManager : MonoBehaviour
    {
        // Base mod data
        private ModManifest _baseModManifest;
        private bool _baseModLoaded = false;
        
        // User mods
        private readonly List<ModManifest> _userMods = new List<ModManifest>();
        private readonly Dictionary<string, ModManifest> _loadedMods = new Dictionary<string, ModManifest>();
        
        // Data collections
        private readonly Dictionary<string, Dictionary<string, object>> _dataCollections = new Dictionary<string, Dictionary<string, object>>();
        
        // Events
        public event Action<ModManifest> OnModLoaded;
        public event Action<string> OnDataCollectionUpdated;
        
        // Paths
        private string BasePath => Path.Combine(Application.streamingAssetsPath, "Mods");
        private string UserModsPath => Path.Combine(Application.persistentDataPath, "Mods");
        
        // References
        private EventDispatcher _eventDispatcher;
        
        private void Awake()
        {
            Debug.Log("ModDataManager initializing...");
            
            // Get references
            _eventDispatcher = GetComponentInParent<EventDispatcher>();
            
            // Create directories if they don't exist
            Directory.CreateDirectory(BasePath);
            Directory.CreateDirectory(UserModsPath);
        }
        
        /// <summary>
        /// Load the base mod that comes with the game
        /// </summary>
        public void LoadBaseMod()
        {
            Debug.Log("Loading base mod...");
            
            try
            {
                string baseModFolder = Path.Combine(BasePath, "BaseMod");
                string manifestPath = Path.Combine(baseModFolder, "manifest.json");
                
                if (!File.Exists(manifestPath))
                {
                    Debug.LogWarning("Base mod manifest not found. Creating default base mod...");
                    CreateDefaultBaseMod();
                    return;
                }
                
                // Load manifest
                string json = File.ReadAllText(manifestPath);
                _baseModManifest = JsonUtility.FromJson<ModManifest>(json);
                
                if (_baseModManifest == null)
                {
                    Debug.LogError("Failed to parse base mod manifest.");
                    return;
                }
                
                // Load all data collections from the base mod
                foreach (var collection in _baseModManifest.DataCollections)
                {
                    LoadDataCollection(baseModFolder, collection, true);
                }
                
                _baseModLoaded = true;
                OnModLoaded?.Invoke(_baseModManifest);
                
                Debug.Log($"Base mod loaded: {_baseModManifest.Name} v{_baseModManifest.Version}");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error loading base mod: {e.Message}\n{e.StackTrace}");
            }
        }
        
        /// <summary>
        /// Create a default base mod if one doesn't exist
        /// </summary>
        private void CreateDefaultBaseMod()
        {
            try
            {
                string baseModFolder = Path.Combine(BasePath, "BaseMod");
                Directory.CreateDirectory(baseModFolder);
                
                // Create base mod structure
                Directory.CreateDirectory(Path.Combine(baseModFolder, "Characters"));
                Directory.CreateDirectory(Path.Combine(baseModFolder, "Items"));
                Directory.CreateDirectory(Path.Combine(baseModFolder, "Locations"));
                Directory.CreateDirectory(Path.Combine(baseModFolder, "Quests"));
                Directory.CreateDirectory(Path.Combine(baseModFolder, "Dialogues"));
                
                // Create manifest
                var manifest = new ModManifest
                {
                    Id = "base",
                    Name = "Base Mod",
                    Version = "1.0.0",
                    Author = "Visual DM",
                    Description = "Base game content",
                    DataCollections = new List<string>
                    {
                        "Characters",
                        "Items",
                        "Locations",
                        "Quests",
                        "Dialogues"
                    }
                };
                
                // Save manifest
                string json = JsonUtility.ToJson(manifest, true);
                File.WriteAllText(Path.Combine(baseModFolder, "manifest.json"), json);
                
                // Create empty data collections
                CreateEmptyDataCollection(baseModFolder, "Characters");
                CreateEmptyDataCollection(baseModFolder, "Items");
                CreateEmptyDataCollection(baseModFolder, "Locations");
                CreateEmptyDataCollection(baseModFolder, "Quests");
                CreateEmptyDataCollection(baseModFolder, "Dialogues");
                
                // Set as base mod
                _baseModManifest = manifest;
                _baseModLoaded = true;
                
                Debug.Log("Default base mod created successfully.");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error creating default base mod: {e.Message}\n{e.StackTrace}");
            }
        }
        
        /// <summary>
        /// Create an empty data collection
        /// </summary>
        private void CreateEmptyDataCollection(string modFolder, string collectionName)
        {
            var collection = new Dictionary<string, object>();
            string json = JsonUtility.ToJson(new { items = collection }, true);
            File.WriteAllText(Path.Combine(modFolder, $"{collectionName}.json"), json);
        }
        
        /// <summary>
        /// Scan and load all user mods
        /// </summary>
        public void LoadUserMods()
        {
            Debug.Log("Loading user mods...");
            
            if (!_baseModLoaded)
            {
                Debug.LogWarning("Base mod not loaded. Loading base mod first...");
                LoadBaseMod();
            }
            
            try
            {
                _userMods.Clear();
                
                // Get all directories in the user mods folder
                var modDirectories = Directory.GetDirectories(UserModsPath);
                
                foreach (var modDir in modDirectories)
                {
                    try
                    {
                        string manifestPath = Path.Combine(modDir, "manifest.json");
                        
                        if (!File.Exists(manifestPath))
                        {
                            Debug.LogWarning($"Mod manifest not found in {modDir}. Skipping...");
                            continue;
                        }
                        
                        // Load manifest
                        string json = File.ReadAllText(manifestPath);
                        var manifest = JsonUtility.FromJson<ModManifest>(json);
                        
                        if (manifest == null)
                        {
                            Debug.LogWarning($"Failed to parse mod manifest in {modDir}. Skipping...");
                            continue;
                        }
                        
                        // Check if mod is already loaded
                        if (_loadedMods.ContainsKey(manifest.Id))
                        {
                            Debug.LogWarning($"Mod with ID '{manifest.Id}' already loaded. Skipping...");
                            continue;
                        }
                        
                        // Load mod data collections
                        foreach (var collection in manifest.DataCollections)
                        {
                            LoadDataCollection(modDir, collection, false);
                        }
                        
                        // Add to loaded mods
                        _userMods.Add(manifest);
                        _loadedMods[manifest.Id] = manifest;
                        
                        OnModLoaded?.Invoke(manifest);
                        
                        Debug.Log($"User mod loaded: {manifest.Name} v{manifest.Version}");
                    }
                    catch (Exception e)
                    {
                        Debug.LogError($"Error loading mod from {modDir}: {e.Message}");
                    }
                }
                
                Debug.Log($"Loaded {_userMods.Count} user mods.");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error loading user mods: {e.Message}\n{e.StackTrace}");
            }
        }
        
        /// <summary>
        /// Load a data collection from a mod
        /// </summary>
        private void LoadDataCollection(string modFolder, string collection, bool isBaseMod)
        {
            try
            {
                string collectionPath = Path.Combine(modFolder, $"{collection}.json");
                
                if (!File.Exists(collectionPath))
                {
                    Debug.LogWarning($"Data collection '{collection}' not found in {modFolder}. Skipping...");
                    return;
                }
                
                // Load collection data
                string json = File.ReadAllText(collectionPath);
                
                // Parse JSON into data collection
                var collectionData = JsonUtility.FromJson<Dictionary<string, object>>(json);
                
                if (collectionData == null)
                {
                    Debug.LogWarning($"Failed to parse data collection '{collection}' in {modFolder}. Skipping...");
                    return;
                }
                
                // Create collection if it doesn't exist
                if (!_dataCollections.ContainsKey(collection))
                {
                    _dataCollections[collection] = new Dictionary<string, object>();
                }
                
                // If it's the base mod, replace the entire collection
                // Otherwise, merge with existing data
                if (isBaseMod)
                {
                    _dataCollections[collection] = collectionData;
                }
                else
                {
                    foreach (var kvp in collectionData)
                    {
                        _dataCollections[collection][kvp.Key] = kvp.Value;
                    }
                }
                
                OnDataCollectionUpdated?.Invoke(collection);
                
                Debug.Log($"Loaded data collection '{collection}' from {modFolder}.");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error loading data collection '{collection}' from {modFolder}: {e.Message}");
            }
        }
        
        /// <summary>
        /// Get the data from a collection
        /// </summary>
        /// <typeparam name="T">Expected type of the data</typeparam>
        /// <param name="collection">Collection name</param>
        /// <param name="id">Data ID</param>
        /// <param name="defaultValue">Default value if not found</param>
        /// <returns>Data object or default</returns>
        public T GetData<T>(string collection, string id, T defaultValue = default)
        {
            if (string.IsNullOrEmpty(collection) || string.IsNullOrEmpty(id))
                return defaultValue;
            
            if (!_dataCollections.TryGetValue(collection, out var collectionData))
                return defaultValue;
            
            if (!collectionData.TryGetValue(id, out var data))
                return defaultValue;
            
            try
            {
                if (data is T typedData)
                {
                    return typedData;
                }
                
                // Try conversion
                return (T)Convert.ChangeType(data, typeof(T));
            }
            catch
            {
                Debug.LogWarning($"Failed to convert data '{id}' to type {typeof(T).Name}");
                return defaultValue;
            }
        }
        
        /// <summary>
        /// Get all data IDs in a collection
        /// </summary>
        /// <param name="collection">Collection name</param>
        /// <returns>List of data IDs</returns>
        public List<string> GetDataIds(string collection)
        {
            if (string.IsNullOrEmpty(collection) || !_dataCollections.TryGetValue(collection, out var collectionData))
                return new List<string>();
            
            return new List<string>(collectionData.Keys);
        }
        
        /// <summary>
        /// Get information about all loaded mods
        /// </summary>
        /// <returns>List of loaded mod manifests</returns>
        public List<ModManifest> GetLoadedMods()
        {
            var mods = new List<ModManifest>();
            
            if (_baseModLoaded && _baseModManifest != null)
            {
                mods.Add(_baseModManifest);
            }
            
            mods.AddRange(_userMods);
            
            return mods;
        }
    }
    
    /// <summary>
    /// Mod manifest data
    /// </summary>
    [Serializable]
    public class ModManifest
    {
        public string Id;
        public string Name;
        public string Version;
        public string Author;
        public string Description;
        public List<string> DataCollections = new List<string>();
        public List<string> Dependencies = new List<string>();
    }
} 