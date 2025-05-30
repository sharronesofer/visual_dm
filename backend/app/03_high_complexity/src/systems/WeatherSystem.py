from typing import Any, Dict, List



  WeatherType,
  WeatherIntensity,
  WeatherState,
  WeatherEffect,
  WeatherSystemState,
  WeatherParams,
  WeatherConfig,
  RegionWeather
} from '../types/weather'
const DEFAULT_CONFIG: WeatherConfig = {
  transitionDuration: 1000, 
  updateInterval: 5000, 
  forecastLength: 5,
  intensityThresholds: Dict[str, Any],
  seasonalWeights: Dict[str, Any],
    summer: Dict[str, Any],
    fall: Dict[str, Any],
    winter: Dict[str, Any]
  },
  terrainWeights: Dict[str, Any],
    mountain: Dict[str, Any],
    forest: Dict[str, Any],
    plains: Dict[str, Any]
  }
}
class WeatherSystem {
  private state: WeatherSystemState
  private config: WeatherConfig
  private updateTimer: float | null
  constructor(config: Partial<WeatherConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
    this.state = {
      regions: {},
      globalEffects: []
    }
    this.updateTimer = null
  }
  public initializeRegion(regionId: str, params: WeatherParams): void {
    const weather = this.generateWeather(params)
    const forecast = Array.from({ length: this.config.forecastLength }, () =>
      this.generateWeather(params)
    )
    this.state.regions[regionId] = {
      current: weather,
      forecast,
      lastUpdated: Date.now()
    }
  }
  private generateWeather(params: WeatherParams): WeatherState {
    const { season = 'spring', terrain = { plains: 1 } } = params
    const weights = this.calculateWeatherWeights(season, terrain)
    const type = this.selectWeatherType(weights)
    const intensity = this.determineIntensity(type)
    const effects = this.generateEffects(type, intensity)
    return {
      type,
      intensity,
      duration: this.calculateDuration(type, intensity),
      effects,
      visualEffects: this.getVisualEffects(type, intensity)
    }
  }
  private calculateWeatherWeights(
    season: str,
    terrain: Record<string, number>
  ): Record<WeatherType, number> {
    const weights: Record<WeatherType, number> = {
      clear: 0,
      rain: 0,
      storm: 0,
      snow: 0,
      fog: 0,
      sandstorm: 0,
      heatwave: 0,
      blizzard: 0
    }
    Object.entries(terrain).forEach(([terrainType, distribution]) => {
      Object.entries(this.config.terrainWeights[terrainType] || {}).forEach(
        ([weatherType, weight]) => {
          weights[weatherType as WeatherType] +=
            weight * distribution * this.config.seasonalWeights[season][weatherType as WeatherType]
        }
      )
    })
    const total = Object.values(weights).reduce((sum, w) => sum + w, 0)
    Object.keys(weights).forEach(key => {
      weights[key as WeatherType] /= total
    })
    return weights
  }
  private selectWeatherType(weights: Record<WeatherType, number>): WeatherType {
    const random = Math.random()
    let sum = 0
    for (const [type, weight] of Object.entries(weights)) {
      sum += weight
      if (random <= sum) {
        return type as WeatherType
      }
    }
    return 'clear' 
  }
  private determineIntensity(type: WeatherType): WeatherIntensity {
    const random = Math.random()
    const { intensityThresholds } = this.config
    if (random >= intensityThresholds.extreme) return 'extreme'
    if (random >= intensityThresholds.heavy) return 'heavy'
    if (random >= intensityThresholds.moderate) return 'moderate'
    return 'light'
  }
  private generateEffects(
    type: WeatherType,
    intensity: WeatherIntensity
  ): WeatherEffect[] {
    const effects: List[WeatherEffect] = []
    const intensityMultiplier = {
      light: 0.5,
      moderate: 1.0,
      heavy: 1.5,
      extreme: 2.0
    }[intensity]
    switch (type) {
      case 'rain':
      case 'storm':
        effects.push({
          type: 'movement',
          value: -0.2 * intensityMultiplier,
          description: 'Reduced movement speed due to wet conditions'
        })
        effects.push({
          type: 'visibility',
          value: -0.3 * intensityMultiplier,
          description: 'Reduced visibility due to rain'
        })
        break
      case 'snow':
      case 'blizzard':
        effects.push({
          type: 'movement',
          value: -0.4 * intensityMultiplier,
          description: 'Significantly reduced movement in snow'
        })
        effects.push({
          type: 'visibility',
          value: -0.5 * intensityMultiplier,
          description: 'Poor visibility in snowy conditions'
        })
        break
      case 'fog':
        effects.push({
          type: 'visibility',
          value: -0.6 * intensityMultiplier,
          description: 'Severely reduced visibility in fog'
        })
        break
      case 'sandstorm':
        effects.push({
          type: 'movement',
          value: -0.3 * intensityMultiplier,
          description: 'Reduced movement in sandstorm'
        })
        effects.push({
          type: 'visibility',
          value: -0.7 * intensityMultiplier,
          description: 'Very poor visibility in sandstorm'
        })
        effects.push({
          type: 'combat',
          value: -0.2 * intensityMultiplier,
          description: 'Combat penalties due to sand'
        })
        break
      case 'heatwave':
        effects.push({
          type: 'status',
          value: -0.4 * intensityMultiplier,
          description: 'Stamina drain due to extreme heat'
        })
        break
    }
    return effects
  }
  private calculateDuration(type: WeatherType, intensity: WeatherIntensity): float {
    const baseDuration = 300 
    const intensityMultiplier = {
      light: 1.5,
      moderate: 1.0,
      heavy: 0.7,
      extreme: 0.5
    }[intensity]
    const typeMultiplier = {
      clear: 2.0,
      rain: 1.0,
      storm: 0.5,
      snow: 1.5,
      fog: 0.7,
      sandstorm: 0.3,
      heatwave: 2.0,
      blizzard: 0.4
    }[type]
    return Math.floor(baseDuration * intensityMultiplier * typeMultiplier)
  }
  private getVisualEffects(
    type: WeatherType,
    intensity: WeatherIntensity
  ): WeatherState['visualEffects'] {
    const intensityValue = {
      light: 0.25,
      moderate: 0.5,
      heavy: 0.75,
      extreme: 1.0
    }[intensity]
    const baseEffects: WeatherState['visualEffects'] = {
      lighting: Dict[str, Any]
    }
    switch (type) {
      case 'rain':
        return {
          ...baseEffects,
          particleSystem: 'rain',
          shader: 'raindrops',
          lighting: Dict[str, Any]
        }
      case 'storm':
        return {
          ...baseEffects,
          particleSystem: 'storm',
          shader: 'raindrops',
          lighting: Dict[str, Any]
        }
      case 'snow':
        return {
          ...baseEffects,
          particleSystem: 'snow',
          shader: 'snow',
          lighting: Dict[str, Any]
        }
      case 'fog':
        return {
          ...baseEffects,
          shader: 'fog',
          lighting: Dict[str, Any]
        }
      case 'sandstorm':
        return {
          ...baseEffects,
          particleSystem: 'sand',
          shader: 'sand',
          lighting: Dict[str, Any]
        }
      case 'blizzard':
        return {
          ...baseEffects,
          particleSystem: 'blizzard',
          shader: 'snow',
          lighting: Dict[str, Any]
        }
      default:
        return baseEffects
    }
  }
  public start(): void {
    if (this.updateTimer !== null) return
    this.updateTimer = window.setInterval(() => {
      this.update()
    }, this.config.updateInterval)
  }
  public stop(): void {
    if (this.updateTimer === null) return
    window.clearInterval(this.updateTimer)
    this.updateTimer = null
  }
  private update(): void {
    Object.entries(this.state.regions).forEach(([regionId, weather]) => {
      const timeSinceUpdate = Date.now() - weather.lastUpdated
      if (timeSinceUpdate >= weather.current.duration * 1000) {
        const nextWeather = weather.forecast.shift()
        if (nextWeather) {
          this.state.regions[regionId] = {
            current: nextWeather,
            forecast: [
              ...weather.forecast,
              this.generateWeather({ region: regionId })
            ],
            lastUpdated: Date.now()
          }
        }
      }
    })
  }
  public getRegionWeather(regionId: str): RegionWeather | null {
    return this.state.regions[regionId] || null
  }
  public getRegionEffects(regionId: str): WeatherEffect[] {
    const weather = this.getRegionWeather(regionId)
    if (!weather) return []
    return [
      ...weather.current.effects,
      ...this.state.globalEffects
    ]
  }
  public addGlobalEffect(effect: WeatherEffect): void {
    this.state.globalEffects.push(effect)
  }
  public removeGlobalEffect(effectType: WeatherEffect['type']): void {
    this.state.globalEffects = this.state.globalEffects.filter(
      effect => effect.type !== effectType
    )
  }
  public getState(): WeatherSystemState {
    return this.state
  }
} 