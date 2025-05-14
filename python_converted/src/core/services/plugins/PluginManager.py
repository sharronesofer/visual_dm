from typing import Any, Dict, List
from enum import Enum


class PluginType(Enum):
    MEDIA_PROCESSOR = 'media-processor'
    THUMBNAIL = 'thumbnail'
    CONVERTER = 'converter'
    METADATA = 'metadata'
class Plugin:
    name: str
    version: str
    type: \'PluginType\'
    initialize(): Awaitable[None>
    shutdown(): Awaitable[None>
class PluginConfig:
    enabled: bool
    options?: Dict[str, Any>
class PluginManager extends EventEmitter {
  private plugins: Map<string, ProcessingPlugin> = new Map()
  private configs: Map<string, PluginConfig> = new Map()
  private logger: Logger
  constructor() {
    super()
    this.logger = Logger.getInstance()
  }
  public async register(plugin: ProcessingPlugin, config?: PluginConfig): Promise<void> {
    try {
      this.validatePlugin(plugin)
      if (this.plugins.has(plugin.name)) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${plugin.name} is already registered`,
          { plugin }
        )
      }
      this.plugins.set(plugin.name, plugin)
      this.configs.set(plugin.name, config || { enabled: true })
      if (this.configs.get(plugin.name)?.enabled) {
        await plugin.initialize()
        this.emit('pluginInitialized', plugin)
      }
      this.emit('pluginRegistered', plugin)
    } catch (error) {
      throw new ServiceError(
        'PluginRegistrationError',
        `Failed to register plugin ${plugin.name}`,
        { plugin, error }
      )
    }
  }
  public async unregister(pluginName: str): Promise<void> {
    try {
      const plugin = this.plugins.get(pluginName)
      if (!plugin) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${pluginName} is not registered`,
          { pluginName }
        )
      }
      if (this.configs.get(pluginName)?.enabled) {
        await plugin.shutdown()
      }
      this.plugins.delete(pluginName)
      this.configs.delete(pluginName)
      this.emit('pluginUnregistered', plugin)
    } catch (error) {
      throw new ServiceError(
        'PluginUnregistrationError',
        `Failed to unregister plugin ${pluginName}`,
        { pluginName, error }
      )
    }
  }
  public async enablePlugin(pluginName: str): Promise<void> {
    try {
      const plugin = this.plugins.get(pluginName)
      const config = this.configs.get(pluginName)
      if (!plugin || !config) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${pluginName} is not registered`,
          { pluginName }
        )
      }
      if (!config.enabled) {
        await plugin.initialize()
        config.enabled = true
        this.emit('pluginEnabled', plugin)
      }
    } catch (error) {
      throw new ServiceError(
        'PluginEnableError',
        `Failed to enable plugin ${pluginName}`,
        { pluginName, error }
      )
    }
  }
  public async disablePlugin(pluginName: str): Promise<void> {
    try {
      const plugin = this.plugins.get(pluginName)
      const config = this.configs.get(pluginName)
      if (!plugin || !config) {
        throw new ServiceError(
          'PluginError',
          `Plugin ${pluginName} is not registered`,
          { pluginName }
        )
      }
      if (config.enabled) {
        await plugin.shutdown()
        config.enabled = false
        this.emit('pluginDisabled', plugin)
      }
    } catch (error) {
      throw new ServiceError(
        'PluginDisableError',
        `Failed to disable plugin ${pluginName}`,
        { pluginName, error }
      )
    }
  }
  public getPlugin(name: str): ProcessingPlugin | undefined {
    return this.plugins.get(name)
  }
  public getPluginConfig(pluginName: str): \'PluginConfig\' | undefined {
    return this.configs.get(pluginName)
  }
  public getPluginsByType(type: PluginType): ProcessingPlugin[] {
    return Array.from(this.plugins.values()).filter(plugin => plugin.type === type)
  }
  public async cleanupAll(): Promise<void> {
    const errors: List[Error] = []
    for (const [name, plugin] of this.plugins.entries()) {
      if (this.configs.get(name)?.enabled) {
        try {
          await plugin.cleanup()
        } catch (error) {
          errors.push(
            new ServiceError(
              'PluginCleanupError',
              `Failed to cleanup plugin ${name}`,
              { plugin, error }
            )
          )
        }
      }
    }
    this.plugins.clear()
    this.configs.clear()
    if (errors.length > 0) {
      throw new ServiceError(
        'PluginCleanupError',
        'Failed to cleanup one or more plugins',
        { errors }
      )
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
    )
  }
  public async loadPlugins(directory: str): Promise<ProcessingPlugin[]> {
    try {
      return Array.from(this.plugins.values())
    } catch (error) {
      throw new ServiceError('PluginLoadError', 'Failed to load plugins', { error })
    }
  }
  public getPlugins(): ProcessingPlugin[] {
    return Array.from(this.plugins.values())
  }
  public async shutdownPlugins(): Promise<void> {
    for (const plugin of this.plugins.values()) {
      try {
        await plugin.shutdown()
        this.logger.info(`Shutdown plugin: ${plugin.name}`)
      } catch (error) {
        this.logger.error(`Failed to shutdown plugin: ${plugin.name}`, error)
      }
    }
    this.plugins.clear()
  }
} 