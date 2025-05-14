from typing import Any, List



const weatherTypes: List[WeatherType] = ['clear', 'rain', 'snow', 'fog', 'storm', 'windy']
class WeatherSystem {
  generate(region: str): WeatherPattern {
    const type = weatherTypes[Math.floor(Math.random() * weatherTypes.length)]
    const intensity = Math.random()
    const duration = 30 + Math.floor(Math.random() * 90) 
    return {
      type,
      intensity,
      region,
      duration
    }
  }
} 