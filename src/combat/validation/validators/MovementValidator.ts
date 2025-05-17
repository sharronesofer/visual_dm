import { CombatValidator } from '../CombatValidator';
import { ValidationResult } from '../ValidationResult';

// Placeholder types for demonstration
export interface MovementAction {
    type: 'move';
    moverId: string;
    destination: { x: number; y: number };
    // ...other fields
}

export interface CombatState {
    // ...combat state fields
}

export class MovementValidator implements CombatValidator<MovementAction, CombatState> {
    isApplicable(action: MovementAction): boolean {
        return action.type === 'move';
    }

    preValidate(action: MovementAction, state: CombatState): ValidationResult {
        // Example checks (replace with real logic):
        // 1. Check movement points
        // 2. Check terrain passability
        // 3. Check collision
        // For now, always succeed
        return ValidationResult.ok();
    }

    postValidate(action: MovementAction, state: CombatState): ValidationResult {
        // Example: check if state is consistent after movement
        return ValidationResult.ok();
    }
} 