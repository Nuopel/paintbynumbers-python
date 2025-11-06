import { Color } from '../../../src/lib/Color';
import { ColorSpace } from '../../../src/lib/constants';

describe('Color', () => {
  describe('fromRGB', () => {
    it('should create color from RGB values', () => {
      const color = Color.fromRGB(255, 0, 0);
      const rgb = color.toRGB();
      expect(rgb.r).toBe(255);
      expect(rgb.g).toBe(0);
      expect(rgb.b).toBe(0);
    });

    it('should clamp values to 0-255', () => {
      const color1 = Color.fromRGB(300, -10, 128);
      const rgb1 = color1.toRGB();
      expect(rgb1.r).toBe(255);
      expect(rgb1.g).toBe(0);
      expect(rgb1.b).toBe(128);
    });

    it('should round to integers', () => {
      const color = Color.fromRGB(127.6, 64.4, 200.5);
      const rgb = color.toRGB();
      expect(rgb.r).toBe(128);
      expect(rgb.g).toBe(64);
      expect(rgb.b).toBe(201);
    });
  });

  describe('fromHSL', () => {
    it('should create red from HSL(0, 1, 0.5)', () => {
      const color = Color.fromHSL(0, 1, 0.5);
      const rgb = color.toRGB();
      expect(rgb.r).toBe(255);
      expect(rgb.g).toBeCloseTo(0, 0);
      expect(rgb.b).toBeCloseTo(0, 0);
    });

    it('should create green from HSL(0.333, 1, 0.5)', () => {
      const color = Color.fromHSL(1/3, 1, 0.5);
      const rgb = color.toRGB();
      expect(rgb.r).toBeCloseTo(0, 0);
      expect(rgb.g).toBe(255);
      expect(rgb.b).toBeCloseTo(0, 0);
    });

    it('should create blue from HSL(0.666, 1, 0.5)', () => {
      const color = Color.fromHSL(2/3, 1, 0.5);
      const rgb = color.toRGB();
      expect(rgb.r).toBeCloseTo(0, 0);
      expect(rgb.g).toBeCloseTo(0, 0);
      expect(rgb.b).toBe(255);
    });

    it('should create gray from HSL(0, 0, 0.5)', () => {
      const color = Color.fromHSL(0, 0, 0.5);
      const rgb = color.toRGB();
      expect(rgb.r).toBeCloseTo(128, 0);
      expect(rgb.g).toBeCloseTo(128, 0);
      expect(rgb.b).toBeCloseTo(128, 0);
    });
  });

  describe('fromLAB', () => {
    it('should create color from LAB values', () => {
      const color = Color.fromLAB(50, 0, 0);
      const rgb = color.toRGB();
      // Should be a neutral gray
      expect(Math.abs(rgb.r - rgb.g)).toBeLessThan(5);
      expect(Math.abs(rgb.g - rgb.b)).toBeLessThan(5);
    });

    it('should handle extreme LAB values', () => {
      const color = Color.fromLAB(100, 0, 0);
      const rgb = color.toRGB();
      expect(rgb.r).toBeCloseTo(255, 0);
      expect(rgb.g).toBeCloseTo(255, 0);
      expect(rgb.b).toBeCloseTo(255, 0);
    });
  });

  describe('fromHex', () => {
    it('should create color from hex with #', () => {
      const color = Color.fromHex('#ff0000');
      const rgb = color.toRGB();
      expect(rgb.r).toBe(255);
      expect(rgb.g).toBe(0);
      expect(rgb.b).toBe(0);
    });

    it('should create color from hex without #', () => {
      const color = Color.fromHex('00ff00');
      const rgb = color.toRGB();
      expect(rgb.r).toBe(0);
      expect(rgb.g).toBe(255);
      expect(rgb.b).toBe(0);
    });

    it('should handle various hex colors', () => {
      expect(Color.fromHex('#ffffff').toRGB()).toEqual({ r: 255, g: 255, b: 255 });
      expect(Color.fromHex('#000000').toRGB()).toEqual({ r: 0, g: 0, b: 0 });
      expect(Color.fromHex('#808080').toRGB()).toEqual({ r: 128, g: 128, b: 128 });
    });
  });

  describe('toRGB', () => {
    it('should return copy of internal RGB', () => {
      const color = Color.fromRGB(100, 150, 200);
      const rgb = color.toRGB();
      rgb.r = 999; // Modify copy
      expect(color.toRGB().r).toBe(100); // Original unchanged
    });
  });

  describe('toHSL', () => {
    it('should convert red to HSL(0, 1, 0.5)', () => {
      const color = Color.fromRGB(255, 0, 0);
      const hsl = color.toHSL();
      expect(hsl.h).toBeCloseTo(0, 2);
      expect(hsl.s).toBeCloseTo(1, 2);
      expect(hsl.l).toBeCloseTo(0.5, 2);
    });

    it('should convert white to HSL(*, 0, 1)', () => {
      const color = Color.fromRGB(255, 255, 255);
      const hsl = color.toHSL();
      expect(hsl.s).toBeCloseTo(0, 2);
      expect(hsl.l).toBeCloseTo(1, 2);
    });

    it('should convert black to HSL(*, 0, 0)', () => {
      const color = Color.fromRGB(0, 0, 0);
      const hsl = color.toHSL();
      expect(hsl.s).toBeCloseTo(0, 2);
      expect(hsl.l).toBeCloseTo(0, 2);
    });
  });

  describe('toLAB', () => {
    it('should convert to LAB values', () => {
      const color = Color.fromRGB(128, 128, 128);
      const lab = color.toLAB();
      expect(lab.l).toBeGreaterThan(0);
      expect(lab.l).toBeLessThan(100);
      // Neutral gray should have a and b near 0
      expect(Math.abs(lab.a)).toBeLessThan(5);
      expect(Math.abs(lab.b)).toBeLessThan(5);
    });
  });

  describe('distanceRGB', () => {
    it('should calculate RGB distance correctly', () => {
      const red = Color.fromRGB(255, 0, 0);
      const blue = Color.fromRGB(0, 0, 255);

      const distance = red.distanceRGB(blue);
      // Distance should be sqrt(255^2 + 0^2 + 255^2) = sqrt(130050) ≈ 360.62
      expect(distance).toBeCloseTo(360.62, 1);
    });

    it('should return 0 for identical colors', () => {
      const c1 = Color.fromRGB(100, 150, 200);
      const c2 = Color.fromRGB(100, 150, 200);
      expect(c1.distanceRGB(c2)).toBe(0);
    });

    it('should be symmetric', () => {
      const c1 = Color.fromRGB(100, 100, 100);
      const c2 = Color.fromRGB(200, 200, 200);
      expect(c1.distanceRGB(c2)).toBeCloseTo(c2.distanceRGB(c1), 10);
    });
  });

  describe('distanceHSL', () => {
    it('should calculate HSL distance', () => {
      const c1 = Color.fromRGB(255, 0, 0);
      const c2 = Color.fromRGB(0, 255, 0);
      const distance = c1.distanceHSL(c2);
      expect(distance).toBeGreaterThan(0);
    });

    it('should handle hue circularity', () => {
      // Hue 0 and hue 1 should be close (both red)
      const c1 = Color.fromHSL(0, 1, 0.5);
      const c2 = Color.fromHSL(0.99, 1, 0.5);
      const distance = c1.distanceHSL(c2);
      // Should be small due to circularity
      expect(distance).toBeLessThan(10);
    });

    it('should be symmetric', () => {
      const c1 = Color.fromHSL(0.2, 0.5, 0.5);
      const c2 = Color.fromHSL(0.8, 0.7, 0.3);
      expect(c1.distanceHSL(c2)).toBeCloseTo(c2.distanceHSL(c1), 10);
    });
  });

  describe('distanceLAB', () => {
    it('should calculate LAB distance (Delta E)', () => {
      const c1 = Color.fromRGB(255, 0, 0);
      const c2 = Color.fromRGB(0, 0, 255);
      const distance = c1.distanceLAB(c2);
      expect(distance).toBeGreaterThan(0);
    });

    it('should return 0 for identical colors', () => {
      const c1 = Color.fromRGB(100, 150, 200);
      const c2 = Color.fromRGB(100, 150, 200);
      expect(c1.distanceLAB(c2)).toBeCloseTo(0, 1);
    });

    it('should be symmetric', () => {
      const c1 = Color.fromRGB(100, 100, 100);
      const c2 = Color.fromRGB(200, 200, 200);
      expect(c1.distanceLAB(c2)).toBeCloseTo(c2.distanceLAB(c1), 10);
    });
  });

  describe('distanceTo', () => {
    it('should use RGB distance when specified', () => {
      const c1 = Color.fromRGB(100, 100, 100);
      const c2 = Color.fromRGB(200, 200, 200);

      const dist1 = c1.distanceTo(c2, ColorSpace.RGB);
      const dist2 = c1.distanceRGB(c2);

      expect(dist1).toBe(dist2);
    });

    it('should use HSL distance when specified', () => {
      const c1 = Color.fromRGB(100, 100, 100);
      const c2 = Color.fromRGB(200, 200, 200);

      const dist1 = c1.distanceTo(c2, ColorSpace.HSL);
      const dist2 = c1.distanceHSL(c2);

      expect(dist1).toBe(dist2);
    });

    it('should use LAB distance when specified', () => {
      const c1 = Color.fromRGB(100, 100, 100);
      const c2 = Color.fromRGB(200, 200, 200);

      const dist1 = c1.distanceTo(c2, ColorSpace.LAB);
      const dist2 = c1.distanceLAB(c2);

      expect(dist1).toBe(dist2);
    });
  });

  describe('clone', () => {
    it('should create independent copy', () => {
      const original = Color.fromRGB(100, 150, 200);
      const copy = original.clone();

      expect(copy.toRGB()).toEqual(original.toRGB());
      expect(copy).not.toBe(original);
    });
  });

  describe('equals', () => {
    it('should return true for identical colors', () => {
      const c1 = Color.fromRGB(100, 150, 200);
      const c2 = Color.fromRGB(100, 150, 200);
      expect(c1.equals(c2)).toBe(true);
    });

    it('should return false for different colors', () => {
      const c1 = Color.fromRGB(100, 150, 200);
      const c2 = Color.fromRGB(100, 150, 201);
      expect(c1.equals(c2)).toBe(false);
    });

    it('should respect tolerance parameter', () => {
      const c1 = Color.fromRGB(100, 150, 200);
      const c2 = Color.fromRGB(102, 151, 199);

      expect(c1.equals(c2, 0)).toBe(false);
      expect(c1.equals(c2, 2)).toBe(true);
    });
  });

  describe('toHex', () => {
    it('should convert to hex string', () => {
      expect(Color.fromRGB(255, 0, 0).toHex()).toBe('#ff0000');
      expect(Color.fromRGB(0, 255, 0).toHex()).toBe('#00ff00');
      expect(Color.fromRGB(0, 0, 255).toHex()).toBe('#0000ff');
      expect(Color.fromRGB(255, 255, 255).toHex()).toBe('#ffffff');
      expect(Color.fromRGB(0, 0, 0).toHex()).toBe('#000000');
    });

    it('should pad with zeros', () => {
      expect(Color.fromRGB(1, 2, 3).toHex()).toBe('#010203');
    });
  });

  describe('toCSSRGB', () => {
    it('should convert to CSS rgb() string', () => {
      expect(Color.fromRGB(255, 0, 0).toCSSRGB()).toBe('rgb(255, 0, 0)');
      expect(Color.fromRGB(128, 128, 128).toCSSRGB()).toBe('rgb(128, 128, 128)');
    });
  });

  describe('toString', () => {
    it('should return hex string', () => {
      const color = Color.fromRGB(255, 128, 64);
      expect(color.toString()).toBe(color.toHex());
    });
  });

  describe('Round-trip conversions', () => {
    it('should preserve RGB through HSL conversion', () => {
      const original = Color.fromRGB(128, 64, 192);
      const hsl = original.toHSL();
      const converted = Color.fromHSL(hsl.h, hsl.s, hsl.l);

      expect(converted.equals(original, 1)).toBe(true);
    });

    it('should preserve RGB through LAB conversion', () => {
      const original = Color.fromRGB(128, 64, 192);
      const lab = original.toLAB();
      const converted = Color.fromLAB(lab.l, lab.a, lab.b);

      expect(converted.equals(original, 2)).toBe(true);
    });

    it('should preserve through hex conversion', () => {
      const original = Color.fromRGB(128, 64, 192);
      const hex = original.toHex();
      const converted = Color.fromHex(hex);

      expect(converted.equals(original)).toBe(true);
    });
  });

  describe('Known color values', () => {
    it('should handle standard web colors', () => {
      const red = Color.fromHex('#ff0000');
      expect(red.toRGB()).toEqual({ r: 255, g: 0, b: 0 });

      const green = Color.fromHex('#00ff00');
      expect(green.toRGB()).toEqual({ r: 0, g: 255, b: 0 });

      const blue = Color.fromHex('#0000ff');
      expect(blue.toRGB()).toEqual({ r: 0, g: 0, b: 255 });

      const white = Color.fromHex('#ffffff');
      expect(white.toRGB()).toEqual({ r: 255, g: 255, b: 255 });

      const black = Color.fromHex('#000000');
      expect(black.toRGB()).toEqual({ r: 0, g: 0, b: 0 });
    });
  });
});
