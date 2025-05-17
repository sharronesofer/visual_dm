// types.ts
export interface MaterialProperty {
    name: string;
    value: number | string;
    unit?: string;
    description?: string;
}

export interface Material {
    id: string;
    name: string;
    durability: number;
    cost: number;
    aesthetics: number;
    specialProperties?: MaterialProperty[];
    [key: string]: any;
}

export interface MaterialComparisonResult {
    property: string;
    aValue: number | string;
    bValue: number | string;
    difference: number;
} 