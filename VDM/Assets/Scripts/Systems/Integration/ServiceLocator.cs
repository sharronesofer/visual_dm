using System;
using System.Collections.Concurrent;

namespace Systems.Integration
{
    public class ServiceLocator
    {
        private static readonly Lazy<ServiceLocator> _instance = new Lazy<ServiceLocator>(() => new ServiceLocator());
        public static ServiceLocator Instance => _instance.Value;

        private readonly ConcurrentDictionary<Type, object> _services = new ConcurrentDictionary<Type, object>();

        private ServiceLocator() { }

        public void Register<T>(T service) where T : class
        {
            _services[typeof(T)] = service;
        }

        public T Get<T>() where T : class
        {
            if (_services.TryGetValue(typeof(T), out var service))
                return service as T;
            throw new InvalidOperationException($"Service of type {typeof(T)} is not registered.");
        }

        public bool TryGet<T>(out T service) where T : class
        {
            if (_services.TryGetValue(typeof(T), out var obj))
            {
                service = obj as T;
                return true;
            }
            service = null;
            return false;
        }
    }
} 