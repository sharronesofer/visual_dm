using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;
using VisualDM.API;
using VisualDM.SceneManagement;

namespace VisualDM.Core
{
    /// <summary>
    /// Core game manager that handles initialization and game flow
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        [SerializeField] private ApiConfig _apiConfig;
        
        private static GameManager _instance;
        private ApiClient _apiClient;
        private bool _isInitialized;
        private CancellationTokenSource _lifetimeCts;

        public static GameManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    // Find existing instance or create one
                    _instance = FindObjectOfType<GameManager>();
                    if (_instance == null)
                    {
                        GameObject gameObject = new GameObject("GameManager");
                        _instance = gameObject.AddComponent<GameManager>();
                        DontDestroyOnLoad(gameObject);
                    }
                }
                return _instance;
            }
        }

        public ApiClient ApiClient => _apiClient;
        public bool IsInitialized => _isInitialized;

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Create lifetime cancellation token source
            _lifetimeCts = new CancellationTokenSource();
            
            // Subscribe to auth-related events
            EventSystem.Subscribe<AuthenticationExpiredEvent>(OnAuthenticationExpired);
        }

        private void OnDestroy()
        {
            // Unsubscribe from events
            EventSystem.Unsubscribe<AuthenticationExpiredEvent>(OnAuthenticationExpired);
            
            // Cancel any ongoing operations
            _lifetimeCts?.Cancel();
            _lifetimeCts?.Dispose();
            _lifetimeCts = null;
        }

        /// <summary>
        /// Initialize the game manager and core systems
        /// </summary>
        public async UniTask InitializeAsync()
        {
            if (_isInitialized)
            {
                Debug.LogWarning("GameManager is already initialized");
                return;
            }
            
            try
            {
                Debug.Log("Initializing GameManager...");
                
                // Initialize API client
                if (_apiConfig == null)
                {
                    Debug.LogError("API Config is missing. Please assign it in the inspector.");
                    return;
                }
                
                _apiClient = new ApiClient(_apiConfig);
                
                // Initialize other core systems
                // TODO: Add initialization for other systems as needed
                
                _isInitialized = true;
                Debug.Log("GameManager initialization complete");
                
                // Publish initialization complete event
                EventSystem.Publish(new GameInitializedEvent());
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Error initializing GameManager: {ex.Message}");
                EventSystem.Publish(new GameInitializationFailedEvent { Error = ex.Message });
            }
        }

        /// <summary>
        /// Start a new game session
        /// </summary>
        public async UniTask StartNewGameAsync()
        {
            if (!_isInitialized)
            {
                Debug.LogError("GameManager is not initialized. Call InitializeAsync first.");
                return;
            }
            
            try
            {
                Debug.Log("Starting new game...");
                
                // Load the main game scene
                await SceneManager.Instance.LoadSceneAsync("Game", showLoadingScreen: true, cancellationToken: _lifetimeCts.Token);
                
                // Publish new game started event
                EventSystem.Publish(new GameStartedEvent { IsNewGame = true });
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Error starting new game: {ex.Message}");
            }
        }

        /// <summary>
        /// Handle authentication expired event
        /// </summary>
        private void OnAuthenticationExpired(AuthenticationExpiredEvent evt)
        {
            Debug.Log("Authentication expired. Returning to login screen...");
            
            // Load the login scene when authentication expires
            SceneManager.Instance.LoadSceneAsync("Login", showLoadingScreen: true).Forget();
        }
    }
    
    #region Events
    
    public class GameInitializedEvent
    {
    }
    
    public class GameInitializationFailedEvent
    {
        public string Error { get; set; }
    }
    
    public class GameStartedEvent
    {
        public bool IsNewGame { get; set; }
    }
    
    #endregion
} 