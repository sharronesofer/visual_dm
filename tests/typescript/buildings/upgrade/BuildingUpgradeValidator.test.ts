import { BuildingUpgradeValidator, Resources, Building } from '../../../../src/buildings/upgrade/BuildingUpgradeValidator';
import { BuildingUpgradeDefinition, UpgradeCost, UpgradeRequirements, UpgradeEffects, UpgradeMetadata } from '../../../../src/buildings/upgrade/BuildingUpgradeDefinition';
import { expect } from 'chai';

describe('BuildingUpgradeValidator', () => {
    describe('validateResources', () => {
        it('returns true if player has enough resources', () => {
            const playerResources: Resources = { wood: 100, stone: 50 };
            const upgradeCost: UpgradeCost = { resources: { wood: 50, stone: 20 }, time: 10 };
            expect(BuildingUpgradeValidator.validateResources(playerResources, upgradeCost)).to.be.true;
        });
        it('returns false if player lacks resources', () => {
            const playerResources: Resources = { wood: 10, stone: 5 };
            const upgradeCost: UpgradeCost = { resources: { wood: 50, stone: 20 }, time: 10 };
            expect(BuildingUpgradeValidator.validateResources(playerResources, upgradeCost)).to.be.false;
        });
    });

    describe('validateTechRequirements', () => {
        it('returns true if player tech level is sufficient', () => {
            expect(BuildingUpgradeValidator.validateTechRequirements(3, 2)).to.be.true;
        });
        it('returns false if player tech level is too low', () => {
            expect(BuildingUpgradeValidator.validateTechRequirements(1, 2)).to.be.false;
        });
    });

    describe('validatePrerequisites', () => {
        it('returns true if all prerequisites are present', () => {
            const playerBuildings: Building[] = [{ type: 'Hut' }, { type: 'Farm' }];
            expect(BuildingUpgradeValidator.validatePrerequisites(playerBuildings, ['Hut'])).to.be.true;
        });
        it('returns false if any prerequisite is missing', () => {
            const playerBuildings: Building[] = [{ type: 'Hut' }];
            expect(BuildingUpgradeValidator.validatePrerequisites(playerBuildings, ['Hut', 'Farm'])).to.be.false;
        });
    });

    describe('canUpgrade', () => {
        it('returns success if all checks pass', () => {
            const building: Building = { type: 'Hut' };
            const cost: UpgradeCost = { resources: { wood: 10 }, time: 5 };
            const requirements: UpgradeRequirements = { techLevel: 1, prerequisites: ['Hut'] };
            const effects: UpgradeEffects = { statChanges: {}, newCapabilities: [] };
            const metadata: UpgradeMetadata = { description: '', upgradeLevel: 1 };
            const upgrade = new BuildingUpgradeDefinition('id', 'Hut', 'House', cost, requirements, effects, metadata);
            const playerResources: Resources = { wood: 20 };
            const playerTechLevel = 2;
            const playerBuildings: Building[] = [{ type: 'Hut' }];
            const result = BuildingUpgradeValidator.canUpgrade(building, upgrade, playerResources, playerTechLevel, playerBuildings);
            expect(result.success).to.be.true;
            expect(result.errors).to.be.undefined;
        });
        it('returns errors if checks fail', () => {
            const building: Building = { type: 'Hut' };
            const cost: UpgradeCost = { resources: { wood: 100 }, time: 5 };
            const requirements: UpgradeRequirements = { techLevel: 3, prerequisites: ['Farm'] };
            const effects: UpgradeEffects = { statChanges: {}, newCapabilities: [] };
            const metadata: UpgradeMetadata = { description: '', upgradeLevel: 1 };
            const upgrade = new BuildingUpgradeDefinition('id', 'Hut', 'House', cost, requirements, effects, metadata);
            const playerResources: Resources = { wood: 10 };
            const playerTechLevel = 1;
            const playerBuildings: Building[] = [{ type: 'Hut' }];
            const result = BuildingUpgradeValidator.canUpgrade(building, upgrade, playerResources, playerTechLevel, playerBuildings);
            expect(result.success).to.be.false;
            expect(result.errors).to.include('Insufficient resources');
            expect(result.errors).to.include('Tech level too low');
            expect(result.errors).to.include('Missing prerequisite buildings');
        });
    });
}); 