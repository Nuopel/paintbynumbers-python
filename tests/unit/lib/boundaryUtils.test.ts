import {
  isInBounds,
  clamp,
  clampPoint,
  getNeighbors4,
  getNeighbors8,
  isOnEdge,
  getEdgeType,
  EdgeType,
} from '../../../src/lib/boundaryUtils';
import { Point } from '../../../src/structs/point';

describe('boundaryUtils', () => {
  describe('isInBounds', () => {
    it('should return true for valid point', () => {
      expect(isInBounds(5, 5, 10, 10)).toBe(true);
    });

    it('should return false for x < 0', () => {
      expect(isInBounds(-1, 5, 10, 10)).toBe(false);
    });

    it('should return false for x >= width', () => {
      expect(isInBounds(10, 5, 10, 10)).toBe(false);
    });

    it('should return false for y < 0', () => {
      expect(isInBounds(5, -1, 10, 10)).toBe(false);
    });

    it('should return false for y >= height', () => {
      expect(isInBounds(5, 10, 10, 10)).toBe(false);
    });

    it('should accept point at (0,0)', () => {
      expect(isInBounds(0, 0, 10, 10)).toBe(true);
    });

    it('should accept point at (width-1, height-1)', () => {
      expect(isInBounds(9, 9, 10, 10)).toBe(true);
    });

    it('should handle 1x1 image', () => {
      expect(isInBounds(0, 0, 1, 1)).toBe(true);
      expect(isInBounds(1, 0, 1, 1)).toBe(false);
      expect(isInBounds(0, 1, 1, 1)).toBe(false);
    });
  });

  describe('clamp', () => {
    it('should return value if in range', () => {
      expect(clamp(5, 0, 10)).toBe(5);
    });

    it('should return min if value below', () => {
      expect(clamp(-5, 0, 10)).toBe(0);
    });

    it('should return max if value above', () => {
      expect(clamp(15, 0, 10)).toBe(10);
    });

    it('should handle value equal to min', () => {
      expect(clamp(0, 0, 10)).toBe(0);
    });

    it('should handle value equal to max', () => {
      expect(clamp(10, 0, 10)).toBe(10);
    });

    it('should handle negative ranges', () => {
      expect(clamp(-5, -10, -1)).toBe(-5);
      expect(clamp(-15, -10, -1)).toBe(-10);
      expect(clamp(0, -10, -1)).toBe(-1);
    });
  });

  describe('clampPoint', () => {
    it('should not modify point within bounds', () => {
      const pt = new Point(5, 5);
      const clamped = clampPoint(pt, 10, 10);
      expect(clamped.x).toBe(5);
      expect(clamped.y).toBe(5);
    });

    it('should clamp negative x', () => {
      const pt = new Point(-5, 5);
      const clamped = clampPoint(pt, 10, 10);
      expect(clamped.x).toBe(0);
      expect(clamped.y).toBe(5);
    });

    it('should clamp excessive x', () => {
      const pt = new Point(100, 5);
      const clamped = clampPoint(pt, 10, 10);
      expect(clamped.x).toBe(9);
      expect(clamped.y).toBe(5);
    });

    it('should clamp negative y', () => {
      const pt = new Point(5, -5);
      const clamped = clampPoint(pt, 10, 10);
      expect(clamped.x).toBe(5);
      expect(clamped.y).toBe(0);
    });

    it('should clamp excessive y', () => {
      const pt = new Point(5, 100);
      const clamped = clampPoint(pt, 10, 10);
      expect(clamped.x).toBe(5);
      expect(clamped.y).toBe(9);
    });

    it('should clamp both coordinates', () => {
      const pt = new Point(-5, 100);
      const clamped = clampPoint(pt, 10, 10);
      expect(clamped.x).toBe(0);
      expect(clamped.y).toBe(9);
    });
  });

  describe('getNeighbors4', () => {
    it('should return 4 neighbors for center point', () => {
      const neighbors = getNeighbors4(5, 5, 10, 10);
      expect(neighbors).toHaveLength(4);
      expect(neighbors.some(n => n.x === 5 && n.y === 4)).toBe(true); // up
      expect(neighbors.some(n => n.x === 5 && n.y === 6)).toBe(true); // down
      expect(neighbors.some(n => n.x === 4 && n.y === 5)).toBe(true); // left
      expect(neighbors.some(n => n.x === 6 && n.y === 5)).toBe(true); // right
    });

    it('should return 2 neighbors for corner (0,0)', () => {
      const neighbors = getNeighbors4(0, 0, 10, 10);
      expect(neighbors).toHaveLength(2);
      expect(neighbors.some(n => n.x === 1 && n.y === 0)).toBe(true); // right
      expect(neighbors.some(n => n.x === 0 && n.y === 1)).toBe(true); // down
    });

    it('should return 2 neighbors for corner (9,9)', () => {
      const neighbors = getNeighbors4(9, 9, 10, 10);
      expect(neighbors).toHaveLength(2);
      expect(neighbors.some(n => n.x === 8 && n.y === 9)).toBe(true); // left
      expect(neighbors.some(n => n.x === 9 && n.y === 8)).toBe(true); // up
    });

    it('should return 3 neighbors for left edge point', () => {
      const neighbors = getNeighbors4(0, 5, 10, 10);
      expect(neighbors).toHaveLength(3);
      // Should have up, down, right (no left)
      expect(neighbors.some(n => n.x === 0 && n.y === 4)).toBe(true);
      expect(neighbors.some(n => n.x === 0 && n.y === 6)).toBe(true);
      expect(neighbors.some(n => n.x === 1 && n.y === 5)).toBe(true);
    });

    it('should handle 1x1 image', () => {
      const neighbors = getNeighbors4(0, 0, 1, 1);
      expect(neighbors).toHaveLength(0);
    });

    it('should handle 2x1 image', () => {
      const neighbors = getNeighbors4(0, 0, 2, 1);
      expect(neighbors).toHaveLength(1);
      expect(neighbors[0].x).toBe(1);
      expect(neighbors[0].y).toBe(0);
    });
  });

  describe('getNeighbors8', () => {
    it('should return 8 neighbors for center point', () => {
      const neighbors = getNeighbors8(5, 5, 10, 10);
      expect(neighbors).toHaveLength(8);
    });

    it('should return 3 neighbors for corner (0,0)', () => {
      const neighbors = getNeighbors8(0, 0, 10, 10);
      expect(neighbors).toHaveLength(3);
      expect(neighbors.some(n => n.x === 1 && n.y === 0)).toBe(true); // right
      expect(neighbors.some(n => n.x === 0 && n.y === 1)).toBe(true); // down
      expect(neighbors.some(n => n.x === 1 && n.y === 1)).toBe(true); // diagonal
    });

    it('should return 5 neighbors for edge point', () => {
      const neighbors = getNeighbors8(5, 0, 10, 10);
      expect(neighbors).toHaveLength(5);
    });

    it('should not include center point', () => {
      const neighbors = getNeighbors8(5, 5, 10, 10);
      expect(neighbors.some(n => n.x === 5 && n.y === 5)).toBe(false);
    });

    it('should include all diagonal neighbors for center', () => {
      const neighbors = getNeighbors8(5, 5, 10, 10);
      expect(neighbors.some(n => n.x === 4 && n.y === 4)).toBe(true); // NW
      expect(neighbors.some(n => n.x === 6 && n.y === 4)).toBe(true); // NE
      expect(neighbors.some(n => n.x === 4 && n.y === 6)).toBe(true); // SW
      expect(neighbors.some(n => n.x === 6 && n.y === 6)).toBe(true); // SE
    });

    it('should handle 1x1 image', () => {
      const neighbors = getNeighbors8(0, 0, 1, 1);
      expect(neighbors).toHaveLength(0);
    });
  });

  describe('isOnEdge', () => {
    it('should return false for center point', () => {
      expect(isOnEdge(5, 5, 10, 10)).toBe(false);
    });

    it('should return true for left edge', () => {
      expect(isOnEdge(0, 5, 10, 10)).toBe(true);
    });

    it('should return true for right edge', () => {
      expect(isOnEdge(9, 5, 10, 10)).toBe(true);
    });

    it('should return true for top edge', () => {
      expect(isOnEdge(5, 0, 10, 10)).toBe(true);
    });

    it('should return true for bottom edge', () => {
      expect(isOnEdge(5, 9, 10, 10)).toBe(true);
    });

    it('should return true for all corners', () => {
      expect(isOnEdge(0, 0, 10, 10)).toBe(true);
      expect(isOnEdge(9, 0, 10, 10)).toBe(true);
      expect(isOnEdge(0, 9, 10, 10)).toBe(true);
      expect(isOnEdge(9, 9, 10, 10)).toBe(true);
    });

    it('should handle 1x1 image', () => {
      expect(isOnEdge(0, 0, 1, 1)).toBe(true);
    });
  });

  describe('getEdgeType', () => {
    it('should return None for center', () => {
      expect(getEdgeType(5, 5, 10, 10)).toBe(EdgeType.None);
    });

    it('should return Left for left edge', () => {
      const edge = getEdgeType(0, 5, 10, 10);
      expect(edge & EdgeType.Left).toBeTruthy();
      expect(edge & EdgeType.Right).toBeFalsy();
      expect(edge & EdgeType.Top).toBeFalsy();
      expect(edge & EdgeType.Bottom).toBeFalsy();
    });

    it('should return Right for right edge', () => {
      const edge = getEdgeType(9, 5, 10, 10);
      expect(edge & EdgeType.Right).toBeTruthy();
      expect(edge & EdgeType.Left).toBeFalsy();
    });

    it('should return Top for top edge', () => {
      const edge = getEdgeType(5, 0, 10, 10);
      expect(edge & EdgeType.Top).toBeTruthy();
      expect(edge & EdgeType.Bottom).toBeFalsy();
    });

    it('should return Bottom for bottom edge', () => {
      const edge = getEdgeType(5, 9, 10, 10);
      expect(edge & EdgeType.Bottom).toBeTruthy();
      expect(edge & EdgeType.Top).toBeFalsy();
    });

    it('should return Top|Left for top-left corner', () => {
      const edge = getEdgeType(0, 0, 10, 10);
      expect(edge & EdgeType.Top).toBeTruthy();
      expect(edge & EdgeType.Left).toBeTruthy();
      expect(edge & EdgeType.Right).toBeFalsy();
      expect(edge & EdgeType.Bottom).toBeFalsy();
    });

    it('should return Top|Right for top-right corner', () => {
      const edge = getEdgeType(9, 0, 10, 10);
      expect(edge & EdgeType.Top).toBeTruthy();
      expect(edge & EdgeType.Right).toBeTruthy();
      expect(edge & EdgeType.Left).toBeFalsy();
      expect(edge & EdgeType.Bottom).toBeFalsy();
    });

    it('should return Bottom|Left for bottom-left corner', () => {
      const edge = getEdgeType(0, 9, 10, 10);
      expect(edge & EdgeType.Bottom).toBeTruthy();
      expect(edge & EdgeType.Left).toBeTruthy();
      expect(edge & EdgeType.Right).toBeFalsy();
      expect(edge & EdgeType.Top).toBeFalsy();
    });

    it('should return Bottom|Right for bottom-right corner', () => {
      const edge = getEdgeType(9, 9, 10, 10);
      expect(edge & EdgeType.Bottom).toBeTruthy();
      expect(edge & EdgeType.Right).toBeTruthy();
      expect(edge & EdgeType.Left).toBeFalsy();
      expect(edge & EdgeType.Top).toBeFalsy();
    });

    it('should handle 1x1 image (all edges)', () => {
      const edge = getEdgeType(0, 0, 1, 1);
      expect(edge & EdgeType.Top).toBeTruthy();
      expect(edge & EdgeType.Bottom).toBeTruthy();
      expect(edge & EdgeType.Left).toBeTruthy();
      expect(edge & EdgeType.Right).toBeTruthy();
    });
  });

  describe('Edge case scenarios', () => {
    it('should handle very large coordinates', () => {
      expect(isInBounds(1000000, 1000000, 2000000, 2000000)).toBe(true);
      expect(isInBounds(2000000, 1000000, 2000000, 2000000)).toBe(false);
    });

    it('should handle zero-sized images gracefully', () => {
      expect(isInBounds(0, 0, 0, 0)).toBe(false);
      expect(getNeighbors4(0, 0, 0, 0)).toHaveLength(0);
      expect(getNeighbors8(0, 0, 0, 0)).toHaveLength(0);
    });
  });
});
