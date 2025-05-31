using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using UnityEngine;
using VDM.Systems.Chaos.Models;
using VDM.Systems.Chaos.Services;

namespace VDM.Systems.Chaos.Integration
{
    /// <summary>
    /// Handles chaos events and coordinates with existing Unity game systems
    /// Provides subtle player-facing effects without revealing chaos mechanics
    /// </summary>
    public class ChaosEventHandler : MonoBehaviour
    {
        [Header("Core References")]
        [SerializeField] private ChaosService chaosService;

        [Header("Environmental Effects")]
        [SerializeField] private GameObject weatherSystem;
        [SerializeField] private GameObject ambientAudioManager;
        [SerializeField] private GameObject lightingController;
        [SerializeField] private GameObject particleManager;

        [Header("UI Ambience")]
        [SerializeField] private CanvasGroup uiCanvasGroup;
        [SerializeField] private float ambientColorIntensity = 0.1f;
        [SerializeField] private float transitionDuration = 2.0f;

        [Header("Audio Configuration")]
        [SerializeField] private AudioClip[] chaosTensionTracks;
        [SerializeField] private AudioClip[] chaosAmbienceClips;
        [SerializeField] private AudioSource backgroundMusicSource;
        [SerializeField] private AudioSource ambienceSource;

        [Header("Effect Intensities")]
        [SerializeField] private AnimationCurve pressureToEffectCurve = AnimationCurve.Linear(0f, 0f, 1f, 1f);
        [SerializeField] private float maxEffectIntensity = 0.5f;
        [SerializeField] private float effectFadeTime = 5.0f;

        [Header("Debug Settings")]
        [SerializeField] private bool enableDebugLogs = false;
        [SerializeField] private bool enableVisualDebug = false;
        [SerializeField] private TextMesh debugDisplay;

        // Internal state
        private float currentChaosLevel = 0f;
        private float targetChaosLevel = 0f;
        private Dictionary<string, ChaosEventDTO> activeEvents = new Dictionary<string, ChaosEventDTO>();
        private Dictionary<string, float> systemPressures = new Dictionary<string, float>();
        private List<EnvironmentalEffect> activeEffects = new List<EnvironmentalEffect>();
        private bool isInitialized = false;

        // Effect coroutines
        private Coroutine ambientColorCoroutine;
        private Coroutine audioTransitionCoroutine;
        private Coroutine weatherCoroutine;

        // Environmental effect data
        private class EnvironmentalEffect
        {
            public string id;
            public string type;
            public float intensity;
            public float duration;
            public float timeRemaining;
            public bool isActive;
            public object effectData;
        }

        private void Start()
        {
            InitializeEventHandler();
        }

        private void Update()
        {
            if (isInitialized)
            {
                UpdateChaosEffects();
                UpdateActiveEffects();
                
                if (enableVisualDebug)
                    UpdateDebugDisplay();
            }
        }

        private void OnDestroy()
        {
            if (chaosService != null)
            {
                UnsubscribeFromChaosService();
            }
        }

        /// <summary>
        /// Initialize the chaos event handler
        /// </summary>
        private void InitializeEventHandler()
        {
            if (chaosService == null)
            {
                chaosService = FindObjectOfType<ChaosService>();
                if (chaosService == null)
                {
                    Debug.LogError("ChaosEventHandler: ChaosService not found");
                    return;
                }
            }

            // Subscribe to chaos service events
            SubscribeToChaosService();

            // Initialize effects systems
            InitializeEffectsSystems();

            isInitialized = true;
            DebugLog("ChaosEventHandler initialized successfully");
        }

        /// <summary>
        /// Subscribe to chaos service events
        /// </summary>
        private void SubscribeToChaosService()
        {
            chaosService.OnChaosEventTriggered += HandleChaosEvent;
            chaosService.OnMetricsUpdated += HandleMetricsUpdate;
            chaosService.OnPressureUpdated += HandlePressureUpdate;
            chaosService.OnConnectionStatusChanged += HandleConnectionStatusChanged;
        }

