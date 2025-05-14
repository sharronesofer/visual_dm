/**
 * RelationshipSystem.ts
 * 
 * Implements a comprehensive relationship system for tracking interpersonal
 * connections between entities, with affinity, trust, and familiarity metrics.
 */

import { BaseSystemManager, SystemConfig, SystemEvent } from './BaseSystemManager';
import { Repository } from './DatabaseLayer';
import {
    Relationship,
    RelationshipType,
    RelationshipEvent,
    createBaseEntity
} from './DataModels';

export interface RelationshipCreateParams {
    entityId1: string;
    entityId2: string;
    type: RelationshipType;
    affinity?: number;
    trust?: number;
    familiarity?: number;
    history?: RelationshipEvent[];
}

export interface RelationshipEventParams {
    description: string;
    affinityChange?: number;
    trustChange?: number;
    familiarityChange?: number;
    memoryIds?: string[];
}

export interface RelationshipQuery {
    entityId?: string;
    relatedEntityId?: string;
    types?: RelationshipType[];
    minAffinity?: number;
    maxAffinity?: number;
    minTrust?: number;
    minFamiliarity?: number;
    limit?: number;
}

/**
 * System for managing relationships between entities
 */
export class RelationshipSystem extends BaseSystemManager {
    private relationshipRepository!: Repository<Relationship>;

    constructor(config: SystemConfig) {
        super(config);
    }

    /**
     * Initialize relationship repositories
     */
    protected async initializeRepositories(): Promise<void> {
        this.relationshipRepository = this.createRepository<Relationship>('relationships', [
            'entityId1',
            'entityId2',
            'type'
        ]);
    }

    /**
     * Initialize the relationship system
     */
    protected async initializeSystem(): Promise<void> {
        // Register event handlers
        this.setupEventHandlers();
    }

    /**
     * Shut down the relationship system
     */
    protected async shutdownSystem(): Promise<void> {
        // No special shutdown needed
    }

    /**
     * Set up event handlers to update relationships based on game events
     */
    private setupEventHandlers(): void {
        // Handle interaction events
        this.on('entity:interaction', async (event) => {
            this.logDebug('Handling interaction event for relationship', event);
            const { data } = event;

            if (data.participants?.length >= 2) {
                const primaryEntityId = data.participants[0];

                // Create or update relationships between primary entity and all other participants
                for (let i = 1; i < data.participants.length; i++) {
                    const secondaryEntityId = data.participants[i];

                    // Get impact on relationship metrics, providing defaults if not specified
                    const affinityChange = data.relationshipChanges?.affinity?.[secondaryEntityId] ?? 0;
                    const trustChange = data.relationshipChanges?.trust?.[secondaryEntityId] ?? 0;
                    const familiarityChange = data.relationshipChanges?.familiarity?.[secondaryEntityId] ?? 1; // Default to small familiarity increase

                    if (affinityChange !== 0 || trustChange !== 0 || familiarityChange !== 0) {
                        await this.updateRelationshipWithEvent(
                            primaryEntityId,
                            secondaryEntityId,
                            {
                                description: data.description || 'Interaction',
                                affinityChange,
                                trustChange,
                                familiarityChange,
                                memoryIds: data.memoryIds || []
                            }
                        );
                    }
                }
            }
        });

        // Handle trade events
        this.on('entity:trade', async (event) => {
            this.logDebug('Handling trade event for relationship', event);
            const { data } = event;

            const buyerId = data.buyerId;
            const sellerId = data.sellerId;

            if (!buyerId || !sellerId) return;

            // Get the fairness rating of the trade (-100 to 100)
            const fairnessRating = data.fairnessRating || 0;

            // Calculate relationship changes based on trade fairness
            let affinityChange = 0;
            let trustChange = 0;

            if (fairnessRating < -50) {
                // Very unfair trade, negative impact
                affinityChange = -10;
                trustChange = -15;
            } else if (fairnessRating < -20) {
                // Somewhat unfair trade
                affinityChange = -5;
                trustChange = -8;
            } else if (fairnessRating > 50) {
                // Very generous trade
                affinityChange = 10;
                trustChange = 8;
            } else if (fairnessRating > 20) {
                // Fair trade with slight advantage
                affinityChange = 5;
                trustChange = 3;
            } else {
                // Balanced trade
                affinityChange = 2;
                trustChange = 1;
            }

            // Increase familiarity through the trade interaction
            const familiarityChange = 5;

            await this.updateRelationshipWithEvent(
                buyerId,
                sellerId,
                {
                    description: `Trade: ${data.description || 'Items exchanged'}`,
                    affinityChange,
                    trustChange,
                    familiarityChange,
                    memoryIds: data.memoryIds || []
                }
            );
        });

        // Handle quest events that affect relationships
        this.on('quest:update', async (event) => {
            this.logDebug('Handling quest update for relationship', event);
            const { data } = event;

            if (data.relationshipChanges && data.relationshipChanges.length > 0) {
                for (const change of data.relationshipChanges) {
                    const { entityId1, entityId2, affinityChange, trustChange, familiarityChange, description } = change;

                    if (entityId1 && entityId2) {
                        await this.updateRelationshipWithEvent(
                            entityId1,
                            entityId2,
                            {
                                description: description || `Quest update: ${data.questTitle || 'Unknown quest'}`,
                                affinityChange: affinityChange || 0,
                                trustChange: trustChange || 0,
                                familiarityChange: familiarityChange || 0,
                                memoryIds: data.memoryIds || []
                            }
                        );
                    }
                }
            }
        });

        // Handle combat events
        this.on('combat:action', async (event) => {
            this.logDebug('Handling combat action for relationship', event);
            const { data } = event;

            const actorId = data.actorId;
            const targetIds = data.targetIds || [];

            if (actorId && targetIds.length > 0) {
                for (const targetId of targetIds) {
                    // Negative impact on relationship when attacking
                    await this.updateRelationshipWithEvent(
                        actorId,
                        targetId,
                        {
                            description: data.description || 'Combat action',
                            affinityChange: -15,  // Significant negative affinity change
                            trustChange: -10,     // Reduced trust
                            familiarityChange: 3, // Still increases familiarity
                            memoryIds: data.memoryIds || []
                        }
                    );
                }
            }
        });
    }

