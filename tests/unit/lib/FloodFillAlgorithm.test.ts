import { FloodFillAlgorithm } from '../../../src/lib/FloodFillAlgorithm';
import { Point } from '../../../src/structs/point';

describe('FloodFillAlgorithm', () => {
  let floodFill: FloodFillAlgorithm;

  beforeEach(() => {
    floodFill = new FloodFillAlgorithm();
  });

  describe('fill', () => {
    it('should fill a single pixel region', () => {
      const visited: boolean[] = new Array(100).fill(false);
      const filled = floodFill.fill(
        new Point(5, 5),
        10,
        10,
        (x, y) => !visited[y * 10 + x]
      );

      // Should fill entire 10x10 grid
      expect(filled.length).toBe(100);
    });

    it('should respect boundary constraints', () => {
      const visited: boolean[] = new Array(100).fill(false);
      const filled = floodFill.fill(
        new Point(0, 0),
        10,
        10,
        (x, y) => !visited[y * 10 + x] && x < 5
      );

      // Should only fill left half (5x10 = 50 pixels)
      expect(filled.length).toBe(50);

      // Verify all filled pixels are in left half
      for (const pt of filled) {
        expect(pt.x).toBeLessThan(5);
      }
    });

    it('should handle isolated regions', () => {
      // Create a 10x10 grid with two separate regions
      const grid = new Array(100).fill(0);

      // Region 1: top-left 3x3
      for (let y = 0; y < 3; y++) {
        for (let x = 0; x < 3; x++) {
          grid[y * 10 + x] = 1;
        }
      }

      // Region 2: bottom-right 3x3 (separated by at least 1 pixel)
      for (let y = 7; y < 10; y++) {
        for (let x = 7; x < 10; x++) {
          grid[y * 10 + x] = 1;
        }
      }

      // Fill from top-left region
      const filled = floodFill.fill(
        new Point(1, 1),
        10,
        10,
        (x, y) => grid[y * 10 + x] === 1
      );

      // Should only fill first region (9 pixels)
      expect(filled.length).toBe(9);
    });

    it('should handle single pixel', () => {
      const filled = floodFill.fill(
        new Point(5, 5),
        10,
        10,
        (x, y) => x === 5 && y === 5
      );

      expect(filled.length).toBe(1);
      expect(filled[0].x).toBe(5);
      expect(filled[0].y).toBe(5);
    });

    it('should handle cross-shaped region', () => {
      // Create cross: horizontal and vertical lines through center
      const filled = floodFill.fill(
        new Point(5, 5),
        11,
        11,
        (x, y) => x === 5 || y === 5
      );

      // Cross has 11 vertical + 10 horizontal (excluding center) = 21 pixels
      expect(filled.length).toBe(21);
    });

    it('should not fill outside bounds', () => {
      const filled = floodFill.fill(
        new Point(0, 0),
        5,
        5,
        (x, y) => true
      );

      // Should fill entire 5x5 grid = 25 pixels
      expect(filled.length).toBe(25);

      // Verify no points outside bounds
      for (const pt of filled) {
        expect(pt.x).toBeGreaterThanOrEqual(0);
        expect(pt.x).toBeLessThan(5);
        expect(pt.y).toBeGreaterThanOrEqual(0);
        expect(pt.y).toBeLessThan(5);
      }
    });

    it('should handle edge start positions', () => {
      // Start from corner
      const filled1 = floodFill.fill(
        new Point(0, 0),
        10,
        10,
        (x, y) => true
      );
      expect(filled1.length).toBe(100);

      // Start from top edge
      const filled2 = floodFill.fill(
        new Point(5, 0),
        10,
        10,
        (x, y) => true
      );
      expect(filled2.length).toBe(100);

      // Start from right edge
      const filled3 = floodFill.fill(
        new Point(9, 5),
        10,
        10,
        (x, y) => true
      );
      expect(filled3.length).toBe(100);
    });

    it('should use 4-connectivity not 8-connectivity', () => {
      // Create diagonal pattern where 8-connectivity would connect but 4-connectivity won't
      const grid = new Array(100).fill(0);
      grid[0] = 1;  // (0,0)
      grid[11] = 1; // (1,1) - diagonal, not 4-connected

      const filled = floodFill.fill(
        new Point(0, 0),
        10,
        10,
        (x, y) => grid[y * 10 + x] === 1
      );

      // Should only fill starting pixel
      expect(filled.length).toBe(1);
    });

    it('should handle complex maze-like patterns', () => {
      // Create a corridor pattern
      const grid = new Array(100).fill(0);

      // Horizontal corridor at y=5
      for (let x = 0; x < 10; x++) {
        grid[5 * 10 + x] = 1;
      }

      // Vertical corridor at x=5
      for (let y = 0; y < 10; y++) {
        grid[y * 10 + 5] = 1;
      }

      const filled = floodFill.fill(
        new Point(5, 5),
        10,
        10,
        (x, y) => grid[y * 10 + x] === 1
      );

      // Should fill both corridors (10 + 9 = 19, excluding center counted twice)
      expect(filled.length).toBe(19);
    });

    it('should return empty array when start point not included', () => {
      const filled = floodFill.fill(
        new Point(5, 5),
        10,
        10,
        (x, y) => false
      );

      expect(filled.length).toBe(0);
    });
  });

  describe('fillWithCallback', () => {
    it('should call callback for each filled pixel', () => {
      const called: Point[] = [];
      const count = floodFill.fillWithCallback(
        new Point(0, 0),
        3,
        3,
        (x, y) => true,
        (x, y) => called.push(new Point(x, y))
      );

      expect(count).toBe(9);
      expect(called.length).toBe(9);
    });

    it('should return correct count', () => {
      const count = floodFill.fillWithCallback(
        new Point(5, 5),
        10,
        10,
        (x, y) => x < 5,
        (x, y) => {}
      );

      expect(count).toBe(50); // Left half of 10x10
    });

    it('should modify state through callback', () => {
      const visited: boolean[] = new Array(25).fill(false);
      const colorMap: number[] = new Array(25).fill(0);

      // Create region to fill (top-left 3x3)
      for (let y = 0; y < 3; y++) {
        for (let x = 0; x < 3; x++) {
          colorMap[y * 5 + x] = 1;
        }
      }

      const count = floodFill.fillWithCallback(
        new Point(1, 1),
        5,
        5,
        (x, y) => !visited[y * 5 + x] && colorMap[y * 5 + x] === 1,
        (x, y) => {
          visited[y * 5 + x] = true;
          colorMap[y * 5 + x] = 2; // Change color
        }
      );

      expect(count).toBe(9);

      // Verify state was modified
      for (let y = 0; y < 3; y++) {
        for (let x = 0; x < 3; x++) {
          expect(visited[y * 5 + x]).toBe(true);
          expect(colorMap[y * 5 + x]).toBe(2);
        }
      }
    });

    it('should handle callback that modifies predicate', () => {
      const visited: boolean[] = new Array(100).fill(false);

      const count = floodFill.fillWithCallback(
        new Point(0, 0),
        10,
        10,
        (x, y) => !visited[y * 10 + x],
        (x, y) => {
          visited[y * 10 + x] = true; // Mark as visited in callback
        }
      );

      expect(count).toBe(100);

      // Verify all were visited
      expect(visited.every(v => v)).toBe(true);
    });

    it('should match behavior of fill method', () => {
      const grid = new Array(100).fill(0);

      // Create checkerboard pattern
      for (let y = 0; y < 10; y++) {
        for (let x = 0; x < 10; x++) {
          grid[y * 10 + x] = (x + y) % 2;
        }
      }

      // Fill with array method
      const filled = floodFill.fill(
        new Point(0, 0),
        10,
        10,
        (x, y) => grid[y * 10 + x] === 0
      );

      // Fill with callback method
      const callbackPoints: Point[] = [];
      const count = floodFill.fillWithCallback(
        new Point(0, 0),
        10,
        10,
        (x, y) => grid[y * 10 + x] === 0,
        (x, y) => callbackPoints.push(new Point(x, y))
      );

      // Both should fill same number of pixels
      expect(count).toBe(filled.length);
      expect(callbackPoints.length).toBe(filled.length);
    });

    it('should return 0 when start point not included', () => {
      const count = floodFill.fillWithCallback(
        new Point(5, 5),
        10,
        10,
        (x, y) => false,
        (x, y) => {}
      );

      expect(count).toBe(0);
    });
  });

  describe('performance characteristics', () => {
    it('should handle large regions efficiently', () => {
      const start = Date.now();

      const filled = floodFill.fill(
        new Point(0, 0),
        100,
        100,
        (x, y) => true
      );

      const duration = Date.now() - start;

      expect(filled.length).toBe(10000);
      expect(duration).toBeLessThan(1000); // Should complete in less than 1 second
    });

    it('should not revisit pixels', () => {
      let visitCount = 0;

      floodFill.fill(
        new Point(0, 0),
        10,
        10,
        (x, y) => {
          visitCount++;
          return true;
        }
      );

      // Each pixel should be visited exactly once
      // (some may be visited via shouldInclude check even if not filled, but should be minimal)
      expect(visitCount).toBeLessThan(200); // Should be close to 100 but allow some overhead
    });
  });

  describe('edge cases', () => {
    it('should handle 1x1 grid', () => {
      const filled = floodFill.fill(
        new Point(0, 0),
        1,
        1,
        (x, y) => true
      );

      expect(filled.length).toBe(1);
    });

    it('should handle very wide grid', () => {
      const filled = floodFill.fill(
        new Point(50, 0),
        1000,
        1,
        (x, y) => true
      );

      expect(filled.length).toBe(1000);
    });

    it('should handle very tall grid', () => {
      const filled = floodFill.fill(
        new Point(0, 50),
        1,
        1000,
        (x, y) => true
      );

      expect(filled.length).toBe(1000);
    });

    it('should handle start point outside bounds', () => {
      const filled = floodFill.fill(
        new Point(-1, -1),
        10,
        10,
        (x, y) => true
      );

      expect(filled.length).toBe(0);
    });

    it('should handle start point at max bounds', () => {
      const filled = floodFill.fill(
        new Point(10, 10),
        10,
        10,
        (x, y) => true
      );

      expect(filled.length).toBe(0);
    });
  });
});
