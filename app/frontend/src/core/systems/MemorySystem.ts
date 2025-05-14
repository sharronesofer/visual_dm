/**
 * MemorySystem.ts
 * 
 * Implements a comprehensive memory system for NPCs and entities with
 * short-term and long-term memory management, importance weighting, and decay.
 */

import { BaseSystemManager, SystemConfig } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import { Memory, MemoryType, BaseEntity, createBaseEntity, createTaggable, createPrioritizable } from './DataModels';

export interface MemoryCreateParams {
    type: MemoryType;
    ownerEntityId: string;
    involvedEntityIds: string[];
    description: string;
    details?: Record<string, any>;
    emotionalImpact?: number;
    importance?: number;
    decayRate?: number;
    tags?: string[];
}

export interface MemoryQuery {
    ownerEntityId?: string;
    involvedEntityIds?: string[];
    types?: MemoryType[];
    minImportance?: number;
    timeframe?: {
        start?: number;
        end?: number;
    };
    tags?: string[];
    limit?: number;
    includeForgotten?: boolean;
}

export interface MemoryDecayConfig {
    baseDecayRate: number; // Base rate for all memories
    emotionalMultiplier: number; // How much emotional impact slows decay
    importanceMultiplier: number; // How much importance slows decay
    recallBoost: number; // How much recalling boosts importance
    minimumImportance: number; // Minimum importance for long-term storage
}

/**
 * System responsible for creating, managing, and retrieving memories
 */
export class MemorySystem extends BaseSystemManager {
    private memoryRepository!: Repository<Memory>;
    private decayConfig: MemoryDecayConfig;
    private decayIntervalId: NodeJS.Timeout | null = null;

    constructor(config: SystemConfig & { decayConfig?: Partial<MemoryDecayConfig> }) {
        super(config);

        // Set default decay configuration
        this.decayConfig = {
            baseDecayRate: 0.1, // 10% decay per cycle
            emotionalMultiplier: 0.8, // 20% slower decay per 10 points of emotional impact
            importanceMultiplier: 0.7, // 30% slower decay per 10 points of importance
            recallBoost: 5, // +5 importance on recall
            minimumImportance: 20 // Minimum importance for long-term storage
        };

        // Override with provided decay config if available
        if (config.decayConfig) {
            this.decayConfig = {
                ...this.decayConfig,
                ...config.decayConfig
            };
        }
    }

    /**
     * Initialize memory repositories
     */
    protected async initializeRepositories(): Promise<void> {
        this.memoryRepository = this.createRepository<Memory>('memories', [
            'ownerEntityId',
            'type',
            'importance',
            'decayRate'
        ]);
    }

    /**
     * Initialize the memory system
     */
    protected async initializeSystem(): Promise<void> {
        // Start memory decay process
        this.startMemoryDecay();

        // Register event handlers
        this.setupEventHandlers();
    }

    /**
     * Shut down the memory system
     */
    protected async shutdownSystem(): Promise<void> {
        // Stop memory decay process
        this.stopMemoryDecay();
    }

