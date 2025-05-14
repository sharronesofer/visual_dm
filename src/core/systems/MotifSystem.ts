/**
 * MotifSystem.ts
 * 
 * Implements a system for tracking, managing, and scoring narrative motifs that
 * appear throughout the game. Motifs are recurring themes, symbols, or narrative
 * elements that give cohesion to the story and influence generative content.
 */

import { BaseSystemManager, SystemConfig, SystemEvent } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import {
    BaseEntity,
    createBaseEntity,
    Motif,
    MotifType,
    MotifOccurrence
} from './DataModels';

/**
 * Parameters for creating a new motif
 */
export interface MotifCreateParams {
    name: string;
    type: MotifType;
    description: string;
    tags?: string[];
    importance?: number; // 0-100 scale
}

/**
 * Parameters for recording a motif occurrence
 */
export interface MotifOccurrenceParams {
    motifId: string;
    context: string;
    strength: number; // 0-100 scale, how strongly the motif appears
    entityIds: string[]; // Entities involved (NPCs, locations, items, etc.)
}

/**
 * Parameters for querying motifs
 */
export interface MotifQuery {
    types?: MotifType[];
    tags?: string[];
    entityIds?: string[];
    minRelevance?: number;
    limit?: number;
}

/**
 * Configuration for relevance scoring
 */
export interface MotifRelevanceConfig {
    // How quickly motif relevance decays over time (lower = slower decay)
    recencyDecay: number;

    // Weight given to frequency of occurrences
    frequencyWeight: number;

    // Weight given to motif importance
    importanceWeight: number;

    // Weight given to occurrence strength
    strengthWeight: number;
}

/**
 * System for tracking and scoring narrative motifs
 */
export class MotifSystem extends BaseSystemManager {
    // Repositories
    private motifRepository!: Repository<Motif>;

    // Configuration
    private relevanceConfig: MotifRelevanceConfig;

    constructor(config: SystemConfig & { relevanceConfig?: Partial<MotifRelevanceConfig> }) {
        super({
            ...config,
            name: config.name || 'MotifSystem'
        });

        // Set default relevance configuration
        this.relevanceConfig = {
            recencyDecay: 0.05,
            frequencyWeight: 0.3,
            importanceWeight: 0.4,
            strengthWeight: 0.3,
            ...config.relevanceConfig
        };
    }

    /**
     * Initialize repositories
     */
    protected async initializeRepositories(): Promise<void> {
        this.motifRepository = this.createRepository<Motif>('motifs', [
            'type',
            'name',
            'tags',
            'importance'
        ]);
    }

    /**
     * Initialize the system
     */
    protected async initializeSystem(): Promise<void> {
        this.logInfo('Initializing Motif System');

        // Set up event listeners
        this.on('world:generated', this.onWorldGenerated.bind(this));
        this.on('character:created', this.onCharacterCreated.bind(this));
        this.on('quest:completed', this.onQuestCompleted.bind(this));
    }

    /**
     * Shutdown the system
     */
    protected async shutdownSystem(): Promise<void> {
        this.logInfo('Shutting down Motif System');
    }

    /**
     * Create a new motif
     */
    public async createMotif(params: MotifCreateParams): Promise<Motif> {
        this.logInfo(`Creating motif: ${params.name}`);

        const motif: Motif = {
            ...createBaseEntity(),
            type: params.type,
            name: params.name,
            description: params.description,
            tags: params.tags || [],
            importance: params.importance || 50, // Default to medium importance
            occurrences: [],
            relevanceScore: 0
        };

        const createdMotif = await this.motifRepository.create(motif);

        // Emit motif created event
        this.emitEvent({
            type: 'motif:created',
            source: this.name,
            timestamp: Date.now(),
            data: {
                motifId: createdMotif.id,
                name: createdMotif.name,
                type: createdMotif.type
            }
        });

        return createdMotif;
    }

    /**
     * Record a new occurrence of a motif
     */
    public async recordOccurrence(params: MotifOccurrenceParams): Promise<Motif> {
        const motif = await this.motifRepository.findById(params.motifId);

        if (!motif) {
            throw new Error(`Motif not found with ID: ${params.motifId}`);
        }

        this.logInfo(`Recording occurrence of motif '${motif.name}' (${params.strength}% strength)`);

        // Create the occurrence
        const occurrence: MotifOccurrence = {
            id: `${motif.id}_occurrence_${Date.now()}`,
            timestamp: Date.now(),
            context: params.context,
            strength: params.strength,
            entityIds: params.entityIds
        };

        // Add to occurrences list
        const updatedOccurrences = [
            ...motif.occurrences,
            occurrence
        ];

        // Update the motif with new occurrence and recalculate relevance
        const updatedMotif = await this.motifRepository.update(motif.id, {
            occurrences: updatedOccurrences
        });

        if (updatedMotif) {
            // Calculate new relevance score
            const relevanceScore = this.calculateRelevanceScore(updatedMotif);

            // Update relevance score
            await this.motifRepository.update(motif.id, {
                relevanceScore
            });

            // Emit motif occurrence event
            this.emitEvent({
                type: 'motif:occurrence',
                source: this.name,
                timestamp: Date.now(),
                data: {
                    motifId: updatedMotif.id,
                    occurrenceId: occurrence.id,
                    strength: occurrence.strength,
                    entities: occurrence.entityIds,
                    relevanceScore
                }
            });

            // Return updated motif with relevance score
            return {
                ...updatedMotif,
                relevanceScore
            };
        }

        return motif;
    }

