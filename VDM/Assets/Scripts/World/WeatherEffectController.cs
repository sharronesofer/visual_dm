using System.Collections;
using UnityEngine;
using System.Collections.Generic;

namespace VisualDM.World
{
    public class WeatherEffectController : MonoBehaviour
    {
        public ParticleSystem rainEffect;
        public ParticleSystem snowEffect;
        public ParticleSystem fogEffect;
        public ParticleSystem windEffect;
        public ParticleSystem lightningEffect;
        public CanvasGroup weatherOverlay;
        public Color clearColor = new Color(1,1,1,0);
        public Color rainColor = new Color(0.7f,0.7f,1f,0.2f);
        public Color snowColor = new Color(0.9f,0.9f,1f,0.3f);
        public Color fogColor = new Color(0.8f,0.8f,0.8f,0.2f);
        public float fadeDuration = 1.0f;
        public Dictionary<string, Color> regionVisuals = new Dictionary<string, Color>();

        private string currentWeather = "Clear";
        private Coroutine transitionCoroutine;

        public void SetWeather(string weatherType, string regionId = null)
        {
            if (transitionCoroutine != null) StopCoroutine(transitionCoroutine);
            transitionCoroutine = StartCoroutine(TransitionWeather(weatherType, regionId));
        }

        IEnumerator TransitionWeather(string weatherType, string regionId = null)
        {
            // Fade out all effects
            if (rainEffect.isPlaying) rainEffect.Stop();
            if (snowEffect.isPlaying) snowEffect.Stop();
            if (fogEffect.isPlaying) fogEffect.Stop();
            if (windEffect != null && windEffect.isPlaying) windEffect.Stop();
            if (lightningEffect != null && lightningEffect.isPlaying) lightningEffect.Stop();
            Color targetColor = clearColor;
            switch (weatherType)
            {
                case "Rain":
                    rainEffect.Play();
                    targetColor = rainColor;
                    break;
                case "Snow":
                    snowEffect.Play();
                    targetColor = snowColor;
                    break;
                case "Fog":
                    fogEffect.Play();
                    targetColor = fogColor;
                    break;
                case "Wind":
                    if (windEffect != null) windEffect.Play();
                    break;
                case "Lightning":
                    if (lightningEffect != null) lightningEffect.Play();
                    break;
                default:
                    targetColor = clearColor;
                    break;
            }
            // Region-specific overlay
            if (!string.IsNullOrEmpty(regionId) && regionVisuals.ContainsKey(regionId))
                targetColor = regionVisuals[regionId];
            // Animate overlay color
            Color startColor = weatherOverlay != null ? weatherOverlay.GetComponent<UnityEngine.UI.Image>().color : clearColor;
            float t = 0f;
            while (t < 1f)
            {
                t += Time.deltaTime / fadeDuration;
                if (weatherOverlay != null)
                    weatherOverlay.GetComponent<UnityEngine.UI.Image>().color = Color.Lerp(startColor, targetColor, t);
                yield return null;
            }
            if (weatherOverlay != null)
                weatherOverlay.GetComponent<UnityEngine.UI.Image>().color = targetColor;
            currentWeather = weatherType;
        }
    }
} 