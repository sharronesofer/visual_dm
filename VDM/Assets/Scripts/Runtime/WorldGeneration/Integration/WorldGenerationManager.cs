using System.Collections.Generic;
using System;
using UnityEngine;
using VDM.Runtime.WorldGeneration.Models;
using VDM.Runtime.WorldGeneration.Services;
using VDM.Runtime.WorldGeneration.UI;


namespace VDM.Runtime.WorldGeneration.Integration
{
    /// <summary>
    /// Central manager for world generation system integration
    /// </summary>
    public class WorldGenerationManager : MonoBehaviour
    {
        [Header("Service References")]
        [SerializeField] private WorldGenerationService worldGenService;
        [SerializeField] private WorldGenerationWebSocketHandler webSocketHandler;

        [Header("UI References")]
        [SerializeField] private WorldGenerationPanel mainPanel;
        [SerializeField] private GameObject worldMapViewer;

        [Header("Configuration")]
        [SerializeField] private bool autoConnectWebSocket = true;
        [SerializeField] private bool enableLogging = true;

        // State
        private bool isInitialized = false;
        private List<ContinentModel> loadedContinents = new List<ContinentModel>();
        private List<BiomeModel> loadedBiomes = new List<BiomeModel>();
        private WorldGenerationResult lastGenerationResult;

        // Events
        public event Action OnSystemInitialized;
        public event Action<WorldGenerationResult> OnWorldGenerated;
        public event Action<ContinentModel> OnContinentCreated;
        public event Action<string> OnError;

        #region Unity Lifecycle

        private void Awake()
        {
            ValidateReferences();
        }

        private void Start()
        {
            InitializeSystem();
        }

        private void OnDestroy()
        {
            CleanupSystem();
        }

        #endregion

        #region Initialization

        private void ValidateReferences()
        {
            if (worldGenService == null)
            {
                worldGenService = FindObjectOfType<WorldGenerationService>();
                if (worldGenService == null)
                {
                    Debug.LogError("WorldGenerationManager: WorldGenerationService not found");
                }
            }

            if (webSocketHandler == null)
            {
                webSocketHandler = FindObjectOfType<WorldGenerationWebSocketHandler>();
                if (webSocketHandler == null)
                {
                    Debug.LogError("WorldGenerationManager: WorldGenerationWebSocketHandler not found");
                }
            }

            if (mainPanel == null)
            {
                mainPanel = FindObjectOfType<WorldGenerationPanel>();
                if (mainPanel == null)
                {
                    Debug.LogWarning("WorldGenerationManager: WorldGenerationPanel not found");
                }
            }
        }

        private async void InitializeSystem()
        {
            try
            {
                if (enableLogging)
                    Debug.Log("[WorldGenerationManager] Initializing world generation system...");

                // Setup event handlers
                SetupEventHandlers();

                // Connect WebSocket if enabled
                if (autoConnectWebSocket && webSocketHandler != null)
                {
                    webSocketHandler.Connect();
                }

                // Load initial data
                await LoadInitialData();

                isInitialized = true;
                OnSystemInitialized?.Invoke();

                if (enableLogging)
                    Debug.Log("[WorldGenerationManager] World generation system initialized successfully");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldGenerationManager] Failed to initialize system: {ex.Message}");
                OnError?.Invoke($"System initialization failed: {ex.Message}");
            }
        }

        private void SetupEventHandlers()
        {
            // WebSocket events
            if (webSocketHandler != null)
            {
                webSocketHandler.OnGenerationComplete += OnGenerationComplete;
                webSocketHandler.OnGenerationError += OnGenerationError;
                webSocketHandler.OnContinentCreated += OnContinentCreatedHandler;
                webSocketHandler.OnError += OnWebSocketError;
            }

            // UI events
            if (mainPanel != null)
            {
                mainPanel.OnWorldGenerationComplete += OnWorldGenerationComplete;
                mainPanel.OnWorldGenerationError += OnWorldGenerationError;
            }
        }

