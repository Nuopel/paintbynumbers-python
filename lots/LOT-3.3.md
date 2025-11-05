# LOT 3.3: Facet Border Tracer - Orientation Strategy ⚠️

**Phase:** 3 - Core Algorithm Refactoring
**Estimated Time:** 10 hours
**Priority:** ⚠️ CRITICAL - Most Complex Refactoring
**Dependencies:** LOT 2.2 (Boundary Utilities), LOT 3.2 (Facet Creation)
**Assigned To:** _[AI Dev will write name here]_

---

## ⚠️ WARNING: CRITICAL LOT

This is the **MOST COMPLEX** refactoring in the entire project. The facetBorderTracer.ts file has:
- 502 lines of code
- ~70% code duplication across 4 orientations
- 50+ nearly identical conditional blocks
- Critical impact: Any bug breaks the entire output

**Requirements:**
- Border paths must be **EXACTLY IDENTICAL** to baseline (zero tolerance)
- Extensive testing required
- Manager must perform extra scrutiny during validation
- If this LOT fails, **PROJECT PAUSES** for investigation

---

## 🎯 Objective

Refactor `facetBorderTracer.ts` from 502 lines to ~250 lines by eliminating code duplication across the 4 orientation cases (Left, Top, Right, Bottom) using the Strategy Pattern or orientation-agnostic vector math.

---

## 📋 Context

**Current State Analysis:**

The file `src/facetBorderTracer.ts` contains nearly identical code repeated 4 times:
- Lines X-Y: Left orientation handling
- Lines Y-Z: Top orientation handling
- Lines Z-A: Right orientation handling
- Lines A-B: Bottom orientation handling

Each section has ~50 conditional checks that differ ONLY in:
- Direction vectors (+1, -1 for x/y)
- Coordinate ordering (x,y vs y,x)
- Rotation logic (clockwise/counterclockwise)

**Current Algorithm (Simplified):**
```typescript
// For each orientation
if (orientation === Left) {
  if (condition1) { /* logic A */ }
  if (condition2) { /* logic B */ }
  // ... 50 more conditions
} else if (orientation === Top) {
  if (condition1) { /* same logic A, different coords */ }
  if (condition2) { /* same logic B, different coords */ }
  // ... 50 more conditions
} // ... repeat for Right and Bottom
```

**Goal Architecture:**
```typescript
interface OrientationStrategy {
  getNextPoint(current: Point, wall: WallOrientation): Point;
  checkBoundary(point: Point, bounds: BoundingBox): boolean;
  rotateClockwise(orientation: WallOrientation): WallOrientation;
  rotateCounterClockwise(orientation: WallOrientation): WallOrientation;
}

class LeftStrategy implements OrientationStrategy { /* ... */ }
class TopStrategy implements OrientationStrategy { /* ... */ }
class RightStrategy implements OrientationStrategy { /* ... */ }
class BottomStrategy implements OrientationStrategy { /* ... */ }

// Main tracing loop becomes:
function traceBorder(start: Point, strategy: OrientationStrategy) {
  // Single implementation that works for all orientations
}
```

---

## ✅ Deliverables

### 1. Read and Understand Current Implementation (2 hours)
- [ ] Read `src/facetBorderTracer.ts:1-502` completely
- [ ] Document the algorithm in pseudocode
- [ ] Identify all duplicated code blocks
- [ ] Map out the differences between orientations
- [ ] Create a document: `docs/BORDER_TRACER_ANALYSIS.md`

**Analysis Document Should Include:**
- High-level algorithm explanation
- List of all duplicated patterns
- Difference matrix (what changes per orientation)
- Proposed refactoring approach
- Risk assessment

### 2. Design Orientation Strategy Pattern (1.5 hours)
- [ ] Create interface definition: `src/lib/OrientationStrategy.ts`
- [ ] Design strategy classes for each orientation
- [ ] Define coordinate transformation logic
- [ ] Plan backward compatibility (can run old & new side-by-side)

