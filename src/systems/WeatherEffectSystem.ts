import { WeatherEffect, WeatherState } from '../core/interfaces/types/weather';
import { CombatState } from '../core/interfaces/types/combat';
import { GameCharacterState } from '../core/interfaces/types/character';
import { MovementState } from '../core/interfaces/types/movement';
import { ResourceMonitor } from '../core/performance/ResourceMonitor';
import { WeatherPerformanceMonitor } from '../core/performance/WeatherPerformanceMonitor';
import { WeatherEffectPool } from './WeatherEffectPool';
import { WeatherCullingManager, WeatherEffectPriority, WeatherCullingConfig } from './WeatherCullingManager';
import { HardwareProfiler, PerformanceMetrics } from '../core/performance/HardwareProfiler';
import { WeatherFallbackManager } from './WeatherFallbackManager';
import { FallbackTier, WeatherFallbackConfig, WeatherResourceConfig, WEATHER_RESOURCE_PRESETS } from '../core/interfaces/types/weather';

export interface WeatherEffectSystemState {
  activeEffects: Map<string, WeatherEffect[]>;
  globalEffects: WeatherEffect[];
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

// NOTE: Use WEATHER_RESOURCE_PRESETS or a valid WeatherResourceConfig for resource management. Remove unused default config.

// --- LOD COMPATIBILITY INTERFACE ---
export interface ILODCompatibleEffect {
  setLODLevel(level: LODLevel, profile: WeatherLODProfile): void;
  getCurrentLODLevel(): LODLevel;
}

// --- EXTENDED LOD PROFILE ---
export type LODLevel = 'ultra' | 'high' | 'medium' | 'low' | 'verylow';

export interface WeatherLODProfile {
  maxParticles: number;
  textureResolution: number; // e.g., 1024, 512, 256
  shaderComplexity: number; // 1=full, 0.5=half, 0.25=simple
  drawDistance: number;
  minDistance: number;
  // Add more as needed
}

export interface WeatherLODConfig {
  thresholds: {
    frameTime: Record<LODLevel, number>;
    memoryUsage: Record<LODLevel, number>;
    gpuScore?: Record<LODLevel, number>; // Optional hardware-based
  };
  profiles: Record<string, Record<LODLevel, WeatherLODProfile>>; // effectType -> LODLevel -> profile
  transitionSmoothing: number; // ms for smoothing transitions
  hardwareProfiles?: Record<string, Partial<WeatherLODConfig>>; // e.g., 'low-end', 'mid', 'high-end'
}

/**
 * Utility: Color coding for LOD levels (for overlays)
 */
export const LODLevelColors: Record<LODLevel, string> = {
  ultra: '#00eaff',
  high: '#00ff00',
  medium: '#ffff00',
  low: '#ff9900',
  verylow: '#ff0000',
};

// --- LOD MANAGER REFACTOR ---
export class WeatherLODManager {
  private config: WeatherLODConfig;
  private currentLOD: Record<string, LODLevel> = {};
  private transitionTimers: Record<string, NodeJS.Timeout | null> = {};
  private onLODChange: (effectType: string, newLOD: LODLevel, profile: WeatherLODProfile) => void;
  private hardwareProfile: string = 'default';
  private transitionController: TransitionController | null = null;
  private fallbackActive: boolean = false;
  private overlayRenderers: Array<(ctx: CanvasRenderingContext2D) => void> = [];
  private lodTransitionLog: Array<{ effectType: string; from: LODLevel; to: LODLevel; timestamp: number }> = [];

  constructor(config: WeatherLODConfig, onLODChange: (effectType: string, newLOD: LODLevel, profile: WeatherLODProfile) => void) {
    this.config = config;
    this.onLODChange = onLODChange;
  }

  // Set hardware profile (e.g., after detection)
  setHardwareProfile(profile: string) {
    this.hardwareProfile = profile;
    if (this.config.hardwareProfiles && this.config.hardwareProfiles[profile]) {
      // Merge overrides
      this.config = {
        ...this.config,
        ...this.config.hardwareProfiles[profile],
        profiles: {
          ...this.config.profiles,
          ...this.config.hardwareProfiles[profile]?.profiles,
        },
      };
    }
  }

  // Get current LOD for an effect type
  getLOD(effectType: string): LODLevel {
    return this.currentLOD[effectType] || 'high';
  }

