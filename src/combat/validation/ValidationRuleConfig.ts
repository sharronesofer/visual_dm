export interface ValidationRuleSet {
    version: string;
    rules: Record<string, any>;
}

export class ValidationRuleConfig {
    private static instance: ValidationRuleConfig;
    private ruleSet: ValidationRuleSet;

    private constructor() {
        // Default rule set; in practice, load from file or server
        this.ruleSet = {
            version: '1.0.0',
            rules: {}
        };
    }

    static getInstance(): ValidationRuleConfig {
        if (!ValidationRuleConfig.instance) {
            ValidationRuleConfig.instance = new ValidationRuleConfig();
        }
        return ValidationRuleConfig.instance;
    }

    getRule(key: string): any {
        return this.ruleSet.rules[key];
    }

    setRule(key: string, value: any) {
        this.ruleSet.rules[key] = value;
    }

    getVersion(): string {
        return this.ruleSet.version;
    }

    setVersion(version: string) {
        this.ruleSet.version = version;
    }

    // For loading from JSON (could be extended to async/file)
    loadFromObject(obj: ValidationRuleSet) {
        this.ruleSet = obj;
    }

    toJSON(): ValidationRuleSet {
        return this.ruleSet;
    }
} 