/**
 * Realtime interface
 * @module core/base/interfaces/realtime
 */

import { BaseEntity } from '../types/entity';
import { ServiceEvent, ServiceEventHandler } from '../types/common';

/**
 * Interface for services that support realtime updates
 */
export interface IRealtimeService<T extends BaseEntity> {
  /**
   * Subscribe to entity events
   * @param event Event type to subscribe to
   * @param handler Event handler function
   */
  subscribe(event: string, handler: ServiceEventHandler<T>): void;

  /**
   * Unsubscribe from entity events
   * @param event Event type to unsubscribe from
   * @param handler Event handler function to remove
   */
  unsubscribe(event: string, handler: ServiceEventHandler<T>): void;

  /**
   * Emit an entity event
   * @param event Event to emit
   */
  emit(event: ServiceEvent<T>): void;

  /**
   * Get all current subscribers
   * @param event Optional event type to filter by
   */
  getSubscribers(event?: string): ServiceEventHandler<T>[];

  /**
   * Check if there are any subscribers
   * @param event Optional event type to check
   */
  hasSubscribers(event?: string): boolean;

  /**
   * Remove all subscribers
   * @param event Optional event type to clear
   */
  clearSubscribers(event?: string): void;
} 