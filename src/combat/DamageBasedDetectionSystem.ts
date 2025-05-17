import { BuildingStructure, BuildingElement } from '../core/interfaces/types/building';

/**
 * DamageBasedDetectionSystem
 * Handles detection of enemies through damaged building sections, with probability modifiers based on damage and lighting.
 */
export class DamageBasedDetectionSystem {
    /**
     * Calculate detection probability through a damaged element.
     * @param element The building element being looked through.
     * @param baseProbability The base detection probability (0-1).
     * @param lightingFactor Lighting modifier (0-1, 1 = fully lit).
     * @returns Probability (0-1)
     */
    public static calculateDetectionProbability(
        element: BuildingElement,
        baseProbability: number = 0.5,
        lightingFactor: number = 1.0
    ): number {
        // Damage increases detection probability; size/type can further modify
        const damageRatio = 1 - (element.health / element.maxHealth);
        let modifier = 1 + damageRatio * 1.5; // Up to 2.5x at max damage
        if (element.type === 'window') modifier += 0.5;
        if (element.type === 'door') modifier += 0.2;
        // Lighting can reduce detection
        modifier *= lightingFactor;
        return Math.max(0, Math.min(1, baseProbability * modifier));
    }

    /**
     * Check if detection occurs, given probability.
     * @param probability Probability of detection (0-1)
     * @returns True if detected
     */
    public static checkDetection(probability: number): boolean {
        return Math.random() < probability;
    }

    /**
     * Trigger detection feedback (animations, UI, etc.)
     * @param detected Whether detection occurred
     * @param element The building element involved
     * @param actorId The ID of the detecting character
     */
    public static triggerDetectionFeedback(detected: boolean, element: BuildingElement, actorId: string) {
        // Hook for animation/UI system
        // Example: if (detected) showPeekAnimation(actorId, element.position);
        // Example: if (detected) showDetectionIndicator(element.position);
    }
} 