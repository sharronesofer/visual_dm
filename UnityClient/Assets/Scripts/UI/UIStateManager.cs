using UnityEngine;
using System;
using System.Collections.Generic;

namespace VisualDM.UI
{
    /// <summary>
    /// Manages UI state across the application.
    /// This is similar to React's useState and Context API.
    /// </summary>
    public class UIStateManager : MonoBehaviour
    {
        // Singleton instance
        private static UIStateManager _instance;
        public static UIStateManager Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("UIStateManager");
                    _instance = go.AddComponent<UIStateManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
        
        // Dictionary to store state values by key
        private Dictionary<string, object> stateValues = new Dictionary<string, object>();
        
        // Dictionary to store state change callbacks
        private Dictionary<string, List<Action<object>>> stateChangeCallbacks = 
            new Dictionary<string, List<Action<object>>>();
            
        private void Awake()
        {
            // Ensure singleton behavior
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }
        
        /// <summary>
        /// Get a state value by key. Similar to accessing React context.
        /// </summary>
        public T GetState<T>(string key, T defaultValue = default)
        {
            if (stateValues.TryGetValue(key, out object value) && value is T typedValue)
            {
                return typedValue;
            }
            
            return defaultValue;
        }
        
        /// <summary>
        /// Set a state value by key. Similar to React's setState.
        /// </summary>
        public void SetState<T>(string key, T value)
        {
            bool valueChanged = false;
            
            // Check if the value has changed
            if (stateValues.TryGetValue(key, out object currentValue))
            {
                if (currentValue == null && value == null)
                {
                    valueChanged = false;
                }
                else if (currentValue == null || !currentValue.Equals(value))
                {
                    valueChanged = true;
                }
            }
            else
            {
                valueChanged = true;
            }
            
            // Update the value
            stateValues[key] = value;
            
            // Notify listeners if the value changed
            if (valueChanged && stateChangeCallbacks.TryGetValue(key, out var callbacks))
            {
                foreach (var callback in callbacks)
                {
                    callback?.Invoke(value);
                }
            }
        }
        
        /// <summary>
        /// Subscribe to state changes. Similar to React's useEffect.
        /// </summary>
        public void SubscribeToState(string key, Action<object> callback)
        {
            if (!stateChangeCallbacks.TryGetValue(key, out var callbacks))
            {
                callbacks = new List<Action<object>>();
                stateChangeCallbacks[key] = callbacks;
            }
            
            callbacks.Add(callback);
            
            // Immediately invoke with current value if it exists
            if (stateValues.TryGetValue(key, out object value))
            {
                callback?.Invoke(value);
            }
        }
        
        /// <summary>
        /// Unsubscribe from state changes. Similar to React's useEffect cleanup.
        /// </summary>
        public void UnsubscribeFromState(string key, Action<object> callback)
        {
            if (stateChangeCallbacks.TryGetValue(key, out var callbacks))
            {
                callbacks.Remove(callback);
                
                if (callbacks.Count == 0)
                {
                    stateChangeCallbacks.Remove(key);
                }
            }
        }
        
        /// <summary>
        /// Helper method to create a state hook within a MonoBehaviour.
        /// Use this to mimic React's useState hook.
        /// </summary>
        public static StateHook<T> UseState<T>(MonoBehaviour component, string key, T initialValue = default)
        {
            return new StateHook<T>(component, key, initialValue);
        }
        
        /// <summary>
        /// Helper class that mimics React's useState hook
        /// </summary>
        public class StateHook<T>
        {
            private readonly string key;
            private readonly MonoBehaviour component;
            private Action<T> onChange;
            
            public StateHook(MonoBehaviour component, string key, T initialValue = default)
            {
                this.key = key;
                this.component = component;
                
                // Initialize with default value if not already set
                if (!Instance.stateValues.ContainsKey(key))
                {
                    Instance.SetState(key, initialValue);
                }
                
                // Setup auto-cleanup when component is destroyed
                var cleanupBehavior = component.gameObject.AddComponent<StateHookCleanup>();
                cleanupBehavior.Initialize(this);
            }
            
            /// <summary>
            /// Get the current value
            /// </summary>
            public T Value
            {
                get => Instance.GetState<T>(key);
                set => Instance.SetState(key, value);
            }
            
            /// <summary>
            /// Subscribe to value changes
            /// </summary>
            public void Subscribe(Action<T> callback)
            {
                onChange = callback;
                Instance.SubscribeToState(key, value => onChange?.Invoke((T)value));
            }
            
            /// <summary>
            /// Unsubscribe from value changes
            /// </summary>
            public void Unsubscribe()
            {
                if (onChange != null)
                {
                    Instance.UnsubscribeFromState(key, value => onChange?.Invoke((T)value));
                    onChange = null;
                }
            }
            
            /// <summary>
            /// Helper component to automatically clean up subscriptions
            /// </summary>
            private class StateHookCleanup : MonoBehaviour
            {
                private StateHook<T> hook;
                
                public void Initialize(StateHook<T> hook)
                {
                    this.hook = hook;
                }
                
                private void OnDestroy()
                {
                    hook?.Unsubscribe();
                }
            }
        }
    }
} 