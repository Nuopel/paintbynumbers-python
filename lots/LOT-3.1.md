# LOT 3.1: K-Means Clustering Refactor

**Phase:** 3 - Core Algorithm Refactoring
**Estimated Time:** 6 hours
**Priority:** HIGH
**Dependencies:** LOT 2.3 (Color Space Utilities)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Refactor K-means clustering implementation to be more modular, maintainable, and extensible while maintaining identical output for deterministic inputs.

---

## 📋 Context

**Current State:**
- K-means clustering in `src/lib/clustering.ts`
- Color quantization in `colorreductionmanagement.ts`
- Vector class mixed with KMeans logic
- Hard to extend with new clustering algorithms

**Files Involved:**
- `src/lib/clustering.ts` (282 lines)
- `src/colorreductionmanagement.ts`

**Why This Matters:**
- K-means is the foundation of color reduction
- Better structure enables future improvements
- Separation of concerns improves testability

---

## ✅ Deliverables

### 1. Separate Vector Class (60 min)
- [ ] Extract Vector class to `src/lib/Vector.ts`
- [ ] Add proper TypeScript types
- [ ] Keep existing functionality identical
- [ ] Add JSDoc comments

### 2. Refactor KMeans Class (120 min)
- [ ] Separate initialization logic (random vs k-means++)
- [ ] Create ClusteringStrategy interface
- [ ] Extract convergence checking
- [ ] Make algorithm parameters configurable

### 3. Refactor ColorQuantizer (90 min)
- [ ] Extract from colorreductionmanagement.ts
- [ ] Create dedicated ColorQuantizer class
- [ ] Separate clustering from color mapping
- [ ] Use Color class from LOT 2.3

### 4. Tests (90 min)
- [ ] Unit tests for Vector operations
- [ ] Unit tests for KMeans with fixed seed
- [ ] Integration tests with snapshot comparison
- [ ] Test determinism (same seed = same result)

### 5. Documentation (30 min)
- [ ] JSDoc for all public methods
- [ ] Algorithm explanation
- [ ] Usage examples

---

## 🧪 Validation Criteria

**Critical:**
1. ✅ Clustering produces IDENTICAL results with same seed
2. ✅ All snapshot tests pass (no regressions)
3. ✅ Test coverage ≥90%
4. ✅ Performance within ±5% of baseline

**Code Quality:**
1. ✅ Vector class in separate file
2. ✅ Clean separation of concerns
3. ✅ Extensible design (easy to add new algorithms)

---

## 🚀 Implementation Guide

### Step 1: Extract Vector Class

**Create:** `src/lib/Vector.ts`

```typescript
export class Vector {
  public values: number[];
  public weight: number;
  public tag?: any;

  constructor(values: number[], weight: number = 1, tag?: any) {
    this.values = values;
    this.weight = weight;
    this.tag = tag;
  }

  /**
   * Calculate Euclidean distance to another vector
   */
  distanceTo(other: Vector): number {
    let sum = 0;
    for (let i = 0; i < this.values.length; i++) {
      const diff = this.values[i] - other.values[i];
      sum += diff * diff;
    }
    return Math.sqrt(sum);
  }

  /**
   * Add another vector (weighted)
   */
  add(other: Vector): void {
    for (let i = 0; i < this.values.length; i++) {
      this.values[i] += other.values[i] * other.weight;
    }
    this.weight += other.weight;
  }

  /**
   * Normalize by weight (compute average)
   */
  normalize(): void {
    if (this.weight > 0) {
      for (let i = 0; i < this.values.length; i++) {
        this.values[i] /= this.weight;
      }
    }
  }

  /**
   * Clone this vector
   */
  clone(): Vector {
    return new Vector([...this.values], this.weight, this.tag);
  }
}
```

### Step 2: Refactor KMeans

**In:** `src/lib/clustering.ts`

```typescript
export interface ClusteringStrategy {
  initialize(data: Vector[], k: number): Vector[];
}

export class RandomInitialization implements ClusteringStrategy {
  initialize(data: Vector[], k: number): Vector[] {
    // Existing random initialization logic
  }
}

export class KMeansPlusPlusInitialization implements ClusteringStrategy {
  initialize(data: Vector[], k: number): Vector[] {
    // K-means++ initialization (optional enhancement)
  }
}

export class KMeans {
  private maxIterations: number;
  private convergenceThreshold: number;
  private initStrategy: ClusteringStrategy;

  constructor(options: {
    maxIterations?: number;
    convergenceThreshold?: number;
    initStrategy?: ClusteringStrategy;
  } = {}) {
    this.maxIterations = options.maxIterations ?? 100;
    this.convergenceThreshold = options.convergenceThreshold ?? 0.001;
    this.initStrategy = options.initStrategy ?? new RandomInitialization();
  }

  /**
   * Perform k-means clustering
   */
  cluster(data: Vector[], k: number): Vector[] {
    // Initialize centroids
    let centroids = this.initStrategy.initialize(data, k);

    // Iterate until convergence or max iterations
    for (let iter = 0; iter < this.maxIterations; iter++) {
      const newCentroids = this.assignAndUpdate(data, centroids);

      if (this.hasConverged(centroids, newCentroids)) {
        break;
      }

      centroids = newCentroids;
    }

    return centroids;
  }

  private assignAndUpdate(data: Vector[], centroids: Vector[]): Vector[] {
    // Existing logic...
  }

  private hasConverged(old: Vector[], new_: Vector[]): boolean {
    // Check if centroids have moved less than threshold
  }
}
```

