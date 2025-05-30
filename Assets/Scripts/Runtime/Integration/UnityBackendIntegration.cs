using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Runtime.Services.Contracts;
using VDM.Runtime.Services.Mock;
using VisualDM.DTOs.Core.Auth;
using VisualDM.DTOs.World.Region;

namespace VDM.Runtime.Integration
{
    /// <summary>
    /// Main integration manager that connects Unity frontend with backend services.
    /// Provides centralized access to all game systems and handles service initialization.
    /// </summary>
    public class UnityBackendIntegration : MonoBehaviour
    {
        [Header("Integration Configuration")]
        [SerializeField] private bool _useMockServices = true;
        [SerializeField] private string _backendBaseUrl = "http://localhost:3000/api";
        [SerializeField] private bool _enableOfflineMode = true;
        [SerializeField] private bool _autoInitialize = true;
        [SerializeField] private float _connectionTimeoutSeconds = 10f;
        
        [Header("Service Configuration")]
        [SerializeField] private bool _enableCharacterService = true;
        [SerializeField] private bool _enableQuestService = true;
        [SerializeField] private bool _enableWorldService = true;
        [SerializeField] private bool _enableCombatService = true;
        [SerializeField] private bool _enableNarrativeService = true;
        [SerializeField] private bool _enableEconomyService = true;
        [SerializeField] private bool _enableFactionService = true;
        
        [Header("Debug Settings")]
        [SerializeField] private bool _enableDebugLogging = true;
        [SerializeField] private bool _logAPIResponses = false;
        
        // Service instances
        private ICharacterAPIContract _characterAPI;
        private IQuestAPIContract _questAPI;
        private IWorldAPIContract _worldAPI;
        private ICombatAPIContract _combatAPI;
        private INarrativeAPIContract _narrativeAPI;
        private IEconomyAPIContract _economyAPI;
        private IFactionAPIContract _factionAPI;
        
        // Mock server reference (if using mock services)
        private MockAPIServer _mockServer;
        
        // Integration state
        private bool _isInitialized = false;
        private bool _isConnected = false;
        private List<string> _initializationErrors = new List<string>();
        
        // Events for service state changes
        public event Action<bool> OnConnectionStateChanged;
        public event Action OnServicesInitialized;
        public event Action<string> OnServiceError;
        
        #region Unity Lifecycle
        
        private void Awake()
        {
            // Ensure singleton behavior
            if (FindObjectsOfType<UnityBackendIntegration>().Length > 1)
            {
                Destroy(gameObject);
                return;
            }
            
            DontDestroyOnLoad(gameObject);
        }
        
        private async void Start()
        {
            if (_autoInitialize)
            {
                await InitializeServicesAsync();
            }
        }
        
        private void OnDestroy()
        {
            _ = CleanupServicesAsync();
        }
        
        #endregion
        
        #region Public API
        
        /// <summary>
        /// Initialize all enabled backend services
        /// </summary>
        public async Task<bool> InitializeServicesAsync()
        {
            if (_isInitialized)
            {
                LogDebug("Services already initialized");
                return true;
            }
            
            LogDebug("Initializing Unity Backend Integration...");
            _initializationErrors.Clear();
            
            try
            {
                // Setup service configuration
                var config = new APIServiceConfig
                {
                    BaseUrl = _backendBaseUrl,
                    TimeoutSeconds = (int)_connectionTimeoutSeconds,
                    EnableLogging = _enableDebugLogging,
                    UseMockData = _useMockServices
                };
                
                if (_useMockServices)
                {
                    await InitializeMockServicesAsync(config);
                }
                else
                {
                    await InitializeRealServicesAsync(config);
                }
                
                // Test service connectivity
                _isConnected = await TestServicesConnectivityAsync();
                
                _isInitialized = true;
                LogDebug($"Services initialized successfully. Connected: {_isConnected}");
                
                OnConnectionStateChanged?.Invoke(_isConnected);
                OnServicesInitialized?.Invoke();
                
                return true;
            }
            catch (Exception ex)
            {
                LogError($"Failed to initialize services: {ex.Message}");
                _initializationErrors.Add(ex.Message);
                OnServiceError?.Invoke(ex.Message);
                return false;
            }
        }
        
        /// <summary>
        /// Get the character service API
        /// </summary>
        public ICharacterAPIContract GetCharacterAPI()
        {
            EnsureInitialized();
            return _characterAPI;
        }
        
        /// <summary>
        /// Get the quest service API
        /// </summary>
        public IQuestAPIContract GetQuestAPI()
        {
            EnsureInitialized();
            return _questAPI;
        }
        
        /// <summary>
        /// Get the world service API
        /// </summary>
        public IWorldAPIContract GetWorldAPI()
        {
            EnsureInitialized();
            return _worldAPI;
        }
        
        /// <summary>
        /// Get the combat service API
        /// </summary>
        public ICombatAPIContract GetCombatAPI()
        {
            EnsureInitialized();
            return _combatAPI;
        }
        
        /// <summary>
        /// Get the narrative service API
        /// </summary>
        public INarrativeAPIContract GetNarrativeAPI()
        {
            EnsureInitialized();
            return _narrativeAPI;
        }
        
