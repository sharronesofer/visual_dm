import { PerformanceOptimizer } from './PerformanceOptimizer';
import { API_METRICS } from '../../shared/constants/api';

interface APIResponse {
  status?: number;
}

interface APIMetricTags {
  endpoint: string;
  method: string;
  statusCode?: string;
  error?: string;
  success?: string;
  statusGroup?: string;
}

export class APIMetricsCollector {
  private static instance: APIMetricsCollector;
  private optimizer: PerformanceOptimizer;
  private isEnabled: boolean = API_METRICS.ENABLE_API_METRICS;

  private constructor() {
    this.optimizer = PerformanceOptimizer.getInstance();
  }

  public static getInstance(): APIMetricsCollector {
    if (!APIMetricsCollector.instance) {
      APIMetricsCollector.instance = new APIMetricsCollector();
    }
    return APIMetricsCollector.instance;
  }

  private convertToStringRecord(tags: APIMetricTags): Record<string, string> {
    const record: Record<string, string> = {};
    for (const [key, value] of Object.entries(tags)) {
      if (value !== undefined) {
        record[key] = value;
      }
    }
    return record;
  }

  public async trackAPICall<T>(
    endpoint: string,
    method: string,
    apiCall: () => Promise<T>
  ): Promise<T> {
    if (!this.isEnabled) return apiCall();

    const startTime = Date.now();
    const tags: APIMetricTags = { endpoint, method };

    try {
      const response = await apiCall();
      
      // For responses with status code
      if (response && typeof response === 'object' && 'status' in response) {
        const apiResponse = response as APIResponse;
        tags.statusCode = apiResponse.status?.toString();
      }

      this.recordAPIMetrics(startTime, tags);
      return response;
    } catch (error) {
      tags.error = error instanceof Error ? error.message : 'Unknown error';
      if (error && typeof error === 'object' && 'status' in error) {
        const errorStatus = (error as APIResponse).status;
        tags.statusCode = errorStatus?.toString() || '500';
      } else {
        tags.statusCode = '500';
      }
      
      this.recordAPIMetrics(startTime, tags);
      throw error;
    }
  }

  private recordAPIMetrics(startTime: number, tags: APIMetricTags): void {
    const duration = Date.now() - startTime;

    // Record response time
    this.optimizer.recordMetric({
      name: 'api_response_time',
      value: duration,
      timestamp: Date.now(),
      tags: this.convertToStringRecord({
        ...tags,
        success: String(!tags.error)
      })
    });

    // Record error rate metrics if applicable
    if (tags.error) {
      this.optimizer.recordMetric({
        name: 'api_error_rate',
        value: 1,
        timestamp: Date.now(),
        tags: this.convertToStringRecord(tags)
      });
    }

    // Record status code metrics
    if (tags.statusCode) {
      const statusGroup = `${Math.floor(parseInt(tags.statusCode) / 100)}xx`;
      this.optimizer.recordMetric({
        name: 'api_status_codes',
        value: 1,
        timestamp: Date.now(),
        tags: this.convertToStringRecord({
          ...tags,
          statusGroup
        })
      });
    }
  }

  public enableMetrics(enabled: boolean = true): void {
    this.isEnabled = enabled;
  }
} 