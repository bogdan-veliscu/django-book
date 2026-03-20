/**
 * Global test setup for Vitest.
 * Runs before each test file.
 */

// Clear localStorage between tests
beforeEach(() => {
  localStorage.clear();
});

// Reset all mocks between tests (configured in vitest.config.ts with globals: true)
afterEach(() => {
  vi.restoreAllMocks();
});
