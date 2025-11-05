/**
 * K-means clustering algorithm implementation
 *
 * Provides K-means clustering for color quantization and general vector clustering.
 * Uses Lloyd's algorithm with random initialization.
 *
 * @module clustering
 */

import { Random } from "../random";
import { Vector } from "./Vector";

// Re-export Vector for backward compatibility
export { Vector } from "./Vector";

/**
 * K-means clustering algorithm
 *
 * Implements the standard K-means algorithm (Lloyd's algorithm) for clustering
 * vectors into k groups. Commonly used for color quantization in the paint-by-numbers
 * generation process.
 *
 * @example
 * ```typescript
 * const random = new Random(42);
 * const points = [
 *   new Vector([255, 0, 0]),    // Red
 *   new Vector([0, 255, 0]),    // Green
 *   new Vector([0, 0, 255]),    // Blue
 * ];
 *
 * const kmeans = new KMeans(points, 3, random);
 * while (kmeans.currentDeltaDistanceDifference > 1) {
 *   kmeans.step();
 * }
 * console.log(`Converged in ${kmeans.currentIteration} iterations`);
 * ```
 */
export class KMeans {
  /** Current iteration count */
  public currentIteration: number = 0;

  /** Vectors assigned to each cluster (indexed by cluster) */
  public pointsPerCategory: Vector[][] = [];

  /** Current cluster centroids */
  public centroids: Vector[] = [];

  /** Sum of distances that centroids moved in last step */
  public currentDeltaDistanceDifference: number = 0;

  /**
   * Create a new K-means clustering instance
   *
   * @param points - Data points to cluster
   * @param k - Number of clusters
   * @param random - Random number generator (for deterministic results)
   * @param centroids - Optional initial centroids (if null, random initialization is used)
   *
   * @example
   * ```typescript
   * const random = new Random(42);  // Fixed seed for reproducibility
   * const data = [new Vector([1, 2]), new Vector([3, 4])];
   * const kmeans = new KMeans(data, 2, random);
   * ```
   */
  constructor(
    private points: Vector[],
    public k: number,
    private random: Random,
    centroids: Vector[] | null = null
  ) {
    if (centroids != null) {
      // Use provided centroids
      this.centroids = centroids;
      for (let i = 0; i < this.k; i++) {
        this.pointsPerCategory.push([]);
      }
    } else {
      // Random initialization
      this.initCentroids();
    }
  }

  /**
   * Initialize centroids by randomly selecting from data points
   *
   * @private
   */
  private initCentroids(): void {
    for (let i = 0; i < this.k; i++) {
      // Select random point as initial centroid
      const randomIndex = Math.floor(this.points.length * this.random.next());
      this.centroids.push(this.points[randomIndex]);
      this.pointsPerCategory.push([]);
    }
  }

  /**
   * Perform one iteration of the K-means algorithm
   *
   * Steps:
   * 1. Assign each point to nearest centroid (assignment step)
   * 2. Recalculate centroids as mean of assigned points (update step)
   * 3. Calculate how much centroids moved (for convergence detection)
   *
   * @example
   * ```typescript
   * const kmeans = new KMeans(data, 3, random);
   *
   * // Run until convergence
   * while (kmeans.currentDeltaDistanceDifference > 0.1 &&
   *        kmeans.currentIteration < 100) {
   *   kmeans.step();
   * }
   * ```
   */
  public step(): void {
    // Clear previous assignments
    for (let i = 0; i < this.k; i++) {
      this.pointsPerCategory[i] = [];
    }

    // Assignment step: assign each point to nearest centroid
    for (const point of this.points) {
      let minDistance = Number.MAX_VALUE;
      let nearestCentroidIndex = -1;

      for (let k = 0; k < this.k; k++) {
        const distance = this.centroids[k].distanceTo(point);
        if (distance < minDistance) {
          nearestCentroidIndex = k;
          minDistance = distance;
        }
      }

      this.pointsPerCategory[nearestCentroidIndex].push(point);
    }

    // Update step: recalculate centroids
    let totalDistanceMoved = 0;

    for (let k = 0; k < this.pointsPerCategory.length; k++) {
      const cluster = this.pointsPerCategory[k];

      if (cluster.length > 0) {
        // Calculate new centroid as weighted average
        const newCentroid = Vector.average(cluster);

        // Track how much this centroid moved
        const distanceMoved = this.centroids[k].distanceTo(newCentroid);
        totalDistanceMoved += distanceMoved;

        // Update centroid
        this.centroids[k] = newCentroid;
      }
    }

    this.currentDeltaDistanceDifference = totalDistanceMoved;
    this.currentIteration++;
  }

  /**
   * Get the cluster index for a given point
   *
   * @param point - Point to classify
   * @returns Index of nearest cluster (0 to k-1)
   */
  public classify(point: Vector): number {
    let minDistance = Number.MAX_VALUE;
    let nearestIndex = 0;

    for (let k = 0; k < this.k; k++) {
      const distance = this.centroids[k].distanceTo(point);
      if (distance < minDistance) {
        nearestIndex = k;
        minDistance = distance;
      }
    }

    return nearestIndex;
  }

  /**
   * Check if algorithm has converged
   *
   * @param threshold - Maximum allowed centroid movement
   * @returns true if converged (movement below threshold)
   */
  public hasConverged(threshold: number): boolean {
    return this.currentDeltaDistanceDifference <= threshold;
  }
}
