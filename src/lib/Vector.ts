/**
 * Vector class for K-means clustering
 *
 * Represents a point in n-dimensional space with optional weight and metadata.
 * Used primarily for color clustering in RGB/HSL/LAB color spaces.
 *
 * @module Vector
 */

/**
 * A vector in n-dimensional space with weight and optional metadata
 */
export class Vector {
  /** The dimensional values of this vector */
  public values: number[];

  /** Weight of this vector (for weighted averaging) */
  public weight: number;

  /** Optional metadata tag (e.g., original RGB color) */
  public tag?: any;

  /**
   * Create a new vector
   *
   * @param values - Array of dimensional values
   * @param weight - Weight for weighted operations (default: 1)
   * @param tag - Optional metadata tag
   *
   * @example
   * ```typescript
   * // Create RGB color vector
   * const colorVec = new Vector([255, 128, 0], 1, { r: 255, g: 128, b: 0 });
   *
   * // Create weighted point
   * const weightedVec = new Vector([1, 2, 3], 5);
   * ```
   */
  constructor(values: number[], weight: number = 1, tag?: any) {
    this.values = values;
    this.weight = weight;
    this.tag = tag;
  }

  /**
   * Calculate Euclidean distance to another vector
   *
   * @param other - Vector to calculate distance to
   * @returns Euclidean distance between vectors
   *
   * @example
   * ```typescript
   * const v1 = new Vector([0, 0]);
   * const v2 = new Vector([3, 4]);
   * const dist = v1.distanceTo(v2); // Returns 5
   * ```
   */
  public distanceTo(other: Vector): number {
    let sumSquares = 0;
    for (let i = 0; i < this.values.length; i++) {
      const diff = other.values[i] - this.values[i];
      sumSquares += diff * diff;
    }
    return Math.sqrt(sumSquares);
  }

  /**
   * Calculate weighted average of multiple vectors
   *
   * Computes the centroid of a set of vectors, taking their weights into account.
   *
   * @param vectors - Array of vectors to average
   * @returns New vector representing the weighted average
   * @throws Error if vectors array is empty
   *
   * @example
   * ```typescript
   * const v1 = new Vector([0, 0], 1);
   * const v2 = new Vector([10, 10], 2);
   * const avg = Vector.average([v1, v2]);
   * // Returns approximately Vector([6.67, 6.67])
   * ```
   */
  public static average(vectors: Vector[]): Vector {
    if (vectors.length === 0) {
      throw new Error("Cannot average empty array of vectors");
    }

    const dims = vectors[0].values.length;
    const values: number[] = new Array(dims).fill(0);

    let weightSum = 0;
    for (const vec of vectors) {
      weightSum += vec.weight;
      for (let i = 0; i < dims; i++) {
        values[i] += vec.weight * vec.values[i];
      }
    }

    // Normalize by total weight
    for (let i = 0; i < values.length; i++) {
      values[i] /= weightSum;
    }

    return new Vector(values, weightSum);
  }

  /**
   * Create a deep clone of this vector
   *
   * @returns New vector with copied values
   *
   * @example
   * ```typescript
   * const original = new Vector([1, 2, 3], 5, { data: 'test' });
   * const copy = original.clone();
   * copy.values[0] = 999; // Original unchanged
   * ```
   */
  public clone(): Vector {
    return new Vector([...this.values], this.weight, this.tag);
  }

  /**
   * Get the dimensionality of this vector
   *
   * @returns Number of dimensions
   */
  public get dimensions(): number {
    return this.values.length;
  }

  /**
   * Get the squared magnitude of this vector
   *
   * @returns Sum of squared values
   *
   * @example
   * ```typescript
   * const v = new Vector([3, 4]);
   * const magSq = v.magnitudeSquared(); // Returns 25
   * ```
   */
  public magnitudeSquared(): number {
    let sum = 0;
    for (let i = 0; i < this.values.length; i++) {
      sum += this.values[i] * this.values[i];
    }
    return sum;
  }

  /**
   * Get the magnitude (length) of this vector
   *
   * @returns Euclidean length of the vector
   *
   * @example
   * ```typescript
   * const v = new Vector([3, 4]);
   * const mag = v.magnitude(); // Returns 5
   * ```
   */
  public magnitude(): number {
    return Math.sqrt(this.magnitudeSquared());
  }
}