        /// <summary>
        /// Get the economy service API
        /// </summary>
        public IEconomyAPIContract GetEconomyAPI()
        {
            EnsureInitialized();
            return _economyAPI;
        }
        
        /// <summary>
        /// Get the faction service API
        /// </summary>
        public IFactionAPIContract GetFactionAPI()
        {
            EnsureInitialized();
            return _factionAPI;
        }
        
        /// <summary>
        /// Check if services are initialized and connected
        /// </summary>
        public bool IsReady => _isInitialized && _isConnected;
        
        /// <summary>
        /// Get current connection status
        /// </summary>
        public bool IsConnected => _isConnected;
        
        /// <summary>
        /// Get any initialization errors
        /// </summary>
        public List<string> GetInitializationErrors() => new List<string>(_initializationErrors);
        
        /// <summary>
        /// Manually test service connectivity
        /// </summary>
        public async Task<bool> TestConnectivityAsync()
        {
            _isConnected = await TestServicesConnectivityAsync();
            OnConnectionStateChanged?.Invoke(_isConnected);
            return _isConnected;
        }
        
        /// <summary>
        /// Switch between mock and real services (requires re-initialization)
        /// </summary>
        public async Task<bool> SwitchToMockServicesAsync(bool useMock)
        {
            if (_useMockServices == useMock)
                return true;
            
            _useMockServices = useMock;
            _isInitialized = false;
            _isConnected = false;
            
            return await InitializeServicesAsync();
        }
        
        #endregion
        
        #region Service Initialization
        
        private async Task InitializeMockServicesAsync(APIServiceConfig config)
        {
            LogDebug("Initializing mock services...");
            
            // Create or find mock server
            _mockServer = FindObjectOfType<MockAPIServer>();
            if (_mockServer == null)
            {
                var mockServerGO = new GameObject("MockAPIServer");
                mockServerGO.transform.SetParent(transform);
                _mockServer = mockServerGO.AddComponent<MockAPIServer>();
                _mockServer.InitializeMockServer();
            }
            
            // Initialize mock service instances
            if (_enableCharacterService)
            {
                _characterAPI = _mockServer.GetCharacterAPI();
                await _characterAPI.InitializeAsync(config);
            }
            
            if (_enableQuestService)
            {
                _questAPI = _mockServer.GetQuestAPI();
                await _questAPI.InitializeAsync(config);
            }
            
            if (_enableWorldService)
            {
                _worldAPI = _mockServer.GetWorldAPI();
                await _worldAPI.InitializeAsync(config);
            }
            
            if (_enableCombatService)
            {
                _combatAPI = _mockServer.GetCombatAPI();
                await _combatAPI.InitializeAsync(config);
            }
            
            if (_enableNarrativeService)
            {
                _narrativeAPI = _mockServer.GetNarrativeAPI();
                await _narrativeAPI.InitializeAsync(config);
            }
            
            if (_enableEconomyService)
            {
                _economyAPI = _mockServer.GetEconomyAPI();
                await _economyAPI.InitializeAsync(config);
            }
            
            if (_enableFactionService)
            {
                _factionAPI = _mockServer.GetFactionAPI();
                await _factionAPI.InitializeAsync(config);
            }
            
            LogDebug("Mock services initialized successfully");
        }
        
        private async Task InitializeRealServicesAsync(APIServiceConfig config)
        {
            LogDebug("Initializing real backend services...");
            
            // TODO: Implement real service initialization
            // This would create actual HTTP client-based implementations
            // For now, we'll use mock services as fallback
            
            LogDebug("Real services not yet implemented, falling back to mock services");
            await InitializeMockServicesAsync(config);
        }
        
        private async Task<bool> TestServicesConnectivityAsync()
        {
            LogDebug("Testing service connectivity...");
            
            try
            {
                var connectivityTasks = new List<Task<bool>>();
                
                if (_characterAPI != null)
                    connectivityTasks.Add(_characterAPI.TestConnectionAsync());
                
                if (_questAPI != null)
                    connectivityTasks.Add(_questAPI.TestConnectionAsync());
                
                if (_worldAPI != null)
                    connectivityTasks.Add(_worldAPI.TestConnectionAsync());
                
                if (_combatAPI != null)
                    connectivityTasks.Add(_combatAPI.TestConnectionAsync());
                
                if (_narrativeAPI != null)
                    connectivityTasks.Add(_narrativeAPI.TestConnectionAsync());
                
                if (_economyAPI != null)
                    connectivityTasks.Add(_economyAPI.TestConnectionAsync());
                
                if (_factionAPI != null)
                    connectivityTasks.Add(_factionAPI.TestConnectionAsync());
                
                var results = await Task.WhenAll(connectivityTasks);
                
                bool allConnected = true;
                foreach (var result in results)
                {
                    if (!result)
                    {
                        allConnected = false;
                        break;
                    }
                }
                
                LogDebug($"Connectivity test completed. All services connected: {allConnected}");
                return allConnected;
            }
            catch (Exception ex)
            {
                LogError($"Connectivity test failed: {ex.Message}");
                return false;
            }
        }
        
