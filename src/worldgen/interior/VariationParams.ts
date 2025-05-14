import { VariationParams } from './types';

export class VariationParamsProvider {
  static getDefault(): VariationParams {
    return {
      region: 'default',
      culture: 'default',
      style: 'modern'
    };
  }

  static getForRegion(region: string, culture: string): VariationParams {
    // TODO: Add logic for region/culture-specific params
    return {
      region,
      culture,
      style: region === 'north' ? 'rustic' : 'modern'
    };
  }
} 