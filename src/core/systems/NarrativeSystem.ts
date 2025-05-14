/**
 * NarrativeSystem.ts
 * 
 * Implements a system for managing narrative progression, story arcs, and
 * narrative choices. Works with MotifSystem to create cohesive storytelling.
 */

import { BaseSystemManager, SystemConfig, SystemEvent, SystemRegistry } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import { BaseEntity, createBaseEntity } from './DataModels';
import { MotifSystem } from './MotifSystem';

/**
 * Represents a narrative arc (main story, side story, character arc, etc.)
 */
export interface NarrativeArc extends BaseEntity {
    title: string;
    description: string;
    arcType: 'main' | 'side' | 'character' | 'faction' | 'location';
    status: 'inactive' | 'active' | 'resolved' | 'failed';
    progress: number; // 0-100
    stageIndex: number;
    stages: NarrativeStage[];
    relatedEntityIds: string[]; // Characters, factions, locations involved
    motifIds: string[]; // Motifs connected to this arc
    outcomes: NarrativeOutcome[];
    requiredArcs: string[]; // IDs of arcs that must be resolved first
    tags: string[];
}

/**
 * Represents a stage within a narrative arc
 */
export interface NarrativeStage {
    id: string;
    title: string;
    description: string;
    triggerConditions: NarrativeTriggerCondition[];
    completionConditions: NarrativeCompletionCondition[];
    choices: NarrativeChoice[];
    status: 'pending' | 'active' | 'completed' | 'failed';
    nextStageIds: string[]; // Can branch to different next stages
}

/**
 * Condition that triggers a narrative stage to become active
 */
export interface NarrativeTriggerCondition {
    type: 'quest_complete' | 'location_discovered' | 'item_acquired' |
    'character_met' | 'motif_relevance' | 'player_choice' | 'time_passed';
    parameters: Record<string, any>;
    fulfilled: boolean;
}

/**
 * Condition that completes a narrative stage
 */
export interface NarrativeCompletionCondition {
    type: 'quest_complete' | 'dialogue_finished' | 'item_delivered' |
    'location_reached' | 'character_interacted' | 'player_choice';
    parameters: Record<string, any>;
    fulfilled: boolean;
}

/**
 * Represents a choice in the narrative that affects future story progression
 */
export interface NarrativeChoice {
    id: string;
    description: string;
    requirements: {
        attributes?: Record<string, number>;
        items?: string[];
        relationships?: Record<string, number>;
        flags?: string[];
    };
    consequences: {
        nextStageId?: string;
        motifOccurrences?: {
            motifId: string;
            strength: number;
        }[];
        relationshipChanges?: {
            entityId: string;
            change: number;
        }[];
        flagChanges?: {
            flag: string;
            value: any;
        }[];
    };
    chosenAt?: number; // Timestamp when this choice was made
}

/**
 * Represents a potential outcome of a narrative arc
 */
export interface NarrativeOutcome {
    id: string;
    description: string;
    conditions: {
        choices?: string[]; // Choice IDs that lead to this outcome
        flags?: Record<string, any>; // Game state flags required
    };
    consequences: {
        worldChanges: {
            description: string;
            entityId?: string;
            changeType: 'status' | 'relationship' | 'access' | 'physical';
            value: any;
        }[];
        followupArcIds: string[]; // Arcs that may be triggered by this outcome
    };
    triggered: boolean;
}

/**
 * Parameters for creating a narrative arc
 */
export interface NarrativeArcCreateParams {
    title: string;
    description: string;
    arcType: 'main' | 'side' | 'character' | 'faction' | 'location';
    initialStage: Omit<NarrativeStage, 'id' | 'status'>;
    relatedEntityIds: string[];
    motifIds: string[];
    requiredArcs?: string[];
    tags?: string[];
}

/**
 * Parameters for querying narrative arcs
 */
export interface NarrativeArcQuery {
    arcType?: ('main' | 'side' | 'character' | 'faction' | 'location')[];
    status?: ('inactive' | 'active' | 'resolved' | 'failed')[];
    tags?: string[];
    entityIds?: string[];
    motifIds?: string[];
    limit?: number;
}

