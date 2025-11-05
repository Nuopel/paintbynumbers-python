# LOT 3.4: Facet Border Segmenter Refactor

**Phase:** 3 - Core Algorithm Refactoring
**Estimated Time:** 6 hours
**Priority:** HIGH
**Dependencies:** LOT 3.3 (Border Tracer)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Refactor border segmentation code to reduce complexity, extract Haar wavelet reduction into separate class, and simplify deeply nested conditionals.

---

## 📋 Context

**Current State:**
- `facetBorderSegmenter.ts` (320 lines)
- 8+ levels of nesting in conditionals
- Haar wavelet reduction embedded in main logic

**Goal:**
- Reduce nesting from 8+ to ≤4 levels
- Extract WaveletReducer class
- Separate border segmentation from point reduction

---

## ✅ Deliverables

### 1. Extract WaveletReducer (90 min)
- [ ] Create `src/lib/WaveletReducer.ts`
- [ ] Extract Haar wavelet algorithm
- [ ] Make configurable (threshold, iterations)
- [ ] Unit tests

### 2. Create BorderSegmenter Class (120 min)
- [ ] Separate border segmentation logic
- [ ] Use early returns to reduce nesting
- [ ] Clear method responsibilities

### 3. Refactor Main File (90 min)
- [ ] Use WaveletReducer
- [ ] Use BorderSegmenter
- [ ] Simplify control flow

### 4. Tests (60 min)
- [ ] Unit tests for WaveletReducer
- [ ] Integration tests for segmentation
- [ ] Snapshot comparison (must match)

### 5. Documentation (30 min)
- [ ] JSDoc comments
- [ ] Algorithm explanation

---

## 🧪 Validation Criteria

1. ✅ Segmented borders IDENTICAL to baseline
2. ✅ Nesting depth reduced to ≤4 levels
3. ✅ Test coverage ≥90%
4. ✅ All snapshot tests pass

---

## 🚀 Implementation Guide

### WaveletReducer

```typescript
export class WaveletReducer {
  constructor(private threshold: number = 0.5) {}

  /**
   * Reduce points using Haar wavelet transform
   */
  reduce(points: PathPoint[]): PathPoint[] {
    // Haar wavelet reduction algorithm
    // Extract from existing code
  }

  private calculateWaveletCoefficients(points: PathPoint[]): number[] {
    // Implementation
  }

  private filterByThreshold(coefficients: number[]): PathPoint[] {
    // Implementation
  }
}
```

### BorderSegmenter

```typescript
export class BorderSegmenter {
  private waveletReducer: WaveletReducer;

  constructor() {
    this.waveletReducer = new WaveletReducer();
  }

  /**
   * Segment border into connected parts
   */
  segmentBorder(border: PathPoint[]): PathPoint[][] {
    // Extract segmentation logic
    // Use early returns instead of deep nesting
  }

  /**
   * Reduce complexity of each segment
   */
  reduceSegments(segments: PathPoint[][]): PathPoint[][] {
    return segments.map(segment => this.waveletReducer.reduce(segment));
  }
}
```

### Reducing Nesting

```typescript
// BEFORE (8 levels):
if (condition1) {
  if (condition2) {
    if (condition3) {
      if (condition4) {
        if (condition5) {
          // ... more nesting
        }
      }
    }
  }
}

// AFTER (≤4 levels):
if (!condition1) return;
if (!condition2) return;
if (!condition3) return;

// Now at level 1 for main logic
```

---

## 📤 Deliverables Checklist

- [ ] WaveletReducer.ts created
- [ ] BorderSegmenter.ts created
- [ ] facetBorderSegmenter.ts refactored
- [ ] Nesting ≤4 levels
- [ ] Tests ≥90% coverage
- [ ] Snapshot tests pass
- [ ] Documentation complete
- [ ] Code committed
- [ ] PROJECT_TRACKER.md updated

---

**Last Updated:** 2025-11-05
**Version:** 1.0
