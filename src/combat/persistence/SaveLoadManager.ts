import { StateSerializer } from './StateSerializer';

export interface SaveFileMeta {
    timestamp: number;
    version: string;
    summary: string;
}

export class SaveLoadManager<T = any> {
    private saves: { meta: SaveFileMeta; data: string }[] = [];
    private version: string;

    constructor(version: string = '1.0.0') {
        this.version = version;
    }

    save(state: T, summary: string) {
        const data = StateSerializer.serialize(state);
        const meta: SaveFileMeta = {
            timestamp: Date.now(),
            version: this.version,
            summary,
        };
        this.saves.push({ meta, data });
        // In production, persist to disk or server
    }

    load(index: number): T | null {
        if (index >= 0 && index < this.saves.length) {
            try {
                return StateSerializer.deserialize<T>(this.saves[index].data);
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    getSaveFiles(): SaveFileMeta[] {
        return this.saves.map(s => s.meta);
    }

    // Stub: UI integration for browsing and selecting saves
    showSaveBrowser() {
        // Integrate with UI framework
    }
} 