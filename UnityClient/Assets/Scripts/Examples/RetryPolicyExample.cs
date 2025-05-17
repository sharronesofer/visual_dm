using System;
using System.Collections;
using System.Threading;
using System.Threading.Tasks;
using Core.Utils;
using Cysharp.Threading.Tasks;
using UnityEngine;
using UnityEngine.Networking;
using Random = UnityEngine.Random;

namespace Examples
{
    /// <summary>
    /// Example script showing how to use RetryPolicy in various scenarios.
    /// Attach this to a GameObject in your Unity scene.
    /// </summary>
    public class RetryPolicyExample : MonoBehaviour
    {
        [Header("Retry Configuration")]
        [SerializeField] private RetryOptions _retryOptions = new RetryOptions
        {
            MaxAttempts = 3,
            InitialDelayMs = 500,
            MaxDelayMs = 3000,
            Jitter = true
        };

        private Logger _logger;
        private RetryPolicy _retryPolicy;

        private void Awake()
        {
            _logger = new Logger("RetryExample");
            _retryPolicy = new RetryPolicy(_retryOptions, _logger);
        }

        private void Start()
        {
            // Run all examples
            RunSyncExample();
            RunAsyncExample().Forget();
            RunUniTaskExample().Forget();
            RunExtensionMethodsExample().Forget();
        }

        #region Synchronous Retry Example

        // Example 1: Synchronous retry with a custom policy
        private void RunSyncExample()
        {
            try
            {
                _logger.Info("Running synchronous retry example...");
                
                // Execute a function that might fail with built-in retry logic
                int result = _retryPolicy.Execute(SimulateUnreliableOperation);
                
                _logger.Info($"Sync operation succeeded after retries, result: {result}");
            }
            catch (Exception ex)
            {
                _logger.Error($"All retry attempts failed: {ex.Message}");
            }
        }

        // Simulation of an unreliable operation that sometimes fails
        private int SimulateUnreliableOperation()
        {
            float failChance = 0.7f;
            if (Random.value < failChance)
            {
                _logger.Warn("Operation failed, will retry...");
                throw new InvalidOperationException("Simulated transient failure");
            }
            
            return Random.Range(1, 100);
        }

        #endregion

        #region Async Task Retry Example

        // Example 2: Async retry with Task-based operations
        private async Task RunAsyncExample()
        {
            try
            {
                _logger.Info("Running async Task-based retry example...");
                
                // Create a cancellation token with a 10-second timeout
                using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
                
                // Execute an async operation with retry logic
                string result = await _retryPolicy.ExecuteAsync(
                    () => FetchDataAsync("https://jsonplaceholder.typicode.com/posts/1"),
                    cts.Token
                );
                
                _logger.Info($"Async operation succeeded: {result}");
            }
            catch (OperationCanceledException)
            {
                _logger.Error("Operation was cancelled due to timeout");
            }
            catch (Exception ex)
            {
                _logger.Error($"All retry attempts failed: {ex.Message}");
            }
        }

        // Simulated API call that might fail
        private async Task<string> FetchDataAsync(string url)
        {
            // Simulate random failures
            if (Random.value < 0.5f)
            {
                _logger.Warn("Network request failed, will retry...");
                throw new InvalidOperationException("Network error");
            }
            
            // Simple web request
            using var webRequest = UnityWebRequest.Get(url);
            await webRequest.SendWebRequest();
            
            if (webRequest.result != UnityWebRequest.Result.Success)
            {
                throw new InvalidOperationException($"Web request failed: {webRequest.error}");
            }
            
            return webRequest.downloadHandler.text;
        }

        #endregion

        #region UniTask Retry Example

        // Example 3: UniTask-based retry
        private async UniTask RunUniTaskExample()
        {
            try
            {
                _logger.Info("Running UniTask-based retry example...");
                
                // Pass a cancellation token that will cancel after 5 seconds
                var cts = new CancellationTokenSource();
                cts.CancelAfter(TimeSpan.FromSeconds(5));
                
                // Execute a UniTask operation with retry
                PlayerData playerData = await _retryPolicy.ExecuteUniTask(
                    () => LoadPlayerDataAsync(1234),
                    cts.Token
                );
                
                _logger.Info($"Player data loaded: {playerData}");
            }
            catch (OperationCanceledException)
            {
                _logger.Error("Operation was cancelled");
            }
            catch (Exception ex)
            {
                _logger.Error($"All retry attempts failed: {ex.Message}");
            }
        }

        // Simulated player data loading that might fail
        private async UniTask<PlayerData> LoadPlayerDataAsync(int playerId)
        {
            // Simulate processing time
            await UniTask.Delay(TimeSpan.FromMilliseconds(Random.Range(100, 300)));
            
            // Simulate random failures
            if (Random.value < 0.6f)
            {
                _logger.Warn("Failed to load player data, will retry...");
                throw new InvalidOperationException("Database connection error");
            }
            
            // Return mock player data
            return new PlayerData
            {
                Id = playerId,
                Name = "Player_" + playerId,
                Score = Random.Range(0, 1000)
            };
        }
        
        // Simple data class for the example
        public class PlayerData
        {
            public int Id { get; set; }
            public string Name { get; set; }
            public int Score { get; set; }
            
            public override string ToString()
            {
                return $"Player[{Id}] {Name} - Score: {Score}";
            }
        }

        #endregion

        #region Extension Methods Example

        // Example 4: Using extension methods for cleaner code
        private async UniTask RunExtensionMethodsExample()
        {
            _logger.Info("Running extension methods examples...");
            
            try
            {
                // Sync extension method
                int syncResult = GetRandomNumber.WithRetry(_retryOptions);
                _logger.Info($"Sync extension method result: {syncResult}");
                
                // Async Task extension method
                string taskResult = await GetMessageAsync.WithRetryAsync(_retryOptions);
                _logger.Info($"Task extension method result: {taskResult}");
                
                // UniTask extension method
                float unitaskResult = await CalculateDamageAsync.WithRetryUniTask(_retryOptions);
                _logger.Info($"UniTask extension method result: {unitaskResult}");
            }
            catch (Exception ex)
            {
                _logger.Error($"Extension method example failed: {ex.Message}");
            }
        }
        
        // Methods to demonstrate extension methods
        
        private int GetRandomNumber()
        {
            if (Random.value < 0.6f)
            {
                throw new InvalidOperationException("Random number generation failed");
            }
            return Random.Range(1, 100);
        }
        
        private async Task<string> GetMessageAsync()
        {
            await Task.Delay(100);
            if (Random.value < 0.6f)
            {
                throw new InvalidOperationException("Message retrieval failed");
            }
            return "Hello from Task-based operation!";
        }
        
        private async UniTask<float> CalculateDamageAsync()
        {
            await UniTask.Delay(150);
            if (Random.value < 0.6f)
            {
                throw new InvalidOperationException("Damage calculation failed");
            }
            return Random.Range(10f, 50f);
        }

        #endregion
    }
} 