/**
 * Color class for type-safe color operations and conversions
 *
 * Provides a unified interface for working with colors in different color spaces
 * (RGB, HSL, LAB). Internally stores colors as RGB and converts on demand.
 *
 * @module Color
 */

import { rgbToHsl, hslToRgb, rgb2lab, lab2rgb } from './colorconversion';
import { ColorSpace } from './constants';

/**
 * RGB color representation (0-255 per channel)
 */
export interface RGB {
  /** Red channel (0-255) */
  r: number;
  /** Green channel (0-255) */
  g: number;
  /** Blue channel (0-255) */
  b: number;
}

/**
 * HSL color representation
 * H: 0-1 (hue as fraction of 360°)
 * S: 0-1 (saturation as fraction)
 * L: 0-1 (lightness as fraction)
 */
export interface HSL {
  /** Hue (0-1, represents 0-360°) */
  h: number;
  /** Saturation (0-1, represents 0-100%) */
  s: number;
  /** Lightness (0-1, represents 0-100%) */
  l: number;
}

/**
 * LAB color representation (perceptually uniform)
 * L: 0-100 (lightness)
 * A: -128 to 127 (green-red)
 * B: -128 to 127 (blue-yellow)
 */
export interface LAB {
  /** Lightness (0-100) */
  l: number;
  /** Green-red axis (-128 to 127) */
  a: number;
  /** Blue-yellow axis (-128 to 127) */
  b: number;
}

/**
 * Immutable Color class with conversions between RGB, HSL, and LAB color spaces
 *
 * @example
 * ```typescript
 * // Create colors
 * const red = Color.fromRGB(255, 0, 0);
 * const blue = Color.fromHSL(240, 100, 50);
 *
 * // Convert between spaces
 * const hsl = red.toHSL();
 * const lab = red.toLAB();
 *
 * // Calculate distances
 * const distance = red.distanceRGB(blue);
 * const perceptual = red.distanceLAB(blue);
 *
 * // Utilities
 * const hex = red.toHex(); // "#ff0000"
 * const equal = red.equals(Color.fromRGB(255, 0, 0)); // true
 * ```
 */
export class Color {
  private rgb: RGB;

  /**
   * Private constructor - use factory methods instead
   * @private
   */
  private constructor(rgb: RGB) {
    this.rgb = {
      r: Math.round(Math.max(0, Math.min(255, rgb.r))),
      g: Math.round(Math.max(0, Math.min(255, rgb.g))),
      b: Math.round(Math.max(0, Math.min(255, rgb.b))),
    };
  }

  /**
   * Create color from RGB values
   *
   * @param r - Red (0-255)
   * @param g - Green (0-255)
   * @param b - Blue (0-255)
   * @returns New Color instance
   *
   * @example
   * ```typescript
   * const red = Color.fromRGB(255, 0, 0);
   * const white = Color.fromRGB(255, 255, 255);
   * ```
   */
  static fromRGB(r: number, g: number, b: number): Color {
    return new Color({ r, g, b });
  }

  /**
   * Create color from HSL values
   *
   * @param h - Hue (0-1, represents 0-360°)
   * @param s - Saturation (0-1, represents 0-100%)
   * @param l - Lightness (0-1, represents 0-100%)
   * @returns New Color instance
   *
   * @example
   * ```typescript
   * const red = Color.fromHSL(0, 1, 0.5);
   * const cyan = Color.fromHSL(0.5, 1, 0.5);
   * ```
   */
  static fromHSL(h: number, s: number, l: number): Color {
    const rgb = hslToRgb(h, s, l);
    return new Color({ r: rgb[0], g: rgb[1], b: rgb[2] });
  }

  /**
   * Create color from LAB values
   *
   * @param l - Lightness (0-100)
   * @param a - Green-red axis (-128 to 127)
   * @param b - Blue-yellow axis (-128 to 127)
   * @returns New Color instance
   *
   * @example
   * ```typescript
   * const color = Color.fromLAB(50, 25, -50);
   * ```
   */
  static fromLAB(l: number, a: number, b: number): Color {
    const rgb = lab2rgb([l, a, b]);
    return new Color({ r: rgb[0], g: rgb[1], b: rgb[2] });
  }

