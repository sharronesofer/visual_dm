import { WeatherEffect, WeatherState } from '../types/weather';
import { CombatState } from '../types/combat';
import { GameCharacterState } from '../types/character';
import { MovementState } from '../types/movement';

export interface WeatherEffectSystemState {
  activeEffects: Map<string, WeatherEffect[]>;
  globalEffects: WeatherEffect[];
}

export class WeatherEffectSystem {
  private state: WeatherEffectSystemState = {
    activeEffects: new Map(),
    globalEffects: []
  };

  // Set weather effects for a region
  public setRegionEffects(regionId: string, weather: WeatherState): void {
    this.state.activeEffects.set(regionId, weather.effects);
  }

  // Clear weather effects for a region
  public clearRegionEffects(regionId: string): void {
    this.state.activeEffects.delete(regionId);
  }

  // Get all effects for a region (including global effects)
  private getEffectsForRegion(regionId: string): WeatherEffect[] {
    const regionEffects = this.state.activeEffects.get(regionId) || [];
    return [...regionEffects, ...this.state.globalEffects];
  }

  // Apply weather effects to combat calculations
  public modifyCombatStats(
    regionId: string,
    combatState: CombatState
  ): CombatState {
    const effects = this.getEffectsForRegion(regionId);
    let modified = { ...combatState };

    effects
      .filter(effect => effect.type === 'combat')
      .forEach(effect => {
        // Apply combat-specific modifiers
        modified.accuracy *= (1 + effect.value);
        modified.damage *= (1 + effect.value);
        modified.defense *= (1 + effect.value);
        modified.criticalChance *= (1 + effect.value);
        
        // Apply resistance modifiers if they exist
        if (modified.resistances && effect.elementalModifiers) {
          Object.entries(effect.elementalModifiers).forEach(([element, value]) => {
            if (modified.resistances[element]) {
              modified.resistances[element] *= (1 + value);
            }
          });
        }
      });

    return modified;
  }

  // Apply weather effects to movement calculations
  public modifyMovementStats(
    regionId: string,
    movementState: MovementState
  ): MovementState {
    const effects = this.getEffectsForRegion(regionId);
    let modified = { ...movementState };

    effects
      .filter(effect => effect.type === 'movement')
      .forEach(effect => {
        modified.speed *= (1 + effect.value);
        modified.staminaCost *= (1 + effect.value);
        
        if (modified.jumpHeight) {
          modified.jumpHeight *= (1 + effect.value);
        }
        if (modified.climbSpeed) {
          modified.climbSpeed *= (1 + effect.value);
        }
        if (modified.swimSpeed) {
          modified.swimSpeed *= (1 + effect.value);
        }
        if (modified.terrainPenalty) {
          modified.terrainPenalty *= (1 + effect.value);
        }
      });

    return modified;
  }

  // Apply weather effects to character stats
  public modifyCharacterStats(
    regionId: string,
    characterState: GameCharacterState
  ): GameCharacterState {
    const effects = this.getEffectsForRegion(regionId);
    let modified = { ...characterState };

    effects
      .filter(effect => effect.type === 'status')
      .forEach(effect => {
        // Apply weather-based status effects
        if (effect.statusEffect && !modified.statusEffects.includes(effect.statusEffect)) {
          modified.statusEffects.push(effect.statusEffect);
        }

        // Modify environmental values if they exist
        if (modified.temperature !== undefined && effect.temperatureModifier) {
          modified.temperature += effect.temperatureModifier;
        }
        if (modified.wetness !== undefined && effect.wetnessModifier) {
          modified.wetness += effect.wetnessModifier;
        }
        if (modified.visibility !== undefined && effect.visibilityModifier) {
          modified.visibility *= (1 + effect.visibilityModifier);
        }
      });

    return modified;
  }

  // Calculate visibility range based on weather effects
  public calculateVisibilityRange(regionId: string, baseRange: number): number {
    const effects = this.getEffectsForRegion(regionId);
    let modifiedRange = baseRange;

    effects
      .filter(effect => effect.type === 'visibility')
      .forEach(effect => {
        modifiedRange *= (1 + effect.value);
      });

    return Math.max(1, modifiedRange); // Ensure visibility never goes below 1
  }

  // Add a global weather effect
  public addGlobalEffect(effect: WeatherEffect): void {
    this.state.globalEffects.push(effect);
  }

  // Remove a global weather effect
  public removeGlobalEffect(effectType: WeatherEffect['type']): void {
    this.state.globalEffects = this.state.globalEffects.filter(
      effect => effect.type !== effectType
    );
  }
} 