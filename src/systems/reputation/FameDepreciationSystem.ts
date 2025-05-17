import { ReputationManager } from '../../managers/ReputationManager';

export class FameDepreciationSystem {
    private manager: ReputationManager;

    constructor() {
        this.manager = ReputationManager.getInstance();
    }

    public applyFameDecay(currentTime: Date): void {
        const reputations = this.manager.getAllReputations();
        for (const rep of reputations) {
            if (rep.legendaryAchievements && rep.legendaryAchievements.length > 0) {
                // Legendary achievements prevent decay
                continue;
            }
            const timeSinceUpdate = (currentTime.getTime() - rep.lastUpdated.getTime()) / (1000 * 60 * 60 * 24); // days
            if (timeSinceUpdate > 0) {
                const decayRate = this.getDecayRate(rep.fame);
                const regionalModifier = this.getRegionalModifier(rep.factionId);
                const decay = decayRate * timeSinceUpdate * regionalModifier;
                rep.fame = Math.max(0, rep.fame - decay);
            }
        }
    }

    private getDecayRate(fame: number): number {
        // Higher fame decays slower
        if (fame > 80) return 0.1;
        if (fame > 50) return 0.2;
        return 0.5;
    }

    private getRegionalModifier(factionId: string): number {
        // TODO: Implement regional fame logic, for now return 1
        return 1;
    }
} 