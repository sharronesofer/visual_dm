from typing import Any, Dict


  Region,
  POI,
  MapData,
  MapViewState,
  createMapViewState,
} from '../../types/map'
  calculateDistance,
  isPointInRectangle,
  doRectanglesOverlap,
  calculateRectangleIntersection,
  applyTransform,
} from '../geometry'
/**
 * Finds all POIs within a region
 */
const findPOIsInRegion = (
  region: Region,
  pois: Record<string, POI>
): POI[] => {
  return Object.values(pois).filter(
    poi =>
      poi.regionId === region.id ||
      isPointInRectangle(poi.position, region.bounds)
  )
}
/**
 * Finds all regions that overlap with a given region
 */
const findOverlappingRegions = (
  region: Region,
  regions: Record<string, Region>
): Region[] => {
  return Object.values(regions).filter(
    r => r.id !== region.id && doRectanglesOverlap(r.bounds, region.bounds)
  )
}
/**
 * Finds the region containing a point
 */
const findRegionAtPoint = (
  point: Position,
  regions: Record<string, Region>
): Region | undefined => {
  return Object.values(regions).find(region =>
    isPointInRectangle(point, region.bounds)
  )
}
/**
 * Finds POIs within a radius of a point
 */
const findPOIsInRadius = (
  center: Position,
  radius: float,
  pois: Record<string, POI>
): POI[] => {
  return Object.values(pois).filter(
    poi => calculateDistance(center, poi.position) <= radius
  )
}
/**
 * Gets the visible bounds of the map view
 */
const getVisibleBounds = (viewState: MapViewState): Rectangle => {
  const width = window.innerWidth / viewState.zoom
  const height = window.innerHeight / viewState.zoom
  return {
    x: viewState.center.x - width / 2,
    y: viewState.center.y - height / 2,
    width,
    height,
  }
}
/**
 * Updates visible regions and POIs based on view state
 */
const updateVisibleElements = (
  viewState: MapViewState,
  mapData: MapData
): MapViewState => {
  const visibleBounds = getVisibleBounds(viewState)
  const visibleRegionIds = new Set(
    Object.values(mapData.regions)
      .filter(region => doRectanglesOverlap(region.bounds, visibleBounds))
      .map(region => region.id)
  )
  const visiblePOIIds = new Set(
    Object.values(mapData.pois)
      .filter(poi => isPointInRectangle(poi.position, visibleBounds))
      .map(poi => poi.id)
  )
  return {
    ...viewState,
    visibleRegionIds,
    visiblePOIIds,
  }
}
/**
 * Converts screen coordinates to world coordinates
 */
const screenToWorld = (
  screenPos: Position,
  viewState: MapViewState
): Position => {
  const transform: Transform = {
    position: viewState.center,
    rotation: -viewState.rotation,
    scale: Dict[str, Any],
  }
  const screenCenter: Position = {
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  }
  const relativePos: Position = {
    x: screenPos.x - screenCenter.x,
    y: screenPos.y - screenCenter.y,
  }
  return applyTransform(relativePos, transform)
}
/**
 * Converts world coordinates to screen coordinates
 */
const worldToScreen = (
  worldPos: Position,
  viewState: MapViewState
): Position => {
  const transform: Transform = {
    position: Dict[str, Any],
    rotation: viewState.rotation,
    scale: Dict[str, Any],
  }
  const screenCenter: Position = {
    x: window.innerWidth / 2,
    y: window.innerHeight / 2,
  }
  const transformedPos = applyTransform(worldPos, transform)
  return {
    x: transformedPos.x + screenCenter.x,
    y: transformedPos.y + screenCenter.y,
  }
}
/**
 * Calculates the optimal view state to show a region
 */
const calculateRegionViewState = (region: Region): MapViewState => {
  const padding = 50 
  const screenAspect = window.innerWidth / window.innerHeight
  const regionAspect = region.bounds.width / region.bounds.height
  let zoom: float
  if (screenAspect > regionAspect) {
    zoom = (window.innerHeight - padding * 2) / region.bounds.height
  } else {
    zoom = (window.innerWidth - padding * 2) / region.bounds.width
  }
  return createMapViewState(
    {
      x: region.bounds.x + region.bounds.width / 2,
      y: region.bounds.y + region.bounds.height / 2,
    },
    zoom
  )
}