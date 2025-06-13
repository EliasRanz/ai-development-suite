# ADR-003: Testing Strategy and Quality Assurance

**Status**: Accepted  
**Date**: 2025-06-12  
**Deciders**: Development Team  

## Context

We need a comprehensive testing strategy that ensures:

### Quality Requirements:
- **High Coverage**: 90%+ backend, 85%+ frontend coverage
- **Production Confidence**: Catch bugs before deployment
- **Regression Prevention**: Prevent breaking existing functionality
- **Fast Feedback**: Quick test execution during development
- **WSL Compatibility**: Tests must run in WSL development environment

### Current Challenges:
- PyWebView code has limited test coverage
- UI components are difficult to test in isolation
- Manual testing is time-consuming and error-prone
- No automated E2E testing for user workflows

## Decision

**Implement multi-layered testing strategy with automated quality gates**

### Testing Pyramid:

```
           ╭─────────────╮
          ╱   E2E Tests   ╲     ← 20% (High value, slow)
         ╱   (Playwright)  ╲
        ╱_________________╲
       ╱                   ╲
      ╱  Integration Tests  ╲   ← 30% (Medium value, medium speed)
     ╱   (Wails + React)    ╲
    ╱_______________________╲
   ╱                         ╲
  ╱      Unit Tests           ╲ ← 50% (High speed, focused)
 ╱   (Go testify + Jest)      ╲
╱___________________________╲
```

### Testing Framework Stack:

#### Backend Testing (Go):
- **Framework**: `testify/suite` for structured tests
- **Mocking**: `testify/mock` for interfaces
- **Coverage**: Built-in `go test -cover`
- **Benchmarking**: Built-in `go test -bench`

#### Frontend Testing (React):
- **Unit/Integration**: Jest + React Testing Library
- **E2E**: Playwright with MSW for API mocking
- **Visual Regression**: Playwright screenshots
- **Performance**: Lighthouse CI

#### Cross-Platform Testing:
- **WSL**: Native Go test execution
- **Windows**: Cross-compiled binaries
- **CI/CD**: GitHub Actions with matrix builds

## Testing Layers

### 1. Unit Tests (50% of test suite)

#### Backend Unit Tests:
```go
// internal/domain/server/manager_test.go
func TestServerManager_Start(t *testing.T) {
    suite.Run(t, new(ServerManagerTestSuite))
}

type ServerManagerTestSuite struct {
    suite.Suite
    manager *Manager
    mockFS  *mocks.FileSystem
    mockProc *mocks.ProcessManager
}

func (s *ServerManagerTestSuite) SetupTest() {
    s.mockFS = &mocks.FileSystem{}
    s.mockProc = &mocks.ProcessManager{}
    s.manager = NewManager(s.mockFS, s.mockProc)
}

func (s *ServerManagerTestSuite) TestStart_Success() {
    // Arrange
    s.mockFS.On("Exists", "/path/to/comfyui").Return(true)
    s.mockProc.On("Start", mock.Anything).Return(&Process{PID: 1234}, nil)
    
    // Act
    err := s.manager.Start(context.Background(), Config{Path: "/path/to/comfyui"})
    
    // Assert
    s.NoError(err)
    s.Equal(StatusRunning, s.manager.GetStatus())
    s.mockFS.AssertExpectations(s.T())
    s.mockProc.AssertExpectations(s.T())
}
```

#### Frontend Unit Tests:
```typescript
// frontend/src/components/ServerControls.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { ServerControls } from './ServerControls'
import { useWails } from '../hooks/useWails'

jest.mock('../hooks/useWails')

describe('ServerControls', () => {
  const mockStartServer = jest.fn()
  const mockStopServer = jest.fn()
  
  beforeEach(() => {
    (useWails as jest.Mock).mockReturnValue({
      startServer: mockStartServer,
      stopServer: mockStopServer,
      serverStatus: 'stopped'
    })
  })
  
  test('should start server when start button clicked', async () => {
    render(<ServerControls />)
    
    fireEvent.click(screen.getByRole('button', { name: /start server/i }))
    
    expect(mockStartServer).toHaveBeenCalled()
  })
})
```

### 2. Integration Tests (30% of test suite)

#### Wails Integration Tests:
```go
// test/integration/wails_handlers_test.go
func TestWailsHandlers_ServerLifecycle(t *testing.T) {
    // Setup test app with real Wails context
    app := setupTestApp(t)
    ctx := setupTestContext(t)
    
    // Test complete server lifecycle
    err := app.StartServer(ctx)
    require.NoError(t, err)
    
    status := app.GetServerStatus(ctx)
    assert.Equal(t, "running", status.State)
    
    err = app.StopServer(ctx)
    require.NoError(t, err)
}
```