        /// <summary>
        /// Unsubscribe from chaos service events
        /// </summary>
        private void UnsubscribeFromChaosService()
        {
            chaosService.OnChaosEventTriggered -= HandleChaosEvent;
            chaosService.OnMetricsUpdated -= HandleMetricsUpdate;
            chaosService.OnPressureUpdated -= HandlePressureUpdate;
            chaosService.OnConnectionStatusChanged -= HandleConnectionStatusChanged;
        }

        /// <summary>
        /// Initialize effects systems
        /// </summary>
        private void InitializeEffectsSystems()
        {
            // Initialize audio sources if not assigned
            if (backgroundMusicSource == null)
                backgroundMusicSource = GetComponent<AudioSource>();

            if (ambienceSource == null && backgroundMusicSource != null)
            {
                ambienceSource = gameObject.AddComponent<AudioSource>();
                ambienceSource.loop = true;
                ambienceSource.volume = 0.3f;
            }

            // Find UI canvas if not assigned
            if (uiCanvasGroup == null)
                uiCanvasGroup = FindObjectOfType<CanvasGroup>();

            // Initialize default effect curve if needed
            if (pressureToEffectCurve.keys.Length == 0)
                pressureToEffectCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);
        }

        // Event Handlers

        /// <summary>
        /// Handle incoming chaos events
        /// </summary>
        private void HandleChaosEvent(ChaosEventDTO chaosEvent)
        {
            DebugLog($"Chaos event received: {chaosEvent.EventType} (Intensity: {chaosEvent.Intensity})");

            // Store active event
            activeEvents[chaosEvent.Id] = chaosEvent;

            // Process event based on type
            ProcessChaosEvent(chaosEvent);

            // Update target chaos level
            UpdateTargetChaosLevel();
        }

        /// <summary>
        /// Handle metrics updates
        /// </summary>
        private void HandleMetricsUpdate(ChaosMetricsDTO metrics)
        {
            targetChaosLevel = metrics.GlobalChaosLevel / 100f;
            
            // Update system pressures
            foreach (var pressure in metrics.SystemPressures)
            {
                systemPressures[pressure.Key] = pressure.Value;
            }

            DebugLog($"Metrics updated - Global Chaos: {metrics.GlobalChaosLevel:F1}%");
        }

        /// <summary>
        /// Handle pressure updates
        /// </summary>
        private void HandlePressureUpdate(PressureSourceDTO pressure)
        {
            systemPressures[pressure.SystemName] = pressure.CurrentPressure / pressure.MaxPressure;
            DebugLog($"Pressure updated - {pressure.SystemName}: {pressure.CurrentPressure:F1}/{pressure.MaxPressure:F1}");
        }

        /// <summary>
        /// Handle connection status changes
        /// </summary>
        private void HandleConnectionStatusChanged(bool connected)
        {
            if (!connected)
            {
                // Gradually fade effects when disconnected
                StartCoroutine(FadeAllEffects());
            }
            
            DebugLog($"Chaos service connection: {(connected ? "Connected" : "Disconnected")}");
        }

        // Event Processing

        /// <summary>
        /// Process specific chaos event types
        /// </summary>
        private void ProcessChaosEvent(ChaosEventDTO chaosEvent)
        {
            switch (chaosEvent.EventType.ToLower())
            {
                case "political upheaval":
                    ProcessPoliticalUpheaval(chaosEvent);
                    break;
                case "natural disaster":
                    ProcessNaturalDisaster(chaosEvent);
                    break;
                case "economic collapse":
                    ProcessEconomicCollapse(chaosEvent);
                    break;
                case "war outbreak":
                    ProcessWarOutbreak(chaosEvent);
                    break;
                case "resource scarcity":
                    ProcessResourceScarcity(chaosEvent);
                    break;
                case "faction betrayal":
                    ProcessFactionBetrayal(chaosEvent);
                    break;
                case "character revelation":
                    ProcessCharacterRevelation(chaosEvent);
                    break;
                default:
                    ProcessGenericChaosEvent(chaosEvent);
                    break;
            }
        }

