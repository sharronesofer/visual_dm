from typing import Any



class VariationParamsProvider {
  static getDefault(): VariationParams {
    return {
      region: 'default',
      culture: 'default',
      style: 'modern'
    }
  }
  static getForRegion(region: str, culture: str): VariationParams {
    return {
      region,
      culture,
      style: region === 'north' ? 'rustic' : 'modern'
    }
  }
} 