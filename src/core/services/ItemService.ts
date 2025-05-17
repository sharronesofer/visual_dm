import { Pool } from 'pg';
import { BaseItem, ItemType, RarityTier, ItemWithRarity, ItemRarity } from '../interfaces/types/loot';
import { Item } from '../models/Item';
import { ItemDatabaseService } from './ItemDatabaseService';
import { InventoryService } from './InventoryService';
import { initializeItemDatabase } from '../data/ItemTemplates';

export class ItemService {
  private pool: Pool;
  private itemDatabase: ItemDatabaseService;
  private playerInventory: InventoryService;
  private initialized: boolean = false;

  constructor(pool: Pool) {
    this.pool = pool;
    this.itemDatabase = new ItemDatabaseService();
    this.playerInventory = new InventoryService();
  }

  /**
   * Initialize the item system with predefined templates
   */
  initialize(): void {
    if (this.initialized) {
      return;
    }

    // Initialize item database with templates
    initializeItemDatabase(this.itemDatabase);
    this.initialized = true;
  }

  /**
   * Get the item database service
   */
  getItemDatabase(): ItemDatabaseService {
    this.ensureInitialized();
    return this.itemDatabase;
  }

  /**
   * Get the player inventory service
   */
  getPlayerInventory(): InventoryService {
    this.ensureInitialized();
    return this.playerInventory;
  }

  /**
   * Make sure the item system is initialized
   */
  private ensureInitialized(): void {
    if (!this.initialized) {
      this.initialize();
    }
  }

  /**
   * Create a new item (in-memory approach)
   */
  createItem(item: Omit<BaseItem, 'id' | 'createdAt' | 'updatedAt'>): Item {
    this.ensureInitialized();

    const newItem = new Item({
      ...item,
      id: undefined, // Will be auto-generated
      createdAt: new Date(),
      updatedAt: new Date()
    });

    return newItem;
  }

  /**
   * Get an item by ID from the item database
   */
  getItem(id: string): Item | undefined {
    this.ensureInitialized();
    return this.itemDatabase.getItem(id);
  }

  /**
   * Update an existing item
   */
  updateItem(id: string, updates: Partial<BaseItem>): Item | null {
    this.ensureInitialized();

    const item = this.itemDatabase.getItem(id);
    if (!item) {
      return null;
    }

    // Apply updates
    if (updates.name !== undefined) {
      item.name = updates.name;
    }

    if (updates.description !== undefined) {
      item.description = updates.description;
    }

    if (updates.weight !== undefined) {
      item.weight = updates.weight;
    }

    if (updates.value !== undefined) {
      item.value = updates.value;
    }

    if (updates.baseStats !== undefined) {
      item.baseStats = updates.baseStats;
    }

    if (updates.type !== undefined) {
      item.type = updates.type;
    }

    // Update the timestamp
    item.updatedAt = new Date();

    return item;
  }

  /**
   * Delete an item (not applicable to in-memory system)
   */
  deleteItem(id: string): boolean {
    // This is a no-op for in-memory storage
    return true;
  }

  /**
   * Get items with optional filtering
   */
  getItems(filters?: {
    type?: ItemType;
    minValue?: number;
    maxValue?: number;
    rarity?: ItemRarity;
  }): Item[] {
    this.ensureInitialized();

    return this.itemDatabase.searchItems({
      type: filters?.type,
      minValue: filters?.minValue,
      maxValue: filters?.maxValue,
      rarity: filters?.rarity
    });
  }

  /**
   * Generate a random item from templates
   */
  generateRandomItem(itemType?: ItemType): Item | null {
    this.ensureInitialized();

    // Get all templates matching the type
    const templates = this.itemDatabase.listTemplates(itemType ? { type: itemType } : undefined);

    if (templates.length === 0) {
      return null;
    }

    // Select a random template
    const template = templates[Math.floor(Math.random() * templates.length)];

    // Generate an item from the template
    return this.itemDatabase.generateItemFromTemplate(template.id);
  }

  /**
   * Generate a magical item (rare or better)
   */
  generateMagicalItem(itemType?: ItemType): Item | null {
    this.ensureInitialized();
    return this.itemDatabase.generateMagicalItem(itemType);
  }

  /**
   * Create a loot drop based on difficulty level
   */
  generateLootDrop(
    difficulty: number,
    count: number = 1,
    guaranteedTypes?: ItemType[]
  ): Item[] {
    this.ensureInitialized();

    const loot: Item[] = [];

    // Add guaranteed types first
    if (guaranteedTypes && guaranteedTypes.length > 0) {
      for (const type of guaranteedTypes) {
        const item = this.generateRandomItem(type);
        if (item) {
          loot.push(item);
        }
      }
    }

    // Add random items until we reach the count
    while (loot.length < count) {
      // Higher difficulty increases chances of magical items
      const magicalChance = Math.min(0.05 + (difficulty * 0.03), 0.5);

      if (Math.random() < magicalChance) {
        const magicalItem = this.generateMagicalItem();
        if (magicalItem) {
          loot.push(magicalItem);
          continue;
        }
      }

      // Otherwise, generate a normal item
      const item = this.generateRandomItem();
      if (item) {
        loot.push(item);
      }
    }

    return loot;
  }