        /// <summary>
        /// Process political upheaval events
        /// </summary>
        private void ProcessPoliticalUpheaval(ChaosEventDTO chaosEvent)
        {
            // Create subtle tension effects
            CreateEnvironmentalEffect("political_tension", chaosEvent.Intensity * 0.7f, 30f, new
            {
                audioIntensity = 0.6f,
                lightingShift = new Vector3(0.8f, 0.7f, 0.9f), // Slightly red/purple tint
                particleEffect = "political_unrest"
            });

            TriggerAudioEffect(chaosTensionTracks, chaosEvent.Intensity * 0.5f);
        }

        /// <summary>
        /// Process natural disaster events
        /// </summary>
        private void ProcessNaturalDisaster(ChaosEventDTO chaosEvent)
        {
            // Create weather and environmental effects
            CreateEnvironmentalEffect("natural_disaster", chaosEvent.Intensity, 45f, new
            {
                weatherType = "storm",
                windIntensity = chaosEvent.Intensity * 0.8f,
                lightingFlicker = true,
                particleEffect = "storm_particles"
            });

            TriggerWeatherEffect("stormy", chaosEvent.Intensity);
        }

        /// <summary>
        /// Process economic collapse events
        /// </summary>
        private void ProcessEconomicCollapse(ChaosEventDTO chaosEvent)
        {
            // Create scarcity atmosphere
            CreateEnvironmentalEffect("economic_crisis", chaosEvent.Intensity * 0.6f, 60f, new
            {
                lightingDim = chaosEvent.Intensity * 0.3f,
                colorDesaturation = chaosEvent.Intensity * 0.4f,
                audioTension = 0.4f
            });
        }

        /// <summary>
        /// Process war outbreak events
        /// </summary>
        private void ProcessWarOutbreak(ChaosEventDTO chaosEvent)
        {
            // Create conflict atmosphere
            CreateEnvironmentalEffect("war_tension", chaosEvent.Intensity * 0.9f, 90f, new
            {
                audioIntensity = 0.8f,
                lightingShift = new Vector3(1.0f, 0.6f, 0.6f), // Red tint
                particleEffect = "conflict_smoke",
                uiTension = chaosEvent.Intensity * 0.5f
            });

            TriggerAudioEffect(chaosTensionTracks, chaosEvent.Intensity * 0.7f);
        }

        /// <summary>
        /// Process resource scarcity events
        /// </summary>
        private void ProcessResourceScarcity(ChaosEventDTO chaosEvent)
        {
            // Create scarcity effects
            CreateEnvironmentalEffect("resource_scarcity", chaosEvent.Intensity * 0.5f, 120f, new
            {
                lightingDim = chaosEvent.Intensity * 0.4f,
                audioFade = chaosEvent.Intensity * 0.3f,
                environmentalDecay = true
            });
        }

        /// <summary>
        /// Process faction betrayal events
        /// </summary>
        private void ProcessFactionBetrayal(ChaosEventDTO chaosEvent)
        {
            // Create subtle betrayal atmosphere
            CreateEnvironmentalEffect("betrayal_tension", chaosEvent.Intensity * 0.6f, 40f, new
            {
                lightingShift = new Vector3(0.9f, 0.8f, 1.1f), // Slight blue-white shift
                audioTension = 0.5f,
                uiSubtleShift = true
            });
        }

        /// <summary>
        /// Process character revelation events
        /// </summary>
        private void ProcessCharacterRevelation(ChaosEventDTO chaosEvent)
        {
            // Create mysterious atmosphere
            CreateEnvironmentalEffect("revelation_mystery", chaosEvent.Intensity * 0.4f, 20f, new
            {
                lightingFlicker = true,
                audioMystery = 0.6f,
                particleEffect = "mystery_motes"
            });
        }

        /// <summary>
        /// Process generic chaos events
        /// </summary>
        private void ProcessGenericChaosEvent(ChaosEventDTO chaosEvent)
        {
            // Generic chaos atmosphere
            CreateEnvironmentalEffect("generic_chaos", chaosEvent.Intensity * 0.5f, 30f, new
            {
                generalTension = chaosEvent.Intensity * 0.3f
            });
        }

