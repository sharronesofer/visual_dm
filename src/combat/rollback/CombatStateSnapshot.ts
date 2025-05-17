export class CombatStateSnapshot<T = any> {
    readonly state: T;
    readonly timestamp: number;

    constructor(state: T) {
        // Deep copy to prevent mutation
        this.state = JSON.parse(JSON.stringify(state));
        this.timestamp = Date.now();
    }

    serialize(): string {
        return JSON.stringify({ state: this.state, timestamp: this.timestamp });
    }

    static deserialize<T = any>(data: string): CombatStateSnapshot<T> {
        const obj = JSON.parse(data);
        const snapshot = new CombatStateSnapshot<T>(obj.state);
        (snapshot as any).timestamp = obj.timestamp;
        return snapshot;
    }

    clone(): CombatStateSnapshot<T> {
        return new CombatStateSnapshot<T>(this.state);
    }
} 