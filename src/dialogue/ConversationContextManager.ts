import { ConversationTurn } from './types';
import { GPTClient } from './GPTClient';
import { EventEmitter } from 'events';

export interface ContextManagerConfig {
    maxTokens?: number;
    maxTurns?: number;
    relevanceWeights?: {
        recency: number;
        semantic: number;
        interaction: number;
    };
    storageBackend?: ContextStorageBackend;
}

export interface ContextStorageBackend {
    save(turns: ConversationTurn[]): Promise<void> | void;
    load(): Promise<ConversationTurn[]> | ConversationTurn[];
}

/**
 * Default in-memory storage backend (no-op for persistence).
 */
export class InMemoryContextStorage implements ContextStorageBackend {
    private turns: ConversationTurn[] = [];
    save(turns: ConversationTurn[]) {
        this.turns = [...turns];
    }
    load() {
        return [...this.turns];
    }
}

/**
 * Manages conversation history, context windowing, relevance scoring, extraction, and persistence for GPT dialogue.
 * Emits 'contextUpdated', 'contextSaved', and 'contextLoaded' events.
 */
export class ConversationContextManager extends EventEmitter {
    private turns: ConversationTurn[] = [];
    private config: ContextManagerConfig;
    private storage: ContextStorageBackend;

    constructor(config: ContextManagerConfig = {}) {
        super();
        this.config = {
            maxTokens: config.maxTokens ?? 1024,
            maxTurns: config.maxTurns ?? 10,
            relevanceWeights: config.relevanceWeights ?? { recency: 1, semantic: 1, interaction: 1 },
            storageBackend: config.storageBackend ?? new InMemoryContextStorage(),
        };
        this.storage = this.config.storageBackend!;
    }

    /**
     * Adds a new conversation turn and emits 'contextUpdated'.
     */
    addTurn(role: ConversationTurn['role'], content: string) {
        this.turns.push({ role, content, timestamp: Date.now() });
        this.emit('contextUpdated', this.turns);
    }

    /**
     * Returns the most recent context as an array of strings, fitting within maxTokens.
     */
    getContext(maxTokens: number = this.config.maxTokens!): string[] {
        let tokens = 0;
        const context: string[] = [];
        for (let i = this.turns.length - 1; i >= 0; i--) {
            const turn = this.turns[i];
            const turnTokens = GPTClient.countTokens(turn.content);
            if (tokens + turnTokens > maxTokens) break;
            context.unshift(turn.content);
            tokens += turnTokens;
        }
        return context;
    }

    /**
     * Returns the last N turns as context.
     */
    getContextByTurns(maxTurns: number = this.config.maxTurns!): string[] {
        return this.turns.slice(-maxTurns).map(t => t.content);
    }

    /**
     * Clears the conversation history and emits 'contextUpdated'.
     */
    clearContext() {
        this.turns = [];
        this.emit('contextUpdated', this.turns);
    }

    /**
     * Calculates a relevance score for a turn (recency, semantic, interaction).
     * Semantic and interaction scoring are stubs for future extension.
     */
    scoreRelevance(turn: ConversationTurn, now: number = Date.now()): number {
        // Recency: newer turns are more relevant
        const recencyScore = 1 / (1 + (now - (turn.timestamp || now)) / 60000);
        // TODO: Add semantic similarity (e.g., embedding distance)
        const semanticScore = 1; // Placeholder
        // TODO: Add interaction type weighting
        const interactionScore = 1; // Placeholder
        const w = this.config.relevanceWeights!;
        return w.recency * recencyScore + w.semantic * semanticScore + w.interaction * interactionScore;
    }

    /**
     * Extracts key information (entities, facts, goals) from the conversation.
     * Stub: returns all user turns for now.
     * Extend with NLP/entity extraction as needed.
     */
    extractKeyInformation(): string[] {
        // Placeholder: return all user turns for now
        // TODO: Add entity/fact extraction using NLP or plugins
        return this.turns.filter(t => t.role === 'user').map(t => t.content);
    }

    /**
     * Returns all turns (for debugging/testing).
     */
    getAllTurns(): ConversationTurn[] {
        return [...this.turns];
    }

    /**
     * Saves the current context using the configured storage backend. Emits 'contextSaved'.
     */
    async saveContext() {
        await this.storage.save(this.turns);
        this.emit('contextSaved', this.turns);
    }

    /**
     * Loads context from the configured storage backend. Emits 'contextLoaded'.
     */
    async loadContext() {
        const loaded = await this.storage.load();
        this.turns = [...loaded];
        this.emit('contextLoaded', this.turns);
    }
}

export type { ContextManagerConfig, ContextStorageBackend }; 