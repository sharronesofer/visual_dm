using System;
using UnityEngine;

namespace VDM.Systems {
    public class MemoryEventDispatcher : MonoBehaviour {
        private static MemoryEventDispatcher _instance;
        public static MemoryEventDispatcher Instance {
            get {
                if (_instance == null) {
                    var go = new GameObject("MemoryEventDispatcher");
                    _instance = go.AddComponent<MemoryEventDispatcher>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
        public event Action<Memory, string> OnMemoryEventGlobal;
        public void Dispatch(Memory memory, string eventType) {
            OnMemoryEventGlobal?.Invoke(memory, eventType);
        }
    }
} 