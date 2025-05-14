from typing import Dict, List, Optional, Any, Union

    RegionValidationRule,
    RegionValidationResult,
    createStandardRegionValidationRules
} from './RegionValidationRules';
/**
 * Validator for regions
 * Applies validation rules to ensure regions meet required criteria
 */
class RegionValidator {
    /** The validation rules to apply */
    private rules: RegionValidationRule[];
    /** Cached validation results */
    private validationCache: Map<string, RegionValidationResult>;
    /**
     * Create a new region validator
     * @param rules Optional validation rules (uses standard rules if not provided)
     */
    constructor(rules?: RegionValidationRule[]) {
        this.rules = rules || [createStandardRegionValidationRules()];
        this.validationCache = new Map();
    }
    /**
     * Add a validation rule
     * @param rule The rule to add
     */
    public addRule(rule: RegionValidationRule): void {
        this.rules.push(rule);
        this.validationCache.clear();
    }
    /**
     * Remove all validation rules
     */
    public clearRules(): void {
        this.rules = [];
        this.validationCache.clear();
    }
    /**
     * Set the validation rules
     * @param rules The rules to set
     */
    public setRules(rules: RegionValidationRule[]): void {
        this.rules = [...rules];
        this.validationCache.clear();
    }
    /**
     * Get all validation rules
     * @returns The validation rules
     */
    public getRules(): RegionValidationRule[] {
        return [...this.rules];
    }
    /**
     * Validate a region
     * @param region The region to validate
     * @returns The validation result
     */
    public validate(region: Region): RegionValidationResult {
        const cacheKey = this.getCacheKey(region);
        if (this.validationCache.has(cacheKey)) {
            return this.validationCache.get(cacheKey)!;
        }
        for (const rule of this.rules) {
            const isValid = rule.validate(region);
            if (!isValid) {
                const result: RegionValidationResult = {
                    isValid: false,
                    errorMessage: rule.getErrorMessage(),
                    details: rule.getDetails()
                };
                this.validationCache.set(cacheKey, result);
                return result;
            }
        }
        const result: RegionValidationResult = {
            isValid: true
        };
        this.validationCache.set(cacheKey, result);
        return result;
    }
    /**
     * Clear the validation cache
     */
    public clearCache(): void {
        this.validationCache.clear();
    }
    /**
     * Generate a cache key for a region
     * @param region The region
     * @returns A cache key
     */
    private getCacheKey(region: Region): string {
        const seed = region.metadata?.seed || Date.now();
        return `${region.id}-${seed}`;
    }
    /**
     * Default validator instance
     */
    private static defaultInstance: RegionValidator;
    /**
     * Get the default validator instance
     * @returns The default validator instance
     */
    public static getDefaultInstance(): RegionValidator {
        if (!RegionValidator.defaultInstance) {
            RegionValidator.defaultInstance = new RegionValidator();
        }
        return RegionValidator.defaultInstance;
    }
} 