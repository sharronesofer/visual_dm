using System;
using VDM.Runtime.Events.Models;


namespace VDM.Runtime.Events.Services
{
    /// <summary>
    /// Interface for event dispatching functionality.
    /// Provides event publishing and subscription capabilities.
    /// </summary>
    public interface IEventDispatcher
    {
        /// <summary>
        /// Subscribe to events of a specific type
        /// </summary>
        /// <typeparam name="T">Event type to subscribe to</typeparam>
        /// <param name="handler">Handler function to call when event is published</param>
        void Subscribe<T>(Action<T> handler) where T : IEvent;

        /// <summary>
        /// Subscribe to events by type string
        /// </summary>
        /// <param name="eventType">Event type string to subscribe to</param>
        /// <param name="handler">Handler function to call when event is published</param>
        void Subscribe(string eventType, Action<IEvent> handler);

        /// <summary>
        /// Unsubscribe from events of a specific type
        /// </summary>
        /// <typeparam name="T">Event type to unsubscribe from</typeparam>
        /// <param name="handler">Handler function to remove</param>
        void Unsubscribe<T>(Action<T> handler) where T : IEvent;

        /// <summary>
        /// Unsubscribe from events by type string
        /// </summary>
        /// <param name="eventType">Event type string to unsubscribe from</param>
        /// <param name="handler">Handler function to remove</param>
        void Unsubscribe(string eventType, Action<IEvent> handler);

        /// <summary>
        /// Publish an event to all subscribers
        /// </summary>
        /// <typeparam name="T">Event type</typeparam>
        /// <param name="eventData">Event data to publish</param>
        void Publish<T>(T eventData) where T : IEvent;

        /// <summary>
        /// Clear all subscriptions
        /// </summary>
        void ClearAllSubscriptions();

        /// <summary>
        /// Clear subscriptions for a specific event type
        /// </summary>
        /// <param name="eventType">Event type to clear subscriptions for</param>
        void ClearSubscriptions(string eventType);

        /// <summary>
        /// Get the number of subscribers for a specific event type
        /// </summary>
        /// <param name="eventType">Event type to check</param>
        /// <returns>Number of subscribers</returns>
        int GetSubscriberCount(string eventType);
    }
} 