import { WeatherPerformanceMonitor, WeatherPerformanceAlertCallback } from '../WeatherPerformanceMonitor';
import { WeatherPerformanceData } from '../../interfaces/types/weather';
import { WeatherEffectPool } from '../../../systems/WeatherEffectPool';
import { WeatherCullingManager } from '../../../systems/WeatherCullingManager';

jest.useFakeTimers();

describe('WeatherPerformanceMonitor', () => {
    let monitor: WeatherPerformanceMonitor;

    beforeEach(() => {
        monitor = WeatherPerformanceMonitor.getInstance();
        monitor.clearHistory();
        monitor.stopMonitoring();
        monitor.setThresholds({ frameTime: 33, memoryUsage: 90 });
        monitor.setIntervalMs(100);
    });

    it('should buffer samples and return current metrics', async () => {
        monitor['sampleMetrics'] = jest.fn().mockImplementation(() => {
            monitor['buffer'].push({
                timestamp: Date.now(),
                frameTime: 10,
                memoryUsage: 50,
            });
        });
        monitor.startMonitoring();
        jest.advanceTimersByTime(500);
        monitor.stopMonitoring();
        const history = monitor.getHistory();
        expect(history.length).toBeGreaterThan(0);
        expect(monitor.getCurrentMetrics()).toEqual(history[history.length - 1]);
    });

    it('should trigger threshold alert callback', async () => {
        const cb = jest.fn();
        monitor.onThresholdExceeded('frameTime', cb);
        monitor['checkThresholds']({
            timestamp: Date.now(),
            frameTime: 40,
            memoryUsage: 50,
        });
        expect(cb).toHaveBeenCalledWith('frameTime', 40, 33);
    });

    it('should debounce threshold alerts', async () => {
        const cb = jest.fn();
        monitor.onThresholdExceeded('frameTime', cb);
        const now = Date.now();
        monitor['lastAlerted']['frameTime'] = now;
        monitor['debounceMs'] = 1000;
        monitor['checkThresholds']({
            timestamp: now + 500,
            frameTime: 40,
            memoryUsage: 50,
        });
        expect(cb).not.toHaveBeenCalled();
    });

    it('should allow updating thresholds and interval', () => {
        monitor.setThresholds({ frameTime: 20 });
        expect((monitor as any).thresholds.frameTime).toBe(20);
        monitor.setIntervalMs(200);
        expect((monitor as any).intervalMs).toBe(200);
    });

    it('should clear history', () => {
        monitor['buffer'].push({ timestamp: Date.now(), frameTime: 10, memoryUsage: 50 });
        monitor.clearHistory();
        expect(monitor.getHistory().length).toBe(0);
    });
});

describe('WeatherEffectPool', () => {
    // Minimal mock WeatherEffect
    const createMockEffect = (type: string): any => ({ type, value: 1, description: 'mock', });
    let pool: any;

    beforeEach(() => {
        pool = new WeatherEffectPool(2, 4);
    });

    it('should prewarm and acquire/release effects', () => {
        pool.prewarm('rain', () => createMockEffect('rain'), 2);
        expect(pool.getStats('rain').available).toBe(2);
        const eff = pool.acquire('rain', () => createMockEffect('rain'));
        expect(pool.getStats('rain').active).toBe(1);
        pool.release(eff);
        expect(pool.getStats('rain').available).toBe(2);
    });

    it('should not exceed max size when releasing', () => {
        pool.prewarm('snow', () => createMockEffect('snow'), 4);
        expect(pool.getStats('snow').available).toBe(4);
        const eff = pool.acquire('snow', () => createMockEffect('snow'));
        pool.release(eff);
        expect(pool.getStats('snow').available).toBe(4); // Should not exceed max
    });

    it('should resize pool and trim excess', () => {
        pool.prewarm('fog', () => createMockEffect('fog'), 4);
        pool.resize('fog', 2);
        expect(pool.getStats('fog').available).toBe(2);
    });
});

