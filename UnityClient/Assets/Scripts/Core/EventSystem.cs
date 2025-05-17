using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Core.EventChannels;

namespace VisualDM.Core
{
    /// <summary>
    /// Central access point for the event system, providing predefined events and utility methods.
    /// This class makes it easier to use the event system by providing a single entry point.
    /// </summary>
    public static class EventSystem
    {
        // Common event types used throughout the application
        public static class Events
        {
            // Scene management events
            public static class Scene
            {
                /// <summary>Request to load a scene by name</summary>
                public class LoadSceneRequested
                {
                    public string SceneName;
                    public bool Additive;
                    public Action OnComplete;
                }
                
                /// <summary>Notification that a scene has finished loading</summary>
                public class SceneLoaded
                {
                    public string SceneName;
                }
            }
            
            // UI events
            public static class UI
            {
                /// <summary>Request to show a UI panel</summary>
                public class ShowPanelRequested
                {
                    public string PanelId;
                    public Dictionary<string, object> Parameters;
                }
                
                /// <summary>Request to hide a UI panel</summary>
                public class HidePanelRequested
                {
                    public string PanelId;
                }
                
                /// <summary>Notification that the UI state has changed</summary>
                public class UIStateChanged
                {
                    public bool IsUIActive;
                    public string ActivePanel;
                }
            }
            
            // Game events
            public static class Game
            {
                /// <summary>Notification that the game state has changed</summary>
                public class GameStateChanged
                {
                    public string State;
                    public Dictionary<string, object> StateData;
                }
                
                /// <summary>Notification that the player has performed an action</summary>
                public class PlayerAction
                {
                    public string ActionType;
                    public Dictionary<string, object> ActionData;
                }
            }
        }
        
        /// <summary>
        /// Subscribe to an event of type T.
        /// </summary>
        /// <typeparam name="T">Type of event to subscribe to</typeparam>
        /// <param name="handler">Handler to call when the event is published</param>
        /// <param name="priority">Priority of the handler</param>
        /// <param name="filter">Optional filter function</param>
        /// <returns>Action that can be invoked to unsubscribe</returns>
        public static Action Subscribe<T>(Action<T> handler, EventPriority priority = EventPriority.Normal, Func<T, bool> filter = null)
        {
            EventBus.Instance.Subscribe(handler, priority, filter);
            return () => EventBus.Instance.Unsubscribe(handler);
        }
        
        /// <summary>
        /// Subscribe to an event of type T with an async handler.
        /// </summary>
        /// <typeparam name="T">Type of event to subscribe to</typeparam>
        /// <param name="handler">Async handler to call when the event is published</param>
        /// <param name="priority">Priority of the handler</param>
        /// <param name="filter">Optional filter function</param>
        /// <returns>Action that can be invoked to unsubscribe</returns>
        public static Action SubscribeAsync<T>(Func<T, System.Threading.Tasks.Task> handler, EventPriority priority = EventPriority.Normal, Func<T, bool> filter = null)
        {
            EventBus.Instance.SubscribeAsync(handler, priority, filter);
            return () => EventBus.Instance.UnsubscribeAsync(handler);
        }
        
        /// <summary>
        /// Publish an event to all subscribers.
        /// </summary>
        /// <typeparam name="T">Type of event to publish</typeparam>
        /// <param name="eventData">Event data to publish</param>
        public static void Publish<T>(T eventData)
        {
            EventBus.Instance.Publish(eventData);
        }
        
        /// <summary>
        /// Publish an event and wait for all async handlers to complete.
        /// </summary>
        /// <typeparam name="T">Type of event to publish</typeparam>
        /// <param name="eventData">Event data to publish</param>
        /// <returns>Task that completes when all async handlers have completed</returns>
        public static System.Threading.Tasks.Task PublishAsync<T>(T eventData)
        {
            return EventBus.Instance.PublishAsync(eventData);
        }
        
        /// <summary>
        /// Connect an event channel to the event system.
        /// </summary>
        /// <typeparam name="T">Type of data the event channel sends</typeparam>
        /// <param name="eventChannel">The event channel to connect</param>
        /// <returns>Action that can be invoked to disconnect</returns>
        public static Action ConnectEventChannel<T>(EventChannelBase<T> eventChannel)
        {
            return EventBus.Instance.ConnectEventChannel(eventChannel);
        }
        
        /// <summary>
        /// Connect the event system to an event channel.
        /// </summary>
        /// <typeparam name="T">Type of event to connect</typeparam>
        /// <param name="eventChannel">The event channel to connect to</param>
        /// <returns>Action that can be invoked to disconnect</returns>
        public static Action ConnectToEventChannel<T>(EventChannelBase<T> eventChannel)
        {
            return EventBus.Instance.ConnectToEventChannel(eventChannel);
        }
    }
} 