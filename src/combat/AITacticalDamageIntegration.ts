import { BuildingStructure, BuildingElement } from '../core/interfaces/types/building';
import { TacticalHexCell } from '../hexmap/TacticalHexCell';

/**
 * AITacticalDamageIntegration
 * Enhances AI tactical behavior using building damage data for shooting, cover, and detection.
 */
export class AITacticalDamageIntegration {
    /**
     * Score a damaged section for tactical shooting opportunities.
     * @param element The building element (damaged section)
     * @returns Score (higher = better shooting opportunity)
     */
    public static scoreShootingOpportunity(element: BuildingElement): number {
        const damageRatio = 1 - (element.health / element.maxHealth);
        let score = 0;
        if (damageRatio > 0.7) score += 2; // heavily damaged
        else if (damageRatio > 0.3) score += 1; // moderately damaged
        if (element.type === 'window') score += 1;
        if (element.type === 'door') score += 0.5;
        return score;
    }

    /**
     * Assess cover quality for AI decision-making.
     * @param cell The tactical hex cell
     * @returns Score (higher = better cover)
     */
    public static scoreCoverQuality(cell: TacticalHexCell): number {
        // Use cover value directly, but penalize if below threshold
        if (cell.cover >= 0.7) return 2;
        if (cell.cover >= 0.4) return 1;
        return 0;
    }

    /**
     * Include damaged structure detection in threat assessment.
     * @param element The building element
     * @returns Threat score (higher = more threat)
     */
    public static scoreDetectionThreat(element: BuildingElement): number {
        const damageRatio = 1 - (element.health / element.maxHealth);
        return damageRatio > 0.5 ? 1 : 0;
    }

    /**
     * Tactical movement: prefer paths that use damaged sections for advantage.
     * @param path Array of TacticalHexCell
     * @returns Path score (higher = more tactically advantageous)
     */
    public static scoreTacticalPath(path: TacticalHexCell[]): number {
        let score = 0;
        for (const cell of path) {
            score += this.scoreCoverQuality(cell);
        }
        return score;
    }

    /**
     * Cache tactical calculations for performance (example: can be extended for real use)
     */
    private static tacticalCache: Map<string, number> = new Map();
    public static cacheScore(key: string, score: number) {
        this.tacticalCache.set(key, score);
    }
    public static getCachedScore(key: string): number | undefined {
        return this.tacticalCache.get(key);
    }
} 