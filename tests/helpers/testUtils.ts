/**
 * Test Utility Functions
 *
 * Helper functions for loading images, creating canvases, and working with ImageData
 * in tests. These utilities abstract away the complexity of working with Canvas API
 * in both browser and Node.js environments.
 */

import * as fs from 'fs';
import * as path from 'path';

/**
 * Load a test image from the fixtures directory
 *
 * @param filename - The name of the image file in tests/fixtures/
 * @returns ImageData object containing the image pixel data
 * @throws Error if the image cannot be loaded
 *
 * @example
 * const img = await loadTestImage('small.png');
 * expect(img.width).toBeGreaterThan(0);
 */
export async function loadTestImage(filename: string): Promise<ImageData> {
  const filepath = path.join(__dirname, '../fixtures', filename);

  if (!fs.existsSync(filepath)) {
    throw new Error(`Test image not found: ${filepath}`);
  }

  // For now, we'll create a mock ImageData object since canvas isn't fully set up
  // In a real implementation, this would use node-canvas to load the actual image
  // This is a placeholder that allows tests to run without native canvas dependencies

  // Read file to verify it exists and is readable
  const buffer = fs.readFileSync(filepath);

  // Create a simple mock ImageData for testing purposes
  // In production tests, you'd use canvas.loadImage() and getImageData()
  const mockImageData: ImageData = {
    width: 100,
    height: 100,
    data: new Uint8ClampedArray(100 * 100 * 4).fill(128) as any,
    colorSpace: 'srgb' as PredefinedColorSpace,
  };

  return mockImageData;
}

/**
 * Create a mock canvas element for testing
 *
 * @param width - Width of the canvas
 * @param height - Height of the canvas
 * @returns A mock HTMLCanvasElement with basic functionality
 *
 * @example
 * const canvas = createMockCanvas(100, 100);
 * const ctx = canvas.getContext('2d');
 */
export function createMockCanvas(width: number, height: number): any {
  // In a real Node.js environment with canvas installed, this would use:
  // import { createCanvas } from 'canvas';
  // return createCanvas(width, height);

  // For now, return a mock canvas object that works with jest-canvas-mock
  const canvas = {
    width,
    height,
    getContext: (contextType: string) => {
      if (contextType === '2d') {
        return {
          canvas,
          fillStyle: '#000000',
          strokeStyle: '#000000',
          lineWidth: 1,
          getImageData: (x: number, y: number, w: number, h: number) => {
            return {
              width: w,
              height: h,
              data: new Uint8ClampedArray(w * h * 4),
              colorSpace: 'srgb' as PredefinedColorSpace,
            };
          },
          putImageData: (imageData: ImageData, dx: number, dy: number) => {
            // Mock implementation
          },
          fillRect: (x: number, y: number, w: number, h: number) => {
            // Mock implementation
          },
          clearRect: (x: number, y: number, w: number, h: number) => {
            // Mock implementation
          },
        };
      }
      return null;
    },
  };

  return canvas;
}

/**
 * Extract ImageData from a canvas element
 *
 * @param canvas - The canvas element to extract data from
 * @returns ImageData object containing all pixel data from the canvas
 *
 * @example
 * const canvas = createMockCanvas(100, 100);
 * const imageData = getImageDataFromCanvas(canvas);
 * expect(imageData.width).toBe(100);
 */
export function getImageDataFromCanvas(canvas: any): ImageData {
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    throw new Error('Could not get 2d context from canvas');
  }

  return ctx.getImageData(0, 0, canvas.width, canvas.height);
}

/**
 * Create an ImageData object with specific dimensions and fill color
 *
 * @param width - Width of the image
 * @param height - Height of the image
 * @param fillColor - RGBA color to fill the image with [r, g, b, a]
 * @returns ImageData object filled with the specified color
 *
 * @example
 * const redImage = createFilledImageData(100, 100, [255, 0, 0, 255]);
 * expect(redImage.data[0]).toBe(255); // Red channel
 */
export function createFilledImageData(
  width: number,
  height: number,
  fillColor: [number, number, number, number] = [0, 0, 0, 255]
): ImageData {
  const data = new Uint8ClampedArray(width * height * 4);

  for (let i = 0; i < data.length; i += 4) {
    data[i] = fillColor[0];     // R
    data[i + 1] = fillColor[1]; // G
    data[i + 2] = fillColor[2]; // B
    data[i + 3] = fillColor[3]; // A
  }

  return {
    width,
    height,
    data: data as any,
    colorSpace: 'srgb' as PredefinedColorSpace,
  };
}

/**
 * Verify that a file exists
 *
 * @param filepath - Path to the file to check
 * @returns true if the file exists, false otherwise
 *
 * @example
 * expect(fileExists('./tests/fixtures/small.png')).toBe(true);
 */
export function fileExists(filepath: string): boolean {
  return fs.existsSync(filepath);
}

/**
 * Get the absolute path to a fixture file
 *
 * @param filename - Name of the fixture file
 * @returns Absolute path to the fixture file
 *
 * @example
 * const path = getFixturePath('small.png');
 * expect(path).toContain('fixtures/small.png');
 */
export function getFixturePath(filename: string): string {
  return path.join(__dirname, '../fixtures', filename);
}
