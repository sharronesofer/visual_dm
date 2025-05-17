export enum InteractionIntegrationEventType {
    INTERACTION_STARTED = 'interaction:started',
    INTERACTION_COMPLETED = 'interaction:completed',
    // ...add more as needed
}

export interface InteractionIntegrationEventPayload {
    initiatorId: string;
    targetId: string;
    interactionType: string;
    result?: any;
    timestamp: number;
} 