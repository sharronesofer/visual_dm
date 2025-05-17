import { TypedEventEmitter } from '../utils/TypedEventEmitter';

/**
 * Base event interface
 */
export interface BaseEvent {
  type: string;
  timestamp: number;
  source: string;
}

/**
 * System event types
 */
export enum SystemEventType {
  STARTUP = 'system:startup',
  SHUTDOWN = 'system:shutdown',
  ERROR = 'system:error',
  WARNING = 'system:warning',
  INFO = 'system:info'
}

/**
 * System event interface
 */
export interface SystemEvent extends BaseEvent {
  type: SystemEventType;
  details: {
    message: string;
    code?: string;
    [key: string]: any;
  };
}

/**
 * Service event types
 */
export enum ServiceEventType {
  CREATED = 'service:created',
  UPDATED = 'service:updated',
  DELETED = 'service:deleted',
  ERROR = 'service:error'
}

/**
 * Service event interface
 */
export interface ServiceEvent<T = any> extends BaseEvent {
  type: ServiceEventType;
  entityType: string;
  entityId: string | number;
  data?: T;
  metadata?: Record<string, any>;
}

/**
 * Media event types
 */
export enum MediaEventType {
  UPLOAD_START = 'media:upload:start',
  UPLOAD_PROGRESS = 'media:upload:progress',
  UPLOAD_COMPLETE = 'media:upload:complete',
  UPLOAD_ERROR = 'media:upload:error',
  PROCESS_START = 'media:process:start',
  PROCESS_PROGRESS = 'media:process:progress',
  PROCESS_COMPLETE = 'media:process:complete',
  PROCESS_ERROR = 'media:process:error'
}

/**
 * Media event interface
 */
export interface MediaEvent extends BaseEvent {
  type: MediaEventType;
  fileId: string;
  filename: string;
  progress?: {
    bytesProcessed: number;
    totalBytes: number;
    percent: number;
  };
  error?: Error;
  metadata?: Record<string, any>;
}

/**
 * Event handler type
 */
export type EventHandler<T extends BaseEvent> = (event: T) => void | Promise<void>;

/**
 * Event subscription options
 */
export interface EventSubscriptionOptions {
  once?: boolean;
  filter?: (event: BaseEvent) => boolean;
}

/**
 * --- Construction System Events ---
 */
export interface ConstructionStartEvent {
  type: 'construction:start';
  buildingId: string;
  duration: number;
  timestamp: number;
  source: string;
}

export interface ConstructionCancelEvent {
  type: 'construction:cancel';
  buildingId: string;
  timestamp: number;
  source: string;
}

export interface ConstructionProgressEvent {
  type: 'construction:progress';
  buildingId: string;
  progress: import('../../../systems/ConstructionProgressSystem').ConstructionProgress;
  timestamp: number;
  source: string;
}

export interface TickEvent {
  type: 'tick';
  timestamp: number;
  source: string;
}

export interface ConstructionValidationErrorEvent {
  type: 'construction:validationError';
  buildingId: string;
  errors: string[];
  timestamp: number;
  source: string;
}

export interface ConstructionCompleteEvent {
  type: 'construction:complete';
  buildingId: string;
  timestamp: number;
  source: string;
}

/**
 * Event map type
 */
export type EventMap = {
  [SystemEventType.STARTUP]: SystemEvent;
  [SystemEventType.SHUTDOWN]: SystemEvent;
  [SystemEventType.ERROR]: SystemEvent;
  [SystemEventType.WARNING]: SystemEvent;
  [SystemEventType.INFO]: SystemEvent;
  [ServiceEventType.CREATED]: ServiceEvent;
  [ServiceEventType.UPDATED]: ServiceEvent;
  [ServiceEventType.DELETED]: ServiceEvent;
  [ServiceEventType.ERROR]: ServiceEvent;
  [MediaEventType.UPLOAD_START]: MediaEvent;
  [MediaEventType.UPLOAD_PROGRESS]: MediaEvent;
  [MediaEventType.UPLOAD_COMPLETE]: MediaEvent;
  [MediaEventType.UPLOAD_ERROR]: MediaEvent;
  [MediaEventType.PROCESS_START]: MediaEvent;
  [MediaEventType.PROCESS_PROGRESS]: MediaEvent;
  [MediaEventType.PROCESS_COMPLETE]: MediaEvent;
  [MediaEventType.PROCESS_ERROR]: MediaEvent;
  'construction:start': ConstructionStartEvent;
  'construction:cancel': ConstructionCancelEvent;
  'construction:progress': ConstructionProgressEvent;
  'tick': TickEvent;
  'construction:validationError': ConstructionValidationErrorEvent;
  'construction:complete': ConstructionCompleteEvent;
};

/**
 * Event bus interface
 */
export interface IEventBus {
  emit<K extends keyof EventMap>(type: K, event: EventMap[K]): boolean;
  on<K extends keyof EventMap>(type: K, handler: (event: EventMap[K]) => void | Promise<void>): this;
  off<K extends keyof EventMap>(type: K, handler: (event: EventMap[K]) => void | Promise<void>): this;
  once<K extends keyof EventMap>(type: K, handler: (event: EventMap[K]) => void | Promise<void>): this;
}

/**
 * Event bus implementation
 */
export class EventBus extends TypedEventEmitter<EventMap> implements IEventBus {
  private static instance: EventBus;

  private constructor() {
    super();
    this.setMaxListeners(100); // Allow more listeners than the default 10
  }

  public static getInstance(): EventBus {
    if (!EventBus.instance) {
      EventBus.instance = new EventBus();
    }
    return EventBus.instance;
  }

  public emit<K extends keyof EventMap>(type: K, event: EventMap[K]): boolean {
    event.timestamp = Date.now();
    return super.emit(type, event);
  }

  public on<K extends keyof EventMap>(
    type: K,
    handler: (event: EventMap[K]) => void | Promise<void>,
    options: EventSubscriptionOptions = {}
  ): this {
    const wrappedHandler = (event: EventMap[K]) => {
      if (!options.filter || options.filter(event)) {
        handler(event);
      }
    };

    if (options.once) {
      return super.once(type, wrappedHandler);
    } else {
      return super.on(type, wrappedHandler);
    }
  }

  public off<K extends keyof EventMap>(
    type: K,
    handler: (event: EventMap[K]) => void | Promise<void>
  ): this {
    return super.off(type, handler);
  }

  public once<K extends keyof EventMap>(
    type: K,
    handler: (event: EventMap[K]) => void | Promise<void>
  ): this {
    return super.once(type, handler);
  }
} 