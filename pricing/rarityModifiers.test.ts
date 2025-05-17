import { applyRarityModifier } from './rarityModifiers.js';
import { expect } from 'chai';

describe('applyRarityModifier', () => {
    it('applies common rarity (no change)', () => {
        const price = applyRarityModifier(100, 'common');
        expect(price).to.equal(100);
    });

    it('applies uncommon rarity (average multiplier)', () => {
        const price = applyRarityModifier(100, 'uncommon');
        expect(price).to.be.within(150, 200);
    });

    it('applies rare rarity (average multiplier)', () => {
        const price = applyRarityModifier(100, 'rare');
        expect(price).to.be.within(300, 500);
    });

    it('applies epic rarity (average multiplier)', () => {
        const price = applyRarityModifier(100, 'epic');
        expect(price).to.be.within(700, 1000);
    });

    it('applies legendary rarity (average multiplier)', () => {
        const price = applyRarityModifier(100, 'legendary');
        expect(price).to.be.within(1500, 2500);
    });

    it('applies unique rarity with scarcity = 0', () => {
        const price = applyRarityModifier(100, 'unique', 0);
        expect(price).to.equal(3000);
    });

    it('applies unique rarity with scarcity = 1', () => {
        const price = applyRarityModifier(100, 'unique', 1);
        expect(price).to.equal(10000);
    });

    it('applies unique rarity with scarcity = 0.5', () => {
        const price = applyRarityModifier(100, 'unique', 0.5);
        expect(price).to.equal(6500);
    });

    it('defaults to 1x for unknown rarity', () => {
        const price = applyRarityModifier(100, 'mythic');
        expect(price).to.equal(100);
    });
}); 