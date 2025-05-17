using System;
using System.Collections.Concurrent;

namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Generic thread-safe object pool for reusable objects.
    /// </summary>
    public class ObjectPool<T> where T : class, new()
    {
        private readonly ConcurrentBag<T> pool = new ConcurrentBag<T>();
        private readonly Func<T> factory;

        public ObjectPool(Func<T> factory = null)
        {
            this.factory = factory ?? (() => new T());
        }

        /// <summary>
        /// Get an object from the pool, or create a new one if empty.
        /// </summary>
        public T Get()
        {
            if (pool.TryTake(out var item))
                return item;
            return factory();
        }

        /// <summary>
        /// Return an object to the pool.
        /// </summary>
        public void Return(T item)
        {
            pool.Add(item);
        }
    }
} 