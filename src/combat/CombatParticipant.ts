export class CombatParticipant {
  id: string;
  position: { q: number; r: number };
  private stats: {
    health: number;
    damage: number;
    defense: number;
  };
  private effects: Map<string, { magnitude: number; duration: number }>;

  constructor(id: string, position: { q: number; r: number }, stats: { health: number; damage: number; defense: number }) {
    this.id = id;
    this.position = position;
    this.stats = stats;
    this.effects = new Map();
  }

  calculateDamage(): number {
    let totalDamage = this.stats.damage;
    for (const [_, effect] of this.effects) {
      if (effect.magnitude > 0) {
        totalDamage += effect.magnitude;
      }
    }
    return totalDamage;
  }

  applyEffect(type: string, magnitude: number, duration: number = 1): void {
    this.effects.set(type, { magnitude, duration });
  }

  applyBuff(type: string, magnitude: number): void {
    this.applyEffect(type, magnitude, 3); // Buffs last 3 turns by default
  }

  processTurn(): void {
    // Process and remove expired effects
    for (const [type, effect] of this.effects) {
      effect.duration--;
      if (effect.duration <= 0) {
        this.effects.delete(type);
      }
    }
  }

  getActiveEffects(): Array<{ type: string; magnitude: number; duration: number }> {
    return Array.from(this.effects.entries()).map(([type, effect]) => ({
      type,
      magnitude: effect.magnitude,
      duration: effect.duration
    }));
  }
} 