        // Effect Management

        /// <summary>
        /// Create and manage environmental effects
        /// </summary>
        private void CreateEnvironmentalEffect(string effectType, float intensity, float duration, object effectData)
        {
            var effect = new EnvironmentalEffect
            {
                id = Guid.NewGuid().ToString(),
                type = effectType,
                intensity = Mathf.Clamp01(intensity),
                duration = duration,
                timeRemaining = duration,
                isActive = true,
                effectData = effectData
            };

            activeEffects.Add(effect);
            ApplyEnvironmentalEffect(effect);
            
            DebugLog($"Created environmental effect: {effectType} (Intensity: {intensity:F2}, Duration: {duration}s)");
        }

        /// <summary>
        /// Apply environmental effect to game systems
        /// </summary>
        private void ApplyEnvironmentalEffect(EnvironmentalEffect effect)
        {
            var effectIntensity = pressureToEffectCurve.Evaluate(effect.intensity) * maxEffectIntensity;

            // Apply lighting effects
            ApplyLightingEffect(effect, effectIntensity);

            // Apply audio effects
            ApplyAudioEffect(effect, effectIntensity);

            // Apply UI ambience
            ApplyUIAmbienceEffect(effect, effectIntensity);

            // Apply particle effects
            ApplyParticleEffect(effect, effectIntensity);

            // Apply weather effects
            ApplyWeatherEffect(effect, effectIntensity);
        }

        /// <summary>
        /// Apply lighting effects
        /// </summary>
        private void ApplyLightingEffect(EnvironmentalEffect effect, float intensity)
        {
            if (lightingController == null) return;

            // This would interact with your lighting system
            // Implementation depends on your lighting architecture
            DebugLog($"Applying lighting effect: {effect.type} (Intensity: {intensity:F2})");
        }

        /// <summary>
        /// Apply audio effects
        /// </summary>
        private void ApplyAudioEffect(EnvironmentalEffect effect, float intensity)
        {
            if (backgroundMusicSource == null) return;

            // Adjust background music volume and pitch based on chaos
            var volumeMultiplier = 1f - (intensity * 0.3f);
            var pitchShift = 1f - (intensity * 0.1f);

            if (audioTransitionCoroutine != null)
                StopCoroutine(audioTransitionCoroutine);

            audioTransitionCoroutine = StartCoroutine(TransitionAudio(volumeMultiplier, pitchShift));
        }

        /// <summary>
        /// Apply UI ambience effects
        /// </summary>
        private void ApplyUIAmbienceEffect(EnvironmentalEffect effect, float intensity)
        {
            if (uiCanvasGroup == null) return;

            // Subtle UI color shifts and opacity changes
            var targetAlpha = 1f - (intensity * ambientColorIntensity);

            if (ambientColorCoroutine != null)
                StopCoroutine(ambientColorCoroutine);

            ambientColorCoroutine = StartCoroutine(TransitionUIAmbience(targetAlpha));
        }

        /// <summary>
        /// Apply particle effects
        /// </summary>
        private void ApplyParticleEffect(EnvironmentalEffect effect, float intensity)
        {
            if (particleManager == null) return;

            // This would trigger particle systems based on effect type
            DebugLog($"Applying particle effect: {effect.type} (Intensity: {intensity:F2})");
        }

        /// <summary>
        /// Apply weather effects
        /// </summary>
        private void ApplyWeatherEffect(EnvironmentalEffect effect, float intensity)
        {
            if (weatherSystem == null) return;

            // This would interact with your weather system
            DebugLog($"Applying weather effect: {effect.type} (Intensity: {intensity:F2})");
        }

        /// <summary>
        /// Trigger specific audio effects
        /// </summary>
        private void TriggerAudioEffect(AudioClip[] clips, float intensity)
        {
            if (clips == null || clips.Length == 0 || ambienceSource == null) return;

            var randomClip = clips[UnityEngine.Random.Range(0, clips.Length)];
            ambienceSource.clip = randomClip;
            ambienceSource.volume = intensity * 0.5f;
            ambienceSource.Play();
        }

