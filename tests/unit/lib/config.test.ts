import {
  DEFAULT_CONFIG,
  mergeConfig,
  validateConfig,
  assertValidConfig,
  PaintByNumbersConfig
} from '../../../src/lib/config';
import { ColorSpace, CLUSTERING_DEFAULTS, FACET_THRESHOLDS } from '../../../src/lib/constants';

describe('Configuration Module', () => {
  describe('DEFAULT_CONFIG', () => {
    it('should have valid default values', () => {
      const errors = validateConfig(DEFAULT_CONFIG);
      expect(errors).toHaveLength(0);
    });

    it('should use constants for defaults', () => {
      expect(DEFAULT_CONFIG.colorCount).toBe(CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT);
      expect(DEFAULT_CONFIG.colorSpace).toBe(ColorSpace.RGB);
      expect(DEFAULT_CONFIG.clusteringIterations).toBe(CLUSTERING_DEFAULTS.MAX_ITERATIONS);
      expect(DEFAULT_CONFIG.clusteringMinDeltaDifference).toBe(CLUSTERING_DEFAULTS.CONVERGENCE_THRESHOLD);
      expect(DEFAULT_CONFIG.minFacetSize).toBe(FACET_THRESHOLDS.MIN_FACET_SIZE);
    });

    it('should have sensible default settings', () => {
      expect(DEFAULT_CONFIG.removeFacetsFromLargeToSmall).toBe(true);
      expect(DEFAULT_CONFIG.resizeImageIfTooLarge).toBe(true);
      expect(DEFAULT_CONFIG.randomSeed).toBe(0);
    });
  });

  describe('mergeConfig', () => {
    it('should merge partial config with defaults', () => {
      const userConfig = { colorCount: 20 };
      const merged = mergeConfig(userConfig);

      expect(merged.colorCount).toBe(20);
      expect(merged.colorSpace).toBe(DEFAULT_CONFIG.colorSpace);
      expect(merged.enableSmoothing).toBeUndefined(); // Not in our config
      expect(merged.clusteringIterations).toBe(DEFAULT_CONFIG.clusteringIterations);
    });

    it('should override multiple properties', () => {
      const userConfig = {
        colorCount: 32,
        colorSpace: ColorSpace.LAB,
        minFacetSize: 10
      };
      const merged = mergeConfig(userConfig);

      expect(merged.colorCount).toBe(32);
      expect(merged.colorSpace).toBe(ColorSpace.LAB);
      expect(merged.minFacetSize).toBe(10);
      expect(merged.clusteringIterations).toBe(DEFAULT_CONFIG.clusteringIterations);
    });

    it('should not mutate default config', () => {
      const original = { ...DEFAULT_CONFIG };
      mergeConfig({ colorCount: 99 });
      expect(DEFAULT_CONFIG).toEqual(original);
    });

    it('should handle empty user config', () => {
      const merged = mergeConfig({});
      expect(merged).toEqual(DEFAULT_CONFIG);
    });
  });

  describe('validateConfig', () => {
    it('should accept valid configuration', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG };
      const errors = validateConfig(config);
      expect(errors).toHaveLength(0);
    });

    it('should reject colorCount < MIN_COLOR_COUNT', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorCount: 1 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('colorCount');
      expect(errors[0]).toContain('between');
    });

    it('should reject colorCount > MAX_COLOR_COUNT', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorCount: 999 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('colorCount');
    });

    it('should reject negative minFacetSize', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, minFacetSize: 0 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('minFacetSize'))).toBe(true);
    });

    it('should reject negative clusteringIterations', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, clusteringIterations: 0 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('clusteringIterations'))).toBe(true);
    });

    it('should reject invalid color space', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorSpace: 999 as ColorSpace };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('colorSpace'))).toBe(true);
    });

    it('should reject negative clusteringMinDeltaDifference', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, clusteringMinDeltaDifference: -1 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('clusteringMinDeltaDifference'))).toBe(true);
    });

    it('should reject negative narrowPixelStripCleanupRuns', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, narrowPixelStripCleanupRuns: -1 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('narrowPixelStripCleanupRuns'))).toBe(true);
    });

    it('should reject negative nrOfTimesToHalveBorderSegments', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, nrOfTimesToHalveBorderSegments: -1 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('nrOfTimesToHalveBorderSegments'))).toBe(true);
    });

    it('should reject invalid resizeImageWidth', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, resizeImageWidth: 0 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('resizeImageWidth'))).toBe(true);
    });

    it('should reject invalid resizeImageHeight', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, resizeImageHeight: 0 };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors.some(e => e.includes('resizeImageHeight'))).toBe(true);
    });

    it('should accept multiple valid color spaces', () => {
      const configRGB: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorSpace: ColorSpace.RGB };
      expect(validateConfig(configRGB)).toHaveLength(0);

      const configHSL: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorSpace: ColorSpace.HSL };
      expect(validateConfig(configHSL)).toHaveLength(0);

      const configLAB: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorSpace: ColorSpace.LAB };
      expect(validateConfig(configLAB)).toHaveLength(0);
    });

    it('should collect multiple validation errors', () => {
      const config: PaintByNumbersConfig = {
        ...DEFAULT_CONFIG,
        colorCount: 1,
        minFacetSize: 0,
        clusteringIterations: -1
      };
      const errors = validateConfig(config);
      expect(errors.length).toBeGreaterThanOrEqual(3);
    });

    it('should accept zero clusteringMinDeltaDifference', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, clusteringMinDeltaDifference: 0 };
      const errors = validateConfig(config);
      expect(errors.filter(e => e.includes('clusteringMinDeltaDifference'))).toHaveLength(0);
    });

    it('should accept zero narrowPixelStripCleanupRuns', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, narrowPixelStripCleanupRuns: 0 };
      const errors = validateConfig(config);
      expect(errors.filter(e => e.includes('narrowPixelStripCleanupRuns'))).toHaveLength(0);
    });
  });

  describe('assertValidConfig', () => {
    it('should not throw for valid config', () => {
      expect(() => assertValidConfig(DEFAULT_CONFIG)).not.toThrow();
    });

    it('should throw for invalid config', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorCount: -1 };
      expect(() => assertValidConfig(config)).toThrow('Invalid configuration');
    });

    it('should include error details in exception', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorCount: 1 };
      try {
        assertValidConfig(config);
        fail('Should have thrown an error');
      } catch (error) {
        expect((error as Error).message).toContain('colorCount');
      }
    });

    it('should throw with multiple errors listed', () => {
      const config: PaintByNumbersConfig = {
        ...DEFAULT_CONFIG,
        colorCount: 1,
        minFacetSize: 0
      };
      try {
        assertValidConfig(config);
        fail('Should have thrown an error');
      } catch (error) {
        const message = (error as Error).message;
        expect(message).toContain('colorCount');
        expect(message).toContain('minFacetSize');
      }
    });
  });

  describe('Edge cases', () => {
    it('should handle boundary values for colorCount', () => {
      const minConfig: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorCount: CLUSTERING_DEFAULTS.MIN_COLOR_COUNT };
      expect(validateConfig(minConfig)).toHaveLength(0);

      const maxConfig: PaintByNumbersConfig = { ...DEFAULT_CONFIG, colorCount: CLUSTERING_DEFAULTS.MAX_COLOR_COUNT };
      expect(validateConfig(maxConfig)).toHaveLength(0);
    });

    it('should handle large image dimensions', () => {
      const config: PaintByNumbersConfig = {
        ...DEFAULT_CONFIG,
        resizeImageWidth: 10000,
        resizeImageHeight: 10000
      };
      expect(validateConfig(config)).toHaveLength(0);
    });

    it('should handle maxFacetCount of 1', () => {
      const config: PaintByNumbersConfig = { ...DEFAULT_CONFIG, maxFacetCount: 1 };
      expect(validateConfig(config)).toHaveLength(0);
    });
  });
});
