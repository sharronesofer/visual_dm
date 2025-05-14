from typing import Any, Dict, List, Union



WeatherType = Union[, 'clear', 'rain', 'storm', 'snow', 'fog', 'sandstorm', 'heatwave', 'blizzard']
WeatherIntensity = Union['light', 'moderate', 'heavy', 'extreme']
class WeatherEffect:
    type: Union['visibility', 'movement', 'combat', 'status']
    value: float
    description: str
class WeatherState:
    type: WeatherType
    intensity: WeatherIntensity
    duration: float
    effects: List[WeatherEffect]
    visualEffects: Dict[str, Any]
}
class RegionWeather:
    current: \'WeatherState\'
    forecast: List[WeatherState]
    lastUpdated: float
class WeatherSystemState:
    regions: Dict[str, RegionWeather>
    globalEffects: List[WeatherEffect]
    transitionState?: {
    from: \'WeatherState\'
    to: \'WeatherState\'
    progress: float
}
class WeatherParams:
    region: str
    biome: Union['temperate', 'desert', 'tundra', 'coastal', 'tropical']
    season: Union['spring', 'summer', 'fall', 'winter']
    altitude: float
    forceWeather?: {
    type: WeatherType
    intensity: WeatherIntensity
}
class WeatherConfig:
    transitionDuration: float
    updateInterval: float
    forecastLength: float
    intensityThresholds: Dict[WeatherIntensity, float>
    seasonalWeights: Dict[str, Dict[WeatherType, float>>
    terrainWeights: Dict[str, Dict[WeatherType, float>> 