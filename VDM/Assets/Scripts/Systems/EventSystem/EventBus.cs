using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using System.Buffers;

namespace VisualDM.Systems.EventSystem
{
    /// <summary>
    /// Advanced event bus for runtime event-driven architecture in Unity.
    /// Supports generic event types, handler priorities, filtering, weak references, and debug logging.
    /// </summary>
    public class EventBus : MonoBehaviour
    {
        private static EventBus _instance;
        public static EventBus Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("EventBus");
                    _instance = go.AddComponent<EventBus>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        [Serializable]
        public class Subscription<TEvent>
        {
            public WeakReference<Action<TEvent>> Handler;
            public int Priority;
            public Predicate<TEvent> Filter;
            public bool OneTime;
        }

        private readonly Dictionary<Type, List<object>> _subscriptions = new();
        private bool _debugMode = false;

        // Object pool for event argument objects (generic, for struct-based event args)
        private static readonly ArrayPool<object> EventArgPool = ArrayPool<object>.Shared;
        // Batch queue for high-frequency events
        private readonly Queue<(Type, object)> _batchedEvents = new();
        private bool _batchingEnabled = false;
        private float _batchInterval = 0.01f; // 10ms default
        private float _batchTimer = 0f;

        /// <summary>
        /// Enable or disable debug mode for event logging.
        /// </summary>
        public void SetDebugMode(bool enabled) => _debugMode = enabled;

        /// <summary>
        /// Enable or disable event batching. When enabled, events are queued and dispatched in batches every batchInterval seconds.
        /// </summary>
        public void SetBatching(bool enabled, float interval = 0.01f)
        {
            _batchingEnabled = enabled;
            _batchInterval = interval;
        }

        void Update()
        {
            if (_batchingEnabled && _batchedEvents.Count > 0)
            {
                _batchTimer += Time.unscaledDeltaTime;
                if (_batchTimer >= _batchInterval)
                {
                    while (_batchedEvents.Count > 0)
                    {
                        var (type, evt) = _batchedEvents.Dequeue();
                        PublishInternal(type, evt);
                    }
                    _batchTimer = 0f;
                }
            }
        }

        /// <summary>
        /// Subscribe to an event type with optional priority and filter.
        /// </summary>
        public void Subscribe<TEvent>(Action<TEvent> handler, int priority = 0, Predicate<TEvent> filter = null, bool oneTime = false)
        {
            if (handler == null) throw new ArgumentNullException(nameof(handler));
            var type = typeof(TEvent);
            if (!_subscriptions.ContainsKey(type))
                _subscriptions[type] = new List<object>();
            _subscriptions[type].Add(new Subscription<TEvent>
            {
                Handler = new WeakReference<Action<TEvent>>(handler),
                Priority = priority,
                Filter = filter,
                OneTime = oneTime
            });
            if (_debugMode)
                Debug.Log($"[EventBus] Subscribed to {type.Name} (priority {priority}, oneTime {oneTime})");
        }

        /// <summary>
        /// Unsubscribe from an event type.
        /// </summary>
        public void Unsubscribe<TEvent>(Action<TEvent> handler)
        {
            var type = typeof(TEvent);
            if (!_subscriptions.TryGetValue(type, out var list)) return;
            list.RemoveAll(subObj =>
            {
                var sub = (Subscription<TEvent>)subObj;
                if (sub.Handler.TryGetTarget(out var h))
                    return h == handler;
                return true; // Remove dead weak refs
            });
            if (_debugMode)
                Debug.Log($"[EventBus] Unsubscribed from {type.Name}");
        }

        /// <summary>
        /// Publish an event, optionally using batching. Uses struct-based event args for efficiency.
        /// </summary>
        public void Publish<TEvent>(TEvent evt, bool useBatching = false) where TEvent : struct
        {
            if (_batchingEnabled || useBatching)
            {
                _batchedEvents.Enqueue((typeof(TEvent), evt));
                return;
            }
            PublishInternal(typeof(TEvent), evt);
        }

