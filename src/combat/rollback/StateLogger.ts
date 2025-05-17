export type LogLevel = 'info' | 'warn' | 'error' | 'debug';

export class StateLogger {
    private level: LogLevel;

    constructor(level: LogLevel = 'info') {
        this.level = level;
    }

    log(message: string, data?: any, level: LogLevel = 'info') {
        if (this.shouldLog(level)) {
            if (data !== undefined) {
                console.log(`[${level.toUpperCase()}] ${message}`, data);
            } else {
                console.log(`[${level.toUpperCase()}] ${message}`);
            }
        }
    }

    diff(prev: any, next: any, context: string = '') {
        // Simple diff: log keys that changed
        const changes: string[] = [];
        for (const key in next) {
            if (JSON.stringify(prev[key]) !== JSON.stringify(next[key])) {
                changes.push(key);
            }
        }
        this.log(`State diff${context ? ' (' + context + ')' : ''}: ${changes.join(', ')}`, { prev, next }, 'debug');
    }

    setLevel(level: LogLevel) {
        this.level = level;
    }

    private shouldLog(level: LogLevel): boolean {
        const order = { error: 0, warn: 1, info: 2, debug: 3 };
        return order[level] <= order[this.level];
    }
} 