    /**
     * Create a new relationship between entities
     */
    public async createRelationship(params: RelationshipCreateParams): Promise<Relationship> {
        // Always store smaller ID first for consistent retrieval
        const [entityId1, entityId2] = this.orderEntityIds(params.entityId1, params.entityId2);

        // Check if relationship already exists
        const existingRelationship = await this.getRelationship(entityId1, entityId2);
        if (existingRelationship) {
            this.logWarn(`Relationship between ${entityId1} and ${entityId2} already exists.`);
            return existingRelationship;
        }

        const baseEntity = createBaseEntity();
        const history = params.history || [];

        const relationship: Relationship = {
            ...baseEntity,
            entityId1,
            entityId2,
            type: params.type,
            affinity: params.affinity || 0,
            trust: params.trust || 0,
            familiarity: params.familiarity || 0,
            history
        };

        const createdRelationship = await this.relationshipRepository.create(relationship);

        // Emit relationship created event
        this.emitEvent({
            type: 'relationship:created',
            source: this.name,
            timestamp: Date.now(),
            data: {
                relationshipId: createdRelationship.id,
                entityId1,
                entityId2,
                relationType: createdRelationship.type
            }
        });

        return createdRelationship;
    }

    /**
     * Get relationship between two entities
     */
    public async getRelationship(entityId1: string, entityId2: string): Promise<Relationship | null> {
        // Always query with ordered IDs for consistency
        const [orderedId1, orderedId2] = this.orderEntityIds(entityId1, entityId2);

        // Query for relationship
        const relationships = await this.relationshipRepository.query(
            rel => rel.entityId1 === orderedId1 && rel.entityId2 === orderedId2,
            1
        );

        return relationships.length > 0 ? relationships[0] : null;
    }

    /**
     * Get all relationships for an entity
     */
    public async getEntityRelationships(entityId: string, query?: Omit<RelationshipQuery, 'entityId'>): Promise<Relationship[]> {
        return this.queryRelationships({
            ...query,
            entityId
        });
    }

