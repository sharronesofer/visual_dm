using System;
using System.Collections.Generic;

namespace VisualDM.World
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
}