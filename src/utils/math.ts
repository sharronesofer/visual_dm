/**
 * Math utility functions for the Region Map Display application.
 */

/**
 * Calculate the distance between two points.
 * @param x1 X coordinate of first point
 * @param y1 Y coordinate of first point
 * @param x2 X coordinate of second point
 * @param y2 Y coordinate of second point
 * @returns The Euclidean distance between the points
 */
export function calculateDistance(x1: number, y1: number, x2: number, y2: number): number {
  const dx = x2 - x1;
  const dy = y2 - y1;
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Check if a point is inside a rectangle.
 * @param pointX X coordinate of the point
 * @param pointY Y coordinate of the point
 * @param rectX X coordinate of the rectangle's top-left corner
 * @param rectY Y coordinate of the rectangle's top-left corner
 * @param rectWidth Width of the rectangle
 * @param rectHeight Height of the rectangle
 * @returns True if the point is inside the rectangle, false otherwise
 */
export function isPointInRect(
  pointX: number,
  pointY: number,
  rectX: number,
  rectY: number,
  rectWidth: number,
  rectHeight: number
): boolean {
  return (
    pointX >= rectX &&
    pointX <= rectX + rectWidth &&
    pointY >= rectY &&
    pointY <= rectY + rectHeight
  );
}

export interface Vector2 {
  x: number;
  y: number;
}

export function distance(a: Vector2, b: Vector2): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  return Math.sqrt(dx * dx + dy * dy);
}

export function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

export function randomRange(min: number, max: number): number {
  return min + Math.random() * (max - min);
}

export function randomInt(min: number, max: number): number {
  return Math.floor(randomRange(min, max + 1));
}

export function degToRad(degrees: number): number {
  return degrees * Math.PI / 180;
}

export function radToDeg(radians: number): number {
  return radians * 180 / Math.PI;
}
