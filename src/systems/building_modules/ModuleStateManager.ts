import { BuildingModule, ModuleState } from './BuildingModule';

export interface ModuleStateChange {
    timestamp: number;
    previousState: ModuleState;
    newState: ModuleState;
    cause: string;
}

export interface ModuleStateObserver {
    onStateChange(module: BuildingModule, change: ModuleStateChange): void;
}

export class ModuleStateHistory {
    private history: ModuleStateChange[] = [];

    record(change: ModuleStateChange) {
        this.history.push(change);
    }

    getHistory(): ModuleStateChange[] {
        return [...this.history];
    }

    prune(beforeTimestamp: number) {
        this.history = this.history.filter(h => h.timestamp >= beforeTimestamp);
    }
}

export class ModuleStateManager {
    private observers: Set<ModuleStateObserver> = new Set();
    private history: ModuleStateHistory = new ModuleStateHistory();

    constructor(private module: BuildingModule) { }

    addObserver(observer: ModuleStateObserver) {
        this.observers.add(observer);
    }

    removeObserver(observer: ModuleStateObserver) {
        this.observers.delete(observer);
    }

    private notify(change: ModuleStateChange) {
        for (const observer of this.observers) {
            observer.onStateChange(this.module, change);
        }
    }

    applyDamage(amount: number, cause: string = 'damage') {
        const prevState = this.module.currentState;
        this.module.applyDamage(amount);
        this.handleStateChange(prevState, cause);
    }

    applyRepair(amount: number, cause: string = 'repair') {
        const prevState = this.module.currentState;
        this.module.repair(amount);
        this.handleStateChange(prevState, cause);
    }

    applyDeterioration(timeElapsed: number, cause: string = 'deterioration') {
        const prevState = this.module.currentState;
        this.module.deteriorate(timeElapsed);
        this.handleStateChange(prevState, cause);
    }

    private handleStateChange(prevState: ModuleState, cause: string) {
        const newState = this.module.currentState;
        if (newState !== prevState) {
            const change: ModuleStateChange = {
                timestamp: Date.now(),
                previousState: prevState,
                newState,
                cause,
            };
            this.history.record(change);
            this.notify(change);
        }
    }

    getHistory(): ModuleStateChange[] {
        return this.history.getHistory();
    }

    // Analytics example: Mean Time Between Failures (MTBF)
    calculateMTBF(): number | null {
        const failures = this.history.getHistory().filter(h => h.newState === ModuleState.DESTROYED);
        if (failures.length < 2) return null;
        let total = 0;
        for (let i = 1; i < failures.length; i++) {
            total += failures[i].timestamp - failures[i - 1].timestamp;
        }
        return total / (failures.length - 1);
    }

    // Health trend analysis (returns array of {timestamp, health})
    getHealthTrend(): { timestamp: number; health: number }[] {
        // For simplicity, just return state change timestamps and health at those times
        return this.history.getHistory().map(h => ({
            timestamp: h.timestamp,
            health: this.module.health,
        }));
    }

    // Serialization
    serialize(): any {
        return {
            history: this.history.getHistory(),
        };
    }

    static deserialize(module: BuildingModule, data: any): ModuleStateManager {
        const manager = new ModuleStateManager(module);
        if (data && Array.isArray(data.history)) {
            for (const h of data.history) {
                manager.history.record(h);
            }
        }
        return manager;
    }
} 