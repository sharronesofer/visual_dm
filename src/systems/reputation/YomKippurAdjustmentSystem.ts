import { ReputationManager } from '../../managers/ReputationManager';

export class YomKippurAdjustmentSystem {
    private manager: ReputationManager;

    constructor() {
        this.manager = ReputationManager.getInstance();
    }

    public applyPeriodicAdjustment(currentDate: Date): void {
        if (this.isYomKippur(currentDate)) {
            const reputations = this.manager.getAllReputations();
            for (const rep of reputations) {
                const forgiveness = this.getForgivenessFactor(rep.factionId);
                if (rep.moral < 0) {
                    rep.moral = Math.floor(rep.moral * (1 - forgiveness));
                }
                // Optionally notify player of adjustment
            }
        }
    }

    public playerAtonement(factionId: string): void {
        const rep = this.manager.getReputation(factionId);
        if (rep && rep.moral < 0) {
            const forgiveness = this.getForgivenessFactor(factionId) * 1.5; // More generous for player-initiated
            rep.moral = Math.floor(rep.moral * (1 - forgiveness));
        }
    }

    private isYomKippur(date: Date): boolean {
        // TODO: Implement game world calendar logic; for now, use a fixed date
        return date.getMonth() === 8 && date.getDate() === 25; // September 25th as placeholder
    }

    private getForgivenessFactor(factionId: string): number {
        // TODO: Implement faction-specific forgiveness rules
        // For now, return 0.5 (50% forgiveness)
        return 0.5;
    }
} 