    /**
     * Set up event handlers to listen for memory-related events
     */
    private setupEventHandlers(): void {
        // Handle interaction events
        this.on('entity:interaction', async (event) => {
            this.logDebug('Handling interaction event', event);
            // Create memories for the participants
            const { source, data } = event;

            if (data.participants?.length > 0) {
                for (const participantId of data.participants) {
                    await this.createMemory({
                        type: MemoryType.INTERACTION,
                        ownerEntityId: participantId,
                        involvedEntityIds: data.participants.filter((id: string) => id !== participantId),
                        description: data.description || `Interaction with ${data.participants.length - 1} entities`,
                        details: data.details || {},
                        emotionalImpact: data.emotionalImpact?.[participantId] || 0,
                        importance: data.importance || 50,
                        tags: data.tags || [],
                    });
                }
            }
        });

        // Handle observation events
        this.on('entity:observation', async (event) => {
            this.logDebug('Handling observation event', event);
            const { source, data } = event;

            await this.createMemory({
                type: MemoryType.OBSERVATION,
                ownerEntityId: data.observerId,
                involvedEntityIds: data.targetIds || [],
                description: data.description || 'Observed something',
                details: data.details || {},
                emotionalImpact: data.emotionalImpact || 0,
                importance: data.importance || 30, // Observations are less important by default
                tags: data.tags || [],
            });
        });

        // Handle quest events
        this.on('quest:update', async (event) => {
            this.logDebug('Handling quest update event', event);
            const { source, data } = event;

            if (data.participantIds?.length > 0) {
                for (const participantId of data.participantIds) {
                    await this.createMemory({
                        type: MemoryType.QUEST,
                        ownerEntityId: participantId,
                        involvedEntityIds: data.relatedEntityIds || [],
                        description: data.description || `Quest update: ${data.questTitle}`,
                        details: {
                            questId: data.questId,
                            questTitle: data.questTitle,
                            status: data.status,
                            progress: data.progress,
                            ...data.details
                        },
                        emotionalImpact: data.emotionalImpact?.[participantId] || 10, // Quests typically have some emotional impact
                        importance: data.importance || 70, // Quests are generally important
                        tags: ['quest', ...(data.tags || [])],
                    });
                }
            }
        });

        // Handle combat events
        this.on('combat:action', async (event) => {
            this.logDebug('Handling combat action event', event);
            const { source, data } = event;

            // Create memory for actor
            await this.createMemory({
                type: MemoryType.COMBAT,
                ownerEntityId: data.actorId,
                involvedEntityIds: data.targetIds || [],
                description: data.description || `Combat action against ${data.targetIds?.length} targets`,
                details: data.details || {},
                emotionalImpact: data.emotionalImpact?.actor || 20, // Combat is emotionally impactful
                importance: data.importance || 60,
                tags: ['combat', ...(data.tags || [])],
            });

            // Create memories for targets
            if (data.targetIds?.length > 0) {
                for (const targetId of data.targetIds) {
                    await this.createMemory({
                        type: MemoryType.COMBAT,
                        ownerEntityId: targetId,
                        involvedEntityIds: [data.actorId],
                        description: data.description || `Targeted by ${data.actorId} in combat`,
                        details: data.details || {},
                        emotionalImpact: data.emotionalImpact?.targets?.[targetId] || 30, // Being attacked is very emotional
                        importance: data.importance || 70, // Being targeted is more important than attacking
                        tags: ['combat', 'targeted', ...(data.tags || [])],
                    });
                }
            }
        });
    }

    /**
     * Create a new memory
     */
    public async createMemory(params: MemoryCreateParams): Promise<Memory> {
        const now = Date.now();

        const baseEntity = createBaseEntity();
        const taggable = createTaggable(params.tags);
        const prioritizable = createPrioritizable(params.importance);

        const memory: Memory = {
            ...baseEntity,
            ...taggable,
            ...prioritizable,
            type: params.type,
            ownerEntityId: params.ownerEntityId,
            involvedEntityIds: params.involvedEntityIds,
            description: params.description,
            details: params.details || {},
            emotionalImpact: params.emotionalImpact || 0,
            decayRate: params.decayRate || this.calculateDecayRate(params.importance || 50, params.emotionalImpact || 0),
            lastRecalled: now,
            relatedMemoryIds: [],
        };

        const createdMemory = await this.memoryRepository.create(memory);

        // Find and link related memories
        const relatedMemories = await this.findRelatedMemories(createdMemory);

        if (relatedMemories.length > 0) {
            createdMemory.relatedMemoryIds = relatedMemories.map(m => m.id);
            await this.memoryRepository.update(createdMemory.id, {
                relatedMemoryIds: createdMemory.relatedMemoryIds
            });

            // Update related memories to point back to this memory
            for (const related of relatedMemories) {
                if (!related.relatedMemoryIds.includes(createdMemory.id)) {
                    related.relatedMemoryIds.push(createdMemory.id);
                    await this.memoryRepository.update(related.id, {
                        relatedMemoryIds: related.relatedMemoryIds
                    });
                }
            }
        }

        // Emit memory created event
        this.emitEvent({
            type: 'memory:created',
            source: this.name,
            timestamp: now,
            data: {
                memoryId: createdMemory.id,
                ownerEntityId: createdMemory.ownerEntityId,
                type: createdMemory.type,
                importance: createdMemory.importance
            }
        });

        return createdMemory;
    }

