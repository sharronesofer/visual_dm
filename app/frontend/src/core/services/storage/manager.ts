import { StorageProvider, StorageError } from './interfaces';
import { Logger } from '../utils/logger';

/**
 * Storage provider registration options
 */
export interface ProviderRegistration {
  /** Provider instance */
  provider: StorageProvider;
  /** Whether this is the default provider */
  isDefault?: boolean;
  /** Provider-specific options */
  options?: Record<string, unknown>;
}

/**
 * Storage manager configuration
 */
export interface StorageManagerConfig {
  /** Whether to allow overwriting the default provider */
  allowDefaultOverride?: boolean;
  /** Whether to enable provider validation on registration */
  validateProviders?: boolean;
  /** Default timeout for provider operations (ms) */
  defaultTimeout?: number;
}

/**
 * Storage manager class for handling multiple storage providers
 */
export class StorageManager {
  private static instance: StorageManager;
  private readonly providers = new Map<string, ProviderRegistration>();
  private defaultProvider?: string;
  private readonly logger: Logger;

  private constructor(private readonly config: StorageManagerConfig = {}) {
    this.logger = Logger.getInstance().child('StorageManager');
    this.config = {
      allowDefaultOverride: false,
      validateProviders: true,
      defaultTimeout: 30000,
      ...config,
    };
  }

  /**
   * Get the storage manager instance (singleton)
   */
  public static getInstance(config?: StorageManagerConfig): StorageManager {
    if (!StorageManager.instance) {
      StorageManager.instance = new StorageManager(config);
    }
    return StorageManager.instance;
  }

  /**
   * Register a new storage provider
   */
  public register(name: string, registration: ProviderRegistration): void {
    this.logger.debug(`Registering provider: ${name}`, { isDefault: registration.isDefault });

    // Validate provider name
    if (!name || typeof name !== 'string') {
      throw new StorageError('Invalid provider name', 'INVALID_PROVIDER_NAME', name);
    }

    // Check for existing provider
    if (this.providers.has(name)) {
      throw new StorageError(`Provider already registered: ${name}`, 'PROVIDER_EXISTS', name);
    }

    // Validate provider implementation
    if (this.config.validateProviders) {
      this.validateProvider(registration.provider);
    }

    // Handle default provider
    if (registration.isDefault) {
      if (this.defaultProvider && !this.config.allowDefaultOverride) {
        throw new StorageError(
          'Default provider already set and override not allowed',
          'DEFAULT_PROVIDER_EXISTS',
          name
        );
      }
      this.defaultProvider = name;
    }

    // Register the provider
    this.providers.set(name, registration);
    this.logger.info(`Provider registered: ${name}`, { isDefault: registration.isDefault });
  }

  /**
   * Unregister a storage provider
   */
  public unregister(name: string): void {
    this.logger.debug(`Unregistering provider: ${name}`);

    if (!this.providers.has(name)) {
      throw new StorageError(`Provider not found: ${name}`, 'PROVIDER_NOT_FOUND', name);
    }

    if (this.defaultProvider === name) {
      this.defaultProvider = undefined;
    }

    this.providers.delete(name);
    this.logger.info(`Provider unregistered: ${name}`);
  }

  /**
   * Get a registered provider by name
   */
  public getProvider(name?: string): StorageProvider {
    const providerName = name || this.defaultProvider;

    if (!providerName) {
      throw new StorageError('No provider specified and no default provider set', 'NO_PROVIDER');
    }

    const registration = this.providers.get(providerName);
    if (!registration) {
      throw new StorageError(
        `Provider not found: ${providerName}`,
        'PROVIDER_NOT_FOUND',
        providerName
      );
    }

    return registration.provider;
  }

  /**
   * Get the default provider
   */
  public getDefaultProvider(): StorageProvider {
    if (!this.defaultProvider) {
      throw new StorageError('No default provider set', 'NO_DEFAULT_PROVIDER');
    }

    return this.getProvider(this.defaultProvider);
  }

  /**
   * Set the default provider
   */
  public setDefaultProvider(name: string): void {
    this.logger.debug(`Setting default provider: ${name}`);

    if (!this.providers.has(name)) {
      throw new StorageError(`Provider not found: ${name}`, 'PROVIDER_NOT_FOUND', name);
    }

    this.defaultProvider = name;
    this.logger.info(`Default provider set: ${name}`);
  }

  /**
   * Check if a provider is registered
   */
  public hasProvider(name: string): boolean {
    return this.providers.has(name);
  }

  /**
   * Get all registered provider names
   */
  public getProviderNames(): string[] {
    return Array.from(this.providers.keys());
  }

  /**
   * Get provider registration details
   */
  public getProviderRegistration(name: string): ProviderRegistration | undefined {
    return this.providers.get(name);
  }

  /**
   * Validate a provider implementation
   */
  private validateProvider(provider: StorageProvider): void {
    const requiredMethods = [
      'save',
      'read',
      'delete',
      'exists',
      'list',
      'getMetadata',
      'getUrl',
      'copy',
      'move',
    ] as const;

    for (const method of requiredMethods) {
      if (typeof (provider as any)[method] !== 'function') {
        throw new StorageError(
          `Invalid provider implementation: missing or invalid method '${method}'`,
          'INVALID_PROVIDER',
          method
        );
      }
    }
  }
}
