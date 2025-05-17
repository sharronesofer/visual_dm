export interface CombatValidator<ActionType = any, StateType = any> {
    /**
     * Determines if this validator should process the given action.
     */
    isApplicable(action: ActionType, state: StateType): boolean;

    /**
     * Validates the action before execution. Returns a ValidationResult.
     */
    preValidate(action: ActionType, state: StateType): ValidationResult;

    /**
     * Validates the state after action execution. Returns a ValidationResult.
     */
    postValidate(action: ActionType, state: StateType): ValidationResult;
}

// Import ValidationResult from sibling file (to be created)
import { ValidationResult } from './ValidationResult'; 