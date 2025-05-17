import { v4 as uuidv4 } from 'uuid';
import { BaseItem, ItemType, ItemRarity, RarityTier } from '../interfaces/types/loot';
import { Item, ItemProperty } from '../models/Item';

export interface ItemTemplate {
    id: string;
    name: string;
    description: string;
    type: ItemType;
    baseWeight: number;
    baseValue: number;
    baseStats: Record<string, number>;
    possibleProperties: ItemProperty[];
    rarityWeights: Record<string, number>; // Which rarities can this template generate
    tags: string[]; // For categorization
}

export interface ItemFilter {
    type?: ItemType | ItemType[];
    minValue?: number;
    maxValue?: number;
    rarity?: ItemRarity | ItemRarity[];
    tag?: string | string[];
    search?: string; // Text search on name/description
    minDurability?: number;
    maxDurability?: number;
}

export class ItemDatabaseService {
    private templates: Map<string, ItemTemplate> = new Map();
    private items: Map<string, Item> = new Map();
    private rarities: Map<string, RarityTier> = new Map();

    constructor() {
        // Initialize with default rarities if none exist
        if (this.rarities.size === 0) {
            this.initializeDefaultRarities();
        }
    }

    /**
     * Initialize default rarities if none exist
     */
    private initializeDefaultRarities(): void {
        const defaultRarities: RarityTier[] = [
            {
                id: 1,
                name: ItemRarity.COMMON,
                probability: 0.6,
                valueMultiplier: 1.0,
                colorHex: '#FFFFFF'
            },
            {
                id: 2,
                name: ItemRarity.UNCOMMON,
                probability: 0.25,
                valueMultiplier: 1.5,
                colorHex: '#00FF00'
            },
            {
                id: 3,
                name: ItemRarity.RARE,
                probability: 0.1,
                valueMultiplier: 3.0,
                colorHex: '#0000FF'
            },
            {
                id: 4,
                name: ItemRarity.EPIC,
                probability: 0.04,
                valueMultiplier: 6.0,
                colorHex: '#A335EE'
            },
            {
                id: 5,
                name: ItemRarity.LEGENDARY,
                probability: 0.01,
                valueMultiplier: 12.0,
                colorHex: '#FF8000'
            }
        ];

        defaultRarities.forEach(rarity => {
            this.rarities.set(rarity.name.toString(), rarity);
        });
    }

    /**
     * Register an item template
     */
    registerTemplate(template: Omit<ItemTemplate, 'id'>): string {
        const id = uuidv4();
        const newTemplate: ItemTemplate = {
            id,
            ...template
        };

        this.templates.set(id, newTemplate);
        return id;
    }

    /**
     * Get a template by ID
     */
    getTemplate(id: string): ItemTemplate | undefined {
        return this.templates.get(id);
    }

    /**
     * List all templates, optionally filtered
     */
    listTemplates(filter?: Partial<ItemFilter>): ItemTemplate[] {
        let templates = Array.from(this.templates.values());

        if (filter) {
            if (filter.type) {
                const types = Array.isArray(filter.type) ? filter.type : [filter.type];
                templates = templates.filter(t => types.includes(t.type));
            }

            if (filter.tag) {
                const tags = Array.isArray(filter.tag) ? filter.tag : [filter.tag];
                templates = templates.filter(t => tags.some(tag => t.tags.includes(tag)));
            }

            if (filter.search) {
                const search = filter.search.toLowerCase();
                templates = templates.filter(t =>
                    t.name.toLowerCase().includes(search) ||
                    t.description.toLowerCase().includes(search));
            }
        }

        return templates;
    }

    /**
     * Generate an item from a template
     */
    generateItemFromTemplate(
        templateId: string,
        overrides: Partial<BaseItem> = {},
        forceRarity?: ItemRarity
    ): Item | null {
        const template = this.templates.get(templateId);
        if (!template) {
            return null;
        }

        // Determine rarity
        let rarity: RarityTier | undefined;

        if (forceRarity && this.rarities.has(forceRarity)) {
            // Use forced rarity if provided
            rarity = this.rarities.get(forceRarity);
        } else {
            // Randomly determine rarity based on template weights
            const rarityRoll = Math.random();
            let cumulativeProbability = 0;

            // Sort rarities by their template weights
            const rarityEntries = Object.entries(template.rarityWeights)
                .sort((a, b) => b[1] - a[1]); // Sort by weight descending

            for (const [rarityName, weight] of rarityEntries) {
                cumulativeProbability += weight;
                if (rarityRoll <= cumulativeProbability && this.rarities.has(rarityName)) {
                    rarity = this.rarities.get(rarityName);
                    break;
                }
            }

            // Fallback to common if no rarity was selected
            if (!rarity && this.rarities.has(ItemRarity.COMMON)) {
                rarity = this.rarities.get(ItemRarity.COMMON);
            }
        }

        // Create the base item
        const baseItem: Partial<BaseItem> = {
            name: template.name,
            description: template.description,
            type: template.type,
            weight: template.baseWeight,
            value: template.baseValue,
            baseStats: { ...template.baseStats },
            ...overrides
        };

        const item = new Item(baseItem);

        // Apply rarity effects if a rarity was determined
        if (rarity) {
            item.setRarity(rarity);
        }

        // Randomly assign properties based on rarity
        const propertyCount = rarity ? Math.min(Math.floor(Math.random() * rarity.id + 1), template.possibleProperties.length) : 0;

        if (propertyCount > 0) {
            // Shuffle the properties array
            const shuffledProperties = [...template.possibleProperties].sort(() => Math.random() - 0.5);

            // Add the first N properties
            for (let i = 0; i < propertyCount; i++) {
                item.addProperty(shuffledProperties[i]);
            }
        }

        // Store the item in the database
        this.items.set(item.id, item);

        return item;
    }

