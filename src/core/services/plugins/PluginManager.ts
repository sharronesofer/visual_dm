import { EventEmitter } from 'events';
import { ServiceError } from '../base/types';
import { ProcessingPlugin } from '../types/MediaProcessing';
import { Logger } from '../utils/logger';
import * as fs from 'fs/promises';
import * as path from 'path';

export enum PluginType {
  MEDIA_PROCESSOR = 'media-processor',
  THUMBNAIL = 'thumbnail',
  CONVERTER = 'converter',
  METADATA = 'metadata'
}

export interface Plugin {
  name: string;
  version: string;
  type: PluginType;
  initialize(): Promise<void>;
  shutdown(): Promise<void>;
}

export interface PluginConfig {
  enabled: boolean;
  options?: Record<string, any>;
}

export class PluginManager extends EventEmitter {
  private plugins: Map<string, ProcessingPlugin> = new Map();
  private configs: Map<string, PluginConfig> = new Map();
  private logger: Logger;

  constructor() {
    super();
    this.logger = Logger.getInstance();
  }

  public async register(plugin: ProcessingPlugin, config?: PluginConfig): Promise<void> {
    try {
      // Validate plugin
      this.validatePlugin(plugin);

      // Check if plugin is already registered
      if (this.plugins.has(plugin.name)) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${plugin.name} is already registered`,
          { plugin }
        );
      }

      // Store plugin and config
      this.plugins.set(plugin.name, plugin);
      this.configs.set(plugin.name, config || { enabled: true });

      // Initialize plugin if enabled
      if (this.configs.get(plugin.name)?.enabled) {
        await plugin.initialize();
        this.emit('pluginInitialized', plugin);
      }

      this.emit('pluginRegistered', plugin);
    } catch (error) {
      throw new ServiceError(
        'PluginRegistrationError',
        `Failed to register plugin ${plugin.name}`,
        { plugin, error }
      );
    }
  }

  public async unregister(pluginName: string): Promise<void> {
    try {
      const plugin = this.plugins.get(pluginName);
      if (!plugin) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${pluginName} is not registered`,
          { pluginName }
        );
      }

      // Cleanup plugin if it was enabled
      if (this.configs.get(pluginName)?.enabled) {
        await plugin.shutdown();
      }

      // Remove plugin and config
      this.plugins.delete(pluginName);
      this.configs.delete(pluginName);

      this.emit('pluginUnregistered', plugin);
    } catch (error) {
      throw new ServiceError(
        'PluginUnregistrationError',
        `Failed to unregister plugin ${pluginName}`,
        { pluginName, error }
      );
    }
  }

  public async enablePlugin(pluginName: string): Promise<void> {
    try {
      const plugin = this.plugins.get(pluginName);
      const config = this.configs.get(pluginName);

      if (!plugin || !config) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${pluginName} is not registered`,
          { pluginName }
        );
      }

      if (!config.enabled) {
        await plugin.initialize();
        config.enabled = true;
        this.emit('pluginEnabled', plugin);
      }
    } catch (error) {
      throw new ServiceError(
        'PluginEnableError',
        `Failed to enable plugin ${pluginName}`,
        { pluginName, error }
      );
    }
  }

  public async disablePlugin(pluginName: string): Promise<void> {
    try {
      const plugin = this.plugins.get(pluginName);
      const config = this.configs.get(pluginName);

      if (!plugin || !config) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${pluginName} is not registered`,
          { pluginName }
        );
      }

      if (config.enabled) {
        await plugin.shutdown();
        config.enabled = false;
        this.emit('pluginDisabled', plugin);
      }
    } catch (error) {
      throw new ServiceError(
        'PluginDisableError',
        `Failed to disable plugin ${pluginName}`,
        { pluginName, error }
      );
    }
  }

  public getPlugin(name: string): ProcessingPlugin | undefined {
    return this.plugins.get(name);
  }

  public getPluginConfig(pluginName: string): PluginConfig | undefined {
    return this.configs.get(pluginName);
  }

  public getPluginsByType(type: PluginType): ProcessingPlugin[] {
    return Array.from(this.plugins.values()).filter(plugin => plugin.type === type);
  }

  public async cleanupAll(): Promise<void> {
    const errors: Error[] = [];

    // Attempt to cleanup all enabled plugins
    for (const [name, plugin] of this.plugins.entries()) {
      if (this.configs.get(name)?.enabled) {
        try {
          await plugin.cleanup();
        } catch (error) {
          errors.push(
            new ServiceError(
              'PluginCleanupError',
              `Failed to cleanup plugin ${name}`,
              { plugin, error }
            )
          );
        }
      }
    }

    // Clear all plugins and configs
    this.plugins.clear();
    this.configs.clear();

    // If any cleanups failed, throw an error with details
    if (errors.length > 0) {
      throw new ServiceError(
        'PluginCleanupError',
        'Failed to cleanup one or more plugins',
        { errors }
      );
    }
  }

  private validatePlugin(plugin: unknown): plugin is ProcessingPlugin {
    return (
      plugin !== null &&
      typeof plugin === 'object' &&
      'name' in plugin &&
      typeof (plugin as ProcessingPlugin).name === 'string' &&
      'version' in plugin &&
      typeof (plugin as ProcessingPlugin).version === 'string' &&
      'type' in plugin &&
      typeof (plugin as ProcessingPlugin).type === 'string' &&
      Object.values(PluginType).includes((plugin as ProcessingPlugin).type) &&
      'initialize' in plugin &&
      typeof (plugin as ProcessingPlugin).initialize === 'function' &&
      'shutdown' in plugin &&
      typeof (plugin as ProcessingPlugin).shutdown === 'function'
    );
  }

  public async loadPlugins(directory: string): Promise<ProcessingPlugin[]> {
    try {
      // Implementation will be added in a separate task
      // For now, return an empty array
      return Array.from(this.plugins.values());
    } catch (error) {
      throw new ServiceError('PluginLoadError', 'Failed to load plugins', { error });
    }
  }

  public getPlugins(): ProcessingPlugin[] {
    return Array.from(this.plugins.values());
  }

  public async shutdownPlugins(): Promise<void> {
    for (const plugin of this.plugins.values()) {
      try {
        await plugin.shutdown();
        this.logger.info(`Shutdown plugin: ${plugin.name}`);
      } catch (error) {
        this.logger.error(`Failed to shutdown plugin: ${plugin.name}`, error);
      }
    }
    this.plugins.clear();
  }
} 