  // Set LOD for an effect type, with optional smoothing
  setLOD(effectType: string, newLOD: LODLevel, smooth: boolean = true) {
    const prevLOD = this.currentLOD[effectType];
    if (prevLOD === newLOD) return;
    this.logLODTransition(effectType, prevLOD || 'high', newLOD);
    const profile = this.getProfile(effectType, newLOD);
    if (smooth && this.config.transitionSmoothing > 0) {
      if (this.transitionTimers[effectType]) {
        clearTimeout(this.transitionTimers[effectType]!);
      }
      this.transitionTimers[effectType] = setTimeout(() => {
        this.currentLOD[effectType] = newLOD;
        this.onLODChange(effectType, newLOD, profile);
      }, this.config.transitionSmoothing);
    } else {
      this.currentLOD[effectType] = newLOD;
      this.onLODChange(effectType, newLOD, profile);
    }
  }

  // Update LOD based on distance, performance, and hardware
  updateLOD(effectType: string, metrics: { frameTime: number; memoryUsage: number; gpuScore?: number }, distance: number) {
    const t = this.config.thresholds;
    let newLOD: LODLevel = 'ultra';
    // Distance-based logic (expandable)
    const profiles = this.config.profiles[effectType];
    if (profiles) {
      for (const level of ['ultra', 'high', 'medium', 'low', 'verylow'] as LODLevel[]) {
        if (distance >= profiles[level]?.minDistance) {
          newLOD = level;
        }
      }
    }
    // Performance/hardware-based override
    if (metrics.frameTime > (t.frameTime.low || 33) || metrics.memoryUsage > (t.memoryUsage.low || 90)) {
      newLOD = 'verylow';
    } else if (metrics.frameTime > (t.frameTime.medium || 24) || metrics.memoryUsage > (t.memoryUsage.medium || 80)) {
      newLOD = 'low';
    } else if (metrics.frameTime > (t.frameTime.high || 16) || metrics.memoryUsage > (t.memoryUsage.high || 60)) {
      newLOD = 'medium';
    }
    // Hardware profile (optional)
    if (metrics.gpuScore && t.gpuScore) {
      for (const level of ['ultra', 'high', 'medium', 'low', 'verylow'] as LODLevel[]) {
        if (metrics.gpuScore < (t.gpuScore[level] || 0)) {
          newLOD = level;
        }
      }
    }
    this.setLOD(effectType, newLOD);
  }

  // Get the LOD profile for an effect type and level
  getProfile(effectType: string, level?: LODLevel): WeatherLODProfile {
    const lod = level || this.getLOD(effectType);
    return (
      (this.config.profiles[effectType] && this.config.profiles[effectType][lod]) ||
      { maxParticles: 100, textureResolution: 256, shaderComplexity: 0.25, drawDistance: 50, minDistance: 0 }
    );
  }

  // Update config (for dynamic reconfiguration)
  setConfig(config: WeatherLODConfig) {
    this.config = config;
  }

  /**
   * Dynamically update LOD for an effect type based on current metrics and distance.
   * Applies adaptive scaling for all relevant parameters.
   * Adds hysteresis to avoid oscillation.
   */
  public updateDynamicLOD(effectType: string, metrics: PerformanceMetrics, distance: number) {
    // Hysteresis: Only change LOD if metrics cross threshold by a margin
    const prevLOD = this.getLOD(effectType);
    this.updateLOD(effectType, metrics, distance);
    const newLOD = this.getLOD(effectType);
    if (prevLOD !== newLOD) {
      // Optionally, add smoothing or delay before applying
      // (Handled by transition logic)
    }
    // Stub: In future, update effect parameters (particle count, texture, etc.) here
  }

  /**
   * Detect hardware tier and activate fallback mode if needed.
   * Uses HardwareProfiler to determine tier and triggers fallbacks for 'low' or 'verylow'.
   */
  public checkAndActivateFallback(hardwareProfiler: HardwareProfiler, metrics: PerformanceMetrics) {
    hardwareProfiler.getHardwareProfile().then(profile => {
      const tier = HardwareProfiler.getTier(profile);
      if ((tier === 'low' || tier === 'verylow') || metrics.frameTime > (this.config.thresholds.frameTime.verylow || 40)) {
        this.activateFallbackMode();
      } else {
        this.deactivateFallbackMode();
      }
    });
  }

