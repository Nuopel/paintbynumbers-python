import { ColorSpace, CLUSTERING_DEFAULTS, FACET_THRESHOLDS, IMAGE_CONSTANTS, SEGMENTATION_CONSTANTS } from './constants';

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

  /** Minimum delta difference for clustering convergence */
  clusteringMinDeltaDifference: number;

  /** Minimum facet size in pixels */
  minFacetSize: number;

  /** Maximum number of facets */
  maxFacetCount: number;

  /** Number of narrow pixel strip cleanup runs */
  narrowPixelStripCleanupRuns: number;

  /** Remove facets from large to small order */
  removeFacetsFromLargeToSmall: boolean;

  /** Number of times to halve border segments for smoothing */
  nrOfTimesToHalveBorderSegments: number;

  /** Resize image if too large */
  resizeImageIfTooLarge: boolean;

  /** Maximum image width for resize */
  resizeImageWidth: number;

  /** Maximum image height for resize */
  resizeImageHeight: number;

  /** Random seed for reproducible results (0 = use current time) */
  randomSeed: number;
}

/**
 * Default configuration using constants
 */
export const DEFAULT_CONFIG: Readonly<PaintByNumbersConfig> = {
  colorCount: CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT,
  colorSpace: ColorSpace.RGB,
  clusteringIterations: CLUSTERING_DEFAULTS.MAX_ITERATIONS,
  clusteringMinDeltaDifference: CLUSTERING_DEFAULTS.CONVERGENCE_THRESHOLD,
  minFacetSize: FACET_THRESHOLDS.MIN_FACET_SIZE,
  maxFacetCount: FACET_THRESHOLDS.MAX_FACET_COUNT,
  narrowPixelStripCleanupRuns: SEGMENTATION_CONSTANTS.DEFAULT_NARROW_STRIP_CLEANUP_RUNS,
  removeFacetsFromLargeToSmall: true,
  nrOfTimesToHalveBorderSegments: SEGMENTATION_CONSTANTS.DEFAULT_HALVE_ITERATIONS,
  resizeImageIfTooLarge: true,
  resizeImageWidth: IMAGE_CONSTANTS.DEFAULT_RESIZE_WIDTH,
  resizeImageHeight: IMAGE_CONSTANTS.DEFAULT_RESIZE_HEIGHT,
  randomSeed: 0, // 0 = use current time
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

  if (config.clusteringMinDeltaDifference < 0) {
    errors.push('clusteringMinDeltaDifference must be non-negative');
  }

  if (config.minFacetSize < 1) {
    errors.push('minFacetSize must be at least 1');
  }

  if (config.maxFacetCount < 1) {
    errors.push('maxFacetCount must be at least 1');
  }

  if (config.narrowPixelStripCleanupRuns < 0) {
    errors.push('narrowPixelStripCleanupRuns must be non-negative');
  }

  if (config.nrOfTimesToHalveBorderSegments < 0) {
    errors.push('nrOfTimesToHalveBorderSegments must be non-negative');
  }

  if (config.resizeImageWidth < 1) {
    errors.push('resizeImageWidth must be at least 1');
  }

  if (config.resizeImageHeight < 1) {
    errors.push('resizeImageHeight must be at least 1');
  }

  const validColorSpaces = [ColorSpace.RGB, ColorSpace.HSL, ColorSpace.LAB];
  if (validColorSpaces.indexOf(config.colorSpace) === -1) {
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
