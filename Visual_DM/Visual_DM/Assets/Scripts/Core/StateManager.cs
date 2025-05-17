using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Core
{
    /// <summary>
    /// Singleton for managing global game state at runtime. Supports storing and retrieving state by key.
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
            state[key] = value;
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
            if (state.ContainsKey(key))
                state.Remove(key);
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