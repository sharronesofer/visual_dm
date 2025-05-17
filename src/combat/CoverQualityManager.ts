import { TacticalHexCell } from '../hexmap/TacticalHexCell';
import { BuildingStructure, BuildingElement, MaterialType } from '../core/interfaces/types/building';

/**
 * CoverQualityManager
 * Dynamically evaluates and updates cover values for TacticalHexCell based on building damage states and material types.
 * Integrates with the building module system for material lookups.
 */
export class CoverQualityManager {
    // Base cover values by material type (configurable)
    private static baseCoverValues: Record<MaterialType, number> = {
        wood: 0.5,
        stone: 0.8,
        metal: 0.9,
        reinforced: 1.0,
    };

    /**
     * Update the cover value for a TacticalHexCell based on the associated building element's damage state.
     * @param cell The tactical hex cell to update.
     * @param element The building element associated with this cell.
     */
    public static updateCellCover(cell: TacticalHexCell, element: BuildingElement) {
        const base = this.baseCoverValues[element.material] ?? 0.5;
        const damageRatio = element.health / element.maxHealth;
        // Cover degrades as damage increases: cover = base * (0.3 + 0.7 * damageRatio)
        // (0.3 minimum cover at 100% damage, full base cover at 0% damage)
        const cover = base * (0.3 + 0.7 * damageRatio);
        cell.cover = Math.max(0, Math.min(1, cover));
    }

    /**
     * Bulk update cover values for all cells associated with a building structure.
     * @param grid The tactical hex grid.
     * @param structure The building structure.
     * @param elementToCellMap A mapping from element IDs to {q, r} cell coordinates.
     */
    public static updateStructureCover(
        grid: { get(q: number, r: number): TacticalHexCell | undefined },
        structure: BuildingStructure,
        elementToCellMap: Record<string, { q: number; r: number }>
    ) {
        for (const [elementId, coords] of Object.entries(elementToCellMap)) {
            const element = structure.elements.get(elementId);
            if (!element) continue;
            const cell = grid.get(coords.q, coords.r);
            if (!cell) continue;
            this.updateCellCover(cell, element);
        }
    }
} 