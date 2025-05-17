import {
    volumeSpikeThreshold,
    priceMoveZScoreThreshold,
    repetitiveTradeThreshold,
    alertLevels
} from './marketManipulationConfig.js';

export interface Trade {
    timestamp: number;
    price: number;
    volume: number;
    itemId: string;
    regionId: string;
    traderId: string;
}

export interface DetectionResult {
    alertLevel: number;
    reason: string;
    details?: any;
}

export function movingAverage(values: number[], window: number): number {
    if (values.length < window) return NaN;
    return values.slice(-window).reduce((a, b) => a + b, 0) / window;
}

export function standardDeviation(values: number[], window: number): number {
    if (values.length < window) return NaN;
    const avg = movingAverage(values, window);
    const slice = values.slice(-window);
    const variance = slice.reduce((sum, v) => sum + (v - avg) ** 2, 0) / window;
    return Math.sqrt(variance);
}

export function zScore(value: number, mean: number, std: number): number {
    if (std === 0) return 0;
    return (value - mean) / std;
}

export function detectVolumeSpike(trades: Trade[], window: number = 20): DetectionResult | null {
    const volumes = trades.map(t => t.volume);
    const avg = movingAverage(volumes, window);
    const latest = volumes[volumes.length - 1];
    if (avg > 0 && latest > avg * volumeSpikeThreshold) {
        return { alertLevel: alertLevels.critical, reason: 'Volume spike', details: { latest, avg } };
    }
    return null;
}

export function detectPriceAnomaly(trades: Trade[], window: number = 20): DetectionResult | null {
    const prices = trades.map(t => t.price);
    const avg = movingAverage(prices, window);
    const std = standardDeviation(prices, window);
    const latest = prices[prices.length - 1];
    const z = zScore(latest, avg, std);
    if (Math.abs(z) > priceMoveZScoreThreshold) {
        return { alertLevel: alertLevels.warning, reason: 'Abnormal price movement', details: { latest, avg, std, z } };
    }
    return null;
}

export function detectRepetitiveTrades(trades: Trade[], window: number = 10): DetectionResult | null {
    if (trades.length < window) return null;
    const recent = trades.slice(-window);
    const uniqueTraders = new Set(recent.map(t => t.traderId));
    if (uniqueTraders.size === 1) {
        return { alertLevel: alertLevels.warning, reason: 'Repetitive trades by single trader', details: { traderId: recent[0].traderId } };
    }
    return null;
}

export function runManipulationDetection(trades: Trade[]): DetectionResult[] {
    const results: DetectionResult[] = [];
    const volume = detectVolumeSpike(trades);
    if (volume) results.push(volume);
    const price = detectPriceAnomaly(trades);
    if (price) results.push(price);
    const repetitive = detectRepetitiveTrades(trades);
    if (repetitive) results.push(repetitive);
    return results;
}

export class CircuitBreaker {
    tripped: boolean = false;
    reason: string = '';
    trip(reason: string) {
        this.tripped = true;
        this.reason = reason;
    }
    reset() {
        this.tripped = false;
        this.reason = '';
    }
}

export function moderatorDashboard(results: DetectionResult[], trades: Trade[]): void {
    // Stub: In a real system, this would be a UI/dashboard
    for (const result of results) {
        console.log(`[ALERT] Level ${result.alertLevel}: ${result.reason}`, result.details);
    }
    // Optionally, print recent trades
    // console.table(trades.slice(-10));
} 