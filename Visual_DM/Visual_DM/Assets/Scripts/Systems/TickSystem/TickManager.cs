using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Narrative;
using VisualDM.Systems.EventSystem;

namespace VisualDM.Systems.TickSystem
{
    /// <summary>
    /// Core manager for flexible tick-based progression of Global Arcs.
    /// Handles both time-based and event-driven progression triggers.
    /// </summary>
    public class TickManager : MonoBehaviour
    {
        // Singleton instance
        public static TickManager Instance { get; private set; }

        // List of all managed Global Arcs
        private readonly List<GlobalArc> _globalArcs = new();

        // Event subscriptions and time tracking will be added in subsequent steps

        private Dictionary<GlobalArc, int> _eventCounters = new();

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
            SubscribeToEvents();
        }

        private void SubscribeToEvents()
        {
            // Example: subscribe to a generic event type; extend for specific event types as needed
            EventBus.Instance.Subscribe<GameEvent>(OnGameEvent);
        }

        private void OnGameEvent(GameEvent evt)
        {
            foreach (var arc in _globalArcs)
            {
                var config = arc.TickConfiguration;
                var state = arc.ProgressionState;
                if (config == null || state == null) continue;
                if (!config.EnableEventBased) continue;
                if (config.EventTypes != null && config.EventTypes.Count > 0 && !config.EventTypes.Contains(evt.Type))
                    continue;
                state.EventsSinceLastTick++;
                if (config.CompoundEventTrigger)
                {
                    if (state.EventsSinceLastTick >= config.CompoundEventCount)
                    {
                        state.EventsSinceLastTick = 0;
                        ProgressArcByEvent(arc);
                    }
                }
                else if (state.EventsSinceLastTick >= config.EventThreshold)
                {
                    state.EventsSinceLastTick = 0;
                    ProgressArcByEvent(arc);
                }
            }
        }

        private void ProgressArcByEvent(GlobalArc arc)
        {
            if (!arc.IsComplete(null)) // TODO: Pass actual GameState
            {
                arc.ProgressStage();
                arc.ProgressionState.LastTickedStage = arc.CurrentStageIndex;
                arc.ProgressionState.TotalTicks++;
                arc.ProgressionState.LastTickTime = DateTime.UtcNow;
                // Broadcast progression event
                EventBus.Instance.Publish(new GlobalArcProgressedEvent(arc, arc.CurrentStageIndex));
            }
        }

        /// <summary>
        /// Registers a Global Arc for tick progression.
        /// </summary>
        public void RegisterArc(GlobalArc arc)
        {
            if (!_globalArcs.Contains(arc))
                _globalArcs.Add(arc);
        }

        /// <summary>
        /// Unregisters a Global Arc from tick progression.
        /// </summary>
        public void UnregisterArc(GlobalArc arc)
        {
            _globalArcs.Remove(arc);
        }

        // Main update loop for time-based progression (to be extended)
        private void Update()
        {
            float deltaTime = Time.deltaTime;
            foreach (var arc in _globalArcs)
            {
                var config = arc.TickConfiguration;
                var state = arc.ProgressionState;
                if (config == null || state == null) continue;
                if (config.EnableTimeBased)
                {
                    float interval = config.TickIntervalSeconds * config.AccelerationFactor / config.DecelerationFactor;
                    state.TimeSinceLastTick += deltaTime;
                    if (state.TimeSinceLastTick >= interval)
                    {
                        state.TimeSinceLastTick -= interval;
                        state.TotalTicks++;
                        state.LastTickTime = DateTime.UtcNow;
                        if (!arc.IsComplete(null))
                        {
                            arc.ProgressStage();
                            state.LastTickedStage = arc.CurrentStageIndex;
                            // Broadcast progression event
                            EventBus.Instance.Publish(new GlobalArcProgressedEvent(arc, arc.CurrentStageIndex));
                        }
                    }
                }
                // Event-based progression handled elsewhere
            }
        }

        // Event-based progression hooks will be implemented here

        // Event definition
        public class GlobalArcProgressedEvent
        {
            public GlobalArc Arc { get; }
            public int NewStageIndex { get; }
            public GlobalArcProgressedEvent(GlobalArc arc, int newStageIndex)
            {
                Arc = arc;
                NewStageIndex = newStageIndex;
            }
        }

        /// <summary>
        /// Reports a relevant event for a specific arc (for custom event-based progression triggers).
        /// </summary>
        /// <param name="arc">The GlobalArc to report the event for.</param>
        /// <param name="eventType">The type of event to report.</param>
        public void ReportEventForArc(GlobalArc arc, string eventType)
        {
            if (!_globalArcs.Contains(arc)) return;
            var config = arc.TickConfiguration;
            var state = arc.ProgressionState;
            if (config == null || state == null) return;
            if (!config.EnableEventBased) return;
            if (config.EventTypes != null && config.EventTypes.Count > 0 && !config.EventTypes.Contains(eventType))
                return;
            state.EventsSinceLastTick++;
            if (config.CompoundEventTrigger)
            {
                if (state.EventsSinceLastTick >= config.CompoundEventCount)
                {
                    state.EventsSinceLastTick = 0;
                    ProgressArcByEvent(arc);
                }
            }
            else if (state.EventsSinceLastTick >= config.EventThreshold)
            {
                state.EventsSinceLastTick = 0;
                ProgressArcByEvent(arc);
            }
        }

        /// <summary>
        /// Gets the tick-based progression state for a specific arc.
        /// </summary>
        /// <param name="arc">The GlobalArc to query.</param>
        /// <returns>The ArcTickProgressionState for the arc.</returns>
        public ArcTickProgressionState GetArcProgressionState(GlobalArc arc)
        {
            return arc.ProgressionState;
        }

        /// <summary>
        /// Validates a TickConfig for design errors and invalid values.
        /// </summary>
        /// <param name="config">The TickConfig to validate.</param>
        public static void ValidateTickConfig(TickConfig config)
        {
            if (config == null)
                throw new ArgumentNullException(nameof(config));
            if (config.EnableTimeBased && config.TickIntervalSeconds <= 0)
                throw new ArgumentException("TickIntervalSeconds must be positive for time-based progression");
            if (config.EnableEventBased && (config.EventTypes == null || config.EventTypes.Count == 0))
                Debug.LogWarning("Event-based progression enabled but no event types specified");
            if (config.CompoundEventTrigger && config.CompoundEventCount <= 0)
                throw new ArgumentException("CompoundEventCount must be positive if CompoundEventTrigger is enabled");
            if (config.StageThresholds != null)
            {
                foreach (var kvp in config.StageThresholds)
                {
                    if (kvp.Value <= 0)
                        throw new ArgumentException($"Stage threshold for stage {kvp.Key} must be positive");
                }
            }
        }

#if UNITY_EDITOR
        /// <summary>
        /// Draws debug info for all registered arcs in the Unity Editor.
        /// </summary>
        private void OnDrawGizmos()
        {
            DrawDebugInfo();
        }

        public void DrawDebugInfo()
        {
            float y = 10f;
            foreach (var arc in _globalArcs)
            {
                var state = arc.ProgressionState;
                if (state == null) continue;
                string label = $"Arc: {arc.Title} | Stage: {arc.CurrentStageIndex} | Ticks: {state.TotalTicks} | LastTick: {state.LastTickTime}";
                UnityEditor.Handles.Label(new Vector3(10, y, 0), label);
                y += 20f;
            }
        }
#endif
    }
}