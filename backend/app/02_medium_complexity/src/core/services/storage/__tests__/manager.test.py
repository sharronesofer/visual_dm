from typing import Any, Dict



class MockStorageProvider implements StorageProvider {
  async save() { return { path: '', metadata: Dict[str, Any] }; }
  async read() { return Buffer.from(''); }
  async delete() { return true; }
  async exists() { return false; }
  async list() { return []; }
  async getMetadata() { return { name: '', mimeType: '', size: 0, createdAt: new Date(), modifiedAt: new Date() }; }
  getUrl() { return ''; }
  async copy() { return { path: '', metadata: Dict[str, Any] }; }
  async move() { return { path: '', metadata: Dict[str, Any] }; }
}
class InvalidProvider implements Partial<StorageProvider> {
  async save() { return { path: '', metadata: Dict[str, Any] }; }
}
describe('StorageManager', () => {
  let manager: StorageManager
  let provider: StorageProvider
  beforeEach(() => {
    manager = StorageManager.getInstance({ allowDefaultOverride: true })
    provider = new MockStorageProvider()
    const names = manager.getProviderNames()
    names.forEach(name => manager.unregister(name))
  })
  describe('getInstance', () => {
    it('should return the same instance', () => {
      const instance1 = StorageManager.getInstance()
      const instance2 = StorageManager.getInstance()
      expect(instance1).toBe(instance2)
    })
    it('should use default config values', () => {
      const manager = StorageManager.getInstance()
      const registration: ProviderRegistration = { provider, isDefault: true }
      expect(() => manager.register('test', registration)).not.toThrow()
    })
  })
  describe('register', () => {
    it('should register a provider', () => {
      const registration: ProviderRegistration = { provider }
      manager.register('test', registration)
      expect(manager.hasProvider('test')).toBe(true)
    })
    it('should set default provider when specified', () => {
      const registration: ProviderRegistration = { provider, isDefault: true }
      manager.register('test', registration)
      expect(manager.getDefaultProvider()).toBe(provider)
    })
    it('should throw on invalid provider name', () => {
      const registration: ProviderRegistration = { provider }
      expect(() => manager.register('', registration)).toThrow(StorageError)
    })
    it('should throw on duplicate provider', () => {
      const registration: ProviderRegistration = { provider }
      manager.register('test', registration)
      expect(() => manager.register('test', registration)).toThrow(StorageError)
    })
    it('should throw on invalid provider implementation', () => {
      const registration: ProviderRegistration = {
        provider: new InvalidProvider() as unknown as StorageProvider
      }
      expect(() => manager.register('test', registration)).toThrow(StorageError)
    })
    it('should throw when setting default provider if one exists and override not allowed', () => {
      const manager = StorageManager.getInstance({ allowDefaultOverride: false })
      const registration: ProviderRegistration = { provider, isDefault: true }
      manager.register('test1', registration)
      expect(() => manager.register('test2', { ...registration })).toThrow(StorageError)
    })
    it('should allow overriding default provider when configured', () => {
      const registration: ProviderRegistration = { provider, isDefault: true }
      const provider2 = new MockStorageProvider()
      manager.register('test1', registration)
      expect(() => manager.register('test2', { provider: provider2, isDefault: true })).not.toThrow()
      expect(manager.getDefaultProvider()).toBe(provider2)
    })
  })
  describe('unregister', () => {
    beforeEach(() => {
      manager.register('test', { provider })
    })
    it('should unregister a provider', () => {
      manager.unregister('test')
      expect(manager.hasProvider('test')).toBe(false)
    })
    it('should clear default provider when unregistering it', () => {
      manager.register('default', { provider, isDefault: true })
      manager.unregister('default')
      expect(() => manager.getDefaultProvider()).toThrow(StorageError)
    })
    it('should throw when unregistering non-existent provider', () => {
      expect(() => manager.unregister('missing')).toThrow(StorageError)
    })
  })
  describe('getProvider', () => {
    beforeEach(() => {
      manager.register('test', { provider })
    })
    it('should return provider by name', () => {
      expect(manager.getProvider('test')).toBe(provider)
    })
    it('should return default provider when no name specified', () => {
      manager.register('default', { provider, isDefault: true })
      expect(manager.getProvider()).toBe(provider)
    })
    it('should throw when provider not found', () => {
      expect(() => manager.getProvider('missing')).toThrow(StorageError)
    })
    it('should throw when no name provided and no default set', () => {
      expect(() => manager.getProvider()).toThrow(StorageError)
    })
  })
  describe('getDefaultProvider', () => {
    it('should return default provider', () => {
      manager.register('default', { provider, isDefault: true })
      expect(manager.getDefaultProvider()).toBe(provider)
    })
    it('should throw when no default provider set', () => {
      expect(() => manager.getDefaultProvider()).toThrow(StorageError)
    })
  })
  describe('setDefaultProvider', () => {
    beforeEach(() => {
      manager.register('test', { provider })
    })
    it('should set default provider', () => {
      manager.setDefaultProvider('test')
      expect(manager.getDefaultProvider()).toBe(provider)
    })
    it('should throw when provider not found', () => {
      expect(() => manager.setDefaultProvider('missing')).toThrow(StorageError)
    })
  })
  describe('getProviderNames', () => {
    it('should return all provider names', () => {
      manager.register('test1', { provider })
      manager.register('test2', { provider })
      expect(manager.getProviderNames().sort()).toEqual(['test1', 'test2'])
    })
    it('should return empty array when no providers registered', () => {
      expect(manager.getProviderNames()).toEqual([])
    })
  })
  describe('getProviderRegistration', () => {
    it('should return registration details', () => {
      const registration: ProviderRegistration = { provider, isDefault: true }
      manager.register('test', registration)
      expect(manager.getProviderRegistration('test')).toEqual(registration)
    })
    it('should return undefined for non-existent provider', () => {
      expect(manager.getProviderRegistration('missing')).toBeUndefined()
    })
  })
}) 