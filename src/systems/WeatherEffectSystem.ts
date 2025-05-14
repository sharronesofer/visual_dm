import { WeatherEffect, WeatherState } from '../core/interfaces/types/weather';
import { CombatState } from '../core/interfaces/types/combat';
import { GameCharacterState } from '../core/interfaces/types/character';
import { MovementState } from '../core/interfaces/types/movement';
import { ResourceMonitor } from '../core/performance/ResourceMonitor';

export interface WeatherEffectSystemState {
  activeEffects: Map<string, WeatherEffect[]>;
  globalEffects: WeatherEffect[];
}

interface WeatherEffectPool {
  [effectType: string]: WeatherEffect[];
}

interface WeatherEffectSystemConfig {
  maxActiveEffects: number;
  poolSize: number;
  cullingDistance: number;
  lodProfiles: Record<string, { maxParticles: number; minDistance: number; }>;
  fallbackThresholds: {
    memory: number; // percent
    cpu: number; // percent
  };
}

// Default config for resource management
const DEFAULT_RESOURCE_CONFIG: WeatherEffectSystemConfig = {
  maxActiveEffects: 100,
  poolSize: 200,
  cullingDistance: 100,
  lodProfiles: {
    high: { maxParticles: 1000, minDistance: 0 },
    medium: { maxParticles: 500, minDistance: 50 },
    low: { maxParticles: 100, minDistance: 100 }
  },
  fallbackThresholds: {
    memory: 85, // percent
    cpu: 90 // percent
  }
};

export class WeatherEffectSystem {
  private state: WeatherEffectSystemState = {
    activeEffects: new Map(),
    globalEffects: []
  };
  private resourceConfig: WeatherEffectSystemConfig = DEFAULT_RESOURCE_CONFIG;
  private effectPool: WeatherEffectPool = {};
  private resourceMonitor: ResourceMonitor = ResourceMonitor.getInstance();
  private currentLOD: 'high' | 'medium' | 'low' = 'high';
  private fallbackActive: boolean = false;

  constructor(config: Partial<WeatherEffectSystemConfig> = {}) {
    this.resourceConfig = { ...DEFAULT_RESOURCE_CONFIG, ...config };
    this.resourceMonitor.startMonitoring();
  }

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
        // Only apply to resistances if present
        if (modified.resistances) {
          Object.keys(modified.resistances).forEach(element => {
            if (typeof modified.resistances![element] === 'number') {
              modified.resistances![element]! *= (1 + effect.value);
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
        if (typeof modified.jumpHeight === 'number') {
          modified.jumpHeight *= (1 + effect.value);
        }
        if (typeof modified.climbSpeed === 'number') {
          modified.climbSpeed *= (1 + effect.value);
        }
        if (typeof modified.swimSpeed === 'number') {
          modified.swimSpeed *= (1 + effect.value);
        }
        if (typeof modified.terrainPenalty === 'number') {
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
        // No statusEffect property, so just a placeholder for extensibility
        // If statusEffects array exists, push a generic weather status effect
        if (Array.isArray(modified.statusEffects)) {
          if (!modified.statusEffects.includes('weather-effect')) {
            modified.statusEffects.push('weather-effect');
          }
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

  // --- DYNAMIC SCALING ---
  public updateLOD(regionDistance: number): void {
    if (regionDistance < this.resourceConfig.lodProfiles.medium.minDistance) {
      this.currentLOD = 'high';
    } else if (regionDistance < this.resourceConfig.lodProfiles.low.minDistance) {
      this.currentLOD = 'medium';
    } else {
      this.currentLOD = 'low';
    }
    // Optionally, trigger re-scaling of active effects
  }

  // --- OBJECT POOLING ---
  private getPooledEffect(effectType: string): WeatherEffect | null {
    if (!this.effectPool[effectType]) {
      this.effectPool[effectType] = [];
    }
    return this.effectPool[effectType].pop() || null;
  }

  private releaseEffectToPool(effect: WeatherEffect): void {
    if (!this.effectPool[effect.type]) {
      this.effectPool[effect.type] = [];
    }
    if (this.effectPool[effect.type].length < this.resourceConfig.poolSize) {
      this.effectPool[effect.type].push(effect);
    }
  }

  // --- CULLING ---
  public cullEffects(regionId: string, cameraDistance: number): void {
    if (cameraDistance > this.resourceConfig.cullingDistance) {
      this.clearRegionEffects(regionId);
    }
  }

  // --- PERFORMANCE MONITORING & FALLBACK ---
  public monitorAndFallback(): void {
    // Simulate getting metrics (in real code, use async/await and callbacks)
    this.resourceMonitor.enableMonitoring(true);
    // For demonstration, use static values; in production, poll ResourceMonitor
    const metrics = {
      memoryUsage: 80, // percent
      cpuUsage: 70 // percent
    };
    if (
      metrics.memoryUsage > this.resourceConfig.fallbackThresholds.memory ||
      metrics.cpuUsage > this.resourceConfig.fallbackThresholds.cpu
    ) {
      this.activateFallbackMode();
    } else {
      this.deactivateFallbackMode();
    }
  }

  private activateFallbackMode(): void {
    if (!this.fallbackActive) {
      this.fallbackActive = true;
      this.currentLOD = 'low';
      // Optionally, clear or reduce active effects
      this.state.activeEffects.clear();
      // Log fallback activation
      console.warn('[WeatherEffectSystem] Fallback mode activated: resource limits exceeded.');
    }
  }

  private deactivateFallbackMode(): void {
    if (this.fallbackActive) {
      this.fallbackActive = false;
      this.currentLOD = 'high';
      // Log fallback deactivation
      console.info('[WeatherEffectSystem] Fallback mode deactivated: resources recovered.');
    }
  }

  // --- LOGGING & MONITORING ---
  public logResourceStatus(): void {
    // In production, fetch real metrics from ResourceMonitor
    console.log('[WeatherEffectSystem] Resource status:', {
      activeEffects: this.state.activeEffects.size,
      globalEffects: this.state.globalEffects.length,
      currentLOD: this.currentLOD,
      fallbackActive: this.fallbackActive
    });
  }
} 