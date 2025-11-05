# LOT 2.1: Configuration & Constants Module

**Phase:** 2 - Extract Common Utilities
**Estimated Time:** 3 hours
**Priority:** HIGH
**Dependencies:** LOT 1.2 (Snapshot & Benchmark)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Eliminate all magic numbers and hardcoded configuration values by creating centralized constants and configuration modules. This improves code maintainability and makes the codebase easier to understand.

---

## 📋 Context

**Current State:**
- Magic numbers scattered throughout codebase:
  - Bit shifting values (2, 4, 8)
  - Update intervals (500ms)
  - Default parameters (16 colors, clustering iterations)
  - Color space identifiers (0, 1, 2)
  - Threshold values

**Examples of Magic Numbers Found:**
```typescript
// src/colorreductionmanagement.ts
if (colorSpace === 0) { // What is 0?
  // RGB
} else if (colorSpace === 1) { // What is 1?
  // HSL
}

// src/guiprocessmanager.ts
setTimeout(updateProgress, 500); // Why 500?

// src/facetReducer.ts
if (facetSize < 10) { // Why 10?
  removeFacet();
}
```

**Why This Matters:**
- Magic numbers make code hard to understand
- Changes require finding all occurrences
- Easy to introduce bugs when values are duplicated
- No single source of truth for configuration

---

## ✅ Deliverables

### 1. Create Constants Module (60 min)
Create `src/lib/constants.ts`:

- [ ] Color space enums
- [ ] Bit manipulation constants
- [ ] Timing constants (update intervals)
- [ ] Default algorithm parameters
- [ ] Threshold values
- [ ] File format constants

**Example Structure:**
```typescript
/**
 * Color space identifiers for clustering algorithms
 */
export enum ColorSpace {
  RGB = 0,
  HSL = 1,
  LAB = 2,
}

/**
 * Default parameters for K-means clustering
 */
export const CLUSTERING_DEFAULTS = {
  /** Maximum number of clustering iterations */
  MAX_ITERATIONS: 100,

  /** Convergence threshold for cluster centers */
  CONVERGENCE_THRESHOLD: 0.001,

  /** Default number of color clusters */
  DEFAULT_COLOR_COUNT: 16,
} as const;

/**
 * UI update intervals in milliseconds
 */
export const UPDATE_INTERVALS = {
  /** Progress bar update interval */
  PROGRESS_UPDATE_MS: 500,

  /** Debounce delay for user input */
  INPUT_DEBOUNCE_MS: 300,
} as const;

/**
 * Facet processing thresholds
 */
export const FACET_THRESHOLDS = {
  /** Minimum facet size in pixels before removal */
  MIN_FACET_SIZE: 10,

  /** Maximum facet count before forced reduction */
  MAX_FACET_COUNT: 1000,
} as const;

// ... more constants
```

### 2. Create Runtime Configuration Module (45 min)
Create `src/lib/config.ts`:

- [ ] Configuration interface
- [ ] Default configuration object
- [ ] Configuration validation
- [ ] Configuration merge utility

**Example Structure:**
```typescript
import { CLUSTERING_DEFAULTS, FACET_THRESHOLDS } from './constants';

/**
 * Runtime configuration for the paint-by-numbers generator
 */
export interface PaintByNumbersConfig {
  /** Number of colors in the final output */
  colorCount: number;

  /** Color space for clustering */
  colorSpace: ColorSpace;

  /** K-means clustering iterations */
  clusteringIterations: number;

  /** Minimum facet size in pixels */
  minFacetSize: number;

  /** Enable border smoothing */
  enableSmoothing: boolean;

  // ... other config options
}

/**
 * Default configuration using constants
 */
export const DEFAULT_CONFIG: PaintByNumbersConfig = {
  colorCount: CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT,
  colorSpace: ColorSpace.RGB,
  clusteringIterations: CLUSTERING_DEFAULTS.MAX_ITERATIONS,
  minFacetSize: FACET_THRESHOLDS.MIN_FACET_SIZE,
  enableSmoothing: true,
};

/**
 * Merge user config with defaults
 */
export function mergeConfig(
  userConfig: Partial<PaintByNumbersConfig>
): PaintByNumbersConfig {
  return {
    ...DEFAULT_CONFIG,
    ...userConfig,
  };
}

/**
 * Validate configuration values
 */
export function validateConfig(config: PaintByNumbersConfig): string[] {
  const errors: string[] = [];

  if (config.colorCount < 2 || config.colorCount > 256) {
    errors.push('colorCount must be between 2 and 256');
  }

  if (config.minFacetSize < 1) {
    errors.push('minFacetSize must be at least 1');
  }

  // ... more validation

  return errors;
}
```

