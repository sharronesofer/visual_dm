export class StateSerializer {
    static serialize(state: any): string {
        // For now, use JSON.stringify. In production, handle circular refs and custom types.
        try {
            return JSON.stringify(state);
        } catch (e) {
            throw new Error('Failed to serialize state: ' + e);
        }
    }

    static deserialize<T = any>(data: string): T {
        try {
            return JSON.parse(data) as T;
        } catch (e) {
            throw new Error('Failed to deserialize state: ' + e);
        }
    }

    static validate(state: any): boolean {
        // Add custom validation logic as needed
        return state !== undefined && state !== null;
    }
} 