#### React-Wails Integration Tests:
```typescript
// frontend/tests/integration/server-management.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { App } from '../src/App'
import { createMockWailsContext } from './utils/mockWails'

describe('Server Management Integration', () => {
  test('should handle complete server lifecycle', async () => {
    const mockWails = createMockWailsContext()
    
    render(<App />, { 
      wrapper: ({ children }) => (
        <WailsProvider value={mockWails}>{children}</WailsProvider>
      )
    })
    
    // Start server
    fireEvent.click(screen.getByTestId('start-server'))
    await waitFor(() => {
      expect(screen.getByText('Server Running')).toBeInTheDocument()
    })
    
    // Verify status updates
    expect(mockWails.startServer).toHaveBeenCalled()
  })
})
```

### 3. End-to-End Tests (20% of test suite)

#### Playwright E2E Tests:
```typescript
// frontend/tests/e2e/server-management.spec.ts
import { test, expect } from '@playwright/test'

test.describe('ComfyUI Server Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock Wails API responses
    await page.route('**/wails/**', async route => {
      const url = route.request().url()
      
      if (url.includes('StartServer')) {
        await route.fulfill({
          contentType: 'application/json',
          body: JSON.stringify({ success: true })
        })
      }
    })
    
    await page.goto('/')
  })
  
  test('should start ComfyUI server successfully', async ({ page }) => {
    // Click start button
    await page.click('[data-testid="start-server"]')
    
    // Verify loading state
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible()
    
    // Verify success state
    await expect(page.locator('[data-testid="server-status"]')).toHaveText('Running')
    
    // Verify UI elements are enabled/disabled correctly
    await expect(page.locator('[data-testid="stop-server"]')).toBeEnabled()
    await expect(page.locator('[data-testid="start-server"]')).toBeDisabled()
  })
  
  test('should handle server start failure gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/StartServer', route => 
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Failed to start server' })
      })
    )
    
    await page.click('[data-testid="start-server"]')
    
    // Verify error handling
    await expect(page.locator('[data-testid="error-message"]')).toHaveText('Failed to start server')
    await expect(page.locator('[data-testid="start-server"]')).toBeEnabled()
  })
})
```

### 4. Visual Regression Tests:
```typescript
// frontend/tests/visual/ui-components.spec.ts
test('should match loading screen visual design', async ({ page }) => {
  await page.goto('/')
  await page.click('[data-testid="start-server"]')
  
  // Wait for loading state
  await page.waitForSelector('[data-testid="loading-spinner"]')
  
  // Visual regression test
  await expect(page).toHaveScreenshot('loading-screen.png')
})
```

## Quality Gates

### Pre-Commit Hooks:
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run linters
golangci-lint run
cd frontend && npm run lint

# Run unit tests
go test ./... -short
cd frontend && npm test -- --watchAll=false

# Check coverage thresholds
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total | awk '{print $3}' | grep -E "^([9-9][0-9]|100)%$" || {
  echo "Coverage below 90%"
  exit 1
}
```

### CI/CD Pipeline:
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v3
        with:
          go-version: 1.21
      
      - name: Run Go tests
        run: |
          go test -v -race -coverprofile=coverage.out ./...
          go tool cover -html=coverage.out -o coverage.html
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install Playwright
        run: cd frontend && npm ci && npx playwright install
      
      - name: Run E2E tests
        run: cd frontend && npm run test:e2e
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

### Coverage Targets:

#### Backend Coverage:
- **Domain Layer**: 95%+ (pure business logic)
- **Application Layer**: 90%+ (orchestration logic)
- **Infrastructure Layer**: 85%+ (external integrations)
- **Interfaces Layer**: 80%+ (Wails handlers)

#### Frontend Coverage:
- **Components**: 90%+ (UI logic)
- **Hooks**: 95%+ (state management)
- **Services**: 85%+ (API integration)
- **Utils**: 95%+ (pure functions)

### Performance Testing:
```go
// Benchmark tests for performance critical paths
func BenchmarkServerManager_Start(b *testing.B) {
    manager := setupBenchmarkManager()
    
    for i := 0; i < b.N; i++ {
        manager.Start(context.Background(), Config{})
    }
}

// Performance targets:
// - Server start: < 100ms
// - Status check: < 1ms
// - Log processing: > 10k lines/sec
```

## WSL Development Support

### WSL Test Setup:
```bash
# scripts/wsl/setup-testing.sh
#!/bin/bash

# Install Go
wget -q -O - https://git.io/vQhTU | bash -s -- --version 1.21.0

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install test dependencies
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
cd frontend && npm install
npx playwright install

# Setup coverage tools
go install github.com/axw/gocov/gocov@latest
go install github.com/matm/gocov-html@latest

echo "✅ WSL testing environment ready"
```

### Cross-Platform Testing:
```makefile
# Makefile
test-all:
	@echo "🧪 Running all tests..."
	make test-go
	make test-frontend
	make test-e2e

test-go:
	@echo "🔧 Running Go tests..."
	go test -v -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

test-frontend:
	@echo "⚛️ Running React tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-e2e:
	@echo "🎭 Running E2E tests..."
	cd frontend && npx playwright test

