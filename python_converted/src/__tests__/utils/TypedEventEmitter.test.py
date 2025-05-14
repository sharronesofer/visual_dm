from typing import Any, Dict


class TestEvents:
    stringEvent: str
    numberEvent: float
    objectEvent: Dict[str, Any]
describe('TypedEventEmitter', () => {
  let emitter: TypedEventEmitter<TestEvents>
  beforeEach(() => {
    emitter = new TypedEventEmitter<TestEvents>()
  })
  describe('Event Handling', () => {
    it('should emit and receive events with correct types', () => {
      const stringHandler = jest.fn()
      const numberHandler = jest.fn()
      const objectHandler = jest.fn()
      emitter.on('stringEvent', stringHandler)
      emitter.on('numberEvent', numberHandler)
      emitter.on('objectEvent', objectHandler)
      emitter.emit('stringEvent', 'test')
      emitter.emit('numberEvent', 42)
      emitter.emit('objectEvent', { id: '1', value: 100 })
      expect(stringHandler).toHaveBeenCalledWith('test')
      expect(numberHandler).toHaveBeenCalledWith(42)
      expect(objectHandler).toHaveBeenCalledWith({ id: '1', value: 100 })
    })
    it('should handle multiple listeners for the same event', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()
      emitter.on('stringEvent', handler1)
      emitter.on('stringEvent', handler2)
      emitter.emit('stringEvent', 'test')
      expect(handler1).toHaveBeenCalledWith('test')
      expect(handler2).toHaveBeenCalledWith('test')
    })
    it('should remove event listeners correctly', () => {
      const handler = jest.fn()
      emitter.on('stringEvent', handler)
      emitter.emit('stringEvent', 'test')
      expect(handler).toHaveBeenCalledTimes(1)
      emitter.off('stringEvent', handler)
      emitter.emit('stringEvent', 'test again')
      expect(handler).toHaveBeenCalledTimes(1)
    })
    it('should handle once listeners correctly', () => {
      const handler = jest.fn()
      emitter.once('numberEvent', handler)
      emitter.emit('numberEvent', 1)
      emitter.emit('numberEvent', 2)
      expect(handler).toHaveBeenCalledTimes(1)
      expect(handler).toHaveBeenCalledWith(1)
    })
  })
  describe('Error Handling', () => {
    it('should handle errors in event handlers', () => {
      const errorHandler = jest.fn()
      const error = new Error('Test error')
      emitter.on('error', errorHandler)
      emitter.emit('errorEvent', error)
      expect(errorHandler).toHaveBeenCalledWith(error)
    })
    it('should not throw when emitting to non-existent event', () => {
      expect(() => {
        emitter.emit('stringEvent', 'test')
      }).not.toThrow()
    })
  })
  describe('Utility Methods', () => {
    it('should return correct listener count', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()
      emitter.on('stringEvent', handler1)
      emitter.on('stringEvent', handler2)
      emitter.on('numberEvent', handler1)
      expect(emitter.listenerCount('stringEvent')).toBe(2)
      expect(emitter.listenerCount('numberEvent')).toBe(1)
    })
    it('should return all event names', () => {
      const handler = jest.fn()
      emitter.on('stringEvent', handler)
      emitter.on('numberEvent', handler)
      emitter.on('objectEvent', handler)
      const eventNames = emitter.eventNames()
      expect(eventNames).toHaveLength(3)
      expect(eventNames).toContain('stringEvent')
      expect(eventNames).toContain('numberEvent')
      expect(eventNames).toContain('objectEvent')
    })
    it('should remove all listeners correctly', () => {
      const handler1 = jest.fn()
      const handler2 = jest.fn()
      emitter.on('stringEvent', handler1)
      emitter.on('numberEvent', handler2)
      emitter.removeAllListeners()
      emitter.emit('stringEvent', 'test')
      emitter.emit('numberEvent', 42)
      expect(handler1).not.toHaveBeenCalled()
      expect(handler2).not.toHaveBeenCalled()
    })
  })
  describe('Type Safety', () => {
    it('should enforce type safety for event payloads', () => {
      emitter.emit('stringEvent', 42)
      emitter.emit('numberEvent', 'test')
      emitter.emit('objectEvent', { id: '1', wrongProp: true })
    })
    it('should enforce type safety for event handlers', () => {
      emitter.on('stringEvent', (arg) => arg.unknown())
      emitter.on('numberEvent', (arg) => arg.toString(16))
      emitter.on('stringEvent', (arg: str) => arg.toUpperCase())
      emitter.on('numberEvent', (arg: float) => arg.toString())
    })
  })
}) 