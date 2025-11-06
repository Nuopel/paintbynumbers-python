import { FacetBuilder } from '../../../src/lib/FacetBuilder';
import { Point } from '../../../src/structs/point';
import { BoundingBox } from '../../../src/structs/boundingbox';
import { FacetResult, Facet } from '../../../src/facetmanagement';
import { BooleanArray2D, Uint8Array2D, Uint32Array2D } from '../../../src/structs/typedarrays';

describe('FacetBuilder', () => {
  let builder: FacetBuilder;

  beforeEach(() => {
    builder = new FacetBuilder();
  });

  describe('calculateBoundingBox', () => {
    it('should calculate bounding box for simple points', () => {
      const points = [
        new Point(5, 10),
        new Point(15, 20),
        new Point(8, 12),
      ];

      const bbox = builder.calculateBoundingBox(points);

      expect(bbox.minX).toBe(5);
      expect(bbox.maxX).toBe(15);
      expect(bbox.minY).toBe(10);
      expect(bbox.maxY).toBe(20);
    });

    it('should handle single point', () => {
      const points = [new Point(7, 9)];
      const bbox = builder.calculateBoundingBox(points);

      expect(bbox.minX).toBe(7);
      expect(bbox.maxX).toBe(7);
      expect(bbox.minY).toBe(9);
      expect(bbox.maxY).toBe(9);
    });

    it('should handle points in a line', () => {
      const points = [
        new Point(0, 5),
        new Point(1, 5),
        new Point(2, 5),
        new Point(3, 5),
      ];

      const bbox = builder.calculateBoundingBox(points);

      expect(bbox.minX).toBe(0);
      expect(bbox.maxX).toBe(3);
      expect(bbox.minY).toBe(5);
      expect(bbox.maxY).toBe(5);
    });

    it('should handle empty point array', () => {
      const bbox = builder.calculateBoundingBox([]);
      expect(bbox).toBeInstanceOf(BoundingBox);
    });

    it('should handle points at (0,0)', () => {
      const points = [
        new Point(0, 0),
        new Point(1, 1),
      ];

      const bbox = builder.calculateBoundingBox(points);

      expect(bbox.minX).toBe(0);
      expect(bbox.minY).toBe(0);
    });

    it('should handle negative coordinates if present', () => {
      const points = [
        new Point(-5, -10),
        new Point(5, 10),
      ];

      const bbox = builder.calculateBoundingBox(points);

      expect(bbox.minX).toBe(-5);
      expect(bbox.maxX).toBe(5);
      expect(bbox.minY).toBe(-10);
      expect(bbox.maxY).toBe(10);
    });
  });

  describe('identifyBorderPoints', () => {
    it('should identify border of single pixel', () => {
      const points = [new Point(5, 5)];
      const border = builder.identifyBorderPoints(points, 10, 10);

      expect(border.length).toBe(1);
      expect(border[0].x).toBe(5);
      expect(border[0].y).toBe(5);
    });

    it('should identify border of 2x2 square', () => {
      const points = [
        new Point(5, 5), new Point(6, 5),
        new Point(5, 6), new Point(6, 6),
      ];

      const border = builder.identifyBorderPoints(points, 10, 10);

      // All 4 points are border points (they all have at least one external neighbor)
      expect(border.length).toBe(4);
    });

    it('should identify border of 3x3 square', () => {
      const points = [
        new Point(5, 5), new Point(6, 5), new Point(7, 5),
        new Point(5, 6), new Point(6, 6), new Point(7, 6),
        new Point(5, 7), new Point(6, 7), new Point(7, 7),
      ];

      const border = builder.identifyBorderPoints(points, 10, 10);

      // Border should be 8 points (excluding center)
      expect(border.length).toBe(8);

      // Center point should not be in border
      const hasCenter = border.some(p => p.x === 6 && p.y === 6);
      expect(hasCenter).toBe(false);
    });

    it('should identify border of horizontal line', () => {
      const points = [
        new Point(3, 5), new Point(4, 5), new Point(5, 5),
      ];

      const border = builder.identifyBorderPoints(points, 10, 10);

      // All points in a line are border points
      expect(border.length).toBe(3);
    });

    it('should identify border of L-shape', () => {
      const points = [
        new Point(5, 5), new Point(6, 5),
        new Point(5, 6),
      ];

      const border = builder.identifyBorderPoints(points, 10, 10);

      // All 3 points should be border points
      expect(border.length).toBe(3);
    });

    it('should mark points at image boundary as border', () => {
      const points = [
        new Point(0, 0), new Point(1, 0), new Point(2, 0),
      ];

      const border = builder.identifyBorderPoints(points, 10, 10);

      // All points on boundary should be border points
      expect(border.length).toBe(3);
    });

    it('should handle points at right/bottom edge', () => {
      const points = [
        new Point(9, 9), // Bottom-right corner
        new Point(8, 9),
        new Point(9, 8),
      ];

      const border = builder.identifyBorderPoints(points, 10, 10);

      // All should be border points (at boundary)
      expect(border.length).toBe(3);
    });

    it('should handle empty point array', () => {
      const border = builder.identifyBorderPoints([], 10, 10);
      expect(border.length).toBe(0);
    });

    it('should handle large square efficiently', () => {
      const points: Point[] = [];

      // Create 10x10 square
      for (let y = 0; y < 10; y++) {
        for (let x = 0; x < 10; x++) {
          points.push(new Point(x, y));
        }
      }

      const start = Date.now();
      const border = builder.identifyBorderPoints(points, 100, 100);
      const duration = Date.now() - start;

      // Border should be outer ring: 10*4 - 4 corners = 36 points
      expect(border.length).toBe(36);
      expect(duration).toBeLessThan(100); // Should be fast
    });
  });

  describe('buildFacet', () => {
    it('should build facet for single pixel', () => {
      const width = 10;
      const height = 10;
      const colorMap = new Uint8Array2D(width, height);
      const visited = new BooleanArray2D(width, height);

      // Set a single pixel with color 1
      colorMap.set(5, 5, 1);

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facet = builder.buildFacet(0, 1, 5, 5, visited, colorMap, facetResult);

      expect(facet.id).toBe(0);
      expect(facet.color).toBe(1);
      expect(facet.pointCount).toBe(1);
      expect(facet.borderPoints.length).toBe(1);
      expect(facet.bbox.minX).toBe(5);
      expect(facet.bbox.maxX).toBe(5);
    });

    it('should build facet for connected region', () => {
      const width = 10;
      const height = 10;
      const colorMap = new Uint8Array2D(width, height);
      const visited = new BooleanArray2D(width, height);

      // Create a 3x3 square of color 1
      for (let y = 4; y <= 6; y++) {
        for (let x = 4; x <= 6; x++) {
          colorMap.set(x, y, 1);
        }
      }

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facet = builder.buildFacet(0, 1, 5, 5, visited, colorMap, facetResult);

      expect(facet.id).toBe(0);
      expect(facet.color).toBe(1);
      expect(facet.pointCount).toBe(9); // 3x3 = 9 pixels
      expect(facet.borderPoints.length).toBe(8); // Outer ring of 3x3
      expect(facet.bbox.minX).toBe(4);
      expect(facet.bbox.maxX).toBe(6);
      expect(facet.bbox.minY).toBe(4);
      expect(facet.bbox.maxY).toBe(6);
    });

    it('should mark visited pixels', () => {
      const width = 5;
      const height = 5;
      const colorMap = new Uint8Array2D(width, height);
      const visited = new BooleanArray2D(width, height);

      // Create horizontal line of color 1
      for (let x = 0; x < 5; x++) {
        colorMap.set(x, 2, 1);
      }

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      builder.buildFacet(0, 1, 2, 2, visited, colorMap, facetResult);

      // Verify all line pixels are marked as visited
      for (let x = 0; x < 5; x++) {
        expect(visited.get(x, 2)).toBe(true);
      }

      // Verify other pixels not visited
      expect(visited.get(0, 0)).toBe(false);
      expect(visited.get(4, 4)).toBe(false);
    });

    it('should update facet map', () => {
      const width = 5;
      const height = 5;
      const colorMap = new Uint8Array2D(width, height);
      const visited = new BooleanArray2D(width, height);

      // Create 2x2 square
      colorMap.set(1, 1, 1);
      colorMap.set(2, 1, 1);
      colorMap.set(1, 2, 1);
      colorMap.set(2, 2, 1);

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      builder.buildFacet(7, 1, 1, 1, visited, colorMap, facetResult);

      // Verify facet map updated with facet index
      expect(facetResult.facetMap.get(1, 1)).toBe(7);
      expect(facetResult.facetMap.get(2, 1)).toBe(7);
      expect(facetResult.facetMap.get(1, 2)).toBe(7);
      expect(facetResult.facetMap.get(2, 2)).toBe(7);
    });

    it('should handle L-shaped region', () => {
      const width = 10;
      const height = 10;
      const colorMap = new Uint8Array2D(width, height);
      const visited = new BooleanArray2D(width, height);

      // Create L-shape
      for (let x = 3; x <= 5; x++) {
        colorMap.set(x, 5, 1); // Horizontal part
      }
      for (let y = 5; y <= 7; y++) {
        colorMap.set(3, y, 1); // Vertical part
      }

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facet = builder.buildFacet(0, 1, 3, 5, visited, colorMap, facetResult);

      expect(facet.pointCount).toBe(5); // 3 horizontal + 2 additional vertical
      expect(facet.borderPoints.length).toBeGreaterThan(0);
    });
  });

  describe('buildAllFacets', () => {
    it('should build facets for simple image', () => {
      const width = 10;
      const height = 10;
      const colorMap = new Uint8Array2D(width, height);

      // Create two regions
      // Region 1: top-left 3x3 with color 1
      for (let y = 0; y < 3; y++) {
        for (let x = 0; x < 3; x++) {
          colorMap.set(x, y, 1);
        }
      }

      // Region 2: bottom-right 3x3 with color 2
      for (let y = 7; y < 10; y++) {
        for (let x = 7; x < 10; x++) {
          colorMap.set(x, y, 2);
        }
      }

      // Rest is color 0
      // (already 0 by default)

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facets = builder.buildAllFacets(colorMap, width, height, facetResult);

      // Should have 3 facets: color 0 (background), color 1, color 2
      expect(facets.length).toBe(3);

      // Find facets by color
      const facet1 = facets.find(f => f.color === 1);
      const facet2 = facets.find(f => f.color === 2);
      const facet0 = facets.find(f => f.color === 0);

      expect(facet1).toBeDefined();
      expect(facet1!.pointCount).toBe(9);

      expect(facet2).toBeDefined();
      expect(facet2!.pointCount).toBe(9);

      expect(facet0).toBeDefined();
      expect(facet0!.pointCount).toBe(82); // 100 - 9 - 9
    });

    it('should assign unique IDs to facets', () => {
      const width = 5;
      const height = 5;
      const colorMap = new Uint8Array2D(width, height);

      // Create checkerboard pattern
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          colorMap.set(x, y, (x + y) % 2);
        }
      }

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facets = builder.buildAllFacets(colorMap, width, height, facetResult);

      // Each facet should have unique ID
      const ids = facets.map(f => f.id);
      const uniqueIds = new Set(ids);

      expect(uniqueIds.size).toBe(facets.length);

      // IDs should be sequential from 0
      for (let i = 0; i < facets.length; i++) {
        expect(ids).toContain(i);
      }
    });

    it('should handle single color image', () => {
      const width = 5;
      const height = 5;
      const colorMap = new Uint8Array2D(width, height);

      // All pixels same color (0 by default)

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facets = builder.buildAllFacets(colorMap, width, height, facetResult);

      expect(facets.length).toBe(1);
      expect(facets[0].pointCount).toBe(25);
      expect(facets[0].color).toBe(0);
    });

    it('should handle image with many small facets', () => {
      const width = 10;
      const height = 10;
      const colorMap = new Uint8Array2D(width, height);

      // Each pixel different "color" (actually just pixel index)
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          colorMap.set(x, y, y * width + x);
        }
      }

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facets = builder.buildAllFacets(colorMap, width, height, facetResult);

      // Should have 100 facets (one per pixel)
      expect(facets.length).toBe(100);

      // Each facet should have 1 pixel
      for (const facet of facets) {
        expect(facet.pointCount).toBe(1);
      }
    });

    it('should populate facet map correctly', () => {
      const width = 10;
      const height = 10;
      const colorMap = new Uint8Array2D(width, height);

      // Create simple two-region image
      for (let x = 0; x < 5; x++) {
        for (let y = 0; y < 10; y++) {
          colorMap.set(x, y, 0); // Left half color 0
        }
      }
      for (let x = 5; x < 10; x++) {
        for (let y = 0; y < 10; y++) {
          colorMap.set(x, y, 1); // Right half color 1
        }
      }

      const facetResult = new FacetResult();
      facetResult.width = width;
      facetResult.height = height;
      facetResult.facetMap = new Uint32Array2D(width, height);
      facetResult.facets = [];

      const facets = builder.buildAllFacets(colorMap, width, height, facetResult);

      expect(facets.length).toBe(2);

      // Verify facet map matches facets
      for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
          const facetIndex = facetResult.facetMap.get(x, y);
          const facet = facets[facetIndex];
          const expectedColor = colorMap.get(x, y);

          expect(facet.color).toBe(expectedColor);
        }
      }
    });
  });
});
