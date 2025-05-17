import { expect } from 'chai';
import { TechnologyRequirementChecker } from '../../../../../src/buildings/upgrade/TechnologyRequirementChecker';
import { MockResearchSystem } from '../../../../../src/buildings/upgrade/integration/ResearchAdapter';

describe('TechnologyRequirementChecker Integration', () => {
    let research: MockResearchSystem;
    let checker: TechnologyRequirementChecker;
    const playerId = 'player1';

    beforeEach(() => {
        research = new MockResearchSystem();
        checker = new TechnologyRequirementChecker(research);
        research.setPlayerTechs(playerId, ['TechA']);
    });

    it('should check if player has technology', async () => {
        expect(await checker.hasTech(playerId, 'TechA')).to.be.true;
        expect(await checker.hasTech(playerId, 'TechB')).to.be.false;
    });

    it('should unlock new technology for player', async () => {
        await checker.unlockTech(playerId, 'TechB');
        expect(await checker.hasTech(playerId, 'TechB')).to.be.true;
    });
}); 