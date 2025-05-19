using UnityEngine;
using System;
using VisualDM.Systems.EventSystem;

namespace VDM.POI
{
    /// <summary>
    /// Manages POI state transitions and holds the state machine for a POI.
    /// </summary>
    public class POIStateManager : MonoBehaviour, IPOIStateContext
    {
        [Header("POI Population Settings")]
        [SerializeField] private int maxPopulation = 100;
        [SerializeField] private int currentPopulation = 100;
        [SerializeField] private float populationChangeRate = 0f;

        [Header("State Transition Configuration")]
        [SerializeField] private POIStateTransitionRuleSet transitionRuleSet;
        [SerializeField] private string poiId; // Unique identifier for this POI

        private POIState currentState;
        public POIState CurrentState => currentState;

        public int CurrentPopulation => currentPopulation;
        public int MaxPopulation => maxPopulation;
        public float PopulationChangeRate => populationChangeRate;

        private PopulationMetricsTracker populationTracker = new PopulationMetricsTracker();
        private float metricsUpdateTimer = 0f;
        private float metricsUpdateInterval => 1f; // Match default in tracker

        public event Action<POIState, POIState> OnStateChanged;

        public struct POIStateChangedEvent
        {
            public string POIId;
            public string OldState;
            public string NewState;
            public DateTime Timestamp;
        }

        private void Awake()
        {
            // Start in Normal state by default
            currentState = new POIStateNormal(this);
            currentState.EnterState();
            populationTracker.Initialize(currentPopulation, maxPopulation);
            // Subscribe to population tracker events for significant changes
            populationTracker.OnSignificantDrop += OnPopulationSignificantChange;
        }

        private void OnDestroy()
        {
            populationTracker.OnSignificantDrop -= OnPopulationSignificantChange;
        }

        private void OnPopulationSignificantChange(float dropPercent)
        {
            // Only check transitions when a significant change occurs
            currentState.CheckTransition();
        }

        private void Update() { /* No longer checks transitions every frame */ }

        public void ChangeState(POIState newState)
        {
            // Exemption check
            if (transitionRuleSet != null && transitionRuleSet.IsExempt(poiId))
                return;
            // Manual override check
            if (transitionRuleSet != null && transitionRuleSet.IsManualOverrideActive(out var overrideState))
            {
                if (currentState.StateName != overrideState.ToString())
                {
                    currentState.ExitState();
                    var oldState = currentState;
                    currentState = CreateStateFromType(overrideState);
                    currentState.EnterState();
                    OnStateChanged?.Invoke(oldState, currentState);
                    // Emit event
                    EventBus.Instance.Publish(new POIStateChangedEvent {
                        POIId = poiId,
                        OldState = oldState.StateName,
                        NewState = currentState.StateName,
                        Timestamp = DateTime.UtcNow
                    });
                }
                return;
            }
            if (currentState != null)
            {
                currentState.ExitState();
                var oldState = currentState;
                currentState = newState;
                if (currentState != null)
                    currentState.EnterState();
                OnStateChanged?.Invoke(oldState, currentState);
                // Emit event
                EventBus.Instance.Publish(new POIStateChangedEvent {
                    POIId = poiId,
                    OldState = oldState.StateName,
                    NewState = currentState.StateName,
                    Timestamp = DateTime.UtcNow
                });
            }
        }

        // Methods to externally set population (for testing/demo)
        public void SetPopulation(int value)
        {
            currentPopulation = Mathf.Clamp(value, 0, maxPopulation);
            populationTracker.UpdateMetrics(currentPopulation, maxPopulation);
        }

        public void SetMaxPopulation(int value)
        {
            maxPopulation = Mathf.Max(1, value);
            currentPopulation = Mathf.Clamp(currentPopulation, 0, maxPopulation);
            populationTracker.UpdateMetrics(currentPopulation, maxPopulation);
        }

        public void SetPopulationChangeRate(float value)
        {
            populationChangeRate = value;
            // Not directly settable; calculated by tracker
        }

        // Expose tracker for advanced queries
        public PopulationMetricsTracker GetPopulationMetricsTracker() => populationTracker;

        public POIStateTransitionRuleSet GetTransitionRuleSet() => transitionRuleSet;
        public string GetPOIId() => poiId;
        public void SetManualOverride(POIStateType state)
        {
            if (transitionRuleSet != null)
            {
                transitionRuleSet.manualOverride = true;
                transitionRuleSet.overrideState = state;
            }
        }
        public void ClearManualOverride()
        {
            if (transitionRuleSet != null)
                transitionRuleSet.manualOverride = false;
        }
        public void AddExemption(string id)
        {
            if (transitionRuleSet != null && !transitionRuleSet.exemptPOIIds.Contains(id))
                transitionRuleSet.exemptPOIIds.Add(id);
        }
        public void RemoveExemption(string id)
        {
            if (transitionRuleSet != null)
                transitionRuleSet.exemptPOIIds.Remove(id);
        }
        private POIState CreateStateFromType(POIStateType type)
        {
            switch (type)
            {
                case POIStateType.Normal: return new POIStateNormal(this);
                case POIStateType.Declining: return new POIStateDeclining(this);
                case POIStateType.Abandoned: return new POIStateAbandoned(this);
                case POIStateType.Ruins: return new POIStateRuins(this);
                case POIStateType.Dungeon: return new POIStateDungeon(this);
                default: return new POIStateNormal(this);
            }
        }

        // Integration utility: Attach POIStateManager at runtime if missing
        public static POIStateManager AttachTo(GameObject go)
        {
            var manager = go.GetComponent<POIStateManager>();
            if (manager == null)
                manager = go.AddComponent<POIStateManager>();
            return manager;
        }

        /// <summary>
        /// Called by WarManager when a POI is affected by war damage.
        /// Triggers state transition to Ruins or Abandoned as appropriate.
        /// </summary>
        public void OnWarDamage(float severity)
        {
            // Example: If severity is high, transition to Ruins; else, Declining/Abandoned
            if (severity > 0.7f)
            {
                TransitionToState(POIStateType.Ruins);
            }
            else if (severity > 0.4f)
            {
                TransitionToState(POIStateType.Abandoned);
            }
            else if (severity > 0.2f)
            {
                TransitionToState(POIStateType.Declining);
            }
            // else, no change
        }
    }
} 