### 3. Find and Replace Magic Numbers (60 min)
Search for magic numbers in these files and replace:

**Priority Files:**
- [ ] `src/colorreductionmanagement.ts` - Color space enums
- [ ] `src/guiprocessmanager.ts` - Update intervals
- [ ] `src/facetReducer.ts` - Threshold values
- [ ] `src/facetBorderSegmenter.ts` - Algorithm parameters
- [ ] `src/settings.ts` - Default values

**Search Strategy:**
```bash
# Find numeric literals that might be magic numbers
grep -rn "\b[0-9]\+\b" src/ --include="*.ts" | grep -v "^.*//.*[0-9]" | grep -v "node_modules"

# Look for specific patterns
grep -rn "colorSpace ===" src/
grep -rn "setTimeout" src/
grep -rn "< [0-9]" src/
```

**Replace Example:**
```typescript
// BEFORE:
if (colorSpace === 0) {
  // RGB
}

// AFTER:
import { ColorSpace } from './lib/constants';

if (colorSpace === ColorSpace.RGB) {
  // RGB
}
```

### 4. Update Existing Settings Module (30 min)
Refactor `src/settings.ts` to use new constants:

- [ ] Import constants from new module
- [ ] Replace hardcoded defaults with constant references
- [ ] Add validation using new validation functions
- [ ] Ensure backward compatibility

### 5. Tests (30 min)
Create `tests/unit/lib/constants.test.ts`:
- [ ] Test that constants are properly defined
- [ ] Test that enums have correct values
- [ ] Test configuration validation
- [ ] Test configuration merging

Create `tests/unit/lib/config.test.ts`:
- [ ] Test default config
- [ ] Test config merging
- [ ] Test config validation (valid cases)
- [ ] Test config validation (invalid cases)

### 6. Documentation (15 min)
- [ ] JSDoc for all exports in constants.ts
- [ ] JSDoc for all exports in config.ts
- [ ] Update README if needed
- [ ] Document migration from old to new constants

---

## 🧪 Validation Criteria

**All of these must pass for manager approval:**

### Technical Validation
1. ✅ All constants are defined with proper types
2. ✅ All magic numbers in priority files are replaced
3. ✅ Configuration validation works correctly
4. ✅ All snapshot tests still pass (no functional changes)
5. ✅ No hardcoded values remain in refactored files

### Code Quality
1. ✅ Constants are well-organized and grouped logically
2. ✅ JSDoc comments explain the purpose of each constant
3. ✅ Enums use descriptive names
4. ✅ No `any` types used

### Testing
1. ✅ Test coverage ≥95% for new modules
2. ✅ All tests pass
3. ✅ Invalid config values are properly rejected

---

## 🚀 Implementation Guide

### Step 1: Create Constants Module (60 min)

**Create file:** `src/lib/constants.ts`

Start by identifying all magic numbers in the codebase:

```bash
# Search for potential magic numbers
cd /home/user/paintbynumbersgenerator
grep -rn "colorSpace ===" src/ > magic-numbers.txt
grep -rn "setTimeout" src/ >> magic-numbers.txt
grep -rn "if.*< [0-9]" src/ >> magic-numbers.txt
```

Review `magic-numbers.txt` and categorize:
1. Color space identifiers
2. Timing values
3. Thresholds
4. Algorithm parameters
5. Bit manipulation constants