    /**
     * Check if two entities have a relationship
     */
    public async hasRelationship(entityId1: string, entityId2: string): Promise<boolean> {
        const relationship = await this.getRelationship(entityId1, entityId2);
        return relationship !== null;
    }

    /**
     * Update an existing relationship with a new event
     */
    public async updateRelationshipWithEvent(
        entityId1: string,
        entityId2: string,
        eventParams: RelationshipEventParams
    ): Promise<Relationship> {
        // Get or create relationship
        let relationship = await this.getRelationship(entityId1, entityId2);

        // Create relationship if it doesn't exist
        if (!relationship) {
            relationship = await this.createRelationship({
                entityId1,
                entityId2,
                type: RelationshipType.ACQUAINTANCE
            });
        }

        // Create the event
        const event: RelationshipEvent = {
            id: `${relationship.id}_event_${Date.now()}`,
            timestamp: Date.now(),
            description: eventParams.description,
            affinityChange: eventParams.affinityChange || 0,
            trustChange: eventParams.trustChange || 0,
            familiarityChange: eventParams.familiarityChange || 0,
            memoryIds: eventParams.memoryIds || []
        };

        // Add event to history
        const updatedHistory = [...relationship.history, event];

        // Calculate new metrics
        const newAffinity = this.clampValue(relationship.affinity + (eventParams.affinityChange || 0), -100, 100);
        const newTrust = this.clampValue(relationship.trust + (eventParams.trustChange || 0), 0, 100);
        const newFamiliarity = this.clampValue(relationship.familiarity + (eventParams.familiarityChange || 0), 0, 100);

        // Determine new relationship type based on metrics if significant changes
        let newType = relationship.type;
        if (Math.abs(eventParams.affinityChange || 0) >= 10 || Math.abs(eventParams.trustChange || 0) >= 10) {
            newType = this.determineRelationshipType(newAffinity, newTrust);
        }

        // Update relationship
        const updatedRelationship = await this.relationshipRepository.update(relationship.id, {
            type: newType,
            affinity: newAffinity,
            trust: newTrust,
            familiarity: newFamiliarity,
            history: updatedHistory
        });

        if (!updatedRelationship) {
            throw new Error(`Failed to update relationship between ${entityId1} and ${entityId2}`);
        }

        // Emit relationship updated event
        this.emitEvent({
            type: 'relationship:updated',
            source: this.name,
            timestamp: Date.now(),
            data: {
                relationshipId: updatedRelationship.id,
                entityId1: updatedRelationship.entityId1,
                entityId2: updatedRelationship.entityId2,
                oldType: relationship.type,
                newType: updatedRelationship.type,
                affinityChange: eventParams.affinityChange || 0,
                trustChange: eventParams.trustChange || 0,
                familiarityChange: eventParams.familiarityChange || 0,
                event
            }
        });

        return updatedRelationship;
    }

    /**
     * Query relationships based on criteria
     */
    public async queryRelationships(query: RelationshipQuery): Promise<Relationship[]> {
        const {
            entityId,
            relatedEntityId,
            types,
            minAffinity = -100,
            maxAffinity = 100,
            minTrust = 0,
            minFamiliarity = 0,
            limit
        } = query;

        this.logDebug('Querying relationships with params:', query);

        return this.relationshipRepository.query((relationship) => {
            // Filter by entity involvement
            if (entityId) {
                const isInvolved = relationship.entityId1 === entityId || relationship.entityId2 === entityId;
                if (!isInvolved) return false;
            }

            // Filter by specific relationship
            if (entityId && relatedEntityId) {
                const [orderedId1, orderedId2] = this.orderEntityIds(entityId, relatedEntityId);
                if (relationship.entityId1 !== orderedId1 || relationship.entityId2 !== orderedId2) {
                    return false;
                }
            }

            // Filter by types
            if (types && types.length > 0 && !types.includes(relationship.type)) {
                return false;
            }

            // Filter by metrics
            if (relationship.affinity < minAffinity || relationship.affinity > maxAffinity) {
                return false;
            }

            if (relationship.trust < minTrust) {
                return false;
            }

            if (relationship.familiarity < minFamiliarity) {
                return false;
            }

            return true;
        }, limit);
    }