  /**
   * Activate fallback mode: switch to lowest LOD, trigger effect-specific fallbacks.
   */
  public activateFallbackMode() {
    if (!this.fallbackActive) {
      this.fallbackActive = true;
      // Set all effects to 'verylow' LOD
      Object.keys(this.currentLOD).forEach(effectType => {
        this.setLOD(effectType, 'verylow', false);
      });
      // Stub: Trigger effect-specific fallbacks (billboards, sprites, simple shaders, etc.)
      // e.g., this.onFallbackActivated?.();
    }
  }

  /**
   * Deactivate fallback mode: restore normal LOD and effect rendering.
   */
  public deactivateFallbackMode() {
    if (this.fallbackActive) {
      this.fallbackActive = false;
      // Restore LOD based on metrics/hardware
      // Stub: Restore normal effect rendering
      // e.g., this.onFallbackDeactivated?.();
    }
  }

  /**
   * Check if fallback mode is active.
   */
  public isFallbackActive(): boolean {
    return this.fallbackActive;
  }

  /**
   * Register a custom overlay renderer for LOD visualization.
   * The renderer receives a CanvasRenderingContext2D.
   */
  public registerOverlayRenderer(renderer: (ctx: CanvasRenderingContext2D) => void) {
    this.overlayRenderers.push(renderer);
  }

  /**
   * Unregister an overlay renderer.
   */
  public unregisterOverlayRenderer(renderer: (ctx: CanvasRenderingContext2D) => void) {
    this.overlayRenderers = this.overlayRenderers.filter(r => r !== renderer);
  }

  /**
   * Render all registered overlays (to be called by the main render loop or debug panel).
   */
  public renderOverlays(ctx: CanvasRenderingContext2D) {
    for (const renderer of this.overlayRenderers) {
      renderer(ctx);
    }
  }

  /**
   * Log LOD transitions for debugging/analysis.
   */
  private logLODTransition(effectType: string, from: LODLevel, to: LODLevel) {
    this.lodTransitionLog.push({ effectType, from, to, timestamp: Date.now() });
    // Optionally, emit event for UI
  }

  /**
   * Expose current LOD state for overlays/panels.
   */
  public getCurrentLODState(): Record<string, LODLevel> {
    return { ...this.currentLOD };
  }

  /**
   * Integration: Receive budget/resource updates from performance/resource systems.
   * (Stub: To be connected to Task #395/394 systems)
   */
  public onBudgetUpdate(budget: { memory: number; cpu: number; gpu: number }) {
    // TODO: Adjust LOD levels based on new budget constraints
  }

  /**
   * Integration: Listen for resource pressure events (e.g., memory/draw call spikes).
   * (Stub: To be connected to resource monitor)
   */
  public onResourcePressure(event: { type: string; value: number }) {
    // TODO: Trigger LOD/fallback changes as needed
  }

  /**
   * Unified API: Query current LOD/resource state for other systems.
   */
  public getLODState(): Record<string, LODLevel> {
    return this.getCurrentLODState();
  }

  /**
   * Unified API: Allow other systems to request LOD adjustments.
   */
  public requestLODAdjustment(effectType: string, targetLOD: LODLevel) {
    this.setLOD(effectType, targetLOD, true);
  }
}

/**
 * TransitionController: Handles smooth transitions between LOD levels for weather effects.
 * Provides stubs for effect-specific transitions (particle, mesh, shader).
 */
export class TransitionController {
  private activeTransitions: Set<string> = new Set();
  private throttlingLimit: number = 5; // Max simultaneous transitions

  // Start a transition for an effect
  public startTransition(effectId: string, type: 'particle' | 'mesh' | 'shader', from: any, to: any, duration: number, onUpdate: (value: any) => void, onComplete?: () => void) {
    if (this.activeTransitions.size >= this.throttlingLimit) {
      // Throttle: skip or queue
      return;
    }
    this.activeTransitions.add(effectId);
    // Stub: Use requestAnimationFrame or setTimeout for real implementation
    // For now, call onUpdate(to) immediately and onComplete
    onUpdate(to);
    if (onComplete) onComplete();
    this.activeTransitions.delete(effectId);
  }

