using System;
using System.Collections.Generic;

namespace VDM.Combat
{
    /// <summary>
    /// Publisher/subscriber event bus for combat events.
    /// </summary>
    public class CombatEventBus
    {
        private static CombatEventBus _instance;
        public static CombatEventBus Instance => _instance ??= new CombatEventBus();

        private readonly Dictionary<Type, List<Delegate>> _subscribers = new();

        public void Subscribe<T>(Action<T> handler)
        {
            var type = typeof(T);
            if (!_subscribers.ContainsKey(type))
                _subscribers[type] = new List<Delegate>();
            _subscribers[type].Add(handler);
        }

        public void Unsubscribe<T>(Action<T> handler)
        {
            var type = typeof(T);
            if (_subscribers.ContainsKey(type))
                _subscribers[type].Remove(handler);
        }

        public void Publish<T>(T evt)
        {
            var type = typeof(T);
            if (_subscribers.ContainsKey(type))
            {
                foreach (var handler in _subscribers[type])
                {
                    (handler as Action<T>)?.Invoke(evt);
                }
            }
        }
    }
} 