import { ErrorCategory } from './ErrorCategory';

export class ErrorSuggestion {
    static suggest(category: ErrorCategory, context: Record<string, any> = {}): string {
        switch (category) {
            case ErrorCategory.INVALID_TARGET:
                return 'Select a valid target.';
            case ErrorCategory.INSUFFICIENT_RESOURCES:
                return 'Try an action that requires fewer resources or replenish resources.';
            case ErrorCategory.COOLDOWN_ACTIVE:
                return 'Wait for the cooldown to expire or choose a different action.';
            case ErrorCategory.STATE_CONFLICT:
                return 'Resolve conflicting states before retrying.';
            case ErrorCategory.PERMISSION_DENIED:
                return 'You do not have permission to perform this action.';
            case ErrorCategory.OUT_OF_RANGE:
                return 'Move closer to the target or select one within range.';
            case ErrorCategory.INVALID_ACTION:
                return 'Choose a valid action for the current context.';
            default:
                return 'Check the action and try again.';
        }
    }
} 