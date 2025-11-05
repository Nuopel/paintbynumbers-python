/**
 * Jest Test Setup
 *
 * This file runs after Jest is initialized but before tests are executed.
 * It sets up the Canvas API mock and any global test configuration.
 */

// Setup Canvas API mocking for unit tests
// This provides a mock implementation of the Canvas API that doesn't require
// native dependencies (cairo, pango, etc.) to be installed
import 'jest-canvas-mock';

/**
 * Global test setup
 * Runs once before all tests
 */
beforeAll(() => {
  // Set up any global test configuration here
  // For example, you might want to suppress console warnings during tests
  // jest.spyOn(console, 'warn').mockImplementation(() => {});
});

/**
 * Global test cleanup
 * Runs once after all tests
 */
afterAll(() => {
  // Clean up any global test resources here
});

/**
 * Per-test setup
 * Runs before each individual test
 */
beforeEach(() => {
  // Clear all mocks before each test to ensure test isolation
  jest.clearAllMocks();
});

/**
 * Per-test cleanup
 * Runs after each individual test
 */
afterEach(() => {
  // Additional per-test cleanup if needed
});
