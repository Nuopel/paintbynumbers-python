# Test Infrastructure Documentation

This directory contains the comprehensive testing infrastructure for the Paint by Numbers Generator project.

## 📁 Directory Structure

```
tests/
├── unit/              # Unit tests for individual functions
├── integration/       # Integration tests for pipeline stages
├── e2e/              # End-to-end tests for complete pipeline
├── fixtures/         # Test images and data
│   ├── small.png     # 100x100 simple test image
│   ├── medium.png    # 500x500 moderate complexity image
│   └── complex.png   # Complex image with gradients
├── snapshots/        # Reference outputs for regression testing
├── helpers/          # Test utilities
│   ├── testUtils.ts         # Canvas and image loading utilities
│   └── imageComparison.ts   # Image comparison and PSNR calculation
├── setup.ts          # Global test configuration
└── setup.test.ts     # Infrastructure smoke tests
```

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests
npm test

# Run tests in watch mode (auto-rerun on file changes)
npm run test:watch

# Run tests with coverage report
npm run test:coverage

# Run tests with verbose output
npm run test:verbose
```

### Advanced Usage

```bash
# Run specific test file
npm test -- tests/unit/kMeans.test.ts

# Run tests matching a pattern
npm test -- --testNamePattern="color space"

# Run tests in a specific directory
npm test -- tests/integration/

# Update snapshots
npm test -- -u

# Run in debug mode
node --inspect-brk node_modules/.bin/jest --runInBand
```

## 📝 Writing Tests

### Test Organization Philosophy

Tests are organized by scope and purpose:

- **Unit tests** (`tests/unit/`): Test individual functions and classes in isolation
- **Integration tests** (`tests/integration/`): Test how components work together
- **E2E tests** (`tests/e2e/`): Test the complete pipeline from input to output

### Example Unit Test

```typescript
import { kMeansCluster } from '../../src/algorithms/kMeans';
import { loadTestImage } from '../helpers/testUtils';

describe('K-Means Clustering', () => {
  it('should cluster colors correctly', async () => {
    const image = await loadTestImage('small.png');
    const clusters = kMeansCluster(image, 5);

    expect(clusters).toHaveLength(5);
    expect(clusters[0]).toHaveProperty('centroid');
    expect(clusters[0]).toHaveProperty('points');
  });
});
```

### Example Integration Test

```typescript
import { processImagePipeline } from '../../src/pipeline';
import { loadTestImage } from '../helpers/testUtils';
import { compareImageData } from '../helpers/imageComparison';

describe('Image Processing Pipeline', () => {
  it('should process image through full pipeline', async () => {
    const input = await loadTestImage('medium.png');
    const output = await processImagePipeline(input, {
      colors: 8,
      minFacetSize: 10,
    });

    expect(output).toBeDefined();
    expect(output.facets).toBeDefined();
  });
});
```

## 🖼️ Image Comparison

### How Image Comparison Works

The image comparison utility compares images pixel-by-pixel, calculating:

- **Difference per pixel**: Maximum difference across R, G, B, A channels
- **Total different pixels**: Count of pixels exceeding tolerance
- **Difference percentage**: Percentage of pixels that differ
- **Maximum difference**: Largest difference found in any channel

### Tolerance Guidelines

| Use Case | Recommended Tolerance | Reason |
|----------|----------------------|--------|
| Unit tests (exact match) | 0 | Expect bit-perfect output |
| Lossy compression (JPEG) | 5 | JPEG artifacts |
| Anti-aliasing operations | 2 | Edge smoothing differences |
| Color space conversions | 3 | Rounding in conversions |
| SVG rendering | 10 | Browser rendering variations |

### Example Image Comparison

```typescript
import { compareImageData, getToleranceRecommendations } from '../helpers/imageComparison';

it('should match reference output', async () => {
  const output = await processImage(input);
  const reference = await loadTestImage('reference.png');

  const tolerance = getToleranceRecommendations().antialiasing;
  const result = compareImageData(output, reference, tolerance);

  expect(result.match).toBe(true);
  expect(result.diffPercentage).toBeLessThan(1);
});
```

### PSNR (Peak Signal-to-Noise Ratio)

PSNR is a quality metric for comparing images:

- **PSNR > 40 dB**: Excellent quality, images very similar
- **PSNR 30-40 dB**: Good quality, minor differences
- **PSNR < 30 dB**: Poor quality, significant differences

```typescript
import { calculatePSNR } from '../helpers/imageComparison';

