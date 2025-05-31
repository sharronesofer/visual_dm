using UnityEngine;
using System.Collections;
using VDM.UI.Core;

namespace VDM.Core.Managers
{
    /// <summary>
    /// Main entry point for Visual DM application.
    /// Handles initialization of core systems and application startup sequence.
    /// </summary>
    public class GameLoader : MonoBehaviour
    {
        [Header("Initialization Settings")]
        [SerializeField] private bool showLoadingScreen = true;
        [SerializeField] private float minLoadingTime = 2f;
        [SerializeField] private bool enableDebugLogging = true;
        
        [Header("Core System Prefabs")]
        [SerializeField] private GameObject uiManagerPrefab;
        [SerializeField] private GameObject modalSystemPrefab;
        [SerializeField] private GameObject notificationSystemPrefab;
        [SerializeField] private GameObject loadingSystemPrefab;
        
        [Header("Scene Management")]
        [SerializeField] private string mainSceneName = "Main";
        [SerializeField] private bool loadMainSceneAfterInit = true;
        
        // Initialization state
        private bool isInitialized = false;
        private LoadingOperation currentLoadingOperation;
        
        // Events
        public static System.Action OnGameInitialized;
        public static System.Action<string> OnInitializationStep;
        
        private void Awake()
        {
            // Ensure this GameObject persists across scene loads
            DontDestroyOnLoad(gameObject);
            
            // Set application settings
            Application.targetFrameRate = 60;
            
            if (enableDebugLogging)
            {
                Debug.Log("GameLoader: Starting Visual DM initialization...");
            }
        }
        
        private void Start()
        {
            StartCoroutine(InitializeGame());
        }
        
        /// <summary>
        /// Main game initialization coroutine.
        /// </summary>
        private IEnumerator InitializeGame()
        {
            if (isInitialized)
            {
                yield break;
            }
            
            float startTime = Time.time;
            
            // Start loading screen if enabled
            if (showLoadingScreen)
            {
                yield return StartCoroutine(InitializeLoadingSystem());
                currentLoadingOperation = LoadingSystem.Instance?.StartLoadingWithProgress("Initializing Visual DM...", false);
            }
            
            // Initialize core systems in order
            yield return StartCoroutine(InitializeCoreSystemsSequence());
            
            // Ensure minimum loading time
            float elapsedTime = Time.time - startTime;
            if (elapsedTime < minLoadingTime)
            {
                UpdateLoadingProgress(0.9f, "Finalizing initialization...");
                yield return new WaitForSeconds(minLoadingTime - elapsedTime);
            }
            
            // Complete initialization
            CompleteInitialization();
            
            // Load main scene if configured
            if (loadMainSceneAfterInit && !string.IsNullOrEmpty(mainSceneName))
            {
                yield return StartCoroutine(LoadMainScene());
            }
            
            isInitialized = true;
            OnGameInitialized?.Invoke();
            
            if (enableDebugLogging)
            {
                Debug.Log("GameLoader: Visual DM initialization complete!");
            }
        }
        
        /// <summary>
        /// Initialize core systems in sequence.
        /// </summary>
        private IEnumerator InitializeCoreSystemsSequence()
        {
            var initSteps = new[]
            {
                ("UI Manager", InitializeUIManager()),
                ("Modal System", InitializeModalSystem()),
                ("Notification System", InitializeNotificationSystem()),
                ("Game Services", InitializeGameServices()),
                ("System Integration", InitializeSystemIntegration()),
                ("Configuration", LoadConfiguration())
            };
            
            for (int i = 0; i < initSteps.Length; i++)
            {
                var (stepName, stepCoroutine) = initSteps[i];
                float progress = (float)i / initSteps.Length;
                
                UpdateLoadingProgress(progress, $"Initializing {stepName}...");
                OnInitializationStep?.Invoke(stepName);
                
                if (enableDebugLogging)
                {
                    Debug.Log($"GameLoader: Initializing {stepName}...");
                }
                
                yield return StartCoroutine(stepCoroutine);
                
                // Small delay between steps for visual feedback
                yield return new WaitForSeconds(0.1f);
            }
        }
        
        /// <summary>
        /// Initialize the loading system first.
        /// </summary>
        private IEnumerator InitializeLoadingSystem()
        {
            if (LoadingSystem.Instance == null)
            {
                if (loadingSystemPrefab != null)
                {
                    Instantiate(loadingSystemPrefab);
                }
                else
                {
                    // Create default loading system
                    GameObject loadingSystemObject = new GameObject("LoadingSystem");
                    loadingSystemObject.AddComponent<LoadingSystem>();
                    DontDestroyOnLoad(loadingSystemObject);
                }
            }
            
            yield return new WaitForEndOfFrame();
        }
        
        /// <summary>
        /// Initialize the UI Manager.
        /// </summary>
        private IEnumerator InitializeUIManager()
        {
            if (UIManager.Instance == null)
            {
                if (uiManagerPrefab != null)
                {
                    Instantiate(uiManagerPrefab);
                }
                else
                {
                    // Create default UI manager
                    GameObject uiManagerObject = new GameObject("UIManager");
                    uiManagerObject.AddComponent<UIManager>();
                    DontDestroyOnLoad(uiManagerObject);
                }
            }
            
            yield return new WaitForEndOfFrame();
        }
        
