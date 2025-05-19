using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Systems
{
    /// <summary>
    /// Central GameManager singleton that coordinates between different modules
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        private static GameManager _instance;
        
        /// <summary>
        /// Singleton instance accessor
        /// </summary>
        public static GameManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("GameManager");
                    _instance = go.AddComponent<GameManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
        
        // Game state properties
        public bool IsGameRunning { get; private set; }
        public bool IsInitialized { get; private set; }
        public int Seed { get; private set; }
        
        // Manager references - these will be initialized during startup
        private ModDataManager _modDataManager;
        private StateManager _stateManager;
        private ModSynchronizer _modSynchronizer;
        private EntityManager _entityManager;
        private EventDispatcher _eventDispatcher;
        
        // Initialization event
        public event Action OnInitializationComplete;
        
        private void Awake()
        {
            // Handle singleton pattern
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Set default game state
            IsGameRunning = false;
            IsInitialized = false;
            
            // Random seed initialization
            Seed = UnityEngine.Random.Range(0, 999999);
            UnityEngine.Random.InitState(Seed);
            
            Debug.Log($"GameManager initialized with seed: {Seed}");
        }
        
        private void Start()
        {
            // Begin the initialization sequence
            InitializeManagers();
        }
        
        /// <summary>
        /// Initialize all required managers in the correct order
        /// </summary>
        private void InitializeManagers()
        {
            try
            {
                Debug.Log("Starting manager initialization sequence...");
                
                // 1. Create event dispatcher first as other systems will need it
                _eventDispatcher = CreateManager<EventDispatcher>("EventDispatcher");
                
                // 2. Initialize state manager for tracking game state
                _stateManager = CreateManager<StateManager>("StateManager");
                
                // 3. Initialize mod data manager for loading game data
                _modDataManager = CreateManager<ModDataManager>("ModDataManager");
                
                // 4. Initialize mod synchronizer for handling mod conflicts
                _modSynchronizer = CreateManager<ModSynchronizer>("ModSynchronizer");
                
                // 5. Initialize entity manager for managing game entities
                _entityManager = CreateManager<EntityManager>("EntityManager");
                
                // 6. Load base game data
                _modDataManager.LoadBaseMod();
                
                // Mark initialization as complete
                IsInitialized = true;
                OnInitializationComplete?.Invoke();
                
                Debug.Log("Manager initialization sequence completed successfully.");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error during manager initialization: {e.Message}\n{e.StackTrace}");
            }
        }
        
        /// <summary>
        /// Helper method to create and initialize a manager
        /// </summary>
        private T CreateManager<T>(string name) where T : MonoBehaviour
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform);
            var manager = go.AddComponent<T>();
            return manager;
        }
        
        /// <summary>
        /// Start a new game session
        /// </summary>
        public void StartNewGame()
        {
            if (!IsInitialized)
            {
                Debug.LogError("Cannot start new game - GameManager not fully initialized");
                return;
            }
            
            Debug.Log("Starting new game...");
            
            // Initialize game world
            _stateManager.ResetState();
            _entityManager.ClearEntities();
            
            // Load user mods if any
            _modDataManager.LoadUserMods();
            
            // Set game running state
            IsGameRunning = true;
            
            // Broadcast game start event
            _eventDispatcher.Dispatch(new GameStartEvent
            {
                TimeStamp = DateTime.Now,
                Seed = Seed
            });
            
            Debug.Log("New game started successfully.");
        }
        
        /// <summary>
        /// Save the current game state
        /// </summary>
        public void SaveGame(string saveFileName = "")
        {
            if (!IsGameRunning)
            {
                Debug.LogWarning("Cannot save game - No game currently running");
                return;
            }
            
            if (string.IsNullOrEmpty(saveFileName))
            {
                saveFileName = $"save_{DateTime.Now:yyyyMMdd_HHmmss}";
            }
            
            Debug.Log($"Saving game to '{saveFileName}'...");
            
            // Save game state
            _stateManager.SaveState(saveFileName);
            
            Debug.Log("Game saved successfully.");
        }
        
        /// <summary>
        /// Load a saved game state
        /// </summary>
        public void LoadGame(string saveFileName)
        {
            if (!IsInitialized)
            {
                Debug.LogError("Cannot load game - GameManager not fully initialized");
                return;
            }
            
            Debug.Log($"Loading game from '{saveFileName}'...");
            
            // Set running state to false during loading
            IsGameRunning = false;
            
            try
            {
                // Clear existing data
                _entityManager.ClearEntities();
                
                // Load game state
                _stateManager.LoadState(saveFileName);
                
                // Set game running state
                IsGameRunning = true;
                
                Debug.Log("Game loaded successfully.");
            }
            catch (Exception e)
            {
                Debug.LogError($"Error loading game: {e.Message}\n{e.StackTrace}");
            }
        }
        
        /// <summary>
        /// End the current game session
        /// </summary>
        public void EndGame()
        {
            if (!IsGameRunning)
            {
                Debug.LogWarning("Cannot end game - No game currently running");
                return;
            }
            
            Debug.Log("Ending current game...");
            
            // Broadcast game end event
            _eventDispatcher.Dispatch(new GameEndEvent
            {
                TimeStamp = DateTime.Now
            });
            
            // Set game running state
            IsGameRunning = false;
            
            Debug.Log("Game ended.");
        }
    }
    
    /// <summary>
    /// Event dispatched when a new game starts
    /// </summary>
    public class GameStartEvent
    {
        public DateTime TimeStamp { get; set; }
        public int Seed { get; set; }
    }
    
    /// <summary>
    /// Event dispatched when a game ends
    /// </summary>
    public class GameEndEvent
    {
        public DateTime TimeStamp { get; set; }
    }
} 