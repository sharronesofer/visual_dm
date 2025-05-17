import fs from 'fs';
import path from 'path';
import { StatusEffectParams } from './StatusEffect';

/**
 * Registry for loading and validating status effect definitions from configuration.
 */
export class StatusEffectRegistry {
    private static _instance: StatusEffectRegistry | null = null;
    private definitions: Map<string, StatusEffectParams> = new Map();

    private constructor() {
        this.loadDefinitions();
    }

    /**
     * Singleton instance accessor.
     */
    static get instance(): StatusEffectRegistry {
        if (!this._instance) {
            this._instance = new StatusEffectRegistry();
        }
        return this._instance;
    }

    /**
     * Loads and validates effect definitions from effectDefinitions.json.
     */
    private loadDefinitions(): void {
        const filePath = path.join(__dirname, 'effectDefinitions.json');
        if (!fs.existsSync(filePath)) {
            throw new Error(`Effect definitions file not found: ${filePath}`);
        }
        const raw = fs.readFileSync(filePath, 'utf-8');
        let json: any;
        try {
            json = JSON.parse(raw);
        } catch (e) {
            throw new Error('Invalid JSON in effectDefinitions.json');
        }
        if (!Array.isArray(json)) {
            throw new Error('effectDefinitions.json must be an array of effect definitions');
        }
        for (const def of json) {
            // Basic validation
            if (!def.id || !def.name || !def.type || !def.category || !def.durationType || typeof def.baseDuration !== 'number' || typeof def.maxStacks !== 'number' || !def.description) {
                throw new Error(`Invalid effect definition: ${JSON.stringify(def)}`);
            }
            this.definitions.set(def.id, def as StatusEffectParams);
        }
    }

    /**
     * Gets a status effect definition by ID.
     */
    getDefinition(id: string): StatusEffectParams | undefined {
        return this.definitions.get(id);
    }

    /**
     * Gets all definitions of a given type.
     */
    getDefinitionsByType(type: string): StatusEffectParams[] {
        return Array.from(this.definitions.values()).filter(def => def.type === type);
    }

    /**
     * Returns all effect definitions.
     */
    getAllDefinitions(): StatusEffectParams[] {
        return Array.from(this.definitions.values());
    }
}
