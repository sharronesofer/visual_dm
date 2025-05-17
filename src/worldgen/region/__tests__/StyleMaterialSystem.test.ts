import { selectMaterialAndStyle, registerStyleMaterial, clearStyleMaterialRegistry, registerStyleMaterialPlugin } from '../StyleMaterialSystem';
import { TerrainType } from '../RegionGeneratorInterfaces';
import { expect } from '@jest/globals';

describe('StyleMaterialSystem', () => {
    afterEach(() => {
        clearStyleMaterialRegistry();
    });

    it('selects biome-appropriate material and style', () => {
        const cell = { x: 0, y: 0, terrain: 'forest' as TerrainType };
        const resources = [{ templateId: 'wood' }] as any;
        const environment = { temperature: 0.5, humidity: 0.5, altitude: 0.5 };
        const result = selectMaterialAndStyle(cell, resources, environment);
        expect(result.material).toBe('wood');
        expect(['cabin', 'timber']).toContain(result.style.replace('-alt', ''));
    });

    it('falls back to default material if none available', () => {
        const cell = { x: 0, y: 0, terrain: 'desert' as TerrainType };
        const resources = [{ templateId: 'stone' }] as any;
        const environment = { temperature: 0.9, humidity: 0.2, altitude: 0.1 };
        const result = selectMaterialAndStyle(cell, resources, environment);
        expect(result.material).toBe('stone');
    });

    it('uses registered material/style from registry', () => {
        registerStyleMaterial({ material: 'bamboo', style: 'pagoda', biome: 'forest' });
        const cell = { x: 0, y: 0, terrain: 'forest' as TerrainType };
        const resources = [{ templateId: 'bamboo' }] as any;
        const environment = { temperature: 0.3, humidity: 0.7, altitude: 0.2 };
        const result = selectMaterialAndStyle(cell, resources, environment);
        expect(result.material).toBe('bamboo');
        expect(result.style).toBe('pagoda');
    });

    it('applies plugin to override style', () => {
        registerStyleMaterialPlugin(({ cell }) => {
            if (cell.terrain === 'mountain') return { style: 'fortress' };
            return {};
        });
        const cell = { x: 0, y: 0, terrain: 'mountain' as TerrainType };
        const resources = [{ templateId: 'stone' }] as any;
        const environment = { temperature: 0.2, humidity: 0.3, altitude: 0.9 };
        const result = selectMaterialAndStyle(cell, resources, environment);
        expect(result.style).toBe('fortress');
    });

    it('adapts texture/model variants based on environment', () => {
        const cell = { x: 0, y: 0, terrain: 'plains' as TerrainType };
        const resources = [{ templateId: 'wood' }] as any;
        const envHot = { temperature: 0.9, humidity: 0.2, altitude: 0.1 };
        const envHumid = { temperature: 0.3, humidity: 0.8, altitude: 0.1 };
        const envHigh = { temperature: 0.3, humidity: 0.2, altitude: 0.8 };
        expect(selectMaterialAndStyle(cell, resources, envHot).textureVariant).toBe('sunbleached');
        expect(selectMaterialAndStyle(cell, resources, envHumid).textureVariant).toBe('mossy');
        expect(selectMaterialAndStyle(cell, resources, envHigh).modelVariant).toBe('high-altitude');
    });
});