    /**
     * Calculate the relevance score for a motif based on recency, frequency, importance, and strength
     */
    private calculateRelevanceScore(motif: Motif): number {
        const now = Date.now();
        const config = this.relevanceConfig;

        // No occurrences means no relevance
        if (motif.occurrences.length === 0) {
            return 0;
        }

        // Calculate recency score based on most recent occurrence
        const mostRecentTimestamp = Math.max(...motif.occurrences.map(o => o.timestamp));
        const daysSinceLastOccurrence = (now - mostRecentTimestamp) / (1000 * 60 * 60 * 24);
        const recencyScore = Math.max(0, 100 - (daysSinceLastOccurrence * config.recencyDecay * 100));

        // Calculate frequency score based on number of occurrences (capped at 20)
        const occurrenceCount = Math.min(motif.occurrences.length, 20);
        const frequencyScore = (occurrenceCount / 20) * 100;

        // Calculate average strength score
        const averageStrength = motif.occurrences.reduce((sum, o) => sum + o.strength, 0) / motif.occurrences.length;

        // Calculate weighted score
        const weightedScore =
            (recencyScore * (1 - config.frequencyWeight - config.importanceWeight - config.strengthWeight)) +
            (frequencyScore * config.frequencyWeight) +
            (motif.importance * config.importanceWeight) +
            (averageStrength * config.strengthWeight);

        // Return rounded score
        return Math.round(weightedScore);
    }

    /**
     * Find motifs relevant to a specific context or entity
     */
    public async findRelevantMotifs(query: MotifQuery): Promise<Motif[]> {
        const {
            types,
            tags,
            entityIds,
            minRelevance = 0,
            limit
        } = query;

        // First, get all motifs that match the basic criteria
        let motifs = await this.motifRepository.query((motif) => {
            // Filter by types if specified
            if (types && types.length > 0 && !types.includes(motif.type)) {
                return false;
            }

            // Filter by tags if specified
            if (tags && tags.length > 0 && !tags.some(tag => motif.tags.includes(tag))) {
                return false;
            }

            // Filter by minimum relevance
            if (motif.relevanceScore < minRelevance) {
                return false;
            }

            return true;
        });

        // If entity IDs are specified, calculate relevance to those specific entities
        if (entityIds && entityIds.length > 0) {
            // Calculate entity-specific scores for each motif
            motifs = motifs.map(motif => {
                // Find occurrences involving these entities
                const relevantOccurrences = motif.occurrences.filter(occurrence =>
                    occurrence.entityIds.some(id => entityIds.includes(id))
                );

                // Create a copy with recalculated relevance score specific to these entities
                if (relevantOccurrences.length > 0) {
                    // Make a copy with filtered occurrences
                    const contextSpecificMotif = {
                        ...motif,
                        occurrences: relevantOccurrences
                    };

                    // Calculate context-specific relevance
                    const contextRelevance = this.calculateRelevanceScore(contextSpecificMotif);

                    // Return motif with context-specific relevance
                    return {
                        ...motif,
                        relevanceScore: contextRelevance
                    };
                }

                // If no relevant occurrences, set relevance to 0 for this context
                return {
                    ...motif,
                    relevanceScore: 0
                };
            });

            // Filter out motifs with no relevance to these entities
            motifs = motifs.filter(motif => motif.relevanceScore > minRelevance);
        }

        // Sort by relevance (high to low)
        motifs.sort((a, b) => b.relevanceScore - a.relevanceScore);

        // Limit results if specified
        if (limit && limit > 0) {
            return motifs.slice(0, limit);
        }

        return motifs;
    }

    /**
     * Get all motifs
     */
    public async getAllMotifs(): Promise<Motif[]> {
        return this.motifRepository.findAll();
    }

    /**
     * Get a motif by ID
     */
    public async getMotifById(id: string): Promise<Motif | null> {
        return this.motifRepository.findById(id);
    }

    /**
     * Update a motif
     */
    public async updateMotif(id: string, updates: Partial<Omit<Motif, 'id' | 'occurrences' | 'relevanceScore'>>): Promise<Motif | null> {
        // Get the current motif
        const motif = await this.motifRepository.findById(id);

        if (!motif) {
            this.logWarn(`Attempted to update non-existent motif: ${id}`);
            return null;
        }

        // Update the motif
        const updatedMotif = await this.motifRepository.update(id, updates);

        if (updatedMotif) {
            // Recalculate relevance score if the importance was updated
            if (updates.importance !== undefined) {
                const relevanceScore = this.calculateRelevanceScore(updatedMotif);
                await this.motifRepository.update(id, { relevanceScore });
                return { ...updatedMotif, relevanceScore };
            }
            return updatedMotif;
        }

        return null;
    }

    /**
     * Delete a motif
     */
    public async deleteMotif(id: string): Promise<boolean> {
        return this.motifRepository.delete(id);
    }

    /**
     * Event handlers
     */
    private async onWorldGenerated(event: SystemEvent): Promise<void> {
        this.logInfo('World generated event - setting up initial motifs');
        // Here you would initialize world motifs based on the generated world
    }

    private async onCharacterCreated(event: SystemEvent): Promise<void> {
        const characterId = event.data.characterId;
        this.logInfo(`Character created event for ${characterId} - analyzing for motifs`);
        // Here you would analyze character and potentially create character-related motifs
    }

    private async onQuestCompleted(event: SystemEvent): Promise<void> {
        const questId = event.data.questId;
        this.logInfo(`Quest completed event for ${questId} - recording motif occurrences`);
        // Here you would analyze quest outcomes and record relevant motif occurrences
    }
} 