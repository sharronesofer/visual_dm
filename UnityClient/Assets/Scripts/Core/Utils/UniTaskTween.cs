using System;
using System.Threading;
using Cysharp.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Core.Utils
{
    /// <summary>
    /// Provides utilities for creating awaitable tween animations using UniTask
    /// </summary>
    public static class UniTaskTween
    {
        /// <summary>
        /// Create a tween animation over a specified duration with progress reporting
        /// </summary>
        /// <param name="duration">Duration in seconds</param>
        /// <param name="onUpdate">Action called each frame with a normalized value (0-1)</param>
        /// <param name="easingFunc">Optional easing function</param>
        /// <param name="progress">Optional progress reporting</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>UniTask that completes when the tween animation is finished</returns>
        public static async UniTask TweenAsync(
            float duration, 
            Action<float> onUpdate, 
            Func<float, float> easingFunc = null, 
            IProgress<float> progress = null, 
            CancellationToken cancellationToken = default)
        {
            if (duration <= 0)
            {
                onUpdate?.Invoke(1.0f);
                progress?.Report(1.0f);
                return;
            }
            
            float startTime = Time.time;
            float endTime = startTime + duration;
            
            while (Time.time < endTime)
            {
                cancellationToken.ThrowIfCancellationRequested();
                
                float normalizedTime = Mathf.Clamp01((Time.time - startTime) / duration);
                float easedValue = easingFunc != null ? easingFunc(normalizedTime) : normalizedTime;
                
                onUpdate?.Invoke(easedValue);
                progress?.Report(normalizedTime);
                
                await UniTask.Yield(cancellationToken);
            }
            
            // Ensure final value is reached
            onUpdate?.Invoke(1.0f);
            progress?.Report(1.0f);
        }
        
        /// <summary>
        /// Create a tween animation that interpolates between two values
        /// </summary>
        /// <typeparam name="T">Type of value to interpolate</typeparam>
        /// <param name="duration">Duration in seconds</param>
        /// <param name="from">Starting value</param>
        /// <param name="to">Ending value</param>
        /// <param name="onUpdate">Action called each frame with the current value</param>
        /// <param name="lerpFunc">Function that performs the interpolation</param>
        /// <param name="easingFunc">Optional easing function</param>
        /// <param name="progress">Optional progress reporting</param>
        /// <param name="cancellationToken">Cancellation token</param>
        /// <returns>UniTask that completes when the tween animation is finished</returns>
        public static async UniTask TweenValueAsync<T>(
            float duration, 
            T from, 
            T to, 
            Action<T> onUpdate, 
            Func<T, T, float, T> lerpFunc, 
            Func<float, float> easingFunc = null, 
            IProgress<float> progress = null, 
            CancellationToken cancellationToken = default)
        {
            await TweenAsync(
                duration,
                normalizedValue => onUpdate?.Invoke(lerpFunc(from, to, easingFunc != null ? easingFunc(normalizedValue) : normalizedValue)),
                null,
                progress,
                cancellationToken
            );
        }
        
        #region Common Interpolation Functions
        
        /// <summary>
        /// Linear interpolation between float values
        /// </summary>
        public static float LerpFloat(float from, float to, float t) => Mathf.Lerp(from, to, t);
        
        /// <summary>
        /// Linear interpolation between Vector2 values
        /// </summary>
        public static Vector2 LerpVector2(Vector2 from, Vector2 to, float t) => Vector2.Lerp(from, to, t);
        
        /// <summary>
        /// Linear interpolation between Vector3 values
        /// </summary>
        public static Vector3 LerpVector3(Vector3 from, Vector3 to, float t) => Vector3.Lerp(from, to, t);
        
        /// <summary>
        /// Linear interpolation between Quaternion values (spherical)
        /// </summary>
        public static Quaternion LerpQuaternion(Quaternion from, Quaternion to, float t) => Quaternion.Slerp(from, to, t);
        
        /// <summary>
        /// Linear interpolation between Color values
        /// </summary>
        public static Color LerpColor(Color from, Color to, float t) => Color.Lerp(from, to, t);
        
        #endregion
        
        #region Common Easing Functions
        
        // Ease In
        public static float EaseInQuad(float t) => t * t;
        public static float EaseInCubic(float t) => t * t * t;
        public static float EaseInQuart(float t) => t * t * t * t;
        public static float EaseInQuint(float t) => t * t * t * t * t;
        public static float EaseInSine(float t) => 1 - Mathf.Cos(t * Mathf.PI / 2);
        public static float EaseInExpo(float t) => t == 0 ? 0 : Mathf.Pow(2, 10 * (t - 1));
        
        // Ease Out
        public static float EaseOutQuad(float t) => t * (2 - t);
        public static float EaseOutCubic(float t) => 1 - Mathf.Pow(1 - t, 3);
        public static float EaseOutQuart(float t) => 1 - Mathf.Pow(1 - t, 4);
        public static float EaseOutQuint(float t) => 1 - Mathf.Pow(1 - t, 5);
        public static float EaseOutSine(float t) => Mathf.Sin(t * Mathf.PI / 2);
        public static float EaseOutExpo(float t) => t == 1 ? 1 : 1 - Mathf.Pow(2, -10 * t);
        
        // Ease InOut
        public static float EaseInOutQuad(float t) => t < 0.5f ? 2 * t * t : -1 + (4 - 2 * t) * t;
        public static float EaseInOutCubic(float t) => t < 0.5f ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
        public static float EaseInOutQuart(float t) => t < 0.5f ? 8 * t * t * t * t : 1 - 8 * (--t) * t * t * t;
        public static float EaseInOutQuint(float t) => t < 0.5f ? 16 * t * t * t * t * t : 1 + 16 * (--t) * t * t * t * t;
        public static float EaseInOutSine(float t) => -0.5f * (Mathf.Cos(Mathf.PI * t) - 1);
        public static float EaseInOutExpo(float t)
        {
            if (t == 0 || t == 1) return t;
            if (t < 0.5f) return 0.5f * Mathf.Pow(2, 20 * t - 10);
            return 0.5f * (-Mathf.Pow(2, -20 * t + 10) + 2);
        }
        
        // Bounce
        public static float EaseOutBounce(float t)
        {
            if (t < 1 / 2.75f)
                return 7.5625f * t * t;
            else if (t < 2 / 2.75f)
                return 7.5625f * (t -= 1.5f / 2.75f) * t + 0.75f;
            else if (t < 2.5 / 2.75)
                return 7.5625f * (t -= 2.25f / 2.75f) * t + 0.9375f;
            else
                return 7.5625f * (t -= 2.625f / 2.75f) * t + 0.984375f;
        }
        
        public static float EaseInBounce(float t) => 1 - EaseOutBounce(1 - t);
        
        public static float EaseInOutBounce(float t)
        {
            if (t < 0.5f)
                return EaseInBounce(t * 2) * 0.5f;
            else
                return EaseOutBounce(t * 2 - 1) * 0.5f + 0.5f;
        }
        
        #endregion
        
        #region Common Tween Extensions
        
        /// <summary>
        /// Fade a CanvasGroup from current alpha to target alpha
        /// </summary>
        public static async UniTask FadeCanvasGroupAsync(
            UnityEngine.CanvasGroup canvasGroup, 
            float targetAlpha, 
            float duration, 
            Func<float, float> easingFunc = null, 
            IProgress<float> progress = null, 
            CancellationToken cancellationToken = default)
        {
            if (canvasGroup == null)
                return;
                
            float startAlpha = canvasGroup.alpha;
            await TweenValueAsync(
                duration,
                startAlpha,
                targetAlpha,
                alpha => canvasGroup.alpha = alpha,
                LerpFloat,
                easingFunc,
                progress,
                cancellationToken
            );
        }
        
        /// <summary>
        /// Move a transform from current position to target position
        /// </summary>
        public static async UniTask MoveTransformAsync(
            Transform transform, 
            Vector3 targetPosition, 
            float duration, 
            bool useLocal = false, 
            Func<float, float> easingFunc = null, 
            IProgress<float> progress = null, 
            CancellationToken cancellationToken = default)
        {
            if (transform == null)
                return;
                
            Vector3 startPosition = useLocal ? transform.localPosition : transform.position;
            await TweenValueAsync(
                duration,
                startPosition,
                targetPosition,
                position => {
                    if (useLocal)
                        transform.localPosition = position;
                    else
                        transform.position = position;
                },
                LerpVector3,
                easingFunc,
                progress,
                cancellationToken
            );
        }
        
        /// <summary>
        /// Rotate a transform from current rotation to target rotation
        /// </summary>
        public static async UniTask RotateTransformAsync(
            Transform transform, 
            Quaternion targetRotation, 
            float duration, 
            bool useLocal = false, 
            Func<float, float> easingFunc = null, 
            IProgress<float> progress = null, 
            CancellationToken cancellationToken = default)
        {
            if (transform == null)
                return;
                
            Quaternion startRotation = useLocal ? transform.localRotation : transform.rotation;
            await TweenValueAsync(
                duration,
                startRotation,
                targetRotation,
                rotation => {
                    if (useLocal)
                        transform.localRotation = rotation;
                    else
                        transform.rotation = rotation;
                },
                LerpQuaternion,
                easingFunc,
                progress,
                cancellationToken
            );
        }
        
        /// <summary>
        /// Scale a transform from current scale to target scale
        /// </summary>
        public static async UniTask ScaleTransformAsync(
            Transform transform, 
            Vector3 targetScale, 
            float duration, 
            Func<float, float> easingFunc = null, 
            IProgress<float> progress = null, 
            CancellationToken cancellationToken = default)
        {
            if (transform == null)
                return;
                
            Vector3 startScale = transform.localScale;
            await TweenValueAsync(
                duration,
                startScale,
                targetScale,
                scale => transform.localScale = scale,
                LerpVector3,
                easingFunc,
                progress,
                cancellationToken
            );
        }
        
        #endregion
    }
} 