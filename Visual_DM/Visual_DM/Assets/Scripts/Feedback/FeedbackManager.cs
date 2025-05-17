using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.CombatSystem;
using VisualDM.Systems.EventSystem;

namespace VisualDM.Feedback
{
    public enum ActionType
    {
        AttackLight,
        AttackHeavy,
        Spell,
        UI,
        // Add more as needed
        SocialCheckSuccess,
        SocialCheckFailure,
        TrustChanged
    }

    public class FeedbackContext
    {
        // Extend with additional context data as needed
        public string ExtraInfo;
    }

    public interface IFeedbackModule
    {
        void TriggerFeedback(ActionType type, int importance, Vector2 position, FeedbackContext context = null);
    }

    public class FeedbackEvent
    {
        public ActionType Type;
        public int Importance;
        public Vector2 Position;
        public FeedbackContext Context;
        public float Timestamp;
    }

    public class VariationSystem
    {
        private readonly System.Random random = new System.Random();
        private float lastFeedbackTime = 0f;
        private float minInterval = 0.03f; // Minimum interval between feedback events (seconds)
        private int overloadThreshold = 12; // Max feedback events per frame
        private int feedbacksThisFrame = 0;
        private int lastFrame = -1;

        // Context-aware importance scaling
        public int AdjustImportance(ActionType type, int baseImportance, FeedbackContext context)
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
        public bool ShouldSuppressFeedback()
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
            if (Time.time - lastFeedbackTime < minInterval)
                return true;
            lastFeedbackTime = Time.time;
            return false;
        }
    }

    [CreateAssetMenu(fileName = "FeedbackConfig", menuName = "VisualDM/FeedbackConfig", order = 1)]
    public class FeedbackConfig : ScriptableObject
    {
        [Serializable]
        public class FeedbackTypeSettings
        {
            public ActionType Type;
            public bool Enabled = true;
            [Range(0.1f, 2f)] public float IntensityScale = 1f;
        }
        public List<FeedbackTypeSettings> TypeSettings = new();
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

    public class FeedbackManager : MonoBehaviour
    {
        public static FeedbackManager Instance { get; private set; }

        [Header("Feedback Configuration")]
        public FeedbackConfig config;

        // Configurable cap for simultaneous feedback events
        [SerializeField] private int maxSimultaneousFeedback = 8;

        // Module references (to be assigned at runtime)
        public IFeedbackModule VisualModule { get; set; }
        public IFeedbackModule AudioModule { get; set; }
        public IFeedbackModule HapticModule { get; set; }

        // Importance mapping (can be loaded from config)
        private readonly Dictionary<ActionType, int> defaultImportance = new Dictionary<ActionType, int>
        {
            { ActionType.AttackLight, 3 },
            { ActionType.AttackHeavy, 7 },
            { ActionType.Spell, 6 },
            { ActionType.UI, 2 },
        };

        // Feedback event queue
        private readonly Queue<FeedbackEvent> eventQueue = new Queue<FeedbackEvent>();
        private readonly List<FeedbackEvent> activeEvents = new List<FeedbackEvent>();

        // Event listeners for extensibility
        public event Action<FeedbackEvent> OnFeedbackTriggered;

        private VariationSystem variationSystem = new VariationSystem();
        private Dictionary<ActionType, FeedbackConfig.FeedbackTypeSettings> typeSettings = new();

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

        public void TriggerFeedback(ActionType type, int importance, Vector2 position, FeedbackContext context = null)
        {
            if (variationSystem.ShouldSuppressFeedback())
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
            var evt = new FeedbackEvent
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
            while (eventQueue.Count > 0 && activeEvents.Count < maxSimultaneousFeedback)
            {
                var evt = eventQueue.Dequeue();
                activeEvents.Add(evt);
                DispatchFeedback(evt);
            }
            // Remove finished events (in a real system, track duration/lifecycle)
            activeEvents.Clear();
        }

        private void DispatchFeedback(FeedbackEvent evt)
        {
            VisualModule?.TriggerFeedback(evt.Type, evt.Importance, evt.Position, evt.Context);
            AudioModule?.TriggerFeedback(evt.Type, evt.Importance, evt.Position, evt.Context);
            HapticModule?.TriggerFeedback(evt.Type, evt.Importance, evt.Position, evt.Context);
            OnFeedbackTriggered?.Invoke(evt);
        }

        private int GetDefaultImportance(ActionType type)
        {
            return defaultImportance.TryGetValue(type, out var imp) ? imp : 5;
        }

        // API for registering/unregistering feedback modules
        public void RegisterVisualModule(IFeedbackModule module) => VisualModule = module;
        public void RegisterAudioModule(IFeedbackModule module) => AudioModule = module;
        public void RegisterHapticModule(IFeedbackModule module) => HapticModule = module;

        private void OnActionErrorEvent(ActionErrorEvent evt)
        {
            TriggerErrorFeedback(evt.ErrorType, evt);
        }

        /// <summary>
        /// Triggers visual/audio feedback for action errors.
        /// </summary>
        public void TriggerErrorFeedback(ActionErrorType errorType, object context = null)
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
                var ctx = new FeedbackContext { ExtraInfo = extraInfo };
                // Optionally pass color via context or extend IFeedbackModule
                VisualModule.TriggerFeedback(feedbackType, importance, Vector2.zero, ctx);
            }
            // Audio feedback (different tones for error types)
            if (AudioModule != null)
            {
                var ctx = new FeedbackContext { ExtraInfo = extraInfo };
                AudioModule.TriggerFeedback(feedbackType, importance, Vector2.zero, ctx);
            }
            // Optionally: haptic feedback for errors
            if (HapticModule != null)
            {
                var ctx = new FeedbackContext { ExtraInfo = extraInfo };
                HapticModule.TriggerFeedback(feedbackType, importance, Vector2.zero, ctx);
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

        // Example usage after a social check:
        // FeedbackManager.Instance.TriggerFeedback(ActionType.SocialCheckSuccess, 5, npcPosition, new FeedbackContext { ExtraInfo = "Persuasion" });
        // FeedbackManager.Instance.TriggerFeedback(ActionType.SocialCheckFailure, 7, npcPosition, new FeedbackContext { ExtraInfo = "Deception" });
        // FeedbackManager.Instance.TriggerFeedback(ActionType.TrustChanged, 3, npcPosition, new FeedbackContext { ExtraInfo = "+10" });
    }
}