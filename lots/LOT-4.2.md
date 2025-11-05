# LOT 4.2: Settings & Configuration Refactor

**Phase:** 4 - Pipeline Orchestration
**Estimated Time:** 3 hours
**Priority:** MEDIUM
**Dependencies:** LOT 2.1 (Constants), LOT 4.1 (Pipeline Manager)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Create type-safe configuration schema with validation, using constants from LOT 2.1.

---

## ✅ Deliverables

### 1. Type-Safe Configuration Schema (60 min)
- [ ] Use Zod or io-ts for runtime validation
- [ ] Create Configuration interface
- [ ] Default configuration from constants

### 2. Settings Validator (45 min)
- [ ] Validation rules
- [ ] Clear error messages
- [ ] Type checking

### 3. Refactor settings.ts (45 min)
- [ ] Use new configuration system
- [ ] Backward compatibility
- [ ] Migration from old settings

### 4. Tests (30 min)
- [ ] Valid configuration tests
- [ ] Invalid configuration rejection
- [ ] Default settings tests

---

## 🧪 Validation Criteria

1. ✅ Invalid settings rejected with clear errors
2. ✅ Default settings produce identical output
3. ✅ Test coverage ≥95%
4. ✅ All snapshot tests pass

---

## 🚀 Implementation Example

```typescript
import { ColorSpace, CLUSTERING_DEFAULTS, FACET_THRESHOLDS } from './lib/constants';

export interface Config {
  colorCount: number;
  colorSpace: ColorSpace;
  minFacetSize: number;
  maxFacetCount: number;
  enableSmoothing: boolean;
  randomSeed?: number;
}

export const DEFAULT_CONFIG: Config = {
  colorCount: CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT,
  colorSpace: ColorSpace.RGB,
  minFacetSize: FACET_THRESHOLDS.MIN_FACET_SIZE,
  maxFacetCount: FACET_THRESHOLDS.MAX_FACET_COUNT,
  enableSmoothing: true,
};

export function validateConfig(config: Config): string[] {
  const errors: string[] = [];

  if (config.colorCount < 2 || config.colorCount > 256) {
    errors.push('colorCount must be between 2 and 256');
  }

  if (config.minFacetSize < 1) {
    errors.push('minFacetSize must be at least 1');
  }

  return errors;
}
```

---

## 📤 Deliverables Checklist

- [ ] Configuration schema created
- [ ] Validation implemented
- [ ] settings.ts refactored
- [ ] Tests ≥95% coverage
- [ ] Documentation complete
- [ ] Code committed
- [ ] PROJECT_TRACKER.md updated

---

**Last Updated:** 2025-11-05
**Version:** 1.0