        private void PublishInternal(Type type, object evt)
        {
            if (_debugMode)
                Debug.Log($"[EventBus] Publishing {type.Name}: {evt}");
            if (!_subscriptions.TryGetValue(type, out var list)) return;
            var toRemove = new List<object>();
            var ordered = list.OrderByDescending(s => ((dynamic)s).Priority).ToList();
            foreach (var subObj in ordered)
            {
                dynamic sub = subObj;
                if (sub.Handler.TryGetTarget(out var handler))
                {
                    if (sub.Filter == null || sub.Filter(evt))
                    {
                        try { handler(evt); }
                        catch (Exception e)
                        {
                            Debug.LogError($"[EventBus] Exception in handler for {type.Name}: {e}");
                        }
                        if (sub.OneTime) toRemove.Add(sub);
                    }
                }
                else toRemove.Add(sub);
            }
            foreach (var sub in toRemove) list.Remove(sub);
        }

        /// <summary>
        /// Publish an event asynchronously to all subscribers.
        /// </summary>
        public async Task PublishAsync<TEvent>(TEvent evt)
        {
            var type = typeof(TEvent);
            if (_debugMode)
                Debug.Log($"[EventBus] Publishing async {type.Name}: {evt}");
            if (!_subscriptions.TryGetValue(type, out var list)) return;
            var toRemove = new List<object>();
            var ordered = list.Cast<Subscription<TEvent>>()
                .OrderByDescending(s => s.Priority).ToList();
            var tasks = new List<Task>();
            foreach (var sub in ordered)
            {
                if (sub.Handler.TryGetTarget(out var handler))
                {
                    if (sub.Filter == null || sub.Filter(evt))
                    {
                        try
                        {
                            tasks.Add(Task.Run(() => handler(evt)));
                        }
                        catch (Exception e)
                        {
                            Debug.LogError($"[EventBus] Exception in async handler for {type.Name}: {e}");
                        }
                        if (sub.OneTime) toRemove.Add(sub);
                    }
                }
                else toRemove.Add(sub);
            }
            foreach (var sub in toRemove) list.Remove(sub);
            await Task.WhenAll(tasks);
        }

        /// <summary>
        /// Utility: Subscribe for a single event occurrence only.
        /// </summary>
        public void SubscribeOnce<TEvent>(Action<TEvent> handler, int priority = 0, Predicate<TEvent> filter = null)
            => Subscribe(handler, priority, filter, oneTime: true);

        /// <summary>
        /// Utility: Publish an event after a delay (in seconds).
        /// </summary>
        public void PublishDelayed<TEvent>(TEvent evt, float delaySeconds)
        {
            StartCoroutine(PublishDelayedCoroutine(evt, delaySeconds));
        }
        private System.Collections.IEnumerator PublishDelayedCoroutine<TEvent>(TEvent evt, float delaySeconds)
        {
            yield return new WaitForSeconds(delaySeconds);
            Publish(evt);
        }

        /// <summary>
        /// Remove all subscriptions for a given event type.
        /// </summary>
        public void Clear<TEvent>()
        {
            var type = typeof(TEvent);
            _subscriptions.Remove(type);
            if (_debugMode)
                Debug.Log($"[EventBus] Cleared all subscriptions for {type.Name}");
        }

        /// <summary>
        /// Remove all subscriptions for all event types.
        /// </summary>
        public void ClearAll()
        {
            _subscriptions.Clear();
            if (_debugMode)
                Debug.Log("[EventBus] Cleared all subscriptions");
        }

        /// <summary>
        /// Rent an event argument array from the pool for temporary use.
        /// </summary>
        public static object[] RentEventArgs(int length) => EventArgPool.Rent(length);
        /// <summary>
        /// Return an event argument array to the pool.
        /// </summary>
        public static void ReturnEventArgs(object[] args) => EventArgPool.Return(args);

        /// <summary>
        /// Example usage for subscribing to nemesis/rival state changes:
        /// </summary>
        /// <example>
        /// EventBus.Instance.Subscribe<RelationshipStateChangedEvent>(evt => {
        ///     Debug.Log($"NPC {evt.NPCId} changed relationship with {evt.TargetId} from {evt.OldState} to {evt.NewState} (intensity: {evt.Intensity})");
        /// });
        /// </example>
        /// <summary>
        /// Example usage for publishing a relationship-impacting event:
        /// </summary>
        /// <example>
        /// EventBus.Instance.Publish(new RelationshipEventTrigger(
        ///     npcId: "npc_1",
        ///     targetId: "npc_2",
        ///     eventType: "combat_win",
        ///     eventScore: 20f,
        ///     context: "NPC 1 defeated NPC 2 in battle",
        ///     timestamp: DateTime.UtcNow
        /// ));
        /// </example>
    }
}