# LOT 2.3: Color Space Utilities Refactor

**Phase:** 2 - Extract Common Utilities
**Estimated Time:** 5 hours
**Priority:** HIGH
**Dependencies:** LOT 1.2, LOT 2.1 (Constants)
**Assigned To:** _[AI Dev will write name here]_

---

## 🎯 Objective

Refactor color space conversion utilities into a clean, class-based design that eliminates code duplication and makes color operations more intuitive and type-safe.

---

## 📋 Context

**Current State:**
- Color conversion functions in `src/lib/colorconversion.ts`
- Color distance calculations scattered in `colorreductionmanagement.ts`
- Duplicate logic for RGB ↔ HSL ↔ LAB conversions
- No unified Color abstraction

**Why This Matters:**
- Color operations are central to the algorithm
- Distance calculations used in K-means clustering
- Type safety prevents color space mixing bugs
- Single source of truth for conversions

---

## ✅ Deliverables

### 1. Create Color Class (120 min)
Refactor `src/lib/colorconversion.ts` into class-based design:

```typescript
export interface RGB {
  r: number; // 0-255
  g: number;
  b: number;
}

export interface HSL {
  h: number; // 0-360
  s: number; // 0-100
  l: number; // 0-100
}

export interface LAB {
  l: number; // 0-100
  a: number; // -128 to 127
  b: number; // -128 to 127
}

export class Color {
  private rgb: RGB;

  private constructor(rgb: RGB) {
    this.rgb = rgb;
  }

  // Factory methods
  static fromRGB(r: number, g: number, b: number): Color;
  static fromHSL(h: number, s: number, l: number): Color;
  static fromLAB(l: number, a: number, b: number): Color;

  // Getters
  toRGB(): RGB;
  toHSL(): HSL;
  toLAB(): LAB;

  // Distance calculations
  distanceTo(other: Color, space: ColorSpace): number;
  distanceRGB(other: Color): number;
  distanceHSL(other: Color): number;
  distanceLAB(other: Color): number;

  // Utilities
  clone(): Color;
  equals(other: Color): boolean;
  toHex(): string;
}
```

### 2. Extract Color Distance Calculations (60 min)
From `colorreductionmanagement.ts` extract distance logic:

- [ ] RGB Euclidean distance
- [ ] HSL weighted distance
- [ ] LAB perceptual distance (Delta E)
- [ ] Move to Color class

### 3. Update Existing Code (90 min)
Update files to use new Color class:

- [ ] `colorreductionmanagement.ts`
- [ ] `lib/clustering.ts` (Vector class)
- [ ] Any other files using color conversions

### 4. Tests (60 min)
- [ ] Unit tests for all conversions
- [ ] Test known color values (e.g., RGB(255,0,0) = HSL(0,100,50))
- [ ] Test distance calculations
- [ ] Integration tests with K-means

### 5. Documentation (30 min)
- [ ] JSDoc for Color class
- [ ] Examples of usage
- [ ] Color space explanations

---

## 🧪 Validation Criteria

1. ✅ All color conversions produce identical results (±0.1 tolerance)
2. ✅ K-means clustering produces identical output
3. ✅ Test coverage ≥90%
4. ✅ All snapshot tests pass
5. ✅ API is cleaner than before

---

## 🚀 Implementation Guide

### Step 1: Create Color Class

```typescript
// src/lib/color.ts
import { ColorSpace } from './constants';

export class Color {
  private rgb: RGB;

  private constructor(rgb: RGB) {
    this.rgb = rgb;
  }

  static fromRGB(r: number, g: number, b: number): Color {
    return new Color({ r, g, b });
  }

  static fromHSL(h: number, s: number, l: number): Color {
    // Use existing conversion logic from colorconversion.ts
    const rgb = hslToRgb(h, s, l);
    return new Color(rgb);
  }

  static fromLAB(l: number, a: number, b: number): Color {
    // Use existing conversion logic
    const rgb = labToRgb(l, a, b);
    return new Color(rgb);
  }

  toRGB(): RGB {
    return { ...this.rgb };
  }

  toHSL(): HSL {
    return rgbToHsl(this.rgb.r, this.rgb.g, this.rgb.b);
  }

  toLAB(): LAB {
    return rgbToLab(this.rgb.r, this.rgb.g, this.rgb.b);
  }

  distanceTo(other: Color, space: ColorSpace): number {
    switch (space) {
      case ColorSpace.RGB:
        return this.distanceRGB(other);
      case ColorSpace.HSL:
        return this.distanceHSL(other);
      case ColorSpace.LAB:
        return this.distanceLAB(other);
    }
  }

  distanceRGB(other: Color): number {
    const dr = this.rgb.r - other.rgb.r;
    const dg = this.rgb.g - other.rgb.g;
    const db = this.rgb.b - other.rgb.b;
    return Math.sqrt(dr * dr + dg * dg + db * db);
  }

  // ... implement distanceHSL, distanceLAB
}
```

### Step 2: Write Tests

```typescript
describe('Color class', () => {
  it('should convert RGB red to HSL', () => {
    const color = Color.fromRGB(255, 0, 0);
    const hsl = color.toHSL();
    expect(hsl.h).toBeCloseTo(0);
    expect(hsl.s).toBeCloseTo(100);
    expect(hsl.l).toBeCloseTo(50);
  });

  it('should calculate RGB distance', () => {
    const c1 = Color.fromRGB(0, 0, 0);
    const c2 = Color.fromRGB(255, 255, 255);
    const dist = c1.distanceRGB(c2);
    expect(dist).toBeCloseTo(441.67, 1);
  });
});
```

---

## 📤 Deliverables Checklist

- [ ] Color class implemented
- [ ] All conversions working
- [ ] Distance calculations moved
- [ ] Existing code updated
- [ ] Tests ≥90% coverage
- [ ] All snapshot tests pass
- [ ] Documentation complete
- [ ] Code committed
- [ ] PROJECT_TRACKER.md updated

---

**Last Updated:** 2025-11-05
**Version:** 1.0
