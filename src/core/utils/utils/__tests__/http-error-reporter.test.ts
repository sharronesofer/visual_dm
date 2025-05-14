import {
  HttpReporterBackend,
  HttpReporterConfig,
} from '../http-error-reporter';
import { httpClient } from '../../../services/http-client';
import { logger } from '../logger';
import { ErrorReport } from '../error-reporter';

// Mock dependencies
jest.mock('../../../services/http-client', () => ({
  httpClient: {
    post: jest.fn(),
  },
}));

jest.mock('../logger', () => ({
  logger: {
    error: jest.fn(),
    debug: jest.fn(),
  },
}));

describe('HttpReporterBackend', () => {
  let reporter: HttpReporterBackend;
  const mockConfig: Required<HttpReporterConfig> = {
    endpoint: 'https://api.example.com/errors',
    apiKey: 'test-key',
    batchSize: 2,
    retryAttempts: 2,
    retryDelay: 100,
    headers: {},
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    reporter = new HttpReporterBackend(mockConfig);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('Configuration', () => {
    it('should use provided configuration', () => {
      expect(reporter['config']).toEqual(mockConfig);
    });

    it('should use default values for optional config', () => {
      const minimalConfig = { endpoint: 'https://api.example.com/errors' };
      const minimalReporter = new HttpReporterBackend(minimalConfig);

      expect(minimalReporter['config']).toEqual({
        endpoint: minimalConfig.endpoint,
        batchSize: 10,
        retryAttempts: 3,
        retryDelay: 1000,
      });
    });
  });

  describe('Error Reporting', () => {
    const mockError = new Error('Test error');
    const mockReport: ErrorReport = {
      error: mockError,
      timestamp: new Date().toISOString(),
      tags: { type: 'test' },
    };

    it('should queue error report', async () => {
      await reporter.report(mockReport);
      expect(reporter['pendingReports']).toHaveLength(1);
      expect(reporter['pendingReports'][0]).toBe(mockReport);
    });

    it('should process batch when size threshold reached', async () => {
      await reporter.report(mockReport);
      await reporter.report(mockReport);

      expect(httpClient.post).toHaveBeenCalledWith(
        mockConfig.endpoint,
        expect.arrayContaining([
          expect.objectContaining({ error: expect.any(Object) }),
        ]),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockConfig.apiKey}`,
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should handle report errors gracefully', async () => {
      const error = new Error('Queue error');
      jest.spyOn(reporter['pendingReports'], 'push').mockImplementation(() => {
        throw error;
      });

      await reporter.report(mockReport);
      expect(logger.error).toHaveBeenCalledWith(
        'Failed to queue error report:',
        error
      );
    });
  });

  describe('Batch Processing', () => {
    const mockError = new Error('Test error');
    const mockReport: ErrorReport = {
      error: mockError,
      timestamp: new Date().toISOString(),
    };

    it('should clear queue after successful processing', async () => {
      (httpClient.post as jest.Mock).mockResolvedValueOnce({});

      await reporter.report(mockReport);
      await reporter.report(mockReport);

      expect(reporter['pendingReports']).toHaveLength(0);
    });

    it('should retry on failure', async () => {
      (httpClient.post as jest.Mock)
        .mockRejectedValueOnce(new Error('First attempt failed'))
        .mockResolvedValueOnce({});

      await reporter.report(mockReport);
      await reporter.report(mockReport);

      // First attempt fails
      expect(logger.error).toHaveBeenCalledWith(
        'Failed to send error reports (attempt 1):',
        expect.any(Error)
      );

      // Advance timer to trigger retry
      jest.advanceTimersByTime(mockConfig.retryDelay);

      // Should have retried
      expect(httpClient.post).toHaveBeenCalledTimes(2);
    });

    it('should give up after max retries', async () => {
      const error = new Error('Request failed');
      (httpClient.post as jest.Mock).mockRejectedValue(error);

      await reporter.report(mockReport);
      await reporter.report(mockReport);

      // Advance through all retry attempts
      for (let i = 0; i < mockConfig.retryAttempts; i++) {
        jest.advanceTimersByTime(mockConfig.retryDelay * (i + 1));
      }

      // Should have logged final error
      expect(logger.error).toHaveBeenLastCalledWith(
        'Failed to send error reports after all retry attempts',
        expect.objectContaining({
          context: expect.objectContaining({
            failedReports: expect.arrayContaining([mockReport]),
          }),
        })
      );

      // Queue should be cleared
      expect(reporter['pendingReports']).toHaveLength(0);
    });
  });

  describe('Flush', () => {
    const mockReport: ErrorReport = {
      error: new Error('Test error'),
      timestamp: new Date().toISOString(),
    };

    it('should process pending reports', async () => {
      await reporter.report(mockReport);
      await reporter.flush();

      expect(httpClient.post).toHaveBeenCalled();
      expect(reporter['pendingReports']).toHaveLength(0);
    });

    it('should clear retry timeouts', async () => {
      // Setup a failed request that will trigger retry
      (httpClient.post as jest.Mock).mockRejectedValueOnce(new Error('Failed'));

      await reporter.report(mockReport);
      await reporter.report(mockReport);

      // Should have one retry timeout
      expect(reporter['retryTimeouts'].size).toBe(1);

      await reporter.flush();

      // Timeouts should be cleared
      expect(reporter['retryTimeouts'].size).toBe(0);
    });

    it('should handle flush errors gracefully', async () => {
      const error = new Error('Flush error');
      (httpClient.post as jest.Mock).mockRejectedValue(error);

      await reporter.report(mockReport);
      await reporter.flush();

      expect(logger.error).toHaveBeenCalledWith(
        'Failed to flush error reports:',
        error
      );
    });
  });
});
