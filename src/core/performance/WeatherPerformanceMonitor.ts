import { WeatherPerformanceData, WeatherPerformanceThresholds } from '../interfaces/types/weather';
import { ResourceMonitor } from './ResourceMonitor';

// Circular buffer utility
class CircularBuffer<T> {
    private buffer: T[];
    private maxSize: number;
    private pointer: number = 0;
    private filled: boolean = false;

    constructor(size: number) {
        this.maxSize = size;
        this.buffer = new Array(size);
    }

    push(item: T) {
        this.buffer[this.pointer] = item;
        this.pointer = (this.pointer + 1) % this.maxSize;
        if (this.pointer === 0) this.filled = true;
    }

    getAll(): T[] {
        return this.filled
            ? [...this.buffer.slice(this.pointer), ...this.buffer.slice(0, this.pointer)]
            : this.buffer.slice(0, this.pointer);
    }

    clear() {
        this.pointer = 0;
        this.filled = false;
        this.buffer = new Array(this.maxSize);
    }
}

export type WeatherPerformanceAlertCallback = (metric: string, value: number, threshold: number) => void;

export class WeatherPerformanceMonitor {
    private static instance: WeatherPerformanceMonitor;
    private buffer: CircularBuffer<WeatherPerformanceData>;
    private intervalMs: number;
    private thresholds: WeatherPerformanceThresholds;
    private alertCallbacks: Map<string, WeatherPerformanceAlertCallback[]> = new Map();
    private monitoringTimer?: NodeJS.Timeout;
    private resourceMonitor: ResourceMonitor;
    private lastAlerted: Record<string, number> = {};
    private debounceMs: number = 2000;

    private constructor(
        bufferSize: number = 60,
        intervalMs: number = 500,
        thresholds: WeatherPerformanceThresholds = { frameTime: 33, memoryUsage: 90 }
    ) {
        this.buffer = new CircularBuffer<WeatherPerformanceData>(bufferSize);
        this.intervalMs = intervalMs;
        this.thresholds = thresholds;
        this.resourceMonitor = ResourceMonitor.getInstance();
    }

    public static getInstance(): WeatherPerformanceMonitor {
        if (!WeatherPerformanceMonitor.instance) {
            WeatherPerformanceMonitor.instance = new WeatherPerformanceMonitor();
        }
        return WeatherPerformanceMonitor.instance;
    }

    public startMonitoring(): void {
        if (this.monitoringTimer) return;
        this.monitoringTimer = setInterval(() => this.sampleMetrics(), this.intervalMs);
    }

    public stopMonitoring(): void {
        if (this.monitoringTimer) {
            clearInterval(this.monitoringTimer);
            this.monitoringTimer = undefined;
        }
    }

    private async sampleMetrics() {
        // Use ResourceMonitor for system metrics
        const metrics = await this.resourceMonitor['gatherResourceMetrics']?.() || {};
        // Simulate frame time (should be replaced with engine/game loop integration)
        const frameTime = Math.random() * 40; // Placeholder
        const data: WeatherPerformanceData = {
            timestamp: Date.now(),
            frameTime,
            memoryUsage: metrics.memoryUsage ?? 0,
            // No GPU usage available from ResourceMonitor; left undefined for future extension
            heapUsage: metrics.heapUsage,
        };
        this.buffer.push(data);
        this.checkThresholds(data);
    }

    private checkThresholds(data: WeatherPerformanceData) {
        for (const metric in this.thresholds) {
            const value = data[metric];
            const threshold = this.thresholds[metric];
            if (typeof value === 'number' && typeof threshold === 'number' && value > threshold) {
                const now = Date.now();
                if (!this.lastAlerted[metric] || now - this.lastAlerted[metric] > this.debounceMs) {
                    this.lastAlerted[metric] = now;
                    this.alertCallbacks.get(metric)?.forEach(cb => cb(metric, value, threshold));
                }
            }
        }
    }

    public onThresholdExceeded(metric: string, callback: WeatherPerformanceAlertCallback) {
        if (!this.alertCallbacks.has(metric)) {
            this.alertCallbacks.set(metric, []);
        }
        this.alertCallbacks.get(metric)!.push(callback);
    }

    public getCurrentMetrics(): WeatherPerformanceData | undefined {
        const all = this.buffer.getAll();
        return all.length > 0 ? all[all.length - 1] : undefined;
    }

    public getHistory(): WeatherPerformanceData[] {
        return this.buffer.getAll();
    }

    public setThresholds(thresholds: Partial<WeatherPerformanceThresholds>) {
        this.thresholds = { ...this.thresholds, ...thresholds };
    }

    public setIntervalMs(interval: number) {
        this.intervalMs = interval;
        if (this.monitoringTimer) {
            this.stopMonitoring();
            this.startMonitoring();
        }
    }

    public clearHistory() {
        this.buffer.clear();
    }
} 