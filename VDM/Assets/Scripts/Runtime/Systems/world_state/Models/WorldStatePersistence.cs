using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.DTOs.Common;

namespace VDM.Systems.WorldState.Services
{
    public class WorldStatePersistence : MonoBehaviour
    {
        private static WorldStatePersistence _instance;
        public static WorldStatePersistence Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<WorldStatePersistence>();
                    if (_instance == null)
                    {
                        GameObject go = new GameObject("WorldStatePersistence");
                        _instance = go.AddComponent<WorldStatePersistence>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        [Header("World State Settings")]
        public string saveDirectory = "WorldStates";
        public bool enableLogging = true;
        public bool autoSave = true;
        public float autoSaveInterval = 300f; // 5 minutes
        
        private Dictionary<string, object> currentWorldState = new Dictionary<string, object>();
        private float lastSaveTime = 0f;
        
        void Start()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            InitializePersistence();
        }
        
        void Update()
        {
            if (autoSave && Time.time - lastSaveTime > autoSaveInterval)
            {
                SaveWorldStateAsync();
                lastSaveTime = Time.time;
            }
        }
        
        private void InitializePersistence()
        {
            string fullPath = System.IO.Path.Combine(Application.persistentDataPath, saveDirectory);
            if (!System.IO.Directory.Exists(fullPath))
            {
                System.IO.Directory.CreateDirectory(fullPath);
                if (enableLogging)
                    Debug.Log($"WorldStatePersistence: Created save directory at {fullPath}");
            }
        }
        
        public async Task<bool> SaveWorldStateAsync(string stateId = null)
        {
            try
            {
                string saveId = stateId ?? $"worldstate_{DateTime.UtcNow:yyyyMMdd_HHmmss}";
                string fileName = $"{saveId}.json";
                string fullPath = System.IO.Path.Combine(Application.persistentDataPath, saveDirectory, fileName);
                
                var saveData = new GameSaveDataDTO
                {
                    metadata = new SaveGameMetadataDTO
                    {
                        id = saveId,
                        name = $"World State {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}",
                        createdAt = DateTime.UtcNow,
                        lastSaved = DateTime.UtcNow,
                        version = Application.version
                    },
                    gameTime = new GameTimeDTO(),
                    worldState = Newtonsoft.Json.JsonConvert.SerializeObject(currentWorldState),
                    systemStates = new Dictionary<string, object>(currentWorldState)
                };
                
                string json = Newtonsoft.Json.JsonConvert.SerializeObject(saveData, Newtonsoft.Json.Formatting.Indented);
                await System.IO.File.WriteAllTextAsync(fullPath, json);
                
                if (enableLogging)
                    Debug.Log($"WorldStatePersistence: Saved world state to {fullPath}");
                
                return true;
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"WorldStatePersistence: Failed to save world state - {ex.Message}");
                return false;
            }
        }
        
        public async Task<GameSaveDataDTO> LoadWorldStateAsync(string stateId)
        {
            try
            {
                string fileName = $"{stateId}.json";
                string fullPath = System.IO.Path.Combine(Application.persistentDataPath, saveDirectory, fileName);
                
                if (!System.IO.File.Exists(fullPath))
                {
                    if (enableLogging)
                        Debug.LogWarning($"WorldStatePersistence: Save file not found - {fullPath}");
                    return null;
                }
                
                string json = await System.IO.File.ReadAllTextAsync(fullPath);
                var saveData = Newtonsoft.Json.JsonConvert.DeserializeObject<GameSaveDataDTO>(json);
                
                if (saveData != null)
                {
                    currentWorldState = saveData.systemStates ?? new Dictionary<string, object>();
                    if (enableLogging)
                        Debug.Log($"WorldStatePersistence: Loaded world state from {fullPath}");
                }
                
                return saveData;
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"WorldStatePersistence: Failed to load world state {stateId} - {ex.Message}");
                return null;
            }
        }
        
        public List<SaveGameMetadataDTO> GetAvailableSaves()
        {
            var saves = new List<SaveGameMetadataDTO>();
            
            try
            {
                string fullPath = System.IO.Path.Combine(Application.persistentDataPath, saveDirectory);
                if (!System.IO.Directory.Exists(fullPath))
                    return saves;
                
                var files = System.IO.Directory.GetFiles(fullPath, "*.json");
                
                foreach (var file in files)
                {
                    try
                    {
                        string json = System.IO.File.ReadAllText(file);
                        var saveData = Newtonsoft.Json.JsonConvert.DeserializeObject<GameSaveDataDTO>(json);
                        if (saveData?.metadata != null)
                        {
                            saves.Add(saveData.metadata);
                        }
                    }
                    catch (Exception ex)
                    {
                        if (enableLogging)
                            Debug.LogWarning($"WorldStatePersistence: Failed to read save file {file} - {ex.Message}");
                    }
                }
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"WorldStatePersistence: Failed to get available saves - {ex.Message}");
            }
            
            return saves;
        }
        
        public void SetWorldStateValue(string key, object value)
        {
            currentWorldState[key] = value;
            if (enableLogging)
                Debug.Log($"WorldStatePersistence: Set world state value {key}");
        }
        
        public T GetWorldStateValue<T>(string key, T defaultValue = default(T))
        {
            if (currentWorldState.ContainsKey(key))
            {
                try
                {
                    return (T)currentWorldState[key];
                }
                catch (InvalidCastException)
                {
                    if (enableLogging)
                        Debug.LogWarning($"WorldStatePersistence: Type mismatch for key {key}");
                    return defaultValue;
                }
            }
            
            return defaultValue;
        }
        
        public bool DeleteSave(string stateId)
        {
            try
            {
                string fileName = $"{stateId}.json";
                string fullPath = System.IO.Path.Combine(Application.persistentDataPath, saveDirectory, fileName);
                
                if (System.IO.File.Exists(fullPath))
                {
                    System.IO.File.Delete(fullPath);
                    if (enableLogging)
                        Debug.Log($"WorldStatePersistence: Deleted save {stateId}");
                    return true;
                }
                
                return false;
            }
            catch (Exception ex)
            {
                if (enableLogging)
                    Debug.LogError($"WorldStatePersistence: Failed to delete save {stateId} - {ex.Message}");
                return false;
            }
        }
        
        public void ClearCurrentState()
        {
            currentWorldState.Clear();
            if (enableLogging)
                Debug.Log("WorldStatePersistence: Cleared current world state");
        }
    }
} 