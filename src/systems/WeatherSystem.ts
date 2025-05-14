import {
  WeatherType,
  WeatherIntensity,
  WeatherState,
  WeatherEffect,
  WeatherSystemState,
  WeatherParams,
  WeatherConfig,
  RegionWeather
} from '../core/interfaces/types/weather';
import { WeatherEffectSystem } from './WeatherEffectSystem';

const DEFAULT_CONFIG: WeatherConfig = {
  transitionDuration: 1000, // 1 second
  updateInterval: 5000, // 5 seconds
  forecastLength: 5,
  intensityThresholds: {
    light: 0.25,
    moderate: 0.5,
    heavy: 0.75,
    extreme: 0.9
  },
  seasonalWeights: {
    spring: {
      clear: 0.4,
      rain: 0.3,
      storm: 0.1,
      fog: 0.1,
      snow: 0.05,
      sandstorm: 0.0,
      heatwave: 0.0,
      blizzard: 0.05
    },
    summer: {
      clear: 0.5,
      rain: 0.2,
      storm: 0.15,
      fog: 0.05,
      snow: 0.0,
      sandstorm: 0.05,
      heatwave: 0.05,
      blizzard: 0.0
    },
    fall: {
      clear: 0.3,
      rain: 0.4,
      storm: 0.15,
      fog: 0.1,
      snow: 0.05,
      sandstorm: 0.0,
      heatwave: 0.0,
      blizzard: 0.0
    },
    winter: {
      clear: 0.3,
      rain: 0.1,
      storm: 0.05,
      fog: 0.15,
      snow: 0.25,
      sandstorm: 0.0,
      heatwave: 0.0,
      blizzard: 0.15
    }
  },
  terrainWeights: {
    desert: {
      clear: 0.6,
      rain: 0.05,
      storm: 0.05,
      fog: 0.05,
      snow: 0.0,
      sandstorm: 0.2,
      heatwave: 0.05,
      blizzard: 0.0
    },
    mountain: {
      clear: 0.3,
      rain: 0.15,
      storm: 0.15,
      fog: 0.1,
      snow: 0.2,
      sandstorm: 0.0,
      heatwave: 0.0,
      blizzard: 0.1
    },
    forest: {
      clear: 0.3,
      rain: 0.3,
      storm: 0.15,
      fog: 0.15,
      snow: 0.05,
      sandstorm: 0.0,
      heatwave: 0.05,
      blizzard: 0.0
    },
    plains: {
      clear: 0.4,
      rain: 0.25,
      storm: 0.15,
      fog: 0.1,
      snow: 0.05,
      sandstorm: 0.0,
      heatwave: 0.05,
      blizzard: 0.0
    }
  }
};

export class WeatherSystem {
  private state: WeatherSystemState;
  private config: WeatherConfig;
  private updateTimer: number | null;
  private effectSystem: WeatherEffectSystem;

