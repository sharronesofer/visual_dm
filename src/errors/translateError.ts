import { getErrorMessageTemplate } from './messages';
import { POIException, AppError } from './index';

/**
 * Translate a technical error into a user-friendly message using templates.
 */
export function translateErrorMessage(error: unknown): string {
    if (error instanceof POIException || error instanceof AppError) {
        const code = (error as any).code;
        let message = getErrorMessageTemplate(code);
        // Optionally interpolate context (e.g., POI ID)
        if (error instanceof POIException && error.context && error.context.poiId) {
            message += ` (POI ID: ${error.context.poiId})`;
        }
        return message;
    }
    if (error instanceof Error) {
        return getErrorMessageTemplate('INTERNAL_ERROR');
    }
    return getErrorMessageTemplate('UNKNOWN_ERROR');
} 