    /**
     * Retrieve memories based on query parameters
     */
    public async queryMemories(query: MemoryQuery): Promise<Memory[]> {
        const {
            ownerEntityId,
            involvedEntityIds,
            types,
            minImportance = 0,
            timeframe,
            tags,
            limit,
            includeForgotten = false
        } = query;

        this.logDebug('Querying memories with params:', query);

        return this.memoryRepository.query((memory) => {
            // Filter by owner
            if (ownerEntityId && memory.ownerEntityId !== ownerEntityId) {
                return false;
            }

            // Filter by involved entities
            if (involvedEntityIds && involvedEntityIds.length > 0) {
                const hasInvolved = involvedEntityIds.some(id => memory.involvedEntityIds.includes(id));
                if (!hasInvolved) {
                    return false;
                }
            }

            // Filter by types
            if (types && types.length > 0 && !types.includes(memory.type)) {
                return false;
            }

            // Filter by importance
            if (memory.importance < minImportance) {
                return false;
            }

            // Filter by timeframe
            if (timeframe) {
                if (timeframe.start && memory.createdAt < timeframe.start) {
                    return false;
                }
                if (timeframe.end && memory.createdAt > timeframe.end) {
                    return false;
                }
            }

            // Filter by tags
            if (tags && tags.length > 0) {
                const hasTags = tags.every(tag => memory.tags.includes(tag));
                if (!hasTags) {
                    return false;
                }
            }

            // Filter forgotten memories
            if (!includeForgotten && this.isMemoryForgotten(memory)) {
                return false;
            }

            return true;
        }, limit);
    }

    /**
     * Get memories for an entity
     */
    public async getEntityMemories(entityId: string, options: Omit<MemoryQuery, 'ownerEntityId'> = {}): Promise<Memory[]> {
        return this.queryMemories({
            ...options,
            ownerEntityId: entityId
        });
    }

    /**
     * Recall a specific memory (increases importance and resets last recalled time)
     */
    public async recallMemory(memoryId: string): Promise<Memory | null> {
        const memory = await this.memoryRepository.findById(memoryId);

        if (!memory) {
            this.logWarn(`Attempted to recall non-existent memory: ${memoryId}`);
            return null;
        }

        // Update importance and last recalled time
        const updatedMemory = await this.memoryRepository.update(memoryId, {
            importance: Math.min(100, memory.importance + this.decayConfig.recallBoost),
            lastRecalled: Date.now()
        });

        // Emit memory recalled event
        if (updatedMemory) {
            this.emitEvent({
                type: 'memory:recalled',
                source: this.name,
                timestamp: Date.now(),
                data: {
                    memoryId: updatedMemory.id,
                    ownerEntityId: updatedMemory.ownerEntityId,
                    importance: updatedMemory.importance
                }
            });
        }

        return updatedMemory;
    }

    /**
     * Find related memories for a given memory
     */
    private async findRelatedMemories(memory: Memory): Promise<Memory[]> {
        // Find memories with same owner and involved entities
        const sameEntitiesMemories = await this.memoryRepository.query((m) => {
            if (m.id === memory.id) return false; // Exclude self
            if (m.ownerEntityId !== memory.ownerEntityId) return false; // Must be same owner

            // Check for overlapping involved entities
            const hasOverlappingEntities = m.involvedEntityIds.some(id =>
                memory.involvedEntityIds.includes(id)
            );

            if (!hasOverlappingEntities) return false;

            // Check for time proximity (within last 24 hours)
            const timeThreshold = 24 * 60 * 60 * 1000; // 24 hours in ms
            if (Math.abs(m.createdAt - memory.createdAt) > timeThreshold) {
                return false;
            }

            return true;
        }, 10);

        // Find memories with same type
        const sameTypeMemories = await this.memoryRepository.query((m) => {
            if (m.id === memory.id) return false; // Exclude self
            if (m.ownerEntityId !== memory.ownerEntityId) return false; // Must be same owner
            if (m.type !== memory.type) return false; // Must be same type

            // Check for time proximity (within last 72 hours)
            const timeThreshold = 72 * 60 * 60 * 1000; // 72 hours in ms
            if (Math.abs(m.createdAt - memory.createdAt) > timeThreshold) {
                return false;
            }

            return true;
        }, 5);

        // Find memories with overlapping tags
        const sameTagsMemories = await this.memoryRepository.query((m) => {
            if (m.id === memory.id) return false; // Exclude self
            if (m.ownerEntityId !== memory.ownerEntityId) return false; // Must be same owner

            // Check for overlapping tags (at least 2)
            const overlappingTags = m.tags.filter(tag => memory.tags.includes(tag));
            if (overlappingTags.length < 2) return false;

            // Check for time proximity (within last week)
            const timeThreshold = 7 * 24 * 60 * 60 * 1000; // 7 days in ms
            if (Math.abs(m.createdAt - memory.createdAt) > timeThreshold) {
                return false;
            }

            return true;
        }, 5);

        // Combine results, remove duplicates
        const relatedMemoryIds = new Set<string>();
        [...sameEntitiesMemories, ...sameTypeMemories, ...sameTagsMemories].forEach(m => {
            relatedMemoryIds.add(m.id);
        });

        // Get full memory objects for all related memories
        return this.memoryRepository.findByIds(Array.from(relatedMemoryIds));
    }

