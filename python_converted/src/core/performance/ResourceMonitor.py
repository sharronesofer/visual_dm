from typing import Any, Dict


class ResourceMetrics:
    cpuUsage: float
    memoryUsage: float
    heapUsage: float
    eventLoopLag: float
class ResourceMonitor {
  private static instance: \'ResourceMonitor\'
  private optimizer: PerformanceOptimizer
  private isEnabled: bool = API_METRICS.ENABLE_PERFORMANCE_TRACKING
  private monitoringInterval?: NodeJS.Timeout
  private lastEventLoopTime: float = Date.now()
  private readonly DEFAULT_INTERVAL = 60000 
  private constructor() {
    this.optimizer = PerformanceOptimizer.getInstance()
  }
  public static getInstance(): \'ResourceMonitor\' {
    if (!ResourceMonitor.instance) {
      ResourceMonitor.instance = new ResourceMonitor()
    }
    return ResourceMonitor.instance
  }
  public startMonitoring(intervalMs: float = this.DEFAULT_INTERVAL): void {
    if (!this.isEnabled || this.monitoringInterval) return
    this.collectMetrics()
    this.monitoringInterval = setInterval(() => {
      this.collectMetrics()
    }, intervalMs)
    this.monitorEventLoopLag()
  }
  public stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = undefined
    }
  }
  private async collectMetrics(): Promise<void> {
    const metrics = await this.gatherResourceMetrics()
    this.optimizer.recordMetric({
      name: 'system_cpu_usage',
      value: metrics.cpuUsage,
      timestamp: Date.now(),
      tags: Dict[str, Any]
    })
    this.optimizer.recordMetric({
      name: 'system_memory_usage',
      value: metrics.memoryUsage,
      timestamp: Date.now(),
      tags: Dict[str, Any]
    })
    this.optimizer.recordMetric({
      name: 'system_heap_usage',
      value: metrics.heapUsage,
      timestamp: Date.now(),
      tags: Dict[str, Any]
    })
    this.optimizer.recordMetric({
      name: 'system_event_loop_lag',
      value: metrics.eventLoopLag,
      timestamp: Date.now(),
      tags: Dict[str, Any]
    })
  }
  private async gatherResourceMetrics(): Promise<ResourceMetrics> {
    const cpuUsage = os.loadavg()[0] * 100 / os.cpus().length
    const totalMemory = os.totalmem()
    const freeMemory = os.freemem()
    const memoryUsage = ((totalMemory - freeMemory) / totalMemory) * 100
    const heapStats = process.memoryUsage()
    const heapUsage = heapStats.heapUsed
    return {
      cpuUsage,
      memoryUsage,
      heapUsage,
      eventLoopLag: await this.measureEventLoopLag()
    }
  }
  private monitorEventLoopLag(): void {
    const measureLag = () => {
      const now = Date.now()
      const lag = now - this.lastEventLoopTime
      this.lastEventLoopTime = now
      setImmediate(measureLag)
    }
    this.lastEventLoopTime = Date.now()
    setImmediate(measureLag)
  }
  private measureEventLoopLag(): Promise<number> {
    return new Promise(resolve => {
      const start = Date.now()
      setImmediate(() => {
        resolve(Date.now() - start)
      })
    })
  }
  public enableMonitoring(enabled: bool = true): void {
    this.isEnabled = enabled
    if (enabled && !this.monitoringInterval) {
      this.startMonitoring()
    } else if (!enabled && this.monitoringInterval) {
      this.stopMonitoring()
    }
  }
  public setMonitoringInterval(intervalMs: float): void {
    if (this.monitoringInterval) {
      this.stopMonitoring()
      this.startMonitoring(intervalMs)
    }
  }
} 