test-wsl:
	@echo "🐧 Running WSL-specific tests..."
	# Test cross-compilation
	GOOS=windows GOARCH=amd64 go build -o build/test.exe ./cmd/app
	# Test development environment
	./scripts/wsl/validate-environment.sh
```

## Project Cleanliness Strategy

### Clean Project Structure:
- ✅ **Separate Test Directory**: All tests in dedicated `/tests` directory
- ✅ **Production Build**: Only ship necessary files in final binary
- ✅ **No Test Pollution**: Keep production code free of test utilities
- ✅ **Clean Dependencies**: Separate dev/test dependencies from runtime
- ✅ **Artifact Management**: Remove build artifacts and temporary files
- ✅ **Security**: Apply principle of least privilege for file permissions
- ✅ **Permission Control**: No overly permissive files (avoid 777, 666)

### Test Organization:
```
project-root/
├── cmd/                    # Main application entry points
├── internal/               # Private application code
├── pkg/                    # Public libraries (if any)
├── frontend/               # React application
│   ├── src/               # Production source code
│   └── package.json       # Runtime + dev dependencies separated
├── tests/                  # All tests separate from production code
│   ├── unit/              # Unit tests mirroring src structure
│   ├── integration/       # Integration tests
│   ├── e2e/              # End-to-end tests
│   ├── fixtures/         # Test data and mocks
│   └── utils/            # Test utilities and helpers
├── docs/                  # Documentation only
├── scripts/               # Build and deployment scripts
└── ADRs/                 # Architecture Decision Records
```

### File Cleanup Rules:
```bash
# Files to KEEP in production:
✅ Source code (*.go, *.ts, *.tsx, *.css)
✅ Assets (icons, images, fonts)
✅ Configuration (go.mod, package.json, wails.json)
✅ Documentation (README.md, ADRs/)
✅ Build scripts (Makefile, scripts/)

# Files to REMOVE from production:
❌ Test files (*_test.go, *.test.ts, *.spec.ts)
❌ Test fixtures and mocks
❌ Build artifacts (build/, dist/, coverage/)
❌ Development configs (.gitignore, .vscode/)
❌ Temporary files (*.tmp, *.log, __pycache__)
❌ Legacy Python implementation (comfy_launcher/)
```

### Dependency Separation:
```json
// frontend/package.json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@playwright/test": "^1.40.0",
    "jest": "^29.7.0",
    "vitest": "^1.0.0"
  }
}
```

```go
// go.mod - Use build tags for test dependencies
//go:build tools
// +build tools

package tools

import (
    _ "github.com/golangci/golangci-lint/cmd/golangci-lint"
    _ "github.com/onsi/ginkgo/v2/ginkgo"
)
```

## Benefits

### Development Efficiency:
- ✅ **Fast Feedback**: Unit tests run in <30 seconds
- ✅ **Confident Refactoring**: High coverage prevents regressions
- ✅ **Parallel Development**: Mocks enable independent work
- ✅ **Quality Assurance**: Automated checks prevent bugs
- ✅ **Clean Codebase**: Production code free of test pollution

### Production Reliability:
- ✅ **User Experience**: E2E tests validate user workflows
- ✅ **Performance**: Benchmark tests catch performance regressions
- ✅ **Cross-Platform**: Tests validate Windows/Linux compatibility
- ✅ **Visual Consistency**: Screenshot tests prevent UI regressions
- ✅ **Minimal Binary**: Only ship necessary code and assets

### Maintenance:
- ✅ **Documentation**: Tests serve as living documentation
- ✅ **Onboarding**: New developers understand system through tests
- ✅ **Debugging**: Test failures provide clear error context
- ✅ **AI Support**: Well-tested code is easier for AI to maintain
- ✅ **Clean Repository**: Easy to navigate and understand structure

## Implementation Timeline

### Week 1: Foundation
- [ ] Set up Go testing framework with testify
- [ ] Configure Jest and React Testing Library
- [ ] Create mock infrastructure
- [ ] Establish coverage reporting

### Week 2: Core Tests
- [ ] Write domain layer unit tests
- [ ] Implement application layer tests
- [ ] Create Wails integration tests
- [ ] Set up CI/CD pipeline

### Week 3: E2E Testing
- [ ] Configure Playwright
- [ ] Implement critical user journey tests
- [ ] Add visual regression testing
- [ ] Create performance benchmarks

### Week 4: Quality Gates
- [ ] Implement pre-commit hooks
- [ ] Configure automatic coverage reporting
- [ ] Set up performance monitoring
- [ ] Create testing documentation

## References

- [Go Testing Best Practices](https://golang.org/doc/effective_go.html#testing)
- [React Testing Library Guide](https://testing-library.com/docs/react-testing-library/intro/)
- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Test Pyramid by Martin Fowler](https://martinfowler.com/articles/practical-test-pyramid.html)

---

**This ADR supersedes**: None  
**Related ADRs**: ADR-001 (Technology Stack), ADR-002 (Project Structure)