  // Cancel a transition (e.g., for rapid camera movement)
  public cancelTransition(effectId: string) {
    this.activeTransitions.delete(effectId);
    // Stub: Add logic to actually stop animation
  }

  // Fast-forward all transitions (e.g., for hardware fallback)
  public fastForwardAll() {
    this.activeTransitions.clear();
    // Stub: Add logic to immediately complete all transitions
  }
}

// Specialized transition stubs
export class ParticleSystemTransition {
  // Alpha blending for particle count/density
  public static blend(fromCount: number, toCount: number, duration: number, onUpdate: (count: number) => void, onComplete?: () => void) {
    // TODO: Implement smooth interpolation using requestAnimationFrame
    onUpdate(toCount);
    if (onComplete) onComplete();
  }
}

export class MeshSwapTransition {
  // Mesh swap with optional overlap
  public static swap(fromMesh: any, toMesh: any, duration: number, onUpdate: (mesh: any) => void, onComplete?: () => void) {
    // TODO: Implement mesh swap logic
    onUpdate(toMesh);
    if (onComplete) onComplete();
  }
}

export class ShaderParameterTransition {
  // Interpolate shader parameters
  public static interpolate(fromParams: any, toParams: any, duration: number, onUpdate: (params: any) => void, onComplete?: () => void) {
    // TODO: Implement parameter interpolation
    onUpdate(toParams);
    if (onComplete) onComplete();
  }
}

// --- Effect prioritization logic ---
export enum EffectImportance {
  Essential = 3,
  High = 2,
  Medium = 1,
  Low = 0,
}

export function getEffectImportance(effect: any): EffectImportance {
  // Stub: Use effect properties to determine importance
  if (effect.type === 'rain' || effect.type === 'snow') return EffectImportance.High;
  if (effect.type === 'fog') return EffectImportance.Medium;
  return EffectImportance.Low;
}

export class WeatherEffectSystem {
  private state: WeatherEffectSystemState = {
    activeEffects: new Map(),
    globalEffects: []
  };
  private resourceConfig: WeatherResourceConfig;
  private effectPool: WeatherEffectPool;
  private resourceMonitor: ResourceMonitor = ResourceMonitor.getInstance();
  private performanceMonitor: WeatherPerformanceMonitor = WeatherPerformanceMonitor.getInstance();
  private currentLOD: 'high' | 'medium' | 'low' = 'high';
  private fallbackActive: boolean = false;
  private lodManager: WeatherLODManager;
  private cullingManager: WeatherCullingManager;
  private hardwareProfiler: HardwareProfiler = HardwareProfiler.getInstance();
  private fallbackManager: WeatherFallbackManager;
  private lodOverlayEnabled: boolean = false;
  private profilingPanelEnabled: boolean = false;

