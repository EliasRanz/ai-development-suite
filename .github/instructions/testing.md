# Testing Instructions for AI Agents

## Coverage Requirements (ENFORCED)
- **MINIMUM 90% test coverage** for all code
- **NO code without tests** accepted
- **REGRESSION tests** for all bug fixes

## Testing Stack
```bash
# Go backend testing
go test -race -coverprofile=coverage.out ./...
go tool cover -func=coverage.out

# Frontend testing  
cd frontend && npm test -- --coverage

# E2E testing
cd frontend && npx playwright test
```

## Test Categories (ALL REQUIRED)

### 1. Unit Tests
```go
func TestTaskService_CreateTask(t *testing.T) {
    service := NewTaskService(mockRepo)
    task := Task{Title: "Test"}
    
    err := service.CreateTask(task)
    assert.NoError(t, err)
}
```

### 2. Integration Tests
```go
func TestAPI_CreateTask(t *testing.T) {
    server := setupTestServer()
    resp := httptest.NewRecorder()
    
    server.ServeHTTP(resp, request)
    assert.Equal(t, 201, resp.Code)
}
```

### 3. Performance Tests (CRITICAL)
```go
func TestStartupTime(t *testing.T) {
    start := time.Now()
    app := StartApplication()
    duration := time.Since(start)
    
    assert.Less(t, duration, 2*time.Second) // 4x improvement target
}
```

### 4. Security Tests  
```go
func TestPathTraversal(t *testing.T) {
    input := "../../../etc/passwd"
    err := validatePath(input)
    assert.Error(t, err)
}
```

### 5. Feature Flag Tests
```go
func TestFeatureFlag_Disabled(t *testing.T) {
    setFeatureFlag("new_feature", false)
    result := processRequest()
    assert.Equal(t, "legacy_behavior", result)
}
```

## Test Organization
```
tests/
├── unit/           # Unit tests
├── integration/    # API/service integration
├── e2e/           # End-to-end browser tests
├── performance/   # Performance benchmarks
└── security/      # Security validation tests
```

## AI Agent Testing Checklist
- [ ] Unit tests written for all functions
- [ ] Integration tests for API endpoints
- [ ] Performance tests validate 4x targets
- [ ] Security validations tested
- [ ] Feature flags tested (on/off states)
- [ ] 90%+ coverage achieved
- [ ] All tests passing before commit

## Performance Targets (MUST MEET)
- **Startup time**: < 2 seconds
- **Memory usage**: < 100MB base
- **Response time**: < 100ms for API calls
- **Concurrent instances**: Support 5+ AI tools
