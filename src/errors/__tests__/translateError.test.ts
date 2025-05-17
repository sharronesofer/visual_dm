import { describe, it, expect } from 'vitest';
import { translateErrorMessage } from '../translateError';
import { POIValidationException, POIException, POIErrorCategory, POISeverityLevel, POIErrorCode, POIErrorContext, AppError } from '../index';

describe('translateErrorMessage', () => {
    const baseContext: POIErrorContext = { poiId: 123, operationType: 'test' };

    it('translates POIValidationException to user-friendly message with POI ID', () => {
        const err = new POIValidationException('Validation failed', baseContext);
        const msg = translateErrorMessage(err);
        expect(msg).toContain('There was a problem with your request');
        expect(msg).toContain('POI ID: 123');
    });

    it('translates AppError to user-friendly message', () => {
        const err = new AppError('Not found', 'NOT_FOUND', 404);
        const msg = translateErrorMessage(err);
        expect(msg).toContain('could not be found');
    });

    it('falls back to internal error for generic Error', () => {
        const err = new Error('Something went wrong');
        const msg = translateErrorMessage(err);
        expect(msg).toContain('internal error');
    });

    it('falls back to unknown error for unknown input', () => {
        const msg = translateErrorMessage('random string');
        expect(msg).toContain('unknown error');
    });
}); 