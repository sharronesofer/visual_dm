import { Region, MapData, MapChunk, Position } from '../types/map';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3001/api';

export interface GenerateMapOptions {
  width: number;
  height: number;
  seed?: string;
}

export interface MapResponse {
  id: string;
  data: MapData;
}

export interface RegionResponse {
  region: Region;
}

export interface ChunkResponse {
  chunk: MapChunk;
}

export const mapApi = {
  async generateMap(options: GenerateMapOptions): Promise<MapResponse> {
    const response = await fetch(`${API_BASE_URL}/map/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });

    if (!response.ok) {
      throw new Error(`Failed to generate map: ${response.statusText}`);
    }

    return response.json();
  },

  async getMap(id: string): Promise<MapResponse> {
    const response = await fetch(`${API_BASE_URL}/map/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch map: ${response.statusText}`);
    }

    return response.json();
  },

  async getChunk(mapId: string, position: Position): Promise<ChunkResponse> {
    const response = await fetch(`${API_BASE_URL}/map/${mapId}/chunk/${position.x}/${position.y}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch chunk: ${response.statusText}`);
    }

    return response.json();
  },

  async getRegion(mapId: string, regionId: string): Promise<RegionResponse> {
    const response = await fetch(`${API_BASE_URL}/map/${mapId}/region/${regionId}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch region: ${response.statusText}`);
    }

    return response.json();
  },

  async discoverRegions(mapId: string, regionIds: string[]): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/map/${mapId}/discover`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ regions: regionIds }),
    });

    if (!response.ok) {
      throw new Error(`Failed to update discovered regions: ${response.statusText}`);
    }
  },
};