Create the constants file:
```typescript
/**
 * Constants and enums for Paint by Numbers Generator
 *
 * This module centralizes all magic numbers and configuration constants
 * to improve maintainability and code clarity.
 *
 * @module constants
 */

/**
 * Color space identifiers for clustering algorithms
 */
export enum ColorSpace {
  /** RGB color space (Red, Green, Blue) */
  RGB = 0,

  /** HSL color space (Hue, Saturation, Lightness) */
  HSL = 1,

  /** LAB color space (Lightness, A, B) */
  LAB = 2,
}

/**
 * Default parameters for K-means clustering
 */
export const CLUSTERING_DEFAULTS = {
  /** Maximum number of clustering iterations */
  MAX_ITERATIONS: 100,

  /** Convergence threshold for cluster centers */
  CONVERGENCE_THRESHOLD: 0.001,

  /** Default number of color clusters */
  DEFAULT_COLOR_COUNT: 16,

  /** Minimum number of colors allowed */
  MIN_COLOR_COUNT: 2,

  /** Maximum number of colors allowed */
  MAX_COLOR_COUNT: 256,
} as const;

/**
 * UI update intervals in milliseconds
 */
export const UPDATE_INTERVALS = {
  /** Progress bar update interval during processing */
  PROGRESS_UPDATE_MS: 500,

  /** Debounce delay for user input changes */
  INPUT_DEBOUNCE_MS: 300,
} as const;

/**
 * Facet processing thresholds
 */
export const FACET_THRESHOLDS = {
  /** Minimum facet size in pixels before removal */
  MIN_FACET_SIZE: 10,

  /** Maximum facet count before forced reduction */
  MAX_FACET_COUNT: 1000,

  /** Minimum border point count for a valid facet */
  MIN_BORDER_POINTS: 3,
} as const;

/**
 * Bit manipulation constants for pixel data processing
 */
export const BIT_CONSTANTS = {
  /** Number of bits per color channel in RGB */
  BITS_PER_CHANNEL: 8,

  /** Maximum value for 8-bit color channel */
  MAX_CHANNEL_VALUE: 255,

  /** Bit shift for RGBA packing */
  RGBA_SHIFT: 2,
} as const;

/**
 * Image processing constants
 */
export const IMAGE_CONSTANTS = {
  /** Default JPEG quality for exports */
  JPEG_QUALITY: 0.95,

  /** Default PNG compression level */
  PNG_COMPRESSION: 6,

  /** Maximum image dimension before warning */
  MAX_DIMENSION_WARNING: 2000,
} as const;
```

### Step 2: Create Configuration Module (45 min)

**Create file:** `src/lib/config.ts`

```typescript
import { ColorSpace, CLUSTERING_DEFAULTS, FACET_THRESHOLDS } from './constants';

/**
 * Runtime configuration for the paint-by-numbers generator
 */
export interface PaintByNumbersConfig {
  /** Number of colors in the final output */
  colorCount: number;

  /** Color space for clustering */
  colorSpace: ColorSpace;

  /** K-means clustering iterations */
  clusteringIterations: number;

  /** Minimum facet size in pixels */
  minFacetSize: number;

  /** Maximum number of facets */
  maxFacetCount: number;

  /** Enable border smoothing */
  enableSmoothing: boolean;

  /** Random seed for reproducible results (undefined = random) */
  randomSeed?: number;
}

/**
 * Default configuration using constants
 */
export const DEFAULT_CONFIG: Readonly<PaintByNumbersConfig> = {
  colorCount: CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT,
  colorSpace: ColorSpace.RGB,
  clusteringIterations: CLUSTERING_DEFAULTS.MAX_ITERATIONS,
  minFacetSize: FACET_THRESHOLDS.MIN_FACET_SIZE,
  maxFacetCount: FACET_THRESHOLDS.MAX_FACET_COUNT,
  enableSmoothing: true,
  randomSeed: undefined,
};

/**
 * Merge user configuration with defaults
 *
 * @param userConfig - Partial configuration provided by user
 * @returns Complete configuration with defaults filled in
 */
export function mergeConfig(
  userConfig: Partial<PaintByNumbersConfig>
): PaintByNumbersConfig {
  return {
    ...DEFAULT_CONFIG,
    ...userConfig,
  };
}

/**
 * Validate configuration values
 *
 * @param config - Configuration to validate
 * @returns Array of error messages (empty if valid)
 */
export function validateConfig(config: PaintByNumbersConfig): string[] {
  const errors: string[] = [];

  if (config.colorCount < CLUSTERING_DEFAULTS.MIN_COLOR_COUNT ||
      config.colorCount > CLUSTERING_DEFAULTS.MAX_COLOR_COUNT) {
    errors.push(
      `colorCount must be between ${CLUSTERING_DEFAULTS.MIN_COLOR_COUNT} ` +
      `and ${CLUSTERING_DEFAULTS.MAX_COLOR_COUNT}`
    );
  }

  if (config.clusteringIterations < 1) {
    errors.push('clusteringIterations must be at least 1');
  }

  if (config.minFacetSize < 1) {
    errors.push('minFacetSize must be at least 1');
  }

  if (config.maxFacetCount < 1) {
    errors.push('maxFacetCount must be at least 1');
  }

  if (![ColorSpace.RGB, ColorSpace.HSL, ColorSpace.LAB].includes(config.colorSpace)) {
    errors.push('colorSpace must be RGB, HSL, or LAB');
  }

  return errors;
}

/**
 * Assert configuration is valid (throws on error)
 *
 * @param config - Configuration to validate
 * @throws Error if configuration is invalid
 */
export function assertValidConfig(config: PaintByNumbersConfig): void {
  const errors = validateConfig(config);
  if (errors.length > 0) {
    throw new Error(`Invalid configuration:\n${errors.join('\n')}`);
  }
}
```