/**
 * System for managing narrative arcs and storytelling
 */
export class NarrativeSystem extends BaseSystemManager {
    // Repositories
    private narrativeArcRepository!: Repository<NarrativeArc>;

    // Related systems
    private motifSystem: MotifSystem | null = null;

    constructor(config: SystemConfig) {
        super({
            ...config,
            name: config.name || 'NarrativeSystem',
            dependencies: [
                { name: 'MotifSystem', required: true }
            ]
        });
    }

    /**
     * Initialize repositories
     */
    protected async initializeRepositories(): Promise<void> {
        this.narrativeArcRepository = this.createRepository<NarrativeArc>('narrative_arcs', [
            'arcType',
            'status',
            'tags'
        ]);
    }

    /**
     * Initialize the system
     */
    protected async initializeSystem(): Promise<void> {
        this.logInfo('Initializing Narrative System');

        // Get dependencies
        const registry = SystemRegistry.getInstance();
        this.motifSystem = registry.getSystem<MotifSystem>('MotifSystem');

        if (!this.motifSystem) {
            throw new Error('Narrative System requires Motif System to be registered');
        }

        // Set up event listeners
        this.on('quest:completed', this.onQuestCompleted.bind(this));
        this.on('dialogue:completed', this.onDialogueCompleted.bind(this));
        this.on('character:relationship_changed', this.onRelationshipChanged.bind(this));
        this.on('item:acquired', this.onItemAcquired.bind(this));
        this.on('location:discovered', this.onLocationDiscovered.bind(this));
    }

    /**
     * Shutdown the system
     */
    protected async shutdownSystem(): Promise<void> {
        this.logInfo('Shutting down Narrative System');
    }

    /**
     * Create a new narrative arc
     */
    public async createNarrativeArc(params: NarrativeArcCreateParams): Promise<NarrativeArc> {
        this.logInfo(`Creating narrative arc: ${params.title}`);

        // Create first stage with default status
        const initialStage: NarrativeStage = {
            id: `stage_${Date.now()}_0`,
            title: params.initialStage.title,
            description: params.initialStage.description,
            triggerConditions: params.initialStage.triggerConditions || [],
            completionConditions: params.initialStage.completionConditions || [],
            choices: params.initialStage.choices || [],
            status: 'pending',
            nextStageIds: params.initialStage.nextStageIds || []
        };

        const arc: NarrativeArc = {
            ...createBaseEntity(),
            title: params.title,
            description: params.description,
            arcType: params.arcType,
            status: 'inactive',
            progress: 0,
            stageIndex: 0,
            stages: [initialStage],
            relatedEntityIds: params.relatedEntityIds,
            motifIds: params.motifIds,
            outcomes: [],
            requiredArcs: params.requiredArcs || [],
            tags: params.tags || []
        };

        const createdArc = await this.narrativeArcRepository.create(arc);

        // Emit narrative arc created event
        this.emitEvent({
            type: 'narrative:arc_created',
            source: this.name,
            timestamp: Date.now(),
            data: {
                arcId: createdArc.id,
                title: createdArc.title,
                arcType: createdArc.arcType
            }
        });

        return createdArc;
    }

    /**
     * Add a stage to a narrative arc
     */
    public async addStageToArc(
        arcId: string,
        stage: Omit<NarrativeStage, 'id' | 'status'>,
        previousStageId?: string
    ): Promise<NarrativeArc | null> {
        const arc = await this.narrativeArcRepository.findById(arcId);

        if (!arc) {
            this.logWarn(`Attempted to add stage to non-existent arc: ${arcId}`);
            return null;
        }

        this.logInfo(`Adding stage "${stage.title}" to arc "${arc.title}"`);

        // Create new stage with unique ID
        const newStage: NarrativeStage = {
            id: `stage_${Date.now()}_${arc.stages.length}`,
            status: 'pending',
            ...stage
        };

        // Update previous stage to point to this new stage if specified
        if (previousStageId) {
            const updatedStages = arc.stages.map(s => {
                if (s.id === previousStageId) {
                    return {
                        ...s,
                        nextStageIds: [...s.nextStageIds, newStage.id]
                    };
                }
                return s;
            });

            // Add the new stage
            updatedStages.push(newStage);

            // Update arc
            return this.narrativeArcRepository.update(arcId, {
                stages: updatedStages
            });
        } else {
            // Simply add the new stage
            return this.narrativeArcRepository.update(arcId, {
                stages: [...arc.stages, newStage]
            });
        }
    }

