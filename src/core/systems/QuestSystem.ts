/**
 * QuestSystem.ts
 * 
 * Implements a system for quest generation, management, and progression.
 * Coordinates with MotifSystem and NarrativeSystem to create cohesive gameplay.
 */

import { BaseSystemManager, SystemConfig, SystemEvent, SystemRegistry } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import {
    BaseEntity,
    createBaseEntity,
    Quest,
    QuestType,
    QuestStatus,
    QuestObjective,
    ObjectiveType,
    QuestReward
} from './DataModels';
import { MotifSystem } from './MotifSystem';
import { NarrativeSystem } from './NarrativeSystem';

/**
 * Parameters for creating a quest
 */
export interface QuestCreateParams {
    title: string;
    description: string;
    type: QuestType;
    giverEntityId: string;
    targetEntityIds: string[];
    objectives: QuestObjectiveParams[];
    rewards: QuestRewardParams[];
    parentQuestId?: string;
    requiredLevel?: number;
    timeLimit?: number;
    associatedMotifIds?: string[];
    tags?: string[];
    summary?: string;
}

/**
 * Parameters for creating a quest objective
 */
export interface QuestObjectiveParams {
    type: ObjectiveType;
    description: string;
    targetId?: string;
    targetCount?: number;
    locationId?: string;
    parameters?: Record<string, any>;
}

/**
 * Parameters for creating a quest reward
 */
export interface QuestRewardParams {
    type: 'item' | 'currency' | 'experience' | 'reputation' | 'skill';
    amount: number;
    targetId?: string;
}

/**
 * Parameters for querying quests
 */
export interface QuestQuery {
    types?: QuestType[];
    status?: QuestStatus[];
    giverEntityId?: string;
    targetEntityIds?: string[];
    associatedMotifIds?: string[];
    tags?: string[];
    limit?: number;
}

/**
 * System for managing quests
 */
export class QuestSystem extends BaseSystemManager {
    // Repositories
    private questRepository!: Repository<Quest>;

    // Related systems
    private motifSystem: MotifSystem | null = null;
    private narrativeSystem: NarrativeSystem | null = null;

    constructor(config: SystemConfig) {
        super({
            ...config,
            name: config.name || 'QuestSystem',
            dependencies: [
                { name: 'MotifSystem', required: true },
                { name: 'NarrativeSystem', required: false }
            ]
        });
    }

    /**
     * Initialize repositories
     */
    protected async initializeRepositories(): Promise<void> {
        this.questRepository = this.createRepository<Quest>('quests', [
            'title',
            'type',
            'status',
            'giverEntityId'
        ]);
    }

    /**
     * Initialize the system
     */
    protected async initializeSystem(): Promise<void> {
        this.logInfo('Initializing Quest System');

        // Get dependencies
        const registry = SystemRegistry.getInstance();
        this.motifSystem = registry.getSystem<MotifSystem>('MotifSystem');
        this.narrativeSystem = registry.getSystem<NarrativeSystem>('NarrativeSystem');

        if (!this.motifSystem) {
            throw new Error('Quest System requires Motif System to be registered');
        }

        // Set up event listeners
        this.on('quest:started', this.onQuestStarted.bind(this));
        this.on('quest:completed', this.onQuestCompleted.bind(this));
        this.on('quest:failed', this.onQuestFailed.bind(this));
        this.on('quest:objective_completed', this.onObjectiveCompleted.bind(this));
        this.on('item:acquired', this.onItemAcquired.bind(this));
        this.on('location:reached', this.onLocationReached.bind(this));
        this.on('character:interacted', this.onCharacterInteracted.bind(this));
    }

    /**
     * Shutdown the system
     */
    protected async shutdownSystem(): Promise<void> {
        this.logInfo('Shutting down Quest System');
    }

