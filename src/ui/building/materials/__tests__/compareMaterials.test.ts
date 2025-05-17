import { describe, it, expect } from 'vitest';
import { compareMaterials } from '../compareMaterials';
import { Material } from '../types';

describe('compareMaterials', () => {
    const wood: Material = {
        id: 'wood',
        name: 'Wood',
        durability: 50,
        cost: 10,
        aesthetics: 60,
        specialProperties: [
            { name: 'flammable', value: 'yes', description: 'Can catch fire easily.' }
        ]
    };
    const stone: Material = {
        id: 'stone',
        name: 'Stone',
        durability: 90,
        cost: 25,
        aesthetics: 70,
        specialProperties: [
            { name: 'fire_resistant', value: 'yes', description: 'Resistant to fire.' },
            { name: 'flammable', value: 'no', description: 'Does not catch fire.' }
        ]
    };

    it('compares core properties', () => {
        const results = compareMaterials(wood, stone);
        expect(results.find(r => r.property === 'durability')?.difference).toBe(40);
        expect(results.find(r => r.property === 'cost')?.difference).toBe(15);
        expect(results.find(r => r.property === 'aesthetics')?.difference).toBe(10);
    });

    it('compares shared special properties', () => {
        const results = compareMaterials(wood, stone);
        const flammable = results.find(r => r.property === 'flammable');
        expect(flammable?.aValue).toBe('yes');
        expect(flammable?.bValue).toBe('no');
        expect(flammable?.difference).toBe(0); // string difference is 0
    });
}); 