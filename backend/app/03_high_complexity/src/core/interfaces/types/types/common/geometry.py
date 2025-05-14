from typing import Any



/**
 * Common geometry types used across the application
 */
/** Basic position interface representing a point in 2D space */
class Position:
    x: float
    y: float
/** Rectangle interface for defining bounds */
class Rectangle:
    x: float
    y: float
    width: float
    height: float
/** Size interface for dimensions */
class Size:
    width: float
    height: float
/** Represents a point with optional z-coordinate */
class Point:
    z?: float
/** Represents a vector in 2D space */
class Vector2D:
    dx: float
    dy: float
/** Represents a scale transformation */
class Scale:
    x: float
    y: float
/** Represents a rotation in degrees */
Rotation = float
/** Represents a transformation matrix */
class Transform:
    position: \'Position\'
    scale: \'Scale\'
    rotation: Rotation
/** Helper function to create a Position */
const createPosition = (x: float, y: float): \'Position\' => ({ x, y })
/** Helper function to create a Rectangle */
const createRectangle = (
  x: float,
  y: float,
  width: float,
  height: float
): \'Rectangle\' => ({
  x,
  y,
  width,
  height,
})
/** Helper function to create a Size */
const createSize = (width: float, height: float): \'Size\' => ({
  width,
  height,
})
/** Helper function to create a Transform */
const createTransform = (
  position: \'Position\' = { x: 0, y: 0 },
  scale: \'Scale\' = { x: 1, y: 1 },
  rotation: Rotation = 0
): \'Transform\' => ({
  position,
  scale,
  rotation,
})
/** Type guard for Position interface */
function isPosition(value: Any): value is Position {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof value.x === 'number' &&
    typeof value.y === 'number'
  )
}
/** Type guard for Rectangle interface */
function isRectangle(value: Any): value is Rectangle {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof value.x === 'number' &&
    typeof value.y === 'number' &&
    typeof value.width === 'number' &&
    typeof value.height === 'number'
  )
}
/** Type guard for Transform interface */
function isTransform(value: Any): value is Transform {
  return (
    typeof value === 'object' &&
    value !== null &&
    isPosition(value.position) &&
    typeof value.scale === 'object' &&
    typeof value.scale.x === 'number' &&
    typeof value.scale.y === 'number' &&
    typeof value.rotation === 'number'
  )
}