// SpriteRegistry.ts
// Singleton for managing building sprite assets and efficient loading/caching

export type SpriteKey = string;

interface Sprite {
    key: SpriteKey;
    image: HTMLImageElement;
}

export class SpriteRegistry {
    private static _instance: SpriteRegistry;
    private spriteMap: Map<string, SpriteKey> = new Map(); // buildingType/moduleType -> spriteKey
    private loadedSprites: Map<SpriteKey, HTMLImageElement> = new Map();
    private spriteBasePath: string = '/assets/sprites/';
    private defaultSpriteKey: SpriteKey = 'default';

    private constructor() {
        // Example mapping; in real use, load from config or data file
        this.spriteMap.set('house', 'house.png');
        this.spriteMap.set('factory', 'factory.png');
        this.spriteMap.set('roof', 'roof.png');
        this.spriteMap.set('wall', 'wall.png');
        this.spriteMap.set(this.defaultSpriteKey, 'default.png');
    }

    public static get instance(): SpriteRegistry {
        if (!SpriteRegistry._instance) {
            SpriteRegistry._instance = new SpriteRegistry();
        }
        return SpriteRegistry._instance;
    }

    public getSpriteKeyForType(type: string): SpriteKey {
        return this.spriteMap.get(type) || this.defaultSpriteKey;
    }

    public async preloadSprites(spriteKeys: SpriteKey[]): Promise<void> {
        await Promise.all(spriteKeys.map(key => this.loadSprite(key)));
    }

    public async loadSprite(key: SpriteKey): Promise<HTMLImageElement> {
        if (this.loadedSprites.has(key)) {
            return this.loadedSprites.get(key)!;
        }
        const img = new Image();
        img.src = this.spriteBasePath + key;
        await new Promise((resolve, reject) => {
            img.onload = () => resolve(undefined);
            img.onerror = reject;
        });
        this.loadedSprites.set(key, img);
        return img;
    }

    public async getSprite(type: string): Promise<Sprite> {
        const key = this.getSpriteKeyForType(type);
        const image = await this.loadSprite(key);
        return { key, image };
    }

    public invalidateCache(key?: SpriteKey) {
        if (key) {
            this.loadedSprites.delete(key);
        } else {
            this.loadedSprites.clear();
        }
    }

    // For integration with OverlayManager and DamageVisualSystem
    public getSpriteSync(type: string): Sprite | null {
        const key = this.getSpriteKeyForType(type);
        const image = this.loadedSprites.get(key);
        if (image) {
            return { key, image };
        }
        return null;
    }
} 