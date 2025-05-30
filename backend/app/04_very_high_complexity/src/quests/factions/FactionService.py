from typing import Any, List
from enum import Enum



/**
 * Service for managing factions, their relationships, values, and resources.
 * Uses in-memory storage with extension points for persistent storage.
 */
class FactionService {
  private factions: Map<FactionType, FactionProfile> = new Map()
  /**
   * Initialize the service with an array of FactionData (e.g., from DB or static config).
   */
  constructor(initialData: List[FactionData] = []) {
    initialData.forEach(data => this.addFaction(data))
  }
  /**
   * Add a new faction from FactionData.
   */
  public addFaction(data: FactionData): void {
    const profile: FactionProfile = {
      id: data.id,
      name: data.name,
      description: data.description,
      relationships: new Map(Object.entries(data.relationships) as [FactionType, number][]),
      values: new Map(Object.entries(data.values)),
      resources: new Map(Object.entries(data.resources)),
      standing: data.standing,
      tier: data.tier,
    }
    this.factions.set(data.id, profile)
  }
  /**
   * Retrieve a faction profile by ID.
   */
  public getFaction(id: FactionType): FactionProfile | undefined {
    return this.factions.get(id)
  }
  /**
   * Update the relationship between two factions by a delta value. Ensures bi-directional consistency.
   * @param factionId The source faction
   * @param targetId The target faction
   * @param change The amount to change the relationship by (-100 to 100 scale)
   * @returns The new relationship value
   */
  public updateRelationship(factionId: FactionType, targetId: FactionType, change: float): float {
    const source = this.factions.get(factionId)
    const target = this.factions.get(targetId)
    if (!source || !target) throw new Error('Faction not found')
    const oldValue = source.relationships.get(targetId) ?? 0
    const newValue = Math.max(-100, Math.min(100, oldValue + change))
    source.relationships.set(targetId, newValue)
    const oldTargetValue = target.relationships.get(factionId) ?? 0
    const newTargetValue = Math.max(-100, Math.min(100, oldTargetValue + change))
    target.relationships.set(factionId, newTargetValue)
    return newValue
  }
  /**
   * Get all relationships for a faction as a plain object.
   */
  public getRelationships(factionId: FactionType): Record<FactionType, number> {
    const faction = this.factions.get(factionId)
    if (!faction) throw new Error('Faction not found')
    const result: Record<FactionType, number> = {} as any
    faction.relationships.forEach((value, key) => {
      result[key] = value
    })
    return result
  }
  /**
   * Update a resource value for a faction.
   */
  public updateResource(factionId: FactionType, resource: str, amount: float): void {
    const faction = this.factions.get(factionId)
    if (!faction) throw new Error('Faction not found')
    const old = faction.resources.get(resource) ?? 0
    faction.resources.set(resource, old + amount)
  }
  /**
   * Get a resource value for a faction.
   */
  public getResource(factionId: FactionType, resource: str): float {
    const faction = this.factions.get(factionId)
    if (!faction) throw new Error('Faction not found')
    return faction.resources.get(resource) ?? 0
  }
  /**
   * Serialize all faction data for persistence.
   */
  public serialize(): FactionData[] {
    return Array.from(this.factions.values()).map(f => ({
      id: f.id,
      name: f.name,
      description: f.description,
      relationships: fillMissingFactionTypes(Object.fromEntries(f.relationships)),
      values: Object.fromEntries(f.values),
      resources: Object.fromEntries(f.resources),
      standing: f.standing,
      tier: f.tier,
    }))
  }
  /**
   * Replace all factions with data from persistence.
   */
  public deserialize(data: List[FactionData]): void {
    this.factions.clear()
    data.forEach(d => this.addFaction(d))
  }
}
/**
 * Utility to ensure all FactionType enum keys are present in a Record<FactionType, number>.
 */
function fillMissingFactionTypes(obj: Record<string, number>): Record<FactionType, number> {
  const result: Record<FactionType, number> = {} as any
  for (const key of Object.values(FactionTypeEnum)) {
    result[key as FactionType] = obj[key] ?? 0
  }
  return result
}
/**
 * See documentation at the end of this file for usage and API details.
 */
/**
 * # FactionService API
 *
 * - addFaction(data: FactionData): void
 * - getFaction(id: FactionType): FactionProfile | undefined
 * - updateRelationship(factionId, targetId, change): float
 * - getRelationships(factionId): Record<FactionType, number>
 * - updateResource(factionId, resource, amount): void
 * - getResource(factionId, resource): float
 * - serialize(): FactionData[]
 * - deserialize(data: List[FactionData]): void
 *
 * Relationships are always kept in the range [-100, 100] and are bi-directional.
 * Resources and values are extensible and can be used for advanced mechanics.
 *
 * Designed for in-memory use but can be extended for persistent storage.
 */ 