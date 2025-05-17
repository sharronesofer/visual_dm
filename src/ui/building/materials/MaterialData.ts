import { Material } from './types';

export const MATERIALS: Material[] = [
    {
        id: 'wood',
        name: 'Wood',
        durability: 50,
        cost: 10,
        aesthetics: 60,
        specialProperties: [
            { name: 'flammable', value: 'yes', description: 'Can catch fire easily.' }
        ]
    },
    {
        id: 'stone',
        name: 'Stone',
        durability: 90,
        cost: 25,
        aesthetics: 70,
        specialProperties: [
            { name: 'fire_resistant', value: 'yes', description: 'Resistant to fire.' }
        ]
    },
    {
        id: 'metal',
        name: 'Metal',
        durability: 80,
        cost: 40,
        aesthetics: 50,
        specialProperties: [
            { name: 'conductive', value: 'yes', description: 'Conducts electricity.' }
        ]
    }
];

export function getMaterialById(id: string): Material | undefined {
    return MATERIALS.find(m => m.id === id);
} 