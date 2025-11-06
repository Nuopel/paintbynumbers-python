/**
 * Boundary checking and validation utilities
 *
 * This module provides reusable functions for checking if points are within image boundaries,
 * clamping values, and getting neighbors. These utilities eliminate duplicated boundary
 * checking logic throughout the codebase.
 *
 * @module boundaryUtils
 */

import { Point } from '../structs/point';

/**
 * Edge type flags for identifying which edge(s) a point is on
 * Can be combined using bitwise OR for corners
 */
export enum EdgeType {
  /** Point is not on any edge */
  None = 0,
  /** Point is on left edge (x = 0) */
  Left = 1,
  /** Point is on right edge (x = width - 1) */
  Right = 2,
  /** Point is on top edge (y = 0) */
  Top = 4,
  /** Point is on bottom edge (y = height - 1) */
  Bottom = 8,
}

/**
 * Check if a point is within image boundaries
 *
 * @param x - X coordinate to check
 * @param y - Y coordinate to check
 * @param width - Image width (exclusive upper bound)
 * @param height - Image height (exclusive upper bound)
 * @returns true if point is within bounds [0, width) × [0, height)
 *
 * @example
 * ```typescript
 * if (isInBounds(x, y, image.width, image.height)) {
 *   // Safe to access pixel at (x, y)
 *   const pixel = imageData[y * width + x];
 * }
 * ```
 */
export function isInBounds(
  x: number,
  y: number,
  width: number,
  height: number
): boolean {
  return x >= 0 && x < width && y >= 0 && y < height;
}

/**
 * Clamp a value to a range [min, max]
 *
 * @param value - Value to clamp
 * @param min - Minimum value (inclusive)
 * @param max - Maximum value (inclusive)
 * @returns Clamped value within [min, max]
 *
 * @example
 * ```typescript
 * const x = clamp(-5, 0, 10);  // Returns 0
 * const y = clamp(15, 0, 10);  // Returns 10
 * const z = clamp(5, 0, 10);   // Returns 5
 * ```
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(value, max));
}

/**
 * Clamp a point to image boundaries
 *
 * @param point - Point to clamp
 * @param width - Image width
 * @param height - Image height
 * @returns New point with coordinates clamped to [0, width-1] × [0, height-1]
 *
 * @example
 * ```typescript
 * const clamped = clampPoint({ x: -5, y: 100 }, 50, 50);
 * // Returns { x: 0, y: 49 }
 * ```
 */
export function clampPoint(
  point: Point,
  width: number,
  height: number
): Point {
  return new Point(
    clamp(point.x, 0, width - 1),
    clamp(point.y, 0, height - 1)
  );
}

/**
 * Get 4-connected neighbors (up, down, left, right)
 * Only returns neighbors that are within image boundaries
 *
 * @param x - X coordinate of center point
 * @param y - Y coordinate of center point
 * @param width - Image width
 * @param height - Image height
 * @returns Array of valid neighbor points (2-4 neighbors depending on position)
 *
 * @example
 * ```typescript
 * // Center point returns 4 neighbors
 * const neighbors = getNeighbors4(5, 5, 10, 10);
 * // Returns [{x:5, y:4}, {x:5, y:6}, {x:4, y:5}, {x:6, y:5}]
 *
 * // Corner returns 2 neighbors
 * const corner = getNeighbors4(0, 0, 10, 10);
 * // Returns [{x:1, y:0}, {x:0, y:1}]
 * ```
 */
export function getNeighbors4(
  x: number,
  y: number,
  width: number,
  height: number
): Point[] {
  const neighbors: Point[] = [];

  // Up
  if (y > 0) neighbors.push(new Point(x, y - 1));
  // Down
  if (y < height - 1) neighbors.push(new Point(x, y + 1));
  // Left
  if (x > 0) neighbors.push(new Point(x - 1, y));
  // Right
  if (x < width - 1) neighbors.push(new Point(x + 1, y));

  return neighbors;
}

/**
 * Get 8-connected neighbors (includes diagonals)
 * Only returns neighbors that are within image boundaries
 *
 * @param x - X coordinate of center point
 * @param y - Y coordinate of center point
 * @param width - Image width
 * @param height - Image height
 * @returns Array of valid neighbor points (3-8 neighbors depending on position)
 *
 * @example
 * ```typescript
 * // Center point returns 8 neighbors
 * const neighbors = getNeighbors8(5, 5, 10, 10);
 * // Returns all 8 surrounding points
 *
 * // Corner returns 3 neighbors
 * const corner = getNeighbors8(0, 0, 10, 10);
 * // Returns [{x:1,y:0}, {x:0,y:1}, {x:1,y:1}]
 * ```
 */
export function getNeighbors8(
  x: number,
  y: number,
  width: number,
  height: number
): Point[] {
  const neighbors: Point[] = [];

  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      if (dx === 0 && dy === 0) continue; // Skip center point

      const nx = x + dx;
      const ny = y + dy;

      if (isInBounds(nx, ny, width, height)) {
        neighbors.push(new Point(nx, ny));
      }
    }
  }

  return neighbors;
}

/**
 * Check if a point is on any edge of the image
 *
 * @param x - X coordinate to check
 * @param y - Y coordinate to check
 * @param width - Image width
 * @param height - Image height
 * @returns true if point is on left, right, top, or bottom edge
 *
 * @example
 * ```typescript
 * isOnEdge(0, 5, 10, 10);    // true (left edge)
 * isOnEdge(9, 5, 10, 10);    // true (right edge)
 * isOnEdge(5, 5, 10, 10);    // false (center)
 * isOnEdge(0, 0, 10, 10);    // true (corner)
 * ```
 */
export function isOnEdge(
  x: number,
  y: number,
  width: number,
  height: number
): boolean {
  return x === 0 || x === width - 1 || y === 0 || y === height - 1;
}

/**
 * Get which edge(s) a point is on
 * Returns a bitmask that can be tested with bitwise AND
 * Points on corners will have multiple flags set
 *
 * @param x - X coordinate to check
 * @param y - Y coordinate to check
 * @param width - Image width
 * @param height - Image height
 * @returns EdgeType bitmask indicating which edge(s) the point is on
 *
 * @example
 * ```typescript
 * const edge = getEdgeType(0, 0, 10, 10);
 * if (edge & EdgeType.Left) {
 *   console.log('On left edge');
 * }
 * if (edge & EdgeType.Top) {
 *   console.log('On top edge');
 * }
 * // For corner (0,0), both conditions above are true
 *
 * const center = getEdgeType(5, 5, 10, 10);
 * // Returns EdgeType.None (0)
 * ```
 */
export function getEdgeType(
  x: number,
  y: number,
  width: number,
  height: number
): EdgeType {
  let edge = EdgeType.None;

  if (x === 0) edge |= EdgeType.Left;
  if (x === width - 1) edge |= EdgeType.Right;
  if (y === 0) edge |= EdgeType.Top;
  if (y === height - 1) edge |= EdgeType.Bottom;

  return edge;
}
