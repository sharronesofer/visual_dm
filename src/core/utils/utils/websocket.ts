import { API_CONFIG } from '../constants/api';
import { IWebSocketMessage } from '../types/api';
import { logger } from './logger';

interface WebSocketOptions {
  url?: string;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
  reconnectDelay?: number;
  onMessage?: (message: IWebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
}

// --- Event Replay and State Resynchronization Logic ---

const LAST_EVENT_ID_KEY = 'last_event_id';
const LAST_EVENT_TIMESTAMP_KEY = 'last_event_timestamp';
const USER_ID_KEY = 'user_id'; // Integration point: set this after login/auth

function getLastEventId(): number | null {
  const val = localStorage.getItem(LAST_EVENT_ID_KEY);
  return val ? parseInt(val, 10) : null;
}
function setLastEventId(id: number) {
  localStorage.setItem(LAST_EVENT_ID_KEY, id.toString());
}
function getLastEventTimestamp(): string | null {
  return localStorage.getItem(LAST_EVENT_TIMESTAMP_KEY);
}
function setLastEventTimestamp(ts: string) {
  localStorage.setItem(LAST_EVENT_TIMESTAMP_KEY, ts);
}
function getUserId(): string | null {
  return localStorage.getItem(USER_ID_KEY);
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, Set<(payload: any) => void>> = new Map();

  private readonly options: Required<WebSocketOptions> = {
    url: API_CONFIG.SOCKET_URL,
    autoReconnect: true,
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    onMessage: () => { },
    onConnect: () => { },
    onDisconnect: () => { },
    onError: () => { },
  };

  constructor(options: WebSocketOptions = {}) {
    this.options = { ...this.options, ...options };
    this.connect();
  }

  /**
   * Establish WebSocket connection
   */
  private connect(): void {
    try {
      this.ws = new WebSocket(this.options.url);
      this.setupEventListeners();
    } catch (error) {
      logger.error('WebSocket connection error:', error);
      this.handleError(error as Error);
    }
  }

  /**
   * Set up WebSocket event listeners
   */
  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      logger.info('WebSocket connected');
      this.reconnectAttempts = 0;
      this.options.onConnect();
      // --- On reconnect, send replay request ---
      const user_id = getUserId();
      const last_event_id = getLastEventId();
      const last_seen = getLastEventTimestamp();
      if (user_id) {
        this.send('reconnect', {
          user_id,
          last_event_id,
          last_seen,
        });
      }
    };

    this.ws.onclose = () => {
      logger.info('WebSocket disconnected');
      this.options.onDisconnect();
      this.handleReconnect();
    };

    this.ws.onerror = event => {
      logger.error('WebSocket error');
      this.handleError(new Error('WebSocket error'));
    };

    this.ws.onmessage = event => {
      try {
        const message: IWebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        logger.error('Error parsing WebSocket message:', error);
      }
    };
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: IWebSocketMessage): void {
    // --- Handle replay and state resync messages ---
    if (message.type === 'initial_state') {
      // Integration point: apply snapshot to local state
      // Example: EventBus.getInstance().applySnapshot(message.payload)
      setLastEventTimestamp(message.payload.timestamp || new Date().toISOString());
      setLastEventId(0); // Reset event ID if needed
      logger.info('Applied initial state snapshot from server');
      return;
    }
    if (message.type === 'event') {
      // Integration point: apply event to local state
      // Example: EventBus.getInstance().emit(message.payload)
      if (message.payload.event_id) {
        setLastEventId(message.payload.event_id);
      }
      if (message.payload.timestamp) {
        setLastEventTimestamp(message.payload.timestamp);
      }
      logger.info('Applied replayed event from server', message.payload);
      return;
    }
    // Call the general message handler
    this.options.onMessage(message);

    // Call specific handlers for the message type
    const handlers = this.messageHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.payload);
        } catch (error) {
          logger.error(
            `Error in message handler for type ${message.type}:`,
            error
          );
        }
      });
    }
  }

  /**
   * Handle WebSocket errors
   */
  private handleError(error: Error): void {
    this.options.onError(error);
    if (this.options.autoReconnect) {
      this.handleReconnect();
    }
  }

  /**
   * Handle reconnection logic
   */
  private handleReconnect(): void {
    if (
      !this.options.autoReconnect ||
      this.reconnectAttempts >= this.options.maxReconnectAttempts ||
      this.reconnectTimeout
    ) {
      return;
    }

    this.reconnectAttempts++;
    const delay =
      this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    logger.info(
      `Attempting to reconnect (${this.reconnectAttempts}/${this.options.maxReconnectAttempts}) in ${delay}ms`
    );

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect();
    }, delay);
  }

  /**
   * Send a message through the WebSocket
   */
  public send<T = unknown>(type: string, payload: T): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      logger.error('WebSocket is not connected');
      return false;
    }

    try {
      const message: IWebSocketMessage<T> = {
        type,
        payload,
        timestamp: new Date().toISOString(),
      };

      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      logger.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  /**
   * Subscribe to specific message types
   */
  public subscribe<T = unknown>(
    type: string,
    handler: (payload: T) => void
  ): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }

    const handlers = this.messageHandlers.get(type)!;
    handlers.add(handler);

    // Return unsubscribe function
    return () => {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.messageHandlers.delete(type);
      }
    };
  }

  /**
   * Check if WebSocket is connected
   */
  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Close the WebSocket connection
   */
  public disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
