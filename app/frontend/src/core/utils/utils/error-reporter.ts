import { BaseError } from '../types/errors';
import { formatError, sanitizeErrorForClient } from './error-utils';
import { logger } from './logger';

/**
 * Error report data interface
 */
export interface ErrorReport {
  error: Error;
  timestamp: string;
  tags?: Record<string, string>;
  extra?: Record<string, any>;
  user?: {
    id?: string;
    email?: string;
    [key: string]: any;
  };
  session?: {
    id: string;
    startTime: string;
    [key: string]: any;
  };
  context?: {
    environment: string;
    version: string;
    [key: string]: any;
  };
}

/**
 * Error reporter backend interface
 */
export interface ErrorReporterBackend {
  name: string;
  report(data: ErrorReport): Promise<void>;
  flush?(): Promise<void>;
}

/**
 * Error reporter options interface
 */
export interface ErrorReporterOptions {
  backends?: ErrorReporterBackend[];
  sampleRate?: number;
  maxBatchSize?: number;
  batchTimeout?: number;
  includePrivateData?: boolean;
  filterFn?: (error: Error) => boolean;
  contextProvider?: () => Record<string, any>;
  userProvider?: () => Record<string, any> | null;
  sessionProvider?: () => Record<string, any> | null;
  environment?: string;
  version?: string;
}

/**
 * Console error reporter backend
 */
export class ConsoleReporterBackend implements ErrorReporterBackend {
  name = 'console';

  async report(data: ErrorReport): Promise<void> {
    logger.error('Error Report:', data.error, {
      tags: data.tags,
      extra: data.extra,
      user: data.user,
      session: data.session,
      context: data.context,
    });
  }
}

/**
 * Error reporter class for handling error reporting and analytics
 */
export class ErrorReporter {
  private static instance: ErrorReporter;
  private readonly options: Required<ErrorReporterOptions>;
  private readonly backends: ErrorReporterBackend[];
  private batchQueue: ErrorReport[] = [];
  private batchTimeout: NodeJS.Timeout | null = null;

  private readonly defaultOptions: Required<ErrorReporterOptions> = {
    backends: [new ConsoleReporterBackend()],
    sampleRate: 1.0,
    maxBatchSize: 10,
    batchTimeout: 5000,
    includePrivateData: false,
    filterFn: () => true,
    contextProvider: () => ({}),
    userProvider: () => null,
    sessionProvider: () => null,
    environment: process.env.NODE_ENV || 'development',
    version: process.env.APP_VERSION || '0.0.0',
  };

  private constructor(options: ErrorReporterOptions = {}) {
    this.options = { ...this.defaultOptions, ...options };
    this.backends = this.options.backends;
  }

  /**
   * Get error reporter instance (singleton)
   */
  public static getInstance(options?: ErrorReporterOptions): ErrorReporter {
    if (!ErrorReporter.instance) {
      ErrorReporter.instance = new ErrorReporter(options);
    }
    return ErrorReporter.instance;
  }

  /**
   * Add a backend to the reporter
   */
  public addBackend(backend: ErrorReporterBackend): void {
    if (!this.backends.find(b => b.name === backend.name)) {
      this.backends.push(backend);
    }
  }

  /**
   * Remove a backend from the reporter
   */
  public removeBackend(name: string): void {
    const index = this.backends.findIndex(b => b.name === name);
    if (index !== -1) {
      this.backends.splice(index, 1);
    }
  }

  /**
   * Create an error report
   */
  private createReport(
    error: Error,
    options: {
      tags?: Record<string, string>;
      extra?: Record<string, any>;
    } = {}
  ): ErrorReport {
    const { tags, extra } = options;
    const context = this.options.contextProvider();
    const user = this.options.includePrivateData
      ? this.options.userProvider()
      : null;
    const rawSession = this.options.includePrivateData
      ? this.options.sessionProvider()
      : null;

    // Ensure session has required fields if provided
    const session = rawSession
      ? {
          id: rawSession.id || 'unknown',
          startTime: rawSession.startTime || new Date().toISOString(),
          ...rawSession,
        }
      : undefined;

    return {
      error,
      timestamp: new Date().toISOString(),
      tags,
      extra,
      user: user || undefined,
      session,
      context: {
        environment: this.options.environment,
        version: this.options.version,
        ...context,
      },
    };
  }

  /**
   * Process the batch queue
   */
  private async processBatch(): Promise<void> {
    if (this.batchQueue.length === 0) return;

    const batch = this.batchQueue.splice(0, this.options.maxBatchSize);
    const promises = this.backends.map(backend =>
      Promise.all(batch.map(report => backend.report(report)))
    );

    try {
      await Promise.all(promises);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      logger.error('Error processing error report batch:', error);
    }

    if (this.batchQueue.length > 0) {
      this.scheduleBatch();
    }
  }

  /**
   * Schedule batch processing
   */
  private scheduleBatch(): void {
    if (this.batchTimeout) return;

    this.batchTimeout = setTimeout(() => {
      this.batchTimeout = null;
      this.processBatch();
    }, this.options.batchTimeout);
  }

  /**
   * Capture and report an error
   */
  public captureException(
    error: unknown,
    options: {
      tags?: Record<string, string>;
      extra?: Record<string, any>;
    } = {}
  ): void {
    // Sample errors based on sample rate
    if (Math.random() > this.options.sampleRate) return;

    // Convert unknown error to Error object
    const errorObject =
      error instanceof Error ? error : new Error(String(error));

    // Apply error filter
    if (!this.options.filterFn(errorObject)) return;

    // Create and sanitize error report
    const report = this.createReport(errorObject, options);
    if (!this.options.includePrivateData) {
      report.error = sanitizeErrorForClient(formatError(report.error)) as Error;
    }

    // Add to batch queue
    this.batchQueue.push(report);

    // Process immediately if batch is full
    if (this.batchQueue.length >= this.options.maxBatchSize) {
      this.processBatch();
    } else {
      this.scheduleBatch();
    }
  }

  /**
   * Flush all pending reports
   */
  public async flush(): Promise<void> {
    if (this.batchTimeout) {
      clearTimeout(this.batchTimeout);
      this.batchTimeout = null;
    }

    await this.processBatch();
    await Promise.all(this.backends.map(backend => backend.flush?.()));
  }

  /**
   * Track error frequency
   */
  private errorFrequency = new Map<
    string,
    { count: number; firstSeen: Date; lastSeen: Date }
  >();

  /**
   * Update error frequency statistics
   */
  private updateErrorStats(error: Error): void {
    const key = `${error.name}:${error.message}`;
    const now = new Date();
    const stats = this.errorFrequency.get(key);

    if (stats) {
      stats.count++;
      stats.lastSeen = now;
    } else {
      this.errorFrequency.set(key, {
        count: 1,
        firstSeen: now,
        lastSeen: now,
      });
    }
  }

  /**
   * Get error frequency statistics
   */
  public getErrorStats(): Record<
    string,
    { count: number; firstSeen: string; lastSeen: string }
  > {
    const stats: Record<
      string,
      { count: number; firstSeen: string; lastSeen: string }
    > = {};

    this.errorFrequency.forEach((value, key) => {
      stats[key] = {
        count: value.count,
        firstSeen: value.firstSeen.toISOString(),
        lastSeen: value.lastSeen.toISOString(),
      };
    });

    return stats;
  }
}

/**
 * Default error reporter instance
 */
export const errorReporter = ErrorReporter.getInstance();

export default errorReporter;
