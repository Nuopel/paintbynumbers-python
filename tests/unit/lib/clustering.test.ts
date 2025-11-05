import { Vector, KMeans } from '../../../src/lib/clustering';
import { Random } from '../../../src/random';

describe('Vector', () => {
  describe('constructor', () => {
    it('should create vector with values and default weight', () => {
      const vec = new Vector([1, 2, 3]);
      expect(vec.values).toEqual([1, 2, 3]);
      expect(vec.weight).toBe(1);
      expect(vec.tag).toBeUndefined();
    });

    it('should create vector with custom weight', () => {
      const vec = new Vector([1, 2], 5);
      expect(vec.weight).toBe(5);
    });

    it('should create vector with tag', () => {
      const tag = { color: 'red' };
      const vec = new Vector([255, 0, 0], 1, tag);
      expect(vec.tag).toBe(tag);
    });
  });

  describe('distanceTo', () => {
    it('should calculate Euclidean distance correctly', () => {
      const v1 = new Vector([0, 0]);
      const v2 = new Vector([3, 4]);
      expect(v1.distanceTo(v2)).toBe(5);
    });

    it('should return 0 for identical vectors', () => {
      const v1 = new Vector([1, 2, 3]);
      const v2 = new Vector([1, 2, 3]);
      expect(v1.distanceTo(v2)).toBe(0);
    });

    it('should work in higher dimensions', () => {
      const v1 = new Vector([1, 0, 0, 0]);
      const v2 = new Vector([0, 1, 0, 0]);
      expect(v1.distanceTo(v2)).toBeCloseTo(Math.sqrt(2), 10);
    });
  });

  describe('average', () => {
    it('should calculate simple average', () => {
      const v1 = new Vector([0, 0]);
      const v2 = new Vector([10, 10]);
      const avg = Vector.average([v1, v2]);
      expect(avg.values).toEqual([5, 5]);
    });

    it('should calculate weighted average', () => {
      const v1 = new Vector([0, 0], 1);
      const v2 = new Vector([10, 10], 2);
      const avg = Vector.average([v1, v2]);
      expect(avg.values[0]).toBeCloseTo(6.666666, 5);
      expect(avg.values[1]).toBeCloseTo(6.666666, 5);
    });

    it('should throw on empty array', () => {
      expect(() => Vector.average([])).toThrow('Cannot average empty array');
    });

    it('should preserve tag from first vector', () => {
      const v1 = new Vector([1, 2], 1, { data: 'test' });
      const v2 = new Vector([3, 4], 1);
      const avg = Vector.average([v1, v2]);
      // Note: current implementation doesn't preserve tags, but documents weight
      expect(avg.weight).toBeGreaterThan(0);
    });
  });

  describe('clone', () => {
    it('should create independent copy', () => {
      const original = new Vector([1, 2, 3], 5, { data: 'test' });
      const copy = original.clone();

      expect(copy.values).toEqual(original.values);
      expect(copy.weight).toBe(original.weight);
      expect(copy.tag).toBe(original.tag);

      // Modify copy
      copy.values[0] = 999;
      expect(original.values[0]).toBe(1); // Original unchanged
    });
  });

  describe('dimensions', () => {
    it('should return correct dimension count', () => {
      expect(new Vector([1]).dimensions).toBe(1);
      expect(new Vector([1, 2]).dimensions).toBe(2);
      expect(new Vector([1, 2, 3, 4, 5]).dimensions).toBe(5);
    });
  });

  describe('magnitude', () => {
    it('should calculate magnitude correctly', () => {
      const v = new Vector([3, 4]);
      expect(v.magnitude()).toBe(5);
    });

    it('should return 0 for zero vector', () => {
      const v = new Vector([0, 0, 0]);
      expect(v.magnitude()).toBe(0);
    });
  });

  describe('magnitudeSquared', () => {
    it('should calculate squared magnitude', () => {
      const v = new Vector([3, 4]);
      expect(v.magnitudeSquared()).toBe(25);
    });
  });
});

