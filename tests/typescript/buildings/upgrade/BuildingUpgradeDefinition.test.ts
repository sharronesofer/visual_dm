import { BuildingUpgradeDefinition, UpgradeCost, UpgradeRequirements, UpgradeEffects, UpgradeMetadata } from '../../../../src/buildings/upgrade/BuildingUpgradeDefinition';
import { expect } from 'chai';

describe('BuildingUpgradeDefinition', () => {
    it('should construct with all properties correctly assigned', () => {
        const cost: UpgradeCost = { resources: { wood: 100, stone: 50 }, time: 60 };
        const requirements: UpgradeRequirements = { techLevel: 2, prerequisites: ['Hut'], otherConditions: [] };
        const effects: UpgradeEffects = { statChanges: { defense: 10 }, newCapabilities: ['Fireproof'] };
        const metadata: UpgradeMetadata = { description: 'Upgrade hut to house', upgradeLevel: 1 };

        const upgrade = new BuildingUpgradeDefinition(
            'hut-to-house',
            'Hut',
            'House',
            cost,
            requirements,
            effects,
            metadata
        );

        expect(upgrade.id).to.equal('hut-to-house');
        expect(upgrade.from).to.equal('Hut');
        expect(upgrade.to).to.equal('House');
        expect(upgrade.cost).to.deep.equal(cost);
        expect(upgrade.requirements).to.deep.equal(requirements);
        expect(upgrade.effects).to.deep.equal(effects);
        expect(upgrade.metadata).to.deep.equal(metadata);
    });
}); 