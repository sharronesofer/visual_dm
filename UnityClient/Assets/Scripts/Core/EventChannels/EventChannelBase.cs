using System;
using UnityEngine;

namespace VisualDM.Core.EventChannels
{
    /// <summary>
    /// Base class for all event channels. Event channels are ScriptableObjects that
    /// make it easier to wire up events in the Unity editor.
    /// </summary>
    public abstract class EventChannelBase : ScriptableObject
    {
        /// <summary>
        /// Description of when the event channel should be used.
        /// </summary>
        [TextArea]
        [Tooltip("Describe when this event should be raised and what the payload contains")]
        public string Description;
    }
    
    /// <summary>
    /// Base class for event channels with a specific type.
    /// </summary>
    /// <typeparam name="T">Type of data this event channel will send</typeparam>
    public abstract class EventChannelBase<T> : EventChannelBase
    {
        /// <summary>
        /// Event that can be subscribed to from code.
        /// </summary>
        private event Action<T> OnEventRaised;
        
        /// <summary>
        /// Raise the event with the specified data.
        /// </summary>
        /// <param name="data">Data to pass to subscribers</param>
        public void RaiseEvent(T data)
        {
            if (OnEventRaised != null)
            {
                try
                {
                    OnEventRaised.Invoke(data);
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Error when raising event on {name}: {ex.Message}");
                }
            }
        }
        
        /// <summary>
        /// Subscribe to this event channel.
        /// </summary>
        /// <param name="listener">Method to call when the event is raised</param>
        public void Subscribe(Action<T> listener)
        {
            OnEventRaised += listener;
        }
        
        /// <summary>
        /// Unsubscribe from this event channel.
        /// </summary>
        /// <param name="listener">Method to remove from the event</param>
        public void Unsubscribe(Action<T> listener)
        {
            OnEventRaised -= listener;
        }
    }
    
    /// <summary>
    /// Base class for void event channels (events with no data).
    /// </summary>
    public abstract class VoidEventChannelBase : EventChannelBase
    {
        /// <summary>
        /// Event that can be subscribed to from code.
        /// </summary>
        private event Action OnEventRaised;
        
        /// <summary>
        /// Raise the event.
        /// </summary>
        public void RaiseEvent()
        {
            if (OnEventRaised != null)
            {
                try
                {
                    OnEventRaised.Invoke();
                }
                catch (Exception ex)
                {
                    Debug.LogError($"Error when raising event on {name}: {ex.Message}");
                }
            }
        }
        
        /// <summary>
        /// Subscribe to this event channel.
        /// </summary>
        /// <param name="listener">Method to call when the event is raised</param>
        public void Subscribe(Action listener)
        {
            OnEventRaised += listener;
        }
        
        /// <summary>
        /// Unsubscribe from this event channel.
        /// </summary>
        /// <param name="listener">Method to remove from the event</param>
        public void Unsubscribe(Action listener)
        {
            OnEventRaised -= listener;
        }
    }
} 