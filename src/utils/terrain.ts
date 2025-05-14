import { GridPosition } from '../types/grid';
import { 
  TerrainData, 
  TerrainFeature, 
  TerrainFeatureType,
  BuildableArea,
  TerrainAnalysisResult,
  TerrainModification,
  TerrainModificationType
} from '../types/terrain';

export { TerrainModificationType };

export interface TerrainAnalysisResult {
  slope: number;
  elevation: number;
  nearbyFeatures: TerrainFeature[];
  buildabilityScore: number;
  environmentalImpact: number;
}

export interface TerrainModification {
  position: GridPosition;
  type: TerrainModificationType;
  params: Record<string, any>;
}

export enum TerrainModificationType {
  LEVEL = 'LEVEL',
  SMOOTH = 'SMOOTH',
  RAMP = 'RAMP',
  FOUNDATION = 'FOUNDATION'
}

export class TerrainManager {
  private heightMap: number[][];
  private features: TerrainFeature[];
  private buildableAreas: BuildableArea[];
  private readonly MAX_SLOPE = 30; // Maximum slope angle in degrees
  private readonly MIN_FEATURE_DISTANCE = 2; // Minimum distance to preserve features
  private readonly ANALYSIS_CACHE_SIZE = 1000;
  private analysisCache: Map<string, TerrainAnalysisResult>;

  constructor(terrainData: TerrainData) {
    this.heightMap = terrainData.heightMap;
    this.features = terrainData.features;
    this.buildableAreas = terrainData.buildableAreas;
    this.analysisCache = new Map();
  }

  public analyzeTerrain(position: GridPosition, radius: number = 1): TerrainAnalysisResult {
    const cacheKey = this.getCacheKey(position, radius);
    const cached = this.analysisCache.get(cacheKey);
    if (cached) return cached;

    const result: TerrainAnalysisResult = {
      slope: this.calculateSlope(position, radius),
      elevation: this.getElevation(position),
      nearbyFeatures: this.findNearbyFeatures(position, radius),
      buildabilityScore: 0,
      environmentalImpact: 0
    };

    // Calculate buildability score (0-1)
    result.buildabilityScore = this.calculateBuildabilityScore(result);
    
    // Calculate environmental impact (0-1)
    result.environmentalImpact = this.calculateEnvironmentalImpact(position, radius);

    // Cache the result
    this.cacheAnalysisResult(cacheKey, result);

    return result;
  }

  public modifyTerrain(modification: TerrainModification): void {
    const { position, type, params } = modification;

    switch (type) {
      case TerrainModificationType.LEVEL:
        this.levelTerrain(position, params.heightDelta || 0, params.preserveFeatures || false);
        break;
      case TerrainModificationType.SMOOTH:
        this.smoothTerrain(position, params.smoothingRadius || 1);
        break;
      case TerrainModificationType.RAMP:
        this.createRamp(position, params.heightDelta || 0);
        break;
      case TerrainModificationType.FOUNDATION:
        this.adjustFoundation(position);
        break;
    }

    // Clear affected area from cache
    this.invalidateAnalysisCache(position, params.smoothingRadius || 1);
  }

  public findBuildableArea(
    size: { width: number; height: number },
    preferredFeatures: TerrainFeatureType[] = []
  ): BuildableArea | null {
    // Sort buildable areas by suitability
    const sortedAreas = [...this.buildableAreas]
      .filter(area => area.size.width >= size.width && area.size.height >= size.height)
      .sort((a, b) => {
        const aScore = this.calculateAreaSuitability(a, preferredFeatures);
        const bScore = this.calculateAreaSuitability(b, preferredFeatures);
        return bScore - aScore;
      });

    return sortedAreas[0] || null;
  }

