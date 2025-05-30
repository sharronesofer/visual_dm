from typing import Any



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
function calculateDistance(x1: float, y1: float, x2: float, y2: float): float {
  const dx = x2 - x1
  const dy = y2 - y1
  return Math.sqrt(dx * dx + dy * dy)
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
function isPointInRect(
  pointX: float,
  pointY: float,
  rectX: float,
  rectY: float,
  rectWidth: float,
  rectHeight: float
): bool {
  return (
    pointX >= rectX &&
    pointX <= rectX + rectWidth &&
    pointY >= rectY &&
    pointY <= rectY + rectHeight
  )
}
class Vector2:
    x: float
    y: float
function distance(a: \'Vector2\', b: Vector2): float {
  const dx = b.x - a.x
  const dy = b.y - a.y
  return Math.sqrt(dx * dx + dy * dy)
}
function lerp(a: float, b: float, t: float): float {
  return a + (b - a) * t
}
function clamp(value: float, min: float, max: float): float {
  return Math.min(Math.max(value, min), max)
}
function randomRange(min: float, max: float): float {
  return min + Math.random() * (max - min)
}
function randomInt(min: float, max: float): float {
  return Math.floor(randomRange(min, max + 1))
}
function degToRad(degrees: float): float {
  return degrees * Math.PI / 180
}
function radToDeg(radians: float): float {
  return radians * 180 / Math.PI
}