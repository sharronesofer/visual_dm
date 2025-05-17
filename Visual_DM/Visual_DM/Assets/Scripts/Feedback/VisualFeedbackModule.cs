using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Feedback
{
    public class VisualFeedbackModule : MonoBehaviour, IFeedbackModule
    {
        // Pool for particle effects
        private readonly List<GameObject> particlePool = new List<GameObject>();
        private int poolSize = 16;
        private int poolIndex = 0;

        // Camera reference for screen shake (runtime only)
        private Camera mainCamera;
        private float shakeDuration = 0f;
        private float shakeMagnitude = 0.1f;
        private Vector3 originalCamPos;

        private void Awake()
        {
            mainCamera = Camera.main;
            if (mainCamera != null)
                originalCamPos = mainCamera.transform.position;
            // Pre-instantiate pool objects
            for (int i = 0; i < poolSize; i++)
            {
                var go = new GameObject("FeedbackParticle");
                var sr = go.AddComponent<SpriteRenderer>();
                go.SetActive(false);
                particlePool.Add(go);
            }
        }

        private void Update()
        {
            if (shakeDuration > 0 && mainCamera != null)
            {
                mainCamera.transform.position = originalCamPos + (Vector3)Random.insideUnitCircle * shakeMagnitude;
                shakeDuration -= Time.deltaTime;
                if (shakeDuration <= 0)
                {
                    mainCamera.transform.position = originalCamPos;
                }
            }
        }

        public void TriggerFeedback(ActionType type, int importance, Vector2 position, FeedbackContext context = null)
        {
            var config = FeedbackManager.Instance?.config;
            // Respect visual enable/disable
            if (config != null && !config.VisualEnabled) return;
            // Particle effect
            SpawnParticle(type, importance, position, config);
            // Animation trigger (could be extended for character sprites)
            // Screen shake for high-importance actions
            if (importance >= 7 && (config == null || config.AllowScreenShake))
            {
                StartScreenShake(importance, config);
            }
        }

        private void SpawnParticle(ActionType type, int importance, Vector2 position, FeedbackConfig config)
        {
            var go = particlePool[poolIndex];
            poolIndex = (poolIndex + 1) % poolSize;
            go.transform.position = position;
            var sr = go.GetComponent<SpriteRenderer>();
            sr.sprite = GetSpriteForAction(type);
            sr.color = GetColorForImportance(importance, config);
            go.SetActive(true);
            // Fade out after short duration, respect reduce motion/flashing
            float fadeDuration = (config != null && config.ReduceMotion) ? 0.2f : (0.5f + 0.1f * importance);
            go.GetComponent<MonoBehaviour>().StartCoroutine(FadeOut(go, fadeDuration, config));
        }

        private System.Collections.IEnumerator FadeOut(GameObject go, float duration, FeedbackConfig config)
        {
            var sr = go.GetComponent<SpriteRenderer>();
            float t = 0f;
            Color startColor = sr.color;
            float minAlpha = (config != null && config.ReduceFlashing) ? 0.5f : 0f;
            while (t < duration)
            {
                t += Time.deltaTime;
                float alpha = Mathf.Lerp(1f, minAlpha, t / duration);
                sr.color = new Color(startColor.r, startColor.g, startColor.b, alpha);
                yield return null;
            }
            go.SetActive(false);
        }

        private Sprite GetSpriteForAction(ActionType type)
        {
            // TODO: Replace with runtime-generated or loaded sprites per action type
            return null;
        }

        private Color GetColorForImportance(int importance, FeedbackConfig config)
        {
            float intensity = Mathf.Clamp01(importance / 10f);
            if (config != null && config.HighContrastMode)
                return Color.Lerp(Color.yellow, Color.black, intensity); // High contrast
            return Color.Lerp(Color.white, Color.red, intensity);
        }

        private void StartScreenShake(int importance, FeedbackConfig config)
        {
            if (config != null && !config.AllowScreenShake) return;
            shakeDuration = 0.1f + 0.05f * (importance - 6);
            shakeMagnitude = 0.1f + 0.05f * (importance - 6);
        }
    }
} 