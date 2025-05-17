import { describe, it, expect, vi } from 'vitest';
import { POIExceptionHandlerFactory } from '../POIExceptionHandlerFactory';
import { POIValidationException, POIPersistenceException, POIConcurrencyException, POIException, POIErrorCategory, POISeverityLevel, POIErrorCode, POIErrorContext } from '../index';
import { AppError } from '../index';

describe('POIExceptionHandlerFactory', () => {
    const baseContext: POIErrorContext = { poiId: 1, operationType: 'test', timestamp: '2024-05-16T00:00:00Z', userId: 'user1' };

    describe('controllerHandler', () => {
        const handler = POIExceptionHandlerFactory.controllerHandler();
        const req = {};
        let statusCode: number | undefined;
        let jsonPayload: any;
        const res = {
            status: (code: number) => { statusCode = code; return res; },
            json: (payload: any) => { jsonPayload = payload; return res; },
        };
        const next = vi.fn();

        it('handles POIException', () => {
            statusCode = undefined; jsonPayload = undefined;
            const err = new POIValidationException('Validation failed', baseContext);
            handler(err, req, res, next);
            expect(statusCode).toBe(400);
            expect(jsonPayload.name).toBe('POIValidationException');
            expect(jsonPayload.errorCategory).toBe(POIErrorCategory.DATA_VALIDATION);
        });

        it('handles AppError', () => {
            statusCode = undefined; jsonPayload = undefined;
            const err = new AppError('App error', 'APP_ERROR', 418);
            handler(err, req, res, next);
            expect(statusCode).toBe(418);
            expect(jsonPayload.code).toBe('APP_ERROR');
        });

        it('handles unknown error', () => {
            statusCode = undefined; jsonPayload = undefined;
            const err = new Error('Unknown');
            handler(err, req, res, next);
            expect(statusCode).toBe(500);
            expect(jsonPayload.name).toBe('InternalServerError');
        });
    });

    describe('serviceHandler', () => {
        const handler = POIExceptionHandlerFactory.serviceHandler();
        it('rethrows POIException', () => {
            const err = new POIValidationException('Validation failed', baseContext);
            expect(() => handler(err)).toThrowError(POIValidationException);
        });
        it('rethrows AppError', () => {
            const err = new AppError('App error', 'APP_ERROR', 500);
            expect(() => handler(err)).toThrowError(AppError);
        });
        it('rethrows unknown error', () => {
            const err = new Error('Unknown');
            expect(() => handler(err)).toThrowError(Error);
        });
        it('calls onError for POIException', () => {
            const onError = vi.fn();
            const handlerWithCb = POIExceptionHandlerFactory.serviceHandler(onError);
            const err = new POIValidationException('Validation failed', baseContext);
            expect(() => handlerWithCb(err)).toThrowError(POIValidationException);
            expect(onError).toHaveBeenCalledWith(err);
        });
    });

    describe('dataAccessHandler', () => {
        const handler = POIExceptionHandlerFactory.dataAccessHandler();
        it('rethrows POIPersistenceException', () => {
            const err = new POIPersistenceException('Persistence failed', baseContext);
            expect(() => handler(err)).toThrowError(POIPersistenceException);
        });
        it('rethrows POIConcurrencyException', () => {
            const err = new POIConcurrencyException('Concurrency failed', baseContext);
            expect(() => handler(err)).toThrowError(POIConcurrencyException);
        });
        it('rethrows POIException', () => {
            const err = new POIException('Other POI error', POIErrorCategory.UNKNOWN, POISeverityLevel.LOW, POIErrorCode.POI_UNKNOWN, baseContext);
            expect(() => handler(err)).toThrowError(POIException);
        });
        it('rethrows AppError', () => {
            const err = new AppError('App error', 'APP_ERROR', 500);
            expect(() => handler(err)).toThrowError(AppError);
        });
        it('rethrows unknown error', () => {
            const err = new Error('Unknown');
            expect(() => handler(err)).toThrowError(Error);
        });
        it('calls onError for POIPersistenceException', () => {
            const onError = vi.fn();
            const handlerWithCb = POIExceptionHandlerFactory.dataAccessHandler(onError);
            const err = new POIPersistenceException('Persistence failed', baseContext);
            expect(() => handlerWithCb(err)).toThrowError(POIPersistenceException);
            expect(onError).toHaveBeenCalledWith(err);
        });
    });
}); 