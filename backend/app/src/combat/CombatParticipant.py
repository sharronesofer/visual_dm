from typing import Any, Dict


class CombatParticipant {
  id: str
  position: Dict[str, Any]
  private stats: Dict[str, Any]
  private effects: Map<string, { magnitude: float; duration: float }>
  constructor(id: str, position: Dict[str, Any], stats: Dict[str, Any]) {
    this.id = id
    this.position = position
    this.stats = stats
    this.effects = new Map()
  }
  calculateDamage(): float {
    let totalDamage = this.stats.damage
    for (const [_, effect] of this.effects) {
      if (effect.magnitude > 0) {
        totalDamage += effect.magnitude
      }
    }
    return totalDamage
  }
  applyEffect(type: str, magnitude: float, duration: float = 1): void {
    this.effects.set(type, { magnitude, duration })
  }
  applyBuff(type: str, magnitude: float): void {
    this.applyEffect(type, magnitude, 3) 
  }
  processTurn(): void {
    for (const [type, effect] of this.effects) {
      effect.duration--
      if (effect.duration <= 0) {
        this.effects.delete(type)
      }
    }
  }
  getActiveEffects(): Array<{ type: str; magnitude: float; duration: float }> {
    return Array.from(this.effects.entries()).map(([type, effect]) => ({
      type,
      magnitude: effect.magnitude,
      duration: effect.duration
    }))
  }
} 