    /**
     * Check if a memory should be considered forgotten
     */
    private isMemoryForgotten(memory: Memory): boolean {
        // Long-term memories (above minimum importance) are never forgotten
        if (memory.importance >= this.decayConfig.minimumImportance) {
            return false;
        }

        // Calculate effective decay based on time since last recall
        const now = Date.now();
        const timeSinceRecall = now - memory.lastRecalled;
        const daysSinceRecall = timeSinceRecall / (24 * 60 * 60 * 1000);

        // Apply decay formula
        const effectiveDecay = memory.decayRate * daysSinceRecall;
        const currentImportance = Math.max(0, memory.importance - effectiveDecay);

        // Memory is forgotten if importance has decayed below threshold
        return currentImportance <= 10; // 10% threshold for remembering
    }

    /**
     * Calculate decay rate based on importance and emotional impact
     */
    private calculateDecayRate(importance: number, emotionalImpact: number): number {
        // Base decay rate
        let decayRate = this.decayConfig.baseDecayRate;

        // Reduce decay based on importance
        decayRate *= Math.pow(
            this.decayConfig.importanceMultiplier,
            importance / 10
        );

        // Reduce decay based on emotional impact (absolute value)
        const absEmotionalImpact = Math.abs(emotionalImpact);
        decayRate *= Math.pow(
            this.decayConfig.emotionalMultiplier,
            absEmotionalImpact / 10
        );

        // Ensure decay rate is within reasonable bounds
        return Math.max(0.01, Math.min(0.5, decayRate));
    }

    /**
     * Start the memory decay process
     */
    private startMemoryDecay(): void {
        if (this.decayIntervalId) return;

        // Process memory decay every hour
        const DECAY_INTERVAL = 60 * 60 * 1000; // 1 hour

        this.decayIntervalId = setInterval(async () => {
            try {
                await this.processMemoryDecay();
            } catch (error) {
                this.logError('Error processing memory decay:', error);
            }
        }, DECAY_INTERVAL);

        this.logInfo('Memory decay process started');
    }

    /**
     * Stop the memory decay process
     */
    private stopMemoryDecay(): void {
        if (this.decayIntervalId) {
            clearInterval(this.decayIntervalId);
            this.decayIntervalId = null;
            this.logInfo('Memory decay process stopped');
        }
    }

    /**
     * Process memory decay for all memories
     */
    private async processMemoryDecay(): Promise<void> {
        const now = Date.now();
        this.logDebug('Processing memory decay');

        // Get all memories
        const memories = await this.memoryRepository.findAll();

        // Process each memory
        for (const memory of memories) {
            // Skip if importance is already at minimum threshold (long-term memory)
            if (memory.importance >= this.decayConfig.minimumImportance) {
                continue;
            }

            const timeSinceRecall = now - memory.lastRecalled;
            const daysSinceRecall = timeSinceRecall / (24 * 60 * 60 * 1000);

            // Skip if recalled recently (less than a day)
            if (daysSinceRecall < 1) {
                continue;
            }

            // Calculate decay amount
            const decayAmount = memory.decayRate * daysSinceRecall;
            const newImportance = Math.max(0, memory.importance - decayAmount);

            // Update memory if importance has changed significantly
            if (Math.abs(memory.importance - newImportance) > 1) {
                await this.memoryRepository.update(memory.id, {
                    importance: newImportance
                });

                // Emit event if memory is now forgotten
                if (memory.importance > 10 && newImportance <= 10) {
                    this.emitEvent({
                        type: 'memory:forgotten',
                        source: this.name,
                        timestamp: now,
                        data: {
                            memoryId: memory.id,
                            ownerEntityId: memory.ownerEntityId,
                            type: memory.type
                        }
                    });
                }
            }
        }

        this.logDebug(`Memory decay processing complete. Processed ${memories.length} memories.`);
    }
} 