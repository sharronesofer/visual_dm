import { compressToUTF16, decompressFromUTF16 } from 'lz-string';

/**
 * Version of the context serialization schema
 */
export const CONTEXT_VERSION = 1;

/**
 * Priority tags for context elements
 */
export type ContextPriority = 'essential' | 'optional';

/**
 * GPTContext element type
 */
export interface GPTContextElement {
    key: string;
    value: any;
    priority: ContextPriority;
}

/**
 * GPTContext is a map of key to GPTContextElement
 */
export type GPTContext = Record<string, GPTContextElement>;

/**
 * Serialized context format
 */
export interface SerializedGPTContext {
    version: number;
    elements: GPTContextElement[];
}

/**
 * Helper to calculate the size (in bytes) of a string
 */
export function getStringSize(str: string): number {
    return new Blob([str]).size;
}

/**
 * ContextSerializer handles serialization, compression, and restoration of GPT context
 */
export class ContextSerializer {
    static MAX_SIZE_BYTES = 32 * 1024; // 32KB default max size

    /**
     * Serialize and compress the context for storage
     */
    static serialize(context: GPTContext): string {
        const elements = Object.values(context);
        const payload: SerializedGPTContext = {
            version: CONTEXT_VERSION,
            elements,
        };
        let json = JSON.stringify(payload);
        // Compress if large
        if (getStringSize(json) > 2048) {
            try {
                json = compressToUTF16(json);
                return JSON.stringify({ compressed: true, data: json });
            } catch (e) {
                // Fallback to plain JSON
            }
        }
        return JSON.stringify({ compressed: false, data: json });
    }

    /**
     * Decompress and deserialize the context from storage
     */
    static deserialize(serialized: string): GPTContext {
        const wrapper = JSON.parse(serialized);
        let json: string = wrapper.data;
        if (wrapper.compressed) {
            try {
                json = decompressFromUTF16(json);
            } catch (e) {
                throw new Error('Failed to decompress GPT context');
            }
        }
        const payload: SerializedGPTContext = JSON.parse(json);
        if (typeof payload.version !== 'number' || !Array.isArray(payload.elements)) {
            throw new Error('Invalid GPT context format');
        }
        // Migration logic for future versions can go here
        const context: GPTContext = {};
        for (const el of payload.elements) {
            context[el.key] = el;
        }
        return context;
    }

    /**
     * Prune context to fit within max size, dropping optional elements first
     */
    static pruneToFit(context: GPTContext, maxBytes = ContextSerializer.MAX_SIZE_BYTES): GPTContext {
        let elements = Object.values(context);
        // Sort: essential first
        elements = elements.sort((a, b) => (a.priority === 'essential' ? -1 : 1));
        let pruned: GPTContext = {};
        for (const el of elements) {
            pruned[el.key] = el;
            const testStr = ContextSerializer.serialize(pruned);
            if (getStringSize(testStr) > maxBytes) {
                delete pruned[el.key];
                if (el.priority === 'essential') break; // Stop if we can't fit essentials
            }
        }
        return pruned;
    }

    /**
     * Helper to tag context elements by priority
     */
    static tagElement(key: string, value: any, priority: ContextPriority = 'optional'): GPTContextElement {
        return { key, value, priority };
    }

    /**
     * Calculate the size of the serialized context
     */
    static getSerializedSize(context: GPTContext): number {
        return getStringSize(ContextSerializer.serialize(context));
    }
}

/**
 * Stub for integration: capture context on interruption event
 * (To be wired up in the main system)
 */
export function captureContextOnInterruption(context: GPTContext, saveFn: (data: string) => void) {
    const pruned = ContextSerializer.pruneToFit(context);
    const serialized = ContextSerializer.serialize(pruned);
    saveFn(serialized);
} 