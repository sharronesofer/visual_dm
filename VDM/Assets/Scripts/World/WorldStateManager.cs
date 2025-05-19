using System;
using UnityEngine;
using VisualDM.World;

namespace VisualDM.World
{
    /// <summary>
    /// [DEPRECATED] Use WorldStateSystem instead. This is a thin wrapper for backward compatibility.
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

        // Delegates to WorldStateSystem
        public object GetState(string key) => WorldStateSystem.Instance.Get(key);
        public void SetState(string key, object value) => WorldStateSystem.Instance.Set(key, value);
        public bool HasState(string key) => WorldStateSystem.Instance.Get(key) != null;
        public void RemoveState(string key) => WorldStateSystem.Instance.Set(key, null);
        public event Action<string, object, object, long, int> OnStateChanged
        {
            add { WorldStateSystem.Instance.Subscribe((k, v, o, t, ver) => value(k, v, o, t, ver)); }
            remove { WorldStateSystem.Instance.Unsubscribe((k, v, o, t, ver) => value(k, v, o, t, ver)); }
        }
    }
} 