    /**
     * Create a new quest
     */
    public async createQuest(params: QuestCreateParams): Promise<Quest> {
        this.logInfo(`Creating quest: ${params.title}`);

        // Create objectives with default values
        const objectives: QuestObjective[] = params.objectives.map((obj, index) => ({
            id: `objective_${Date.now()}_${index}`,
            type: obj.type,
            description: obj.description,
            targetId: obj.targetId,
            targetCount: obj.targetCount || 1,
            currentCount: 0,
            completed: false,
            locationId: obj.locationId,
            parameters: obj.parameters || {}
        }));

        // Create rewards with default values
        const rewards: QuestReward[] = params.rewards.map((reward, index) => ({
            type: reward.type,
            amount: reward.amount,
            targetId: reward.targetId,
            delivered: false
        }));

        // Create the quest entity
        const quest: Quest = {
            ...createBaseEntity(),
            title: params.title,
            description: params.description,
            type: params.type,
            status: QuestStatus.AVAILABLE,
            giverEntityId: params.giverEntityId,
            targetEntityIds: params.targetEntityIds,
            objectives,
            rewards,
            parentQuestId: params.parentQuestId,
            childQuestIds: [],
            requiredLevel: params.requiredLevel,
            timeLimit: params.timeLimit,
            associatedMotifIds: params.associatedMotifIds || [],
            summary: params.summary || params.description.substring(0, 100) + '...',
            tags: params.tags || []
        };

        // If this is a child quest, update the parent
        if (params.parentQuestId) {
            const parentQuest = await this.questRepository.findById(params.parentQuestId);
            if (parentQuest) {
                await this.questRepository.update(parentQuest.id, {
                    childQuestIds: [...parentQuest.childQuestIds, quest.id]
                });
            }
        }

        const createdQuest = await this.questRepository.create(quest);

        // Emit quest created event
        this.emitEvent({
            type: 'quest:created',
            source: this.name,
            timestamp: Date.now(),
            data: {
                questId: createdQuest.id,
                title: createdQuest.title,
                type: createdQuest.type
            }
        });

        return createdQuest;
    }

    /**
     * Start a quest (change status from AVAILABLE to ACTIVE)
     */
    public async startQuest(questId: string): Promise<Quest | null> {
        const quest = await this.questRepository.findById(questId);

        if (!quest) {
            this.logWarn(`Attempted to start non-existent quest: ${questId}`);
            return null;
        }

        if (quest.status !== QuestStatus.AVAILABLE) {
            this.logWarn(`Cannot start quest ${questId} because it is not available (current status: ${quest.status})`);
            return null;
        }

        this.logInfo(`Starting quest: ${quest.title}`);

        // Update quest status and start time
        const updatedQuest = await this.questRepository.update(questId, {
            status: QuestStatus.ACTIVE,
            startTime: Date.now()
        });

        if (updatedQuest) {
            // Emit quest started event
            this.emitEvent({
                type: 'quest:started',
                source: this.name,
                timestamp: Date.now(),
                data: {
                    questId: updatedQuest.id,
                    title: updatedQuest.title,
                    type: updatedQuest.type
                }
            });
        }

        return updatedQuest;
    }

