/**
 * Common geometry types used across the application
 */

/** Basic position interface representing a point in 2D space */
export interface Position {
  x: number;
  y: number;
}

/** Rectangle interface for defining bounds */
export interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

/** Size interface for dimensions */
export interface Size {
  width: number;
  height: number;
}

/** Represents a point with optional z-coordinate */
export interface Point extends Position {
  z?: number;
}

/** Represents a vector in 2D space */
export interface Vector2D {
  dx: number;
  dy: number;
}

/** Represents a scale transformation */
export interface Scale {
  x: number;
  y: number;
}

/** Represents a rotation in degrees */
export type Rotation = number;

/** Represents a transformation matrix */
export interface Transform {
  position: Position;
  scale: Scale;
  rotation: Rotation;
}

/** Helper function to create a Position */
export const createPosition = (x: number, y: number): Position => ({ x, y });

/** Helper function to create a Rectangle */
export const createRectangle = (
  x: number,
  y: number,
  width: number,
  height: number
): Rectangle => ({
  x,
  y,
  width,
  height,
});

/** Helper function to create a Size */
export const createSize = (width: number, height: number): Size => ({
  width,
  height,
});

/** Helper function to create a Transform */
export const createTransform = (
  position: Position = { x: 0, y: 0 },
  scale: Scale = { x: 1, y: 1 },
  rotation: Rotation = 0
): Transform => ({
  position,
  scale,
  rotation,
});

/** Type guard for Position interface */
export function isPosition(value: any): value is Position {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof value.x === 'number' &&
    typeof value.y === 'number'
  );
}

/** Type guard for Rectangle interface */
export function isRectangle(value: any): value is Rectangle {
  return (
    typeof value === 'object' &&
    value !== null &&
    typeof value.x === 'number' &&
    typeof value.y === 'number' &&
    typeof value.width === 'number' &&
    typeof value.height === 'number'
  );
}

/** Type guard for Transform interface */
export function isTransform(value: any): value is Transform {
  return (
    typeof value === 'object' &&
    value !== null &&
    isPosition(value.position) &&
    typeof value.scale === 'object' &&
    typeof value.scale.x === 'number' &&
    typeof value.scale.y === 'number' &&
    typeof value.rotation === 'number'
  );
}
