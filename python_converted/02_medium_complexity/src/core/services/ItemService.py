from typing import Any, List



class ItemService {
  private pool: Pool
  constructor(pool: Pool) {
    this.pool = pool
  }
  /**
   * Create a new item
   */
  async createItem(item: Omit<BaseItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<BaseItem> {
    const query = `
      INSERT INTO items (name, description, type, weight, value, base_stats)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `
    const values = [
      item.name,
      item.description,
      item.type,
      item.weight,
      item.value,
      JSON.stringify(item.baseStats)
    ]
    const result = await this.pool.query(query, values)
    return this.mapRowToItem(result.rows[0])
  }
  /**
   * Get an item by ID
   */
  async getItem(id: str): Promise<ItemWithRarity | null> {
    const query = `
      SELECT i.*, r.*
      FROM items i
      LEFT JOIN rarity_tiers r ON i.rarity_id = r.id
      WHERE i.id = $1
    `
    const result = await this.pool.query(query, [id])
    if (result.rows.length === 0) {
      return null
    }
    return this.mapRowToItemWithRarity(result.rows[0])
  }
  /**
   * Update an existing item
   */
  async updateItem(id: str, updates: Partial<BaseItem>): Promise<BaseItem | null> {
    const setClause = []
    const values = [id]
    let paramIndex = 2
    if (updates.name !== undefined) {
      setClause.push(`name = $${paramIndex}`)
      values.push(updates.name)
      paramIndex++
    }
    if (updates.description !== undefined) {
      setClause.push(`description = $${paramIndex}`)
      values.push(updates.description)
      paramIndex++
    }
    if (updates.type !== undefined) {
      setClause.push(`type = $${paramIndex}`)
      values.push(updates.type)
      paramIndex++
    }
    if (updates.weight !== undefined) {
      setClause.push(`weight = $${paramIndex}`)
      values.push(updates.weight)
      paramIndex++
    }
    if (updates.value !== undefined) {
      setClause.push(`value = $${paramIndex}`)
      values.push(updates.value)
      paramIndex++
    }
    if (updates.baseStats !== undefined) {
      setClause.push(`base_stats = $${paramIndex}`)
      values.push(JSON.stringify(updates.baseStats))
      paramIndex++
    }
    if (setClause.length === 0) {
      return this.getItem(id)
    }
    const query = `
      UPDATE items
      SET ${setClause.join(', ')}
      WHERE id = $1
      RETURNING *
    `
    const result = await this.pool.query(query, values)
    if (result.rows.length === 0) {
      return null
    }
    return this.mapRowToItem(result.rows[0])
  }
  /**
   * Delete an item
   */
  async deleteItem(id: str): Promise<boolean> {
    const query = 'DELETE FROM items WHERE id = $1 RETURNING id'
    const result = await this.pool.query(query, [id])
    return result.rows.length > 0
  }
  /**
   * Get all items with optional filtering
   */
  async getItems(filters?: {
    type?: ItemType
    minValue?: float
    maxValue?: float
    rarityId?: float
  }): Promise<ItemWithRarity[]> {
    let query = `
      SELECT i.*, r.*
      FROM items i
      LEFT JOIN rarity_tiers r ON i.rarity_id = r.id
      WHERE 1=1
    `
    const values: List[any] = []
    let paramIndex = 1
    if (filters?.type) {
      query += ` AND i.type = $${paramIndex}`
      values.push(filters.type)
      paramIndex++
    }
    if (filters?.minValue !== undefined) {
      query += ` AND i.value >= $${paramIndex}`
      values.push(filters.minValue)
      paramIndex++
    }
    if (filters?.maxValue !== undefined) {
      query += ` AND i.value <= $${paramIndex}`
      values.push(filters.maxValue)
      paramIndex++
    }
    if (filters?.rarityId !== undefined) {
      query += ` AND i.rarity_id = $${paramIndex}`
      values.push(filters.rarityId)
      paramIndex++
    }
    const result = await this.pool.query(query, values)
    return result.rows.map(row => this.mapRowToItemWithRarity(row))
  }
  /**
   * Set the rarity of an item
   */
  async setItemRarity(itemId: str, rarityId: float): Promise<ItemWithRarity | null> {
    const query = `
      UPDATE items
      SET rarity_id = $2
      WHERE id = $1
      RETURNING *
    `
    const result = await this.pool.query(query, [itemId, rarityId])
    if (result.rows.length === 0) {
      return null
    }
    return this.getItem(itemId)
  }
  /**
   * Get all rarity tiers
   */
  async getRarityTiers(): Promise<RarityTier[]> {
    const query = 'SELECT * FROM rarity_tiers ORDER BY probability DESC'
    const result = await this.pool.query(query)
    return result.rows.map(row => ({
      id: row.id,
      name: row.name,
      probability: parseFloat(row.probability),
      valueMultiplier: parseFloat(row.value_multiplier),
      colorHex: row.color_hex
    }))
  }
  /**
   * Map a database row to a BaseItem
   */
  private mapRowToItem(row: Any): BaseItem {
    return {
      id: row.id,
      name: row.name,
      description: row.description,
      type: row.type as ItemType,
      weight: parseFloat(row.weight),
      value: parseInt(row.value),
      baseStats: row.base_stats as BaseStats,
      createdAt: row.created_at,
      updatedAt: row.updated_at
    }
  }
  /**
   * Map a database row to an ItemWithRarity
   */
  private mapRowToItemWithRarity(row: Any): ItemWithRarity {
    const baseItem = this.mapRowToItem(row)
    return {
      ...baseItem,
      rarity: row.rarity_id ? {
        id: row.rarity_id,
        name: row.name,
        probability: parseFloat(row.probability),
        valueMultiplier: parseFloat(row.value_multiplier),
        colorHex: row.color_hex
      } : null
    } as ItemWithRarity
  }
} 