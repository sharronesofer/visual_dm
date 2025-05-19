using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace VisualDM.Systems
{
    /// <summary>
    /// Manages game state persistence, loading, and tracking
    /// </summary>
    public class StateManager : MonoBehaviour
    {
        // Current game state data
        private Dictionary<string, object> _gameState = new Dictionary<string, object>();
        
        // Tracked game variables for easy access
        private Dictionary<string, object> _gameVariables = new Dictionary<string, object>();
        
        // Last save/load information
        private string _lastSavePath = string.Empty;
        private DateTime _lastSaveTime = DateTime.MinValue;
        
        // Events
        public event Action<string> OnStateSaved;
        public event Action<string> OnStateLoaded;
        
        /// <summary>
        /// Initialize the state manager
        /// </summary>
        private void Awake()
        {
            Debug.Log("StateManager initializing...");
            ResetState();
        }
        
        /// <summary>
        /// Reset the game state to defaults
        /// </summary>
        public void ResetState()
        {
            _gameState.Clear();
            _gameVariables.Clear();
            
            // Initialize with default values
            _gameState["gameVersion"] = Application.version;
            _gameState["creationTime"] = DateTime.Now.ToString("o");
            _gameState["lastUpdateTime"] = DateTime.Now.ToString("o");
            
            Debug.Log("Game state reset to defaults.");
        }
        
        /// <summary>
        /// Set a state value
        /// </summary>
        /// <param name="key">State key</param>
        /// <param name="value">State value</param>
        public void SetState(string key, object value)
        {
            if (string.IsNullOrEmpty(key))
                return;
            
            _gameState[key] = value;
            _gameState["lastUpdateTime"] = DateTime.Now.ToString("o");
        }
        
        /// <summary>
        /// Get a state value
        /// </summary>
        /// <typeparam name="T">Expected type</typeparam>
        /// <param name="key">State key</param>
        /// <param name="defaultValue">Default value if not found</param>
        /// <returns>State value or default</returns>
        public T GetState<T>(string key, T defaultValue = default)
        {
            if (string.IsNullOrEmpty(key) || !_gameState.ContainsKey(key))
                return defaultValue;
            
            try
            {
                if (_gameState[key] is T typedValue)
                {
                    return typedValue;
                }
                
                // Try conversion
                return (T)Convert.ChangeType(_gameState[key], typeof(T));
            }
            catch
            {
                Debug.LogWarning($"Failed to convert state value '{key}' to type {typeof(T).Name}");
                return defaultValue;
            }
        }
        
        /// <summary>
        /// Track a game variable for easy access
        /// </summary>
        /// <typeparam name="T">Variable type</typeparam>
        /// <param name="key">Variable key</param>
        /// <param name="initialValue">Initial value</param>
        public void TrackVariable<T>(string key, T initialValue = default)
        {
            if (string.IsNullOrEmpty(key))
                return;
            
            _gameVariables[key] = initialValue;
        }
        
        /// <summary>
        /// Set a tracked game variable
        /// </summary>
        /// <typeparam name="T">Variable type</typeparam>
        /// <param name="key">Variable key</param>
        /// <param name="value">New value</param>
        public void SetVariable<T>(string key, T value)
        {
            if (string.IsNullOrEmpty(key))
                return;
            
            _gameVariables[key] = value;
        }
        
        /// <summary>
        /// Get a tracked game variable
        /// </summary>
        /// <typeparam name="T">Expected type</typeparam>
        /// <param name="key">Variable key</param>
        /// <param name="defaultValue">Default value if not found</param>
        /// <returns>Variable value or default</returns>
        public T GetVariable<T>(string key, T defaultValue = default)
        {
            if (string.IsNullOrEmpty(key) || !_gameVariables.ContainsKey(key))
                return defaultValue;
            
            try
            {
                if (_gameVariables[key] is T typedValue)
                {
                    return typedValue;
                }
                
                // Try conversion
                return (T)Convert.ChangeType(_gameVariables[key], typeof(T));
            }
            catch
            {
                Debug.LogWarning($"Failed to convert variable '{key}' to type {typeof(T).Name}");
                return defaultValue;
            }
        }
        
        /// <summary>
        /// Save the current game state to disk
        /// </summary>
        /// <param name="saveFileName">Save file name</param>
        public void SaveState(string saveFileName)
        {
            try
            {
                // Prepare save directory
                string saveDir = Path.Combine(Application.persistentDataPath, "Saves");
                Directory.CreateDirectory(saveDir);
                
                // Generate save file path
                string savePath = Path.Combine(saveDir, $"{saveFileName}.json");
                
                // Update timestamps
                _gameState["lastSaveTime"] = DateTime.Now.ToString("o");
                
                // Create save data object with state and variables
                var saveData = new SaveData
                {
                    GameState = new Dictionary<string, object>(_gameState),
                    GameVariables = new Dictionary<string, object>(_gameVariables)
                };
                
                // Serialize to JSON
                string json = JsonUtility.ToJson(saveData, true);
                
                // Write to file
                File.WriteAllText(savePath, json);
                
                // Update tracking info
                _lastSavePath = savePath;
                _lastSaveTime = DateTime.Now;
                
                Debug.Log($"Game state saved to: {savePath}");
                OnStateSaved?.Invoke(savePath);
            }
            catch (Exception e)
            {
                Debug.LogError($"Error saving game state: {e.Message}\n{e.StackTrace}");
                throw;
            }
        }
        
        /// <summary>
        /// Load a game state from disk
        /// </summary>
        /// <param name="saveFileName">Save file name</param>
        public void LoadState(string saveFileName)
        {
            try
            {
                // Generate save file path
                string saveDir = Path.Combine(Application.persistentDataPath, "Saves");
                string savePath = Path.Combine(saveDir, $"{saveFileName}.json");
                
                // Check if file exists
                if (!File.Exists(savePath))
                {
                    Debug.LogError($"Save file not found: {savePath}");
                    throw new FileNotFoundException($"Save file not found: {savePath}");
                }
                
                // Read JSON file
                string json = File.ReadAllText(savePath);
                
                // Deserialize from JSON
                SaveData saveData = JsonUtility.FromJson<SaveData>(json);
                
                // Clear existing state
                _gameState.Clear();
                _gameVariables.Clear();
                
                // Load state and variables
                foreach (var kvp in saveData.GameState)
                {
                    _gameState[kvp.Key] = kvp.Value;
                }
                
                foreach (var kvp in saveData.GameVariables)
                {
                    _gameVariables[kvp.Key] = kvp.Value;
                }
                
                // Update load timestamp
                _gameState["lastLoadTime"] = DateTime.Now.ToString("o");
                
                Debug.Log($"Game state loaded from: {savePath}");
                OnStateLoaded?.Invoke(savePath);
            }
            catch (Exception e)
            {
                Debug.LogError($"Error loading game state: {e.Message}\n{e.StackTrace}");
                throw;
            }
        }
        
        /// <summary>
        /// Get a list of available save files
        /// </summary>
        /// <returns>List of save file names without extension</returns>
        public List<string> GetAvailableSaves()
        {
            List<string> saves = new List<string>();
            
            try
            {
                string saveDir = Path.Combine(Application.persistentDataPath, "Saves");
                
                if (!Directory.Exists(saveDir))
                    return saves;
                
                foreach (string file in Directory.GetFiles(saveDir, "*.json"))
                {
                    saves.Add(Path.GetFileNameWithoutExtension(file));
                }
            }
            catch (Exception e)
            {
                Debug.LogError($"Error getting available saves: {e.Message}");
            }
            
            return saves;
        }
        
        /// <summary>
        /// Get a summary of a saved game without loading it
        /// </summary>
        /// <param name="saveFileName">Save file name</param>
        /// <returns>Save summary or null if not found</returns>
        public SaveSummary GetSaveSummary(string saveFileName)
        {
            try
            {
                string saveDir = Path.Combine(Application.persistentDataPath, "Saves");
                string savePath = Path.Combine(saveDir, $"{saveFileName}.json");
                
                if (!File.Exists(savePath))
                    return null;
                
                // Read file info
                FileInfo fileInfo = new FileInfo(savePath);
                
                // Read a small part of the file to extract basic info
                string json = File.ReadAllText(savePath);
                SaveData saveData = JsonUtility.FromJson<SaveData>(json);
                
                string gameVersion = "";
                string creationTime = "";
                string lastSaveTime = "";
                
                if (saveData.GameState.ContainsKey("gameVersion"))
                    gameVersion = saveData.GameState["gameVersion"].ToString();
                
                if (saveData.GameState.ContainsKey("creationTime"))
                    creationTime = saveData.GameState["creationTime"].ToString();
                
                if (saveData.GameState.ContainsKey("lastSaveTime"))
                    lastSaveTime = saveData.GameState["lastSaveTime"].ToString();
                
                return new SaveSummary
                {
                    FileName = saveFileName,
                    FilePath = savePath,
                    FileSize = fileInfo.Length,
                    LastWriteTime = fileInfo.LastWriteTime,
                    GameVersion = gameVersion,
                    CreationTime = creationTime,
                    LastSaveTime = lastSaveTime
                };
            }
            catch (Exception e)
            {
                Debug.LogError($"Error getting save summary: {e.Message}");
                return null;
            }
        }
    }
    
    /// <summary>
    /// Serializable save data container
    /// </summary>
    [Serializable]
    public class SaveData
    {
        public Dictionary<string, object> GameState = new Dictionary<string, object>();
        public Dictionary<string, object> GameVariables = new Dictionary<string, object>();
    }
    
    /// <summary>
    /// Summary information about a save file
    /// </summary>
    [Serializable]
    public class SaveSummary
    {
        public string FileName;
        public string FilePath;
        public long FileSize;
        public DateTime LastWriteTime;
        public string GameVersion;
        public string CreationTime;
        public string LastSaveTime;
    }
} 