    /**
     * Complete a quest objective
     */
    public async completeObjective(questId: string, objectiveId: string, progress: number = 1): Promise<Quest | null> {
        const quest = await this.questRepository.findById(questId);

        if (!quest) {
            this.logWarn(`Attempted to update objective in non-existent quest: ${questId}`);
            return null;
        }

        if (quest.status !== QuestStatus.ACTIVE) {
            this.logWarn(`Cannot update objective in quest ${questId} because it is not active`);
            return null;
        }

        // Find the objective
        const objectiveIndex = quest.objectives.findIndex(obj => obj.id === objectiveId);

        if (objectiveIndex === -1) {
            this.logWarn(`Objective ${objectiveId} not found in quest ${questId}`);
            return null;
        }

        const objective = quest.objectives[objectiveIndex];

        // If objective is already completed, do nothing
        if (objective.completed) {
            return quest;
        }

        this.logInfo(`Updating objective "${objective.description}" in quest "${quest.title}"`);

        // Update objective progress
        const updatedObjectives = [...quest.objectives];
        const newCount = Math.min((objective.targetCount || 1), objective.currentCount + progress);
        const completed = newCount >= (objective.targetCount || 1);

        updatedObjectives[objectiveIndex] = {
            ...objective,
            currentCount: newCount,
            completed
        };

        // Check if all objectives are completed
        const allCompleted = updatedObjectives.every(obj => obj.completed);

        // Update the quest
        let updatedQuest: Quest | null = null;

        if (allCompleted) {
            // All objectives completed, mark quest as completed
            updatedQuest = await this.questRepository.update(questId, {
                objectives: updatedObjectives,
                status: QuestStatus.COMPLETED
            });

            if (updatedQuest) {
                // Emit quest completed event
                this.emitEvent({
                    type: 'quest:completed',
                    source: this.name,
                    timestamp: Date.now(),
                    data: {
                        questId: updatedQuest.id,
                        title: updatedQuest.title,
                        type: updatedQuest.type
                    }
                });

                // Record motif occurrences for completed quest
                if (this.motifSystem && updatedQuest.associatedMotifIds.length > 0) {
                    for (const motifId of updatedQuest.associatedMotifIds) {
                        await this.motifSystem.recordOccurrence({
                            motifId,
                            context: `Completed quest: ${updatedQuest.title}`,
                            strength: 75, // Significant occurrence
                            entityIds: [
                                ...updatedQuest.targetEntityIds,
                                updatedQuest.giverEntityId
                            ]
                        });
                    }
                }
            }
        } else {
            // Just update the objectives
            updatedQuest = await this.questRepository.update(questId, {
                objectives: updatedObjectives
            });

            if (updatedQuest && completed) {
                // Emit objective completed event
                this.emitEvent({
                    type: 'quest:objective_completed',
                    source: this.name,
                    timestamp: Date.now(),
                    data: {
                        questId: updatedQuest.id,
                        objectiveId,
                        description: objective.description
                    }
                });
            }
        }

        return updatedQuest;
    }

    /**
     * Fail a quest
     */
    public async failQuest(questId: string, reason: string): Promise<Quest | null> {
        const quest = await this.questRepository.findById(questId);

        if (!quest) {
            this.logWarn(`Attempted to fail non-existent quest: ${questId}`);
            return null;
        }

        if (quest.status !== QuestStatus.ACTIVE) {
            this.logWarn(`Cannot fail quest ${questId} because it is not active`);
            return null;
        }

        this.logInfo(`Failing quest: ${quest.title} - Reason: ${reason}`);

        // Update quest status
        const updatedQuest = await this.questRepository.update(questId, {
            status: QuestStatus.FAILED
        });

        if (updatedQuest) {
            // Emit quest failed event
            this.emitEvent({
                type: 'quest:failed',
                source: this.name,
                timestamp: Date.now(),
                data: {
                    questId: updatedQuest.id,
                    title: updatedQuest.title,
                    reason
                }
            });
        }

        return updatedQuest;
    }

    /**
     * Get a quest by ID
     */
    public async getQuest(questId: string): Promise<Quest | null> {
        return this.questRepository.findById(questId);
    }

    /**
     * Find quests based on query parameters
     */
    public async findQuests(query: QuestQuery): Promise<Quest[]> {
        const {
            types,
            status,
            giverEntityId,
            targetEntityIds,
            associatedMotifIds,
            tags,
            limit
        } = query;

        return this.questRepository.query((quest) => {
            // Filter by type
            if (types && types.length > 0 && !types.includes(quest.type)) {
                return false;
            }

            // Filter by status
            if (status && status.length > 0 && !status.includes(quest.status)) {
                return false;
            }

            // Filter by giver
            if (giverEntityId && quest.giverEntityId !== giverEntityId) {
                return false;
            }

            // Filter by targets
            if (targetEntityIds && targetEntityIds.length > 0 &&
                !targetEntityIds.some(id => quest.targetEntityIds.includes(id))) {
                return false;
            }

            // Filter by associated motifs
            if (associatedMotifIds && associatedMotifIds.length > 0 &&
                !associatedMotifIds.some(id => quest.associatedMotifIds.includes(id))) {
                return false;
            }

            // Filter by tags
            if (tags && tags.length > 0 &&
                !tags.some(tag => quest.tags.includes(tag))) {
                return false;
            }

            return true;
        }, limit);
    }

