using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.CombatSystem;
using VisualDM.Systems.EventSystem;

namespace VisualDM.UI
{
    public enum ActionType
    {
        AttackLight,
        AttackHeavy,
        Spell,
        UI,
        ChainAction,
        // Add more as needed
        SocialCheckSuccess,
        SocialCheckFailure,
        TrustChanged,
        FactionSchism,
        FactionSwitch,
        FactionRelationshipChanged
    }

    public class SystemsContext
    {
        // Extend with additional context data as needed
        public string ExtraInfo;
    }

    public interface ISystemsModule
    {
        void TriggerSystems(ActionType type, int importance, Vector2 position, SystemsContext context = null);
    }

    public class SystemsEvent
    {
        public ActionType Type;
        public int Importance;
        public Vector2 Position;
        public SystemsContext Context;
        public float Timestamp;
    }

    public class VariationSystem
    {
        private readonly System.Random random = new System.Random();
        private float lastSystemsTime = 0f;
        private float minInterval = 0.03f; // Minimum interval between feedback events (seconds)
        private int overloadThreshold = 12; // Max feedback events per frame
        private int feedbacksThisFrame = 0;
        private int lastFrame = -1;

        // Context-aware importance scaling
        public int AdjustImportance(ActionType type, int baseImportance, SystemsContext context)
        {
            int importance = baseImportance;
            // Example: context-based scaling (extend as needed)
            if (context != null && !string.IsNullOrEmpty(context.ExtraInfo))
            {
                if (context.ExtraInfo.Contains("Critical"))
                    importance = Mathf.Clamp(baseImportance + 2, 1, 10);
                if (context.ExtraInfo.Contains("Low"))
                    importance = Mathf.Clamp(baseImportance - 1, 1, 10);
            }
            // Add randomization within +/-1 for unpredictability
            importance += random.Next(-1, 2);
            importance = Mathf.Clamp(importance, 1, 10);
            return importance;
        }

        // Throttling/overload protection
        public bool ShouldSuppressSystems()
        {
            int currentFrame = Time.frameCount;
            if (currentFrame != lastFrame)
            {
                feedbacksThisFrame = 0;
                lastFrame = currentFrame;
            }
            feedbacksThisFrame++;
            if (feedbacksThisFrame > overloadThreshold)
                return true;
            // Also throttle if feedbacks are too close in time
            if (Time.time - lastSystemsTime < minInterval)
                return true;
            lastSystemsTime = Time.time;
            return false;
        }
    }

    [CreateAssetMenu(fileName = "SystemsConfig", menuName = "VisualDM/SystemsConfig", order = 1)]
    public class SystemsConfig : ScriptableObject
    {
        [Serializable]
        public class SystemsTypeSettings
        {
            public ActionType Type;
            public bool Enabled = true;
            [Range(0.1f, 2f)] public float IntensityScale = 1f;
        }
        public List<SystemsTypeSettings> TypeSettings = new();
        public bool VisualEnabled = true;
        public bool AudioEnabled = true;
        public bool HapticEnabled = true;
        public bool HighContrastMode = false;
        public bool ReduceMotion = false;
        public bool ReduceFlashing = false;
        public bool AllowScreenShake = true;
        public bool AllowVibration = true;
        public bool AllowLoudSounds = true;
    }

    public class SystemsManager : MonoBehaviour
    {
        public static SystemsManager Instance { get; private set; }

        [Header("Systems Configuration")]
        public SystemsConfig config;

        // Configurable cap for simultaneous feedback events
        [SerializeField] private int maxSimultaneousSystems = 8;

        // Module references (to be assigned at runtime)
        public ISystemsModule VisualModule { get; set; }
        public ISystemsModule AudioModule { get; set; }
        public ISystemsModule HapticModule { get; set; }