        /// <summary>
        /// Initialize the Modal System.
        /// </summary>
        private IEnumerator InitializeModalSystem()
        {
            if (ModalSystem.Instance == null)
            {
                if (modalSystemPrefab != null)
                {
                    Instantiate(modalSystemPrefab);
                }
                else
                {
                    // Create default modal system
                    GameObject modalSystemObject = new GameObject("ModalSystem");
                    modalSystemObject.AddComponent<ModalSystem>();
                    DontDestroyOnLoad(modalSystemObject);
                }
            }
            
            yield return new WaitForEndOfFrame();
        }
        
        /// <summary>
        /// Initialize the Notification System.
        /// </summary>
        private IEnumerator InitializeNotificationSystem()
        {
            if (NotificationSystem.Instance == null)
            {
                if (notificationSystemPrefab != null)
                {
                    Instantiate(notificationSystemPrefab);
                }
                else
                {
                    // Create default notification system
                    GameObject notificationSystemObject = new GameObject("NotificationSystem");
                    notificationSystemObject.AddComponent<NotificationSystem>();
                    DontDestroyOnLoad(notificationSystemObject);
                }
            }
            
            yield return new WaitForEndOfFrame();
        }
        
        /// <summary>
        /// Initialize game services and backend connections.
        /// </summary>
        private IEnumerator InitializeGameServices()
        {
            // TODO: Initialize backend API connections
            // TODO: Initialize WebSocket connections
            // TODO: Initialize authentication services
            // TODO: Initialize data services
            
            yield return new WaitForSeconds(0.5f); // Simulate initialization time
        }
        
        /// <summary>
        /// Initialize system integration and cross-system communication.
        /// </summary>
        private IEnumerator InitializeSystemIntegration()
        {
            // TODO: Setup event system integration
            // TODO: Initialize system-to-system communication
            // TODO: Setup data synchronization
            
            yield return new WaitForSeconds(0.3f); // Simulate initialization time
        }
        
        /// <summary>
        /// Load application configuration.
        /// </summary>
        private IEnumerator LoadConfiguration()
        {
            // TODO: Load user preferences
            // TODO: Load game settings
            // TODO: Load system configurations
            
            yield return new WaitForSeconds(0.2f); // Simulate loading time
        }
        
        /// <summary>
        /// Complete the initialization process.
        /// </summary>
        private void CompleteInitialization()
        {
            UpdateLoadingProgress(1f, "Initialization complete!");
            
            // Complete loading operation
            if (currentLoadingOperation != null && LoadingSystem.Instance != null)
            {
                LoadingSystem.Instance.CompleteLoading(currentLoadingOperation.Id);
                currentLoadingOperation = null;
            }
            
            // Show welcome notification
            if (NotificationSystem.Instance != null)
            {
                NotificationSystem.Instance.ShowSuccess("Visual DM initialized successfully!");
            }
        }
        
        /// <summary>
        /// Load the main scene.
        /// </summary>
        private IEnumerator LoadMainScene()
        {
            if (enableDebugLogging)
            {
                Debug.Log($"GameLoader: Loading main scene '{mainSceneName}'...");
            }
            
            // Start loading operation for scene transition
            var sceneLoadingOperation = LoadingSystem.Instance?.StartLoading("Loading main scene...");
            
            // Load scene asynchronously
            var asyncOperation = UnityEngine.SceneManagement.SceneManager.LoadSceneAsync(mainSceneName);
            
            if (asyncOperation != null)
            {
                while (!asyncOperation.isDone)
                {
                    // Update loading progress based on scene loading
                    if (sceneLoadingOperation != null && LoadingSystem.Instance != null)
                    {
                        LoadingSystem.Instance.UpdateProgress(sceneLoadingOperation.Id, asyncOperation.progress);
                    }
                    yield return null;
                }
            }
            
            // Complete scene loading operation
            if (sceneLoadingOperation != null && LoadingSystem.Instance != null)
            {
                LoadingSystem.Instance.CompleteLoading(sceneLoadingOperation.Id);
            }
            
            yield return new WaitForEndOfFrame();
        }
        
        /// <summary>
        /// Update loading progress if loading system is available.
        /// </summary>
        private void UpdateLoadingProgress(float progress, string message)
        {
            if (currentLoadingOperation != null && LoadingSystem.Instance != null)
            {
                LoadingSystem.Instance.UpdateProgress(currentLoadingOperation.Id, progress, message);
            }
        }
        
        /// <summary>
        /// Handle application quit.
        /// </summary>
        private void OnApplicationQuit()
        {
            if (enableDebugLogging)
            {
                Debug.Log("GameLoader: Visual DM shutting down...");
            }
            
            // TODO: Cleanup systems
            // TODO: Save user data
            // TODO: Close connections
        }
        
        /// <summary>
        /// Handle application pause (mobile/focus lost).
        /// </summary>
        private void OnApplicationPause(bool pauseStatus)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"GameLoader: Application pause status: {pauseStatus}");
            }
            
            // TODO: Handle pause/resume logic
        }
        
        /// <summary>
        /// Handle application focus (desktop).
        /// </summary>
        private void OnApplicationFocus(bool hasFocus)
        {
            if (enableDebugLogging)
            {
                Debug.Log($"GameLoader: Application focus status: {hasFocus}");
            }
            
            // TODO: Handle focus/unfocus logic
        }
        
        /// <summary>
        /// Check if the game is fully initialized.
        /// </summary>
        public bool IsInitialized => isInitialized;
        
        /// <summary>
        /// Restart the application (useful for testing).
        /// </summary>
        public void RestartApplication()
        {
            if (enableDebugLogging)
            {
                Debug.Log("GameLoader: Restarting application...");
            }
            
            UnityEngine.SceneManagement.SceneManager.LoadScene(0);
        }
    }
} 