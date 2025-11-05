/**
 * Image Comparison Utilities
 *
 * Functions for comparing images pixel-by-pixel with configurable tolerance.
 * These utilities are essential for regression testing image processing algorithms.
 */

import * as fs from 'fs';
import * as path from 'path';
import { loadTestImage } from './testUtils';

/**
 * Result of an image comparison operation
 */
export interface ComparisonResult {
  /** Whether the images match within the given tolerance */
  match: boolean;
  /** Number of pixels that differ beyond the tolerance */
  diffPixels: number;
  /** Percentage of pixels that differ (0-100) */
  diffPercentage: number;
  /** Maximum difference found in any color channel (0-255) */
  maxDifference: number;
}

/**
 * Compare two ImageData objects pixel-by-pixel
 *
 * @param img1 - First image to compare
 * @param img2 - Second image to compare
 * @param tolerance - Maximum acceptable difference per channel (0-255). Default: 0 (exact match)
 * @returns ComparisonResult with details about the comparison
 *
 * @example
 * const result = compareImageData(image1, image2, 5);
 * expect(result.match).toBe(true);
 * expect(result.diffPercentage).toBeLessThan(1);
 */
export function compareImageData(
  img1: ImageData,
  img2: ImageData,
  tolerance: number = 0
): ComparisonResult {
  // Check dimensions first
  if (img1.width !== img2.width || img1.height !== img2.height) {
    const totalPixels1 = img1.width * img1.height;
    const totalPixels2 = img2.width * img2.height;
    const diffPixels = Math.abs(totalPixels1 - totalPixels2);

    return {
      match: false,
      diffPixels,
      diffPercentage: 100,
      maxDifference: 255,
    };
  }

  let diffPixels = 0;
  let maxDiff = 0;
  const totalPixels = img1.width * img1.height;

  // Compare pixel by pixel
  // ImageData.data is a Uint8ClampedArray with 4 values per pixel (RGBA)
  for (let i = 0; i < img1.data.length; i += 4) {
    // Calculate difference for each channel
    const rDiff = Math.abs(img1.data[i] - img2.data[i]);
    const gDiff = Math.abs(img1.data[i + 1] - img2.data[i + 1]);
    const bDiff = Math.abs(img1.data[i + 2] - img2.data[i + 2]);
    const aDiff = Math.abs(img1.data[i + 3] - img2.data[i + 3]);

    // Use the maximum difference across all channels
    const pixelDiff = Math.max(rDiff, gDiff, bDiff, aDiff);

    // Track maximum difference found
    maxDiff = Math.max(maxDiff, pixelDiff);

    // Count pixels that exceed tolerance
    if (pixelDiff > tolerance) {
      diffPixels++;
    }
  }

  const diffPercentage = (diffPixels / totalPixels) * 100;

  return {
    match: diffPixels === 0,
    diffPixels,
    diffPercentage,
    maxDifference: maxDiff,
  };
}

/**
 * Compare two images by file path
 *
 * @param path1 - Path to first image file
 * @param path2 - Path to second image file
 * @param tolerance - Maximum acceptable difference per channel (0-255)
 * @returns Promise resolving to ComparisonResult
 *
 * @example
 * const result = await compareImages(
 *   './output.png',
 *   './expected.png',
 *   5
 * );
 * expect(result.match).toBe(true);
 */
export async function compareImages(
  path1: string,
  path2: string,
  tolerance: number = 0
): Promise<ComparisonResult> {
  // Extract just the filename if a full path is provided
  const filename1 = path.basename(path1);
  const filename2 = path.basename(path2);

  try {
    const img1 = await loadTestImage(filename1);
    const img2 = await loadTestImage(filename2);

    return compareImageData(img1, img2, tolerance);
  } catch (error) {
    throw new Error(
      `Failed to compare images ${path1} and ${path2}: ${error}`
    );
  }
}

/**
 * Create a diff image highlighting differences between two images
 *
 * Pixels that differ beyond the tolerance are highlighted in red.
 * This is useful for debugging test failures.
 *
 * @param img1 - First image
 * @param img2 - Second image
 * @param outputPath - Where to save the diff image
 * @param tolerance - Difference tolerance (0-255)
 *
 * @example
 * saveImageDiff(original, processed, './diff.png', 5);
 */
