from typing import Any, Dict, List


class HttpReporterConfig:
    endpoint: str
    apiKey?: str
    batchSize?: float
    retryAttempts?: float
    retryDelay?: float
    headers?: Dict[str, str>
class ErrorWithContext:
    context?: List[{
    failedReports?: ErrorReport]
}
/**
 * HTTP backend for error reporting that sends errors to a remote service
 */
class HttpReporterBackend implements ErrorReporterBackend {
  public readonly name = 'http'
  private pendingReports: List[ErrorReport] = []
  private retryTimeouts: Map<string, NodeJS.Timeout> = new Map()
  constructor(private config: HttpReporterConfig) {
    this.config = {
      batchSize: 10,
      retryAttempts: 3,
      retryDelay: 1000,
      ...config,
    }
  }
  /**
   * Reports an error to the remote service
   */
  async report(errorReport: ErrorReport): Promise<void> {
    try {
      this.pendingReports.push(errorReport)
      if (this.pendingReports.length >= this.config.batchSize!) {
        await this.processBatch()
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      logger.error('Failed to queue error report:', error)
    }
  }
  /**
   * Flushes any pending error reports
   */
  async flush(): Promise<void> {
    try {
      if (this.pendingReports.length > 0) {
        await this.processBatch()
      }
      for (const timeout of this.retryTimeouts.values()) {
        clearTimeout(timeout)
      }
      this.retryTimeouts.clear()
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      logger.error('Failed to flush error reports:', error)
    }
  }
  /**
   * Processes a batch of error reports
   */
  private async processBatch(attempt: float = 1): Promise<void> {
    if (this.pendingReports.length === 0) return
    try {
      const batch = this.pendingReports.map(report => ({
        ...report,
        error: serializeError(report.error), 
      }))
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...this.config.headers,
      }
      if (this.config.apiKey) {
        headers['Authorization'] = `Bearer ${this.config.apiKey}`
      }
      await httpClient.post(this.config.endpoint, batch, { headers })
      this.pendingReports = []
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err))
      logger.error(`Failed to send error reports (attempt ${attempt}):`, error)
      if (attempt < this.config.retryAttempts!) {
        const batchId = Date.now().toString()
        const timeout = setTimeout(() => {
          this.retryTimeouts.delete(batchId)
          this.processBatch(attempt + 1)
        }, this.config.retryDelay! * attempt) 
        this.retryTimeouts.set(batchId, timeout)
      } else {
        const contextError = new Error(
          'Failed to send error reports after all retry attempts'
        ) as ErrorWithContext
        contextError.context = {
          failedReports: this.pendingReports,
        }
        logger.error(contextError.message, contextError)
        this.pendingReports = []
      }
    }
  }
}