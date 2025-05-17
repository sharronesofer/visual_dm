using System;
using System.Collections.Generic;
using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;
using UnityEngine.SceneManagement;
using VisualDM.Core;

namespace VisualDM.SceneManagement
{
    /// <summary>
    /// Manages scene loading, transitions, and dependencies
    /// </summary>
    public class SceneManager : MonoBehaviour
    {
        [SerializeField] private SceneTransitionSettings _transitionSettings;
        
        private static SceneManager _instance;
        private Scene _currentScene;
        private Dictionary<string, SceneData> _loadedScenes = new Dictionary<string, SceneData>();
        private CancellationTokenSource _loadingCts;

        public static SceneManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    // Find existing instance or create one
                    _instance = FindObjectOfType<SceneManager>();
                    if (_instance == null)
                    {
                        GameObject gameObject = new GameObject("SceneManager");
                        _instance = gameObject.AddComponent<SceneManager>();
                        DontDestroyOnLoad(gameObject);
                    }
                }
                return _instance;
            }
        }

        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
            
            // Initialize data for the currently active scene
            _currentScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            _loadedScenes[_currentScene.name] = new SceneData
            {
                Name = _currentScene.name,
                IsLoaded = true,
                IsActive = true
            };
        }

        /// <summary>
        /// Load a scene asynchronously with transition effects
        /// </summary>
        public async UniTask<bool> LoadSceneAsync(string sceneName, LoadSceneMode loadMode = LoadSceneMode.Single, bool showLoadingScreen = true, CancellationToken cancellationToken = default)
        {
            try
            {
                // Cancel any ongoing loading operation
                _loadingCts?.Cancel();
                _loadingCts = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                
                EventSystem.Publish(new SceneLoadStartEvent { SceneName = sceneName });
                
                // Show loading screen if requested
                if (showLoadingScreen && _transitionSettings != null)
                {
                    await ShowTransition(_transitionSettings.FadeInDuration, _loadingCts.Token);
                }
                
                // Begin loading the scene
                var asyncOperation = UnityEngine.SceneManagement.SceneManager.LoadSceneAsync(sceneName, loadMode);
                asyncOperation.allowSceneActivation = false;
                
                // Wait until the load has finished
                while (asyncOperation.progress < 0.9f)
                {
                    // Report progress
                    float progress = Mathf.Clamp01(asyncOperation.progress / 0.9f);
                    EventSystem.Publish(new SceneLoadProgressEvent { SceneName = sceneName, Progress = progress });
                    
                    await UniTask.Yield(_loadingCts.Token);
                }
                
                // Activate the scene
                asyncOperation.allowSceneActivation = true;
                await asyncOperation;
                
                // Update current scene tracking
                if (loadMode == LoadSceneMode.Single)
                {
                    // Update previous scene status
                    if (_loadedScenes.ContainsKey(_currentScene.name))
                    {
                        _loadedScenes[_currentScene.name].IsActive = false;
                        _loadedScenes[_currentScene.name].IsLoaded = false;
                    }
                    
                    _currentScene = UnityEngine.SceneManagement.SceneManager.GetSceneByName(sceneName);
                }
                
                // Add or update scene in loaded scenes dictionary
                _loadedScenes[sceneName] = new SceneData
                {
                    Name = sceneName,
                    IsLoaded = true,
                    IsActive = loadMode == LoadSceneMode.Single || !_loadedScenes.ContainsKey(sceneName)
                };
                
                // Hide loading screen
                if (showLoadingScreen && _transitionSettings != null)
                {
                    await HideTransition(_transitionSettings.FadeOutDuration, _loadingCts.Token);
                }
                
                EventSystem.Publish(new SceneLoadCompleteEvent { SceneName = sceneName });
                return true;
            }
            catch (OperationCanceledException)
            {
                Debug.Log("Scene loading was canceled");
                return false;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error loading scene {sceneName}: {ex.Message}");
                EventSystem.Publish(new SceneLoadFailedEvent { SceneName = sceneName, Error = ex.Message });
                return false;
            }
        }
        
        /// <summary>
        /// Unload a scene asynchronously
        /// </summary>
        public async UniTask<bool> UnloadSceneAsync(string sceneName, CancellationToken cancellationToken = default)
        {
            try
            {
                // Check if scene is loaded
                if (!_loadedScenes.TryGetValue(sceneName, out var sceneData) || !sceneData.IsLoaded)
                {
                    Debug.LogWarning($"Scene {sceneName} is not loaded, nothing to unload");
                    return false;
                }
                
                EventSystem.Publish(new SceneUnloadStartEvent { SceneName = sceneName });
                
                // Unload the scene
                var asyncOperation = UnityEngine.SceneManagement.SceneManager.UnloadSceneAsync(sceneName);
                await asyncOperation;
                
                // Update scene data
                _loadedScenes[sceneName].IsLoaded = false;
                _loadedScenes[sceneName].IsActive = false;
                
                EventSystem.Publish(new SceneUnloadCompleteEvent { SceneName = sceneName });
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogError($"Error unloading scene {sceneName}: {ex.Message}");
                EventSystem.Publish(new SceneUnloadFailedEvent { SceneName = sceneName, Error = ex.Message });
                return false;
            }
        }
        
        /// <summary>
        /// Show transition effect (fade in)
        /// </summary>
        private async UniTask ShowTransition(float duration, CancellationToken cancellationToken)
        {
            // Create transition overlay if needed
            await UniTask.Delay(TimeSpan.FromSeconds(duration), cancellationToken: cancellationToken);
        }
        
        /// <summary>
        /// Hide transition effect (fade out)
        /// </summary>
        private async UniTask HideTransition(float duration, CancellationToken cancellationToken)
        {
            await UniTask.Delay(TimeSpan.FromSeconds(duration), cancellationToken: cancellationToken);
        }
        
        /// <summary>
        /// Get the current active scene name
        /// </summary>
        public string GetCurrentSceneName()
        {
            return _currentScene.name;
        }
        
        /// <summary>
        /// Check if a scene is currently loaded
        /// </summary>
        public bool IsSceneLoaded(string sceneName)
        {
            return _loadedScenes.TryGetValue(sceneName, out var sceneData) && sceneData.IsLoaded;
        }
    }
    
    /// <summary>
    /// Data structure to track loaded scenes
    /// </summary>
    [Serializable]
    public class SceneData
    {
        public string Name;
        public bool IsLoaded;
        public bool IsActive;
    }
    
    /// <summary>
    /// Settings for scene transitions
    /// </summary>
    [CreateAssetMenu(fileName = "SceneTransitionSettings", menuName = "VisualDM/Scene Transition Settings")]
    public class SceneTransitionSettings : ScriptableObject
    {
        [Tooltip("Duration of the fade in transition in seconds")]
        public float FadeInDuration = 0.5f;
        
        [Tooltip("Duration of the fade out transition in seconds")]
        public float FadeOutDuration = 0.5f;
        
        [Tooltip("Curve for fade transitions")]
        public AnimationCurve FadeCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);
        
        [Tooltip("Color for the transition overlay")]
        public Color TransitionColor = Color.black;
    }
    
    #region Events
    
    public class SceneLoadStartEvent
    {
        public string SceneName { get; set; }
    }
    
    public class SceneLoadProgressEvent
    {
        public string SceneName { get; set; }
        public float Progress { get; set; }
    }
    
    public class SceneLoadCompleteEvent
    {
        public string SceneName { get; set; }
    }
    
    public class SceneLoadFailedEvent
    {
        public string SceneName { get; set; }
        public string Error { get; set; }
    }
    
    public class SceneUnloadStartEvent
    {
        public string SceneName { get; set; }
    }
    
    public class SceneUnloadCompleteEvent
    {
        public string SceneName { get; set; }
    }
    
    public class SceneUnloadFailedEvent
    {
        public string SceneName { get; set; }
        public string Error { get; set; }
    }
    
    #endregion
} 