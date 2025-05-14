import { API_METRICS } from '../../shared/constants/api';
import { type Metric, onCLS, onFID, onFCP, onLCP, onTTFB } from 'web-vitals';

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  tags?: Record<string, string>;
}

interface ThresholdConfig {
  metric: string;
  warning: number;
  critical: number;
}

export class PerformanceOptimizer {
  private static instance: PerformanceOptimizer;
  private metrics: PerformanceMetric[] = [];
  private thresholds: ThresholdConfig[] = [];
  private webVitalsHandler?: (metric: Metric) => void;
  private isEnabled: boolean = API_METRICS.ENABLE_PERFORMANCE_TRACKING;
  private sampleRate: number = API_METRICS.TRACKING_SAMPLE_RATE;

  private constructor() {
    this.initializeWebVitals();
    this.initializeDefaultThresholds();
  }

  public static getInstance(): PerformanceOptimizer {
    if (!PerformanceOptimizer.instance) {
      PerformanceOptimizer.instance = new PerformanceOptimizer();
    }
    return PerformanceOptimizer.instance;
  }

  private initializeWebVitals(): void {
    if (!this.isEnabled) return;

    this.webVitalsHandler = (metric: Metric) => {
      this.recordMetric({
        name: `web_vitals_${metric.name.toLowerCase()}`,
        value: metric.value,
        timestamp: Date.now(),
        tags: {
          id: metric.id,
          navigationType: metric.navigationType || 'unknown'
        }
      });
    };

    onCLS(this.webVitalsHandler);
    onFID(this.webVitalsHandler);
    onFCP(this.webVitalsHandler);
    onLCP(this.webVitalsHandler);
    onTTFB(this.webVitalsHandler);
  }

  private initializeDefaultThresholds(): void {
    this.thresholds = [
      { metric: 'web_vitals_cls', warning: 0.1, critical: 0.25 },
      { metric: 'web_vitals_fid', warning: 100, critical: 300 },
      { metric: 'web_vitals_fcp', warning: 1800, critical: 3000 },
      { metric: 'web_vitals_lcp', warning: 2500, critical: 4000 },
      { metric: 'web_vitals_ttfb', warning: 600, critical: 1000 },
      { metric: 'memory_usage', warning: 80, critical: 90 },
      { metric: 'cpu_usage', warning: 70, critical: 85 },
      { metric: 'response_time', warning: 1000, critical: 3000 }
    ];
  }

  public recordMetric(metric: PerformanceMetric): void {
    if (!this.isEnabled || Math.random() > this.sampleRate) return;

    this.metrics.push({
      ...metric,
      timestamp: metric.timestamp || Date.now()
    });

    this.checkThresholds(metric);
  }

  public measureExecutionTime<T>(
    operation: () => T,
    metricName: string,
    tags?: Record<string, string>
  ): T {
    if (!this.isEnabled) return operation();

    const start = performance.now();
    try {
      return operation();
    } finally {
      const duration = performance.now() - start;
      this.recordMetric({
        name: metricName,
        value: duration,
        timestamp: Date.now(),
        tags
      });
    }
  }

  public async measureAsyncExecutionTime<T>(
    operation: () => Promise<T>,
    metricName: string,
    tags?: Record<string, string>
  ): Promise<T> {
    if (!this.isEnabled) return operation();

    const start = performance.now();
    try {
      return await operation();
    } finally {
      const duration = performance.now() - start;
      this.recordMetric({
        name: metricName,
        value: duration,
        timestamp: Date.now(),
        tags
      });
    }
  }

  private checkThresholds(metric: PerformanceMetric): void {
    const threshold = this.thresholds.find(t => t.metric === metric.name);
    if (!threshold) return;

    if (metric.value >= threshold.critical) {
      console.error(`Critical threshold exceeded for ${metric.name}: ${metric.value}`);
      // TODO: Implement alert system integration
    } else if (metric.value >= threshold.warning) {
      console.warn(`Warning threshold exceeded for ${metric.name}: ${metric.value}`);
    }
  }

  public getMetrics(
    name?: string,
    startTime?: number,
    endTime?: number
  ): PerformanceMetric[] {
    let filtered = this.metrics;

    if (name) {
      filtered = filtered.filter(m => m.name === name);
    }

    if (startTime) {
      filtered = filtered.filter(m => m.timestamp >= startTime);
    }

    if (endTime) {
      filtered = filtered.filter(m => m.timestamp <= endTime);
    }

    return filtered;
  }

  public getMetricStatistics(
    name: string,
    startTime?: number,
    endTime?: number
  ): {
    min: number;
    max: number;
    avg: number;
    count: number;
    p95: number;
  } {
    const metrics = this.getMetrics(name, startTime, endTime);
    if (!metrics.length) {
      return { min: 0, max: 0, avg: 0, count: 0, p95: 0 };
    }

    const values = metrics.map(m => m.value).sort((a, b) => a - b);
    const sum = values.reduce((a, b) => a + b, 0);
    const p95Index = Math.floor(values.length * 0.95);

    return {
      min: values[0],
      max: values[values.length - 1],
      avg: sum / values.length,
      count: values.length,
      p95: values[p95Index]
    };
  }

  public setThreshold(threshold: ThresholdConfig): void {
    const index = this.thresholds.findIndex(t => t.metric === threshold.metric);
    if (index >= 0) {
      this.thresholds[index] = threshold;
    } else {
      this.thresholds.push(threshold);
    }
  }

  public clearMetrics(olderThan?: number): void {
    if (olderThan) {
      const cutoff = Date.now() - olderThan;
      this.metrics = this.metrics.filter(m => m.timestamp >= cutoff);
    } else {
      this.metrics = [];
    }
  }

  public enableTracking(enabled: boolean = true): void {
    this.isEnabled = enabled;
    if (enabled) {
      this.initializeWebVitals();
    }
  }

  public setSampleRate(rate: number): void {
    this.sampleRate = Math.max(0, Math.min(1, rate));
  }
} 