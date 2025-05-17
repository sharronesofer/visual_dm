using System;
using System.Threading.Tasks;
using UnityEngine;
using VisualDM.Core.EventChannels;

namespace VisualDM.Core
{
    /// <summary>
    /// Extension methods for the EventBus class to integrate with ScriptableObject event channels.
    /// </summary>
    public static class EventBusExtensions
    {
        /// <summary>
        /// Connect a void event channel to the event bus.
        /// </summary>
        /// <param name="eventBus">The event bus instance</param>
        /// <param name="eventChannel">The event channel to connect</param>
        /// <param name="eventType">The event type to publish when the channel is raised</param>
        /// <returns>An action that can be used to unsubscribe</returns>
        public static Action ConnectEventChannel(this EventBus eventBus, VoidEventChannelBase eventChannel, Type eventType)
        {
            Action handler = () => eventBus.Publish(eventType, null);
            eventChannel.Subscribe(handler);
            return () => eventChannel.Unsubscribe(handler);
        }
        
        /// <summary>
        /// Connect a typed event channel to the event bus.
        /// </summary>
        /// <typeparam name="T">The type of data the event channel sends</typeparam>
        /// <param name="eventBus">The event bus instance</param>
        /// <param name="eventChannel">The event channel to connect</param>
        /// <returns>An action that can be used to unsubscribe</returns>
        public static Action ConnectEventChannel<T>(this EventBus eventBus, EventChannelBase<T> eventChannel)
        {
            Action<T> handler = data => eventBus.Publish(data);
            eventChannel.Subscribe(handler);
            return () => eventChannel.Unsubscribe(handler);
        }
        
        /// <summary>
        /// Connect a typed event channel to the event bus, specifying a custom event type.
        /// </summary>
        /// <typeparam name="T">The type of data the event channel sends</typeparam>
        /// <typeparam name="TEvent">The type of event to publish</typeparam>
        /// <param name="eventBus">The event bus instance</param>
        /// <param name="eventChannel">The event channel to connect</param>
        /// <param name="converter">Converter function from T to TEvent</param>
        /// <returns>An action that can be used to unsubscribe</returns>
        public static Action ConnectEventChannel<T, TEvent>(this EventBus eventBus, EventChannelBase<T> eventChannel, Func<T, TEvent> converter)
        {
            Action<T> handler = data => eventBus.Publish(converter(data));
            eventChannel.Subscribe(handler);
            return () => eventChannel.Unsubscribe(handler);
        }
        
        /// <summary>
        /// Connect the event bus to an event channel, so the channel is raised when the event is published.
        /// </summary>
        /// <typeparam name="T">The type of data for both the event and channel</typeparam>
        /// <param name="eventBus">The event bus instance</param>
        /// <param name="eventChannel">The event channel to connect</param>
        /// <returns>An action that can be used to unsubscribe</returns>
        public static Action ConnectToEventChannel<T>(this EventBus eventBus, EventChannelBase<T> eventChannel)
        {
            Action<T> handler = data => eventChannel.RaiseEvent(data);
            eventBus.Subscribe(handler);
            return () => eventBus.Unsubscribe(handler);
        }
        
        /// <summary>
        /// Connect the event bus to a void event channel, so the channel is raised when a specific event type is published.
        /// </summary>
        /// <typeparam name="T">The type of the event to listen for</typeparam>
        /// <param name="eventBus">The event bus instance</param>
        /// <param name="eventChannel">The void event channel to connect</param>
        /// <returns>An action that can be used to unsubscribe</returns>
        public static Action ConnectToVoidEventChannel<T>(this EventBus eventBus, VoidEventChannelBase eventChannel)
        {
            Action<T> handler = _ => eventChannel.RaiseEvent();
            eventBus.Subscribe(handler);
            return () => eventBus.Unsubscribe(handler);
        }
        
        /// <summary>
        /// Publish an event to the event bus.
        /// </summary>
        /// <param name="eventBus">The event bus instance</param>
        /// <param name="eventType">The type of event to publish</param>
        /// <param name="eventData">The event data (can be null)</param>
        public static void Publish(this EventBus eventBus, Type eventType, object eventData)
        {
            // Use reflection to call the generic Publish method
            var method = typeof(EventBus).GetMethod("Publish");
            var genericMethod = method.MakeGenericMethod(eventType);
            genericMethod.Invoke(eventBus, new[] { eventData });
        }
        
        /// <summary>
        /// Publish an event to the event bus and wait for all async handlers to complete.
        /// </summary>
        /// <param name="eventBus">The event bus instance</param>
        /// <param name="eventType">The type of event to publish</param>
        /// <param name="eventData">The event data (can be null)</param>
        /// <returns>Task that completes when all async handlers have completed</returns>
        public static async Task PublishAsync(this EventBus eventBus, Type eventType, object eventData)
        {
            // Use reflection to call the generic PublishAsync method
            var method = typeof(EventBus).GetMethod("PublishAsync");
            var genericMethod = method.MakeGenericMethod(eventType);
            var task = (Task)genericMethod.Invoke(eventBus, new[] { eventData });
            await task;
        }
    }
} 