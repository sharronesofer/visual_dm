using System;
using System.Collections.Generic;

namespace Visual_DM.WorldState
{
    // Delegate for world state change events
    public delegate void WorldStateChangedHandler<T>(T newValue, T oldValue);

    // Base class for observable world state properties
    public class ObservableWorldStateProperty<T>
    {
        private T _value;
        private readonly List<WorldStateChangedHandler<T>> _subscribers = new List<WorldStateChangedHandler<T>>();
        private bool _hasValue = false;

        public ObservableWorldStateProperty(T initialValue = default)
        {
            _value = initialValue;
            _hasValue = !EqualityComparer<T>.Default.Equals(initialValue, default);
        }

        public void Subscribe(WorldStateChangedHandler<T> handler)
        {
            if (!_subscribers.Contains(handler))
                _subscribers.Add(handler);
        }

        public void Unsubscribe(WorldStateChangedHandler<T> handler)
        {
            _subscribers.Remove(handler);
        }

        public T Value
        {
            get => _value;
            set
            {
                if (_hasValue && EqualityComparer<T>.Default.Equals(_value, value))
                    return; // Prevent redundant notification
                T oldValue = _value;
                _value = value;
                _hasValue = true;
                NotifySubscribers(_value, oldValue);
            }
        }

        private void NotifySubscribers(T newValue, T oldValue)
        {
            foreach (var handler in _subscribers)
            {
                try
                {
                    handler?.Invoke(newValue, oldValue);
                }
                catch (Exception ex)
                {
                    // Log or handle subscriber exceptions as needed
                    UnityEngine.Debug.LogError($"WorldStateObserver: Exception in subscriber: {ex}");
                }
            }
        }
    }

    // Example usage: WorldStateManager holding observable properties
    public class WorldStateManager
    {
        // Example: public observable properties for world state
        public ObservableWorldStateProperty<int> Population = new ObservableWorldStateProperty<int>(0);
        public ObservableWorldStateProperty<string> Weather = new ObservableWorldStateProperty<string>("Clear");
        // Add more properties as needed

        // Singleton pattern for global access (optional)
        private static WorldStateManager _instance;
        public static WorldStateManager Instance => _instance ?? (_instance = new WorldStateManager());

        private WorldStateManager() { }

        /// <summary>
        /// Exports a snapshot of all global world state properties for use in quest generation, arc conditions, etc.
        /// </summary>
        public Dictionary<string, object> ExportWorldStateSnapshot()
        {
            var snapshot = new Dictionary<string, object>();
            var globalProps = this.GetType().GetField("_globalProperties", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)?.GetValue(this) as Dictionary<string, object>;
            if (globalProps != null)
            {
                foreach (var kvp in globalProps)
                {
                    snapshot[kvp.Key] = kvp.Value;
                }
            }
            // Optionally, add region/global observable properties as needed
            return snapshot;
        }

        // Integration Example:
        // - Use WorldStateManager.Instance.GetProperty<T>("Population") in arc trigger/completion conditions
        // - Use WorldStateManager.Instance.ExportWorldStateSnapshot() when constructing ArcQuestGenerationContext
        // - Subscribe to property changes: WorldStateManager.Instance.Population.Subscribe(OnPopulationChanged);
    }
}