        // Importance mapping (can be loaded from config)
        private readonly Dictionary<ActionType, int> defaultImportance = new Dictionary<ActionType, int>
        {
            { ActionType.AttackLight, 3 },
            { ActionType.AttackHeavy, 7 },
            { ActionType.Spell, 6 },
            { ActionType.UI, 2 },
        };

        // Systems event queue
        private readonly Queue<SystemsEvent> eventQueue = new Queue<SystemsEvent>();
        private readonly List<SystemsEvent> activeEvents = new List<SystemsEvent>();

        // Event listeners for extensibility
        public event Action<SystemsEvent> OnSystemsTriggered;

        private VariationSystem variationSystem = new VariationSystem();
        private Dictionary<ActionType, SystemsConfig.SystemsTypeSettings> typeSettings = new();

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            LoadConfig();
            // Subscribe to error events
            EventBus.Instance.Subscribe<ActionErrorEvent>(OnActionErrorEvent);
        }

        private void Update()
        {
            ProcessEventQueue();
        }

        public void LoadConfig()
        {
            typeSettings.Clear();
            if (config != null)
            {
                foreach (var s in config.TypeSettings)
                {
                    typeSettings[s.Type] = s;
                }
            }
        }

        public void ApplyUserSettings(bool visual, bool audio, bool haptic, bool highContrast, bool reduceMotion, bool reduceFlashing)
        {
            if (config == null) return;
            config.VisualEnabled = visual;
            config.AudioEnabled = audio;
            config.HapticEnabled = haptic;
            config.HighContrastMode = highContrast;
            config.ReduceMotion = reduceMotion;
            config.ReduceFlashing = reduceFlashing;
            LoadConfig();
        }

        public void TriggerSystems(ActionType type, int importance, Vector2 position, SystemsContext context = null)
        {
            if (variationSystem.ShouldSuppressSystems())
                return;
            // Check config for enable/disable and intensity scaling
            if (config != null)
            {
                if (typeSettings.TryGetValue(type, out var s) && !s.Enabled)
                    return;
                if (type == ActionType.UI && !config.VisualEnabled && !config.AudioEnabled && !config.HapticEnabled)
                    return;
            }
            int adjustedImportance = variationSystem.AdjustImportance(type, importance > 0 ? importance : GetDefaultImportance(type), context);
            float scale = 1f;
            if (typeSettings.TryGetValue(type, out var ts))
                scale = ts.IntensityScale;
            adjustedImportance = Mathf.Clamp(Mathf.RoundToInt(adjustedImportance * scale), 1, 10);
            var evt = new SystemsEvent
            {
                Type = type,
                Importance = adjustedImportance,
                Position = position,
                Context = context,
                Timestamp = Time.time
            };
            eventQueue.Enqueue(evt);
        }

        private void ProcessEventQueue()
        {
            while (eventQueue.Count > 0 && activeEvents.Count < maxSimultaneousSystems)
            {
                var evt = eventQueue.Dequeue();
                activeEvents.Add(evt);
                DispatchSystems(evt);
            }
            // Remove finished events (in a real system, track duration/lifecycle)
            activeEvents.Clear();
        }

        private void DispatchSystems(SystemsEvent evt)
        {
            VisualModule?.TriggerSystems(evt.Type, evt.Importance, evt.Position, evt.Context);
            AudioModule?.TriggerSystems(evt.Type, evt.Importance, evt.Position, evt.Context);
            HapticModule?.TriggerSystems(evt.Type, evt.Importance, evt.Position, evt.Context);
            OnSystemsTriggered?.Invoke(evt);
        }

        private int GetDefaultImportance(ActionType type)
        {
            return defaultImportance.TryGetValue(type, out var imp) ? imp : 5;
        }

        // API for registering/unregistering feedback modules
        public void RegisterVisualModule(ISystemsModule module) => VisualModule = module;
        public void RegisterAudioModule(ISystemsModule module) => AudioModule = module;
        public void RegisterHapticModule(ISystemsModule module) => HapticModule = module;

