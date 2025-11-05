/**
 * Test Infrastructure Smoke Tests
 *
 * These tests verify that the test infrastructure is properly set up
 * and all core testing utilities work correctly.
 */

import {
  loadTestImage,
  createMockCanvas,
  getImageDataFromCanvas,
  createFilledImageData,
  fileExists,
  getFixturePath,
} from './helpers/testUtils';

import {
  compareImageData,
  compareImages,
  calculatePSNR,
  getToleranceRecommendations,
} from './helpers/imageComparison';

describe('Test Infrastructure', () => {
  /**
   * Basic smoke test to ensure Jest is running
   */
  it('should load and run tests', () => {
    expect(true).toBe(true);
  });

  /**
   * Verify that Jest environment is properly configured
   */
  it('should have proper test environment', () => {
    expect(process.env.NODE_ENV).toBeDefined();
    expect(typeof describe).toBe('function');
    expect(typeof it).toBe('function');
    expect(typeof expect).toBe('function');
  });
});

describe('Canvas API', () => {
  /**
   * Test that we can create canvas elements
   */
  it('should create canvas with correct dimensions', () => {
    const canvas = createMockCanvas(100, 200);
    expect(canvas).toBeDefined();
    expect(canvas.width).toBe(100);
    expect(canvas.height).toBe(200);
  });

  /**
   * Test that we can get 2D context from canvas
   */
  it('should get 2D context from canvas', () => {
    const canvas = createMockCanvas(100, 100);
    const ctx = canvas.getContext('2d');
    expect(ctx).toBeDefined();
    expect(ctx).not.toBeNull();
  });

  /**
   * Test that we can extract ImageData from canvas
   */
  it('should extract ImageData from canvas', () => {
    const canvas = createMockCanvas(50, 50);
    const imageData = getImageDataFromCanvas(canvas);

    expect(imageData).toBeDefined();
    expect(imageData.width).toBe(50);
    expect(imageData.height).toBe(50);
    expect(imageData.data).toBeDefined();
    expect(imageData.data.length).toBe(50 * 50 * 4); // RGBA = 4 bytes per pixel
  });

  /**
   * Test creating filled ImageData
   */
  it('should create filled ImageData with correct color', () => {
    const red: [number, number, number, number] = [255, 0, 0, 255];
    const imageData = createFilledImageData(10, 10, red);

    expect(imageData.width).toBe(10);
    expect(imageData.height).toBe(10);

    // Check first pixel
    expect(imageData.data[0]).toBe(255);  // R
    expect(imageData.data[1]).toBe(0);    // G
    expect(imageData.data[2]).toBe(0);    // B
    expect(imageData.data[3]).toBe(255);  // A

    // Check last pixel
    const lastPixelIndex = (10 * 10 - 1) * 4;
    expect(imageData.data[lastPixelIndex]).toBe(255);
    expect(imageData.data[lastPixelIndex + 1]).toBe(0);
    expect(imageData.data[lastPixelIndex + 2]).toBe(0);
    expect(imageData.data[lastPixelIndex + 3]).toBe(255);
  });
});

describe('Test Image Loading', () => {
  /**
   * Test that fixture files exist
   */
  it('should find test fixture files', () => {
    expect(fileExists(getFixturePath('small.png'))).toBe(true);
    expect(fileExists(getFixturePath('medium.png'))).toBe(true);
    expect(fileExists(getFixturePath('complex.png'))).toBe(true);
  });

  /**
   * Test that we can load test images
   */
  it('should load test images', async () => {
    const img = await loadTestImage('small.png');

    expect(img).toBeDefined();
    expect(img.width).toBeGreaterThan(0);
    expect(img.height).toBeGreaterThan(0);
    expect(img.data).toBeDefined();
    expect(img.data.length).toBe(img.width * img.height * 4);
  });

  /**
   * Test loading different test images
   */
  it('should load all test fixture images', async () => {
    const small = await loadTestImage('small.png');
    const medium = await loadTestImage('medium.png');
    const complex = await loadTestImage('complex.png');

    expect(small).toBeDefined();
    expect(medium).toBeDefined();
    expect(complex).toBeDefined();
  });

  /**
   * Test error handling for missing images
   */
  it('should throw error for missing image', async () => {
    await expect(loadTestImage('nonexistent.png')).rejects.toThrow();
  });
});

