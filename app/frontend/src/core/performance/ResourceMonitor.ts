import { PerformanceOptimizer } from './PerformanceOptimizer';
import { API_METRICS } from '../../shared/constants/api';
import os from 'os';

interface ResourceMetrics {
  cpuUsage: number;
  memoryUsage: number;
  heapUsage: number;
  eventLoopLag: number;
}

export class ResourceMonitor {
  private static instance: ResourceMonitor;
  private optimizer: PerformanceOptimizer;
  private isEnabled: boolean = API_METRICS.ENABLE_PERFORMANCE_TRACKING;
  private monitoringInterval?: NodeJS.Timeout;
  private lastEventLoopTime: number = Date.now();
  private readonly DEFAULT_INTERVAL = 60000; // 1 minute

  private constructor() {
    this.optimizer = PerformanceOptimizer.getInstance();
  }

  public static getInstance(): ResourceMonitor {
    if (!ResourceMonitor.instance) {
      ResourceMonitor.instance = new ResourceMonitor();
    }
    return ResourceMonitor.instance;
  }

  public startMonitoring(intervalMs: number = this.DEFAULT_INTERVAL): void {
    if (!this.isEnabled || this.monitoringInterval) return;

    // Initial collection
    this.collectMetrics();

    // Set up interval for regular collection
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics();
    }, intervalMs);

    // Start event loop lag monitoring
    this.monitorEventLoopLag();
  }

  public stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = undefined;
    }
  }

  private async collectMetrics(): Promise<void> {
    const metrics = await this.gatherResourceMetrics();
    
    // Record CPU usage
    this.optimizer.recordMetric({
      name: 'system_cpu_usage',
      value: metrics.cpuUsage,
      timestamp: Date.now(),
      tags: { unit: 'percent' }
    });

    // Record memory usage
    this.optimizer.recordMetric({
      name: 'system_memory_usage',
      value: metrics.memoryUsage,
      timestamp: Date.now(),
      tags: { unit: 'percent' }
    });

    // Record heap usage
    this.optimizer.recordMetric({
      name: 'system_heap_usage',
      value: metrics.heapUsage,
      timestamp: Date.now(),
      tags: { unit: 'bytes' }
    });

    // Record event loop lag
    this.optimizer.recordMetric({
      name: 'system_event_loop_lag',
      value: metrics.eventLoopLag,
      timestamp: Date.now(),
      tags: { unit: 'milliseconds' }
    });
  }

  private async gatherResourceMetrics(): Promise<ResourceMetrics> {
    // Calculate CPU usage
    const cpuUsage = os.loadavg()[0] * 100 / os.cpus().length;

    // Calculate memory usage
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const memoryUsage = ((totalMemory - freeMemory) / totalMemory) * 100;

    // Get heap statistics
    const heapStats = process.memoryUsage();
    const heapUsage = heapStats.heapUsed;

    return {
      cpuUsage,
      memoryUsage,
      heapUsage,
      eventLoopLag: await this.measureEventLoopLag()
    };
  }

  private monitorEventLoopLag(): void {
    const measureLag = () => {
      const now = Date.now();
      const lag = now - this.lastEventLoopTime;
      this.lastEventLoopTime = now;
      setImmediate(measureLag);
    };

    this.lastEventLoopTime = Date.now();
    setImmediate(measureLag);
  }

  private measureEventLoopLag(): Promise<number> {
    return new Promise(resolve => {
      const start = Date.now();
      setImmediate(() => {
        resolve(Date.now() - start);
      });
    });
  }

  public enableMonitoring(enabled: boolean = true): void {
    this.isEnabled = enabled;
    if (enabled && !this.monitoringInterval) {
      this.startMonitoring();
    } else if (!enabled && this.monitoringInterval) {
      this.stopMonitoring();
    }
  }

  public setMonitoringInterval(intervalMs: number): void {
    if (this.monitoringInterval) {
      this.stopMonitoring();
      this.startMonitoring(intervalMs);
    }
  }
} 