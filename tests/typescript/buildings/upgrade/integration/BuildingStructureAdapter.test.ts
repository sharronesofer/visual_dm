import { expect } from 'chai';
import { MockBuildingStructureSystem } from '../../../../../src/buildings/upgrade/integration/BuildingStructureAdapter';

describe('MockBuildingStructureSystem Integration', () => {
    let system: MockBuildingStructureSystem;
    const buildingId = 'b1';

    beforeEach(() => {
        system = new MockBuildingStructureSystem();
    });

    it('should apply and track upgrades', async () => {
        await system.applyUpgrade(buildingId, 'UpgradeA');
        await system.applyUpgrade(buildingId, 'UpgradeB');
        expect(system.getUpgrades(buildingId)).to.deep.equal(['UpgradeA', 'UpgradeB']);
    });

    it('should apply and track downgrades', async () => {
        await system.applyDowngrade(buildingId, 'DowngradeA');
        expect(system.getDowngrades(buildingId)).to.deep.equal(['DowngradeA']);
    });

    it('should return empty arrays for buildings with no upgrades/downgrades', () => {
        expect(system.getUpgrades('unknown')).to.deep.equal([]);
        expect(system.getDowngrades('unknown')).to.deep.equal([]);
    });
}); 