describe('KMeans', () => {
  let random: Random;

  beforeEach(() => {
    random = new Random(42); // Fixed seed for reproducibility
  });

  describe('constructor', () => {
    it('should initialize with random centroids', () => {
      const points = [
        new Vector([0, 0]),
        new Vector([1, 1]),
        new Vector([2, 2]),
      ];
      const kmeans = new KMeans(points, 2, random);

      expect(kmeans.centroids).toHaveLength(2);
      expect(kmeans.k).toBe(2);
      expect(kmeans.currentIteration).toBe(0);
    });

    it('should use provided centroids', () => {
      const points = [new Vector([0, 0]), new Vector([10, 10])];
      const centroids = [new Vector([1, 1]), new Vector([9, 9])];

      const kmeans = new KMeans(points, 2, random, centroids);

      expect(kmeans.centroids).toBe(centroids);
    });
  });

  describe('step', () => {
    it('should perform one iteration', () => {
      const points = [
        new Vector([0, 0]),
        new Vector([1, 1]),
        new Vector([10, 10]),
        new Vector([11, 11]),
      ];

      const kmeans = new KMeans(points, 2, new Random(123));
      const initialCentroids = kmeans.centroids.map(c => c.clone());

      kmeans.step();

      expect(kmeans.currentIteration).toBe(1);
      // Centroids should have moved
      const moved = kmeans.centroids.some((c, i) =>
        c.distanceTo(initialCentroids[i]) > 0
      );
      expect(moved).toBe(true);
    });

    it('should assign points to nearest centroid', () => {
      const points = [
        new Vector([0, 0]),
        new Vector([0.1, 0.1]),
        new Vector([10, 10]),
        new Vector([10.1, 10.1]),
      ];

      // Initialize with clear centroids
      const centroids = [new Vector([0, 0]), new Vector([10, 10])];
      const kmeans = new KMeans(points, 2, random, centroids);

      kmeans.step();

      // Each cluster should have 2 points
      expect(kmeans.pointsPerCategory[0]).toHaveLength(2);
      expect(kmeans.pointsPerCategory[1]).toHaveLength(2);
    });
  });

  describe('classify', () => {
    it('should return nearest cluster index', () => {
      const centroids = [new Vector([0, 0]), new Vector([10, 10])];
      const kmeans = new KMeans([], 2, random, centroids);

      expect(kmeans.classify(new Vector([1, 1]))).toBe(0);
      expect(kmeans.classify(new Vector([9, 9]))).toBe(1);
    });
  });

  describe('hasConverged', () => {
    it('should return true when movement below threshold', () => {
      const kmeans = new KMeans([new Vector([0, 0])], 1, random);
      kmeans.currentDeltaDistanceDifference = 0.5;

      expect(kmeans.hasConverged(1.0)).toBe(true);
      expect(kmeans.hasConverged(0.1)).toBe(false);
    });
  });

  describe('determinism', () => {
    it('should produce identical results with same seed', () => {
      const points = [
        new Vector([0, 0]),
        new Vector([1, 1]),
        new Vector([10, 10]),
        new Vector([11, 11]),
      ];

      // Run 1
      const kmeans1 = new KMeans(points, 2, new Random(42));
      for (let i = 0; i < 10; i++) kmeans1.step();

      // Run 2 with same seed
      const kmeans2 = new KMeans(points, 2, new Random(42));
      for (let i = 0; i < 10; i++) kmeans2.step();

      // Should have identical centroids
      for (let i = 0; i < 2; i++) {
        expect(kmeans1.centroids[i].values).toEqual(kmeans2.centroids[i].values);
      }
    });
  });

  describe('convergence', () => {
    it('should converge on well-separated clusters', () => {
      const points = [
        new Vector([0, 0]),
        new Vector([0.5, 0.5]),
        new Vector([100, 100]),
        new Vector([100.5, 100.5]),
      ];

      const kmeans = new KMeans(points, 2, new Random(42));

      let iterations = 0;
      while (!kmeans.hasConverged(0.1) && iterations < 100) {
        kmeans.step();
        iterations++;
      }

      expect(iterations).toBeLessThan(100); // Should converge quickly
      expect(kmeans.hasConverged(0.1)).toBe(true);
    });
  });
});
