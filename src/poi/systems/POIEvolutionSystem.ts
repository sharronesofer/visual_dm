import { IPOI } from '../interfaces/IPOI';
import { POIManager } from '../managers/POIManager';
import { POIType, POISubtype, ThematicElements } from '../types/POITypes';

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
     */
    public addEvolutionRule(poiType: POIType, rule: EvolutionRule): void {
        const rules = this.evolutionRules.get(poiType) || [];
        rules.push(rule);
        rules.sort((a, b) => b.priority - a.priority); // Higher priority first
        this.evolutionRules.set(poiType, rules);
    }

    /**
     * Process evolution for a specific POI based on a trigger
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

        // Exploration evolution rules
        this.addEvolutionRule(POIType.EXPLORATION, {
            condition: (poi) => poi.getStateTracking().discoveries > 5,
            transform: (poi) => ({
                thematicElements: {
                    ...poi.thematicElements,
                    resourceDensity: Math.min(10, (poi.thematicElements.resourceDensity || 1) + 1)
                }
            }),
            priority: 1
        });

        // Social evolution rules
        this.addEvolutionRule(POIType.SOCIAL, {
            condition: (poi) => poi.getStateTracking().interactions > 20,
            transform: (poi) => ({
                thematicElements: {
                    ...poi.thematicElements,
                    population: Math.min(10, (poi.thematicElements.population || 1) + 1)
                }
            }),
            priority: 1
        });
    }
} 