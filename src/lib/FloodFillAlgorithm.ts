/**
 * Flood fill algorithm for finding connected regions
 *
 * Provides a class-based interface for flood-fill operations, making it
 * easier to test and reuse across different parts of the application.
 *
 * @module FloodFillAlgorithm
 */

import { Point } from "../structs/point";
import { isInBounds } from "./boundaryUtils";

/**
 * Flood fill algorithm implementation
 *
 * Uses a stack-based approach to find all connected pixels matching a predicate.
 * The algorithm starts from a seed point and expands to all reachable neighbors
 * that satisfy the given condition.
 *
 * @example
 * ```typescript
 * const floodFill = new FloodFillAlgorithm();
 * const start = new Point(10, 10);
 * const region = floodFill.fill(
 *   start,
 *   width,
 *   height,
 *   (x, y) => colorMap[y * width + x] === targetColor
 * );
 * console.log(`Found region with ${region.length} pixels`);
 * ```
 */
export class FloodFillAlgorithm {
  /**
   * Perform flood fill from a starting point
   *
   * Finds all connected pixels that satisfy the shouldInclude predicate
   * using 4-connectivity (up, down, left, right neighbors).
   *
   * @param start - Starting point for the flood fill
   * @param width - Width of the area to fill
   * @param height - Height of the area to fill
   * @param shouldInclude - Predicate function that returns true if a pixel should be included
   * @returns Array of all points in the filled region
   *
   * @example
   * ```typescript
   * const floodFill = new FloodFillAlgorithm();
   * const filled = floodFill.fill(
   *   new Point(5, 5),
   *   100,
   *   100,
   *   (x, y) => !visited[y * 100 + x] && colorMap[y * 100 + x] === targetColor
   * );
   * ```
   */
  public fill(
    start: Point,
    width: number,
    height: number,
    shouldInclude: (x: number, y: number) => boolean
  ): Point[] {
    const filled: Point[] = [];
    const visited = new Set<number>();
    const stack: Point[] = [start];

    while (stack.length > 0) {
      const point = stack.pop()!;
      const key = point.y * width + point.x;

      // Skip if already visited
      if (visited.has(key)) {
        continue;
      }

      // Skip if out of bounds
      if (!isInBounds(point.x, point.y, width, height)) {
        continue;
      }

      // Skip if doesn't match predicate
      if (!shouldInclude(point.x, point.y)) {
        continue;
      }

      // Mark as visited and add to result
      visited.add(key);
      filled.push(point);

      // Add 4-connected neighbors to stack
      // Note: We don't use getNeighbors4 here to avoid extra allocations
      // Instead, we push points directly and rely on bounds checking above
      if (point.y > 0) {
        stack.push(new Point(point.x, point.y - 1)); // Up
      }
      if (point.y < height - 1) {
        stack.push(new Point(point.x, point.y + 1)); // Down
      }
      if (point.x > 0) {
        stack.push(new Point(point.x - 1, point.y)); // Left
      }
      if (point.x < width - 1) {
        stack.push(new Point(point.x + 1, point.y)); // Right
      }
    }

    return filled;
  }

  /**
   * Perform flood fill with a custom callback for each filled pixel
   *
   * Similar to fill() but executes a callback for each pixel instead of
   * collecting them in an array. This is more memory-efficient for large regions.
   *
   * @param start - Starting point for the flood fill
   * @param width - Width of the area to fill
   * @param height - Height of the area to fill
   * @param shouldInclude - Predicate function that returns true if a pixel should be included
   * @param onFill - Callback function executed for each filled pixel
   * @returns Number of pixels filled
   *
   * @example
   * ```typescript
   * const floodFill = new FloodFillAlgorithm();
   * const count = floodFill.fillWithCallback(
   *   new Point(5, 5),
   *   100,
   *   100,
   *   (x, y) => !visited[y * 100 + x],
   *   (x, y) => {
   *     visited[y * 100 + x] = true;
   *     colorMap[y * 100 + x] = newColor;
   *   }
   * );
   * ```
   */
  public fillWithCallback(
    start: Point,
    width: number,
    height: number,
    shouldInclude: (x: number, y: number) => boolean,
    onFill: (x: number, y: number) => void
  ): number {
    const visited = new Set<number>();
    const stack: Point[] = [start];
    let count = 0;

    while (stack.length > 0) {
      const point = stack.pop()!;
      const key = point.y * width + point.x;

      if (visited.has(key)) {
        continue;
      }

      if (!isInBounds(point.x, point.y, width, height)) {
        continue;
      }

      if (!shouldInclude(point.x, point.y)) {
        continue;
      }

      visited.add(key);
      onFill(point.x, point.y);
      count++;

      // Add 4-connected neighbors
      if (point.y > 0) {
        stack.push(new Point(point.x, point.y - 1));
      }
      if (point.y < height - 1) {
        stack.push(new Point(point.x, point.y + 1));
      }
      if (point.x > 0) {
        stack.push(new Point(point.x - 1, point.y));
      }
      if (point.x < width - 1) {
        stack.push(new Point(point.x + 1, point.y));
      }
    }

    return count;
  }
}
