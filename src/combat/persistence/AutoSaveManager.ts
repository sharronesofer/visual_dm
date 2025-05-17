import { StateSerializer } from './StateSerializer';

export class AutoSaveManager<T = any> {
    private saveFrequency: number; // in turns
    private retention: number; // max number of saves
    private saves: { timestamp: number; data: string }[] = [];
    private turnCounter = 0;

    constructor(saveFrequency: number = 1, retention: number = 5) {
        this.saveFrequency = saveFrequency;
        this.retention = retention;
    }

    onTurnStart(state: T) {
        this.turnCounter++;
        if (this.turnCounter % this.saveFrequency === 0) {
            this.save(state);
        }
    }

    save(state: T) {
        const data = StateSerializer.serialize(state);
        const timestamp = Date.now();
        this.saves.push({ timestamp, data });
        // Retention policy
        if (this.saves.length > this.retention) {
            this.saves.shift();
        }
        // In production, persist to disk or server
    }

    getLatestSave(): { timestamp: number; data: string } | undefined {
        return this.saves[this.saves.length - 1];
    }

    getAllSaves(): { timestamp: number; data: string }[] {
        return [...this.saves];
    }
} 