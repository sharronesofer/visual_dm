using System;
using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.Core;
using VisualDM.Core.Utils;

namespace VisualDM.Examples
{
    /// <summary>
    /// Example class demonstrating UniTask utilities
    /// </summary>
    public class UniTaskExample : MonoBehaviour
    {
        [SerializeField] private Button _timeoutButton;
        [SerializeField] private Button _retryButton;
        [SerializeField] private Button _progressButton;
        [SerializeField] private Button _tweenButton;
        [SerializeField] private Slider _progressSlider;
        [SerializeField] private Text _statusText;
        [SerializeField] private CanvasGroup _canvasGroup;
        [SerializeField] private Transform _cubeTransform;
        
        private CancellationTokenSource _cts;
        
        private void Awake()
        {
            _cts = new CancellationTokenSource();
            
            if (_timeoutButton != null)
                _timeoutButton.onClick.AddListener(() => TimeoutExampleAsync().Forget());
            
            if (_retryButton != null)
                _retryButton.onClick.AddListener(() => RetryExampleAsync().Forget());
            
            if (_progressButton != null)
                _progressButton.onClick.AddListener(() => ProgressExampleAsync().Forget());
            
            if (_tweenButton != null)
                _tweenButton.onClick.AddListener(() => TweenExampleAsync().Forget());
        }
        
        private void OnDestroy()
        {
            _cts.Cancel();
            _cts.Dispose();
        }
        
