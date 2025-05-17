import { ReputationManager } from '../../managers/ReputationManager';
import { ReputationAuditLogger } from './ReputationAuditLogger';

export class ReputationSystem {
    private manager: ReputationManager;

    constructor() {
        this.manager = ReputationManager.getInstance();
    }

    public applyMoralAction(factionId: string, delta: number, context: string, source: string): void {
        // Diminishing returns: reduce effect if repeated
        const adjustedDelta = this.applyDiminishingReturns(factionId, delta, 'moral');
        this.manager.modifyMoral(factionId, adjustedDelta);
        ReputationAuditLogger.log({
            timestamp: new Date().toISOString(),
            sourceSystem: source,
            targetEntity: factionId,
            valueChange: adjustedDelta,
            context,
            callingSystem: 'ReputationSystem.applyMoralAction',
        });
        this.broadcastReputationChange(factionId, 'moral', adjustedDelta);
        this.handleThresholds(factionId);
        this.handleCrossFactionEffects(factionId, adjustedDelta, 'moral');
    }

    public applyFameAction(factionId: string, delta: number, context: string, source: string): void {
        const adjustedDelta = this.applyDiminishingReturns(factionId, delta, 'fame');
        this.manager.modifyFame(factionId, adjustedDelta);
        ReputationAuditLogger.log({
            timestamp: new Date().toISOString(),
            sourceSystem: source,
            targetEntity: factionId,
            valueChange: adjustedDelta,
            context,
            callingSystem: 'ReputationSystem.applyFameAction',
        });
        this.broadcastReputationChange(factionId, 'fame', adjustedDelta);
    }

    private applyDiminishingReturns(factionId: string, delta: number, axis: 'moral' | 'fame'): number {
        // TODO: Implement diminishing returns logic based on recent action history
        // For now, return delta unchanged
        return delta;
    }

    private handleThresholds(factionId: string): void {
        // TODO: Implement logic for triggering events when reputation crosses thresholds
    }

    private handleCrossFactionEffects(factionId: string, delta: number, axis: 'moral' | 'fame'): void {
        // TODO: Implement cross-faction reputation effects (e.g., gaining with one may lose with rivals)
    }

    private broadcastReputationChange(factionId: string, axis: 'moral' | 'fame', delta: number): void {
        // TODO: Integrate with event bus or observer pattern to notify other systems
    }
} 