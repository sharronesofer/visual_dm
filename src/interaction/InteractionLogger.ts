type LogLevel = 'info' | 'warn' | 'error' | 'debug';

export class InteractionLogger {
    private static debugMode: boolean = process.env.INTERACTION_DEBUG === 'true';

    static setDebugMode(enabled: boolean) {
        InteractionLogger.debugMode = enabled;
    }

    static info(message: string, ...args: any[]) {
        console.info(`[Interaction][INFO] ${message}`, ...args);
    }

    static warn(message: string, ...args: any[]) {
        console.warn(`[Interaction][WARN] ${message}`, ...args);
    }

    static error(message: string, ...args: any[]) {
        console.error(`[Interaction][ERROR] ${message}`, ...args);
    }

    static debug(message: string, ...args: any[]) {
        if (InteractionLogger.debugMode) {
            console.debug(`[Interaction][DEBUG] ${message}`, ...args);
        }
    }
} 