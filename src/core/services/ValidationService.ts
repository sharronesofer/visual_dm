import { NoNegativeBalanceRule, SufficientFundsRule, ReputationBoundsRule, InventorySlotLimitRule, InventoryWeightLimitRule, ValidItemRule, EconomicInventoryConsistencyRule, ReputationEconomicConsistencyRule, InventoryReputationConsistencyRule } from './validationRules';
import { EventBus } from '../events/EventBus';
import { SceneEventType } from '../events/SceneEventTypes';
import { ErrorHandlingService, ErrorContext, ErrorCategory } from './ErrorHandlingService';

/**
 * Severity levels for validation rules.
 */
export enum ValidationSeverity {
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info',
}

/**
 * Interface for validation rules.
 */
export interface ValidationRule {
  validate(data: any, context?: ValidationContext): boolean | Promise<boolean>;
  getErrorMessage?(): string;
  severity?: ValidationSeverity;
  metadata?: Record<string, any>;
}

/**
 * Registry for managing validation rules by context/type.
 */
export class RuleRegistry {
  private rules: Map<string, ValidationRule[]> = new Map();
  register(context: string, rule: ValidationRule) {
    if (!this.rules.has(context)) this.rules.set(context, []);
    this.rules.get(context)!.push(rule);
  }
  get(context: string): ValidationRule[] {
    return this.rules.get(context) || [];
  }
  remove(context: string, rule: ValidationRule) {
    if (!this.rules.has(context)) return;
    this.rules.set(context, this.rules.get(context)!.filter(r => r !== rule));
  }
  clear(context?: string) {
    if (context) this.rules.delete(context);
    else this.rules.clear();
  }
}

/**
 * Context for passing state and metadata between validation steps.
 */
export class ValidationContext {
  public errors: string[] = [];
  public warnings: string[] = [];
  public info: string[] = [];
  public metadata: Record<string, any> = {};
  public origin?: string;
  public timestamp: number = Date.now();
  addError(msg: string) { this.errors.push(msg); }
  addWarning(msg: string) { this.warnings.push(msg); }
  addInfo(msg: string) { this.info.push(msg); }
  clone(): ValidationContext {
    const ctx = new ValidationContext();
    ctx.errors = [...this.errors];
    ctx.warnings = [...this.warnings];
    ctx.info = [...this.info];
    ctx.metadata = { ...this.metadata };
    ctx.origin = this.origin;
    ctx.timestamp = this.timestamp;
    return ctx;
  }
}

/**
 * Utility for cross-system data consistency checks.
 */
export class ConsistencyChecker {
  static async checkEconomicInventory(economicData: any, inventoryData: any): Promise<boolean> {
    // Example: Check that all items in economic system exist in inventory
    // (Stub implementation)
    return true;
  }
  static async checkReputationEconomic(reputationData: any, economicData: any): Promise<boolean> {
    // Example: Check that reputation changes are reflected in economic privileges
    return true;
  }
  static async checkInventoryReputation(inventoryData: any, reputationData: any): Promise<boolean> {
    // Example: Check that inventory access matches reputation requirements
    return true;
  }
}

/**
 * Configuration for enabling/disabling rules by environment.
 */
export class ValidationConfiguration {
  private enabledRules: Set<string> = new Set();
  enableRule(ruleName: string) { this.enabledRules.add(ruleName); }
  disableRule(ruleName: string) { this.enabledRules.delete(ruleName); }
  isEnabled(ruleName: string): boolean { return this.enabledRules.has(ruleName); }
}

/**
 * Specialized validators for each system type.
 */
export class EconomicValidator {
  constructor(private registry: RuleRegistry) { }
  async validate(data: any, context: ValidationContext): Promise<boolean> {
    let valid = true;
    for (const rule of this.registry.get('economic')) {
      const result = await rule.validate(data, context);
      if (!result) {
        context.addError(rule.getErrorMessage?.() || 'Economic validation failed');
        valid = false;
      }
    }
    return valid;
  }
}
export class ReputationValidator {
  constructor(private registry: RuleRegistry) { }
  async validate(data: any, context: ValidationContext): Promise<boolean> {
    let valid = true;
    for (const rule of this.registry.get('reputation')) {
      const result = await rule.validate(data, context);
      if (!result) {
        context.addError(rule.getErrorMessage?.() || 'Reputation validation failed');
        valid = false;
      }
    }
    return valid;
  }
}
export class InventoryValidator {
  constructor(private registry: RuleRegistry) { }
  async validate(data: any, context: ValidationContext): Promise<boolean> {
    let valid = true;
    for (const rule of this.registry.get('inventory')) {
      const result = await rule.validate(data, context);
      if (!result) {
        context.addError(rule.getErrorMessage?.() || 'Inventory validation failed');
        valid = false;
      }
    }
    return valid;
  }
}

