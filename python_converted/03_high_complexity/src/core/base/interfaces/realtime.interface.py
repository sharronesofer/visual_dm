from typing import Any



/**
 * Realtime interface
 * @module core/base/interfaces/realtime
 */
/**
 * Interface for services that support realtime updates
 */
interface IRealtimeService<T extends BaseEntity> {
  /**
   * Subscribe to entity events
   * @param event Event type to subscribe to
   * @param handler Event handler function
   */
  subscribe(event: str, handler: ServiceEventHandler<T>): void
  /**
   * Unsubscribe from entity events
   * @param event Event type to unsubscribe from
   * @param handler Event handler function to remove
   */
  unsubscribe(event: str, handler: ServiceEventHandler<T>): void
  /**
   * Emit an entity event
   * @param event Event to emit
   */
  emit(event: ServiceEvent<T>): void
  /**
   * Get all current subscribers
   * @param event Optional event type to filter by
   */
  getSubscribers(event?: str): ServiceEventHandler<T>[]
  /**
   * Check if there are any subscribers
   * @param event Optional event type to check
   */
  hasSubscribers(event?: str): bool
  /**
   * Remove all subscribers
   * @param event Optional event type to clear
   */
  clearSubscribers(event?: str): void
} 