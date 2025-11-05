module.exports = {
  // Use ts-jest preset for TypeScript support
  preset: 'ts-jest',

  // Use Node environment for testing
  testEnvironment: 'node',

  // Look for tests in the tests directory
  roots: ['<rootDir>/tests'],

  // Match test files with .test.ts or .spec.ts extensions
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],

  // Transform TypeScript files using ts-jest
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },

  // File extensions to recognize
  moduleFileExtensions: ['ts', 'js', 'json'],

  // Coverage configuration
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
  ],

  // Setup files to run after Jest is initialized
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],

  // TypeScript configuration for ts-jest
  globals: {
    'ts-jest': {
      tsconfig: {
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        // Allow JavaScript files in TypeScript
        allowJs: true,
      },
    },
  },

  // Increase timeout for image processing tests
  testTimeout: 30000,
};