    /**
     * Get all available quests
     */
    public async getAvailableQuests(): Promise<Quest[]> {
        return this.questRepository.query(quest => quest.status === QuestStatus.AVAILABLE);
    }

    /**
     * Get all active quests
     */
    public async getActiveQuests(): Promise<Quest[]> {
        return this.questRepository.query(quest => quest.status === QuestStatus.ACTIVE);
    }

    /**
     * Get all completed quests
     */
    public async getCompletedQuests(): Promise<Quest[]> {
        return this.questRepository.query(quest => quest.status === QuestStatus.COMPLETED);
    }

    /**
     * Generate a quest based on current motifs and narrative
     */
    public async generateQuest(params: {
        type?: QuestType,
        difficulty?: number,
        locationId?: string,
        giverEntityId: string,
        targetEntityIds?: string[]
    }): Promise<Quest> {
        this.logInfo(`Generating quest for giver: ${params.giverEntityId}`);

        const type = params.type || QuestType.SIDE;
        const difficulty = params.difficulty || 1;
        const locationId = params.locationId;
        const giverEntityId = params.giverEntityId;
        const targetEntityIds = params.targetEntityIds || [];

        // Get relevant motifs to influence quest generation
        let relevantMotifs = [];
        if (this.motifSystem) {
            relevantMotifs = await this.motifSystem.findRelevantMotifs({
                minRelevance: 30,
                entityIds: [giverEntityId, ...targetEntityIds],
                limit: 3
            });
        }

        // Generate a quest title and description based on motifs
        let title = "Generic Quest";
        let description = "A generic quest.";
        let summary = "Complete the assigned task.";
        let tags: string[] = [];
        let associatedMotifIds: string[] = [];

        // If we have motifs, use them to customize the quest
        if (relevantMotifs.length > 0) {
            const primaryMotif = relevantMotifs[0];
            associatedMotifIds = relevantMotifs.map(m => m.id);

            // Generate quest based on motif type
            switch (primaryMotif.type) {
                case 'theme':
                    title = `The ${primaryMotif.name}`;
                    description = `A quest exploring the theme of ${primaryMotif.name.toLowerCase()}.`;
                    break;
                case 'recurring_element':
                    title = `Recurring ${primaryMotif.name}`;
                    description = `A quest involving the recurring element of ${primaryMotif.name.toLowerCase()}.`;
                    break;
                case 'symbol':
                    title = `Symbol of ${primaryMotif.name}`;
                    description = `A quest centered around the symbol of ${primaryMotif.name.toLowerCase()}.`;
                    break;
                default:
                    title = `${primaryMotif.name} Quest`;
                    description = `A quest inspired by ${primaryMotif.name.toLowerCase()}.`;
            }

            // Add motif tags
            tags = [...primaryMotif.tags];
            summary = `A quest about ${primaryMotif.name.toLowerCase()}.`;
        }

        // Generate objectives based on quest type
        const objectives: QuestObjectiveParams[] = [];

        switch (type) {
            case QuestType.MAIN:
                objectives.push(
                    {
                        type: ObjectiveType.TALK,
                        description: "Speak with the quest giver",
                        targetId: giverEntityId
                    },
                    {
                        type: ObjectiveType.REACH_LOCATION,
                        description: locationId ? "Travel to the designated location" : "Explore the area",
                        locationId
                    },
                    {
                        type: ObjectiveType.COLLECT,
                        description: "Collect the required items",
                        targetCount: 3
                    }
                );
                break;

            case QuestType.SIDE:
                objectives.push(
                    {
                        type: ObjectiveType.COLLECT,
                        description: "Collect the required items",
                        targetCount: 2
                    },
                    {
                        type: ObjectiveType.TALK,
                        description: "Return to the quest giver",
                        targetId: giverEntityId
                    }
                );
                break;

            case QuestType.REPEATABLE:
                objectives.push(
                    {
                        type: ObjectiveType.COLLECT,
                        description: "Collect the required items",
                        targetCount: 5
                    }
                );
                break;

            default:
                objectives.push(
                    {
                        type: ObjectiveType.TALK,
                        description: "Complete the assigned task",
                        targetId: giverEntityId
                    }
                );
        }

        // Generate rewards based on difficulty
        const rewards: QuestRewardParams[] = [
            {
                type: 'currency',
                amount: 100 * difficulty
            },
            {
                type: 'experience',
                amount: 50 * difficulty
            }
        ];

        // If difficulty is higher, add an item reward
        if (difficulty >= 2) {
            rewards.push({
                type: 'item',
                amount: 1,
                targetId: `reward_item_${Math.floor(Math.random() * 100)}`
            });
        }

        // Create the quest
        return this.createQuest({
            title,
            description,
            type,
            giverEntityId,
            targetEntityIds,
            objectives,
            rewards,
            requiredLevel: Math.max(1, difficulty),
            associatedMotifIds,
            tags,
            summary
        });
    }