    /**
     * Generate a magical item with guaranteed rarity of rare or higher
     */
    generateMagicalItem(itemType?: ItemType): Item | null {
        // Filter templates to matching type and those that can generate rare+ items
        const eligibleTemplates = this.listTemplates()
            .filter(t => {
                // Check if template can generate rare or better items
                const hasRarePlus = Object.entries(t.rarityWeights)
                    .some(([rarity, weight]) => {
                        return (rarity === ItemRarity.RARE || rarity === ItemRarity.EPIC || rarity === ItemRarity.LEGENDARY) && weight > 0;
                    });

                // Check if type matches if specified
                const matchesType = !itemType || t.type === itemType;

                return hasRarePlus && matchesType;
            });

        if (eligibleTemplates.length === 0) {
            return null;
        }

        // Select a random template
        const template = eligibleTemplates[Math.floor(Math.random() * eligibleTemplates.length)];

        // Determine rarity (RARE+)
        const rarities = [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY];
        const rarityWeights = rarities.map(r => template.rarityWeights[r] || 0);
        const totalWeight = rarityWeights.reduce((a, b) => a + b, 0);

        if (totalWeight <= 0) {
            return null;
        }

        const rarityRoll = Math.random() * totalWeight;
        let cumulativeWeight = 0;
        let selectedRarity = ItemRarity.RARE; // Default fallback

        for (let i = 0; i < rarities.length; i++) {
            cumulativeWeight += rarityWeights[i];
            if (rarityRoll <= cumulativeWeight) {
                selectedRarity = rarities[i];
                break;
            }
        }

        // Generate the item with the selected rarity
        return this.generateItemFromTemplate(template.id, {}, selectedRarity);
    }

    /**
     * Create a unique item with special properties
     */
    createUniqueItem(
        base: Partial<BaseItem>,
        properties: Omit<ItemProperty, 'id'>[],
        rarity: ItemRarity = ItemRarity.LEGENDARY
    ): Item | null {
        if (!this.rarities.has(rarity)) {
            return null;
        }

        // Create the item
        const item = new Item(base);

        // Set rarity
        item.setRarity(this.rarities.get(rarity)!);

        // Add all properties
        properties.forEach(property => {
            item.addProperty(property);
        });

        // Add special history event for unique creation
        item.addHistoryEvent({
            eventType: 'UNIQUE_CREATION',
            description: 'This unique item was created with special properties',
        });

        // Store the item
        this.items.set(item.id, item);

        return item;
    }

    /**
     * Get an item by ID
     */
    getItem(id: string): Item | undefined {
        return this.items.get(id);
    }

    /**
     * Search for items with filters
     */
    searchItems(filter: ItemFilter = {}): Item[] {
        let results = Array.from(this.items.values());

        // Apply type filter
        if (filter.type) {
            const types = Array.isArray(filter.type) ? filter.type : [filter.type];
            results = results.filter(item => types.includes(item.type));
        }

        // Apply value range filter
        if (filter.minValue !== undefined) {
            results = results.filter(item => item.value >= filter.minValue!);
        }

        if (filter.maxValue !== undefined) {
            results = results.filter(item => item.value <= filter.maxValue!);
        }

        // Apply rarity filter
        if (filter.rarity) {
            const rarities = Array.isArray(filter.rarity) ? filter.rarity : [filter.rarity];
            results = results.filter(item =>
                item.rarity && rarities.includes(item.rarity.name)
            );
        }

        // Apply tag filter by checking item properties
        if (filter.tag) {
            const tags = Array.isArray(filter.tag) ? filter.tag : [filter.tag];
            results = results.filter(item => {
                // Check if any property matches any tag
                return item.properties.some(prop =>
                    tags.some(tag => prop.name.toLowerCase().includes(tag.toLowerCase()))
                );
            });
        }

        // Apply text search
        if (filter.search) {
            const search = filter.search.toLowerCase();
            results = results.filter(item =>
                item.name.toLowerCase().includes(search) ||
                item.description.toLowerCase().includes(search)
            );
        }

        // Apply durability filter
        if (filter.minDurability !== undefined) {
            results = results.filter(item => item.currentDurability >= filter.minDurability!);
        }

        if (filter.maxDurability !== undefined) {
            results = results.filter(item => item.currentDurability <= filter.maxDurability!);
        }

        return results;
    }

    /**
     * Get all supported rarities
     */
    getRarities(): RarityTier[] {
        return Array.from(this.rarities.values());
    }

    /**
     * Register a new rarity tier
     */
    registerRarity(rarity: RarityTier): void {
        this.rarities.set(rarity.name.toString(), rarity);
    }

    /**
     * Get item categories based on item types
     */
    getCategories(): Record<string, number> {
        const categories: Record<string, number> = {};

        this.items.forEach(item => {
            const category = item.type.toString();
            categories[category] = (categories[category] || 0) + 1;
        });

        return categories;
    }
} 