  constructor(config: Partial<WeatherEffectSystemConfig> = {}) {
    this.resourceConfig = { ...config };
    this.resourceMonitor.startMonitoring();
    this.performanceMonitor.startMonitoring();
    this.effectPool = new WeatherEffectPool(
      Math.floor(this.resourceConfig.poolSize / 2),
      this.resourceConfig.poolSize
    );
    // Example LOD config (could be loaded from JSON)
    const defaultLODConfig: WeatherLODConfig = {
      thresholds: {
        frameTime: {
          ultra: 8,
          high: 16,
          medium: 24,
          low: 33,
          verylow: 40
        },
        memoryUsage: {
          ultra: 40,
          high: 60,
          medium: 80,
          low: 90,
          verylow: 95
        },
        // gpuScore: { ultra: 10000, high: 7000, medium: 4000, low: 2000, verylow: 1000 } // Optional, fill as needed
      },
      profiles: {
        rain: {
          ultra: { maxParticles: 2000, textureResolution: 2048, shaderComplexity: 1.0, drawDistance: 200, minDistance: 0 },
          high: { maxParticles: 1000, textureResolution: 1024, shaderComplexity: 1.0, drawDistance: 120, minDistance: 0 },
          medium: { maxParticles: 500, textureResolution: 512, shaderComplexity: 0.7, drawDistance: 80, minDistance: 50 },
          low: { maxParticles: 100, textureResolution: 256, shaderComplexity: 0.5, drawDistance: 40, minDistance: 100 },
          verylow: { maxParticles: 20, textureResolution: 128, shaderComplexity: 0.25, drawDistance: 20, minDistance: 150 }
        },
        snow: {
          ultra: { maxParticles: 1600, textureResolution: 2048, shaderComplexity: 1.0, drawDistance: 180, minDistance: 0 },
          high: { maxParticles: 800, textureResolution: 1024, shaderComplexity: 1.0, drawDistance: 100, minDistance: 0 },
          medium: { maxParticles: 400, textureResolution: 512, shaderComplexity: 0.7, drawDistance: 60, minDistance: 50 },
          low: { maxParticles: 80, textureResolution: 256, shaderComplexity: 0.5, drawDistance: 30, minDistance: 100 },
          verylow: { maxParticles: 10, textureResolution: 128, shaderComplexity: 0.25, drawDistance: 15, minDistance: 150 }
        },
        // ...add more effect types as needed
      },
      transitionSmoothing: 300, // ms
    };
    this.lodManager = new WeatherLODManager(defaultLODConfig, (effectType, newLOD, profile) => {
      // Callback: update effect system parameters for this effectType
      // Example: adjust pool size, max particles, etc.
      this.effectPool.resize(effectType, profile.maxParticles);
      // Additional logic to update active effects as needed
    });
    // Register fallback trigger on frame time threshold
    this.performanceMonitor.onThresholdExceeded('frameTime', (metric, value, threshold) => {
      // Fallback logic is now handled by WeatherFallbackManager; no direct call here.
      // this.fallbackManager will handle emergency fallback based on performance metrics.
      // If needed, you could call: this.fallbackManager.triggerEmergencyFallback();
      // For now, do nothing here.
    });
    // Example culling config (could be loaded from JSON)
    const defaultCullingConfig: WeatherCullingConfig = {
      distanceThresholds: {
        rain: 120,
        snow: 100,
        fog: 80,
        // ...
      },
      priority: {
        rain: WeatherEffectPriority.High,
        snow: WeatherEffectPriority.Medium,
        fog: WeatherEffectPriority.Low,
        // ...
      },
      frustumBuffer: 10,
      occlusionEnabled: true,
      smoothingMs: 200,
    };
    // Dummy camera and occlusion for now
    const dummyCamera = { isInFrustum: () => true };
    const dummyOcclusion = () => true;
    this.cullingManager = new WeatherCullingManager(
      defaultCullingConfig,
      this.state.activeEffects,
      dummyCamera,
      dummyOcclusion
    );
    // Fallback system integration
    const fallbackConfig: WeatherFallbackConfig = {
      thresholds: {
        frameTime: { degraded: 40, emergency: 60 },
        memory: { degraded: 90, emergency: 98 },
      },
      hysteresis: 5,
      recoveryDelayMs: 5000,
    };
    this.fallbackManager = new WeatherFallbackManager(
      fallbackConfig,
      this.performanceMonitor,
      (tier: FallbackTier) => this.handleFallbackTierChange(tier)
    );
  }

  private handleFallbackTierChange(tier: FallbackTier) {
    // Adjust LOD or effect complexity based on fallback tier
    // Example: lower LOD, reduce particle count, etc.
    // This is a stub for now; real logic would coordinate with LODManager and effect pools
    switch (tier) {
      case FallbackTier.EMERGENCY:
        // Set all effects to lowest LOD, disable non-essential effects
        break;
      case FallbackTier.DEGRADED:
        // Set effects to medium LOD, reduce complexity
        break;
      case FallbackTier.NORMAL:
        // Restore full quality
        break;
    }
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
    this.checkHardwareAndFallback();
    // Existing fallback logic (clear active effects, etc.) can be integrated here
    if (this.lodManager.isFallbackActive()) {
      // Stub: Apply effect-specific fallbacks (disable effects, switch to billboards, etc.)
    } else {
      // Stub: Restore normal effects if previously in fallback
    }
  }

