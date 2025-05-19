using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading;

namespace VisualDM.Systems.Animation.Memory
{
    /// <summary>
    /// Generic, thread-safe object pool for animation system components.
    /// </summary>
    public class ObjectPool<T> where T : class, new()
    {
        private readonly ConcurrentBag<T> _objects;
        private int _count;
        private readonly int _maxSize;
        private readonly Func<T> _objectGenerator;

        public ObjectPool(int initialSize = 32, int maxSize = 1024, Func<T> objectGenerator = null)
        {
            _objects = new ConcurrentBag<T>();
            _maxSize = maxSize;
            _objectGenerator = objectGenerator ?? (() => new T());
            PreAllocate(initialSize);
        }

        private void PreAllocate(int count)
        {
            for (int i = 0; i < count; i++)
            {
                _objects.Add(_objectGenerator());
                Interlocked.Increment(ref _count);
            }
        }

        public T Rent()
        {
            if (_objects.TryTake(out T item))
            {
                Interlocked.Decrement(ref _count);
                return item;
            }
            return _objectGenerator();
        }

        public void Return(T item)
        {
            if (_count < _maxSize)
            {
                _objects.Add(item);
                Interlocked.Increment(ref _count);
            }
            // else: let GC collect if pool is full
        }

        public int Count => _count;
    }
} 