        /// <summary>
        /// Trigger weather effects
        /// </summary>
        private void TriggerWeatherEffect(string weatherType, float intensity)
        {
            if (weatherCoroutine != null)
                StopCoroutine(weatherCoroutine);

            weatherCoroutine = StartCoroutine(TransitionWeather(weatherType, intensity));
        }

        // Update Methods

        /// <summary>
        /// Update chaos effects over time
        /// </summary>
        private void UpdateChaosEffects()
        {
            // Smoothly transition current chaos level toward target
            currentChaosLevel = Mathf.Lerp(currentChaosLevel, targetChaosLevel, Time.deltaTime / transitionDuration);

            // Apply global chaos effects
            ApplyGlobalChaosEffects(currentChaosLevel);
        }

        /// <summary>
        /// Update active environmental effects
        /// </summary>
        private void UpdateActiveEffects()
        {
            for (int i = activeEffects.Count - 1; i >= 0; i--)
            {
                var effect = activeEffects[i];
                effect.timeRemaining -= Time.deltaTime;

                if (effect.timeRemaining <= 0f)
                {
                    // Effect has expired
                    activeEffects.RemoveAt(i);
                    DebugLog($"Environmental effect expired: {effect.type}");
                }
                else
                {
                    // Update effect intensity based on remaining time
                    var timeProgress = 1f - (effect.timeRemaining / effect.duration);
                    var fadeMultiplier = timeProgress < 0.8f ? 1f : (1f - timeProgress) * 5f; // Fade out in last 20%
                    
                    var adjustedEffect = new EnvironmentalEffect
                    {
                        id = effect.id,
                        type = effect.type,
                        intensity = effect.intensity * fadeMultiplier,
                        duration = effect.duration,
                        timeRemaining = effect.timeRemaining,
                        isActive = effect.isActive,
                        effectData = effect.effectData
                    };

                    ApplyEnvironmentalEffect(adjustedEffect);
                }
            }
        }

        /// <summary>
        /// Apply global chaos effects
        /// </summary>
        private void ApplyGlobalChaosEffects(float chaosLevel)
        {
            // Subtle global effects that scale with overall chaos
            var effectIntensity = pressureToEffectCurve.Evaluate(chaosLevel) * maxEffectIntensity * 0.3f;

            // Global audio adjustment
            if (backgroundMusicSource != null)
            {
                var targetVolume = 1f - (effectIntensity * 0.2f);
                backgroundMusicSource.volume = Mathf.Lerp(backgroundMusicSource.volume, targetVolume, Time.deltaTime);
            }
        }

        /// <summary>
        /// Update target chaos level based on active events and pressures
        /// </summary>
        private void UpdateTargetChaosLevel()
        {
            float totalIntensity = 0f;
            int eventCount = 0;

            // Calculate intensity from active events
            foreach (var activeEvent in activeEvents.Values)
            {
                if (activeEvent.Status == ChaosEventStatus.Active || activeEvent.Status == ChaosEventStatus.Escalating)
                {
                    totalIntensity += activeEvent.Intensity;
                    eventCount++;
                }
            }

            // Calculate average system pressure
            float averagePressure = 0f;
            if (systemPressures.Count > 0)
            {
                foreach (var pressure in systemPressures.Values)
                {
                    averagePressure += pressure;
                }
                averagePressure /= systemPressures.Count;
            }

            // Combine event intensity and system pressure
            targetChaosLevel = Mathf.Clamp01((totalIntensity / Mathf.Max(1f, eventCount)) * 0.5f + averagePressure * 0.5f);
        }

        // Coroutines

