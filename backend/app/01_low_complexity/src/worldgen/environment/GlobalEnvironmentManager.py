from typing import Any



class GlobalEnvironmentManager {
  private weatherSystem = new WeatherSystem()
  private hazardSystem = new HazardSystem()
  generate(region: str, season: str, time: float): EnvironmentalState {
    const weather = this.weatherSystem.generate(region)
    const hazards = this.hazardSystem.generate(region)
    return {
      weather,
      hazards,
      season,
      time
    }
  }
} 