### Step 3: Create ColorQuantizer

**Create:** `src/lib/ColorQuantizer.ts`

```typescript
import { Color } from './color';
import { KMeans } from './clustering';
import { Vector } from './Vector';
import { ColorSpace } from './constants';

export class ColorQuantizer {
  private kmeans: KMeans;
  private colorSpace: ColorSpace;

  constructor(colorSpace: ColorSpace = ColorSpace.RGB) {
    this.kmeans = new KMeans();
    this.colorSpace = colorSpace;
  }

  /**
   * Reduce image colors using k-means clustering
   */
  quantize(
    imageData: ImageData,
    numberOfColors: number
  ): { palette: Color[]; colorMap: Uint8Array } {
    // Convert pixels to vectors in chosen color space
    const vectors = this.imageDataToVectors(imageData);

    // Cluster
    const centroids = this.kmeans.cluster(vectors, numberOfColors);

    // Convert centroids back to colors
    const palette = centroids.map(v => this.vectorToColor(v));

    // Map each pixel to nearest color
    const colorMap = this.createColorMap(imageData, palette);

    return { palette, colorMap };
  }

  private imageDataToVectors(imageData: ImageData): Vector[] {
    // Implementation...
  }

  private vectorToColor(vector: Vector): Color {
    // Implementation...
  }

  private createColorMap(imageData: ImageData, palette: Color[]): Uint8Array {
    // Implementation...
  }
}
```

### Step 4: Tests

**Determinism Test (CRITICAL):**
```typescript
describe('KMeans determinism', () => {
  it('should produce identical results with same seed', () => {
    const data = generateTestData();
    const seed = 12345;

    Random.setSeed(seed);
    const result1 = kmeans.cluster(data, 5);

    Random.setSeed(seed);
    const result2 = kmeans.cluster(data, 5);

    // Results must be IDENTICAL
    expect(result1).toEqual(result2);
  });
});
```

**Integration Test:**
```typescript
describe('Color quantization integration', () => {
  it('should match snapshot for test image', () => {
    const img = loadTestImage('small.png');
    const quantizer = new ColorQuantizer(ColorSpace.RGB);
    const result = quantizer.quantize(img, 16);

    // Load snapshot
    const snapshot = loadSnapshot('small/01-clustering.json');

    // Compare (allow small tolerance for floating point)
    expectPalettesMatch(result.palette, snapshot.palette, 1);
  });
});
```

### Step 5: Validation

```bash
# Run new tests
npm test -- --testPathPattern=clustering
npm test -- --testPathPattern=Vector

# CRITICAL: Run snapshot tests
npm test -- --testPathPattern=snapshot

# Check coverage
npm test -- --coverage

# Run benchmarks
npm test -- --testPathPattern=benchmark
```

---

## 💡 Tips & Gotchas

### Determinism is Critical
- Use seeded random number generator
- Test with same seed multiple times
- Snapshots prove determinism

### Floating Point Tolerance
- Allow ±0.1 RGB value difference
- Rounding can cause minor variations
- Document tolerance in tests

### Performance
- Don't add unnecessary abstractions
- Keep hot paths optimized
- Typed arrays where appropriate

---

## 📤 Deliverables Checklist

- [ ] Vector.ts created and tested
- [ ] KMeans class refactored
- [ ] ColorQuantizer class created
- [ ] colorreductionmanagement.ts updated
- [ ] Unit tests ≥90% coverage
- [ ] Integration tests pass
- [ ] All snapshot tests pass
- [ ] Performance validated (±5%)
- [ ] JSDoc complete
- [ ] Code committed
- [ ] PROJECT_TRACKER.md updated

---

## 🔄 Handoff Notes

**For Manager:**
- Verify determinism (run tests multiple times)
- Check snapshot tests pass
- Validate performance

**For Next AI Devs:**
- Use ColorQuantizer for color reduction
- Vector class is now separate
- Clustering is extensible

---

## 📝 AI Dev Updates

**Started:** [Date/Time]

**Progress Notes:**
- [Updates]

**Completed:** [Date/Time]

**Actual Hours:** [Hours]

**Issues:**
- [Problems]

---

**Last Updated:** 2025-11-05
**Version:** 1.0
