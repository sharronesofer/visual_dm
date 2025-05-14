import { Logger } from './logger';

export type Constructor<T = any> = new (...args: any[]) => T;
export type Factory<T = any> = (...args: any[]) => T;
export type Token<T = any> = Constructor<T> | string | symbol;

export class Container {
  private static instance: Container;
  private dependencies: Map<Token, any>;
  private factories: Map<Token, Factory>;
  private logger: Logger;

  private constructor() {
    this.dependencies = new Map();
    this.factories = new Map();
    this.logger = new Logger('Container');
  }

  static getInstance(): Container {
    if (!Container.instance) {
      Container.instance = new Container();
    }
    return Container.instance;
  }

  register<T>(token: Token<T>, value: T): void {
    this.logger.debug(`Registering dependency: ${token.toString()}`);
    this.dependencies.set(token, value);
  }

  registerFactory<T>(token: Token<T>, factory: Factory<T>): void {
    this.logger.debug(`Registering factory: ${token.toString()}`);
    this.factories.set(token, factory);
  }

  get<T>(token: Token<T>): T {
    this.logger.debug(`Resolving dependency: ${token.toString()}`);

    // Check for factory first
    const factory = this.factories.get(token);
    if (factory) {
      return factory();
    }

    // Then check for singleton instance
    const dependency = this.dependencies.get(token);
    if (dependency) {
      return dependency;
    }

    // If token is a constructor, create new instance
    if (typeof token === 'function') {
      try {
        const instance = new token();
        this.register(token, instance);
        return instance;
      } catch (error) {
        this.logger.error(`Failed to instantiate dependency: ${token.toString()}`, { error });
        throw error;
      }
    }

    throw new Error(`No dependency found for token: ${token.toString()}`);
  }

  clear(): void {
    this.logger.debug('Clearing all dependencies');
    this.dependencies.clear();
    this.factories.clear();
  }
}

// Export singleton instance
export const container = Container.getInstance();
