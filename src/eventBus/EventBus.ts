import fs from 'fs';

function logEventBus(message: string) {
    // Simple file logger for demonstration; replace with a real logger in production
    fs.appendFileSync('eventbus.log', `[${new Date().toISOString()}] ${message}\n`);
}

export interface EventBus {
    emit(eventType: string, payload: any): void;
    on(eventType: string, handler: (payload: any) => void): void;
    off(eventType: string, handler: (payload: any) => void): void;
}

export class InMemoryEventBus implements EventBus {
    private listeners: Map<string, Set<(payload: any) => void>> = new Map();

    emit(eventType: string, payload: any): void {
        logEventBus(`Emitting event: ${eventType} with payload: ${JSON.stringify(payload)}`);
        const handlers = this.listeners.get(eventType);
        if (handlers) {
            for (const handler of handlers) {
                setTimeout(() => {
                    try {
                        handler(payload);
                    } catch (err) {
                        logEventBus(`Error in handler for event ${eventType}: ${err}`);
                    }
                }, 0);
            }
        }
    }

    on(eventType: string, handler: (payload: any) => void): void {
        logEventBus(`Registering handler for event: ${eventType}`);
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, new Set());
        }
        this.listeners.get(eventType)!.add(handler);
    }

    off(eventType: string, handler: (payload: any) => void): void {
        logEventBus(`Unregistering handler for event: ${eventType}`);
        this.listeners.get(eventType)?.delete(handler);
    }
}

// Singleton instance for app-wide use
export const eventBus = new InMemoryEventBus(); 