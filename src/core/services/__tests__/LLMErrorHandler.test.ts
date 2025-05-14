import { LLMErrorHandler, LLMErrorType, LLMErrorContext, RetryStrategy } from '../LLMErrorHandler';
import { LoggerService } from '../LoggerService';

// Mock LoggerService
jest.mock('../LoggerService', () => ({
  LoggerService: {
    getInstance: jest.fn().mockReturnValue({
      log: jest.fn(),
      debug: jest.fn(),
      info: jest.fn(),
      warn: jest.fn(),
      error: jest.fn()
    })
  }
}));

describe('LLMErrorHandler', () => {
  let errorHandler: LLMErrorHandler;
  let loggerMock: any;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Get instance and mock
    errorHandler = LLMErrorHandler.getInstance();
    loggerMock = LoggerService.getInstance();
    
    // Reset error counts to ensure tests are isolated
    errorHandler.resetErrorCounts();
  });

  describe('identifyErrorType', () => {
    test('should identify timeout errors correctly', () => {
      const error = new Error('Request timed out after 10s');
      expect(errorHandler.identifyErrorType(error)).toBe(LLMErrorType.TIMEOUT);
    });

    test('should identify content policy errors correctly', () => {
      const error = new Error('Content policy violation detected in prompt');
      expect(errorHandler.identifyErrorType(error)).toBe(LLMErrorType.CONTENT_POLICY);
    });

    test('should identify rate limit errors correctly', () => {
      const error = new Error('Rate limit exceeded, too many requests');
      expect(errorHandler.identifyErrorType(error)).toBe(LLMErrorType.RATE_LIMIT);
    });

    test('should identify malformed response errors correctly', () => {
      const error = new Error('Failed to parse response: invalid json');
      expect(errorHandler.identifyErrorType(error)).toBe(LLMErrorType.MALFORMED_RESPONSE);
    });

    test('should return UNKNOWN for unrecognized errors', () => {
      const error = new Error('Some unrecognized error');
      expect(errorHandler.identifyErrorType(error)).toBe(LLMErrorType.UNKNOWN);
    });
  });

  describe('logError', () => {
    test('should log error with appropriate level', () => {
      const context: LLMErrorContext = {
        timestamp: Date.now(),
        prompt: 'Test prompt',
        gameState: { interactionType: 'dialogue' }
      };
      
      errorHandler.logError(LLMErrorType.TIMEOUT, context);
      expect(loggerMock.log).toHaveBeenCalledWith('info', 'LLM Error', expect.any(Object));
    });

    test('should log severe errors with error level', () => {
      const context: LLMErrorContext = {
        timestamp: Date.now(),
        prompt: 'Test prompt',
        gameState: { interactionType: 'dialogue' }
      };
      
      errorHandler.logError(LLMErrorType.SERVER_ERROR, context);
      expect(loggerMock.log).toHaveBeenCalledWith('error', 'LLM Error', expect.any(Object));
    });

    test('should track error count', () => {
      const context: LLMErrorContext = {
        timestamp: Date.now(),
        prompt: 'Test prompt',
        gameState: { interactionType: 'dialogue' }
      };
      
      // Call multiple times
      errorHandler.logError(LLMErrorType.TIMEOUT, context);
      errorHandler.logError(LLMErrorType.TIMEOUT, context);
      
      // Second call should have count of 2
      expect(loggerMock.log).toHaveBeenLastCalledWith(
        'info',
        'LLM Error',
        expect.objectContaining({
          errorCount: 2
        })
      );
    });

    test('should trigger alert for high error rates', () => {
      const context: LLMErrorContext = {
        timestamp: Date.now(),
        prompt: 'Test prompt',
        gameState: { interactionType: 'dialogue' }
      };
      
      // Call enough times to trigger alert (based on default config)
      for (let i = 0; i < 10; i++) {
        errorHandler.logError(LLMErrorType.TIMEOUT, context);
      }
      
      expect(loggerMock.warn).toHaveBeenCalledWith(
        'LLM Error Rate Alert',
        expect.objectContaining({
          errorType: LLMErrorType.TIMEOUT,
          count: 10
        })
      );
    });
  });

  describe('getFallbackResponse', () => {
    test('should return appropriate fallback based on context type', () => {
      const context: LLMErrorContext = {
        timestamp: Date.now(),
        gameState: { interactionType: 'negotiation' }
      };
      
      const fallback = errorHandler.getFallbackResponse(LLMErrorType.TIMEOUT, context);
      expect(fallback).toBeTruthy();
      expect(typeof fallback).toBe('string');
    });

    test('should use default fallbacks when context type is unknown', () => {
      const context: LLMErrorContext = {
        timestamp: Date.now(),
        gameState: { interactionType: 'non_existent_type' }
      };
      
      // Mock the determineContextType method to ensure it returns 'default'
      const spy = jest.spyOn(errorHandler as any, 'determineContextType');
      spy.mockReturnValue('default');
      
      const fallback = errorHandler.getFallbackResponse(LLMErrorType.TIMEOUT, context);
      expect(spy).toHaveBeenCalled();
      expect(fallback).toBeTruthy();
      expect(typeof fallback).toBe('string');
      
      spy.mockRestore();
    });
  });

  describe('getRetryDelay', () => {
    test('should increase delay with each retry', () => {
      const delay1 = errorHandler.getRetryDelay(0);
      const delay2 = errorHandler.getRetryDelay(1);
      const delay3 = errorHandler.getRetryDelay(2);
      
      expect(delay2).toBeGreaterThan(delay1);
      expect(delay3).toBeGreaterThan(delay2);
    });

    test('should use exponential backoff', () => {
      // Get private config to calculate expected values
      const config = (errorHandler as any).config;
      const { initialDelayMs, backoffFactor } = config.retryStrategy;
      
      const delay1 = errorHandler.getRetryDelay(1);
      const expectedDelay1 = initialDelayMs * Math.pow(backoffFactor, 1);
      
      // Allow for jitter if enabled
      const jitterRange = config.retryStrategy.jitter ? 0.3 * expectedDelay1 : 0;
      
      expect(delay1).toBeGreaterThanOrEqual(expectedDelay1 - jitterRange);
      expect(delay1).toBeLessThanOrEqual(expectedDelay1 + jitterRange);
    });
  });

  describe('getAlternativePrompt', () => {
    test('should simplify prompt when no alternatives provided', () => {
      const originalPrompt = 'This is a very long prompt that should be simplified by the system when retrying';
      const newPrompt = errorHandler.getAlternativePrompt(originalPrompt, LLMErrorType.TIMEOUT, 1);
      
      expect(newPrompt.length).toBeLessThan(originalPrompt.length);
    });

    test('should use predefined alternatives when available', () => {
      const originalPrompt = 'Test prompt';
      const alternativePrompts = ['Alternative 1', 'Alternative 2'];
      
      // Update config to include alternative prompts
      const retryStrategy: RetryStrategy = {
        maxRetries: 3,
        backoffFactor: 2,
        initialDelayMs: 1000,
        jitter: true,
        alternativePrompts
      };
      
      errorHandler.updateConfig({
        retryStrategy
      });
      
      const newPrompt = errorHandler.getAlternativePrompt(originalPrompt, LLMErrorType.TIMEOUT, 1);
      expect(newPrompt).toBe(alternativePrompts[0]);
      
      // Reset
      errorHandler.updateConfig({
        retryStrategy: {
          maxRetries: 3,
          backoffFactor: 2,
          initialDelayMs: 1000,
          jitter: true,
          alternativePrompts: []
        }
      });
    });
  });

  describe('updateConfig', () => {
    test('should update the config correctly', () => {
      const newConfig = {
        logLevel: 'debug' as const,
        retryStrategy: {
          maxRetries: 5,
          backoffFactor: 3,
          initialDelayMs: 1000,
          jitter: true
        }
      };
      
      errorHandler.updateConfig(newConfig);
      
      // Test a method that uses the config
      const delay = errorHandler.getRetryDelay(1);
      const expectedDelay = 1000 * Math.pow(3, 1); // initialDelayMs * backoffFactor^1
      
      // Allow for jitter
      const jitterRange = 0.3 * expectedDelay;
      expect(delay).toBeGreaterThanOrEqual(expectedDelay - jitterRange);
      expect(delay).toBeLessThanOrEqual(expectedDelay + jitterRange);
    });

    test('should merge fallback libraries', () => {
      const newFallbacks = {
        'test_type': ['Test fallback 1', 'Test fallback 2']
      };
      
      errorHandler.updateConfig({
        fallbackLibrary: newFallbacks
      });
      
      // Create a context with the test type
      const context: LLMErrorContext = {
        timestamp: Date.now(),
        gameState: { interactionType: 'test_type' }
      };
      
      // Mock to ensure the new type is detected
      const spy = jest.spyOn(errorHandler as any, 'determineContextType');
      spy.mockReturnValue('test_type');
      
      // Get fallback and verify it's from our new library
      const fallback = errorHandler.getFallbackResponse(LLMErrorType.TIMEOUT, context);
      expect(newFallbacks['test_type']).toContain(fallback);
      
      spy.mockRestore();
    });
  });
}); 