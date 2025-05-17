import { CombatValidator } from './CombatValidator';
import { ValidationResult } from './ValidationResult';

export class ValidationPipeline<ActionType = any, StateType = any> {
    private validators: CombatValidator<ActionType, StateType>[] = [];

    /**
     * Register a validator in the pipeline (in order of priority).
     */
    register(validator: CombatValidator<ActionType, StateType>) {
        this.validators.push(validator);
    }

    /**
     * Run preValidate for all applicable validators.
     */
    preValidate(action: ActionType, state: StateType): ValidationResult {
        const results: ValidationResult[] = [];
        for (const validator of this.validators) {
            if (validator.isApplicable(action, state)) {
                results.push(validator.preValidate(action, state));
            }
        }
        return ValidationResult.combine(results);
    }

    /**
     * Run postValidate for all applicable validators.
     */
    postValidate(action: ActionType, state: StateType): ValidationResult {
        const results: ValidationResult[] = [];
        for (const validator of this.validators) {
            if (validator.isApplicable(action, state)) {
                results.push(validator.postValidate(action, state));
            }
        }
        return ValidationResult.combine(results);
    }

    /**
     * Run full validation (pre and post) for an action/state.
     */
    validate(action: ActionType, state: StateType): ValidationResult {
        const pre = this.preValidate(action, state);
        if (!pre.success) return pre;
        // Optionally, postValidate could be run after action execution
        return pre;
    }
} 