// WeatherEffectPool moved from WeatherEffectSystem.ts for testability and maintainability

import type { WeatherEffect } from '../core/interfaces/types/weather';

export class WeatherEffectPool {
    private pools: Record<string, WeatherEffect[]> = {};
    private minSize: number;
    private maxSize: number;
    private stats: Record<string, { active: number; available: number; total: number }> = {};

    constructor(minSize: number, maxSize: number) {
        this.minSize = minSize;
        this.maxSize = maxSize;
    }

    acquire(effectType: string, createFn: () => WeatherEffect): WeatherEffect {
        if (!this.pools[effectType]) this.pools[effectType] = [];
        const pool = this.pools[effectType];
        if (pool.length > 0) {
            this.stats[effectType] = this.stats[effectType] || { active: 0, available: 0, total: 0 };
            this.stats[effectType].active++;
            this.stats[effectType].available--;
            return pool.pop()!;
        }
        this.stats[effectType] = this.stats[effectType] || { active: 0, available: 0, total: 0 };
        this.stats[effectType].active++;
        this.stats[effectType].total++;
        return createFn();
    }

    release(effect: WeatherEffect): void {
        const effectType = effect.type;
        if (!this.pools[effectType]) this.pools[effectType] = [];
        const pool = this.pools[effectType];
        if (pool.length < this.maxSize) {
            pool.push(effect);
            this.stats[effectType].active--;
            this.stats[effectType].available++;
        }
    }

    prewarm(effectType: string, createFn: () => WeatherEffect, count: number): void {
        if (!this.pools[effectType]) this.pools[effectType] = [];
        const pool = this.pools[effectType];
        for (let i = pool.length; i < count && pool.length < this.maxSize; i++) {
            pool.push(createFn());
            this.stats[effectType] = this.stats[effectType] || { active: 0, available: 0, total: 0 };
            this.stats[effectType].available++;
            this.stats[effectType].total++;
        }
    }

    resize(effectType: string, newMax: number): void {
        this.maxSize = newMax;
        if (!this.pools[effectType]) return;
        const pool = this.pools[effectType];
        while (pool.length > newMax) {
            pool.pop();
            this.stats[effectType].available--;
            this.stats[effectType].total--;
        }
    }

    getStats(effectType: string) {
        return this.stats[effectType] || { active: 0, available: 0, total: 0 };
    }
} 