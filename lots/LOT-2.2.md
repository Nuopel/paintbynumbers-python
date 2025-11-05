# LOT 2.2: Boundary & Validation Utilities

**Phase:** 2 - Extract Common Utilities
**Estimated Time:** 4 hours
**Priority:** HIGH
**Dependencies:** LOT 1.2 (Snapshot & Benchmark)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Create reusable boundary checking and validation utilities to eliminate duplicated boundary logic throughout the codebase. These utilities will be used in facet creation, border tracing, and border segmentation.

---

## 📋 Context

**Current State:**
Boundary checking code is duplicated across multiple files:
- `facetCreator.ts` - Checks if pixels are within image bounds
- `facetBorderTracer.ts` - Validates border points are in bounds
- `facetBorderSegmenter.ts` - Checks array indices
- Similar checks repeated 50+ times across codebase

**Examples of Duplication:**
```typescript
// Pattern repeated everywhere:
if (x >= 0 && x < width && y >= 0 && y < height) {
  // safe to access
}

if (x < 0 || x >= width || y < 0 || y >= height) {
  continue; // out of bounds
}

const safeX = Math.max(0, Math.min(x, width - 1));
```

**Why This Matters:**
- 50+ instances of boundary checking code
- Easy to introduce off-by-one errors
- Hard to maintain consistency
- No single source of truth

---

## ✅ Deliverables

### 1. Create Boundary Utilities Module (90 min)
Create `src/lib/boundaryUtils.ts`:

- [ ] `isInBounds(x, y, width, height): boolean` - Check if point is in bounds
- [ ] `clamp(value, min, max): number` - Clamp value to range
- [ ] `clampPoint(point, width, height): Point` - Clamp point to bounds
- [ ] `getNeighbors4(x, y, width, height): Point[]` - Get 4-connected neighbors (up, down, left, right)
- [ ] `getNeighbors8(x, y, width, height): Point[]` - Get 8-connected neighbors (includes diagonals)
- [ ] `isOnEdge(x, y, width, height): boolean` - Check if point is on image edge
- [ ] `getEdgeType(x, y, width, height): EdgeType` - Determine which edge(s)

**Example Implementation:**
```typescript
export interface Point {
  x: number;
  y: number;
}

export enum EdgeType {
  None = 0,
  Left = 1,
  Right = 2,
  Top = 4,
  Bottom = 8,
}

/**
 * Check if a point is within bounds
 */
export function isInBounds(
  x: number,
  y: number,
  width: number,
  height: number
): boolean {
  return x >= 0 && x < width && y >= 0 && y < height;
}

/**
 * Clamp a value to a range [min, max]
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(value, max));
}

/**
 * Clamp a point to image boundaries
 */
export function clampPoint(
  point: Point,
  width: number,
  height: number
): Point {
  return {
    x: clamp(point.x, 0, width - 1),
    y: clamp(point.y, 0, height - 1),
  };
}

/**
 * Get 4-connected neighbors (up, down, left, right)
 * Only returns neighbors that are in bounds
 */
export function getNeighbors4(
  x: number,
  y: number,
  width: number,
  height: number
): Point[] {
  const neighbors: Point[] = [];

  // Up
  if (y > 0) neighbors.push({ x, y: y - 1 });
  // Down
  if (y < height - 1) neighbors.push({ x, y: y + 1 });
  // Left
  if (x > 0) neighbors.push({ x: x - 1, y });
  // Right
  if (x < width - 1) neighbors.push({ x: x + 1, y });

  return neighbors;
}

/**
 * Get 8-connected neighbors (includes diagonals)
 * Only returns neighbors that are in bounds
 */
export function getNeighbors8(
  x: number,
  y: number,
  width: number,
  height: number
): Point[] {
  const neighbors: Point[] = [];

  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      if (dx === 0 && dy === 0) continue; // Skip center

      const nx = x + dx;
      const ny = y + dy;

      if (isInBounds(nx, ny, width, height)) {
        neighbors.push({ x: nx, y: ny });
      }
    }
  }

  return neighbors;
}

/**
 * Check if point is on any edge
 */
export function isOnEdge(
  x: number,
  y: number,
  width: number,
  height: number
): boolean {
  return x === 0 || x === width - 1 || y === 0 || y === height - 1;
}

/**
 * Get which edge(s) a point is on (can be corner = multiple edges)
 */
export function getEdgeType(
  x: number,
  y: number,
  width: number,
  height: number
): EdgeType {
  let edge = EdgeType.None;

  if (x === 0) edge |= EdgeType.Left;
  if (x === width - 1) edge |= EdgeType.Right;
  if (y === 0) edge |= EdgeType.Top;
  if (y === height - 1) edge |= EdgeType.Bottom;

  return edge;
}
```

### 2. Replace Duplicated Boundary Checks (90 min)
Find and replace boundary checks in these files:

