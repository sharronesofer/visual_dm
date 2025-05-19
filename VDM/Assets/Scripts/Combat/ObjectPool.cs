using System.Collections.Generic;
using UnityEngine;

namespace VDM.Combat
{
    /// <summary>
    /// Generic object pool for MonoBehaviour objects (e.g., effect icons).
    /// </summary>
    /// <typeparam name="T">Type of MonoBehaviour to pool.</typeparam>
    public class ObjectPool<T> : MonoBehaviour where T : MonoBehaviour
    {
        private readonly Queue<T> _pool = new();
        private T _prefab;
        private Transform _parent;

        /// <summary>
        /// Initializes the pool with a prefab and optional parent.
        /// </summary>
        public void Initialize(T prefab, int prewarmCount = 0, Transform parent = null)
        {
            _prefab = prefab;
            _parent = parent;
            for (int i = 0; i < prewarmCount; i++)
            {
                var obj = Instantiate(_prefab, _parent);
                obj.gameObject.SetActive(false);
                _pool.Enqueue(obj);
            }
        }

        /// <summary>
        /// Gets an object from the pool, or instantiates a new one if empty.
        /// </summary>
        public T Get()
        {
            if (_pool.Count > 0)
            {
                var obj = _pool.Dequeue();
                obj.gameObject.SetActive(true);
                return obj;
            }
            var newObj = Instantiate(_prefab, _parent);
            newObj.gameObject.SetActive(true);
            return newObj;
        }

        /// <summary>
        /// Releases an object back to the pool.
        /// </summary>
        public void Release(T obj)
        {
            obj.gameObject.SetActive(false);
            _pool.Enqueue(obj);
        }
    }
} 