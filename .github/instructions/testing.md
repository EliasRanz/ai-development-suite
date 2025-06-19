# Testing Standards for Agentic Workflows

All agents must enforce comprehensive, automated testing for all code and workflows. Reference: [coding-standards.md], [version-control.md], [copilot-instructions.md], [security.md].

## Core Testing Principles
- **Test-First**: All code must be covered by automated tests before merging.
- **Automation**: Use scripts and CI/CD pipelines to run, validate, and report on all tests.
- **Traceability**: Document all test failures, regressions, and exceptions in the session context and project management system.

## Coverage & Enforcement
- **Minimum 90% test coverage** for all code (enforced by CI/CD).
- **No code without tests** is accepted.
- **Regression tests** are required for all bug fixes.
- **All tests must pass before commit and merge.**

## Test Categories (All Required)
1. **Unit Tests**: Validate individual functions and logic.
2. **Integration Tests**: Validate API endpoints and service interactions.
3. **Performance Tests**: Validate startup time, memory, and response targets.
4. **Security Tests**: Validate input validation, path traversal, and other security requirements.
5. **Feature Flag Tests**: Validate all feature flags in both on/off states.

## Test Organization
```
tests/
├── unit/           # Unit tests
├── integration/    # API/service integration
├── e2e/           # End-to-end browser tests
├── performance/   # Performance benchmarks
└── security/      # Security validation tests
```

## Automated Testing Workflow
1. **Write Tests**: For all new code, features, and bug fixes.
2. **Run Tests Locally**: Use scripts or `make help` to run all test suites before committing.
3. **Automated CI/CD**: All tests must run and pass in CI/CD before merge.
4. **Document Failures**: Log all test failures, regressions, and exceptions in the session context and project management system.
5. **Review Coverage**: Use automated tools to enforce and report coverage.

## Example Test Commands
```bash
# Go backend testing
make test-backend
# or
cd ai-pm/backend && go test -race -coverprofile=coverage.out ./...
go tool cover -func=coverage.out

# Frontend testing  
cd ai-pm/frontend && npm test -- --coverage

# E2E testing
cd ai-pm/frontend && npx playwright test
```

## Performance Targets (Must Meet)
- **Startup time**: < 2 seconds
- **Memory usage**: < 100MB base
- **Response time**: < 100ms for API calls
- **Concurrent instances**: Support 5+ AI tools

## AI Agent Testing Checklist
- [ ] Unit tests written for all functions
- [ ] Integration tests for API endpoints
- [ ] Performance tests validate targets
- [ ] Security validations tested
- [ ] Feature flags tested (on/off states)
- [ ] 90%+ coverage achieved
- [ ] All tests passing before commit/merge

## Continuous Improvement
- Agents must participate in periodic test suite reviews and propose improvements.
- Update tests and documentation as new features, bugs, or requirements emerge.

## Test Data Management
- Use anonymized, non-production data for all tests.
- Document procedures for generating and maintaining test data.

## Flaky Test Handling
- Identify, document, and resolve flaky or non-deterministic tests.
- Quarantine or fix flaky tests before merging.

## Test Tagging & Selective Runs
- Tag tests (e.g., slow, integration, security) to support selective execution and faster feedback.
- Use test runner features to run subsets of tests as needed.

## Test Documentation
- Document complex test cases and rationale for edge cases within the test code.
- Maintain clear, up-to-date documentation for all test suites.

## Test Metrics & Reporting
- Regularly report test coverage, pass/fail rates, and time-to-fix for regressions.
- Use automated tools to generate and track these metrics.

## Accessibility & Usability Testing (If Applicable)
- For user-facing features, include accessibility and usability tests as part of the test suite.

## Mocking & Test Data Usage
- Use mocked data, services, and dependencies for unit tests to ensure isolation and determinism.
- Avoid external network calls or real service dependencies in unit tests; use mocks or stubs instead.
- Clearly document the use of mocks and their intended behavior within the test code.

## Glossary
- **Flaky Test**: A test that produces inconsistent results (sometimes passing, sometimes failing) without code changes.
- **Test Tagging**: The practice of labeling tests for selective execution (e.g., slow, integration, security).
- **Test Data**: Data used exclusively for testing, never from production sources.

---
Testing is a shared, continuous responsibility for all agents. For detailed requirements and examples, see `coding-standards.md` and related standards.
