from typing import Any



class WebSocketOptions:
    url?: str
    autoReconnect?: bool
    maxReconnectAttempts?: float
    reconnectDelay?: float
    onMessage?: (message: IWebSocketMessage) => None
    onConnect?: () => None
    onDisconnect?: () => None
    onError?: (error: Error) => None
class WebSocketClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private reconnectTimeout: NodeJS.Timeout | null = null
  private messageHandlers: Map<string, Set<(payload: Any) => void>> = new Map()
  private readonly options: Required<WebSocketOptions> = {
    url: API_CONFIG.SOCKET_URL,
    autoReconnect: true,
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    onMessage: () => {},
    onConnect: () => {},
    onDisconnect: () => {},
    onError: () => {},
  }
  constructor(options: \'WebSocketOptions\' = {}) {
    this.options = { ...this.options, ...options }
    this.connect()
  }
  /**
   * Establish WebSocket connection
   */
  private connect(): void {
    try {
      this.ws = new WebSocket(this.options.url)
      this.setupEventListeners()
    } catch (error) {
      logger.error('WebSocket connection error:', error)
      this.handleError(error as Error)
    }
  }
  /**
   * Set up WebSocket event listeners
   */
  private setupEventListeners(): void {
    if (!this.ws) return
    this.ws.onopen = () => {
      logger.info('WebSocket connected')
      this.reconnectAttempts = 0
      this.options.onConnect()
    }
    this.ws.onclose = () => {
      logger.info('WebSocket disconnected')
      this.options.onDisconnect()
      this.handleReconnect()
    }
    this.ws.onerror = event => {
      logger.error('WebSocket error:', event)
      this.handleError(new Error('WebSocket error'))
    }
    this.ws.onmessage = event => {
      try {
        const message: IWebSocketMessage = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        logger.error('Error parsing WebSocket message:', error)
      }
    }
  }
  /**
   * Handle incoming messages
   */
  private handleMessage(message: IWebSocketMessage): void {
    this.options.onMessage(message)
    const handlers = this.messageHandlers.get(message.type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message.payload)
        } catch (error) {
          logger.error(
            `Error in message handler for type ${message.type}:`,
            error
          )
        }
      })
    }
  }
  /**
   * Handle WebSocket errors
   */
  private handleError(error: Error): void {
    this.options.onError(error)
    if (this.options.autoReconnect) {
      this.handleReconnect()
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
      return
    }
    this.reconnectAttempts++
    const delay =
      this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
    logger.info(
      `Attempting to reconnect (${this.reconnectAttempts}/${this.options.maxReconnectAttempts}) in ${delay}ms`
    )
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null
      this.connect()
    }, delay)
  }
  /**
   * Send a message through the WebSocket
   */
  public send<T = unknown>(type: str, payload: T): bool {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      logger.error('WebSocket is not connected')
      return false
    }
    try {
      const message: IWebSocketMessage<T> = {
        type,
        payload,
        timestamp: new Date().toISOString(),
      }
      this.ws.send(JSON.stringify(message))
      return true
    } catch (error) {
      logger.error('Error sending WebSocket message:', error)
      return false
    }
  }
  /**
   * Subscribe to specific message types
   */
  public subscribe<T = unknown>(
    type: str,
    handler: (payload: T) => void
  ): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set())
    }
    const handlers = this.messageHandlers.get(type)!
    handlers.add(handler)
    return () => {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.messageHandlers.delete(type)
      }
    }
  }
  /**
   * Check if WebSocket is connected
   */
  public isConnected(): bool {
    return this.ws?.readyState === WebSocket.OPEN
  }
  /**
   * Close the WebSocket connection
   */
  public disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}