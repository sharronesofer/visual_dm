using System.Collections.Generic;
using UnityEngine;
using VisualDM.Systems.EventSystem;
using System;

namespace VisualDM.Core
{
    /// <summary>
    /// Singleton for managing global game state at runtime. Supports storing and retrieving state by key.
    /// Now publishes GameStateChangedEvent via EventBus for all state changes.
    /// </summary>
    public class StateManager : MonoBehaviour
    {
        private static StateManager _instance;
        public static StateManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("StateManager");
                    _instance = go.AddComponent<StateManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        private readonly Dictionary<string, object> state = new Dictionary<string, object>();
        private const string JwtTokenKey = "jwt_token";
        private const string UserRoleKey = "user_role";

        void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }

        public void Set<T>(string key, T value)
        {
            object oldValue = null;
            bool changed = false;
            if (state.TryGetValue(key, out var existing))
            {
                oldValue = existing;
                if (!(existing is T tExisting && EqualityComparer<T>.Default.Equals(tExisting, value)))
                {
                    state[key] = value;
                    changed = true;
                }
            }
            else
            {
                state[key] = value;
                changed = true;
            }
            if (changed)
            {
                var evt = new GameStateChangedEvent(
                    key,
                    value,
                    oldValue,
                    DateTime.UtcNow
                );
                EventBus.Instance.Publish(evt);
            }
        }

        public T Get<T>(string key, T defaultValue = default)
        {
            if (state.TryGetValue(key, out var value) && value is T tValue)
                return tValue;
            return defaultValue;
        }

        public bool Has(string key)
        {
            return state.ContainsKey(key);
        }

        public void Remove(string key)
        {
            if (state.TryGetValue(key, out var oldValue))
            {
                state.Remove(key);
                var evt = new GameStateChangedEvent(
                    key,
                    null,
                    oldValue,
                    DateTime.UtcNow
                );
                EventBus.Instance.Publish(evt);
            }
        }

        public void SetJwtToken(string token)
        {
            Set(JwtTokenKey, token);
        }

        public string GetJwtToken()
        {
            return Get<string>(JwtTokenKey, null);
        }

        public void SetUserRole(string role)
        {
            Set(UserRoleKey, role);
        }

        public string GetUserRole()
        {
            return Get<string>(UserRoleKey, null);
        }
    }
} 