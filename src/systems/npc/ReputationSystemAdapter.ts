import { EventBus, EventPriority } from '../../core/events/EventBus';
import { SceneEventType, ISceneEvent } from '../../core/events/SceneEventTypes';
import { ReputationSystem } from './ReputationSystem';
import { UnifiedApiGateway, ReputationApi } from '../../core/services/UnifiedApiGateway';
import { ReputationChangeEvent } from '../../core/events/SceneEventTypes';
import { ValidationService, ValidationContext } from '../../core/services/ValidationService';

export class ReputationSystemAdapter implements ReputationApi {
    private reputationSystem: ReputationSystem;
    private eventBus: EventBus;
    private apiGateway: UnifiedApiGateway;
    private static instance: ReputationSystemAdapter;

    private constructor(reputationSystem: ReputationSystem) {
        this.reputationSystem = reputationSystem;
        this.eventBus = EventBus.getInstance();
        this.apiGateway = UnifiedApiGateway.getInstance();
        this.registerEventHandlers();
    }

    public static getInstance(reputationSystem: ReputationSystem): ReputationSystemAdapter {
        if (!ReputationSystemAdapter.instance) {
            ReputationSystemAdapter.instance = new ReputationSystemAdapter(reputationSystem);
        }
        return ReputationSystemAdapter.instance;
    }

    private registerEventHandlers() {
        // Listen for reputation changed events
        this.eventBus.on(
            SceneEventType.REPUTATION_CHANGED,
            this.handleReputationChanged.bind(this),
            { priority: EventPriority.NORMAL }
        );
        // Listen for threshold events, status updates, etc. (customize as needed)
        // this.eventBus.on(SceneEventType.REPUTATION_THRESHOLD, ...);
    }

    private async handleReputationChanged(event: ISceneEvent) {
        // Example: Update reputation system state based on event
        const { data } = event;
        if (data && data.npcId && data.change) {
            // Implement logic to update reputation, trigger threshold events, etc.
            // await this.reputationSystem.processReputationChange(data.npcId, data.change);
        }
    }

    // Add more hooks as needed for threshold events, status updates, etc.

    public async getReputation(agentId: string): Promise<number> {
        // Use a default targetId or aggregate across all targets
        // For now, return 0 if no target is specified
        // TODO: Optionally aggregate across all targets
        return 0;
    }

    public async modifyReputation(agentId: string, delta: number): Promise<boolean> {
        const validationService = ValidationService.getInstance();
        // Pre-operation validation
        const preContext = await validationService.validateAsync('reputation', { agentId, delta });
        if (preContext.errors.length > 0) {
            // Optionally emit validation event here
            throw new Error('Validation failed before reputation change: ' + preContext.errors.join('; '));
        }
        // No direct method; emit event and return false
        const event: ReputationChangeEvent = {
            type: SceneEventType.REPUTATION_CHANGED,
            change: delta,
            reason: 'api',
            subjectId: agentId,
            source: 'ReputationSystemAdapter',
            timestamp: Date.now(),
        };
        await this.eventBus.emit(event);
        // Post-operation validation (could be after actual reputation change if implemented)
        const postContext = await validationService.validateAsync('reputation', { agentId, delta });
        if (postContext.errors.length > 0) {
            // Optionally emit validation event here
            throw new Error('Validation failed after reputation change: ' + postContext.errors.join('; '));
        }
        // TODO: Implement actual reputation modification
        return false;
    }

    public async getReputationHistory(agentId: string): Promise<any[]> {
        // Aggregate all reputation history entries for agentId
        // Not directly supported; return empty array for now
        return [];
    }
} 