        private void CleanupSystem()
        {
            // Cleanup WebSocket events
            if (webSocketHandler != null)
            {
                webSocketHandler.OnGenerationComplete -= OnGenerationComplete;
                webSocketHandler.OnGenerationError -= OnGenerationError;
                webSocketHandler.OnContinentCreated -= OnContinentCreatedHandler;
                webSocketHandler.OnError -= OnWebSocketError;
            }

            // Cleanup UI events
            if (mainPanel != null)
            {
                mainPanel.OnWorldGenerationComplete -= OnWorldGenerationComplete;
                mainPanel.OnWorldGenerationError -= OnWorldGenerationError;
            }
        }

        private async System.Threading.Tasks.Task LoadInitialData()
        {
            if (worldGenService == null) return;

            try
            {
                // Load continents
                var continentsResponse = await worldGenService.GetContinentsAsync();
                if (continentsResponse.success)
                {
                    loadedContinents = continentsResponse.data;
                    if (enableLogging)
                        Debug.Log($"[WorldGenerationManager] Loaded {loadedContinents.Count} continents");
                }

                // Load biomes
                var biomesResponse = await worldGenService.GetBiomesAsync();
                if (biomesResponse.success)
                {
                    loadedBiomes = biomesResponse.data;
                    if (enableLogging)
                        Debug.Log($"[WorldGenerationManager] Loaded {loadedBiomes.Count} biomes");
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"[WorldGenerationManager] Error loading initial data: {ex.Message}");
                throw;
            }
        }

        #endregion

        #region Event Handlers

        private void OnGenerationComplete(WorldGenerationResult result)
        {
            lastGenerationResult = result;
            OnWorldGenerated?.Invoke(result);

            if (enableLogging)
                Debug.Log($"[WorldGenerationManager] World generation completed: {result.worldName}");
        }

        private void OnGenerationError(string error)
        {
            Debug.LogError($"[WorldGenerationManager] Generation error: {error}");
            OnError?.Invoke($"Generation error: {error}");
        }

        private void OnContinentCreatedHandler(ContinentModel continent)
        {
            if (!loadedContinents.Exists(c => c.id == continent.id))
            {
                loadedContinents.Add(continent);
            }
            
            OnContinentCreated?.Invoke(continent);

            if (enableLogging)
                Debug.Log($"[WorldGenerationManager] Continent created: {continent.name}");
        }

        private void OnWebSocketError(string error)
        {
            Debug.LogError($"[WorldGenerationManager] WebSocket error: {error}");
            OnError?.Invoke($"WebSocket error: {error}");
        }

        private void OnWorldGenerationComplete(WorldGenerationResult result)
        {
            // Handle UI completion event
            OnGenerationComplete(result);
        }

        private void OnWorldGenerationError(string error)
        {
            // Handle UI error event
            OnGenerationError(error);
        }

        #endregion

        #region Public API

        /// <summary>
        /// Check if the system is initialized
        /// </summary>
        public bool IsInitialized => isInitialized;

        /// <summary>
        /// Get the world generation service
        /// </summary>
        public WorldGenerationService Service => worldGenService;

        /// <summary>
        /// Get the WebSocket handler
        /// </summary>
        public WorldGenerationWebSocketHandler WebSocketHandler => webSocketHandler;

        /// <summary>
        /// Get the main UI panel
        /// </summary>
        public WorldGenerationPanel MainPanel => mainPanel;

        /// <summary>
        /// Get loaded continents
        /// </summary>
        public List<ContinentModel> LoadedContinents => new List<ContinentModel>(loadedContinents);

        /// <summary>
        /// Get loaded biomes
        /// </summary>
        public List<BiomeModel> LoadedBiomes => new List<BiomeModel>(loadedBiomes);

        /// <summary>
        /// Get last generation result
        /// </summary>
        public WorldGenerationResult LastGenerationResult => lastGenerationResult;

        /// <summary>
        /// Show the world generation UI
        /// </summary>
        public void ShowUI()
        {
            if (mainPanel != null)
            {
                mainPanel.Show();
            }
        }

        /// <summary>
        /// Hide the world generation UI
        /// </summary>
        public void HideUI()
        {
            if (mainPanel != null)
            {
                mainPanel.Hide();
            }
        }