    /**
     * Update a narrative arc
     */
    public async updateNarrativeArc(
        arcId: string,
        updates: Partial<Omit<NarrativeArc, 'id' | 'createdAt' | 'updatedAt'>>
    ): Promise<NarrativeArc | null> {
        const arc = await this.narrativeArcRepository.findById(arcId);

        if (!arc) {
            this.logWarn(`Attempted to update non-existent narrative arc: ${arcId}`);
            return null;
        }

        this.logInfo(`Updating narrative arc: ${arc.title}`);

        // Update the arc
        const updatedArc = await this.narrativeArcRepository.update(arcId, updates);

        // Emit update event if status changed
        if (updatedArc && updates.status && updates.status !== arc.status) {
            this.emitEvent({
                type: 'narrative:arc_status_changed',
                source: this.name,
                timestamp: Date.now(),
                data: {
                    arcId: updatedArc.id,
                    title: updatedArc.title,
                    previousStatus: arc.status,
                    newStatus: updatedArc.status
                }
            });
        }

        return updatedArc;
    }

    /**
     * Get a narrative arc by ID
     */
    public async getNarrativeArc(arcId: string): Promise<NarrativeArc | null> {
        return this.narrativeArcRepository.findById(arcId);
    }

    /**
     * Find narrative arcs based on query parameters
     */
    public async findNarrativeArcs(query: NarrativeArcQuery): Promise<NarrativeArc[]> {
        const {
            arcType,
            status,
            tags,
            entityIds,
            motifIds,
            limit
        } = query;

        return this.narrativeArcRepository.query((arc) => {
            // Filter by arc type
            if (arcType && arcType.length > 0 && !arcType.includes(arc.arcType)) {
                return false;
            }

            // Filter by status
            if (status && status.length > 0 && !status.includes(arc.status)) {
                return false;
            }

            // Filter by tags
            if (tags && tags.length > 0 && !tags.some(tag => arc.tags.includes(tag))) {
                return false;
            }

            // Filter by related entities
            if (entityIds && entityIds.length > 0 &&
                !entityIds.some(id => arc.relatedEntityIds.includes(id))) {
                return false;
            }

            // Filter by motifs
            if (motifIds && motifIds.length > 0 &&
                !motifIds.some(id => arc.motifIds.includes(id))) {
                return false;
            }

            return true;
        }, limit);
    }

    /**
     * Make a narrative choice
     */
    public async makeNarrativeChoice(
        arcId: string,
        stageId: string,
        choiceId: string
    ): Promise<NarrativeArc | null> {
        const arc = await this.narrativeArcRepository.findById(arcId);

        if (!arc) {
            this.logWarn(`Attempted to make choice in non-existent arc: ${arcId}`);
            return null;
        }

        // Find the stage
        const stageIndex = arc.stages.findIndex(stage => stage.id === stageId);

        if (stageIndex === -1) {
            this.logWarn(`Stage ${stageId} not found in arc ${arcId}`);
            return null;
        }

        // Find the choice
        const stage = arc.stages[stageIndex];
        const choice = stage.choices.find(c => c.id === choiceId);

        if (!choice) {
            this.logWarn(`Choice ${choiceId} not found in stage ${stageId}`);
            return null;
        }

        this.logInfo(`Making narrative choice: "${choice.description}" in arc "${arc.title}"`);

        // Mark the choice as chosen
        const updatedChoices = stage.choices.map(c => {
            if (c.id === choiceId) {
                return { ...c, chosenAt: Date.now() };
            }
            return c;
        });

        // Update stage with chosen choice
        const updatedStages = [...arc.stages];
        updatedStages[stageIndex] = {
            ...stage,
            choices: updatedChoices
        };

        // Process consequences
        await this.processChoiceConsequences(arc, choice);

        // If choice specifies next stage, update current stage status and activate next stage
        if (choice.consequences.nextStageId) {
            const nextStageIndex = arc.stages.findIndex(s => s.id === choice.consequences.nextStageId);

            if (nextStageIndex !== -1) {
                // Mark current stage as completed
                updatedStages[stageIndex].status = 'completed';

                // Activate next stage
                updatedStages[nextStageIndex] = {
                    ...arc.stages[nextStageIndex],
                    status: 'active'
                };

                // Update arc with new stage index
                return this.narrativeArcRepository.update(arcId, {
                    stages: updatedStages,
                    stageIndex: nextStageIndex,
                    progress: this.calculateArcProgress(updatedStages)
                });
            }
        }

        // If no next stage specified, just update the choices
        return this.narrativeArcRepository.update(arcId, {
            stages: updatedStages
        });
    }

