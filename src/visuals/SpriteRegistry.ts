// SpriteRegistry.ts
// Manages building/module sprite assets: loading, caching, and lookup
// Asset dir: /assets/sprites/

import { Point, Size } from './types.ts';

/**
 * SpriteKey - Unique key for a building/module sprite
 */
export type SpriteKey = string; // e.g., 'house', 'factory:roof', etc.

/**
 * SpriteInstance - Represents a loaded sprite asset
 */
export interface SpriteInstance {
    key: SpriteKey;
    assetRef: HTMLImageElement;
    width: number;
    height: number;
}

/**
 * SpriteRegistry - Singleton for managing building/module sprites
 */
export class SpriteRegistry {
    private static _instance: SpriteRegistry;
    private spriteMap: Map<SpriteKey, SpriteInstance> = new Map();
    private assetDir: string = '/assets/sprites/';

    private constructor() { }

    /**
     * Get the singleton instance
     */
    public static getInstance(): SpriteRegistry {
        if (!SpriteRegistry._instance) {
            SpriteRegistry._instance = new SpriteRegistry();
        }
        return SpriteRegistry._instance;
    }

    /**
     * Register a sprite with a key and asset filename
     * @param key - Unique sprite key
     * @param filename - Asset filename (relative to assetDir)
     */
    public registerSprite(key: SpriteKey, filename: string) {
        if (this.spriteMap.has(key)) return;
        const img = new window.Image();
        img.src = this.assetDir + filename;
        img.onload = () => {
            this.spriteMap.set(key, {
                key,
                assetRef: img,
                width: img.width,
                height: img.height,
            });
        };
        // Set a placeholder immediately (will update on load)
        this.spriteMap.set(key, {
            key,
            assetRef: img,
            width: 0,
            height: 0,
        });
    }

    /**
     * Get a sprite by key
     * @param key - SpriteKey
     * @returns SpriteInstance | undefined
     */
    public getSprite(key: SpriteKey): SpriteInstance | undefined {
        return this.spriteMap.get(key);
    }

    /**
     * Preload a list of sprites
     * @param entries - Array of [key, filename]
     */
    public preloadSprites(entries: Array<[SpriteKey, string]>) {
        entries.forEach(([key, filename]) => this.registerSprite(key, filename));
    }

    /**
     * Clear the sprite cache (for testing or hot reload)
     */
    public clearCache() {
        this.spriteMap.clear();
    }

    // --- Integration stubs ---
    /**
     * Integrate with OverlayManager (stub)
     */
    public setOverlayManager(_manager: any) {
        // TODO: implement integration
    }

    /**
     * Integrate with DamageVisualSystem (stub)
     */
    public setDamageVisualSystem(_system: any) {
        // TODO: implement integration
    }

    // --- Performance notes ---
    // TODO: Use offscreen canvas for sprite batching
    // TODO: Minimize redraws to only changed sprites
    // TODO: Memory management for unused sprites
}

// Usage: const spriteRegistry = SpriteRegistry.getInstance();
