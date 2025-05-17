export class StateVersioning {
    static currentVersion = '1.0.0';

    static tagVersion(state: any): any {
        return { ...state, __version: this.currentVersion };
    }

    static isCompatible(version: string): boolean {
        // In production, implement real compatibility logic
        return version === this.currentVersion;
    }

    static migrate(state: any, fromVersion: string): any {
        // In production, implement migration logic for each version
        if (fromVersion === this.currentVersion) return state;
        // Example: migrate from 0.9.0 to 1.0.0
        // ...
        return state;
    }
} 