from typing import Any, Dict, List



const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http:
class GenerateMapOptions:
    width: float
    height: float
    seed?: str
class MapResponse:
    id: str
    data: MapData
class RegionResponse:
    region: Region
class ChunkResponse:
    chunk: MapChunk
const mapApi = {
  async generateMap(options: GenerateMapOptions): Promise<MapResponse> {
    const response = await fetch(`${API_BASE_URL}/map/generate`, {
      method: 'POST',
      headers: Dict[str, Any],
      body: JSON.stringify(options),
    })
    if (!response.ok) {
      throw new Error(`Failed to generate map: ${response.statusText}`)
    }
    return response.json()
  },
  async getMap(id: str): Promise<MapResponse> {
    const response = await fetch(`${API_BASE_URL}/map/${id}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch map: ${response.statusText}`)
    }
    return response.json()
  },
  async getChunk(mapId: str, position: Position): Promise<ChunkResponse> {
    const response = await fetch(`${API_BASE_URL}/map/${mapId}/chunk/${position.x}/${position.y}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch chunk: ${response.statusText}`)
    }
    return response.json()
  },
  async getRegion(mapId: str, regionId: str): Promise<RegionResponse> {
    const response = await fetch(`${API_BASE_URL}/map/${mapId}/region/${regionId}`)
    if (!response.ok) {
      throw new Error(`Failed to fetch region: ${response.statusText}`)
    }
    return response.json()
  },
  async discoverRegions(mapId: str, regionIds: List[string]): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/map/${mapId}/discover`, {
      method: 'POST',
      headers: Dict[str, Any],
      body: JSON.stringify({ regions: regionIds }),
    })
    if (!response.ok) {
      throw new Error(`Failed to update discovered regions: ${response.statusText}`)
    }
  },
}