**File: `src/lib/OrientationStrategy.ts`**
```typescript
export enum WallOrientation {
  Left = 0,
  Top = 1,
  Right = 2,
  Bottom = 3,
}

export interface OrientationStrategy {
  /**
   * Get the next point when moving along the wall
   */
  getNextPoint(current: Point, direction: number): Point;

  /**
   * Check if point is within valid boundaries
   */
  isInBounds(point: Point, width: number, height: number): boolean;

  /**
   * Rotate orientation clockwise
   */
  rotateClockwise(): OrientationStrategy;

  /**
   * Rotate orientation counter-clockwise
   */
  rotateCounterClockwise(): OrientationStrategy;

  /**
   * Get the wall orientation enum
   */
  getOrientation(): WallOrientation;
}
```

### 3. Implement Strategy Classes (3 hours)
Create strategy implementations:

**File: `src/lib/borderTracing/LeftOrientationStrategy.ts`**
**File: `src/lib/borderTracing/TopOrientationStrategy.ts`**
**File: `src/lib/borderTracing/RightOrientationStrategy.ts`**
**File: `src/lib/borderTracing/BottomOrientationStrategy.ts`**

Each strategy should:
- [ ] Implement `OrientationStrategy` interface
- [ ] Encapsulate orientation-specific logic
- [ ] Use boundary utilities from LOT 2.2
- [ ] Be thoroughly unit tested

**OR (Alternative Approach): Vector-Based Solution**

Instead of 4 strategy classes, use vector math:

**File: `src/lib/borderTracing/VectorOrientationHandler.ts`**
```typescript
class VectorOrientationHandler {
  private static DIRECTION_VECTORS = {
    [WallOrientation.Left]: { dx: -1, dy: 0 },
    [WallOrientation.Top]: { dx: 0, dy: -1 },
    [WallOrientation.Right]: { dx: 1, dy: 0 },
    [WallOrientation.Bottom]: { dx: 0, dy: 1 },
  };

  static getNextPoint(
    current: Point,
    orientation: WallOrientation
  ): Point {
    const vec = this.DIRECTION_VECTORS[orientation];
    return { x: current.x + vec.dx, y: current.y + vec.dy };
  }

  // ... other methods using vector math
}
```

**Choose One Approach:**
- Strategy Pattern: More OOP, easier to test individual orientations
- Vector Math: More concise, mathematically elegant

Document your choice in `BORDER_TRACER_ANALYSIS.md`

### 4. Refactor Main Border Tracing Loop (2.5 hours)
- [ ] Refactor `facetBorderTracer.ts` to use strategies
- [ ] Eliminate all code duplication
- [ ] Maintain exact same public API
- [ ] Keep old implementation as `facetBorderTracer.old.ts` for comparison

**Target Structure:**
```typescript
export class FacetBorderTracer {
  private strategies: Map<WallOrientation, OrientationStrategy>;

  constructor() {
    this.strategies = new Map([
      [WallOrientation.Left, new LeftOrientationStrategy()],
      [WallOrientation.Top, new TopOrientationStrategy()],
      [WallOrientation.Right, new RightOrientationStrategy()],
      [WallOrientation.Bottom, new BottomOrientationStrategy()],
    ]);
  }

  public traceBorder(facet: Facet, imgWidth: number, imgHeight: number): PathPoint[] {
    // Single implementation using strategy pattern
    // Should be ~100-150 lines instead of 500
  }
}
```

**Code Reduction Target:**
- Original: 502 lines
- Target: ≤250 lines (50% reduction)
- Minimum acceptable: ≤300 lines (40% reduction)

### 5. Extensive Testing (2 hours)
This LOT requires MORE tests than any other:

**Unit Tests: `tests/unit/borderTracing/orientationStrategy.test.ts`**
- [ ] Test each strategy independently
- [ ] Test coordinate transformations
- [ ] Test boundary conditions
- [ ] Test rotation logic
- [ ] Edge cases: corners, single-pixel facets, borders

**Integration Tests: `tests/integration/borderTracer.test.ts`**
- [ ] Test complete border tracing with each strategy
- [ ] Test facets with complex borders
- [ ] Test facets at image edges
- [ ] Test tiny facets (1-4 pixels)

**Comparison Tests: `tests/integration/borderTracer.comparison.test.ts`**
- [ ] Run old and new implementation side-by-side
- [ ] Compare outputs point-by-point
- [ ] Must be **EXACTLY IDENTICAL** (zero tolerance)
- [ ] Test with all test images (small, medium, complex)

