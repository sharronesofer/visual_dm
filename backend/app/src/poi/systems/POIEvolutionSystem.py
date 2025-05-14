from typing import Any, Dict, List, Union


class EvolutionRule:
    condition: (poi: IPOI) => bool
    transform: (poi: IPOI) => Partial<IPOI>
    priority: float
class EvolutionTrigger:
    type: Union['time', 'event', 'interaction']
    data: Dict[str, unknown>
/**
 * System for handling POI evolution based on game events and player interactions.
 * Features:
 * - Rule-based evolution conditions
 * - Multiple trigger types (time-based, event-based, interaction-based)
 * - Priority-based rule processing
 * - Thematic consistency validation
 * - Event emission for evolution steps
 */
class POIEvolutionSystem {
    private static instance: \'POIEvolutionSystem\'
    private evolutionRules: Map<string, EvolutionRule[]>
    private poiManager: POIManager
    private constructor() {
        this.evolutionRules = new Map()
        this.poiManager = POIManager.getInstance()
    }
    public static getInstance(): \'POIEvolutionSystem\' {
        if (!POIEvolutionSystem.instance) {
            POIEvolutionSystem.instance = new POIEvolutionSystem()
        }
        return POIEvolutionSystem.instance
    }
    /**
     * Add an evolution rule for a specific POI type
     */
    public addEvolutionRule(poiType: POIType, rule: EvolutionRule): void {
        const rules = this.evolutionRules.get(poiType) || []
        rules.push(rule)
        rules.sort((a, b) => b.priority - a.priority) 
        this.evolutionRules.set(poiType, rules)
    }
    /**
     * Process evolution for a specific POI based on a trigger
     */
    public processPOIEvolution(poiId: str, trigger: EvolutionTrigger): void {
        const poi = this.poiManager.getPOI(poiId)
        if (!poi) return
        const rules = this.evolutionRules.get(poi.type) || []
        for (const rule of rules) {
            if (rule.condition(poi)) {
                const changes = rule.transform(poi)
                this.applyEvolution(poi, changes, trigger)
                break 
            }
        }
    }
    /**
     * Apply evolution changes to a POI
     */
    private applyEvolution(poi: IPOI, changes: Partial<IPOI>, trigger: EvolutionTrigger): void {
        const preEvolutionState = poi.serialize()
        Object.entries(changes).forEach(([key, value]) => {
            if (key in poi) {
                (poi as any)[key] = value
            }
        })
        if (!this.validateThematicConsistency(poi)) {
            poi.deserialize(preEvolutionState)
            return
        }
        poi.updateStateTracking(
            `Evolution applied - Trigger: ${trigger.type}`,
            'modification'
        )
        this.poiManager.onPOIModified(poi.id)
    }
    /**
     * Validate thematic consistency of evolved POI
     */
    private validateThematicConsistency(poi: IPOI): bool {
        const connections = poi.getConnections()
        const connectedPOIs = connections
            .map(id => this.poiManager.getPOI(id))
            .filter((p): p is IPOI => p !== undefined)
        return this.checkThematicCompatibility(poi.thematicElements, connectedPOIs)
    }
    /**
     * Check if thematic elements are compatible with connected POIs
     */
    private checkThematicCompatibility(
        elements: ThematicElements,
        connectedPOIs: List[IPOI]
    ): bool {
        return connectedPOIs.every(connected => 
            elements.themes.some(theme => 
                connected.thematicElements.themes.includes(theme)
            )
        )
    }
    /**
     * Register default evolution rules for POI types
     */
    public registerDefaultRules(): void {
        this.addEvolutionRule(POIType.DUNGEON, {
            condition: (poi) => poi.getStateTracking().visits > 10,
            transform: (poi) => ({
                thematicElements: Dict[str, Any]
            }),
            priority: 1
        })
        this.addEvolutionRule(POIType.EXPLORATION, {
            condition: (poi) => poi.getStateTracking().discoveries > 5,
            transform: (poi) => ({
                thematicElements: Dict[str, Any]
            }),
            priority: 1
        })
        this.addEvolutionRule(POIType.SOCIAL, {
            condition: (poi) => poi.getStateTracking().interactions > 20,
            transform: (poi) => ({
                thematicElements: Dict[str, Any]
            }),
            priority: 1
        })
    }
} 