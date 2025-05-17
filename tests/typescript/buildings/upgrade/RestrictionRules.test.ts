import { LocationRestriction, FactionRestriction, ResourceRestriction, RestrictionContext } from '../../../../src/buildings/upgrade/restrictions/RestrictionRules';
import { Building } from '../../../../src/buildings/upgrade/BuildingUpgradeValidator';
import { expect } from 'chai';

describe('RestrictionRules', () => {
    const building: Building = { type: 'Hut' };

    describe('LocationRestriction', () => {
        it('allows upgrade if location is allowed', () => {
            const restriction = new LocationRestriction(['Forest', 'Plains']);
            const context: RestrictionContext = { location: 'Forest' };
            expect(restriction.isAllowed(building, context)).to.be.true;
        });
        it('blocks upgrade if location is not allowed', () => {
            const restriction = new LocationRestriction(['Forest', 'Plains']);
            const context: RestrictionContext = { location: 'Desert' };
            expect(restriction.isAllowed(building, context)).to.be.false;
        });
    });

    describe('FactionRestriction', () => {
        it('allows upgrade if faction is allowed', () => {
            const restriction = new FactionRestriction(['Elves', 'Humans']);
            const context: RestrictionContext = { faction: 'Elves' };
            expect(restriction.isAllowed(building, context)).to.be.true;
        });
        it('blocks upgrade if faction is not allowed', () => {
            const restriction = new FactionRestriction(['Elves', 'Humans']);
            const context: RestrictionContext = { faction: 'Orcs' };
            expect(restriction.isAllowed(building, context)).to.be.false;
        });
    });

    describe('ResourceRestriction', () => {
        it('allows upgrade if resources are sufficient', () => {
            const restriction = new ResourceRestriction({ wood: 10, stone: 5 });
            const context: RestrictionContext = { resources: { wood: 20, stone: 10 } };
            expect(restriction.isAllowed(building, context)).to.be.true;
        });
        it('blocks upgrade if resources are insufficient', () => {
            const restriction = new ResourceRestriction({ wood: 10, stone: 5 });
            const context: RestrictionContext = { resources: { wood: 5, stone: 2 } };
            expect(restriction.isAllowed(building, context)).to.be.false;
        });
    });
}); 