from typing import Any, Dict, List



class WeatherEffectSystemState:
    activeEffects: Dict[str, WeatherEffect[]>
    globalEffects: List[WeatherEffect]
class WeatherEffectSystem {
  private state: \'WeatherEffectSystemState\' = {
    activeEffects: new Map(),
    globalEffects: []
  }
  public setRegionEffects(regionId: str, weather: WeatherState): void {
    this.state.activeEffects.set(regionId, weather.effects)
  }
  public clearRegionEffects(regionId: str): void {
    this.state.activeEffects.delete(regionId)
  }
  private getEffectsForRegion(regionId: str): WeatherEffect[] {
    const regionEffects = this.state.activeEffects.get(regionId) || []
    return [...regionEffects, ...this.state.globalEffects]
  }
  public modifyCombatStats(
    regionId: str,
    combatState: CombatState
  ): CombatState {
    const effects = this.getEffectsForRegion(regionId)
    let modified = { ...combatState }
    effects
      .filter(effect => effect.type === 'combat')
      .forEach(effect => {
        modified.accuracy *= (1 + effect.value)
        modified.damage *= (1 + effect.value)
        modified.defense *= (1 + effect.value)
        modified.criticalChance *= (1 + effect.value)
        if (modified.resistances && effect.elementalModifiers) {
          Object.entries(effect.elementalModifiers).forEach(([element, value]) => {
            if (modified.resistances[element]) {
              modified.resistances[element] *= (1 + value)
            }
          })
        }
      })
    return modified
  }
  public modifyMovementStats(
    regionId: str,
    movementState: MovementState
  ): MovementState {
    const effects = this.getEffectsForRegion(regionId)
    let modified = { ...movementState }
    effects
      .filter(effect => effect.type === 'movement')
      .forEach(effect => {
        modified.speed *= (1 + effect.value)
        modified.staminaCost *= (1 + effect.value)
        if (modified.jumpHeight) {
          modified.jumpHeight *= (1 + effect.value)
        }
        if (modified.climbSpeed) {
          modified.climbSpeed *= (1 + effect.value)
        }
        if (modified.swimSpeed) {
          modified.swimSpeed *= (1 + effect.value)
        }
        if (modified.terrainPenalty) {
          modified.terrainPenalty *= (1 + effect.value)
        }
      })
    return modified
  }
  public modifyCharacterStats(
    regionId: str,
    characterState: GameCharacterState
  ): GameCharacterState {
    const effects = this.getEffectsForRegion(regionId)
    let modified = { ...characterState }
    effects
      .filter(effect => effect.type === 'status')
      .forEach(effect => {
        if (effect.statusEffect && !modified.statusEffects.includes(effect.statusEffect)) {
          modified.statusEffects.push(effect.statusEffect)
        }
        if (modified.temperature !== undefined && effect.temperatureModifier) {
          modified.temperature += effect.temperatureModifier
        }
        if (modified.wetness !== undefined && effect.wetnessModifier) {
          modified.wetness += effect.wetnessModifier
        }
        if (modified.visibility !== undefined && effect.visibilityModifier) {
          modified.visibility *= (1 + effect.visibilityModifier)
        }
      })
    return modified
  }
  public calculateVisibilityRange(regionId: str, baseRange: float): float {
    const effects = this.getEffectsForRegion(regionId)
    let modifiedRange = baseRange
    effects
      .filter(effect => effect.type === 'visibility')
      .forEach(effect => {
        modifiedRange *= (1 + effect.value)
      })
    return Math.max(1, modifiedRange) 
  }
  public addGlobalEffect(effect: WeatherEffect): void {
    this.state.globalEffects.push(effect)
  }
  public removeGlobalEffect(effectType: WeatherEffect['type']): void {
    this.state.globalEffects = this.state.globalEffects.filter(
      effect => effect.type !== effectType
    )
  }
} 