### Step 3: Find and Replace Magic Numbers (60 min)

**File: `src/colorreductionmanagement.ts`**

Search for:
```bash
grep -n "=== 0\|=== 1\|=== 2" src/colorreductionmanagement.ts
```

Replace:
```typescript
// BEFORE:
if (colorSpace === 0) {
  // RGB logic
} else if (colorSpace === 1) {
  // HSL logic
} else if (colorSpace === 2) {
  // LAB logic
}

// AFTER:
import { ColorSpace } from './lib/constants';

if (colorSpace === ColorSpace.RGB) {
  // RGB logic
} else if (colorSpace === ColorSpace.HSL) {
  // HSL logic
} else if (colorSpace === ColorSpace.LAB) {
  // LAB logic
}
```

**File: `src/guiprocessmanager.ts`**

Replace:
```typescript
// BEFORE:
setTimeout(() => this.updateProgress(), 500);

// AFTER:
import { UPDATE_INTERVALS } from './lib/constants';

setTimeout(() => this.updateProgress(), UPDATE_INTERVALS.PROGRESS_UPDATE_MS);
```

**File: `src/facetReducer.ts`**

Replace:
```typescript
// BEFORE:
if (facetSize < 10) {
  removeFacet();
}

// AFTER:
import { FACET_THRESHOLDS } from './lib/constants';

if (facetSize < FACET_THRESHOLDS.MIN_FACET_SIZE) {
  removeFacet();
}
```

Repeat for all priority files.

### Step 4: Update Settings Module (30 min)

**File: `src/settings.ts`**

```typescript
// Add imports
import { ColorSpace, CLUSTERING_DEFAULTS, FACET_THRESHOLDS } from './lib/constants';
import { validateConfig } from './lib/config';

// Update defaults
export class Settings {
  public kMeansNrOfClusters: number = CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT;
  public colorSpace: ColorSpace = ColorSpace.RGB;
  public minFacetSize: number = FACET_THRESHOLDS.MIN_FACET_SIZE;
  // ... etc

  /**
   * Validate settings
   */
  public validate(): string[] {
    return validateConfig(this);
  }
}
```

### Step 5: Create Tests (30 min)

**File: `tests/unit/lib/constants.test.ts`**

```typescript
import { ColorSpace, CLUSTERING_DEFAULTS, FACET_THRESHOLDS } from '../../../src/lib/constants';

describe('Constants', () => {
  describe('ColorSpace enum', () => {
    it('should have RGB as 0', () => {
      expect(ColorSpace.RGB).toBe(0);
    });

    it('should have HSL as 1', () => {
      expect(ColorSpace.HSL).toBe(1);
    });

    it('should have LAB as 2', () => {
      expect(ColorSpace.LAB).toBe(2);
    });
  });

  describe('CLUSTERING_DEFAULTS', () => {
    it('should have sensible default color count', () => {
      expect(CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT).toBe(16);
      expect(CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT).toBeGreaterThanOrEqual(
        CLUSTERING_DEFAULTS.MIN_COLOR_COUNT
      );
      expect(CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT).toBeLessThanOrEqual(
        CLUSTERING_DEFAULTS.MAX_COLOR_COUNT
      );
    });

    it('should have positive iteration count', () => {
      expect(CLUSTERING_DEFAULTS.MAX_ITERATIONS).toBeGreaterThan(0);
    });
  });

  describe('FACET_THRESHOLDS', () => {
    it('should have positive min facet size', () => {
      expect(FACET_THRESHOLDS.MIN_FACET_SIZE).toBeGreaterThan(0);
    });

    it('should have reasonable max facet count', () => {
      expect(FACET_THRESHOLDS.MAX_FACET_COUNT).toBeGreaterThan(100);
    });
  });
});
```

**File: `tests/unit/lib/config.test.ts`**

