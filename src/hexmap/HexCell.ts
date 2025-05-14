export type TerrainType = 'plains' | 'forest' | 'mountain' | 'water' | 'desert' | 'urban';
export type WeatherType = 'clear' | 'rain' | 'snow' | 'fog' | 'storm' | 'windy';

export class HexCell {
  q: number; // Axial coordinate
  r: number; // Axial coordinate
  col: number; // Offset coordinate
  row: number; // Offset coordinate
  terrain: TerrainType;
  elevation: number;
  discovered: boolean;
  weather?: WeatherType;

  constructor(q: number, r: number, terrain: TerrainType = 'plains', elevation = 0, discovered = false, weather?: WeatherType) {
    this.q = q;
    this.r = r;
    this.col = q + (r - (r & 1)) / 2; // Even-q offset
    this.row = r;
    this.terrain = terrain;
    this.elevation = elevation;
    this.discovered = discovered;
    this.weather = weather;
  }

  serialize(): object {
    return {
      q: this.q,
      r: this.r,
      col: this.col,
      row: this.row,
      terrain: this.terrain,
      elevation: this.elevation,
      discovered: this.discovered,
      weather: this.weather
    };
  }
} 