        /// <summary>
        /// Transition audio properties
        /// </summary>
        private System.Collections.IEnumerator TransitionAudio(float targetVolume, float targetPitch)
        {
            if (backgroundMusicSource == null) yield break;

            var startVolume = backgroundMusicSource.volume;
            var startPitch = backgroundMusicSource.pitch;
            var elapsed = 0f;

            while (elapsed < transitionDuration)
            {
                elapsed += Time.deltaTime;
                var progress = elapsed / transitionDuration;

                backgroundMusicSource.volume = Mathf.Lerp(startVolume, targetVolume, progress);
                backgroundMusicSource.pitch = Mathf.Lerp(startPitch, targetPitch, progress);

                yield return null;
            }

            backgroundMusicSource.volume = targetVolume;
            backgroundMusicSource.pitch = targetPitch;
        }

        /// <summary>
        /// Transition UI ambience
        /// </summary>
        private System.Collections.IEnumerator TransitionUIAmbience(float targetAlpha)
        {
            if (uiCanvasGroup == null) yield break;

            var startAlpha = uiCanvasGroup.alpha;
            var elapsed = 0f;

            while (elapsed < transitionDuration)
            {
                elapsed += Time.deltaTime;
                var progress = elapsed / transitionDuration;

                uiCanvasGroup.alpha = Mathf.Lerp(startAlpha, targetAlpha, progress);

                yield return null;
            }

            uiCanvasGroup.alpha = targetAlpha;
        }

        /// <summary>
        /// Transition weather effects
        /// </summary>
        private System.Collections.IEnumerator TransitionWeather(string weatherType, float intensity)
        {
            // This would transition weather based on your weather system
            DebugLog($"Transitioning weather to: {weatherType} (Intensity: {intensity:F2})");
            yield return new WaitForSeconds(2f);
        }

        /// <summary>
        /// Fade all effects when disconnected
        /// </summary>
        private System.Collections.IEnumerator FadeAllEffects()
        {
            var fadeTime = effectFadeTime;
            var elapsed = 0f;

            while (elapsed < fadeTime)
            {
                elapsed += Time.deltaTime;
                var fadeMultiplier = 1f - (elapsed / fadeTime);

                // Apply fade to all active effects
                foreach (var effect in activeEffects)
                {
                    var fadedEffect = new EnvironmentalEffect
                    {
                        id = effect.id,
                        type = effect.type,
                        intensity = effect.intensity * fadeMultiplier,
                        duration = effect.duration,
                        timeRemaining = effect.timeRemaining,
                        isActive = effect.isActive,
                        effectData = effect.effectData
                    };

                    ApplyEnvironmentalEffect(fadedEffect);
                }

                yield return null;
            }

            // Clear all effects
            activeEffects.Clear();
            activeEvents.Clear();
            targetChaosLevel = 0f;
        }

        // Debug and Utility

        /// <summary>
        /// Update debug display
        /// </summary>
        private void UpdateDebugDisplay()
        {
            if (debugDisplay == null) return;

            var debugText = $"Chaos Level: {currentChaosLevel:F2}\n";
            debugText += $"Target: {targetChaosLevel:F2}\n";
            debugText += $"Active Events: {activeEvents.Count}\n";
            debugText += $"Active Effects: {activeEffects.Count}\n";
            debugText += $"System Pressures: {systemPressures.Count}";

            debugDisplay.text = debugText;
        }

        /// <summary>
        /// Debug logging
        /// </summary>
        private void DebugLog(string message)
        {
            if (enableDebugLogs)
                Debug.Log($"ChaosEventHandler: {message}");
        }

        // Public Properties and Methods

        public float CurrentChaosLevel => currentChaosLevel;
        public int ActiveEventCount => activeEvents.Count;
        public int ActiveEffectCount => activeEffects.Count;
        public bool IsInitialized => isInitialized;

        /// <summary>
        /// Manually trigger chaos effect for testing
        /// </summary>
        public void TriggerTestEffect(string effectType, float intensity, float duration)
        {
            CreateEnvironmentalEffect(effectType, intensity, duration, new { test = true });
        }

        /// <summary>
        /// Clear all active effects
        /// </summary>
        public void ClearAllEffects()
        {
            activeEffects.Clear();
            activeEvents.Clear();
            targetChaosLevel = 0f;
            currentChaosLevel = 0f;
        }
    }
} 