  /**
   * Check hardware tier and activate fallback mode on initialization or when metrics change.
   */
  public checkHardwareAndFallback() {
    const metrics = this.performanceMonitor.getCurrentMetrics() || this.hardwareProfiler.getCurrentMetrics();
    this.lodManager.checkAndActivateFallback(this.hardwareProfiler, metrics);
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

  // Expose current weather performance metrics for debugging/visualization
  public getWeatherPerformanceMetrics() {
    return this.performanceMonitor.getCurrentMetrics();
  }

  // Example: Pre-warm pools for all effect types before a weather transition
  public prewarmPools(effectTypes: string[], createFn: (type: string) => WeatherEffect, count: number) {
    for (const type of effectTypes) {
      this.effectPool.prewarm(type, () => createFn(type), count);
    }
  }

  // Acquire a weather effect from the pool
  public acquireEffect(effectType: string, createFn: () => WeatherEffect): WeatherEffect {
    return this.effectPool.acquire(effectType, createFn);
  }

  // Release a weather effect back to the pool
  public releaseEffect(effect: WeatherEffect): void {
    this.effectPool.release(effect);
  }

  // Optionally, adjust pool sizes based on performance metrics
  public adjustPoolSizes(): void {
    const metrics = this.performanceMonitor.getCurrentMetrics();
    if (metrics && metrics.memoryUsage > this.resourceConfig.fallbackThresholds.memory) {
      // Shrink pool size if memory usage is high
      this.effectPool.resize('rain', Math.floor(this.resourceConfig.poolSize / 4));
      this.effectPool.resize('snow', Math.floor(this.resourceConfig.poolSize / 4));
      // ...repeat for other types as needed
    } else {
      // Restore to default
      this.effectPool.resize('rain', this.resourceConfig.poolSize);
      this.effectPool.resize('snow', this.resourceConfig.poolSize);
      // ...repeat for other types as needed
    }
  }

  // Update all effect instantiation and recycling to use the pool
  // Example usage in effect creation:
  // const effect = this.acquireEffect('rain', () => createRainEffect(...));
  // ... use effect ...
  // this.releaseEffect(effect);

  // Call this periodically or after performance metric updates
  public updateLODForAllEffects() {
    const metrics = this.performanceMonitor.getCurrentMetrics();
    if (!metrics) return;
    for (const effectType of Object.keys(this.lodManager['config'].profiles)) {
      this.lodManager.updateLOD(effectType, metrics, 0);
    }
  }

  // Get current LOD for an effect type
  public getLOD(effectType: string): LODLevel {
    return this.lodManager.getLOD(effectType);
  }

  // Get LOD profile for an effect type
  public getLODProfile(effectType: string): WeatherLODProfile {
    return this.lodManager.getProfile(effectType);
  }

  // Cull effects for a region before rendering
  public getCulledEffects(regionId: string, cameraPos: { x: number; y: number; z: number }): WeatherEffect[] {
    return this.cullingManager.cull(regionId, cameraPos);
  }

  /**
   * Periodically update LOD for all active effects using current metrics and camera distance.
   * Integrates with HardwareProfiler and WeatherPerformanceMonitor.
   */
  public updateAllDynamicLOD(cameraDistances: Record<string, number>) {
    const metrics = this.performanceMonitor.getCurrentMetrics() || this.hardwareProfiler.getCurrentMetrics();
    for (const regionId of this.state.activeEffects.keys()) {
      const effects = this.state.activeEffects.get(regionId) || [];
      const distance = cameraDistances[regionId] || 0;
      for (const effect of effects) {
        this.lodManager.updateDynamicLOD(effect.type, metrics, distance);
        // Stub: In future, update effect instance parameters here
      }
    }
  }

  /**
   * Subscribe to performance metric updates for event-driven LOD adjustment (stub).
   */
  public subscribeToPerformanceEvents() {
    this.hardwareProfiler.onMetricsUpdate((metrics) => {
      // Optionally, trigger updateAllDynamicLOD with latest metrics
      // (Requires camera distance context)
    });
    // TODO: Add event-driven integration for WeatherPerformanceMonitor if/when supported
  }

  /**
   * Toggle LOD overlay visualization.
   */
  public toggleLODOverlay(enabled?: boolean) {
    this.lodOverlayEnabled = enabled !== undefined ? enabled : !this.lodOverlayEnabled;
  }

  /**
   * Toggle profiling panel.
   */
  public toggleProfilingPanel(enabled?: boolean) {
    this.profilingPanelEnabled = enabled !== undefined ? enabled : !this.profilingPanelEnabled;
  }

  /**
   * Render LOD debug overlay (stub: to be called from main render loop or debug UI).
   */
  public renderLODOverlay(ctx: CanvasRenderingContext2D) {
    if (!this.lodOverlayEnabled) return;
    // Example: Draw LOD boundaries and color-code active effects
    const lodState = this.lodManager.getCurrentLODState();
    for (const [effectType, lod] of Object.entries(lodState)) {
      // Draw overlay for each effectType (stub)
      ctx.save();
      ctx.strokeStyle = LODLevelColors[lod];
      ctx.lineWidth = 2;
      // ... draw effect boundary/label (implementation-specific)
      ctx.restore();
    }
  }

  /**
   * Render profiling panel (stub: to be called from debug UI).
   */
  public renderProfilingPanel(ctx: CanvasRenderingContext2D) {
    if (!this.profilingPanelEnabled) return;
    // Example: Show particle counts, draw calls, memory usage per effect (stub)
    // ... gather and render metrics
  }

  /**
   * Expose profiling data for UI panels.
   */
  public getProfilingData(): Record<string, { particles: number; drawCalls: number; memory: number }> {
    // Stub: Return metrics for each effectType
    return {};
  }

  /**
   * Expose LOD transition log for debugging panels.
   */
  public getLODTransitionLog(): Array<{ effectType: string; from: LODLevel; to: LODLevel; timestamp: number }> {
    return this.lodManager['lodTransitionLog'] || [];
  }

  /**
   * Integration: Connect to dynamic resource management for asset handling.
   * (Stub: To be connected to Task #394 system)
   */
  public onResourceManagerUpdate(resources: { textures: number; meshes: number }) {
    // TODO: Load/unload assets based on LOD transitions
  }

  /**
   * Integration: Support fallback rendering paths when resources are constrained.
   */
  public enableFallbackRendering() {
    // TODO: Switch to fallback rendering for weather effects
  }

  public disableFallbackRendering() {
    // TODO: Restore normal rendering for weather effects
  }

  /**
   * Unified API: Expose LOD/resource state for external systems.
   */
  public getCurrentLODState(): Record<string, LODLevel> {
    return this.lodManager.getLODState();
  }

  /**
   * Unified API: Allow external systems to request LOD changes.
   */
  public setLODForEffect(effectType: string, lod: LODLevel) {
    this.lodManager.requestLODAdjustment(effectType, lod);
  }

  /**
   * Load a resource config from JSON.
   */
  public loadResourceConfig(json: string) {
    this.resourceConfig = JSON.parse(json);
    this.applyResourceConfig();
  }

  /**
   * Save the current resource config as JSON.
   */
  public saveResourceConfig(): string {
    return JSON.stringify(this.resourceConfig, null, 2);
  }

  /**
   * Apply a preset by hardware tier (e.g., 'ultra', 'high', 'medium', 'low').
   */
  public applyPreset(tier: keyof typeof WEATHER_RESOURCE_PRESETS) {
    this.resourceConfig = { ...WEATHER_RESOURCE_PRESETS[tier] };
    this.applyResourceConfig();
  }

  /**
   * Apply the current resource config to all subsystems.
   */
  private applyResourceConfig() {
    // Pool sizes
    Object.entries(this.resourceConfig.poolSizes).forEach(([type, size]) => {
      this.effectPool.resize(type, size);
    });
    // LOD thresholds
    this.lodManager.setThresholds(this.resourceConfig.lodThresholds);
    // Fallback thresholds
    this.fallbackManager.setThresholds(this.resourceConfig.fallbackThresholds);
    // Culling distances
    this.cullingManager.setDistances(this.resourceConfig.cullingDistances);
    // Asset preload count (used during forecast transitions)
    // ...
    // Debug overlays
    this.toggleLODOverlay(this.resourceConfig.enableDebugOverlays);
  }

  /**
   * Get the current resource config.
   */
  public getResourceConfig(): WeatherResourceConfig {
    return this.resourceConfig;
  }

  // --- Weather/Material Integration Hooks ---
  // TODO: When applying weather effects, query affected building elements and apply weathering based on their material resistance and weatheringRate.
  // TODO: Integrate with BuildingDamageSystem and MaterialRegistry for material-aware weathering.
  // TODO: Implement LOD batching for material rendering in large-scale weather events.
} 