        /// <summary>
        /// Example of using timeout utilities
        /// </summary>
        private async UniTaskAsync TimeoutExampleAsync()
        {
            SetStatus("Starting timeout example...");
            
            try
            {
                // Example with timeout that throws an exception
                await SimulateLongOperationAsync(5f)
                    .WithTimeout(TimeSpan.FromSeconds(2f), _cts.Token);
                
                SetStatus("Operation completed successfully");
            }
            catch (TimeoutException)
            {
                SetStatus("Operation timed out!");
                
                // Example with timeout returning a default value
                bool result = await SimulateLongOperationWithResultAsync<bool>(5f)
                    .WithTimeoutOrDefault(TimeSpan.FromSeconds(2f), false, _cts.Token);
                
                SetStatus($"Operation with default returned: {result}");
            }
            catch (OperationCanceledException)
            {
                SetStatus("Operation was canceled");
            }
            catch (Exception ex)
            {
                SetStatus($"Error: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Example of using retry utilities
        /// </summary>
        private async UniTaskAsync RetryExampleAsync()
        {
            SetStatus("Starting retry example...");
            
            try
            {
                int result = await UniTaskUtils.WithRetry(
                    async (ct) =>
                    {
                        SetStatus("Attempt in progress...");
                        return await SimulateFailingOperationAsync(ct);
                    },
                    maxRetries: 3,
                    initialDelay: TimeSpan.FromSeconds(1),
                    retryPredicate: (ex, attempt) => ex is InvalidOperationException,
                    cancellationToken: _cts.Token
                );
                
                SetStatus($"Operation succeeded with result: {result}");
            }
            catch (Exception ex)
            {
                SetStatus($"All retries failed: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Example of using progress reporting
        /// </summary>
        private async UniTaskAsync ProgressExampleAsync()
        {
            SetStatus("Starting progress example...");
            
            // Setup progress reporting
            var progress = new UniTaskProgress(
                progressAction: value => {
                    if (_progressSlider != null)
                        _progressSlider.value = value;
                },
                messageAction: message => {
                    SetStatus(message);
                }
            );
            
            // Create child progress objects
            var child1 = progress.CreateChild(0.5f, 0);        // First half
            var child2 = progress.CreateChild(0.5f, 0.5f);     // Second half
            
            try
            {
                // First operation uses first half of the progress bar
                progress.ReportMessage("Starting first operation...");
                await SimulateProgressOperationAsync(3f, child1, _cts.Token);
                
                // Second operation uses second half of the progress bar
                progress.ReportMessage("Starting second operation...");
                await SimulateProgressOperationAsync(2f, child2, _cts.Token);
                
                progress.ReportMessage("All operations completed!");
            }
            catch (OperationCanceledException)
            {
                progress.ReportMessage("Operation was canceled");
            }
            catch (Exception ex)
            {
                progress.ReportMessage($"Error: {ex.Message}");
            }
        }
        
        /// <summary>
        /// Example of using tween utilities
        /// </summary>
        private async UniTaskAsync TweenExampleAsync()
        {
            SetStatus("Starting tween example...");
            
            try
            {
                // Fade canvas group
                if (_canvasGroup != null)
                {
                    SetStatus("Fading canvas group...");
                    await UniTaskTween.FadeCanvasGroupAsync(
                        _canvasGroup,
                        0.2f,
                        1.0f,
                        UniTaskTween.EaseInOutQuad,
                        null,
                        _cts.Token
                    );
                    
                    await UniTask.Delay(500, cancellationToken: _cts.Token);
                    
                    await UniTaskTween.FadeCanvasGroupAsync(
                        _canvasGroup,
                        1.0f,
                        1.0f,
                        UniTaskTween.EaseInOutQuad,
                        null,
                        _cts.Token
                    );
                }
                
                // Move, rotate and scale a transform
                if (_cubeTransform != null)
                {
                    SetStatus("Moving cube...");
                    await UniTaskTween.MoveTransformAsync(
                        _cubeTransform,
                        _cubeTransform.position + Vector3.up * 2f,
                        1.0f,
                        false,
                        UniTaskTween.EaseOutBounce,
                        null,
                        _cts.Token
                    );
                    
                    SetStatus("Rotating cube...");
                    await UniTaskTween.RotateTransformAsync(
                        _cubeTransform,
                        Quaternion.Euler(0, 180, 0),
                        1.0f,
                        false,
                        UniTaskTween.EaseInOutCubic,
                        null,
                        _cts.Token
                    );
                    
                    SetStatus("Scaling cube...");
                    await UniTaskTween.ScaleTransformAsync(
                        _cubeTransform,
                        _cubeTransform.localScale * 1.5f,
                        1.0f,
                        UniTaskTween.EaseOutElastic,
                        null,
                        _cts.Token
                    );
                    
                    await UniTask.Delay(500, cancellationToken: _cts.Token);
                    
                    // Reset cube
                    await UniTaskTween.ScaleTransformAsync(
                        _cubeTransform,
                        Vector3.one,
                        1.0f,
                        UniTaskTween.EaseInOutQuad,
                        null,
                        _cts.Token
                    );
                }
                
                SetStatus("Tween example completed!");
            }
            catch (OperationCanceledException)
            {
                SetStatus("Tweens were canceled");
            }
            catch (Exception ex)
            {
                SetStatus($"Error: {ex.Message}");
            }
        }
        
        #region Helper Methods
        
        private void SetStatus(string message)
        {
            Debug.Log(message);
            if (_statusText != null)
                _statusText.text = message;
        }
        
        private async UniTask SimulateLongOperationAsync(float seconds)
        {
            await UniTask.Delay(TimeSpan.FromSeconds(seconds), cancellationToken: _cts.Token);
        }
        
        private async UniTask<T> SimulateLongOperationWithResultAsync<T>(float seconds)
        {
            await UniTask.Delay(TimeSpan.FromSeconds(seconds), cancellationToken: _cts.Token);
            return default;
        }
        
        private async UniTask<int> SimulateFailingOperationAsync(CancellationToken cancellationToken)
        {
            await UniTask.Delay(TimeSpan.FromSeconds(0.5f), cancellationToken: cancellationToken);
            
            // Simulate random failure
            if (UnityEngine.Random.value < 0.7f)
            {
                throw new InvalidOperationException("Operation failed (simulated)");
            }
            
            return UnityEngine.Random.Range(1, 100);
        }
        
        private async UniTask SimulateProgressOperationAsync(float seconds, IProgress<float> progress, CancellationToken cancellationToken)
        {
            float startTime = Time.time;
            float endTime = startTime + seconds;
            
            while (Time.time < endTime)
            {
                cancellationToken.ThrowIfCancellationRequested();
                
                float normalizedProgress = Mathf.Clamp01((Time.time - startTime) / seconds);
                progress?.Report(normalizedProgress);
                
                await UniTask.Yield(cancellationToken);
            }
            
            progress?.Report(1.0f);
        }
        
        #endregion
        
        #region Custom Easing Functions
        
        // Additional easing function for the example
        private static float EaseOutElastic(float t)
        {
            float p = 0.3f;
            return Mathf.Pow(2f, -10f * t) * Mathf.Sin((t - p / 4f) * (2f * Mathf.PI) / p) + 1f;
        }
        
        #endregion
    }
} 