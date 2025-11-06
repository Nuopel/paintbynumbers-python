/**
 * Facet building utilities
 *
 * Separates facet construction from region finding, making the code
 * more modular and easier to test.
 *
 * @module FacetBuilder
 */

import { Point } from "../structs/point";
import { BoundingBox } from "../structs/boundingbox";
import { Facet, FacetResult } from "../facetmanagement";
import { BooleanArray2D, Uint8Array2D } from "../structs/typedarrays";
import { fill } from "./fill";

/**
 * Builder class for creating facets from color-mapped images
 *
 * Provides a clean interface for facet creation that separates the concerns
 * of region detection (flood fill) from facet object construction.
 *
 * @example
 * ```typescript
 * const builder = new FacetBuilder();
 * const facet = builder.buildFacet(
 *   0,           // facetIndex
 *   5,           // colorIndex
 *   10, 10,      // starting x, y
 *   visited,     // visited mask
 *   colorMap,    // color indices
 *   facetResult  // result container
 * );
 * ```
 */
export class FacetBuilder {
  /**
   * Build a single facet starting from a given point
   *
   * Uses flood fill to find all connected pixels of the same color,
   * then constructs a Facet object with:
   * - Point count
   * - Border points
   * - Bounding box
   * - Color index
   *
   * @param facetIndex - Unique index for this facet
   * @param facetColorIndex - Color index this facet represents
   * @param x - Starting x coordinate
   * @param y - Starting y coordinate
   * @param visited - 2D array tracking visited pixels
   * @param imgColorIndices - 2D array of color indices
   * @param facetResult - Result container to update
   * @returns Newly created facet
   *
   * @example
   * ```typescript
   * const builder = new FacetBuilder();
   * const visited = new BooleanArray2D(width, height);
   * const facet = builder.buildFacet(
   *   0, 5, 10, 10,
   *   visited, colorMap, result
   * );
   * console.log(`Facet has ${facet.pointCount} pixels`);
   * ```
   */
  public buildFacet(
    facetIndex: number,
    facetColorIndex: number,
    x: number,
    y: number,
    visited: BooleanArray2D,
    imgColorIndices: Uint8Array2D,
    facetResult: FacetResult
  ): Facet {
    const facet = new Facet();
    facet.id = facetIndex;
    facet.color = facetColorIndex;
    facet.bbox = new BoundingBox();
    facet.borderPoints = [];
    facet.neighbourFacetsIsDirty = true;
    facet.neighbourFacets = null;

    // Use optimized fill algorithm with callbacks
    // This avoids allocating Point objects during the fill
    fill(
      x,
      y,
      facetResult.width,
      facetResult.height,
      (ptx, pty) =>
        visited.get(ptx, pty) || imgColorIndices.get(ptx, pty) !== facetColorIndex,
      (ptx, pty) => {
        // Mark as visited
        visited.set(ptx, pty, true);
        facetResult.facetMap.set(ptx, pty, facetIndex);
        facet.pointCount++;

        // Determine if this is a border point
        // A point is a border point if any of its 4-neighbors has a different color
        const isInnerPoint = imgColorIndices.matchAllAround(ptx, pty, facetColorIndex);
        if (!isInnerPoint) {
          facet.borderPoints.push(new Point(ptx, pty));
        }

        // Update bounding box
        if (ptx > facet.bbox.maxX) {
          facet.bbox.maxX = ptx;
        }
        if (pty > facet.bbox.maxY) {
          facet.bbox.maxY = pty;
        }
        if (ptx < facet.bbox.minX) {
          facet.bbox.minX = ptx;
        }
        if (pty < facet.bbox.minY) {
          facet.bbox.minY = pty;
        }
      }
    );

    return facet;
  }

