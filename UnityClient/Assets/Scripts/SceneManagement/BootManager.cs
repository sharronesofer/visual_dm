using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;
using VisualDM.Core;
using VisualDM.SceneManagement;

namespace VisualDM.SceneManagement
{
    /// <summary>
    /// Handles the boot sequence and initialization of the application
    /// </summary>
    public class BootManager : MonoBehaviour
    {
        [SerializeField] private string _initialSceneName = "Main";
        [SerializeField] private float _minimumLoadTime = 2.0f;
        
        private CancellationTokenSource _bootCts;

        private async void Start()
        {
            _bootCts = new CancellationTokenSource();
            
            try
            {
                Debug.Log("Starting boot sequence...");
                
                // Initialize core systems
                await InitializeCoreSystemsAsync(_bootCts.Token);
                
                // Wait for minimum boot time to show splash screen or loading animation
                await UniTask.Delay(System.TimeSpan.FromSeconds(_minimumLoadTime), cancellationToken: _bootCts.Token);
                
                // Load initial scene
                await LoadInitialSceneAsync(_bootCts.Token);
                
                Debug.Log("Boot sequence complete");
            }
            catch (System.OperationCanceledException)
            {
                Debug.Log("Boot sequence was canceled");
            }
            catch (System.Exception ex)
            {
                Debug.LogError($"Error during boot sequence: {ex.Message}");
                
                // Handle critical errors during boot
                // TODO: Show error UI to the user
            }
        }

        private void OnDestroy()
        {
            _bootCts?.Cancel();
            _bootCts?.Dispose();
            _bootCts = null;
        }

        /// <summary>
        /// Initialize all core systems required for the game
        /// </summary>
        private async UniTask InitializeCoreSystemsAsync(CancellationToken cancellationToken)
        {
            // Wait for SceneManager to be available
            while (SceneManager.Instance == null)
            {
                await UniTask.Yield(cancellationToken);
            }
            
            // Initialize GameManager
            await GameManager.Instance.InitializeAsync();
            
            // Initialize other core systems here
            // TODO: Add initialization for other systems as needed
        }

        /// <summary>
        /// Load the initial scene after boot sequence is complete
        /// </summary>
        private async UniTask LoadInitialSceneAsync(CancellationToken cancellationToken)
        {
            // Determine which scene to load (could be Main, Login, etc.)
            string targetScene = _initialSceneName;
            
            // Load the scene
            bool success = await SceneManager.Instance.LoadSceneAsync(targetScene, showLoadingScreen: false, cancellationToken: cancellationToken);
            
            if (!success)
            {
                Debug.LogError($"Failed to load initial scene: {targetScene}");
                // TODO: Show error UI to the user
            }
        }
    }
} 