    /**
     * Event handlers
     */
    private async onQuestStarted(event: SystemEvent): Promise<void> {
        const questId = event.data.questId;
        this.logInfo(`Quest started event for ${questId}`);
    }

    private async onQuestCompleted(event: SystemEvent): Promise<void> {
        const questId = event.data.questId;
        this.logInfo(`Quest completed event for ${questId}`);

        // If we have a narrative system, check for arc triggers
        if (this.narrativeSystem) {
            await this.narrativeSystem.checkTriggerConditions({
                completedQuestId: questId,
                ...event.data
            });
        }
    }

    private async onQuestFailed(event: SystemEvent): Promise<void> {
        const questId = event.data.questId;
        this.logInfo(`Quest failed event for ${questId}`);
    }

    private async onObjectiveCompleted(event: SystemEvent): Promise<void> {
        const questId = event.data.questId;
        const objectiveId = event.data.objectiveId;
        this.logInfo(`Objective completed event for quest ${questId}, objective ${objectiveId}`);
    }

    private async onItemAcquired(event: SystemEvent): Promise<void> {
        const itemId = event.data.itemId;
        this.logInfo(`Item acquired event for ${itemId} - checking quest objectives`);

        // Update any active quest objectives that require collecting this item
        const activeQuests = await this.getActiveQuests();

        for (const quest of activeQuests) {
            for (const objective of quest.objectives) {
                if (objective.type === ObjectiveType.COLLECT &&
                    objective.targetId === itemId &&
                    !objective.completed) {
                    await this.completeObjective(quest.id, objective.id);
                }
            }
        }
    }

    private async onLocationReached(event: SystemEvent): Promise<void> {
        const locationId = event.data.locationId;
        this.logInfo(`Location reached event for ${locationId} - checking quest objectives`);

        // Update any active quest objectives that require reaching this location
        const activeQuests = await this.getActiveQuests();

        for (const quest of activeQuests) {
            for (const objective of quest.objectives) {
                if (objective.type === ObjectiveType.REACH_LOCATION &&
                    objective.locationId === locationId &&
                    !objective.completed) {
                    await this.completeObjective(quest.id, objective.id);
                }
            }
        }
    }

    private async onCharacterInteracted(event: SystemEvent): Promise<void> {
        const characterId = event.data.characterId;
        const interactionType = event.data.interactionType;
        this.logInfo(`Character interaction event with ${characterId} (${interactionType}) - checking quest objectives`);

        // Update any active quest objectives that require talking to this character
        const activeQuests = await this.getActiveQuests();

        for (const quest of activeQuests) {
            for (const objective of quest.objectives) {
                if (objective.type === ObjectiveType.TALK &&
                    objective.targetId === characterId &&
                    !objective.completed) {
                    await this.completeObjective(quest.id, objective.id);
                }
            }
        }
    }
} 