  /**
   * Build all facets from a color-mapped image
   *
   * Scans the entire image and creates a facet for each connected region
   * of pixels with the same color.
   *
   * @param imgColorIndices - 2D array of color indices
   * @param width - Image width
   * @param height - Image height
   * @param facetResult - Result container to populate
   * @returns Array of created facets
   *
   * @example
   * ```typescript
   * const builder = new FacetBuilder();
   * const result = new FacetResult();
   * result.width = 100;
   * result.height = 100;
   * result.facetMap = new Uint32Array2D(100, 100);
   * result.facets = [];
   *
   * const facets = builder.buildAllFacets(colorMap, 100, 100, result);
   * console.log(`Created ${facets.length} facets`);
   * ```
   */
  public buildAllFacets(
    imgColorIndices: Uint8Array2D,
    width: number,
    height: number,
    facetResult: FacetResult
  ): Facet[] {
    const visited = new BooleanArray2D(width, height);
    const facets: Facet[] = [];

    for (let j = 0; j < height; j++) {
      for (let i = 0; i < width; i++) {
        if (!visited.get(i, j)) {
          const colorIndex = imgColorIndices.get(i, j);
          const facetIndex = facets.length;

          const facet = this.buildFacet(
            facetIndex,
            colorIndex,
            i,
            j,
            visited,
            imgColorIndices,
            facetResult
          );

          facets.push(facet);
        }
      }
    }

    return facets;
  }

  /**
   * Calculate the bounding box of a set of points
   *
   * @param points - Array of points
   * @returns Bounding box containing all points
   *
   * @example
   * ```typescript
   * const builder = new FacetBuilder();
   * const points = [new Point(5, 10), new Point(15, 20), new Point(8, 12)];
   * const bbox = builder.calculateBoundingBox(points);
   * console.log(`Box: (${bbox.minX}, ${bbox.minY}) to (${bbox.maxX}, ${bbox.maxY})`);
   * ```
   */
  public calculateBoundingBox(points: Point[]): BoundingBox {
    if (points.length === 0) {
      return new BoundingBox();
    }

    const bbox = new BoundingBox();
    bbox.minX = Number.MAX_VALUE;
    bbox.minY = Number.MAX_VALUE;
    bbox.maxX = Number.MIN_VALUE;
    bbox.maxY = Number.MIN_VALUE;

    for (const pt of points) {
      if (pt.x < bbox.minX) {
        bbox.minX = pt.x;
      }
      if (pt.x > bbox.maxX) {
        bbox.maxX = pt.x;
      }
      if (pt.y < bbox.minY) {
        bbox.minY = pt.y;
      }
      if (pt.y > bbox.maxY) {
        bbox.maxY = pt.y;
      }
    }

    return bbox;
  }

  /**
   * Identify border points within a set of points
   *
   * A point is considered a border point if any of its 4-neighbors
   * (up, down, left, right) is not in the point set.
   *
   * @param points - Array of points in the region
   * @param width - Width of the area
   * @param height - Height of the area
   * @returns Array of border points
   *
   * @example
   * ```typescript
   * const builder = new FacetBuilder();
   * const region = [
   *   new Point(5, 5), new Point(6, 5), new Point(7, 5),
   *   new Point(5, 6), new Point(6, 6), new Point(7, 6),
   * ];
   * const border = builder.identifyBorderPoints(region, 100, 100);
   * console.log(`${border.length} border points found`);
   * ```
   */
  public identifyBorderPoints(
    points: Point[],
    width: number,
    height: number
  ): Point[] {
    // Create a set for fast lookup
    const pointSet = new Set<number>();
    for (const pt of points) {
      pointSet.add(pt.y * width + pt.x);
    }

    const borderPoints: Point[] = [];

    for (const pt of points) {
      let isBorder = false;

      // Check 4-neighbors
      if (pt.y > 0 && !pointSet.has((pt.y - 1) * width + pt.x)) {
        isBorder = true; // Top neighbor missing
      } else if (pt.y < height - 1 && !pointSet.has((pt.y + 1) * width + pt.x)) {
        isBorder = true; // Bottom neighbor missing
      } else if (pt.x > 0 && !pointSet.has(pt.y * width + (pt.x - 1))) {
        isBorder = true; // Left neighbor missing
      } else if (pt.x < width - 1 && !pointSet.has(pt.y * width + (pt.x + 1))) {
        isBorder = true; // Right neighbor missing
      }

      // Also check if at image boundary
      if (pt.x === 0 || pt.x === width - 1 || pt.y === 0 || pt.y === height - 1) {
        isBorder = true;
      }

      if (isBorder) {
        borderPoints.push(pt);
      }
    }

    return borderPoints;
  }
}