export function saveImageDiff(
  img1: ImageData,
  img2: ImageData,
  outputPath: string,
  tolerance: number = 0
): void {
  // Ensure dimensions match
  if (img1.width !== img2.width || img1.height !== img2.height) {
    throw new Error(
      'Cannot create diff image: dimensions do not match'
    );
  }

  // Create a new ImageData for the diff
  const diffData = new Uint8ClampedArray(img1.data.length);

  for (let i = 0; i < img1.data.length; i += 4) {
    const rDiff = Math.abs(img1.data[i] - img2.data[i]);
    const gDiff = Math.abs(img1.data[i + 1] - img2.data[i + 1]);
    const bDiff = Math.abs(img1.data[i + 2] - img2.data[i + 2]);
    const aDiff = Math.abs(img1.data[i + 3] - img2.data[i + 3]);

    const maxDiff = Math.max(rDiff, gDiff, bDiff, aDiff);

    if (maxDiff > tolerance) {
      // Highlight differences in red
      diffData[i] = 255;     // R
      diffData[i + 1] = 0;   // G
      diffData[i + 2] = 0;   // B
      diffData[i + 3] = 255; // A
    } else {
      // Keep original pixel
      diffData[i] = img1.data[i];
      diffData[i + 1] = img1.data[i + 1];
      diffData[i + 2] = img1.data[i + 2];
      diffData[i + 3] = img1.data[i + 3];
    }
  }

  // In a real implementation with canvas support, you would:
  // 1. Create a canvas with the diff ImageData
  // 2. Convert canvas to PNG
  // 3. Save to outputPath
  //
  // For now, we'll create a placeholder file
  const diffInfo = {
    width: img1.width,
    height: img1.height,
    message: 'Diff image (requires canvas for actual rendering)',
  };

  fs.writeFileSync(outputPath, JSON.stringify(diffInfo, null, 2));
}

/**
 * Calculate PSNR (Peak Signal-to-Noise Ratio) between two images
 *
 * PSNR is a quality metric commonly used in image processing.
 * Higher values indicate more similar images.
 * - PSNR > 40 dB: Images are very similar
 * - PSNR 30-40 dB: Images are similar
 * - PSNR < 30 dB: Images differ significantly
 *
 * @param img1 - First image
 * @param img2 - Second image
 * @returns PSNR value in decibels (dB), or Infinity if images are identical
 *
 * @example
 * const psnr = calculatePSNR(original, processed);
 * expect(psnr).toBeGreaterThan(40); // Expect high quality
 */
export function calculatePSNR(
  img1: ImageData,
  img2: ImageData
): number {
  if (img1.width !== img2.width || img1.height !== img2.height) {
    throw new Error('Cannot calculate PSNR: dimensions do not match');
  }

  let mse = 0;
  const numPixels = img1.width * img1.height;

  // Calculate Mean Squared Error
  for (let i = 0; i < img1.data.length; i += 4) {
    // Only compare RGB channels (ignore alpha)
    for (let j = 0; j < 3; j++) {
      const diff = img1.data[i + j] - img2.data[i + j];
      mse += diff * diff;
    }
  }

  mse = mse / (numPixels * 3); // 3 channels (RGB)

  // If images are identical, MSE is 0 and PSNR is infinity
  if (mse === 0) {
    return Infinity;
  }

  // PSNR formula: 10 * log10(MAX^2 / MSE)
  // MAX is 255 for 8-bit images
  const maxPixelValue = 255;
  const psnr = 10 * Math.log10((maxPixelValue * maxPixelValue) / mse);

  return psnr;
}

/**
 * Get tolerance recommendations based on image processing type
 *
 * @returns Object with recommended tolerance values for different scenarios
 */
export function getToleranceRecommendations(): {
  exact: number;
  lossy: number;
  antialiasing: number;
  colorSpace: number;
} {
  return {
    exact: 0,           // For exact pixel matches (e.g., unit tests)
    lossy: 5,           // For JPEG or lossy compression
    antialiasing: 2,    // For operations that may anti-alias edges
    colorSpace: 3,      // For color space conversions
  };
}
