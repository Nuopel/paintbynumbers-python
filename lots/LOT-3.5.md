# LOT 3.5: Facet Reducer Refactor

**Phase:** 3 - Core Algorithm Refactoring
**Estimated Time:** 5 hours
**Priority:** MEDIUM
**Dependencies:** LOT 3.2 (Facet Creation)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Refactor facet reduction logic to separate small facet detection from merge strategy, making the code more extensible and testable.

---

## 📋 Context

**Current:** `facetReducer.ts` (321 lines) - Mixed concerns
**Goal:** Separate facet detection, merge strategies, neighbor finding

---

## ✅ Deliverables

### 1. Extract FacetMergeStrategy (90 min)
- [ ] Create interface for merge strategies
- [ ] Implement current merge logic as strategy
- [ ] Enable future alternative strategies

### 2. Separate SmallFacetDetector (60 min)
- [ ] Extract detection logic
- [ ] Configurable thresholds
- [ ] Clear interface

### 3. Refactor Main Reducer (90 min)
- [ ] Use strategies
- [ ] Simplify neighbor finding
- [ ] Clear control flow

### 4. Tests (60 min)
- [ ] Unit tests for merge strategies
- [ ] Integration tests
- [ ] Snapshot comparison

### 5. Documentation (30 min)
- [ ] JSDoc
- [ ] Algorithm explanation

---

## 🧪 Validation Criteria

1. ✅ Output IDENTICAL to baseline
2. ✅ Test coverage ≥90%
3. ✅ Snapshot tests pass
4. ✅ Code is self-documenting

---

## 🚀 Implementation Example

```typescript
export interface FacetMergeStrategy {
  shouldMerge(facet: Facet, neighbor: Facet): boolean;
  merge(target: Facet, source: Facet): void;
}

export class SmallFacetDetector {
  constructor(private minSize: number) {}

  findSmallFacets(facets: Facet[]): Facet[] {
    return facets.filter(f => f.size < this.minSize);
  }
}

export class FacetReducer {
  constructor(
    private detector: SmallFacetDetector,
    private strategy: FacetMergeStrategy
  ) {}

  reduce(facets: Facet[]): Facet[] {
    const small = this.detector.findSmallFacets(facets);

    for (const facet of small) {
      const neighbor = this.findBestNeighbor(facet, facets);
      if (neighbor && this.strategy.shouldMerge(facet, neighbor)) {
        this.strategy.merge(neighbor, facet);
      }
    }

    return facets.filter(f => f.size >= this.detector.minSize);
  }
}
```

---

## 📤 Deliverables Checklist

- [ ] FacetMergeStrategy interface
- [ ] SmallFacetDetector class
- [ ] FacetReducer refactored
- [ ] Tests ≥90% coverage
- [ ] Snapshot tests pass
- [ ] Documentation complete
- [ ] Code committed
- [ ] PROJECT_TRACKER.md updated

---

**Last Updated:** 2025-11-05
**Version:** 1.0
