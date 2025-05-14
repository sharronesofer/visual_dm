// Coordinate transformation utilities for map rendering

export interface Viewport {
  center: [number, number]; // [longitude, latitude]
  zoom: number;
  rotation: number; // in degrees
  width: number; // viewport width in pixels
  height: number; // viewport height in pixels
}

export interface Point {
  x: number;
  y: number;
}

const DEG_TO_RAD = Math.PI / 180;
const RAD_TO_DEG = 180 / Math.PI;

/**
 * Converts latitude/longitude to pixel coordinates using Mercator projection
 */
export function latLngToPixel(lat: number, lng: number, viewport: Viewport): Point {
  const sinLat = Math.sin(lat * DEG_TO_RAD);
  const mercatorY = Math.log((1 + sinLat) / (1 - sinLat)) / 2;
  const scale = Math.pow(2, viewport.zoom) * (viewport.width / 360);
  const centerPixelX = viewport.width / 2;
  const centerPixelY = viewport.height / 2;
  const centerMercatorY = Math.log(Math.tan(((90 + viewport.center[1]) * DEG_TO_RAD) / 2));
  let x = (lng - viewport.center[0]) * scale + centerPixelX;
  let y = (mercatorY - centerMercatorY) * scale * -1 + centerPixelY;
  if (viewport.rotation !== 0) {
    const rotRad = viewport.rotation * DEG_TO_RAD;
    const cosRot = Math.cos(rotRad);
    const sinRot = Math.sin(rotRad);
    const xDiff = x - centerPixelX;
    const yDiff = y - centerPixelY;
    x = centerPixelX + xDiff * cosRot - yDiff * sinRot;
    y = centerPixelY + xDiff * sinRot + yDiff * cosRot;
  }
  return { x, y };
}

/**
 * Checks if a bounding box is (possibly) visible in the viewport
 */
export function isBoundingBoxInViewport(
  minLat: number,
  minLng: number,
  maxLat: number,
  maxLng: number,
  viewport: Viewport
): boolean {
  const buffer = Math.max(viewport.width, viewport.height) * 0.1;
  const corners = [
    latLngToPixel(minLat, minLng, viewport),
    latLngToPixel(minLat, maxLng, viewport),
    latLngToPixel(maxLat, minLng, viewport),
    latLngToPixel(maxLat, maxLng, viewport),
  ];
  for (const corner of corners) {
    if (
      corner.x >= -buffer &&
      corner.x <= viewport.width + buffer &&
      corner.y >= -buffer &&
      corner.y <= viewport.height + buffer
    ) {
      return true;
    }
  }
  return false;
}

/**
 * Returns the pixel size of 1 degree at the current zoom
 */
export function getPixelSizeAtZoom(viewport: Viewport): number {
  return Math.pow(2, viewport.zoom) * (viewport.width / 360);
}
