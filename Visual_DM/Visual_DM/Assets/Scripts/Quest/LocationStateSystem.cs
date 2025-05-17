using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Quest
{
    /// <summary>
    /// Singleton system for tracking and updating the state of game locations.
    /// </summary>
    public class LocationStateSystem : MonoBehaviour
    {
        private static LocationStateSystem _instance;
        public static LocationStateSystem Instance
        {
            get
            {
                if (_instance == null)
                {
                    var go = new GameObject("LocationStateSystem");
                    _instance = go.AddComponent<LocationStateSystem>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }

        public enum LocationState { Normal, Endangered, Destroyed, Occupied, Hidden }

        [Serializable]
        public class LocationStateChangeEvent : UnityEngine.Events.UnityEvent<string, LocationState> { }

        [SerializeField] private Dictionary<string, LocationState> locationStates = new Dictionary<string, LocationState>();
        public LocationStateChangeEvent OnLocationStateChanged = new LocationStateChangeEvent();

        /// <summary>
        /// Gets the state of a location by id.
        /// </summary>
        public LocationState GetState(string locationId)
        {
            locationStates.TryGetValue(locationId, out var state);
            return state;
        }

        /// <summary>
        /// Sets the state of a location and notifies listeners.
        /// </summary>
        public void SetState(string locationId, LocationState state)
        {
            locationStates[locationId] = state;
            OnLocationStateChanged.Invoke(locationId, state);
        }

        /// <summary>
        /// Checks if a location has a tracked state.
        /// </summary>
        public bool HasState(string locationId) => locationStates.ContainsKey(locationId);
    }
} 