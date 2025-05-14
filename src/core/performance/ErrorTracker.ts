import { PerformanceOptimizer } from './PerformanceOptimizer';
import { API_METRICS } from '../../shared/constants/api';

interface ErrorDetails {
  message: string;
  stack?: string;
  type: string;
  source: string;
  timestamp: number;
  metadata?: Record<string, string>;
}

interface ErrorPattern {
  pattern: RegExp;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  suggestedAction?: string;
}

export class ErrorTracker {
  private static instance: ErrorTracker;
  private optimizer: PerformanceOptimizer;
  private isEnabled: boolean = API_METRICS.ENABLE_ERROR_TRACKING;
  private errorPatterns: ErrorPattern[] = [];
  private readonly MAX_STORED_ERRORS = 1000;
  private recentErrors: ErrorDetails[] = [];

  private constructor() {
    this.optimizer = PerformanceOptimizer.getInstance();
    this.initializeDefaultPatterns();
    this.setupGlobalHandlers();
  }

  public static getInstance(): ErrorTracker {
    if (!ErrorTracker.instance) {
      ErrorTracker.instance = new ErrorTracker();
    }
    return ErrorTracker.instance;
  }

  private initializeDefaultPatterns(): void {
    this.errorPatterns = [
      {
        pattern: /ECONNREFUSED|ETIMEDOUT|ECONNRESET/,
        type: 'NetworkError',
        severity: 'high',
        category: 'connectivity',
        suggestedAction: 'Check network connectivity and service availability'
      },
      {
        pattern: /TypeError|ReferenceError/,
        type: 'CodeError',
        severity: 'medium',
        category: 'implementation',
        suggestedAction: 'Review code implementation and type checks'
      },
      {
        pattern: /OutOfMemory|RangeError/,
        type: 'ResourceError',
        severity: 'critical',
        category: 'resources',
        suggestedAction: 'Check resource allocation and memory usage'
      },
      {
        pattern: /Unauthorized|Forbidden|InvalidToken/,
        type: 'AuthError',
        severity: 'high',
        category: 'security',
        suggestedAction: 'Verify authentication credentials and permissions'
      }
    ];
  }

  private setupGlobalHandlers(): void {
    if (typeof window !== 'undefined') {
      // Browser environment
      window.addEventListener('error', (event) => {
        this.trackError(event.error, 'browser');
      });

      window.addEventListener('unhandledrejection', (event) => {
        this.trackError(event.reason, 'promise');
      });
    } else {
      // Node.js environment
      process.on('uncaughtException', (error) => {
        this.trackError(error, 'uncaught');
      });

      process.on('unhandledRejection', (reason) => {
        this.trackError(reason instanceof Error ? reason : new Error(String(reason)), 'promise');
      });
    }
  }

  public trackError(error: Error | unknown, source: string, metadata?: Record<string, string>): void {
    if (!this.isEnabled) return;

    const errorDetails = this.normalizeError(error, source, metadata);
    this.storeError(errorDetails);
    this.analyzeAndRecordMetrics(errorDetails);
  }

  private normalizeError(error: Error | unknown, source: string, metadata?: Record<string, string>): ErrorDetails {
    const normalizedError: ErrorDetails = {
      message: 'Unknown error',
      type: 'UnknownError',
      source,
      timestamp: Date.now(),
      metadata
    };

    if (error instanceof Error) {
      normalizedError.message = error.message;
      normalizedError.stack = error.stack;
      normalizedError.type = error.constructor.name;
    } else if (typeof error === 'string') {
      normalizedError.message = error;
      normalizedError.type = 'StringError';
    } else if (error && typeof error === 'object') {
      normalizedError.message = String(error);
      normalizedError.type = 'ObjectError';
    }

    return normalizedError;
  }

  private storeError(error: ErrorDetails): void {
    this.recentErrors.push(error);
    if (this.recentErrors.length > this.MAX_STORED_ERRORS) {
      this.recentErrors.shift();
    }
  }

  private analyzeAndRecordMetrics(error: ErrorDetails): void {
    // Find matching pattern
    const matchedPattern = this.errorPatterns.find(pattern => 
      pattern.pattern.test(error.message) || pattern.pattern.test(error.type)
    );

    const tags: Record<string, string> = {
      errorType: error.type,
      source: error.source,
      severity: matchedPattern?.severity || 'medium',
      category: matchedPattern?.category || 'unknown',
      ...error.metadata
    };

    // Record error occurrence
    this.optimizer.recordMetric({
      name: 'error_occurrence',
      value: 1,
      timestamp: error.timestamp,
      tags
    });

    // Record error by type
    this.optimizer.recordMetric({
      name: `error_by_type_${error.type.toLowerCase()}`,
      value: 1,
      timestamp: error.timestamp,
      tags
    });

    // Record error by source
    this.optimizer.recordMetric({
      name: `error_by_source_${error.source.toLowerCase()}`,
      value: 1,
      timestamp: error.timestamp,
      tags
    });
  }

  public getRecentErrors(
    type?: string,
    source?: string,
    startTime?: number,
    endTime?: number
  ): ErrorDetails[] {
    let filtered = this.recentErrors;

    if (type) {
      filtered = filtered.filter(e => e.type === type);
    }

    if (source) {
      filtered = filtered.filter(e => e.source === source);
    }

    if (startTime) {
      filtered = filtered.filter(e => e.timestamp >= startTime);
    }

    if (endTime) {
      filtered = filtered.filter(e => e.timestamp <= endTime);
    }

    return filtered;
  }

  public addErrorPattern(pattern: ErrorPattern): void {
    const existingIndex = this.errorPatterns.findIndex(p => 
      p.pattern.toString() === pattern.pattern.toString() && p.type === pattern.type
    );

    if (existingIndex >= 0) {
      this.errorPatterns[existingIndex] = pattern;
    } else {
      this.errorPatterns.push(pattern);
    }
  }

  public removeErrorPattern(type: string): void {
    this.errorPatterns = this.errorPatterns.filter(p => p.type !== type);
  }

  public enableTracking(enabled: boolean = true): void {
    this.isEnabled = enabled;
  }

  public clearErrors(): void {
    this.recentErrors = [];
  }
} 