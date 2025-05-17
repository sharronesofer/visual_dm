import { ReputationManager } from '../../managers/ReputationManager';
import { ReputationSystem } from '../../systems/reputation/ReputationSystem';
import { FameDepreciationSystem } from '../../systems/reputation/FameDepreciationSystem';
import { YomKippurAdjustmentSystem } from '../../systems/reputation/YomKippurAdjustmentSystem';

describe('Reputation System Integration', () => {
    let manager: ReputationManager;
    let system: ReputationSystem;
    let fameSystem: FameDepreciationSystem;
    let yomKippurSystem: YomKippurAdjustmentSystem;

    beforeEach(() => {
        manager = ReputationManager.getInstance();
        manager.reset();
        system = new ReputationSystem();
        fameSystem = new FameDepreciationSystem();
        yomKippurSystem = new YomKippurAdjustmentSystem();
        manager.setReputation('factionA', {
            factionId: 'factionA',
            moral: 0,
            fame: 50,
            lastUpdated: new Date(),
            legendaryAchievements: [],
        });
    });

    it('modifies moral and fame correctly', () => {
        system.applyMoralAction('factionA', 10, 'Test', 'TestSystem');
        system.applyFameAction('factionA', 5, 'Test', 'TestSystem');
        const rep = manager.getReputation('factionA');
        expect(rep?.moral).toBe(10);
        expect(rep?.fame).toBe(55);
    });

    it('applies fame decay over time', () => {
        const now = new Date();
        const twoDaysLater = new Date(now.getTime() + 2 * 24 * 60 * 60 * 1000);
        fameSystem.applyFameDecay(twoDaysLater);
        const rep = manager.getReputation('factionA');
        expect(rep?.fame).toBeLessThan(50);
    });

    it('applies Yom Kippur adjustment', () => {
        system.applyMoralAction('factionA', -60, 'Test', 'TestSystem');
        const yomKippur = new Date(2023, 8, 25); // September 25
        yomKippurSystem.applyPeriodicAdjustment(yomKippur);
        const rep = manager.getReputation('factionA');
        expect(rep?.moral).toBeGreaterThan(-60);
    });

    it('player atonement increases forgiveness', () => {
        system.applyMoralAction('factionA', -40, 'Test', 'TestSystem');
        yomKippurSystem.playerAtonement('factionA');
        const rep = manager.getReputation('factionA');
        expect(rep?.moral).toBeGreaterThan(-40);
    });
}); 