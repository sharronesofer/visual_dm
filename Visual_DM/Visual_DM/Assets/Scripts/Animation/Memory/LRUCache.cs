using System;
using System.Collections.Generic;

namespace Visual_DM.Animation.Memory
{
    /// <summary>
    /// Thread-safe LRU (Least Recently Used) cache for animation data.
    /// </summary>
    public class LRUCache<TKey, TValue>
    {
        private readonly int _capacity;
        private readonly Dictionary<TKey, LinkedListNode<CacheItem>> _cacheMap;
        private readonly LinkedList<CacheItem> _lruList;
        private readonly object _lock = new object();

        private class CacheItem
        {
            public TKey Key;
            public TValue Value;
        }

        public LRUCache(int capacity)
        {
            if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
            _capacity = capacity;
            _cacheMap = new Dictionary<TKey, LinkedListNode<CacheItem>>();
            _lruList = new LinkedList<CacheItem>();
        }

        public bool TryGet(TKey key, out TValue value)
        {
            lock (_lock)
            {
                if (_cacheMap.TryGetValue(key, out var node))
                {
                    _lruList.Remove(node);
                    _lruList.AddFirst(node);
                    value = node.Value.Value;
                    return true;
                }
                value = default;
                return false;
            }
        }

        public void AddOrUpdate(TKey key, TValue value)
        {
            lock (_lock)
            {
                if (_cacheMap.TryGetValue(key, out var node))
                {
                    node.Value.Value = value;
                    _lruList.Remove(node);
                    _lruList.AddFirst(node);
                }
                else
                {
                    if (_cacheMap.Count >= _capacity)
                    {
                        var last = _lruList.Last;
                        if (last != null)
                        {
                            _cacheMap.Remove(last.Value.Key);
                            _lruList.RemoveLast();
                        }
                    }
                    var cacheItem = new CacheItem { Key = key, Value = value };
                    var newNode = new LinkedListNode<CacheItem>(cacheItem);
                    _lruList.AddFirst(newNode);
                    _cacheMap[key] = newNode;
                }
            }
        }

        public bool Remove(TKey key)
        {
            lock (_lock)
            {
                if (_cacheMap.TryGetValue(key, out var node))
                {
                    _lruList.Remove(node);
                    _cacheMap.Remove(key);
                    return true;
                }
                return false;
            }
        }

        public int Count
        {
            get { lock (_lock) { return _cacheMap.Count; } }
        }
    }
} 