**Priority Files:**
- [ ] `src/facetCreator.ts` - Replace all boundary checks
- [ ] `src/facetBorderTracer.ts` - Replace all boundary checks
- [ ] `src/facetBorderSegmenter.ts` - Replace all boundary checks
- [ ] `src/facetReducer.ts` - Replace boundary checks if any
- [ ] `src/lib/fill.ts` - Replace flood-fill boundary checks

**Search for patterns:**
```bash
# Find boundary check patterns
grep -rn "x >= 0 && x <" src/
grep -rn "y >= 0 && y <" src/
grep -rn "Math.max(0, Math.min" src/
```

**Replace Example:**
```typescript
// BEFORE:
if (x >= 0 && x < width && y >= 0 && y < height) {
  const pixel = imgData[y * width + x];
}

// AFTER:
import { isInBounds } from './lib/boundaryUtils';

if (isInBounds(x, y, width, height)) {
  const pixel = imgData[y * width + x];
}
```

### 3. Unit Tests (60 min)
Create `tests/unit/lib/boundaryUtils.test.ts`:

**Test Coverage:**
- [ ] Test `isInBounds` with valid points
- [ ] Test `isInBounds` with out-of-bounds points (all 4 directions)
- [ ] Test `isInBounds` with edge cases (0, negative, max)
- [ ] Test `clamp` with value in range
- [ ] Test `clamp` with value below min
- [ ] Test `clamp` with value above max
- [ ] Test `clampPoint` various cases
- [ ] Test `getNeighbors4` in center (should return 4)
- [ ] Test `getNeighbors4` on edges (should return 2-3)
- [ ] Test `getNeighbors4` in corners (should return 2)
- [ ] Test `getNeighbors8` in center (should return 8)
- [ ] Test `getNeighbors8` on edges (should return 5)
- [ ] Test `getNeighbors8` in corners (should return 3)
- [ ] Test `isOnEdge` for edge points
- [ ] Test `isOnEdge` for center points
- [ ] Test `getEdgeType` for corners (should return multiple flags)

**Example Tests:**
```typescript
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
  });

  describe('getNeighbors4', () => {
    it('should return 4 neighbors for center point', () => {
      const neighbors = getNeighbors4(5, 5, 10, 10);
      expect(neighbors).toHaveLength(4);
      expect(neighbors).toContainEqual({ x: 5, y: 4 }); // up
      expect(neighbors).toContainEqual({ x: 5, y: 6 }); // down
      expect(neighbors).toContainEqual({ x: 4, y: 5 }); // left
      expect(neighbors).toContainEqual({ x: 6, y: 5 }); // right
    });

    it('should return 2 neighbors for corner (0,0)', () => {
      const neighbors = getNeighbors4(0, 0, 10, 10);
      expect(neighbors).toHaveLength(2);
      expect(neighbors).toContainEqual({ x: 1, y: 0 }); // right
      expect(neighbors).toContainEqual({ x: 0, y: 1 }); // down
    });

    it('should return 3 neighbors for edge point', () => {
      const neighbors = getNeighbors4(0, 5, 10, 10);
      expect(neighbors).toHaveLength(3);
    });
  });

  describe('getNeighbors8', () => {
    it('should return 8 neighbors for center point', () => {
      const neighbors = getNeighbors8(5, 5, 10, 10);
      expect(neighbors).toHaveLength(8);
    });

    it('should return 3 neighbors for corner', () => {
      const neighbors = getNeighbors8(0, 0, 10, 10);
      expect(neighbors).toHaveLength(3);
    });

    it('should return 5 neighbors for edge', () => {
      const neighbors = getNeighbors8(5, 0, 10, 10);
      expect(neighbors).toHaveLength(5);
    });

    it('should not include center point', () => {
      const neighbors = getNeighbors8(5, 5, 10, 10);
      expect(neighbors).not.toContainEqual({ x: 5, y: 5 });
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

    it('should return true for corner', () => {
      expect(isOnEdge(0, 0, 10, 10)).toBe(true);
    });
  });

  describe('getEdgeType', () => {
    it('should return None for center', () => {
      expect(getEdgeType(5, 5, 10, 10)).toBe(EdgeType.None);
    });

    it('should return Left for left edge', () => {
      const edge = getEdgeType(0, 5, 10, 10);
      expect(edge & EdgeType.Left).toBeTruthy();
    });

    it('should return Top|Left for top-left corner', () => {
      const edge = getEdgeType(0, 0, 10, 10);
      expect(edge & EdgeType.Top).toBeTruthy();
      expect(edge & EdgeType.Left).toBeTruthy();
      expect(edge & EdgeType.Right).toBeFalsy();
      expect(edge & EdgeType.Bottom).toBeFalsy();
    });
  });
});
```

### 4. Integration Testing (30 min)
Verify that refactored files still work:

- [ ] Run all snapshot tests (must pass)
- [ ] Run facet creation tests
- [ ] Run border tracing tests
- [ ] Visual inspection of output

```bash
npm test -- --testPathPattern=snapshot
npm test -- --testPathPattern=facet
npm test -- --testPathPattern=border
```