**Test Coverage Requirement:** ≥95%

### 6. Performance Validation (30 min)
- [ ] Run benchmarks on refactored code
- [ ] Compare to baseline from LOT 1.2
- [ ] Performance must be within ±5%
- [ ] Document any performance changes

### 7. Documentation (30 min)
- [ ] Update comments in refactored code
- [ ] JSDoc for all public methods
- [ ] Document the strategy pattern approach
- [ ] Update architecture documentation

---

## 🧪 Validation Criteria

### ⚠️ CRITICAL: Zero-Tolerance Validation

**Border Path Comparison:**
```bash
# Must pass with ZERO differences
npm test -- --testPathPattern=borderTracer.comparison
```

If ANY border path differs by even ONE point, this LOT is **REJECTED**.

### Comprehensive Validation
1. ✅ All tests pass (50+ tests)
2. ✅ Test coverage ≥95%
3. ✅ Border paths EXACTLY match baseline (zero tolerance)
4. ✅ Code reduction ≥40% (502 → ≤300 lines)
5. ✅ No code duplication between orientations
6. ✅ Performance within ±5% of baseline
7. ✅ All snapshot tests still pass
8. ✅ Strategy pattern properly implemented
9. ✅ Code is cleaner and more maintainable
10. ✅ Documentation is complete

### Manager Extra Scrutiny
- Manager must manually review ALL code changes
- Manager must run tests 10+ times (check for flakiness)
- Manager must visually inspect border paths on test images
- Manager must compare old vs new implementation line-by-line

---

## 🚀 Implementation Guide

### Phase 1: Analysis (2 hours)

**Step 1: Read Current Implementation**
```bash
# Open and read
code src/facetBorderTracer.ts
```

Take notes on:
- What is the main algorithm doing?
- How does border tracing work?
- What are the wall orientations?
- How does it handle corners?
- What are the edge cases?

**Step 2: Identify Duplication Patterns**

Create a spreadsheet or document:
```
| Code Block | Left | Top | Right | Bottom | Difference |
|------------|------|-----|-------|--------|------------|
| Next point | x-1  | y-1 | x+1   | y+1    | Direction  |
| Boundary   | x>=0 | y>=0| x<w   | y<h    | Axis/bound |
| ...        | ...  | ... | ...   | ...    | ...        |
```

**Step 3: Document Algorithm**

Write `docs/BORDER_TRACER_ANALYSIS.md`:
```markdown
# Border Tracer Algorithm Analysis

## High-Level Algorithm
[Explain what it does]

## Current Implementation Issues
1. Code duplication: 70%
2. Hard to maintain: Any bug fix must be applied 4 times
3. Hard to extend: Adding new functionality requires 4 copies

## Proposed Solution
[Explain strategy pattern or vector approach]

## Risk Mitigation
- Keep old implementation for comparison
- Point-by-point validation tests
- Extensive edge case testing
```

### Phase 2: Design (1.5 hours)

**Step 1: Choose Approach**

Evaluate both approaches:

**Strategy Pattern Pros:**
- Clear separation of concerns
- Easy to test individual orientations
- Follows SOLID principles

**Strategy Pattern Cons:**
- More files to manage
- Slightly more verbose

**Vector Math Pros:**
- More concise
- Mathematically elegant
- Fewer files

**Vector Math Cons:**
- May be harder to debug
- Less obvious separation

**Recommendation:** Start with Strategy Pattern (easier to validate correctness).

**Step 2: Design Interfaces**

```typescript
// src/lib/OrientationStrategy.ts
export interface OrientationStrategy {
  getNextPoint(current: Point, wall: WallOrientation): Point;
  checkBoundary(point: Point, bounds: BoundingBox): boolean;
  rotateClockwise(): OrientationStrategy;
  rotateCounterClockwise(): OrientationStrategy;
  getOrientation(): WallOrientation;
}

// Factory for creating strategies
export class OrientationStrategyFactory {
  static create(orientation: WallOrientation): OrientationStrategy {
    switch (orientation) {
      case WallOrientation.Left:
        return new LeftOrientationStrategy();
      case WallOrientation.Top:
        return new TopOrientationStrategy();
      case WallOrientation.Right:
        return new RightOrientationStrategy();
      case WallOrientation.Bottom:
        return new BottomOrientationStrategy();
    }
  }
}
```

