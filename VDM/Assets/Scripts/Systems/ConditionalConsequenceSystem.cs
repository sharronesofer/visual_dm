using System;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

namespace VisualDM.Systems.Quest
{
    public enum ConditionType { And, Or, Leaf }

    [Serializable]
    public class ConditionTree
    {
        public ConditionType Type;
        public List<ConditionTree> Children = new();
        public Func<bool> LeafEvaluator; // Only used for leaf nodes

        public bool Evaluate()
        {
            switch (Type)
            {
                case ConditionType.And:
                    foreach (var child in Children)
                        if (!child.Evaluate()) return false;
                    return true;
                case ConditionType.Or:
                    foreach (var child in Children)
                        if (child.Evaluate()) return true;
                    return false;
                case ConditionType.Leaf:
                    return LeafEvaluator != null && LeafEvaluator();
                default:
                    return false;
            }
        }
    }

    public class DelayedConsequence
    {
        public IConsequence Consequence;
        public float DelaySeconds;
        public DateTime TriggerTime;
        public bool Triggered;
        public Action OnInterrupt;
        public string EventName; // For event-based triggers
    }

    public class TriggerListener
    {
        public string EventName;
        public ConditionTree Condition;
        public IConsequence Consequence;
        public Action OnTriggered;
    }

    /// <summary>
    /// System for managing conditional and delayed consequences.
    /// </summary>
    public class ConditionalConsequenceSystem : MonoBehaviour
    {
        private static ConditionalConsequenceSystem _instance;
        public static ConditionalConsequenceSystem Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("ConditionalConsequenceSystem");
                    _instance = go.AddComponent<ConditionalConsequenceSystem>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private readonly List<TriggerListener> _listeners = new();
        private readonly List<DelayedConsequence> _delayed = new();
        private readonly object _lock = new();

        void Update()
        {
            // Check for delayed consequences to trigger
            lock (_lock)
            {
                var now = DateTime.UtcNow;
                foreach (var dc in _delayed)
                {
                    if (!dc.Triggered && dc.DelaySeconds > 0 && now >= dc.TriggerTime)
                    {
                        ConsequencePropagationSystem.Instance.PropagateConsequence(dc.Consequence);
                        dc.Triggered = true;
                    }
                }
                _delayed.RemoveAll(dc => dc.Triggered);
            }
        }

        public void RegisterTriggerListener(TriggerListener listener)
        {
            lock (_lock)
            {
                _listeners.Add(listener);
            }
        }

        public void UnregisterTriggerListener(TriggerListener listener)
        {
            lock (_lock)
            {
                _listeners.Remove(listener);
            }
        }

        public void RegisterDelayedConsequence(DelayedConsequence dc)
        {
            lock (_lock)
            {
                dc.TriggerTime = DateTime.UtcNow.AddSeconds(dc.DelaySeconds);
                _delayed.Add(dc);
            }
        }

        public void InterruptDelayedConsequence(DelayedConsequence dc)
        {
            lock (_lock)
            {
                if (_delayed.Contains(dc))
                {
                    dc.OnInterrupt?.Invoke();
                    _delayed.Remove(dc);
                }
            }
        }

        // Simulate event trigger (in real system, hook into event bus)
        public void OnGameEvent(string eventName)
        {
            lock (_lock)
            {
                foreach (var listener in _listeners)
                {
                    if (listener.EventName == eventName && listener.Condition.Evaluate())
                    {
                        ConsequencePropagationSystem.Instance.PropagateConsequence(listener.Consequence);
                        listener.OnTriggered?.Invoke();
                    }
                }
                foreach (var dc in _delayed)
                {
                    if (!dc.Triggered && dc.EventName == eventName)
                    {
                        ConsequencePropagationSystem.Instance.PropagateConsequence(dc.Consequence);
                        dc.Triggered = true;
                    }
                }
                _delayed.RemoveAll(dc => dc.Triggered);
            }
        }
    }
} 