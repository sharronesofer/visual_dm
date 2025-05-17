using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Singleton manager for global world state variables.
    /// </summary>
    public class WorldStateManager : MonoBehaviour
    {
        private static WorldStateManager _instance;
        public static WorldStateManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("WorldStateManager");
                    _instance = go.AddComponent<WorldStateManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        [Serializable]
        public class StateChangeEvent : UnityEngine.Events.UnityEvent<string, object> { }

        [SerializeField] private Dictionary<string, object> worldState = new Dictionary<string, object>();
        public StateChangeEvent OnStateChanged = new StateChangeEvent();

        /// <summary>
        /// Gets a world state value by key.
        /// </summary>
        public object GetState(string key)
        {
            worldState.TryGetValue(key, out var value);
            return value;
        }

        /// <summary>
        /// Sets a world state value and notifies listeners.
        /// </summary>
        public void SetState(string key, object value)
        {
            worldState[key] = value;
            OnStateChanged.Invoke(key, value);
        }

        /// <summary>
        /// Checks if a world state key exists.
        /// </summary>
        public bool HasState(string key) => worldState.ContainsKey(key);

        /// <summary>
        /// Removes a world state key.
        /// </summary>
        public void RemoveState(string key)
        {
            if (worldState.Remove(key))
                OnStateChanged.Invoke(key, null);
        }
    }
} 