  /**
   * Create color from hex string
   *
   * @param hex - Hex color string (e.g., "#ff0000" or "ff0000")
   * @returns New Color instance
   *
   * @example
   * ```typescript
   * const red = Color.fromHex("#ff0000");
   * const blue = Color.fromHex("0000ff");
   * ```
   */
  static fromHex(hex: string): Color {
    // Remove # if present
    hex = hex.replace(/^#/, '');

    // Parse hex values
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    return new Color({ r, g, b });
  }

  /**
   * Get RGB representation
   *
   * @returns RGB object with r, g, b values (0-255)
   */
  toRGB(): RGB {
    return { ...this.rgb };
  }

  /**
   * Get HSL representation
   *
   * @returns HSL object with h (0-1), s (0-1), l (0-1)
   */
  toHSL(): HSL {
    const hsl = rgbToHsl(this.rgb.r, this.rgb.g, this.rgb.b);
    return { h: hsl[0], s: hsl[1], l: hsl[2] };
  }

  /**
   * Get LAB representation
   *
   * @returns LAB object with l, a, b values
   */
  toLAB(): LAB {
    const lab = rgb2lab([this.rgb.r, this.rgb.g, this.rgb.b]);
    return { l: lab[0], a: lab[1], b: lab[2] };
  }

  /**
   * Calculate distance to another color in specified color space
   *
   * @param other - Color to compare to
   * @param space - Color space to use for distance calculation
   * @returns Euclidean distance in specified space
   *
   * @example
   * ```typescript
   * const red = Color.fromRGB(255, 0, 0);
   * const blue = Color.fromRGB(0, 0, 255);
   *
   * const rgbDist = red.distanceTo(blue, ColorSpace.RGB);
   * const labDist = red.distanceTo(blue, ColorSpace.LAB);
   * ```
   */
  distanceTo(other: Color, space: ColorSpace): number {
    if (space === ColorSpace.RGB) {
      return this.distanceRGB(other);
    } else if (space === ColorSpace.HSL) {
      return this.distanceHSL(other);
    } else if (space === ColorSpace.LAB) {
      return this.distanceLAB(other);
    }
    return this.distanceRGB(other);
  }

  /**
   * Calculate Euclidean distance in RGB space
   *
   * @param other - Color to compare to
   * @returns Distance in RGB space
   */
  distanceRGB(other: Color): number {
    const dr = this.rgb.r - other.rgb.r;
    const dg = this.rgb.g - other.rgb.g;
    const db = this.rgb.b - other.rgb.b;
    return Math.sqrt(dr * dr + dg * dg + db * db);
  }

  /**
   * Calculate distance in HSL space
   *
   * Uses weighted distance accounting for hue circularity
   *
   * @param other - Color to compare to
   * @returns Distance in HSL space
   */
  distanceHSL(other: Color): number {
    const hsl1 = this.toHSL();
    const hsl2 = other.toHSL();

    // Handle hue circularity (0 and 1 are adjacent)
    let dh = Math.abs(hsl1.h - hsl2.h);
    if (dh > 0.5) dh = 1 - dh;

    const ds = hsl1.s - hsl2.s;
    const dl = hsl1.l - hsl2.l;

    // Weighted distance (hue more important than saturation/lightness)
    return Math.sqrt(dh * dh * 360 * 360 + ds * ds * 100 * 100 + dl * dl * 100 * 100);
  }

  /**
   * Calculate Delta E distance in LAB space (perceptually uniform)
   *
   * LAB is designed to be perceptually uniform, so Euclidean distance
   * in LAB space approximates perceived color difference
   *
   * @param other - Color to compare to
   * @returns Delta E distance (perceptual color difference)
   */
  distanceLAB(other: Color): number {
    const lab1 = this.toLAB();
    const lab2 = other.toLAB();

    const dl = lab1.l - lab2.l;
    const da = lab1.a - lab2.a;
    const db = lab1.b - lab2.b;

    return Math.sqrt(dl * dl + da * da + db * db);
  }

  /**
   * Create a deep copy of this color
   *
   * @returns New Color instance with same values
   */
  clone(): Color {
    return new Color({ ...this.rgb });
  }

  /**
   * Check if two colors are equal (in RGB space)
   *
   * @param other - Color to compare to
   * @param tolerance - Maximum difference per channel (default: 0)
   * @returns true if colors are equal within tolerance
   *
   * @example
   * ```typescript
   * const c1 = Color.fromRGB(255, 0, 0);
   * const c2 = Color.fromRGB(255, 0, 0);
   * const c3 = Color.fromRGB(254, 0, 0);
   *
   * c1.equals(c2); // true
   * c1.equals(c3); // false
   * c1.equals(c3, 1); // true (within tolerance of 1)
   * ```
   */
  equals(other: Color, tolerance: number = 0): boolean {
    return (
      Math.abs(this.rgb.r - other.rgb.r) <= tolerance &&
      Math.abs(this.rgb.g - other.rgb.g) <= tolerance &&
      Math.abs(this.rgb.b - other.rgb.b) <= tolerance
    );
  }

  /**
   * Convert color to hex string
   *
   * @returns Hex string (e.g., "#ff0000")
   *
   * @example
   * ```typescript
   * const red = Color.fromRGB(255, 0, 0);
   * red.toHex(); // "#ff0000"
   * ```
   */
  toHex(): string {
    const toHex = (n: number) => {
      const hex = Math.round(n).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    };

    return '#' + toHex(this.rgb.r) + toHex(this.rgb.g) + toHex(this.rgb.b);
  }

  /**
   * Get CSS rgb() string
   *
   * @returns CSS rgb string (e.g., "rgb(255, 0, 0)")
   */
  toCSSRGB(): string {
    return `rgb(${Math.round(this.rgb.r)}, ${Math.round(this.rgb.g)}, ${Math.round(this.rgb.b)})`;
  }

  /**
   * Get string representation of color
   *
   * @returns Hex string representation
   */
  toString(): string {
    return this.toHex();
  }
}
