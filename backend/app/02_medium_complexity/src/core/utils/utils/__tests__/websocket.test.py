from typing import Any, Dict



class MockWebSocket {
  private listeners: Record<string, ((event: Any) => void)[]> = {
    open: [],
    close: [],
    error: [],
    message: [],
  }
  public readyState: float
  public onopen: ((event: Any) => void) | null = null
  public onclose: ((event: Any) => void) | null = null
  public onerror: ((event: Any) => void) | null = null
  public onmessage: ((event: Any) => void) | null = null
  constructor(public url: str) {
    this.readyState = MockWebSocket.CONNECTING
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN
      this.onopen?.({})
    }, 0)
  }
  addEventListener(event: str, callback: (event: Any) => void) {
    this.listeners[event] = this.listeners[event] || []
    this.listeners[event].push(callback)
  }
  removeEventListener(event: str, callback: (event: Any) => void) {
    const index = this.listeners[event]?.indexOf(callback)
    if (index !== undefined && index !== -1) {
      this.listeners[event].splice(index, 1)
    }
  }
  send(data: str) {
    const message = JSON.parse(data)
    this.onmessage?.({ data: JSON.stringify(message) })
  }
  close() {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.({})
  }
  emit(event: str, data?: Any) {
    switch (event) {
      case 'open':
        this.onopen?.(data)
        break
      case 'close':
        this.onclose?.(data)
        break
      case 'error':
        this.onerror?.(data)
        break
      case 'message':
        this.onmessage?.(data)
        break
    }
    this.listeners[event]?.forEach(callback => callback(data))
  }
  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3
}
global.WebSocket = MockWebSocket as any
vi.mock('../logger', () => ({
  logger: Dict[str, Any],
}))
describe('WebSocketClient', () => {
  let wsClient: WebSocketClient
  beforeEach(async () => {
    vi.clearAllMocks()
    wsClient = new WebSocketClient()
    await new Promise(resolve => setTimeout(resolve, 0))
  })
  afterEach(() => {
    wsClient.disconnect()
  })
  describe('Connection Management', () => {
    it('should connect to WebSocket server with default options', () => {
      const ws = (wsClient as any).ws as MockWebSocket
      expect(ws.url).toBe(API_CONFIG.SOCKET_URL)
      expect(wsClient.isConnected()).toBe(true)
      expect(logger.info).toHaveBeenCalledWith('WebSocket connected')
    })
    it('should connect to WebSocket server with custom URL', async () => {
      const customUrl = 'ws:
      wsClient = new WebSocketClient({ url: customUrl })
      await new Promise(resolve => setTimeout(resolve, 0))
      const ws = (wsClient as any).ws as MockWebSocket
      expect(ws.url).toBe(customUrl)
    })
    it('should handle connection errors', () => {
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('error', new Error('Connection failed'))
      expect(logger.error).toHaveBeenCalled()
    })
    it('should attempt reconnection on connection loss', () => {
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('close')
      expect(logger.info).toHaveBeenCalledWith('WebSocket disconnected')
    })
    it('should disconnect properly', () => {
      wsClient.disconnect()
      expect(wsClient.isConnected()).toBe(false)
    })
  })
  describe('Message Handling', () => {
    it('should send messages correctly', async () => {
      const ws = (wsClient as any).ws as MockWebSocket
      const spy = vi.spyOn(ws, 'send')
      const type = 'test-message'
      const payload = { data: 'test' }
      wsClient.send(type, payload)
      expect(spy).toHaveBeenCalledWith(
        expect.stringMatching(
          new RegExp(`"type":"${type}","payload":${JSON.stringify(payload)}`)
        )
      )
    })
    it('should handle incoming messages', () => {
      const handler = vi.fn()
      const type = 'test-message'
      const payload = { data: 'test' }
      wsClient.subscribe(type, handler)
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('message', {
        data: JSON.stringify({
          type,
          payload,
          timestamp: new Date().toISOString(),
        }),
      })
      expect(handler).toHaveBeenCalledWith(payload)
    })
    it('should handle message parsing errors', () => {
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('message', { data: 'invalid-json' })
      expect(logger.error).toHaveBeenCalledWith(
        'Error parsing WebSocket message:',
        expect.any(Error)
      )
    })
    it('should not send messages when disconnected', () => {
      wsClient.disconnect()
      const result = wsClient.send('test', { data: 'test' })
      expect(result).toBe(false)
      expect(logger.error).toHaveBeenCalledWith('WebSocket is not connected')
    })
  })
  describe('Subscription Management', () => {
    it('should manage message subscriptions', () => {
      const handler = vi.fn()
      const type = 'test-message'
      const payload = { data: 'test' }
      const unsubscribe = wsClient.subscribe(type, handler)
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('message', {
        data: JSON.stringify({
          type,
          payload,
          timestamp: new Date().toISOString(),
        }),
      })
      expect(handler).toHaveBeenCalledWith(payload)
      unsubscribe()
      ws.emit('message', {
        data: JSON.stringify({
          type,
          payload,
          timestamp: new Date().toISOString(),
        }),
      })
      expect(handler).toHaveBeenCalledTimes(1)
    })
    it('should handle multiple subscribers for the same message type', () => {
      const handler1 = vi.fn()
      const handler2 = vi.fn()
      const type = 'test-message'
      const payload = { data: 'test' }
      wsClient.subscribe(type, handler1)
      wsClient.subscribe(type, handler2)
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('message', {
        data: JSON.stringify({
          type,
          payload,
          timestamp: new Date().toISOString(),
        }),
      })
      expect(handler1).toHaveBeenCalledWith(payload)
      expect(handler2).toHaveBeenCalledWith(payload)
    })
  })
  describe('Error Handling', () => {
    it('should handle WebSocket errors', () => {
      const error = new Error('WebSocket error')
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('error', error)
      expect(logger.error).toHaveBeenCalledWith('WebSocket error:', error)
    })
    it('should handle message handler errors', () => {
      const handler = vi.fn().mockImplementation(() => {
        throw new Error('Handler error')
      })
      const type = 'test-message'
      const payload = { data: 'test' }
      wsClient.subscribe(type, handler)
      const ws = (wsClient as any).ws as MockWebSocket
      ws.emit('message', {
        data: JSON.stringify({
          type,
          payload,
          timestamp: new Date().toISOString(),
        }),
      })
      expect(logger.error).toHaveBeenCalledWith(
        'Error in message handler for type test-message:',
        expect.any(Error)
      )
    })
  })
})