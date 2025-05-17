import { IPOI } from '../interfaces/IPOI';
import { POIManager } from '../managers/POIManager';
import { POIType, POISubtype, ThematicElements } from '../types/POITypes';
import { isFeatureEnabled } from '../../utils/FeatureFlags';
import { retryAsync } from '../../utils/retry';
import { getDegradedMode, isFeatureAllowed } from './DegradedModeService';
import { POIIntegrationException } from '../../errors';

interface EvolutionRule {
    condition: (poi: IPOI) => boolean;
    transform: (poi: IPOI) => Partial<IPOI>;
    priority: number;
}

interface EvolutionTrigger {
    type: 'time' | 'event' | 'interaction';
    data: Record<string, unknown>;
}

/**
 * System for handling POI evolution based on game events and player interactions.
 * Features:
 * - Rule-based evolution conditions
 * - Multiple trigger types (time-based, event-based, interaction-based)
 * - Priority-based rule processing
 * - Thematic consistency validation
 * - Event emission for evolution steps
 */
export class POIEvolutionSystem {
    private static instance: POIEvolutionSystem;
    private evolutionRules: Map<string, EvolutionRule[]>;
    private poiManager: POIManager;

    private constructor() {
        this.evolutionRules = new Map();
        this.poiManager = POIManager.getInstance();
    }

    public static getInstance(): POIEvolutionSystem {
        if (!POIEvolutionSystem.instance) {
            POIEvolutionSystem.instance = new POIEvolutionSystem();
        }
        return POIEvolutionSystem.instance;
    }

    /**
     * Add an evolution rule for a specific POI type
     * @param poiType - The POI type
     * @param rule - The evolution rule to add
     */
    public addEvolutionRule(poiType: POIType, rule: EvolutionRule): void {
        const rules = this.evolutionRules.get(poiType) || [];
        rules.push(rule);
        rules.sort((a, b) => b.priority - a.priority); // Higher priority first
        this.evolutionRules.set(poiType, rules);
    }

    /**
     * Process evolution for a specific POI based on a trigger
     * @param poiId - The ID of the POI to evolve
     * @param trigger - The trigger object (must have a string 'type' property)
     */
    public processPOIEvolution(poiId: string, trigger: EvolutionTrigger): void {
        const poi = this.poiManager.getPOI(poiId);
        if (!poi) return;

        const rules = this.evolutionRules.get(poi.type) || [];
        for (const rule of rules) {
            if (rule.condition(poi)) {
                const changes = rule.transform(poi);
                this.applyEvolution(poi, changes, trigger);
                break; // Only apply first matching rule
            }
        }
    }

    /**
     * Apply evolution changes to a POI
     */
    private applyEvolution(poi: IPOI, changes: Partial<IPOI>, trigger: EvolutionTrigger): void {
        // Defensive check for trigger
        if (!trigger || typeof trigger !== 'object' || typeof trigger.type !== 'string') {
            throw new Error('Invalid trigger object passed to applyEvolution: must be an object with a string "type" property.');
        }
        // Record pre-evolution state
        const preEvolutionState = poi.serialize();

        // Apply changes
        Object.entries(changes).forEach(([key, value]) => {
            if (key in poi) {
                (poi as any)[key] = value;
            }
        });

        // Validate thematic consistency
        if (!this.validateThematicConsistency(poi)) {
            // Revert changes if thematic validation fails
            poi.deserialize(preEvolutionState);
            return;
        }

        // Update state tracking
        poi.updateStateTracking(
            `Evolution applied - Trigger: ${trigger.type}`,
            'modification'
        );

        // Notify manager of changes
        this.poiManager.onPOIModified(poi.id);

        // Emit event with full trigger object
        this.poiManager.emit('poi:evolved', {
            poiId: poi.id,
            poi,
            trigger: trigger.type,
            changes,
            version: 1
        });
        // Log event emission for monitoring
        console.log(`[POIEvolutionSystem] Emitted 'poi:evolved' for POI ${poi.id} (trigger: ${trigger.type})`, changes);
    }

