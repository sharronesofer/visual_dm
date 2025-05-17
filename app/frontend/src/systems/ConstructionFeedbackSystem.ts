import { EventBus } from '../core/interfaces/types/events';

export class ConstructionFeedbackSystem {
    private eventBus = EventBus.getInstance();

    constructor() {
        this.eventBus.on('construction:progress', this.handleProgress);
        this.eventBus.on('construction:validationError', this.handleValidationError);
        this.eventBus.on('construction:complete', this.handleComplete);
    }

    handleProgress = (event: any) => {
        // Optionally show progress notifications or update UI
        // Example: if (event.progress.status === 'complete') trigger completion notification
        if (event.progress.status === 'complete') {
            this.eventBus.emit('construction:complete', {
                type: 'construction:complete',
                buildingId: event.buildingId,
                timestamp: Date.now(),
                source: 'ConstructionFeedbackSystem',
            });
        }
    };

    handleValidationError = (event: any) => {
        // Show error panel or toast with event.errors (array of error messages)
        // Optionally play error sound
        // Log error for debugging
        console.error('[Construction Validation Error]', event.errors);
    };

    handleComplete = (event: any) => {
        // Show notification for completed construction
        // Optionally play success sound
        // Log completion for analytics
        console.info('[Construction Complete]', event.buildingId);
    };
}

export default ConstructionFeedbackSystem; 