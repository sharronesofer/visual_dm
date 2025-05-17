import { ErrorMessage, SeverityLevel } from './ErrorMessage';

export class ErrorVisualizer {
    static printToConsole(error: ErrorMessage) {
        const color = this.getColor(error.severity);
        // eslint-disable-next-line no-console
        console.log(`%c[${error.severity}] ${error.description} ${error.suggestion ? 'Suggestion: ' + error.suggestion : ''}`,
            `color: ${color}`);
    }

    static showUIIndicator(error: ErrorMessage) {
        // Stub: Integrate with UI framework to show error indicators
        // e.g., display tooltip, modal, or highlight UI element
    }

    private static getColor(severity: SeverityLevel): string {
        switch (severity) {
            case SeverityLevel.CRITICAL: return 'red';
            case SeverityLevel.ERROR: return 'orange';
            case SeverityLevel.WARNING: return 'goldenrod';
            case SeverityLevel.INFO: return 'blue';
            default: return 'black';
        }
    }
} 