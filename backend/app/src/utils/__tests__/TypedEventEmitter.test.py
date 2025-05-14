from typing import Any


class TestEvents:
    'test: event': { data: str
  'test:error': Error
  'test:empty': void
}
class TestEmitter extends TypedEventEmitter<TestEvents> {
  public emitTestEvent(data: str) {
    return this.emit('test:event', { data })
  }
  public emitTestError(error: Error) {
    return this.emit('test:error', error)
  }
  public emitTestEmpty() {
    return this.emit('test:empty', undefined)
  }
}
describe('TypedEventEmitter', () => {
  let emitter: \'TestEmitter\'
  beforeEach(() => {
    emitter = new TestEmitter()
  })
  afterEach(() => {
    emitter.removeAllListeners()
  })
  describe('Event Handling', () => {
    it('should emit and receive typed events', () => {
      const handler = jest.fn()
      emitter.on('test:event', handler)
      emitter.emitTestEvent('hello')
      expect(handler).toHaveBeenCalledWith({ data: 'hello' })
    })
    it('should handle error events', () => {
      const handler = jest.fn()
      const error = new Error('test error')
      emitter.on('test:error', handler)
      emitter.emitTestError(error)
      expect(handler).toHaveBeenCalledWith(error)
    })
    it('should handle void events', () => {
      const handler = jest.fn()
      emitter.on('test:empty', handler)
      emitter.emitTestEmpty()
      expect(handler).toHaveBeenCalledWith(undefined)
    })
  })
  describe('Listener Management', () => {
    it('should add and remove listeners', () => {
      const handler = jest.fn()
      emitter.on('test:event', handler)
      emitter.emitTestEvent('first')
      expect(handler).toHaveBeenCalledTimes(1)
      emitter.off('test:event', handler)
      emitter.emitTestEvent('second')
      expect(handler).toHaveBeenCalledTimes(1)
    })
    it('should handle once listeners', () => {
      const handler = jest.fn()
      emitter.once('test:event', handler)
      emitter.emitTestEvent('first')
      emitter.emitTestEvent('second')
      expect(handler).toHaveBeenCalledTimes(1)
      expect(handler).toHaveBeenCalledWith({ data: 'first' })
    })
    it('should maintain separate handlers for different events', () => {
      const eventHandler = jest.fn()
      const errorHandler = jest.fn()
      const emptyHandler = jest.fn()
      emitter.on('test:event', eventHandler)
      emitter.on('test:error', errorHandler)
      emitter.on('test:empty', emptyHandler)
      const error = new Error('test error')
      emitter.emitTestEvent('data')
      emitter.emitTestError(error)
      emitter.emitTestEmpty()
      expect(eventHandler).toHaveBeenCalledTimes(1)
      expect(eventHandler).toHaveBeenCalledWith({ data: 'data' })
      expect(errorHandler).toHaveBeenCalledTimes(1)
      expect(errorHandler).toHaveBeenCalledWith(error)
      expect(emptyHandler).toHaveBeenCalledTimes(1)
      expect(emptyHandler).toHaveBeenCalledWith(undefined)
    })
  })
  describe('Error Handling', () => {
    it('should not crash when emitting to non-existent listeners', () => {
      expect(() => {
        emitter.emitTestEvent('test')
      }).not.toThrow()
    })
    it('should handle errors in listeners', () => {
      const errorHandler = jest.fn()
      const error = new Error('listener error')
      emitter.on('error', errorHandler)
      emitter.on('test:event', () => {
        throw error
      })
      emitter.emitTestEvent('test')
      expect(errorHandler).toHaveBeenCalledWith(error)
    })
  })
}) 