  private calculateSlope(position: GridPosition, radius: number): number {
    let maxSlope = 0;
    
    // Calculate slope in all directions within radius
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        if (dx === 0 && dy === 0) continue;
        
        const neighborPos = { x: position.x + dx, y: position.y + dy };
        if (!this.isValidPosition(neighborPos)) continue;

        const heightDiff = Math.abs(
          this.getElevation(position) - this.getElevation(neighborPos)
        );
        const distance = Math.sqrt(dx * dx + dy * dy);
        const slope = Math.atan(heightDiff / distance) * (180 / Math.PI);
        
        maxSlope = Math.max(maxSlope, slope);
      }
    }

    return maxSlope;
  }

  private calculateBuildabilityScore(analysis: TerrainAnalysisResult): number {
    const slopeScore = Math.max(0, 1 - analysis.slope / this.MAX_SLOPE);
    const featureScore = Math.max(0, 1 - analysis.nearbyFeatures.length * 0.2);
    
    // Weight the scores (slope is more important)
    return slopeScore * 0.7 + featureScore * 0.3;
  }

  private calculateEnvironmentalImpact(position: GridPosition, radius: number): number {
    const features = this.findNearbyFeatures(position, radius);
    let impact = 0;

    // Calculate impact based on feature proximity and type
    features.forEach(feature => {
      const distance = this.calculateDistance(position, feature.position);
      const featureImpact = this.getFeatureImpactWeight(feature.type) / Math.max(1, distance);
      impact += featureImpact;
    });

    return Math.min(1, impact);
  }

  private getFeatureImpactWeight(type: TerrainFeatureType): number {
    switch (type) {
      case TerrainFeatureType.WATER: return 1.0;
      case TerrainFeatureType.FOREST: return 0.8;
      case TerrainFeatureType.CLIFF: return 0.6;
      case TerrainFeatureType.MOUNTAIN: return 0.4;
      case TerrainFeatureType.VALLEY: return 0.3;
      default: return 0.1;
    }
  }

  private levelTerrain(position: GridPosition, heightDelta: number, preserveFeatures: boolean): void {
    const radius = 1;
    if (preserveFeatures && this.hasNearbyFeatures(position, radius)) {
      return;
    }

    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy };
        if (this.isValidPosition(pos)) {
          this.setElevation(pos, this.getElevation(position) + heightDelta);
        }
      }
    }
  }

  private smoothTerrain(position: GridPosition, radius: number): void {
    const originalHeight = this.getElevation(position);
    let sum = 0;
    let count = 0;

    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy };
        if (this.isValidPosition(pos)) {
          sum += this.getElevation(pos);
          count++;
        }
      }
    }

    const averageHeight = sum / count;
    this.setElevation(position, (originalHeight + averageHeight) / 2);
  }

  private createRamp(position: GridPosition, heightDelta: number): void {
    const radius = 2;
    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy };
        if (!this.isValidPosition(pos)) continue;

        const distance = Math.sqrt(dx * dx + dy * dy);
        const gradientFactor = 1 - (distance / radius);
        const adjustment = heightDelta * gradientFactor;
        
        this.setElevation(pos, this.getElevation(pos) + adjustment);
      }
    }
  }

  private adjustFoundation(position: GridPosition): void {
    const radius = 1;
    const targetHeight = this.getElevation(position);

    for (let dx = -radius; dx <= radius; dx++) {
      for (let dy = -radius; dy <= radius; dy++) {
        const pos = { x: position.x + dx, y: position.y + dy };
        if (!this.isValidPosition(pos)) continue;

        // Gradually adjust height towards target
        const currentHeight = this.getElevation(pos);
        const adjustment = (targetHeight - currentHeight) * 0.5;
        this.setElevation(pos, currentHeight + adjustment);
      }
    }
  }

  private findNearbyFeatures(position: GridPosition, radius: number): TerrainFeature[] {
    return this.features.filter(feature => {
      const distance = this.calculateDistance(position, feature.position);
      return distance <= radius;
    });
  }

  private hasNearbyFeatures(position: GridPosition, radius: number): boolean {
    return this.findNearbyFeatures(position, radius).length > 0;
  }

  private calculateDistance(a: GridPosition, b: GridPosition): number {
    return Math.sqrt(Math.pow(b.x - a.x, 2) + Math.pow(b.y - a.y, 2));
  }

  private calculateAreaSuitability(
    area: BuildableArea,
    preferredFeatures: TerrainFeatureType[]
  ): number {
    const center: GridPosition = {
      x: area.position.x + Math.floor(area.size.width / 2),
      y: area.position.y + Math.floor(area.size.height / 2)
    };

    const analysis = this.analyzeTerrain(center, Math.max(area.size.width, area.size.height));
    let score = analysis.buildabilityScore;

    // Bonus for preferred features nearby
    const hasPreferredFeatures = analysis.nearbyFeatures.some(
      feature => preferredFeatures.includes(feature.type)
    );
    if (hasPreferredFeatures) score *= 1.2;

    return score;
  }

  private getElevation(position: GridPosition): number {
    if (!this.isValidPosition(position)) return 0;
    return this.heightMap[position.y][position.x];
  }

  private setElevation(position: GridPosition, height: number): void {
    if (!this.isValidPosition(position)) return;
    this.heightMap[position.y][position.x] = height;
  }

  private isValidPosition(position: GridPosition): boolean {
    return position.x >= 0 && 
           position.x < this.heightMap[0].length &&
           position.y >= 0 && 
           position.y < this.heightMap.length;
  }

  private getCacheKey(position: GridPosition, radius: number): string {
    return `${position.x},${position.y},${radius}`;
  }

  private cacheAnalysisResult(key: string, result: TerrainAnalysisResult): void {
    if (this.analysisCache.size >= this.ANALYSIS_CACHE_SIZE) {
      // Remove oldest entry if cache is full
      const firstKey = this.analysisCache.keys().next().value;
      this.analysisCache.delete(firstKey);
    }
    this.analysisCache.set(key, result);
  }

  private invalidateAnalysisCache(position: GridPosition, radius: number): void {
    for (const key of this.analysisCache.keys()) {
      const [x, y] = key.split(',').map(Number);
      const distance = this.calculateDistance(position, { x, y });
      if (distance <= radius) {
        this.analysisCache.delete(key);
      }
    }
  }

  public toSerializedData(): any {
    return {
      heightMap: this.heightMap,
      features: this.features,
      buildableAreas: this.buildableAreas,
      analysisCache: Array.from(this.analysisCache.entries())
    };
  }

  public static fromSerializedData(data: any): TerrainManager {
    const manager = new TerrainManager(
      data.heightMap,
      data.features,
      data.buildableAreas
    );
    manager.analysisCache = new Map(data.analysisCache);
    return manager;
  }
} 