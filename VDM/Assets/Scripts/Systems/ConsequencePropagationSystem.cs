using System;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

namespace VisualDM.Systems.Quest
{
    public enum ConsequenceSeverity
    {
        Minor,
        Moderate,
        Major,
        Critical
    }

    public enum ConsequenceCategory
    {
        NPC,
        Faction,
        World,
        Item,
        Other
    }

    public interface IConsequence
    {
        ConsequenceCategory Category { get; }
        ConsequenceSeverity Severity { get; }
        string Description { get; }
        object Payload { get; }
    }

    public interface IConsequenceListener
    {
        void OnConsequence(IConsequence consequence);
    }

    public class Consequence : IConsequence
    {
        public ConsequenceCategory Category { get; set; }
        public ConsequenceSeverity Severity { get; set; }
        public string Description { get; set; }
        public object Payload { get; set; }
        public List<IConsequence> ChainedConsequences { get; set; } = new();
    }

    /// <summary>
    /// Event-driven system for propagating quest consequences to game systems.
    /// </summary>
    public class ConsequencePropagationSystem
    {
        private static ConsequencePropagationSystem _instance;
        public static ConsequencePropagationSystem Instance => _instance ??= new ConsequencePropagationSystem();

        private readonly Dictionary<ConsequenceCategory, List<IConsequenceListener>> _listeners = new();
        private readonly object _lock = new();

        private ConsequencePropagationSystem()
        {
            foreach (ConsequenceCategory cat in Enum.GetValues(typeof(ConsequenceCategory)))
                _listeners[cat] = new List<IConsequenceListener>();
        }

        public void RegisterListener(ConsequenceCategory category, IConsequenceListener listener)
        {
            lock (_lock)
            {
                if (!_listeners[category].Contains(listener))
                    _listeners[category].Add(listener);
            }
        }

        public void UnregisterListener(ConsequenceCategory category, IConsequenceListener listener)
        {
            lock (_lock)
            {
                _listeners[category].Remove(listener);
            }
        }

        /// <summary>
        /// Propagate a consequence to all registered listeners, resolving conflicts and chaining as needed.
        /// </summary>
        public void PropagateConsequence(IConsequence consequence)
        {
            try
            {
                List<IConsequenceListener> listeners;
                lock (_lock)
                {
                    listeners = new List<IConsequenceListener>(_listeners[consequence.Category]);
                }
                foreach (var listener in listeners)
                {
                    try
                    {
                        listener.OnConsequence(consequence);
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"Consequence listener error: {ex.Message}");
                    }
                }
                // Handle chained consequences
                if (consequence is Consequence c && c.ChainedConsequences != null)
                {
                    foreach (var chained in c.ChainedConsequences)
                        PropagateConsequence(chained);
                }
            }
            catch (Exception ex)
            {
                Debug.LogError($"Consequence propagation error: {ex.Message}");
            }
        }

        /// <summary>
        /// Resolves conflicting consequences by severity (example: highest severity wins).
        /// </summary>
        public IConsequence ResolveConflicts(List<IConsequence> consequences)
        {
            if (consequences == null || consequences.Count == 0) return null;
            IConsequence highest = consequences[0];
            foreach (var c in consequences)
            {
                if (c.Severity > highest.Severity)
                    highest = c;
            }
            return highest;
        }
    }
} 