### 5. Documentation (30 min)
- [ ] JSDoc for all functions in boundaryUtils.ts
- [ ] Examples in documentation
- [ ] Update any relevant documentation

---

## 🧪 Validation Criteria

**All of these must pass for manager approval:**

### Technical Validation
1. ✅ All boundary utility functions implemented
2. ✅ Test coverage ≥95%
3. ✅ All tests pass
4. ✅ All snapshot tests still pass (no regressions)
5. ✅ Boundary checks in priority files replaced

### Code Quality
1. ✅ Functions are pure (no side effects)
2. ✅ Proper TypeScript types
3. ✅ JSDoc comments on all exports
4. ✅ Edge cases handled correctly

### Integration
1. ✅ Refactored files use utilities correctly
2. ✅ No duplicate boundary checking logic remains
3. ✅ Code is more readable than before

---

## 🚀 Implementation Guide

### Step 1: Create boundaryUtils.ts (90 min)

Follow the example implementation above. Key points:

**Function Design:**
- Pure functions (no side effects)
- Clear, descriptive names
- Handle edge cases
- Proper types

**Edge Cases to Consider:**
- Empty images (0x0)
- Single pixel images (1x1)
- Negative coordinates
- Large coordinates beyond bounds

### Step 2: Find Boundary Checks (30 min)

```bash
# Search for boundary check patterns
cd /home/user/paintbynumbersgenerator

# Pattern 1: x >= 0 && x < width
grep -rn "x >= 0 && x <" src/ > boundary-checks.txt

# Pattern 2: Clamping
grep -rn "Math.max(0, Math.min" src/ >> boundary-checks.txt

# Pattern 3: Continue on out of bounds
grep -rn "< 0 ||.*>=" src/ >> boundary-checks.txt
```

Review `boundary-checks.txt` and plan replacements.

### Step 3: Replace in Each File (60 min)

**File: src/facetCreator.ts**
```typescript
// Add import
import { isInBounds, getNeighbors4 } from './lib/boundaryUtils';

// Replace checks
// BEFORE:
if (x >= 0 && x < width && y >= 0 && y < height) {
  // ...
}

// AFTER:
if (isInBounds(x, y, width, height)) {
  // ...
}
```

**File: src/lib/fill.ts (flood fill)**
```typescript
// BEFORE: Manual neighbor checking
const neighbors = [];
if (x > 0) neighbors.push({ x: x - 1, y });
if (x < width - 1) neighbors.push({ x: x + 1, y });
// ... etc

// AFTER:
import { getNeighbors4 } from './boundaryUtils';
const neighbors = getNeighbors4(x, y, width, height);
```

### Step 4: Create Tests (60 min)

Use the test examples above. Ensure you test:
- Normal cases
- Edge cases (literally - edges and corners)
- Boundary conditions (0, max)
- Invalid inputs (negative, overflow)

### Step 5: Validate (30 min)

```bash
# Run new tests
npm test -- --testPathPattern=boundaryUtils

# Check coverage
npm test -- --coverage --testPathPattern=boundaryUtils

# Run snapshot tests (must still pass)
npm test -- --testPathPattern=snapshot

# Run all tests
npm test
```

---

## 💡 Tips & Gotchas

### Off-by-One Errors
Common mistake:
```typescript
// WRONG: width is exclusive
if (x >= 0 && x <= width) // Bug! Should be x < width

// RIGHT:
if (x >= 0 && x < width)
```

### Neighbor Order
Be consistent with neighbor order (up, down, left, right) for predictability.

### Edge Type Flags
Use bitwise operations for edge types:
```typescript
const edge = getEdgeType(0, 0, 10, 10);
if (edge & EdgeType.Left) {
  // On left edge
}
```

---

## 📤 Deliverables Checklist

- [ ] `src/lib/boundaryUtils.ts` created with all functions
- [ ] Boundary checks replaced in facetCreator.ts
- [ ] Boundary checks replaced in facetBorderTracer.ts
- [ ] Boundary checks replaced in facetBorderSegmenter.ts
- [ ] Boundary checks replaced in lib/fill.ts
- [ ] Unit tests created (≥95% coverage)
- [ ] All tests pass
- [ ] All snapshot tests pass
- [ ] JSDoc comments complete
- [ ] Code committed to git
- [ ] Updated PROJECT_TRACKER.md

---

## 🔄 Handoff Notes

**For Manager:**
- Verify no duplicate boundary logic remains
- Check snapshot tests pass (proves no functional changes)
- Verify test coverage ≥95%

**For Next AI Devs:**
- Use boundaryUtils functions in all future code
- Don't write manual boundary checks
- Functions are well-tested and reliable

---

## 📝 AI Dev Updates

**Started:** [Date/Time]

**Progress Notes:**
- [Update as you work]

**Completed:** [Date/Time]

**Actual Hours:** [Hours]

**Deviations:**
- [Any changes]

**Issues:**
- [Problems encountered]

---

**Last Updated:** 2025-11-05
**Version:** 1.0