```typescript
import {
  DEFAULT_CONFIG,
  mergeConfig,
  validateConfig,
  assertValidConfig,
} from '../../../src/lib/config';
import { ColorSpace } from '../../../src/lib/constants';

describe('Configuration', () => {
  describe('DEFAULT_CONFIG', () => {
    it('should have valid default values', () => {
      const errors = validateConfig(DEFAULT_CONFIG);
      expect(errors).toHaveLength(0);
    });
  });

  describe('mergeConfig', () => {
    it('should merge partial config with defaults', () => {
      const userConfig = { colorCount: 20 };
      const merged = mergeConfig(userConfig);

      expect(merged.colorCount).toBe(20);
      expect(merged.colorSpace).toBe(DEFAULT_CONFIG.colorSpace);
      expect(merged.enableSmoothing).toBe(DEFAULT_CONFIG.enableSmoothing);
    });

    it('should not mutate default config', () => {
      const original = { ...DEFAULT_CONFIG };
      mergeConfig({ colorCount: 99 });
      expect(DEFAULT_CONFIG).toEqual(original);
    });
  });

  describe('validateConfig', () => {
    it('should accept valid configuration', () => {
      const config = { ...DEFAULT_CONFIG };
      const errors = validateConfig(config);
      expect(errors).toHaveLength(0);
    });

    it('should reject colorCount < 2', () => {
      const config = { ...DEFAULT_CONFIG, colorCount: 1 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('colorCount');
    });

    it('should reject colorCount > 256', () => {
      const config = { ...DEFAULT_CONFIG, colorCount: 999 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('colorCount');
    });

    it('should reject negative minFacetSize', () => {
      const config = { ...DEFAULT_CONFIG, minFacetSize: -1 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('minFacetSize');
    });

    it('should reject invalid color space', () => {
      const config = { ...DEFAULT_CONFIG, colorSpace: 999 as ColorSpace };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('colorSpace');
    });
  });

  describe('assertValidConfig', () => {
    it('should not throw for valid config', () => {
      expect(() => assertValidConfig(DEFAULT_CONFIG)).not.toThrow();
    });

    it('should throw for invalid config', () => {
      const config = { ...DEFAULT_CONFIG, colorCount: -1 };
      expect(() => assertValidConfig(config)).toThrow('Invalid configuration');
    });
  });
});
```

### Step 6: Run Validation (15 min)

```bash
# Run all tests
npm test

# Check that snapshot tests still pass
npm test -- --testPathPattern=snapshot

# Run new tests specifically
npm test -- --testPathPattern=constants
npm test -- --testPathPattern=config

# Check coverage
npm test -- --coverage --testPathPattern="constants|config"
```

---

## 💡 Tips & Gotchas

### What Counts as a Magic Number?
**YES (replace these):**
- Thresholds: `if (size < 10)`
- Enum-like values: `colorSpace === 0`
- Configuration: `setTimeout(..., 500)`
- Bit manipulation: `value >> 2`

**NO (keep these):**
- Array indices: `array[0]`, `array[1]`
- Mathematical constants: `x / 2`, `y * 100`
- Boolean conversions: `!!value`, `value ? 1 : 0`
- Loop counters: `for (let i = 0; i < n; i++)`

### Using `as const`
```typescript
export const MY_CONSTANTS = {
  VALUE: 42,
} as const;
```
The `as const` makes the object deeply readonly and preserves literal types.

### Enum vs Object
**Use Enum when:**
- Values represent distinct categories
- Need type safety
- Want autocomplete

**Use Object when:**
- Related configuration values
- Want to group logically
- Don't need nominal typing

---

## 📤 Deliverables Checklist

- [ ] `src/lib/constants.ts` created with all constants
- [ ] `src/lib/config.ts` created with config utilities
- [ ] Magic numbers replaced in priority files
- [ ] `src/settings.ts` updated to use constants
- [ ] Unit tests created for constants
- [ ] Unit tests created for config utilities
- [ ] Test coverage ≥95% for new modules
- [ ] All tests pass (including snapshots)
- [ ] JSDoc comments on all exports
- [ ] Code committed to git
- [ ] Updated `PROJECT_TRACKER.md`

---

## 🔄 Handoff Notes

**For Manager:**
- Verify no magic numbers remain in refactored files
- Check that snapshot tests pass (proves no functional changes)
- Review constant names for clarity

**For Next AI Devs:**
- Use constants from `src/lib/constants.ts` in your code
- Don't add new magic numbers - add to constants instead
- Use config utilities for validation

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
