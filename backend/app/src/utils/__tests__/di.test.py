from typing import Any


class TestService {
  getValue(): str {
    return 'test'
  }
}
class DependentService {
  constructor(private testService: TestService) {}
  getTestValue(): str {
    return this.testService.getValue()
  }
}
describe('Container', () => {
  beforeEach(() => {
    container.clear()
  })
  describe('getInstance', () => {
    it('should return the same instance', () => {
      const instance1 = Container.getInstance()
      const instance2 = Container.getInstance()
      expect(instance1).toBe(instance2)
    })
  })
  describe('register and get', () => {
    it('should register and retrieve a value', () => {
      const testService = new TestService()
      container.register(TestService, testService)
      expect(container.get(TestService)).toBe(testService)
    })
    it('should register and retrieve a value by string token', () => {
      const testService = new TestService()
      container.register('testService', testService)
      expect(container.get('testService')).toBe(testService)
    })
    it('should register and retrieve a value by symbol token', () => {
      const token = Symbol('test')
      const testService = new TestService()
      container.register(token, testService)
      expect(container.get(token)).toBe(testService)
    })
    it('should throw error when dependency not found', () => {
      expect(() => container.get('nonexistent')).toThrow('No dependency found for token: nonexistent')
    })
    it('should create new instance if token is constructor', () => {
      const instance = container.get(TestService)
      expect(instance).toBeInstanceOf(TestService)
      expect(instance.getValue()).toBe('test')
    })
  })
  describe('registerFactory', () => {
    it('should register and use a factory function', () => {
      const factory = () => new TestService()
      container.registerFactory(TestService, factory)
      const instance = container.get(TestService)
      expect(instance).toBeInstanceOf(TestService)
      expect(instance.getValue()).toBe('test')
    })
    it('should create new instance on each factory call', () => {
      const factory = () => new TestService()
      container.registerFactory(TestService, factory)
      const instance1 = container.get(TestService)
      const instance2 = container.get(TestService)
      expect(instance1).not.toBe(instance2)
    })
  })
  describe('clear', () => {
    it('should remove all registered dependencies', () => {
      const testService = new TestService()
      container.register(TestService, testService)
      container.clear()
      expect(() => container.get(TestService)).toThrow()
    })
    it('should remove all registered factories', () => {
      const factory = () => new TestService()
      container.registerFactory(TestService, factory)
      container.clear()
      expect(() => container.get(TestService)).toThrow()
    })
  })
}) 