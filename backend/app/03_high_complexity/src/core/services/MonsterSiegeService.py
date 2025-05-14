from typing import Any, Dict, List



/**
 * Service for generating and recording monster siege attacks on POIs.
 * Implements attack probability, monster selection, and attack record creation.
 */
class MonsterSiegeService {
  private static instance: \'MonsterSiegeService\'
  private attacks: List[MonsterAttack] = []
  private directions: List[MonsterAttackDirection] = [
    'north',
    'northeast',
    'southeast',
    'south',
    'southwest',
    'northwest',
  ]
  private constructor() {}
  /**
   * Singleton accessor
   */
  public static getInstance(): \'MonsterSiegeService\' {
    if (!MonsterSiegeService.instance) {
      MonsterSiegeService.instance = new MonsterSiegeService()
    }
    return MonsterSiegeService.instance
  }
  /**
   * Generate monster attacks for eligible POIs.
   * @param pois List of POIs to consider for attacks
   * @param options Optional config for attack frequency, randomness, etc.
   */
  public triggerAttacks(pois: List[POI], options?: { seed?: float; attackChance?: float }): MonsterAttack[] {
    const attacks: List[MonsterAttack] = []
    const rng = options?.seed !== undefined ? this.seededRandom(options.seed) : Math.random
    const attackChance = options?.attackChance ?? 0.2 
    for (const poi of pois) {
      if (!this.isEligiblePOI(poi)) continue
      const vulnerability = rng()
      if (vulnerability < attackChance) {
        const monsterTypes = this.selectMonsterTypes(poi, rng)
        const strength = Math.floor(rng() * 10) + 1
        const direction = this.directions[Math.floor(rng() * this.directions.length)]
        const attack: MonsterAttack = {
          id: uuidv4(),
          poiId: poi.id,
          direction,
          strength,
          monsterTypes,
          timestamp: new Date(),
          resolved: false,
        }
        this.attacks.push(attack)
        attacks.push(attack)
      }
    }
    return attacks
  }
  /**
   * Determine if a POI is eligible for a monster attack.
   * @param poi The POI to check
   */
  private isEligiblePOI(poi: POI): bool {
    return poi.state === 'active'
  }
  /**
   * Select monster types for an attack based on POI region/type.
   * Placeholder: returns a static array. Integrate with monster selection logic.
   */
  private selectMonsterTypes(poi: POI, rng: () => number): string[] {
    return ['goblin']
  }
  /**
   * Seeded random number generator for testability.
   */
  private seededRandom(seed: float): () => number {
    let s = seed % 2147483647
    return () => {
      s = (s * 16807) % 2147483647
      return (s - 1) / 2147483646
    }
  }
  /**
   * Get all recorded attacks (for testing or review)
   */
  public getAttacks(): MonsterAttack[] {
    return [...this.attacks]
  }
  /**
   * Simulate combat for a monster attack and resolve the outcome.
   * @param attackId The ID of the MonsterAttack to resolve
   * @returns Promise with outcome and combat log
   */
  public async resolveAttack(attackId: str): Promise<{ outcome: MonsterAttackOutcome; combatLog: List[string] }> {
    const attack = this.attacks.find(a => a.id === attackId)
    if (!attack) throw new Error('Attack not found')
    if (attack.resolved) throw new Error('Attack already resolved')
    const poi = this.mockGetPOI(attack.poiId)
    const defenderStrength = this.mockDefenderStrength(attack.poiId)
    const monsterStrength = attack.strength
    const combatLog: List[string] = []
    const randomFactor = 0.85 + Math.random() * 0.3 
    const adjustedDefender = defenderStrength * randomFactor
    const ratio = adjustedDefender / monsterStrength
    let outcome: MonsterAttackOutcome
    if (ratio >= 0.9) {
      outcome = 'defended'
      combatLog.push('Defenders held off the monsters.')
    } else if (ratio >= 0.7) {
      outcome = 'close_defeat'
      combatLog.push('Defenders fought bravely but suffered a close defeat.')
    } else {
      outcome = 'decisive_defeat'
      combatLog.push('Defenders were overwhelmed in a decisive defeat.')
    }
    combatLog.push(
      `Defender strength: ${defenderStrength.toFixed(2)}, Monster strength: ${monsterStrength.toFixed(2)}, Adjusted defender: ${adjustedDefender.toFixed(2)}, Ratio: ${ratio.toFixed(2)}`
    )
    this.updatePoiFactionStrength(poi, outcome)
    const damage = this.calculateDamage(outcome)
    this.trackPoiDamage(poi, damage)
    if (outcome === 'decisive_defeat') {
      this.convertPoiType(poi, 'monster_den')
    }
    this.recordStateChange(poi, outcome)
    this.notifyStateChange(poi, 'battle_outcome')
    attack.outcome = outcome
    attack.resolved = true
    return { outcome, combatLog }
  }
  /**
   * Update POI faction strength based on battle outcome.
   */
  private updatePoiFactionStrength(poi: POI, outcome: MonsterAttackOutcome): void {
    const meta = { ...(poi.metadata || {}) }
    let strength = meta.factionStrength ?? 100
    if (outcome === 'defended') strength = Math.max(0, strength - 5)
    else if (outcome === 'close_defeat') strength = Math.max(0, strength - 20)
    else if (outcome === 'decisive_defeat') strength = Math.max(0, strength - 50)
    meta.factionStrength = strength
    poi.setMetadata(meta)
  }
  /**
   * Track damage to POI structures.
   */
  private trackPoiDamage(poi: POI, damageAmount: float): void {
    const meta = { ...(poi.metadata || {}) }
    let damage = meta.damageLevel ?? 0
    damage = Math.min(100, damage + damageAmount)
    meta.damageLevel = damage
    poi.setMetadata(meta)
  }
  /**
   * Convert POI type after decisive defeat.
   */
  private convertPoiType(poi: POI, newType: str): void {
    const prevType = poi.type
    poi.setType(newType)
    this.recordStateChange(poi, `type_change: ${prevType} -> ${newType}`)
  }
  /**
   * Record historical state changes for a POI.
   */
  private recordStateChange(poi: POI, cause: str): void {
    const meta = { ...(poi.metadata || {}) }
    if (!meta.stateHistory) meta.stateHistory = []
    meta.stateHistory.push({ timestamp: new Date(), state: Dict[str, Any], cause })
    poi.setMetadata(meta)
  }
  /**
   * Simulate POI recovery over time (to be called on world tick).
   */
  public processPoiRecovery(poi: POI): void {
    const meta = { ...(poi.metadata || {}) }
    let damage = meta.damageLevel ?? 0
    let strength = meta.factionStrength ?? 0
    const recoveryRate = meta.recoveryRate ?? 5
    damage = Math.max(0, damage - recoveryRate)
    strength = Math.min(100, strength + recoveryRate)
    meta.damageLevel = damage
    meta.factionStrength = strength
    if (poi.type === 'monster_den' && strength > 60 && damage < 20) {
      this.convertPoiType(poi, 'village')
    }
    poi.setMetadata(meta)
  }
  /**
   * Notify players of significant POI state changes (stub).
   */
  private notifyStateChange(poi: POI, changeType: str): void {
    console.log(`[NOTIFY] POI ${poi.name} (${poi.id}) state change: ${changeType}`)
  }
  /**
   * Calculate damage based on outcome.
   */
  private calculateDamage(outcome: MonsterAttackOutcome): float {
    if (outcome === 'defended') return 5
    if (outcome === 'close_defeat') return 20
    return 50
  }
  /**
   * Mock: Retrieve POI by ID (replace with real DB/service call).
   */
  private mockGetPOI(poiId: str): POI {
    return new POI(poiId, `POI-${poiId}`, [0, 0], 'village', 'region', 'active', {})
  }
  /**
   * Mock defender strength calculation for a POI.
   * Replace with real logic as needed.
   */
  private mockDefenderStrength(poiId: str): float {
    let hash = 0
    for (let i = 0; i < poiId.length; i++) {
      hash = ((hash << 5) - hash) + poiId.charCodeAt(i)
      hash |= 0
    }
    return 8 + (Math.abs(hash) % 8) 
  }
} 