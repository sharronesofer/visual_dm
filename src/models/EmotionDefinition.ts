/**
 * Unified Emotion Model - Core Definitions
 *
 * Provides extensible, hierarchical emotion definitions and a centralized registry for emotion management.
 * Includes interfaces for emotion consumers and providers, and serialization support.
 *
 * Usage Example:
 *   const joy = new BasicEmotion('joy', 0.8, 1.0, 0.7, { performanceCritical: true });
 *   EmotionRegistry.instance.registerEmotion(joy);
 *   const all = EmotionRegistry.instance.getAllEmotions();
 */

export type EmotionMetadata = {
    /** If true, this emotion is critical for performance-sensitive contexts */
    performanceCritical?: boolean;
    /** Level of detail required for this emotion (1=low, 5=high) */
    fidelityLevel?: number; // 1 (low) - 5 (high)
    /** Domains where this emotion is relevant (e.g., 'combat', 'dialogue') */
    domainSpecific?: string[];
    [key: string]: any;
};

/**
 * Context object for emotion evaluation and filtering.
 */
export interface IEmotionContext {
    [key: string]: any;
}

/**
 * Abstract base class for all emotion definitions.
 * Supports hierarchical relationships and context-driven toggling.
 */
export abstract class EmotionDefinition {
    /** Unique name/identifier for the emotion */
    public readonly name: string;
    /** Intensity (0.0-1.0) */
    public intensity: number; // 0.0 - 1.0
    /** Valence (-1.0=negative, 1.0=positive) */
    public valence: number;   // -1.0 (negative) to 1.0 (positive)
    /** Arousal (0.0-1.0) */
    public arousal: number;   // 0.0 - 1.0
    /** Metadata for context toggling, fidelity, etc. */
    public metadata: EmotionMetadata;
    /** Parent emotions (for hierarchical/complex emotions) */
    public parentEmotions: EmotionDefinition[] = [];
    /** Child emotions (for hierarchical/complex emotions) */
    public childEmotions: EmotionDefinition[] = [];

    constructor(
        name: string,
        intensity: number,
        valence: number,
        arousal: number,
        metadata: EmotionMetadata = {}
    ) {
        this.name = name;
        this.intensity = intensity;
        this.valence = valence;
        this.arousal = arousal;
        this.metadata = metadata;
    }

    /**
     * Returns true if this emotion should be active in the given context.
     * Override for custom context logic.
     */
    public isActiveInContext(context: IEmotionContext): boolean {
        // Default: always active. Override for context-specific logic.
        return true;
    }

    /**
     * Returns a modifier for intensity based on context (default: 1.0).
     * Override for custom context logic.
     */
    public getIntensityModifier(context: IEmotionContext): number {
        // Default: no modifier. Override for context-specific logic.
        return 1.0;
    }

    /**
     * Serializes this emotion to a plain object for JSON export.
     */
    public toJSON(): object {
        return {
            name: this.name,
            intensity: this.intensity,
            valence: this.valence,
            arousal: this.arousal,
            metadata: this.metadata,
            parentEmotions: this.parentEmotions.map(e => e.name),
            childEmotions: this.childEmotions.map(e => e.name)
        };
    }
}

/**
 * Basic (atomic) emotion definition.
 * Example: joy, anger, sadness.
 */
export class BasicEmotion extends EmotionDefinition {
    constructor(
        name: string,
        intensity: number,
        valence: number,
        arousal: number,
        metadata: EmotionMetadata = {}
    ) {
        super(name, intensity, valence, arousal, metadata);
    }
}

/**
 * Complex (hierarchical) emotion definition.
 * Example: jealousy (anger + fear), nostalgia (joy + sadness).
 */
export class ComplexEmotion extends EmotionDefinition {
    constructor(
        name: string,
        intensity: number,
        valence: number,
        arousal: number,
        parents: EmotionDefinition[],
        metadata: EmotionMetadata = {}
    ) {
        super(name, intensity, valence, arousal, metadata);
        this.parentEmotions = parents;
        for (const parent of parents) {
            parent.childEmotions.push(this);
        }
    }
}

/**
 * Singleton registry for all emotion definitions.
 * Provides registration, lookup, filtering, and serialization.
 *
 * Usage:
 *   const registry = EmotionRegistry.instance;
 *   registry.registerEmotion(new BasicEmotion(...));
 *   const joy = registry.getEmotionByName('joy');
 */
export class EmotionRegistry {
    private static _instance: EmotionRegistry;
    private emotions: Map<string, EmotionDefinition> = new Map();

    private constructor() { }

    /** Returns the singleton instance of the registry. */
    public static get instance(): EmotionRegistry {
        if (!EmotionRegistry._instance) {
            EmotionRegistry._instance = new EmotionRegistry();
        }
        return EmotionRegistry._instance;
    }

    /** Register a new emotion definition. */
    public registerEmotion(emotion: EmotionDefinition): void {
        this.emotions.set(emotion.name, emotion);
    }

    /** Retrieve an emotion by name. */
    public getEmotionByName(name: string): EmotionDefinition | undefined {
        return this.emotions.get(name);
    }

    /** Get all registered emotions. */
    public getAllEmotions(): EmotionDefinition[] {
        return Array.from(this.emotions.values());
    }

    /** Filter emotions by context. */
    public getEmotionsForContext(context: IEmotionContext): EmotionDefinition[] {
        return this.getAllEmotions().filter(e => e.isActiveInContext(context));
    }

    /** Serialize all emotions to a JSON string. */
    public serializeEmotions(): string {
        return JSON.stringify(this.getAllEmotions().map(e => e.toJSON()));
    }

    /**
     * Deserialize emotions from a JSON string.
     * Note: Only supports basic emotions for now.
     */
    public deserializeEmotions(data: string): void {
        // For now, only supports basic deserialization (no class methods)
        const arr = JSON.parse(data);
        for (const obj of arr) {
            const emotion = new BasicEmotion(
                obj.name,
                obj.intensity,
                obj.valence,
                obj.arousal,
                obj.metadata
            );
            this.registerEmotion(emotion);
        }
    }

    /**
     * Delete an emotion by name. Returns true if deleted, false if not found.
     */
    public deleteEmotionByName(name: string): boolean {
        return this.emotions.delete(name);
    }
}

/**
 * Interface for systems that consume emotion data.
 * Example: animation, dialogue, AI.
 */
export interface IEmotionConsumer {
    consumeEmotion(emotion: EmotionDefinition, context: IEmotionContext): void;
}

/**
 * Interface for systems that provide/generate emotion data.
 */
export interface IEmotionProvider {
    provideEmotions(context: IEmotionContext): EmotionDefinition[];
} 