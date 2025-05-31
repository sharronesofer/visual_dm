using UnityEngine;
using VDM.Systems.Motifs.Models;
using VDM.Systems.Motifs.Services;
using VDM.Systems.Motifs.Services;
using VDM.Systems.Motifs.Ui;

namespace VDM.Systems.Motifs
{
    /// <summary>
    /// Main entry point and coordinator for the motif system
    /// </summary>
    public class MotifSystem : MonoBehaviour
    {
        [Header("Configuration")]
        [SerializeField] private string backendUrl = "http://localhost:8000/api/motifs";
        [SerializeField] private bool autoInitialize = true;
        [SerializeField] private bool enableDebugLogging = true;

        [Header("UI References")]
        [SerializeField] private MotifManagementPanel managementPanel;
        [SerializeField] private Canvas motifCanvas;

        [Header("Visualization")]
        [SerializeField] private GameObject motifVisualizationPrefab;
        [SerializeField] private bool enableVisualization = true;

        // System components
        private MotifApiService _apiService;
        private MotifManager _motifManager;

        // Singleton
        private static MotifSystem _instance;
        public static MotifSystem Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = FindObjectOfType<MotifSystem>();
                    if (_instance == null)
                    {
                        var go = new GameObject("MotifSystem");
                        _instance = go.AddComponent<MotifSystem>();
                        DontDestroyOnLoad(go);
                    }
                }
                return _instance;
            }
        }

        #region Unity Lifecycle

        private void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
                
                if (autoInitialize)
                {
                    Initialize();
                }
            }
            else if (_instance != this)
            {
                Destroy(gameObject);
            }
        }

        private void Start()
        {
            if (autoInitialize && IsInitialized)
            {
                StartSystem();
            }
        }

        #endregion

        #region Public API

        /// <summary>
        /// Check if the motif system is initialized
        /// </summary>
        public bool IsInitialized { get; private set; }

        /// <summary>
        /// Initialize the motif system
        /// </summary>
        public void Initialize()
        {
            if (IsInitialized)
            {
                LogDebug("Motif system already initialized");
                return;
            }

            LogDebug("Initializing motif system...");

            try
            {
                InitializeApiService();
                InitializeManager();
                InitializeUI();
                
                IsInitialized = true;
                LogDebug("Motif system initialized successfully");
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[MotifSystem] Failed to initialize: {ex.Message}");
            }
        }

        /// <summary>
        /// Start the motif system (load initial data, etc.)
        /// </summary>
        public void StartSystem()
        {
            if (!IsInitialized)
            {
                LogDebug("Cannot start system - not initialized");
                return;
            }

            LogDebug("Starting motif system...");

            // Load initial motifs
            if (_motifManager != null)
            {
                _motifManager.RefreshMotifs();
            }

            // Show management panel if available
            if (managementPanel != null)
            {
                managementPanel.RefreshMotifs();
            }

            LogDebug("Motif system started");
        }

        /// <summary>
        /// Get the API service instance
        /// </summary>
        public MotifApiService GetApiService()
        {
            return _apiService;
        }

        /// <summary>
        /// Get the motif manager instance
        /// </summary>
        public MotifManager GetMotifManager()
        {
            return _motifManager;
        }

        /// <summary>
        /// Get the management panel instance
        /// </summary>
        public MotifManagementPanel GetManagementPanel()
        {
            return managementPanel;
        }

        /// <summary>
        /// Show the motif management UI
        /// </summary>
        public void ShowManagementUI()
        {
            if (managementPanel != null)
            {
                managementPanel.Show();
            }
            else
            {
                LogDebug("Management panel not available");
            }
        }

        /// <summary>
        /// Hide the motif management UI
        /// </summary>
        public void HideManagementUI()
        {
            if (managementPanel != null)
            {
                managementPanel.Hide();
            }
        }

        /// <summary>
        /// Toggle the motif management UI
        /// </summary>
        public void ToggleManagementUI()
        {
            if (managementPanel != null)
            {
                managementPanel.Toggle();
            }
        }

        /// <summary>
        /// Create a test motif for demonstration
        /// </summary>
        public async void CreateTestMotif()
        {
            if (!IsInitialized || _motifManager == null)
            {
                LogDebug("Cannot create test motif - system not ready");
                return;
            }

            var testData = new MotifCreateData
            {
                name = "Test Motif",
                description = "A test motif created from the Unity frontend",
                category = MotifCategory.Hope,
                scope = MotifScope.Local,
                intensity = 7,
                durationDays = 10,
                location = new LocationInfo("test_region", Vector2.zero, 5f)
            };

            LogDebug("Creating test motif...");
            
            try
            {
                var motif = await _motifManager.CreateMotifAsync(testData);
                if (motif != null)
                {
                    LogDebug($"Test motif created: {motif.name}");
                }
                else
                {
                    LogDebug("Failed to create test motif");
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[MotifSystem] Error creating test motif: {ex.Message}");
            }
        }

        /// <summary>
        /// Generate a random motif for demonstration
        /// </summary>
        public async void GenerateRandomMotif()
        {
            if (!IsInitialized || _motifManager == null)
            {
                LogDebug("Cannot generate random motif - system not ready");
                return;
            }

            LogDebug("Generating random motif...");
            
            try
            {
                var motif = await _motifManager.GenerateRandomMotifAsync(MotifScope.Local);
                if (motif != null)
                {
                    LogDebug($"Random motif generated: {motif.name}");
                }
                else
                {
                    LogDebug("Failed to generate random motif");
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"[MotifSystem] Error generating random motif: {ex.Message}");
            }
        }

        #endregion

        #region Configuration

        /// <summary>
        /// Set the backend URL
        /// </summary>
        public void SetBackendUrl(string url)
        {
            backendUrl = url;
            
            if (_apiService != null)
            {
                _apiService.SetBaseUrl(url);
            }
        }

        /// <summary>
        /// Enable or disable visualization
        /// </summary>
        public void SetVisualizationEnabled(bool enabled)
        {
            enableVisualization = enabled;
            
            if (_motifManager != null)
            {
                _motifManager.SetVisualizationEnabled(enabled);
            }
        }

        /// <summary>
        /// Enable or disable debug logging
        /// </summary>
        public void SetDebugLogging(bool enabled)
        {
            enableDebugLogging = enabled;
        }

        #endregion

        #region Initialization

        private void InitializeApiService()
        {
            // Get or create API service
            _apiService = MotifApiService.Instance;
            
            if (_apiService != null)
            {
                _apiService.SetBaseUrl(backendUrl);
                _apiService.SetLogging(enableDebugLogging);
                LogDebug("API service initialized");
            }
            else
            {
                throw new System.Exception("Failed to initialize API service");
            }
        }

        private void InitializeManager()
        {
            // Get or create motif manager
            _motifManager = MotifManager.Instance;
            
            if (_motifManager != null)
            {
                _motifManager.SetVisualizationEnabled(enableVisualization);
                
                // Set visualization prefab if provided
                if (motifVisualizationPrefab != null)
                {
                    // This would require adding a method to MotifManager to set the prefab
                    // For now, we'll assume it's set in the inspector
                }
                
                LogDebug("Motif manager initialized");
            }
            else
            {
                throw new System.Exception("Failed to initialize motif manager");
            }
        }

        private void InitializeUI()
        {
            // Find management panel if not assigned
            if (managementPanel == null)
            {
                managementPanel = FindObjectOfType<MotifManagementPanel>();
            }

            // Find canvas if not assigned
            if (motifCanvas == null)
            {
                motifCanvas = FindObjectOfType<Canvas>();
            }

            if (managementPanel != null)
            {
                managementPanel.Initialize();
                LogDebug("Management panel initialized");
            }
            else
            {
                LogDebug("No management panel found - UI features will be limited");
            }
        }

        #endregion

        #region Helper Methods

        private void LogDebug(string message)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"[MotifSystem] {message}");
            }
        }

        #endregion

        #region Unity Editor Support

#if UNITY_EDITOR
        [ContextMenu("Initialize System")]
        private void EditorInitialize()
        {
            Initialize();
        }

        [ContextMenu("Start System")]
        private void EditorStart()
        {
            StartSystem();
        }

        [ContextMenu("Create Test Motif")]
        private void EditorCreateTestMotif()
        {
            CreateTestMotif();
        }

        [ContextMenu("Generate Random Motif")]
        private void EditorGenerateRandomMotif()
        {
            GenerateRandomMotif();
        }

        [ContextMenu("Show Management UI")]
        private void EditorShowManagementUI()
        {
            ShowManagementUI();
        }

        [ContextMenu("Hide Management UI")]
        private void EditorHideManagementUI()
        {
            HideManagementUI();
        }
#endif

        #endregion
    }
} 