        private void OnActionErrorEvent(ActionErrorEvent evt)
        {
            TriggerErrorSystems(evt.ErrorType, evt);
        }

        /// <summary>
        /// Triggers visual/audio feedback for action errors.
        /// </summary>
        public void TriggerErrorSystems(ActionErrorType errorType, object context = null)
        {
            // Map error types to feedback
            ActionType feedbackType = ActionType.UI;
            int importance = 7;
            string extraInfo = "Error";
            Color color = Color.red;
            AudioClip audioClip = null;
            switch (errorType)
            {
                case ActionErrorType.InvalidTarget:
                    color = Color.red;
                    importance = 8;
                    extraInfo = "InvalidTarget";
                    break;
                case ActionErrorType.InsufficientResources:
                    color = Color.yellow;
                    importance = 7;
                    extraInfo = "InsufficientResources";
                    break;
                case ActionErrorType.StateConflict:
                    color = Color.magenta;
                    importance = 7;
                    extraInfo = "StateConflict";
                    break;
                case ActionErrorType.Timeout:
                    color = Color.gray;
                    importance = 6;
                    extraInfo = "Timeout";
                    break;
                default:
                    color = Color.red;
                    importance = 7;
                    extraInfo = "UnknownError";
                    break;
            }
            // Visual feedback (flash, icon, etc.)
            if (VisualModule != null)
            {
                var ctx = new SystemsContext { ExtraInfo = extraInfo };
                // Optionally pass color via context or extend ISystemsModule
                VisualModule.TriggerSystems(feedbackType, importance, Vector2.zero, ctx);
            }
            // Audio feedback (different tones for error types)
            if (AudioModule != null)
            {
                var ctx = new SystemsContext { ExtraInfo = extraInfo };
                AudioModule.TriggerSystems(feedbackType, importance, Vector2.zero, ctx);
            }
            // Optionally: haptic feedback for errors
            if (HapticModule != null)
            {
                var ctx = new SystemsContext { ExtraInfo = extraInfo };
                HapticModule.TriggerSystems(feedbackType, importance, Vector2.zero, ctx);
            }
        }

        /// <summary>
        /// Show an overlay with the error log (for developer debugging).
        /// </summary>
        public void ShowErrorLogOverlay()
        {
            // In a real implementation, this would display a UI overlay with the error log contents.
            // For now, just output to the console for developer debugging.
            var log = ErrorDetector.Instance.ExportErrorLog();
            Debug.Log("[ErrorLogOverlay]\n" + log);
        }

        public void ShowFactionSchism(Vector2 position, string parentName, string childName)
        {
            var ctx = new SystemsContext { ExtraInfo = $"Schism: {parentName} → {childName}" };
            TriggerSystems(ActionType.FactionSchism, 8, position, ctx);
        }
        public void ShowFactionSwitch(Vector2 position, string entityId, string from, string to)
        {
            var ctx = new SystemsContext { ExtraInfo = $"Switch: {entityId} {from} → {to}" };
            TriggerSystems(ActionType.FactionSwitch, 7, position, ctx);
        }
        public void ShowFactionRelationshipChanged(Vector2 position, string a, string b, float value)
        {
            var ctx = new SystemsContext { ExtraInfo = $"Rel: {a} ↔ {b} = {value:F2}" };
            TriggerSystems(ActionType.FactionRelationshipChanged, 6, position, ctx);
        }

        // Example usage after a social check:
        // SystemsManager.Instance.TriggerSystems(ActionType.SocialCheckSuccess, 5, npcPosition, new SystemsContext { ExtraInfo = "Persuasion" });
        // SystemsManager.Instance.TriggerSystems(ActionType.SocialCheckFailure, 7, npcPosition, new SystemsContext { ExtraInfo = "Deception" });
        // SystemsManager.Instance.TriggerSystems(ActionType.TrustChanged, 3, npcPosition, new SystemsContext { ExtraInfo = "+10" });
    }
}