### Phase 3: Implementation (3 hours)

**Step 1: Create Base Strategy**

Start with one orientation (e.g., Left) and get it working perfectly:

```typescript
// src/lib/borderTracing/LeftOrientationStrategy.ts
export class LeftOrientationStrategy implements OrientationStrategy {
  getNextPoint(current: Point, wall: WallOrientation): Point {
    // Implementation for left orientation
    // This is extracted from the current facetBorderTracer.ts
  }

  checkBoundary(point: Point, bounds: BoundingBox): boolean {
    return point.x >= 0 && point.x < bounds.width &&
           point.y >= 0 && point.y < bounds.height;
  }

  rotateClockwise(): OrientationStrategy {
    return new TopOrientationStrategy();
  }

  rotateCounterClockwise(): OrientationStrategy {
    return new BottomOrientationStrategy();
  }

  getOrientation(): WallOrientation {
    return WallOrientation.Left;
  }
}
```

**Step 2: Test First Strategy**

Before implementing others, make sure Left works:
```typescript
describe('LeftOrientationStrategy', () => {
  it('should get next point correctly', () => {
    const strategy = new LeftOrientationStrategy();
    const current = { x: 5, y: 5 };
    const next = strategy.getNextPoint(current, WallOrientation.Left);
    expect(next).toEqual({ x: 4, y: 5 });
  });

  // ... more tests
});
```

**Step 3: Implement Remaining Strategies**

Once Left works, implement Top, Right, Bottom using the same pattern.

**Step 4: Refactor Main Border Tracer**

**CRITICAL: Keep old code for comparison**
```bash
cp src/facetBorderTracer.ts src/facetBorderTracer.old.ts
```

Now refactor:
```typescript
export function buildFacetBorderPaths(
  facetResult: FacetResult,
  imgWidth: number,
  imgHeight: number
): void {
  const tracer = new FacetBorderTracer();

  for (const facet of facetResult.facets) {
    facet.borderPath = tracer.traceBorder(facet, imgWidth, imgHeight);
  }
}

class FacetBorderTracer {
  private strategyFactory = new OrientationStrategyFactory();

  traceBorder(facet: Facet, imgWidth: number, imgHeight: number): PathPoint[] {
    const path: PathPoint[] = [];
    let currentPoint = facet.startPoint;
    let currentOrientation = this.detectInitialOrientation(currentPoint, facet);

    // Main tracing loop
    while (true) {
      const strategy = this.strategyFactory.create(currentOrientation);

      // Use strategy to determine next move
      const nextPoint = strategy.getNextPoint(currentPoint, currentOrientation);

      // Check if we've completed the loop
      if (this.isBackAtStart(nextPoint, facet.startPoint, path)) {
        break;
      }

      path.push(nextPoint);
      currentPoint = nextPoint;

      // Determine if orientation needs to change
      if (this.shouldRotate(currentPoint, facet)) {
        currentOrientation = this.rotate(currentOrientation, strategy);
      }
    }

    return path;
  }

  // ... helper methods
}
```

**Step 5: Iterative Refinement**

After initial implementation:
1. Run tests → Find failures → Fix → Repeat
2. Compare with old implementation
3. Refine until EXACTLY identical

### Phase 4: Testing (2 hours)

**Step 1: Unit Tests**

Test each component:
```typescript
// tests/unit/borderTracing/strategies.test.ts
describe('Orientation Strategies', () => {
  describe('LeftOrientationStrategy', () => {
    // 10+ tests for left
  });

  describe('TopOrientationStrategy', () => {
    // 10+ tests for top
  });

  // ... etc
});
```

**Step 2: Comparison Tests**

