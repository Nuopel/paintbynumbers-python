import {
  ColorSpace,
  CLUSTERING_DEFAULTS,
  UPDATE_INTERVALS,
  FACET_THRESHOLDS,
  BIT_CONSTANTS,
  IMAGE_CONSTANTS,
  SEGMENTATION_CONSTANTS,
  SVG_CONSTANTS,
  RANDOM_SEED_CONSTANTS
} from '../../../src/lib/constants';
import { ClusteringColorSpace } from '../../../src/settings';

describe('Constants Module', () => {
  describe('ColorSpace enum', () => {
    it('should re-export ClusteringColorSpace as ColorSpace', () => {
      expect(ColorSpace.RGB).toBe(ClusteringColorSpace.RGB);
      expect(ColorSpace.HSL).toBe(ClusteringColorSpace.HSL);
      expect(ColorSpace.LAB).toBe(ClusteringColorSpace.LAB);
    });

    it('should have correct numeric values', () => {
      expect(ColorSpace.RGB).toBe(0);
      expect(ColorSpace.HSL).toBe(1);
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
      expect(CLUSTERING_DEFAULTS.MAX_ITERATIONS).toBe(100);
    });

    it('should have valid convergence threshold', () => {
      expect(CLUSTERING_DEFAULTS.CONVERGENCE_THRESHOLD).toBe(1);
      expect(CLUSTERING_DEFAULTS.CONVERGENCE_THRESHOLD).toBeGreaterThanOrEqual(0);
    });

    it('should have valid color count range', () => {
      expect(CLUSTERING_DEFAULTS.MIN_COLOR_COUNT).toBe(2);
      expect(CLUSTERING_DEFAULTS.MAX_COLOR_COUNT).toBe(256);
      expect(CLUSTERING_DEFAULTS.MIN_COLOR_COUNT).toBeLessThan(
        CLUSTERING_DEFAULTS.MAX_COLOR_COUNT
      );
    });

    it('should have max delta distance for progress', () => {
      expect(CLUSTERING_DEFAULTS.MAX_DELTA_DISTANCE_FOR_PROGRESS).toBe(100);
      expect(CLUSTERING_DEFAULTS.MAX_DELTA_DISTANCE_FOR_PROGRESS).toBeGreaterThan(0);
    });
  });

  describe('UPDATE_INTERVALS', () => {
    it('should have positive update intervals', () => {
      expect(UPDATE_INTERVALS.PROGRESS_UPDATE_MS).toBe(500);
      expect(UPDATE_INTERVALS.PROGRESS_UPDATE_MS).toBeGreaterThan(0);
    });

    it('should have positive debounce delay', () => {
      expect(UPDATE_INTERVALS.INPUT_DEBOUNCE_MS).toBe(300);
      expect(UPDATE_INTERVALS.INPUT_DEBOUNCE_MS).toBeGreaterThan(0);
    });

    it('should have batch update frequency', () => {
      expect(UPDATE_INTERVALS.BATCH_UPDATE_FREQUENCY).toBe(100);
      expect(UPDATE_INTERVALS.BATCH_UPDATE_FREQUENCY).toBeGreaterThan(0);
    });
  });

  describe('FACET_THRESHOLDS', () => {
    it('should have positive min facet size', () => {
      expect(FACET_THRESHOLDS.MIN_FACET_SIZE).toBe(20);
      expect(FACET_THRESHOLDS.MIN_FACET_SIZE).toBeGreaterThan(0);
    });

    it('should have reasonable max facet count', () => {
      expect(FACET_THRESHOLDS.MAX_FACET_COUNT).toBe(Number.MAX_VALUE);
      expect(FACET_THRESHOLDS.MAX_FACET_COUNT).toBeGreaterThan(100);
    });

    it('should have min border points', () => {
      expect(FACET_THRESHOLDS.MIN_BORDER_POINTS).toBe(3);
      expect(FACET_THRESHOLDS.MIN_BORDER_POINTS).toBeGreaterThan(0);
    });

    it('should have min path length for reduction', () => {
      expect(FACET_THRESHOLDS.MIN_PATH_LENGTH_FOR_REDUCTION).toBe(5);
      expect(FACET_THRESHOLDS.MIN_PATH_LENGTH_FOR_REDUCTION).toBeGreaterThan(0);
    });
  });

  describe('BIT_CONSTANTS', () => {
    it('should have correct bits per channel', () => {
      expect(BIT_CONSTANTS.BITS_PER_CHANNEL).toBe(8);
    });

    it('should have correct max channel value', () => {
      expect(BIT_CONSTANTS.MAX_CHANNEL_VALUE).toBe(255);
      expect(BIT_CONSTANTS.MAX_CHANNEL_VALUE).toBe(
        Math.pow(2, BIT_CONSTANTS.BITS_PER_CHANNEL) - 1
      );
    });

    it('should have bits to chop off', () => {
      expect(BIT_CONSTANTS.BITS_TO_CHOP_OFF).toBe(2);
      expect(BIT_CONSTANTS.BITS_TO_CHOP_OFF).toBeGreaterThanOrEqual(0);
    });

    it('should have RGBA shift', () => {
      expect(BIT_CONSTANTS.RGBA_SHIFT).toBe(2);
      expect(BIT_CONSTANTS.RGBA_SHIFT).toBeGreaterThanOrEqual(0);
    });
  });

  describe('IMAGE_CONSTANTS', () => {
    it('should have valid JPEG quality', () => {
      expect(IMAGE_CONSTANTS.JPEG_QUALITY).toBe(0.95);
      expect(IMAGE_CONSTANTS.JPEG_QUALITY).toBeGreaterThan(0);
      expect(IMAGE_CONSTANTS.JPEG_QUALITY).toBeLessThanOrEqual(1);
    });

    it('should have PNG compression level', () => {
      expect(IMAGE_CONSTANTS.PNG_COMPRESSION).toBe(6);
      expect(IMAGE_CONSTANTS.PNG_COMPRESSION).toBeGreaterThanOrEqual(0);
    });

    it('should have max dimension warning', () => {
      expect(IMAGE_CONSTANTS.MAX_DIMENSION_WARNING).toBe(2000);
      expect(IMAGE_CONSTANTS.MAX_DIMENSION_WARNING).toBeGreaterThan(0);
    });

    it('should have default resize dimensions', () => {
      expect(IMAGE_CONSTANTS.DEFAULT_RESIZE_WIDTH).toBe(1024);
      expect(IMAGE_CONSTANTS.DEFAULT_RESIZE_HEIGHT).toBe(1024);
      expect(IMAGE_CONSTANTS.DEFAULT_RESIZE_WIDTH).toBeGreaterThan(0);
      expect(IMAGE_CONSTANTS.DEFAULT_RESIZE_HEIGHT).toBeGreaterThan(0);
    });
  });

  describe('SEGMENTATION_CONSTANTS', () => {
    it('should have default halve iterations', () => {
      expect(SEGMENTATION_CONSTANTS.DEFAULT_HALVE_ITERATIONS).toBe(2);
      expect(SEGMENTATION_CONSTANTS.DEFAULT_HALVE_ITERATIONS).toBeGreaterThanOrEqual(0);
    });

    it('should have max segment match distance', () => {
      expect(SEGMENTATION_CONSTANTS.MAX_SEGMENT_MATCH_DISTANCE).toBe(4);
      expect(SEGMENTATION_CONSTANTS.MAX_SEGMENT_MATCH_DISTANCE).toBeGreaterThan(0);
    });

    it('should have default narrow strip cleanup runs', () => {
      expect(SEGMENTATION_CONSTANTS.DEFAULT_NARROW_STRIP_CLEANUP_RUNS).toBe(3);
      expect(SEGMENTATION_CONSTANTS.DEFAULT_NARROW_STRIP_CLEANUP_RUNS).toBeGreaterThanOrEqual(0);
    });
  });

  describe('SVG_CONSTANTS', () => {
    it('should have default font size', () => {
      expect(SVG_CONSTANTS.DEFAULT_FONT_SIZE).toBe(50);
      expect(SVG_CONSTANTS.DEFAULT_FONT_SIZE).toBeGreaterThan(0);
    });

    it('should have default font color', () => {
      expect(SVG_CONSTANTS.DEFAULT_FONT_COLOR).toBe('black');
      expect(typeof SVG_CONSTANTS.DEFAULT_FONT_COLOR).toBe('string');
    });

    it('should have default stroke width', () => {
      expect(SVG_CONSTANTS.DEFAULT_STROKE_WIDTH).toBe(1);
      expect(SVG_CONSTANTS.DEFAULT_STROKE_WIDTH).toBeGreaterThan(0);
    });
  });

  describe('RANDOM_SEED_CONSTANTS', () => {
    it('should have USE_CURRENT_TIME constant', () => {
      expect(RANDOM_SEED_CONSTANTS.USE_CURRENT_TIME).toBe(0);
    });
  });

  describe('Constants immutability', () => {
    it('should prevent modification of CLUSTERING_DEFAULTS', () => {
      expect(Object.isFrozen(CLUSTERING_DEFAULTS)).toBe(true);
    });

    it('should prevent modification of UPDATE_INTERVALS', () => {
      expect(Object.isFrozen(UPDATE_INTERVALS)).toBe(true);
    });

    it('should prevent modification of FACET_THRESHOLDS', () => {
      expect(Object.isFrozen(FACET_THRESHOLDS)).toBe(true);
    });

    it('should prevent modification of BIT_CONSTANTS', () => {
      expect(Object.isFrozen(BIT_CONSTANTS)).toBe(true);
    });

    it('should prevent modification of IMAGE_CONSTANTS', () => {
      expect(Object.isFrozen(IMAGE_CONSTANTS)).toBe(true);
    });

    it('should prevent modification of SEGMENTATION_CONSTANTS', () => {
      expect(Object.isFrozen(SEGMENTATION_CONSTANTS)).toBe(true);
    });

    it('should prevent modification of SVG_CONSTANTS', () => {
      expect(Object.isFrozen(SVG_CONSTANTS)).toBe(true);
    });

    it('should prevent modification of RANDOM_SEED_CONSTANTS', () => {
      expect(Object.isFrozen(RANDOM_SEED_CONSTANTS)).toBe(true);
    });
  });
});