it('should maintain high quality after processing', async () => {
  const original = await loadTestImage('input.png');
  const processed = await processImage(original);

  const psnr = calculatePSNR(original, processed);
  expect(psnr).toBeGreaterThan(35); // Good quality threshold
});
```

## 🎨 Test Fixtures

### Available Test Images

- **small.png** (100x100): Simple 2-3 color image for fast unit tests
- **medium.png** (500x500): Moderate complexity for integration tests
- **complex.png** (500x500): Photo-realistic with gradients for E2E tests

### Adding New Test Fixtures

1. Place image in `tests/fixtures/`
2. Use PNG format (lossless, deterministic)
3. Document the purpose and characteristics
4. Keep file sizes reasonable (< 5MB)

```typescript
// Load custom fixture
const myImage = await loadTestImage('my-custom-fixture.png');
```

## 🛠️ Test Utilities

### testUtils.ts

Helper functions for working with images and canvas:

```typescript
import {
  loadTestImage,          // Load image from fixtures
  createMockCanvas,       // Create canvas for testing
  getImageDataFromCanvas, // Extract ImageData from canvas
  createFilledImageData,  // Create solid color ImageData
  fileExists,            // Check if file exists
  getFixturePath,        // Get absolute path to fixture
} from './helpers/testUtils';
```

### imageComparison.ts

Functions for comparing and analyzing images:

```typescript
import {
  compareImageData,              // Compare two ImageData objects
  compareImages,                 // Compare images by file path
  saveImageDiff,                 // Create visual diff image
  calculatePSNR,                 // Calculate image quality metric
  getToleranceRecommendations,   // Get recommended tolerances
} from './helpers/imageComparison';
```

## 🧪 Canvas API Testing

### Canvas Mock

Tests use `jest-canvas-mock` which provides a mock Canvas API without requiring native dependencies (cairo, pango, etc.).

The mock supports:
- Canvas creation
- 2D context
- Basic drawing operations
- ImageData operations
- `getImageData()` and `putImageData()`

### Limitations

The canvas mock is for unit testing only. For integration tests that need real rendering:

1. Use snapshot testing with pre-generated reference images
2. Run integration tests in a real browser (future work)
3. Use the actual node-canvas in CI/CD with native dependencies

## 📊 Code Coverage

### Viewing Coverage Reports

After running `npm run test:coverage`, open `coverage/lcov-report/index.html` in a browser.

### Coverage Goals

- **Statements**: > 80%
- **Branches**: > 75%
- **Functions**: > 80%
- **Lines**: > 80%

Critical paths (image processing algorithms) should aim for 90%+ coverage.

## 🐛 Debugging Tests

### Debug in VS Code

Add this configuration to `.vscode/launch.json`:

```json
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/node_modules/.bin/jest",
  "args": ["--runInBand", "${file}"],
  "console": "integratedTerminal",
  "internalConsoleOptions": "neverOpen"
}
```

### Debug in Chrome DevTools

```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

Then open `chrome://inspect` in Chrome.

### Common Issues

#### "Cannot find module 'canvas'"

The native canvas module isn't required for unit tests. If you see this error:
1. Make sure `jest-canvas-mock` is in setupFilesAfterEnv
2. Check that `jest.config.js` is correctly configured
3. Clear Jest cache: `npm test -- --clearCache`

#### "Timeout of 5000ms exceeded"

Image processing can be slow. Increase timeout in individual tests:

```typescript
it('should process large image', async () => {
  // Test code
}, 30000); // 30 second timeout
```

Or globally in `jest.config.js`:

```javascript
testTimeout: 30000
```

## 📚 Best Practices

### 1. Test Isolation

Each test should be independent and not rely on other tests:

```typescript
beforeEach(() => {
  // Reset state before each test
});

afterEach(() => {
  // Clean up after each test
});
```

### 2. Descriptive Test Names

Use clear, descriptive test names that explain what is being tested:

```typescript
// ❌ Bad
it('works', () => { ... });

// ✅ Good
it('should cluster 8 colors from a gradient image', () => { ... });
```

### 3. Arrange-Act-Assert Pattern

Structure tests clearly:

```typescript
it('should remove small facets', () => {
  // Arrange: Set up test data
  const facets = createTestFacets();
  const minSize = 10;

  // Act: Execute the function
  const result = removeSma llFacets(facets, minSize);

  // Assert: Verify the outcome
  expect(result).toHaveLength(5);
  expect(result.every(f => f.size >= minSize)).toBe(true);
});
```

### 4. Use Snapshots Wisely

Snapshots are great for catching unintended changes, but:

- Review snapshot changes carefully
- Don't snapshot large objects
- Prefer explicit assertions for critical behavior

```typescript
// Use for UI/output structure
expect(svgOutput).toMatchSnapshot();

// Use explicit assertions for critical values
expect(output.palette).toHaveLength(8);
expect(output.facets[0].color).toEqual([255, 0, 0]);
```

### 5. Test Error Cases

Don't just test the happy path:

```typescript
it('should throw error for invalid cluster count', () => {
  expect(() => kMeans(data, -1)).toThrow('Cluster count must be positive');
  expect(() => kMeans(data, 0)).toThrow('Cluster count must be positive');
});
```

## 🔄 Continuous Integration

Tests run automatically on:
- Every push to a branch
- Every pull request
- Scheduled nightly runs

### CI Configuration

See `.github/workflows/test.yml` for the full CI setup.

## 📖 Further Reading

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing TypeScript](https://jestjs.io/docs/getting-started#using-typescript)
- [Canvas API Reference](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [Image Processing Basics](https://en.wikipedia.org/wiki/Digital_image_processing)

## 🤝 Contributing

When adding new tests:

1. Follow the existing structure and patterns
2. Add tests for both success and error cases
3. Document any new test utilities
4. Ensure all tests pass before committing
5. Update this README if adding new testing patterns

## 📝 Change Log

- **2025-11-05**: Initial test infrastructure setup (LOT 1.1)
  - Jest configuration
  - Test utilities and helpers
  - Smoke tests
  - Documentation