        #endregion
        
        #region Service Cleanup
        
        private async Task CleanupServicesAsync()
        {
            LogDebug("Cleaning up services...");
            
            var cleanupTasks = new List<Task>();
            
            if (_characterAPI != null)
                cleanupTasks.Add(_characterAPI.DisposeAsync());
            
            if (_questAPI != null)
                cleanupTasks.Add(_questAPI.DisposeAsync());
            
            if (_worldAPI != null)
                cleanupTasks.Add(_worldAPI.DisposeAsync());
            
            if (_combatAPI != null)
                cleanupTasks.Add(_combatAPI.DisposeAsync());
            
            if (_narrativeAPI != null)
                cleanupTasks.Add(_narrativeAPI.DisposeAsync());
            
            if (_economyAPI != null)
                cleanupTasks.Add(_economyAPI.DisposeAsync());
            
            if (_factionAPI != null)
                cleanupTasks.Add(_factionAPI.DisposeAsync());
            
            try
            {
                await Task.WhenAll(cleanupTasks);
                LogDebug("Services cleaned up successfully");
            }
            catch (Exception ex)
            {
                LogError($"Error during service cleanup: {ex.Message}");
            }
        }
        
        #endregion
        
        #region Helper Methods
        
        private void EnsureInitialized()
        {
            if (!_isInitialized)
            {
                throw new InvalidOperationException("Services not initialized. Call InitializeServicesAsync() first.");
            }
        }
        
        private void LogDebug(string message)
        {
            if (_enableDebugLogging)
                Debug.Log($"[UnityBackendIntegration] {message}");
        }
        
        private void LogError(string message)
        {
            Debug.LogError($"[UnityBackendIntegration] {message}");
        }
        
        #endregion
        
        #region Example Usage Methods
        
        /// <summary>
        /// Example method showing how to use the character API
        /// </summary>
        public async Task<CharacterDTO> GetCharacterExampleAsync(string characterId)
        {
            try
            {
                var response = await GetCharacterAPI().GetCharacterAsync(characterId);
                
                if (response.IsSuccess)
                {
                    LogDebug($"Retrieved character: {response.Data.Name}");
                    return response.Data;
                }
                else
                {
                    LogError($"Failed to get character: {response.Error}");
                    OnServiceError?.Invoke(response.Error);
                    return null;
                }
            }
            catch (Exception ex)
            {
                LogError($"Exception getting character: {ex.Message}");
                OnServiceError?.Invoke(ex.Message);
                return null;
            }
        }
        
        /// <summary>
        /// Example method showing how to use the world API
        /// </summary>
        public async Task<List<RegionDTO>> GetRegionsExampleAsync()
        {
            try
            {
                var response = await GetWorldAPI().GetRegionsAsync();
                
                if (response.IsSuccess)
                {
                    LogDebug($"Retrieved {response.Data.Count} regions");
                    return response.Data;
                }
                else
                {
                    LogError($"Failed to get regions: {response.Error}");
                    OnServiceError?.Invoke(response.Error);
                    return new List<RegionDTO>();
                }
            }
            catch (Exception ex)
            {
                LogError($"Exception getting regions: {ex.Message}");
                OnServiceError?.Invoke(ex.Message);
                return new List<RegionDTO>();
            }
        }
        
        #endregion
    }
    
    /// <summary>
    /// Static helper class for easy access to the integration manager
    /// </summary>
    public static class BackendServices
    {
        private static UnityBackendIntegration _instance;
        
        /// <summary>
        /// Get the integration manager instance
        /// </summary>
        public static UnityBackendIntegration Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<UnityBackendIntegration>();
                    if (_instance == null)
                    {
                        Debug.LogError("UnityBackendIntegration not found in scene. Please add it to your scene.");
                    }
                }
                return _instance;
            }
        }
        
        /// <summary>
        /// Quick access to character API
        /// </summary>
        public static ICharacterAPIContract Character => Instance?.GetCharacterAPI();
        
        /// <summary>
        /// Quick access to quest API
        /// </summary>
        public static IQuestAPIContract Quest => Instance?.GetQuestAPI();
        
        /// <summary>
        /// Quick access to world API
        /// </summary>
        public static IWorldAPIContract World => Instance?.GetWorldAPI();
        
        /// <summary>
        /// Quick access to combat API
        /// </summary>
        public static ICombatAPIContract Combat => Instance?.GetCombatAPI();
        
        /// <summary>
        /// Quick access to narrative API
        /// </summary>
        public static INarrativeAPIContract Narrative => Instance?.GetNarrativeAPI();
        
        /// <summary>
        /// Quick access to economy API
        /// </summary>
        public static IEconomyAPIContract Economy => Instance?.GetEconomyAPI();
        
        /// <summary>
        /// Quick access to faction API
        /// </summary>
        public static IFactionAPIContract Faction => Instance?.GetFactionAPI();
        
        /// <summary>
        /// Check if services are ready to use
        /// </summary>
        public static bool IsReady => Instance?.IsReady ?? false;
    }
} 