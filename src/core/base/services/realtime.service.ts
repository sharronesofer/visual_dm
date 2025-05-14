/**
 * Realtime service implementation
 * @module core/base/services/realtime
 */

import { BaseEntity } from '../types/entity';
import { BaseService } from './base.service';
import { IRealtimeService } from '../interfaces/realtime.interface';
import { ServiceEvent, ServiceEventHandler } from '../types/common';

/**
 * Abstract realtime service class that extends BaseService and implements IRealtimeService
 */
export abstract class RealtimeService<T extends BaseEntity> extends BaseService<T> implements IRealtimeService<T> {
  protected subscribers: Map<string, Set<ServiceEventHandler<T>>> = new Map();

  /**
   * Subscribe to entity events
   */
  subscribe(event: string, handler: ServiceEventHandler<T>): void {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, new Set());
    }
    this.subscribers.get(event)!.add(handler);
  }

  /**
   * Unsubscribe from entity events
   */
  unsubscribe(event: string, handler: ServiceEventHandler<T>): void {
    const handlers = this.subscribers.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.subscribers.delete(event);
      }
    }
  }

  /**
   * Emit an entity event
   */
  emit(event: ServiceEvent<T>): void {
    const handlers = this.subscribers.get(event.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(event);
        } catch (error) {
          console.error('Error in event handler:', error);
          this.handleError(error);
        }
      });
    }
  }

  /**
   * Get all current subscribers
   */
  getSubscribers(event?: string): ServiceEventHandler<T>[] {
    if (event) {
      const handlers = this.subscribers.get(event);
      return handlers ? Array.from(handlers) : [];
    }
    
    const allHandlers: ServiceEventHandler<T>[] = [];
    this.subscribers.forEach(handlers => {
      allHandlers.push(...Array.from(handlers));
    });
    return allHandlers;
  }

  /**
   * Check if there are any subscribers
   */
  hasSubscribers(event?: string): boolean {
    if (event) {
      const handlers = this.subscribers.get(event);
      return !!handlers && handlers.size > 0;
    }
    return this.subscribers.size > 0;
  }

  /**
   * Remove all subscribers
   */
  clearSubscribers(event?: string): void {
    if (event) {
      this.subscribers.delete(event);
    } else {
      this.subscribers.clear();
    }
  }

  /**
   * Helper method to safely emit events
   */
  protected safeEmit(event: ServiceEvent<T>): void {
    try {
      this.emit(event);
    } catch (error) {
      console.error('Error emitting event:', error);
      this.handleError(error);
    }
  }
} 