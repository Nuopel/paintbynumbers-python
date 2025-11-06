/**
 * Constants and enums for Paint by Numbers Generator
 *
 * This module centralizes all magic numbers and configuration constants
 * to improve maintainability and code clarity.
 *
 * @module constants
 */

// Re-export ClusteringColorSpace from settings for convenience
export { ClusteringColorSpace as ColorSpace } from '../settings';

/**
 * Default parameters for K-means clustering
 */
export const CLUSTERING_DEFAULTS = {
  /** Maximum number of clustering iterations */
  MAX_ITERATIONS: 100,

  /** Convergence threshold for cluster centers (delta distance) */
  CONVERGENCE_THRESHOLD: 1,

  /** Default number of color clusters */
  DEFAULT_COLOR_COUNT: 16,

  /** Minimum number of colors allowed */
  MIN_COLOR_COUNT: 2,

  /** Maximum number of colors allowed */
  MAX_COLOR_COUNT: 256,

  /** Maximum delta distance for progress calculation */
  MAX_DELTA_DISTANCE_FOR_PROGRESS: 100,
} as const;

/**
 * UI update intervals in milliseconds
 */
export const UPDATE_INTERVALS = {
  /** Progress bar update interval during processing */
  PROGRESS_UPDATE_MS: 500,

  /** Debounce delay for user input changes */
  INPUT_DEBOUNCE_MS: 300,

  /** Frequency of updates during iterative processes (every N items) */
  BATCH_UPDATE_FREQUENCY: 100,
} as const;

/**
 * Facet processing thresholds
 */
export const FACET_THRESHOLDS = {
  /** Minimum facet size in pixels before removal */
  MIN_FACET_SIZE: 20,

  /** Maximum facet count before forced reduction */
  MAX_FACET_COUNT: Number.MAX_VALUE,

  /** Minimum border point count for a valid facet */
  MIN_BORDER_POINTS: 3,

  /** Minimum path length before reduction */
  MIN_PATH_LENGTH_FOR_REDUCTION: 5,
} as const;

/**
 * Bit manipulation constants for pixel data processing
 */
export const BIT_CONSTANTS = {
  /** Number of bits per color channel in RGB */
  BITS_PER_CHANNEL: 8,

  /** Maximum value for 8-bit color channel */
  MAX_CHANNEL_VALUE: 255,

  /** Number of bits to chop off for color grouping (reduces precision) */
  BITS_TO_CHOP_OFF: 2,

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

  /** Default resize width for large images */
  DEFAULT_RESIZE_WIDTH: 1024,

  /** Default resize height for large images */
  DEFAULT_RESIZE_HEIGHT: 1024,
} as const;

/**
 * Border segmentation constants
 */
export const SEGMENTATION_CONSTANTS = {
  /** Default number of times to halve border segments for smoothing */
  DEFAULT_HALVE_ITERATIONS: 2,

  /** Maximum distance between segment endpoints for matching */
  MAX_SEGMENT_MATCH_DISTANCE: 4,

  /** Number of narrow pixel strip cleanup runs */
  DEFAULT_NARROW_STRIP_CLEANUP_RUNS: 3,
} as const;

/**
 * SVG output constants
 */
export const SVG_CONSTANTS = {
  /** Default font size for color labels */
  DEFAULT_FONT_SIZE: 50,

  /** Default font color for labels */
  DEFAULT_FONT_COLOR: "black",

  /** Default stroke width for paths */
  DEFAULT_STROKE_WIDTH: 1,
} as const;

/**
 * Random seed constants
 */
export const RANDOM_SEED_CONSTANTS = {
  /** Special value indicating random seed should be generated */
  USE_CURRENT_TIME: 0,
} as const;