    /**
     * Set the relationship type directly
     */
    public async setRelationshipType(
        entityId1: string,
        entityId2: string,
        type: RelationshipType
    ): Promise<Relationship | null> {
        const relationship = await this.getRelationship(entityId1, entityId2);

        if (!relationship) {
            this.logWarn(`No relationship found between ${entityId1} and ${entityId2} to update type.`);
            return null;
        }

        const oldType = relationship.type;

        // Update the relationship type
        const updatedRelationship = await this.relationshipRepository.update(relationship.id, {
            type
        });

        if (updatedRelationship) {
            // Add an event to the history
            const event: RelationshipEvent = {
                id: `${relationship.id}_event_${Date.now()}`,
                timestamp: Date.now(),
                description: `Relationship changed from ${oldType} to ${type}`,
                affinityChange: 0,
                trustChange: 0,
                familiarityChange: 0,
                memoryIds: []
            };

            updatedRelationship.history.push(event);

            await this.relationshipRepository.update(relationship.id, {
                history: updatedRelationship.history
            });

            // Emit relationship type changed event
            this.emitEvent({
                type: 'relationship:type_changed',
                source: this.name,
                timestamp: Date.now(),
                data: {
                    relationshipId: updatedRelationship.id,
                    entityId1: updatedRelationship.entityId1,
                    entityId2: updatedRelationship.entityId2,
                    oldType,
                    newType: type
                }
            });
        }

        return updatedRelationship;
    }

    /**
     * Get all relationships by type
     */
    public async getRelationshipsByType(type: RelationshipType, limit?: number): Promise<Relationship[]> {
        return this.relationshipRepository.query(
            relationship => relationship.type === type,
            limit
        );
    }

    /**
     * Get entities with specific relationship to an entity
     */
    public async getRelatedEntities(
        entityId: string,
        type?: RelationshipType,
        minAffinity?: number,
        minTrust?: number
    ): Promise<string[]> {
        const relationships = await this.getEntityRelationships(entityId, {
            types: type ? [type] : undefined,
            minAffinity,
            minTrust
        });

        return relationships.map(rel => {
            // Return the ID of the other entity
            return rel.entityId1 === entityId ? rel.entityId2 : rel.entityId1;
        });
    }

    /**
     * Delete a relationship between entities
     */
    public async deleteRelationship(entityId1: string, entityId2: string): Promise<boolean> {
        const relationship = await this.getRelationship(entityId1, entityId2);

        if (!relationship) {
            this.logWarn(`No relationship found between ${entityId1} and ${entityId2} to delete.`);
            return false;
        }

        const deleted = await this.relationshipRepository.delete(relationship.id);

        if (deleted) {
            // Emit relationship deleted event
            this.emitEvent({
                type: 'relationship:deleted',
                source: this.name,
                timestamp: Date.now(),
                data: {
                    relationshipId: relationship.id,
                    entityId1,
                    entityId2
                }
            });
        }

        return deleted;
    }

    /**
     * Helper method to ensure consistent order of entity IDs
     */
    private orderEntityIds(id1: string, id2: string): [string, string] {
        return id1 < id2 ? [id1, id2] : [id2, id1];
    }

    /**
     * Helper method to clamp a value within a range
     */
    private clampValue(value: number, min: number, max: number): number {
        return Math.max(min, Math.min(max, value));
    }

    /**
     * Determine relationship type based on affinity and trust
     */
    private determineRelationshipType(affinity: number, trust: number): RelationshipType {
        if (affinity >= 80 && trust >= 80) {
            return RelationshipType.ROMANTIC;
        } else if (affinity >= 70 && trust >= 70) {
            return RelationshipType.FRIEND;
        } else if (affinity >= 60 && trust >= 50) {
            return RelationshipType.ALLY;
        } else if (affinity <= -70) {
            return RelationshipType.ENEMY;
        } else if (affinity <= -50 || (affinity <= -30 && trust <= 30)) {
            return RelationshipType.RIVAL;
        } else {
            return RelationshipType.ACQUAINTANCE;
        }
    }
} 