  /**
   * Add an item to player inventory
   */
  addItemToInventory(item: Item, quantity: number = 1): string | null {
    this.ensureInitialized();
    return this.playerInventory.addItem(item, quantity);
  }

  /**
   * Remove an item from player inventory
   */
  removeItemFromInventory(slotId: string, quantity: number = 1): boolean {
    this.ensureInitialized();
    return this.playerInventory.removeItem(slotId, quantity);
  }

  /**
   * Check if player has an item
   */
  playerHasItem(itemId: string, quantity: number = 1): boolean {
    this.ensureInitialized();
    return this.playerInventory.hasItem(itemId, quantity);
  }

  /**
   * Get player inventory summary
   */
  getInventorySummary() {
    this.ensureInitialized();
    return this.playerInventory.getSummary();
  }

  /**
   * Equip an item from inventory
   */
  equipItem(slotId: string): boolean {
    this.ensureInitialized();
    return this.playerInventory.equipItem(slotId);
  }

  /**
   * Unequip an item
   */
  unequipItem(slotId: string): boolean {
    this.ensureInitialized();
    return this.playerInventory.unequipItem(slotId);
  }

  /**
   * Get equipped items
   */
  getEquippedItems() {
    this.ensureInitialized();
    return this.playerInventory.getEquippedSlots();
  }

  /**
   * Upgrade player inventory capacity
   */
  upgradeInventory(additionalWeight: number = 10, additionalSlots: number = 5): void {
    this.ensureInitialized();
    this.playerInventory.upgradeCapacity(additionalWeight, additionalSlots);
  }

  /**
   * Get all rarity tiers
   */
  getRarityTiers(): RarityTier[] {
    this.ensureInitialized();
    return this.itemDatabase.getRarities();
  }

  /**
   * Create loot table for a location/enemy
   */
  createLootTable(
    entityType: 'location' | 'enemy',
    entityId: string,
    items: Array<{ itemType: ItemType, weight: number, count: number }>
  ): boolean {
    // In a real implementation, this would persist the loot table
    // For now, we'll just return true to indicate success
    return true;
  }

  /**
   * Roll for loot from a loot table
   */
  rollLoot(
    entityType: 'location' | 'enemy',
    entityId: string,
    difficultyModifier: number = 1.0
  ): Item[] {
    // In a real implementation, this would use the stored loot table
    // For now, we'll generate random loot
    const itemCount = Math.floor(Math.random() * 3) + 1; // 1-3 items
    return this.generateLootDrop(difficultyModifier, itemCount);
  }

  // DATABASE METHODS FOR PERSISTENCE (Optional)
  // These methods can be used if/when we need to persist items to the database

  /**
   * Save an in-memory item to the database
   */
  async saveItemToDatabase(item: Item): Promise<string> {
    const query = `
      INSERT INTO items (name, description, type, weight, value, base_stats)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING id
    `;

    const values = [
      item.name,
      item.description,
      item.type,
      item.weight,
      item.value,
      JSON.stringify(item.baseStats)
    ];

    const result = await this.pool.query(query, values);
    return result.rows[0].id;
  }

  /**
   * Load all database items into memory
   */
  async loadItemsFromDatabase(): Promise<void> {
    const query = `
      SELECT i.*, r.*
      FROM items i
      LEFT JOIN rarity_tiers r ON i.rarity_id = r.id
    `;

    const result = await this.pool.query(query);

    for (const row of result.rows) {
      const baseItem = this.mapRowToItem(row);
      const item = new Item(baseItem);

      // If it has a rarity, set it
      if (row.rarity_id) {
        const rarity: RarityTier = {
          id: row.rarity_id,
          name: row.rarity_name,
          probability: parseFloat(row.probability),
          valueMultiplier: parseFloat(row.value_multiplier),
          colorHex: row.color_hex
        };

        item.setRarity(rarity);
      }
    }
  }

  /**
   * Map a database row to a BaseItem
   */
  private mapRowToItem(row: any): BaseItem {
    return {
      id: row.id,
      name: row.name,
      description: row.description,
      type: row.type as ItemType,
      weight: parseFloat(row.weight),
      value: parseInt(row.value),
      baseStats: row.base_stats,
      createdAt: row.created_at,
      updatedAt: row.updated_at
    };
  }
} 