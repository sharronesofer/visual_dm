export enum AlertSeverity {
    INFO = 'INFO',
    WARNING = 'WARNING',
    ERROR = 'ERROR',
    CRITICAL = 'CRITICAL',
}

interface AlertOptions {
    message: string;
    severity: AlertSeverity;
    context?: Record<string, unknown>;
    channel?: 'console' | 'email' | 'slack';
}

const alertThrottle: Record<string, number> = {};
const THROTTLE_WINDOW_MS = 60_000; // 1 minute per error type/channel

export class AlertService {
    static sendAlert({ message, severity, context, channel }: AlertOptions) {
        const key = `${severity}:${channel || 'console'}:${message}`;
        const now = Date.now();
        if (alertThrottle[key] && now - alertThrottle[key] < THROTTLE_WINDOW_MS) {
            // Throttle duplicate alerts
            return;
        }
        alertThrottle[key] = now;
        // Route by severity
        switch (channel || AlertService.getDefaultChannel(severity)) {
            case 'console':
                // eslint-disable-next-line no-console
                console.error(`[ALERT][${severity}]`, message, context || '');
                break;
            case 'email':
                // TODO: Integrate real email service
                // eslint-disable-next-line no-console
                console.log(`[ALERT][EMAIL][${severity}]`, message, context || '');
                break;
            case 'slack':
                // TODO: Integrate real Slack service
                // eslint-disable-next-line no-console
                console.log(`[ALERT][SLACK][${severity}]`, message, context || '');
                break;
            default:
                // eslint-disable-next-line no-console
                console.error(`[ALERT][${severity}]`, message, context || '');
        }
    }

    static getDefaultChannel(severity: AlertSeverity): 'console' | 'email' | 'slack' {
        switch (severity) {
            case AlertSeverity.CRITICAL:
                return 'slack';
            case AlertSeverity.ERROR:
                return 'email';
            default:
                return 'console';
        }
    }
} 