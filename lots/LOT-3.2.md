# LOT 3.2: Facet Creation Refactor

**Phase:** 3 - Core Algorithm Refactoring
**Estimated Time:** 5 hours
**Priority:** HIGH
**Dependencies:** LOT 2.2 (Boundary Utilities)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Refactor facet creation logic to separate flood-fill algorithm from facet building, making the code more modular and easier to test.

---

## 📋 Context

**Current State:**
- Facet creation in `src/facetCreator.ts` (185 lines)
- Flood-fill logic in `src/lib/fill.ts`
- Mixed responsibilities: finding regions + building facet objects

**Why This Matters:**
- Flood-fill is reusable algorithm
- Facet building should be separate concern
- Easier to test and maintain

---

## ✅ Deliverables

### 1. Extract FloodFill Algorithm (90 min)
- [ ] Create `src/lib/FloodFillAlgorithm.ts`
- [ ] Extract flood-fill logic from fill.ts
- [ ] Use boundary utilities from LOT 2.2
- [ ] Make algorithm generic and reusable

### 2. Create FacetBuilder Class (120 min)
- [ ] Separate facet construction from region finding
- [ ] Clear interface for facet creation
- [ ] Use FloodFillAlgorithm internally

### 3. Refactor facetCreator.ts (60 min)
- [ ] Use new FloodFillAlgorithm
- [ ] Use new FacetBuilder
- [ ] Clean up code structure

### 4. Tests (60 min)
- [ ] Unit tests for FloodFillAlgorithm
- [ ] Unit tests for FacetBuilder
- [ ] Integration tests for facet creation
- [ ] Snapshot tests (must match exactly)

### 5. Documentation (30 min)
- [ ] JSDoc for all classes
- [ ] Algorithm explanation
- [ ] Usage examples

---

## 🧪 Validation Criteria

**Critical:**
1. ✅ Facet output IDENTICAL to baseline (same count, same boundaries)
2. ✅ All snapshot tests pass
3. ✅ Test coverage ≥90%
4. ✅ Performance within ±5%

---

## 🚀 Implementation Guide

### FloodFillAlgorithm

```typescript
import { isInBounds, getNeighbors4 } from './boundaryUtils';

export class FloodFillAlgorithm {
  /**
   * Flood fill from start point, finding all connected pixels matching predicate
   */
  fill(
    start: Point,
    width: number,
    height: number,
    shouldInclude: (x: number, y: number) => boolean
  ): Point[] {
    const filled: Point[] = [];
    const visited = new Set<number>();
    const stack = [start];

    while (stack.length > 0) {
      const point = stack.pop()!;
      const key = point.y * width + point.x;

      if (visited.has(key)) continue;
      visited.add(key);

      if (!isInBounds(point.x, point.y, width, height)) continue;
      if (!shouldInclude(point.x, point.y)) continue;

      filled.push(point);

      // Add neighbors using utility
      const neighbors = getNeighbors4(point.x, point.y, width, height);
      stack.push(...neighbors);
    }

    return filled;
  }
}
```

### FacetBuilder

```typescript
export class FacetBuilder {
  private floodFill: FloodFillAlgorithm;

  constructor() {
    this.floodFill = new FloodFillAlgorithm();
  }

  /**
   * Build all facets from color-mapped image
   */
  buildFacets(
    colorMap: Uint8Array,
    width: number,
    height: number
  ): Facet[] {
    const visited = new Uint8Array(width * height);
    const facets: Facet[] = [];

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        if (visited[y * width + x]) continue;

        const color = colorMap[y * width + x];
        const points = this.floodFill.fill(
          { x, y },
          width,
          height,
          (px, py) => {
            const idx = py * width + px;
            return !visited[idx] && colorMap[idx] === color;
          }
        );

        // Mark as visited
        points.forEach(p => {
          visited[p.y * width + p.x] = 1;
        });

        facets.push(this.createFacet(points, color));
      }
    }

    return facets;
  }

  private createFacet(points: Point[], colorIndex: number): Facet {
    // Create facet object from points
    return {
      points,
      colorIndex,
      boundingBox: this.calculateBoundingBox(points),
      // ... other properties
    };
  }
}
```

### Tests

```typescript
describe('FloodFillAlgorithm', () => {
  it('should fill connected region', () => {
    const fill = new FloodFillAlgorithm();
    const grid = createTestGrid(10, 10);

    const filled = fill.fill({ x: 0, y: 0 }, 10, 10, (x, y) => grid[y][x] === 1);

    expect(filled.length).toBeGreaterThan(0);
  });

  it('should respect boundaries', () => {
    // Test that it doesn't go out of bounds
  });
});

describe('FacetBuilder', () => {
  it('should produce identical facets to baseline', () => {
    const colorMap = loadTestColorMap();
    const builder = new FacetBuilder();
    const facets = builder.buildFacets(colorMap, 100, 100);

    const snapshot = loadSnapshot('small/02-facets.json');
    expect(facets.length).toBe(snapshot.length);
    // Compare each facet...
  });
});
```

---

## 📤 Deliverables Checklist

- [ ] FloodFillAlgorithm.ts created
- [ ] FacetBuilder.ts created
- [ ] facetCreator.ts refactored
- [ ] Uses boundary utilities
- [ ] Tests ≥90% coverage
- [ ] All snapshot tests pass
- [ ] Performance ±5%
- [ ] Documentation complete
- [ ] Code committed
- [ ] PROJECT_TRACKER.md updated

---

**Last Updated:** 2025-11-05
**Version:** 1.0