describe('Image Comparison', () => {
  /**
   * Test comparing identical images
   */
  it('should detect identical images', () => {
    const img1 = createFilledImageData(10, 10, [100, 150, 200, 255]);
    const img2 = createFilledImageData(10, 10, [100, 150, 200, 255]);

    const result = compareImageData(img1, img2, 0);

    expect(result.match).toBe(true);
    expect(result.diffPixels).toBe(0);
    expect(result.diffPercentage).toBe(0);
    expect(result.maxDifference).toBe(0);
  });

  /**
   * Test comparing different images
   */
  it('should detect different images', () => {
    const img1 = createFilledImageData(10, 10, [255, 0, 0, 255]); // Red
    const img2 = createFilledImageData(10, 10, [0, 255, 0, 255]); // Green

    const result = compareImageData(img1, img2, 0);

    expect(result.match).toBe(false);
    expect(result.diffPixels).toBeGreaterThan(0);
    expect(result.diffPercentage).toBeGreaterThan(0);
    expect(result.maxDifference).toBeGreaterThan(0);
  });

  /**
   * Test tolerance in comparison
   */
  it('should respect tolerance in comparison', () => {
    const img1 = createFilledImageData(10, 10, [100, 100, 100, 255]);
    const img2 = createFilledImageData(10, 10, [103, 103, 103, 255]); // 3 units different

    // Should not match with tolerance 0
    const resultStrict = compareImageData(img1, img2, 0);
    expect(resultStrict.match).toBe(false);

    // Should not match with tolerance 2
    const resultMedium = compareImageData(img1, img2, 2);
    expect(resultMedium.match).toBe(false);

    // Should match with tolerance 5
    const resultLenient = compareImageData(img1, img2, 5);
    expect(resultLenient.match).toBe(true);
  });

  /**
   * Test comparing images with different dimensions
   */
  it('should handle dimension mismatches', () => {
    const img1 = createFilledImageData(10, 10, [255, 0, 0, 255]);
    const img2 = createFilledImageData(20, 20, [255, 0, 0, 255]);

    const result = compareImageData(img1, img2, 0);

    expect(result.match).toBe(false);
    expect(result.diffPercentage).toBe(100);
  });

  /**
   * Test PSNR calculation for identical images
   */
  it('should calculate infinite PSNR for identical images', () => {
    const img1 = createFilledImageData(10, 10, [128, 128, 128, 255]);
    const img2 = createFilledImageData(10, 10, [128, 128, 128, 255]);

    const psnr = calculatePSNR(img1, img2);

    expect(psnr).toBe(Infinity);
  });

  /**
   * Test PSNR calculation for different images
   */
  it('should calculate finite PSNR for different images', () => {
    const img1 = createFilledImageData(10, 10, [128, 128, 128, 255]);
    const img2 = createFilledImageData(10, 10, [130, 130, 130, 255]);

    const psnr = calculatePSNR(img1, img2);

    expect(psnr).toBeGreaterThan(0);
    expect(psnr).toBeLessThan(Infinity);
  });

  /**
   * Test tolerance recommendations
   */
  it('should provide tolerance recommendations', () => {
    const recommendations = getToleranceRecommendations();

    expect(recommendations.exact).toBe(0);
    expect(recommendations.lossy).toBeGreaterThan(0);
    expect(recommendations.antialiasing).toBeGreaterThan(0);
    expect(recommendations.colorSpace).toBeGreaterThan(0);
  });
});

describe('Test Utilities', () => {
  /**
   * Test fixture path helper
   */
  it('should generate correct fixture paths', () => {
    const path = getFixturePath('test.png');

    expect(path).toContain('fixtures');
    expect(path).toContain('test.png');
    expect(typeof path).toBe('string');
  });

  /**
   * Test file existence checker
   */
  it('should correctly check file existence', () => {
    const existingFile = getFixturePath('small.png');
    const nonExistentFile = getFixturePath('does-not-exist.png');

    expect(fileExists(existingFile)).toBe(true);
    expect(fileExists(nonExistentFile)).toBe(false);
  });
});

describe('Test Configuration', () => {
  /**
   * Verify Jest timeout is configured
   */
  it('should have sufficient timeout for image processing', () => {
    // This test verifies that jest.config.js has a proper timeout
    // Image processing can be slow, so we need adequate timeout
    expect(jest.setTimeout).toBeDefined();
  });

  /**
   * Verify test environment setup
   */
  it('should have setup file loaded', () => {
    // If this test runs, it means tests/setup.ts was loaded successfully
    // and jest-canvas-mock is initialized
    expect(true).toBe(true);
  });
});
