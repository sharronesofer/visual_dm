export type ValidationSeverity = 'info' | 'warning' | 'error';

export class ValidationResult {
    readonly success: boolean;
    readonly messages: string[];
    readonly codes: string[];
    readonly severity: ValidationSeverity;

    constructor(
        success: boolean,
        messages: string[] = [],
        codes: string[] = [],
        severity: ValidationSeverity = 'error'
    ) {
        this.success = success;
        this.messages = messages;
        this.codes = codes;
        this.severity = severity;
    }

    static ok(): ValidationResult {
        return new ValidationResult(true, [], [], 'info');
    }

    static fail(message: string, code: string = '', severity: ValidationSeverity = 'error'): ValidationResult {
        return new ValidationResult(false, [message], code ? [code] : [], severity);
    }

    /**
     * Combine multiple ValidationResults. If any is failure, result is failure.
     */
    static combine(results: ValidationResult[]): ValidationResult {
        const allSuccess = results.every(r => r.success);
        const messages = results.flatMap(r => r.messages);
        const codes = results.flatMap(r => r.codes);
        // Highest severity if any error, else warning, else info
        let severity: ValidationSeverity = 'info';
        if (results.some(r => r.severity === 'error')) severity = 'error';
        else if (results.some(r => r.severity === 'warning')) severity = 'warning';
        return new ValidationResult(allSuccess, messages, codes, severity);
    }
} 