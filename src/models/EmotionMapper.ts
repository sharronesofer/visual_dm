/**
 * EmotionMapper: Bidirectional Emotion Mapping System
 *
 * Translates between emotion definitions and their visual, behavioral, and internal state representations.
 * Supports bidirectional mapping, extensible strategies, change notification, configuration, and caching.
 *
 * Usage Example:
 *   const mapper = new EmotionMapper();
 *   mapper.registerMapping('visual', new MyVisualMapping());
 *   const result = mapper.mapToRepresentation('visual', joyEmotion, context);
 *   mapper.subscribe('visual', (change) => { ... });
 */
import { EmotionDefinition, IEmotionContext } from './EmotionDefinition';

/**
 * Context for mapping decisions (character, system load, etc.)
 */
export interface MappingContext extends IEmotionContext {
    characterType?: string;
    systemLoad?: number;
    [key: string]: any;
}

/**
 * Standardized mapping result
 */
export interface EmotionMappingResult {
    representation: any; // e.g., blend shape values, animation params, etc.
    confidence?: number; // 0.0-1.0, for reverse mapping
    notes?: string;
}

/**
 * Base interface for all mapping strategies
 */
export interface IEmotionMapping {
    mapToRepresentation(
        emotion: EmotionDefinition,
        context: MappingContext
    ): EmotionMappingResult;
    mapToEmotion(
        representation: any,
        context: MappingContext
    ): EmotionDefinition | null;
}

/**
 * Visual mapping: facial expressions, blend shapes, animation triggers
 */
export interface VisualEmotionMapping extends IEmotionMapping {
    // Optionally extend with visual-specific methods
}

/**
 * Behavioral mapping: voice tone, gestures, posture
 */
export interface BehavioralEmotionMapping extends IEmotionMapping {
    // Optionally extend with behavioral-specific methods
}

/**
 * Internal mapping: memory impact, decision influence
 */
export interface InternalEmotionMapping extends IEmotionMapping {
    // Optionally extend with internal-specific methods
}

/**
 * Observer callback for change notifications
 */
export type EmotionMappingChangeCallback = (change: {
    layer: string;
    emotion: EmotionDefinition;
    representation: any;
    context: MappingContext;
}) => void;

/**
 * LRU Cache for mapping results
 */
class LRUCache<K, V> {
    private maxSize: number;
    private map: Map<K, V>;

    constructor(maxSize: number = 100) {
        this.maxSize = maxSize;
        this.map = new Map();
    }

    get(key: K): V | undefined {
        if (!this.map.has(key)) return undefined;
        const value = this.map.get(key)!;
        this.map.delete(key);
        this.map.set(key, value);
        return value;
    }

    set(key: K, value: V): void {
        if (this.map.has(key)) this.map.delete(key);
        else if (this.map.size >= this.maxSize) this.map.delete(this.map.keys().next().value);
        this.map.set(key, value);
    }
}

/**
 * Main EmotionMapper class
 */
export class EmotionMapper {
    private mappings: Map<string, IEmotionMapping> = new Map();
    private observers: Map<string, Set<EmotionMappingChangeCallback>> = new Map();
    private config: Record<string, any> = {};
    private cache: LRUCache<string, EmotionMappingResult>;

    constructor(cacheSize: number = 100) {
        this.cache = new LRUCache(cacheSize);
    }

    /**
     * Register a mapping strategy for a given layer (e.g., 'visual', 'behavioral', 'internal')
     */
    public registerMapping(layer: string, mapping: IEmotionMapping): void {
        this.mappings.set(layer, mapping);
    }

    /**
     * Unregister a mapping strategy
     */
    public unregisterMapping(layer: string): void {
        this.mappings.delete(layer);
    }

    /**
     * Map an emotion to a representation for a given layer
     */
    public mapToRepresentation(
        layer: string,
        emotion: EmotionDefinition,
        context: MappingContext = {}
    ): EmotionMappingResult | null {
        const mapping = this.mappings.get(layer);
        if (!mapping) return null;
        const cacheKey = this.makeCacheKey(layer, emotion, context);
        const cached = this.cache.get(cacheKey);
        if (cached) return cached;
        const result = mapping.mapToRepresentation(emotion, context);
        this.cache.set(cacheKey, result);
        this.notify(layer, emotion, result.representation, context);
        return result;
    }

    /**
     * Map a representation back to an emotion for a given layer
     */
    public mapToEmotion(
        layer: string,
        representation: any,
        context: MappingContext = {}
    ): EmotionDefinition | null {
        const mapping = this.mappings.get(layer);
        if (!mapping) return null;
        return mapping.mapToEmotion(representation, context);
    }

    /**
     * Subscribe to change notifications for a given layer
     */
    public subscribe(layer: string, callback: EmotionMappingChangeCallback): void {
        if (!this.observers.has(layer)) this.observers.set(layer, new Set());
        this.observers.get(layer)!.add(callback);
    }

    /**
     * Unsubscribe from change notifications
     */
    public unsubscribe(layer: string, callback: EmotionMappingChangeCallback): void {
        this.observers.get(layer)?.delete(callback);
    }

    /**
     * Load configuration for custom mappings (e.g., from JSON)
     */
    public loadConfig(config: Record<string, any>): void {
        this.config = config;
    }

    /**
     * Get current configuration
     */
    public getConfig(): Record<string, any> {
        return this.config;
    }

    /**
     * Internal: Notify observers of a mapping change
     */
    private notify(
        layer: string,
        emotion: EmotionDefinition,
        representation: any,
        context: MappingContext
    ) {
        if (!this.observers.has(layer)) return;
        for (const cb of this.observers.get(layer)!) {
            cb({ layer, emotion, representation, context });
        }
    }

    /**
     * Internal: Create a cache key for mapping results
     */
    private makeCacheKey(
        layer: string,
        emotion: EmotionDefinition,
        context: MappingContext
    ): string {
        return `${layer}:${emotion.name}:${emotion.intensity}:${emotion.valence}:${emotion.arousal}:${JSON.stringify(context)}`;
    }
} 