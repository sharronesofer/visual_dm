from typing import Dict, List, Optional, Any, Union
from typing import Union

TerrainType = Union['plains', 'forest', 'mountain', 'water', 'desert', 'urban']
WeatherType = Union['clear', 'rain', 'snow', 'fog', 'storm', 'windy']
class HexCell {
  q: number; 
  r: number; 
  col: number; 
  row: number; 
  terrain: TerrainType;
  elevation: number;
  discovered: boolean;
  weather?: WeatherType;
  constructor(q: number, r: number, terrain: TerrainType = 'plains', elevation = 0, discovered = false, weather?: WeatherType) {
    this.q = q;
    this.r = r;
    this.col = q + (r - (r & 1)) / 2; 
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