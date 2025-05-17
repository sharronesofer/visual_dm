// WeatherFallbackManager: Handles tiered fallback logic for weather effects under performance pressure

import { WeatherFallbackConfig, FallbackTier } from '../core/interfaces/types/weather';
import { WeatherPerformanceMonitor } from '../core/performance/WeatherPerformanceMonitor';

export class WeatherFallbackManager {
    private config: WeatherFallbackConfig;
    private currentTier: FallbackTier = FallbackTier.NORMAL;
    private monitor: WeatherPerformanceMonitor;
    private lastTransition: number = 0;
    private recoveryTimeout: NodeJS.Timeout | null = null;
    private onTierChange: (tier: FallbackTier) => void;
    private static readonly TIER_ORDER = [FallbackTier.NORMAL, FallbackTier.DEGRADED, FallbackTier.EMERGENCY];

    constructor(config: WeatherFallbackConfig, monitor: WeatherPerformanceMonitor, onTierChange: (tier: FallbackTier) => void) {
        this.config = config;
        this.monitor = monitor;
        this.onTierChange = onTierChange;
        // Register alert callbacks for each relevant metric
        this.monitor.onThresholdExceeded('frameTime', (_, value, threshold) => this.handlePerformanceAlert({ frameTime: value }));
        this.monitor.onThresholdExceeded('memoryUsage', (_, value, threshold) => this.handlePerformanceAlert({ memoryUsage: value }));
        this.monitor.onThresholdExceeded('gpuUsage', (_, value, threshold) => this.handlePerformanceAlert({ gpuUsage: value }));
    }

    private handlePerformanceAlert(metrics: any) {
        const now = Date.now();
        const currentMetrics = {
            frameTime: metrics.frameTime ?? this.monitor.getCurrentMetrics()?.frameTime ?? 0,
            memoryUsage: metrics.memoryUsage ?? this.monitor.getCurrentMetrics()?.memoryUsage ?? 0,
            gpuUsage: metrics.gpuUsage ?? this.monitor.getCurrentMetrics()?.gpuUsage ?? 0,
        };
        const { thresholds, hysteresis } = this.config;
        let newTier = FallbackTier.NORMAL;
        if (currentMetrics.frameTime > thresholds.frameTime.emergency || currentMetrics.memoryUsage > thresholds.memory.emergency || (currentMetrics.gpuUsage && currentMetrics.gpuUsage > (thresholds.gpu?.emergency ?? 100))) {
            newTier = FallbackTier.EMERGENCY;
        } else if (currentMetrics.frameTime > thresholds.frameTime.degraded || currentMetrics.memoryUsage > thresholds.memory.degraded || (currentMetrics.gpuUsage && currentMetrics.gpuUsage > (thresholds.gpu?.degraded ?? 100))) {
            newTier = FallbackTier.DEGRADED;
        }
        if (newTier !== this.currentTier) {
            const newIdx = WeatherFallbackManager.TIER_ORDER.indexOf(newTier);
            const curIdx = WeatherFallbackManager.TIER_ORDER.indexOf(this.currentTier);
            if (newIdx > curIdx) {
                this.setTier(newTier);
            } else if (now - this.lastTransition > this.config.recoveryDelayMs) {
                if (this.isRecoverySafe(currentMetrics)) {
                    this.setTier(newTier);
                }
            }
        }
    }

    private isRecoverySafe(metrics: any): boolean {
        const { frameTime, memoryUsage, gpuUsage } = metrics;
        const { thresholds, hysteresis } = this.config;
        // Only recover if all metrics are below (degraded - hysteresis)
        return (
            frameTime < thresholds.frameTime.degraded - hysteresis &&
            memoryUsage < thresholds.memory.degraded - hysteresis &&
            (!thresholds.gpu || (gpuUsage ?? 0) < (thresholds.gpu.degraded ?? 100) - hysteresis)
        );
    }

    private setTier(tier: FallbackTier) {
        this.currentTier = tier;
        this.lastTransition = Date.now();
        this.onTierChange(tier);
    }

    public getCurrentTier(): FallbackTier {
        return this.currentTier;
    }

    public setConfig(config: WeatherFallbackConfig) {
        this.config = config;
    }

    /**
     * Set fallback thresholds at runtime (for config/preset updates).
     */
    public setThresholds(thresholds: WeatherFallbackConfig['thresholds']) {
        this.config.thresholds = { ...thresholds };
        // Optionally, trigger logic to re-evaluate current tier
    }
} 