    /**
     * Process narrative choice consequences
     */
    private async processChoiceConsequences(arc: NarrativeArc, choice: NarrativeChoice): Promise<void> {
        const consequences = choice.consequences;

        // Process motif occurrences
        if (consequences.motifOccurrences && this.motifSystem) {
            for (const occurrence of consequences.motifOccurrences) {
                await this.motifSystem.recordOccurrence({
                    motifId: occurrence.motifId,
                    context: `Narrative choice in arc "${arc.title}": ${choice.description}`,
                    strength: occurrence.strength,
                    entityIds: arc.relatedEntityIds
                });
            }
        }

        // Process relationship changes
        if (consequences.relationshipChanges) {
            for (const change of consequences.relationshipChanges) {
                // Emit relationship change event for other systems to handle
                this.emitEvent({
                    type: 'narrative:relationship_changed',
                    source: this.name,
                    timestamp: Date.now(),
                    data: {
                        entityId: change.entityId,
                        change: change.change,
                        context: `Narrative choice: ${choice.description}`
                    }
                });
            }
        }

        // Process flag changes
        if (consequences.flagChanges) {
            for (const change of consequences.flagChanges) {
                // Emit flag change event for other systems to handle
                this.emitEvent({
                    type: 'narrative:flag_changed',
                    source: this.name,
                    timestamp: Date.now(),
                    data: {
                        flag: change.flag,
                        value: change.value,
                        context: `Narrative choice: ${choice.description}`
                    }
                });
            }
        }
    }

    /**
     * Calculate the progress percentage of a narrative arc
     */
    private calculateArcProgress(stages: NarrativeStage[]): number {
        if (stages.length === 0) return 0;

        const completedStages = stages.filter(s => s.status === 'completed').length;
        return Math.round((completedStages / stages.length) * 100);
    }

    /**
     * Check and update narrative trigger conditions
     */
    public async checkTriggerConditions(context: Record<string, any> = {}): Promise<void> {
        // Get active arcs
        const arcs = await this.narrativeArcRepository.query(
            arc => arc.status === 'active' || arc.status === 'inactive'
        );

        for (const arc of arcs) {
            let updated = false;

            // Process each stage
            const updatedStages = arc.stages.map(stage => {
                // Only check pending stages
                if (stage.status !== 'pending') return stage;

                // Check if all trigger conditions are met
                const allConditionsMet = this.checkConditions(stage.triggerConditions, context);

                if (allConditionsMet) {
                    updated = true;
                    this.logInfo(`Activating stage "${stage.title}" in arc "${arc.title}"`);

                    // Update trigger conditions
                    const updatedTriggerConditions = stage.triggerConditions.map(c => ({
                        ...c,
                        fulfilled: true
                    }));

                    // Activate the stage
                    return {
                        ...stage,
                        status: 'active',
                        triggerConditions: updatedTriggerConditions
                    };
                }

                return stage;
            });

            if (updated) {
                // If any arc was inactive and now has an active stage, activate the arc
                if (arc.status === 'inactive' && updatedStages.some(s => s.status === 'active')) {
                    await this.narrativeArcRepository.update(arc.id, {
                        stages: updatedStages,
                        status: 'active'
                    });
                } else {
                    await this.narrativeArcRepository.update(arc.id, {
                        stages: updatedStages
                    });
                }
            }
        }
    }

