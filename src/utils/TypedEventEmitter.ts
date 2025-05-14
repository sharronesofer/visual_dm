import { EventEmitter } from 'events';

/**
 * Type-safe EventEmitter base class that provides strongly-typed event handling
 * @template Events - Interface describing the events and their payload types
 * @example
 * ```typescript
 * interface MyEvents {
 *   'data': { id: string; value: number };
 *   'error': Error;
 *   'end': void;
 * }
 * 
 * class MyEmitter extends TypedEventEmitter<MyEvents> {
 *   process() {
 *     this.emit('data', { id: '1', value: 42 }); // Type-safe!
 *   }
 * }
 * ```
 */
export class TypedEventEmitter<Events extends Record<string | symbol, any>> extends EventEmitter {
  /**
   * Add a listener for a specific event
   * @param event - The event name to listen for
   * @param listener - The callback function that handles the event
   * @returns The instance of the emitter for chaining
   */
  public on<E extends keyof Events>(
    event: E,
    listener: Events[E] extends void ? () => void : (arg: Events[E]) => void
  ): this {
    return super.on(event as string, listener);
  }

  /**
   * Add a one-time listener for a specific event
   * @param event - The event name to listen for
   * @param listener - The callback function that handles the event (called only once)
   * @returns The instance of the emitter for chaining
   */
  public once<E extends keyof Events>(
    event: E,
    listener: Events[E] extends void ? () => void : (arg: Events[E]) => void
  ): this {
    return super.once(event as string, listener);
  }

  /**
   * Remove a specific listener for an event
   * @param event - The event name to remove the listener from
   * @param listener - The callback function to remove
   * @returns The instance of the emitter for chaining
   */
  public off<E extends keyof Events>(
    event: E,
    listener: Events[E] extends void ? () => void : (arg: Events[E]) => void
  ): this {
    return super.off(event as string, listener);
  }

  /**
   * Remove all listeners for a specific event or all events
   * @param event - Optional event name. If not provided, removes all listeners for all events
   * @returns The instance of the emitter for chaining
   */
  public removeAllListeners<E extends keyof Events>(event?: E): this {
    return super.removeAllListeners(event as string);
  }

  /**
   * Get all listeners for a specific event
   * @param event - The event name to get listeners for
   * @returns Array of listener functions
   */
  public listeners<E extends keyof Events>(event: E): Array<Events[E] extends void ? () => void : (arg: Events[E]) => void> {
    return super.listeners(event as string) as Array<Events[E] extends void ? () => void : (arg: Events[E]) => void>;
  }

  /**
   * Get raw listeners for a specific event (includes wrapped listeners)
   * @param event - The event name to get listeners for
   * @returns Array of raw listener functions
   */
  public rawListeners<E extends keyof Events>(event: E): Array<Events[E] extends void ? () => void : (arg: Events[E]) => void> {
    return super.rawListeners(event as string) as Array<Events[E] extends void ? () => void : (arg: Events[E]) => void>;
  }

  /**
   * Emit an event with a type-safe payload
   * @param event - The event name to emit
   * @param arg - The payload to send with the event (omitted for void events)
   * @returns true if the event had listeners, false otherwise
   */
  public emit<E extends keyof Events>(
    event: E,
    ...args: Events[E] extends void ? [] : [Events[E]]
  ): boolean {
    return super.emit(event as string, ...(args as [Events[E]]));
  }

  /**
   * Get the number of listeners for a specific event
   * @param event - The event name to count listeners for
   * @returns The number of listeners for the event
   */
  public listenerCount<E extends keyof Events>(event: E): number {
    return super.listenerCount(event as string);
  }

  /**
   * Get all event names that have registered listeners
   * @returns Array of event names
   */
  public eventNames(): Array<string | symbol> {
    return super.eventNames();
  }

  /**
   * Get the maximum number of listeners that can be registered for an event
   * @returns The maximum number of listeners
   */
  public getMaxListeners(): number {
    return super.getMaxListeners();
  }

  /**
   * Set the maximum number of listeners that can be registered for an event
   * @param n - The maximum number of listeners
   * @returns The instance of the emitter for chaining
   */
  public setMaxListeners(n: number): this {
    return super.setMaxListeners(n);
  }

  /**
   * Add a listener for a specific event at the beginning of the listeners array
   * @param event - The event name to listen for
   * @param listener - The callback function that handles the event
   * @returns The instance of the emitter for chaining
   */
  public prependListener<E extends keyof Events>(
    event: E,
    listener: Events[E] extends void ? () => void : (arg: Events[E]) => void
  ): this {
    return super.prependListener(event as string, listener);
  }

  /**
   * Add a one-time listener for a specific event at the beginning of the listeners array
   * @param event - The event name to listen for
   * @param listener - The callback function that handles the event (called only once)
   * @returns The instance of the emitter for chaining
   */
  public prependOnceListener<E extends keyof Events>(
    event: E,
    listener: Events[E] extends void ? () => void : (arg: Events[E]) => void
  ): this {
    return super.prependOnceListener(event as string, listener);
  }

  /**
   * Add a listener for multiple events
   * @param events - Object mapping event names to listener functions
   * @returns The instance of the emitter for chaining
   */
  public addListeners(events: {
    [E in keyof Events]?: Events[E] extends void ? () => void : (arg: Events[E]) => void;
  }): this {
    Object.entries(events).forEach(([event, listener]) => {
      if (listener) {
        this.on(event as keyof Events, listener);
      }
    });
    return this;
  }

  /**
   * Remove a listener for multiple events
   * @param events - Object mapping event names to listener functions
   * @returns The instance of the emitter for chaining
   */
  public removeListeners(events: {
    [E in keyof Events]?: Events[E] extends void ? () => void : (arg: Events[E]) => void;
  }): this {
    Object.entries(events).forEach(([event, listener]) => {
      if (listener) {
        this.off(event as keyof Events, listener);
      }
    });
    return this;
  }
} 