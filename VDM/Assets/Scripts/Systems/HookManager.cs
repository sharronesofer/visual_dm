using System;
using System.Collections.Generic;
using System.Threading;

namespace VisualDM.AI
{
    public class HookManager
    {
        private static HookManager _instance;
        private static readonly object _lock = new object();
        public static HookManager Instance
        {
            get
            {
                lock (_lock)
                {
                    return _instance ??= new HookManager();
                }
            }
        }

        private readonly HookPriorityQueue _queue = new HookPriorityQueue();
        private readonly HookAnalytics _analytics = new HookAnalytics();
        private readonly HashSet<Guid> _pausedHooks = new HashSet<Guid>();
        private readonly Dictionary<Guid, HookEvent> _registeredHooks = new Dictionary<Guid, HookEvent>();
        private readonly List<Action<HookEvent>> _subscribers = new List<Action<HookEvent>>();
        private readonly object _queueLock = new object();

        public Guid RegisterHook(HookEvent hookEvent)
        {
            var id = Guid.NewGuid();
            lock (_queueLock)
            {
                _registeredHooks[id] = hookEvent;
                _queue.Enqueue(hookEvent);
                _analytics.LogEvent(hookEvent.EventType);
            }
            return id;
        }

        public void DeregisterHook(Guid hookId)
        {
            lock (_queueLock)
            {
                _registeredHooks.Remove(hookId);
                // No direct removal from queue; processed on dequeue
            }
        }

        public void PauseHook(Guid hookId)
        {
            lock (_queueLock)
            {
                _pausedHooks.Add(hookId);
            }
        }

        public void ResumeHook(Guid hookId)
        {
            lock (_queueLock)
            {
                _pausedHooks.Remove(hookId);
            }
        }

        public void Subscribe(Action<HookEvent> listener)
        {
            lock (_queueLock)
            {
                _subscribers.Add(listener);
            }
        }

        public void Unsubscribe(Action<HookEvent> listener)
        {
            lock (_queueLock)
            {
                _subscribers.Remove(listener);
            }
        }

        public void ProcessNextEvent()
        {
            HookEvent hookEvent = null;
            lock (_queueLock)
            {
                while (_queue.Count > 0)
                {
                    hookEvent = _queue.Dequeue();
                    var hookId = GetHookId(hookEvent);
                    if (hookId != null && _pausedHooks.Contains(hookId.Value))
                        continue; // Skip paused hooks
                    break;
                }
            }
            if (hookEvent != null)
            {
                foreach (var subscriber in _subscribers)
                {
                    subscriber.Invoke(hookEvent);
                }
            }
        }

        private Guid? GetHookId(HookEvent hookEvent)
        {
            foreach (var kvp in _registeredHooks)
            {
                if (kvp.Value == hookEvent)
                    return kvp.Key;
            }
            return null;
        }
    }
} 