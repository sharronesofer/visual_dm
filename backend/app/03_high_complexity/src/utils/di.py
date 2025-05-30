from typing import Any, List



type Constructor<T = any> = new (...args: List[any]) => T
type Factory<T = any> = (...args: List[any]) => T
type Token<T = any> = Constructor<T> | string | symbol
class Container {
  private static instance: \'Container\'
  private dependencies: Map<Token, any>
  private factories: Map<Token, Factory>
  private logger: Logger
  private constructor() {
    this.dependencies = new Map()
    this.factories = new Map()
    this.logger = new Logger('Container')
  }
  static getInstance(): \'Container\' {
    if (!Container.instance) {
      Container.instance = new Container()
    }
    return Container.instance
  }
  register<T>(token: Token<T>, value: T): void {
    this.logger.debug(`Registering dependency: ${token.toString()}`)
    this.dependencies.set(token, value)
  }
  registerFactory<T>(token: Token<T>, factory: Factory<T>): void {
    this.logger.debug(`Registering factory: ${token.toString()}`)
    this.factories.set(token, factory)
  }
  get<T>(token: Token<T>): T {
    this.logger.debug(`Resolving dependency: ${token.toString()}`)
    const factory = this.factories.get(token)
    if (factory) {
      return factory()
    }
    const dependency = this.dependencies.get(token)
    if (dependency) {
      return dependency
    }
    if (typeof token === 'function') {
      try {
        const instance = new token()
        this.register(token, instance)
        return instance
      } catch (error) {
        this.logger.error(`Failed to instantiate dependency: ${token.toString()}`, { error })
        throw error
      }
    }
    throw new Error(`No dependency found for token: ${token.toString()}`)
  }
  clear(): void {
    this.logger.debug('Clearing all dependencies')
    this.dependencies.clear()
    this.factories.clear()
  }
}
const container = Container.getInstance()