/**
 * Extended ValidationService with pre/post hooks, sync/async modes, and environment config.
 */
export class ValidationService {
  private static instance: ValidationService;
  private registry: RuleRegistry = new RuleRegistry();
  private config: ValidationConfiguration = new ValidationConfiguration();
  private preHooks: Array<(data: any, context: ValidationContext) => void | Promise<void>> = [];
  private postHooks: Array<(data: any, context: ValidationContext) => void | Promise<void>> = [];

  private constructor() {
    // Register and enable economic rules
    this.registerRule('economic', new NoNegativeBalanceRule());
    this.config.enableRule('NoNegativeBalanceRule');
    this.registerRule('economic', new SufficientFundsRule());
    this.config.enableRule('SufficientFundsRule');
    // Register and enable reputation rules
    this.registerRule('reputation', new ReputationBoundsRule());
    this.config.enableRule('ReputationBoundsRule');
    // Register and enable inventory rules
    this.registerRule('inventory', new InventorySlotLimitRule());
    this.config.enableRule('InventorySlotLimitRule');
    this.registerRule('inventory', new InventoryWeightLimitRule());
    this.config.enableRule('InventoryWeightLimitRule');
    this.registerRule('inventory', new ValidItemRule());
    this.config.enableRule('ValidItemRule');
    // Register and enable cross-system consistency rules
    this.registerRule('cross-system', new EconomicInventoryConsistencyRule());
    this.config.enableRule('EconomicInventoryConsistencyRule');
    this.registerRule('cross-system', new ReputationEconomicConsistencyRule());
    this.config.enableRule('ReputationEconomicConsistencyRule');
    this.registerRule('cross-system', new InventoryReputationConsistencyRule());
    this.config.enableRule('InventoryReputationConsistencyRule');
  }

  public static getInstance(): ValidationService {
    if (!ValidationService.instance) {
      ValidationService.instance = new ValidationService();
    }
    return ValidationService.instance;
  }

  public registerRule(context: string, rule: ValidationRule) {
    this.registry.register(context, rule);
  }
  public clearRules(context?: string) {
    this.registry.clear(context);
  }
  public registerPreHook(hook: (data: any, context: ValidationContext) => void | Promise<void>) {
    this.preHooks.push(hook);
  }
  public registerPostHook(hook: (data: any, context: ValidationContext) => void | Promise<void>) {
    this.postHooks.push(hook);
  }
  public setConfig(config: ValidationConfiguration) {
    this.config = config;
  }
  /**
   * Synchronous (blocking) validation.
   */
  public validateSync(contextName: string, data: any): ValidationContext {
    const context = new ValidationContext();
    for (const hook of this.preHooks) hook(data, context);
    for (const rule of this.registry.get(contextName)) {
      if (!this.config.isEnabled(rule.constructor.name)) continue;
      const result = rule.validate(data, context);
      if (result === false) {
        const msg = rule.getErrorMessage?.() || 'Validation failed';
        context.addError(msg);
        // Emit validation event
        const event = {
          type: SceneEventType.VALIDATION_EVENT,
          source: 'ValidationService',
          timestamp: Date.now(),
          level: 'error',
          ruleName: rule.constructor.name,
          message: msg,
          contextData: data,
        } as import('../events/SceneEventTypes').ValidationEvent;
        EventBus.getInstance().emit(event);
        // Forward to error handling
        const ctx = new ErrorContext({
          category: ErrorCategory.VALIDATION,
          message: msg,
          details: data,
          service: 'ValidationService',
        });
        ErrorHandlingService.getInstance().logError(ctx);
      }
    }
    for (const hook of this.postHooks) hook(data, context);
    return context;
  }
  /**
   * Asynchronous (non-blocking) validation.
   */
  public async validateAsync(contextName: string, data: any): Promise<ValidationContext> {
    const context = new ValidationContext();
    for (const hook of this.preHooks) await hook(data, context);
    for (const rule of this.registry.get(contextName)) {
      if (!this.config.isEnabled(rule.constructor.name)) continue;
      const result = await rule.validate(data, context);
      if (result === false) {
        const msg = rule.getErrorMessage?.() || 'Validation failed';
        context.addError(msg);
        // Emit validation event
        const event = {
          type: SceneEventType.VALIDATION_EVENT,
          source: 'ValidationService',
          timestamp: Date.now(),
          level: 'error',
          ruleName: rule.constructor.name,
          message: msg,
          contextData: data,
        } as import('../events/SceneEventTypes').ValidationEvent;
        await EventBus.getInstance().emit(event);
        // Forward to error handling
        const ctx = new ErrorContext({
          category: ErrorCategory.VALIDATION,
          message: msg,
          details: data,
          service: 'ValidationService',
        });
        ErrorHandlingService.getInstance().logError(ctx);
      }
    }
    for (const hook of this.postHooks) await hook(data, context);
    return context;
  }
}
