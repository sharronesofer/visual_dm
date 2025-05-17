import { describe, it, expect } from 'vitest';
import {
    POIErrorCategory,
    POISeverityLevel,
    POIErrorCode,
    POIErrorContext,
    POIException,
    POIValidationException,
    POIIntegrationException,
    POIPersistenceException,
    POIConcurrencyException,
    POIAuthorizationException,
    POIUnknownException,
} from '../index';

describe('POI Error Enums', () => {
    it('should have all expected categories', () => {
        expect(POIErrorCategory.DATA_VALIDATION).toBe('DATA_VALIDATION');
        expect(POIErrorCategory.INTEGRATION).toBe('INTEGRATION');
        expect(POIErrorCategory.PERSISTENCE).toBe('PERSISTENCE');
        expect(POIErrorCategory.CONCURRENCY).toBe('CONCURRENCY');
        expect(POIErrorCategory.AUTHORIZATION).toBe('AUTHORIZATION');
        expect(POIErrorCategory.UNKNOWN).toBe('UNKNOWN');
    });
    it('should have all expected severity levels', () => {
        expect(POISeverityLevel.CRITICAL).toBe('CRITICAL');
        expect(POISeverityLevel.HIGH).toBe('HIGH');
        expect(POISeverityLevel.MEDIUM).toBe('MEDIUM');
        expect(POISeverityLevel.LOW).toBe('LOW');
    });
    it('should have all expected error codes', () => {
        expect(POIErrorCode.POI_VALIDATION).toBe('POI_001');
        expect(POIErrorCode.POI_INTEGRATION).toBe('POI_002');
        expect(POIErrorCode.POI_PERSISTENCE).toBe('POI_003');
        expect(POIErrorCode.POI_CONCURRENCY).toBe('POI_004');
        expect(POIErrorCode.POI_AUTHORIZATION).toBe('POI_005');
        expect(POIErrorCode.POI_UNKNOWN).toBe('POI_999');
    });
});

describe('POIErrorContext', () => {
    it('should allow flexible context creation', () => {
        const ctx: POIErrorContext = {
            poiId: 'abc123',
            operationType: 'update',
            timestamp: '2024-05-16T00:00:00Z',
            userId: 'user42',
            additionalData: { foo: 'bar' },
        };
        expect(ctx.poiId).toBe('abc123');
        expect(ctx.additionalData?.foo).toBe('bar');
    });
});

describe('POIException hierarchy', () => {
    const baseContext: POIErrorContext = {
        poiId: 42,
        operationType: 'create',
        timestamp: '2024-05-16T00:00:00Z',
        userId: 'user1',
        additionalData: { test: true },
    };

    it('should instantiate POIException with all fields', () => {
        const err = new POIException(
            'Base POI error',
            POIErrorCategory.UNKNOWN,
            POISeverityLevel.LOW,
            POIErrorCode.POI_UNKNOWN,
            baseContext,
            500,
            { foo: 'bar' }
        );
        expect(err).toBeInstanceOf(POIException);
        expect(err.errorCategory).toBe(POIErrorCategory.UNKNOWN);
        expect(err.severityLevel).toBe(POISeverityLevel.LOW);
        expect(err.errorCode).toBe(POIErrorCode.POI_UNKNOWN);
        expect(err.context.poiId).toBe(42);
        expect(err.statusCode).toBe(500);
        expect(err.details).toEqual({ foo: 'bar' });
        expect(err.toJSON().context.poiId).toBe(42);
    });

    it('should instantiate POIValidationException', () => {
        const err = new POIValidationException('Validation failed', baseContext, { field: 'name' });
        expect(err).toBeInstanceOf(POIException);
        expect(err).toBeInstanceOf(POIValidationException);
        expect(err.errorCategory).toBe(POIErrorCategory.DATA_VALIDATION);
        expect(err.severityLevel).toBe(POISeverityLevel.HIGH);
        expect(err.errorCode).toBe(POIErrorCode.POI_VALIDATION);
        expect(err.statusCode).toBe(400);
        expect(err.details).toEqual({ field: 'name' });
    });

    it('should instantiate POIIntegrationException', () => {
        const err = new POIIntegrationException('Integration failed', baseContext, { endpoint: 'serviceX' });
        expect(err.errorCategory).toBe(POIErrorCategory.INTEGRATION);
        expect(err.severityLevel).toBe(POISeverityLevel.CRITICAL);
        expect(err.errorCode).toBe(POIErrorCode.POI_INTEGRATION);
        expect(err.statusCode).toBe(502);
        expect(err.details).toEqual({ endpoint: 'serviceX' });
    });

    it('should instantiate POIPersistenceException', () => {
        const err = new POIPersistenceException('Persistence failed', baseContext, { entity: 'POI' });
        expect(err.errorCategory).toBe(POIErrorCategory.PERSISTENCE);
        expect(err.severityLevel).toBe(POISeverityLevel.CRITICAL);
        expect(err.errorCode).toBe(POIErrorCode.POI_PERSISTENCE);
        expect(err.statusCode).toBe(500);
        expect(err.details).toEqual({ entity: 'POI' });
    });

    it('should instantiate POIConcurrencyException', () => {
        const err = new POIConcurrencyException('Concurrency conflict', baseContext, { conflict: true });
        expect(err.errorCategory).toBe(POIErrorCategory.CONCURRENCY);
        expect(err.severityLevel).toBe(POISeverityLevel.HIGH);
        expect(err.errorCode).toBe(POIErrorCode.POI_CONCURRENCY);
        expect(err.statusCode).toBe(409);
        expect(err.details).toEqual({ conflict: true });
    });

    it('should instantiate POIAuthorizationException', () => {
        const err = new POIAuthorizationException('Not authorized', baseContext, { role: 'guest' });
        expect(err.errorCategory).toBe(POIErrorCategory.AUTHORIZATION);
        expect(err.severityLevel).toBe(POISeverityLevel.HIGH);
        expect(err.errorCode).toBe(POIErrorCode.POI_AUTHORIZATION);
        expect(err.statusCode).toBe(403);
        expect(err.details).toEqual({ role: 'guest' });
    });

    it('should instantiate POIUnknownException', () => {
        const err = new POIUnknownException('Unknown error', baseContext, { info: 'none' });
        expect(err.errorCategory).toBe(POIErrorCategory.UNKNOWN);
        expect(err.severityLevel).toBe(POISeverityLevel.MEDIUM);
        expect(err.errorCode).toBe(POIErrorCode.POI_UNKNOWN);
        expect(err.statusCode).toBe(500);
        expect(err.details).toEqual({ info: 'none' });
    });

    it('should serialize to JSON with all fields', () => {
        const err = new POIValidationException('Validation failed', baseContext, { foo: 'bar' });
        const json = err.toJSON();
        expect(json.name).toBe('POIValidationException');
        expect(json.errorCategory).toBe(POIErrorCategory.DATA_VALIDATION);
        expect(json.severityLevel).toBe(POISeverityLevel.HIGH);
        expect(json.errorCode).toBe(POIErrorCode.POI_VALIDATION);
        expect(json.context.poiId).toBe(42);
        expect(json.details).toEqual({ foo: 'bar' });
    });
}); 