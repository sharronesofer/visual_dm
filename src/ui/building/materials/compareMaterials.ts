import { Material, MaterialComparisonResult } from './types';

export function compareMaterials(a: Material, b: Material): MaterialComparisonResult[] {
    const results: MaterialComparisonResult[] = [];
    // Compare core properties
    for (const prop of ['durability', 'cost', 'aesthetics']) {
        results.push({
            property: prop,
            aValue: a[prop],
            bValue: b[prop],
            difference: Number(b[prop]) - Number(a[prop]),
        });
    }
    // Compare shared special properties
    if (a.specialProperties && b.specialProperties) {
        for (const aProp of a.specialProperties) {
            const bProp = b.specialProperties.find(p => p.name === aProp.name);
            if (bProp) {
                results.push({
                    property: aProp.name,
                    aValue: aProp.value,
                    bValue: bProp.value,
                    difference: aProp.value === bProp.value ? 0 : (typeof aProp.value === 'number' && typeof bProp.value === 'number' ? bProp.value - aProp.value : 0),
                });
            }
        }
    }
    return results;
} 