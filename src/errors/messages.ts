/**
 * User-friendly error message templates for POI and App errors.
 */
export const errorMessageTemplates: Record<string, string> = {
    POI_001: 'There was a problem with your request. Please check your input and try again.',
    POI_002: 'A system integration failed. Please try again later or contact support if the issue persists.',
    POI_003: 'A data storage error occurred. Your changes may not have been saved.',
    POI_004: 'A concurrency conflict was detected. Please retry your action.',
    POI_005: 'You do not have permission to perform this action.',
    POI_999: 'An unknown error occurred. Please try again or contact support.',
    VALIDATION_ERROR: 'Some fields are invalid. Please review and correct them.',
    NOT_FOUND: 'The requested resource could not be found.',
    UNAUTHENTICATED: 'You must be logged in to perform this action.',
    FORBIDDEN: 'You do not have permission to access this resource.',
    CONFLICT: 'A conflict occurred. Please refresh and try again.',
    RATE_LIMIT: 'You are sending requests too quickly. Please slow down.',
    SERVICE_UNAVAILABLE: 'The service is temporarily unavailable. Please try again later.',
    BAD_REQUEST: 'The request was invalid. Please check your input.',
    DATABASE_ERROR: 'A database error occurred. Please try again later.',
    EXTERNAL_SERVICE_ERROR: 'An external service failed. Please try again later.',
    FILE_SYSTEM_ERROR: 'A file system error occurred. Please try again.',
    MEDIA_PROCESSING_ERROR: 'A media processing error occurred. Please try again.',
    INTERNAL_ERROR: 'An internal error occurred. Please try again.',
    UNKNOWN_ERROR: 'An unknown error occurred. Please try again.',
};

/**
 * Get a user-friendly error message template by code, with fallback.
 */
export function getErrorMessageTemplate(code: string): string {
    return errorMessageTemplates[code] || errorMessageTemplates.UNKNOWN_ERROR;
} 