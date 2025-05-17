using System;
using System.Collections.Generic;
using System.Threading;

namespace Systems.Integration
{
    public class IntegrationEventBus
    {
        private static readonly Lazy<IntegrationEventBus> _instance = new Lazy<IntegrationEventBus>(() => new IntegrationEventBus());
        public static IntegrationEventBus Instance => _instance.Value;

        private readonly Dictionary<Type, List<Delegate>> _subscribers = new Dictionary<Type, List<Delegate>>();

        private IntegrationEventBus() { }

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

        public void Publish<T>(T message)
        {
            var type = typeof(T);
            if (_subscribers.ContainsKey(type))
            {
                foreach (var handler in _subscribers[type])
                {
                    ((Action<T>)handler)?.Invoke(message);
                }
            }
        }

        public void PublishWithRetry<T>(T message, int maxRetries = 3, int retryDelayMs = 100)
        {
            int attempt = 0;
            bool success = false;
            Exception lastException = null;
            while (attempt < maxRetries && !success)
            {
                try
                {
                    Publish(message);
                    success = true;
                }
                catch (Exception ex)
                {
                    lastException = ex;
                    IntegrationLogger.Log($"[EventBus] Publish failed (attempt {attempt + 1}): {ex.Message}", LogLevel.Warn);
                    Thread.Sleep(retryDelayMs);
                }
                attempt++;
            }
            if (!success && lastException != null)
            {
                IntegrationLogger.Log($"[EventBus] Publish ultimately failed after {maxRetries} attempts: {lastException.Message}", LogLevel.Error);
                IntegrationAlerting.Alert($"EventBus publish failure: {lastException.Message}", LogLevel.Error);
            }
        }
    }

    // Standardized message format
    public class IntegrationMessage
    {
        public string SourceSystem;
        public string TargetSystem;
        public string MessageType;
        public string Payload;
        public DateTime Timestamp;
    }
} 