        /// <summary>
        /// Start world generation with specified configuration
        /// </summary>
        public async System.Threading.Tasks.Task<WorldGenerationResult> GenerateWorldAsync(WorldGenerationConfig config)
        {
            if (!isInitialized)
            {
                throw new InvalidOperationException("System not initialized");
            }

            if (worldGenService == null)
            {
                throw new InvalidOperationException("WorldGenerationService not available");
            }

            try
            {
                var response = await worldGenService.GenerateWorldAsync(config);
                if (response.success)
                {
                    return response.data;
                }
                else
                {
                    throw new Exception($"Generation failed: {string.Join(", ", response.errors)}");
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Generation failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Create a new continent
        /// </summary>
        public async System.Threading.Tasks.Task<ContinentModel> CreateContinentAsync(ContinentModel continent)
        {
            if (!isInitialized)
            {
                throw new InvalidOperationException("System not initialized");
            }

            if (worldGenService == null)
            {
                throw new InvalidOperationException("WorldGenerationService not available");
            }

            try
            {
                var response = await worldGenService.CreateContinentAsync(continent);
                if (response.success)
                {
                    return response.data;
                }
                else
                {
                    throw new Exception($"Continent creation failed: {string.Join(", ", response.errors)}");
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Continent creation failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Generate regions for a continent
        /// </summary>
        public async System.Threading.Tasks.Task<List<RegionGenerationResult>> GenerateRegionsAsync(string continentId, RegionGenerationParams parameters)
        {
            if (!isInitialized)
            {
                throw new InvalidOperationException("System not initialized");
            }

            if (worldGenService == null)
            {
                throw new InvalidOperationException("WorldGenerationService not available");
            }

            try
            {
                var response = await worldGenService.GenerateRegionsAsync(continentId, parameters);
                if (response.success)
                {
                    return response.data;
                }
                else
                {
                    throw new Exception($"Region generation failed: {string.Join(", ", response.errors)}");
                }
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Region generation failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Refresh loaded data from the server
        /// </summary>
        public async System.Threading.Tasks.Task RefreshDataAsync()
        {
            if (!isInitialized)
            {
                throw new InvalidOperationException("System not initialized");
            }

            try
            {
                await LoadInitialData();
                if (enableLogging)
                    Debug.Log("[WorldGenerationManager] Data refreshed successfully");
            }
            catch (Exception ex)
            {
                OnError?.Invoke($"Data refresh failed: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Connect to WebSocket for real-time updates
        /// </summary>
        public void ConnectWebSocket()
        {
            if (webSocketHandler != null)
            {
                webSocketHandler.Connect();
            }
        }

        /// <summary>
        /// Disconnect from WebSocket
        /// </summary>
        public void DisconnectWebSocket()
        {
            if (webSocketHandler != null)
            {
                webSocketHandler.Disconnect();
            }
        }

        /// <summary>
        /// Get WebSocket connection status
        /// </summary>
        public bool IsWebSocketConnected => webSocketHandler?.IsConnected ?? false;

        #endregion

        #region Utility Methods

        /// <summary>
        /// Find continent by ID
        /// </summary>
        public ContinentModel FindContinent(string continentId)
        {
            return loadedContinents.Find(c => c.id == continentId);
        }

        /// <summary>
        /// Find biome by ID
        /// </summary>
        public BiomeModel FindBiome(string biomeId)
        {
            return loadedBiomes.Find(b => b.id == biomeId);
        }

        /// <summary>
        /// Get system status information
        /// </summary>
        public SystemStatus GetSystemStatus()
        {
            return new SystemStatus
            {
                isInitialized = isInitialized,
                isWebSocketConnected = IsWebSocketConnected,
                continentCount = loadedContinents.Count,
                biomeCount = loadedBiomes.Count,
                hasLastGeneration = lastGenerationResult != null,
                serviceAvailable = worldGenService != null,
                webSocketAvailable = webSocketHandler != null,
                uiAvailable = mainPanel != null
            };
        }

        #endregion
    }

    /// <summary>
    /// System status information
    /// </summary>
    [Serializable]
    public class SystemStatus
    {
        public bool isInitialized;
        public bool isWebSocketConnected;
        public int continentCount;
        public int biomeCount;
        public bool hasLastGeneration;
        public bool serviceAvailable;
        public bool webSocketAvailable;
        public bool uiAvailable;
    }
} 