describe('WeatherCullingManager', () => {
    // Minimal mock WeatherEffect
    const createEffect = (type: string, x: number, y: number, z: number): any => ({ type, position: { x, y, z } });
    let cullingManager: any;
    let activeEffects: Map<string, any[]>;
    let camera: any;
    let occlusion: any;
    const config = {
        distanceThresholds: { rain: 10, snow: 20 },
        priority: { rain: 2, snow: 1 },
        frustumBuffer: 0,
        occlusionEnabled: true,
        smoothingMs: 0,
    };

    beforeEach(() => {
        activeEffects = new Map();
        camera = { isInFrustum: jest.fn(() => true) };
        occlusion = jest.fn(() => true);
        cullingManager = new WeatherCullingManager(
            config,
            activeEffects,
            camera,
            occlusion
        );
    });

    it('culls by distance', () => {
        activeEffects.set('r1', [createEffect('rain', 0, 0, 0), createEffect('rain', 20, 0, 0)]);
        const kept = cullingManager.cull('r1', { x: 0, y: 0, z: 0 });
        expect(kept.length).toBe(1);
        expect(kept[0].position.x).toBe(0);
    });

    it('culls by frustum', () => {
        camera.isInFrustum = jest.fn((pos) => pos.x < 5);
        activeEffects.set('r1', [createEffect('rain', 0, 0, 0), createEffect('rain', 10, 0, 0)]);
        const kept = cullingManager.cull('r1', { x: 0, y: 0, z: 0 });
        expect(kept.length).toBe(1);
        expect(kept[0].position.x).toBe(0);
    });

    it('culls by occlusion', () => {
        occlusion = jest.fn((effect) => effect.position.x < 5);
        cullingManager.occlusionQuery = occlusion;
        activeEffects.set('r1', [createEffect('rain', 0, 0, 0), createEffect('rain', 10, 0, 0)]);
        const kept = cullingManager.cull('r1', { x: 0, y: 0, z: 0 });
        expect(kept.length).toBe(1);
        expect(kept[0].position.x).toBe(0);
    });

    it('sorts by priority', () => {
        activeEffects.set('r1', [createEffect('rain', 0, 0, 0), createEffect('snow', 0, 0, 0)]);
        const kept = cullingManager.cull('r1', { x: 0, y: 0, z: 0 });
        expect(kept[0].type).toBe('snow'); // Lower priority value first
        expect(kept[1].type).toBe('rain');
    });
});

describe('WeatherFallbackManager', () => {
    const { WeatherFallbackManager } = require('../../../systems/WeatherFallbackManager');
    const { FallbackTier } = require('../../interfaces/types/weather');
    let monitor: any;
    let onTierChange: jest.Mock;
    let fallback: any;
    const config = {
        thresholds: {
            frameTime: { degraded: 40, emergency: 60 },
            memory: { degraded: 90, emergency: 98 },
        },
        hysteresis: 5,
        recoveryDelayMs: 1000,
    };

    beforeEach(() => {
        monitor = {
            onThresholdExceeded: jest.fn(),
            getCurrentMetrics: jest.fn(() => ({ frameTime: 0, memoryUsage: 0, gpuUsage: 0 })),
        };
        onTierChange = jest.fn();
        fallback = new WeatherFallbackManager(config, monitor, onTierChange);
    });

    it('should start at NORMAL tier', () => {
        expect(fallback.getCurrentTier()).toBe(FallbackTier.NORMAL);
    });

    it('should transition to DEGRADED and EMERGENCY based on metrics', () => {
        fallback['handlePerformanceAlert']({ frameTime: 45, memoryUsage: 80 });
        expect(fallback.getCurrentTier()).toBe(FallbackTier.DEGRADED);
        fallback['handlePerformanceAlert']({ frameTime: 65, memoryUsage: 99 });
        expect(fallback.getCurrentTier()).toBe(FallbackTier.EMERGENCY);
    });

    it('should not recover immediately due to hysteresis and recoveryDelay', () => {
        fallback['handlePerformanceAlert']({ frameTime: 65, memoryUsage: 99 });
        expect(fallback.getCurrentTier()).toBe(FallbackTier.EMERGENCY);
        fallback['lastTransition'] = Date.now() - 500;
        fallback['handlePerformanceAlert']({ frameTime: 30, memoryUsage: 50 });
        expect(fallback.getCurrentTier()).toBe(FallbackTier.EMERGENCY);
    });

    it('should recover to NORMAL after recoveryDelay and safe metrics', () => {
        fallback['handlePerformanceAlert']({ frameTime: 65, memoryUsage: 99 });
        expect(fallback.getCurrentTier()).toBe(FallbackTier.EMERGENCY);
        fallback['lastTransition'] = Date.now() - 2000;
        fallback['handlePerformanceAlert']({ frameTime: 30, memoryUsage: 50 });
        expect(fallback.getCurrentTier()).toBe(FallbackTier.NORMAL);
    });
}); 