  constructor(config: Partial<WeatherConfig> = {}, effectSystem?: WeatherEffectSystem) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.state = {
      regions: {},
      globalEffects: []
    };
    this.updateTimer = null;
    this.effectSystem = effectSystem || new WeatherEffectSystem();
  }

  // Initialize weather for a region
  public initializeRegion(regionId: string, params: WeatherParams): void {
    const weather = this.generateWeather(params);
    const forecast = Array.from({ length: this.config.forecastLength }, () =>
      this.generateWeather(params)
    );

    this.state.regions[regionId] = {
      current: weather,
      forecast,
      lastUpdated: Date.now()
    };
  }

  // Generate a new weather state based on parameters
  private generateWeather(params: WeatherParams): WeatherState {
    const { season = 'spring', biome = 'temperate', altitude = 0 } = params;

    // Calculate weights based on season and biome (use biome as a proxy for terrain)
    const weights = this.calculateWeatherWeights(season, biome);

    // Select weather type based on weights
    const type = this.selectWeatherType(weights);

    // Determine intensity
    const intensity = this.determineIntensity(type);

    // Generate effects
    const effects = this.generateEffects(type, intensity);

    return {
      type,
      intensity,
      duration: this.calculateDuration(type, intensity),
      effects,
      visualEffects: this.getVisualEffects(type, intensity)
    };
  }

  // Calculate weighted probabilities for weather types
  private calculateWeatherWeights(
    season: string,
    biome: string
  ): Record<WeatherType, number> {
    // Map biome to terrain type for weights
    const terrainType = biome === 'desert' ? 'desert'
      : biome === 'tundra' ? 'mountain'
        : biome === 'coastal' ? 'plains'
          : biome === 'tropical' ? 'forest'
            : 'plains';
    const weights: Record<WeatherType, number> = {
      clear: 0,
      rain: 0,
      storm: 0,
      snow: 0,
      fog: 0,
      sandstorm: 0,
      heatwave: 0,
      blizzard: 0
    };
    Object.entries(this.config.terrainWeights[terrainType] || {}).forEach(
      ([weatherType, weight]) => {
        weights[weatherType as WeatherType] +=
          weight * this.config.seasonalWeights[season][weatherType as WeatherType];
      }
    );
    // Normalize weights
    const total = Object.values(weights).reduce((sum, w) => sum + w, 0);
    Object.keys(weights).forEach(key => {
      weights[key as WeatherType] /= total;
    });
    return weights;
  }

  // Select weather type based on weights
  private selectWeatherType(weights: Record<WeatherType, number>): WeatherType {
    const random = Math.random();
    let sum = 0;

    for (const [type, weight] of Object.entries(weights)) {
      sum += weight;
      if (random <= sum) {
        return type as WeatherType;
      }
    }

    return 'clear'; // Fallback
  }

  // Determine weather intensity
  private determineIntensity(type: WeatherType): WeatherIntensity {
    const random = Math.random();
    const { intensityThresholds } = this.config;

    if (random >= intensityThresholds.extreme) return 'extreme';
    if (random >= intensityThresholds.heavy) return 'heavy';
    if (random >= intensityThresholds.moderate) return 'moderate';
    return 'light';
  }

  // Generate weather effects based on type and intensity
  private generateEffects(
    type: WeatherType,
    intensity: WeatherIntensity
  ): WeatherEffect[] {
    const effects: WeatherEffect[] = [];
    const intensityMultiplier = {
      light: 0.5,
      moderate: 1.0,
      heavy: 1.5,
      extreme: 2.0
    }[intensity];

    switch (type) {
      case 'rain':
      case 'storm':
        effects.push({
          type: 'movement',
          value: -0.2 * intensityMultiplier,
          description: 'Reduced movement speed due to wet conditions'
        });
        effects.push({
          type: 'visibility',
          value: -0.3 * intensityMultiplier,
          description: 'Reduced visibility due to rain'
        });
        break;

      case 'snow':
      case 'blizzard':
        effects.push({
          type: 'movement',
          value: -0.4 * intensityMultiplier,
          description: 'Significantly reduced movement in snow'
        });
        effects.push({
          type: 'visibility',
          value: -0.5 * intensityMultiplier,
          description: 'Poor visibility in snowy conditions'
        });
        break;

      case 'fog':
        effects.push({
          type: 'visibility',
          value: -0.6 * intensityMultiplier,
          description: 'Severely reduced visibility in fog'
        });
        break;

      case 'sandstorm':
        effects.push({
          type: 'movement',
          value: -0.3 * intensityMultiplier,
          description: 'Reduced movement in sandstorm'
        });
        effects.push({
          type: 'visibility',
          value: -0.7 * intensityMultiplier,
          description: 'Very poor visibility in sandstorm'
        });
        effects.push({
          type: 'combat',
          value: -0.2 * intensityMultiplier,
          description: 'Combat penalties due to sand'
        });
        break;

      case 'heatwave':
        effects.push({
          type: 'status',
          value: -0.4 * intensityMultiplier,
          description: 'Stamina drain due to extreme heat'
        });
        break;
    }

    return effects;
  }

  // Calculate weather duration based on type and intensity
  private calculateDuration(type: WeatherType, intensity: WeatherIntensity): number {
    const baseDuration = 300; // 5 minutes in seconds
    const intensityMultiplier = {
      light: 1.5,
      moderate: 1.0,
      heavy: 0.7,
      extreme: 0.5
    }[intensity];

    const typeMultiplier = {
      clear: 2.0,
      rain: 1.0,
      storm: 0.5,
      snow: 1.5,
      fog: 0.7,
      sandstorm: 0.3,
      heatwave: 2.0,
      blizzard: 0.4
    }[type];

    return Math.floor(baseDuration * intensityMultiplier * typeMultiplier);
  }

  // Get visual effects configuration
  private getVisualEffects(
    type: WeatherType,
    intensity: WeatherIntensity
  ): WeatherState['visualEffects'] {
    const intensityValue = {
      light: 0.25,
      moderate: 0.5,
      heavy: 0.75,
      extreme: 1.0
    }[intensity];

    const baseEffects: WeatherState['visualEffects'] = {
      lighting: {
        brightness: 1.0,
        color: '#FFFFFF'
      }
    };

    switch (type) {
      case 'rain':
        return {
          ...baseEffects,
          particleSystem: 'rain',
          shader: 'raindrops',
          lighting: {
            brightness: 1.0 - intensityValue * 0.3,
            color: '#8FA5B3'
          }
        };

      case 'storm':
        return {
          ...baseEffects,
          particleSystem: 'storm',
          shader: 'raindrops',
          lighting: {
            brightness: 1.0 - intensityValue * 0.5,
            color: '#4A545C'
          }
        };

      case 'snow':
        return {
          ...baseEffects,
          particleSystem: 'snow',
          shader: 'snow',
          lighting: {
            brightness: 1.0 + intensityValue * 0.2,
            color: '#E8F0FF'
          }
        };

      case 'fog':
        return {
          ...baseEffects,
          shader: 'fog',
          lighting: {
            brightness: 1.0 - intensityValue * 0.2,
            color: '#D4D4D4'
          }
        };

      case 'sandstorm':
        return {
          ...baseEffects,
          particleSystem: 'sand',
          shader: 'sand',
          lighting: {
            brightness: 1.0 - intensityValue * 0.4,
            color: '#D2B48C'
          }
        };

      case 'blizzard':
        return {
          ...baseEffects,
          particleSystem: 'blizzard',
          shader: 'snow',
          lighting: {
            brightness: 1.0 + intensityValue * 0.3,
            color: '#F0F8FF'
          }
        };

      default:
        return baseEffects;
    }
  }

  // Start weather system updates
  public start(): void {
    if (this.updateTimer !== null) return;

    this.updateTimer = window.setInterval(() => {
      this.update();
    }, this.config.updateInterval);
  }

  // Stop weather system updates
  public stop(): void {
    if (this.updateTimer === null) return;

    window.clearInterval(this.updateTimer);
    this.updateTimer = null;
  }

  // Update weather state
  private update(): void {
    Object.entries(this.state.regions).forEach(([regionId, weather]: [string, RegionWeather]) => {
      const timeSinceUpdate = Date.now() - weather.lastUpdated;

      // Check if current weather has expired
      if (timeSinceUpdate >= weather.current.duration * 1000) {
        // Shift to next forecasted weather
        const nextWeather = weather.forecast.shift();
        if (nextWeather) {
          this.state.regions[regionId] = {
            current: nextWeather,
            forecast: [
              ...weather.forecast,
              this.generateWeather({ region: regionId, biome: 'temperate', season: 'spring', altitude: 0 })
            ],
            lastUpdated: Date.now()
          };
          // Set new region effects in the effect system
          this.effectSystem.setRegionEffects(regionId, nextWeather);
        }
      }
      // --- DYNAMIC SCALING: Update LOD based on distance (stub: use 0 for now) ---
      this.effectSystem.updateLOD(0); // Replace 0 with actual camera/region distance
      // --- CULLING: Cull effects if needed (stub: use 0 for now) ---
      this.effectSystem.cullEffects(regionId, 0); // Replace 0 with actual camera/region distance
      // --- PERFORMANCE MONITORING & FALLBACK ---
      this.effectSystem.monitorAndFallback();
      // --- LOGGING & MONITORING ---
      this.effectSystem.logResourceStatus();
    });
  }

  // Get current weather for a region
  public getRegionWeather(regionId: string): RegionWeather | null {
    return this.state.regions[regionId] || null;
  }

  // Get current weather effects for a region
  public getRegionEffects(regionId: string): WeatherEffect[] {
    const weather = this.getRegionWeather(regionId);
    if (!weather) return [];

    return [
      ...weather.current.effects,
      ...this.state.globalEffects
    ];
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

  // Get the current state of the weather system
  public getState(): WeatherSystemState {
    return this.state;
  }
} 