**MOST IMPORTANT TEST:**
```typescript
// tests/integration/borderTracer.comparison.test.ts
import { buildFacetBorderPaths as oldImplementation } from '../facetBorderTracer.old';
import { buildFacetBorderPaths as newImplementation } from '../facetBorderTracer';

describe('Border Tracer - Old vs New Comparison', () => {
  const testImages = ['small', 'medium', 'complex'];

  testImages.forEach(imageName => {
    it(`should produce identical output for ${imageName}`, () => {
      // Load test image
      const img = loadTestImage(`${imageName}.png`);

      // Run through pipeline to get facets
      const facetsOld = createFacets(img); // clone data
      const facetsNew = createFacets(img); // clone data

      // Run old implementation
      oldImplementation(facetsOld, img.width, img.height);

      // Run new implementation
      newImplementation(facetsNew, img.width, img.height);

      // Compare point-by-point
      expect(facetsNew.length).toBe(facetsOld.length);

      for (let i = 0; i < facetsNew.length; i++) {
        const oldPath = facetsOld[i].borderPath;
        const newPath = facetsNew[i].borderPath;

        expect(newPath.length).toBe(oldPath.length);

        for (let j = 0; j < newPath.length; j++) {
          expect(newPath[j].x).toBe(oldPath[j].x);
          expect(newPath[j].y).toBe(oldPath[j].y);
        }
      }
    });
  });
});
```

**If this test fails, DO NOT PROCEED. Fix the bug.**

**Step 3: Edge Case Tests**

```typescript
describe('Border Tracer - Edge Cases', () => {
  it('should handle single-pixel facets', () => {});
  it('should handle facets at image corners', () => {});
  it('should handle facets at image edges', () => {});
  it('should handle L-shaped facets', () => {});
  it('should handle donut-shaped facets (holes)', () => {});
  it('should handle facets with complex borders', () => {});
});
```

### Phase 5: Validation (1 hour)

```bash
# Run all tests
npm test

# Run comparison tests specifically
npm test -- --testPathPattern=comparison

# Check coverage
npm test -- --coverage

# Run benchmarks
npm test -- --testPathPattern=benchmark

# Visual inspection
# Open SVG outputs and compare old vs new visually
```

---

## 💡 Tips & Gotchas

### Common Pitfalls
1. **Off-by-one errors** in coordinate math (x vs x+1)
2. **Rotation direction** confusion (CW vs CCW)
3. **Boundary checking** at image edges
4. **Corner handling** where orientation changes
5. **Path closure** - ensuring loop completes correctly

### Debugging Strategy
If outputs don't match:
1. Add logging to both old and new implementations
2. Compare point-by-point where they diverge
3. Visualize the paths (draw them on canvas)
4. Check for coordinate transformation errors

### Testing Strategy
- Test strategies individually BEFORE integrating
- Use small, simple test cases first (3x3 images)
- Gradually increase complexity
- Always compare with baseline

---

## 📤 Deliverables Checklist

- [ ] `docs/BORDER_TRACER_ANALYSIS.md` created
- [ ] `src/lib/OrientationStrategy.ts` interface defined
- [ ] All 4 strategy classes implemented (or vector handler)
- [ ] `src/facetBorderTracer.ts` refactored to ≤300 lines
- [ ] Old implementation saved as `facetBorderTracer.old.ts`
- [ ] 50+ unit tests created
- [ ] Comparison tests pass with ZERO differences
- [ ] All snapshot tests pass
- [ ] Test coverage ≥95%
- [ ] Performance within ±5% of baseline
- [ ] Code is well-documented
- [ ] All code committed to git
- [ ] Updated `PROJECT_TRACKER.md`

---

## 🔄 Handoff Notes

**For Manager:**
This is a CRITICAL LOT. Please perform extra validation:
- Run tests 10+ times
- Manually inspect border paths
- Compare old vs new visually
- Check performance carefully

**For Next AI Dev (LOT 3.4):**
- Border tracer is now refactored and tested
- Use the strategy pattern as example for other refactorings
- Border segmenter can build on this work

---

## 📝 AI Dev Updates

**Started:** [Date/Time]

**Progress Notes:**
- [Detailed updates as you work]

**Completed:** [Date/Time]

**Actual Hours:** [Hours]

**Deviations:**
- [Any changes from plan]

**Issues:**
- [Problems encountered and solutions]

**Test Results:**
- Comparison tests: [PASS/FAIL]
- Coverage: [%]
- Performance: [vs baseline]

---

**Last Updated:** 2025-11-05
**Version:** 1.0