    /**
     * Validate thematic consistency of evolved POI
     */
    private validateThematicConsistency(poi: IPOI): boolean {
        // Get connected POIs for context
        const connections = poi.getConnections();
        const connectedPOIs = connections
            .map(id => this.poiManager.getPOI(id))
            .filter((p): p is IPOI => p !== undefined);

        // Check thematic elements compatibility
        return this.checkThematicCompatibility(poi.thematicElements, connectedPOIs);
    }

    /**
     * Check if thematic elements are compatible with connected POIs
     */
    private checkThematicCompatibility(
        elements: ThematicElements,
        connectedPOIs: IPOI[]
    ): boolean {
        // Must share at least one theme with connected POIs
        return connectedPOIs.every(connected =>
            elements.themes.some(theme =>
                connected.thematicElements.themes.includes(theme)
            )
        );
    }

    /**
     * Register default evolution rules for POI types
     */
    public registerDefaultRules(): void {
        // Dungeon evolution rules
        this.addEvolutionRule(POIType.DUNGEON, {
            condition: (poi) => poi.getStateTracking().visits > 10,
            transform: (poi) => ({
                thematicElements: {
                    ...poi.thematicElements,
                    difficulty: Math.min(10, (poi.thematicElements.difficulty || 1) + 1)
                }
            }),
            priority: 1
        });

        // Example: Settlement evolution rules (replace EXPLORATION/SOCIAL with SETTLEMENT)
        this.addEvolutionRule(POIType.SETTLEMENT, {
            condition: (poi) => poi.getStateTracking().interactions > 20,
            transform: (poi) => ({
                thematicElements: {
                    ...poi.thematicElements,
                    population: Math.min(10, (poi.thematicElements.population || 1) + 1)
                }
            }),
            priority: 1
        });

        // Commented out: EXPLORATION and SOCIAL types do not exist
        // this.addEvolutionRule(POIType.EXPLORATION, { ... });
        // this.addEvolutionRule(POIType.SOCIAL, { ... });
    }
}

// Example: Classify operations
// Critical operation: must succeed, use retry and degraded mode
async function performCriticalOperation(args) {
    if (!isFeatureAllowed('criticalOperation')) {
        // Log and skip if not allowed in current mode
        console.warn('[DegradedMode] Skipping criticalOperation due to degraded mode');
        return;
    }
    return await retryAsync(async () => {
        // ... actual operation ...
        // Add timeout wrapper for external calls
        const result = await Promise.race([
            actualExternalCall(args),
            new Promise((_, reject) => setTimeout(() => reject(new POIIntegrationException('Timeout', { operationType: 'criticalOperation' })), 3000)),
        ]);
        return result;
    }, {
        maxAttempts: 3,
        initialDelayMs: 200,
        onRetry: (attempt, err) => {
            console.warn(`[retry] criticalOperation attempt ${attempt} failed`, err);
        },
    });
}

// Non-critical operation: can be disabled or degraded
async function performNonCriticalOperation(args) {
    if (!isFeatureEnabled('nonCriticalFeature') || !isFeatureAllowed('nonCriticalOperation')) {
        console.info('[FeatureFlag/DegradedMode] nonCriticalOperation is disabled or not allowed');
        return;
    }
    try {
        // Try primary source
        return await primaryNonCriticalCall(args);
    } catch (err) {
        // Fallback to cache/replica
        try {
            console.warn('[Fallback] primary failed, trying cache');
            return await cacheNonCriticalCall(args);
        } catch (cacheErr) {
            console.warn('[Fallback] cache failed, trying replica');
            return await replicaNonCriticalCall(args);
        }
    }
}

// Health check endpoint extension
export function getPOIEvolutionSystemHealth() {
    return {
        degradedMode: getDegradedMode(),
        // ...other health info...
    };
}

// --- Placeholders for actual external/fallback implementations ---
async function actualExternalCall(args: any) {
    // TODO: Replace with real external call logic
    return Promise.resolve('external call result');
}
async function primaryNonCriticalCall(args: any) {
    // TODO: Replace with real primary non-critical call logic
    return Promise.resolve('primary non-critical result');
}
async function cacheNonCriticalCall(args: any) {
    // TODO: Replace with real cache fallback logic
    return Promise.resolve('cache fallback result');
}
async function replicaNonCriticalCall(args: any) {
    // TODO: Replace with real replica fallback logic
    return Promise.resolve('replica fallback result');
} 