    /**
     * Check conditions against context
     */
    private checkConditions(
        conditions: (NarrativeTriggerCondition | NarrativeCompletionCondition)[],
        context: Record<string, any>
    ): boolean {
        // No conditions means they're all satisfied
        if (conditions.length === 0) return true;

        return conditions.every(condition => {
            // Skip conditions already fulfilled
            if (condition.fulfilled) return true;

            // Check each condition type
            switch (condition.type) {
                case 'quest_complete':
                    return context.completedQuestId === condition.parameters.questId;

                case 'location_discovered':
                    return context.discoveredLocationId === condition.parameters.locationId;

                case 'item_acquired':
                    return context.acquiredItemId === condition.parameters.itemId;

                case 'character_met':
                    return context.metCharacterId === condition.parameters.characterId;

                case 'motif_relevance':
                    if (this.motifSystem && context.motifRelevanceCheck) {
                        // The condition is that a motif relevance is above a threshold
                        const motif = context.relevantMotifs?.find(
                            (m: any) => m.id === condition.parameters.motifId
                        );
                        return motif && motif.relevanceScore >= condition.parameters.threshold;
                    }
                    return false;

                case 'player_choice':
                    return context.madeChoiceId === condition.parameters.choiceId;

                case 'time_passed':
                    return Date.now() >= condition.parameters.timestamp;

                case 'dialogue_finished':
                    return context.finishedDialogueId === condition.parameters.dialogueId;

                default:
                    return false;
            }
        });
    }

    /**
     * Get active narrative arcs
     */
    public async getActiveArcs(): Promise<NarrativeArc[]> {
        return this.narrativeArcRepository.query(arc => arc.status === 'active');
    }

    /**
     * Get completed narrative arcs
     */
    public async getCompletedArcs(): Promise<NarrativeArc[]> {
        return this.narrativeArcRepository.query(arc => arc.status === 'resolved');
    }

    /**
     * Get narrative arcs involving specific entities
     */
    public async getArcsForEntities(entityIds: string[]): Promise<NarrativeArc[]> {
        if (entityIds.length === 0) return [];

        return this.narrativeArcRepository.query(
            arc => entityIds.some(id => arc.relatedEntityIds.includes(id))
        );
    }

    /**
     * Event handlers
     */
    private async onQuestCompleted(event: SystemEvent): Promise<void> {
        const questId = event.data.questId;
        this.logInfo(`Quest completed event for ${questId} - checking narrative triggers`);

        await this.checkTriggerConditions({
            completedQuestId: questId,
            ...event.data
        });
    }

    private async onDialogueCompleted(event: SystemEvent): Promise<void> {
        const dialogueId = event.data.dialogueId;
        this.logInfo(`Dialogue completed event for ${dialogueId} - checking narrative triggers`);

        await this.checkTriggerConditions({
            finishedDialogueId: dialogueId,
            ...event.data
        });
    }

    private async onRelationshipChanged(event: SystemEvent): Promise<void> {
        const entityId = event.data.entityId;
        this.logInfo(`Relationship changed event for ${entityId} - checking narrative triggers`);

        await this.checkTriggerConditions({
            relationshipChangedEntityId: entityId,
            ...event.data
        });
    }

    private async onItemAcquired(event: SystemEvent): Promise<void> {
        const itemId = event.data.itemId;
        this.logInfo(`Item acquired event for ${itemId} - checking narrative triggers`);

        await this.checkTriggerConditions({
            acquiredItemId: itemId,
            ...event.data
        });
    }

    private async onLocationDiscovered(event: SystemEvent): Promise<void> {
        const locationId = event.data.locationId;
        this.logInfo(`Location discovered event for ${locationId} - checking narrative triggers`);

        await this.checkTriggerConditions({
            discoveredLocationId: locationId,
            ...event.data
        });
    }
} 