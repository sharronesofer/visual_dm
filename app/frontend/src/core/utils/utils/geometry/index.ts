import {
  Position,
  Point,
  Rectangle,
  Vector2D,
  Transform,
} from '../../types/common/geometry';

/**
 * Calculates the Euclidean distance between two positions
 */
export const calculateDistance = (from: Position, to: Position): number => {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  return Math.sqrt(dx * dx + dy * dy);
};

/**
 * Calculates the Manhattan distance between two positions
 */
export const calculateManhattanDistance = (
  from: Position,
  to: Position
): number => {
  return Math.abs(to.x - from.x) + Math.abs(to.y - from.y);
};

/**
 * Checks if a point is inside a rectangle
 */
export const isPointInRectangle = (
  point: Position,
  rect: Rectangle
): boolean => {
  return (
    point.x >= rect.x &&
    point.x <= rect.x + rect.width &&
    point.y >= rect.y &&
    point.y <= rect.y + rect.height
  );
};

/**
 * Checks if two rectangles overlap
 */
export const doRectanglesOverlap = (
  rect1: Rectangle,
  rect2: Rectangle
): boolean => {
  return (
    rect1.x < rect2.x + rect2.width &&
    rect1.x + rect1.width > rect2.x &&
    rect1.y < rect2.y + rect2.height &&
    rect1.y + rect1.height > rect2.y
  );
};

/**
 * Calculates the intersection of two rectangles
 */
export const calculateRectangleIntersection = (
  rect1: Rectangle,
  rect2: Rectangle
): Rectangle | null => {
  const x = Math.max(rect1.x, rect2.x);
  const y = Math.max(rect1.y, rect2.y);
  const width = Math.min(rect1.x + rect1.width, rect2.x + rect2.width) - x;
  const height = Math.min(rect1.y + rect1.height, rect2.y + rect2.height) - y;

  if (width <= 0 || height <= 0) {
    return null;
  }

  return { x, y, width, height };
};

/**
 * Calculates the center point of a rectangle
 */
export const calculateRectangleCenter = (rect: Rectangle): Position => ({
  x: rect.x + rect.width / 2,
  y: rect.y + rect.height / 2,
});

/**
 * Normalizes a vector to have a magnitude of 1
 */
export const normalizeVector = (vector: Vector2D): Vector2D => {
  const magnitude = Math.sqrt(vector.dx * vector.dx + vector.dy * vector.dy);
  if (magnitude === 0) {
    return { dx: 0, dy: 0 };
  }
  return {
    dx: vector.dx / magnitude,
    dy: vector.dy / magnitude,
  };
};

/**
 * Applies a transform to a position
 */
export const applyTransform = (
  position: Position,
  transform: Transform
): Position => {
  const rotatedX =
    position.x * Math.cos(transform.rotation) -
    position.y * Math.sin(transform.rotation);
  const rotatedY =
    position.x * Math.sin(transform.rotation) +
    position.y * Math.cos(transform.rotation);

  return {
    x: rotatedX * transform.scale.x + transform.position.x,
    y: rotatedY * transform.scale.y + transform.position.y,
  };
};
