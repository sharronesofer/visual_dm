import { StateSerializer } from './StateSerializer';
import { AutoSaveManager } from './AutoSaveManager';

export class RecoveryManager<T = any> {
    private autoSaveManager: AutoSaveManager<T>;
    private lastRecovered: number | null = null;

    constructor(autoSaveManager: AutoSaveManager<T>) {
        this.autoSaveManager = autoSaveManager;
    }

    detectCrash(): boolean {
        // Stub: In production, check for abnormal shutdowns, incomplete writes, etc.
        return false;
    }

    recover(): T | null {
        const latest = this.autoSaveManager.getLatestSave();
        if (latest) {
            try {
                const state = StateSerializer.deserialize<T>(latest.data);
                this.lastRecovered = latest.timestamp;
                this.log('Recovery successful', { timestamp: latest.timestamp });
                return state;
            } catch (e) {
                this.log('Recovery failed', { error: e });
                return null;
            }
        }
        this.log('No save available for recovery');
        return null;
    }

    log(message: string, data?: any) {
        // In production, use a proper logger
        // eslint-disable-next-line no-console
        console.log(`[RecoveryManager] ${message}`, data || '');
    }
} 