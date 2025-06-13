# ADR-001: Technology Stack Selection

**Status**: Accepted  
**Date**: 2025-06-12  
**Deciders**: Development Team  

## Context

The current ComfyUI Launcher uses PyWebView for desktop GUI, which has several limitations:

### Current Issues with PyWebView:
- **Performance**: 800-1200ms startup time, 80-120MB memory usage
- **WSL Compatibility**: Cannot run GUI in WSL, networking issues between WSL and Windows
- **Limited Features**: No native notifications, poor overlay support, complex tray management
- **Maintenance Burden**: 114 lines of complex threading code for system tray alone
- **User Experience**: Page replacement instead of true overlays, limited window management

### Business Requirements:
- Must support WSL development workflow
- Need native desktop features (tray, notifications, overlays)
- Require 5-10x performance improvement
- Must be AI-maintainable with clear architecture
- Production-ready with comprehensive testing

## Decision

**Adopt Wails v2 with Go backend and React frontend**

### Technology Stack:
- **Backend**: Go 1.21+ with Wails v2 framework
- **Frontend**: React 18+ with TypeScript, existing components
- **Testing**: Go testify + Playwright for E2E
- **Logging**: Zerolog for structured logging
- **Build**: Native compilation for Windows/Linux/macOS

## Rationale

### Why Wails v2:
1. **Performance**: 4-10x faster than PyWebView
   - Startup: 150-300ms (vs 800-1200ms)
   - Memory: 15-35MB (vs 80-120MB)
   - Binary: 6-10MB (vs 50-80MB)

2. **Native Features**: Built-in support for
   - System tray (15 lines vs 114 lines Python)
   - Native notifications
   - Multiple windows
   - Proper overlay system
   - Cross-platform compatibility

3. **WSL Compatibility**: 
   - Build native Windows executable from WSL
   - No GUI dependencies in build environment
   - Direct Windows API access when needed

4. **Developer Experience**:
   - Hot reload during development
   - TypeScript generation for APIs
   - Excellent debugging tools
   - Active community and maintenance

### Why Go Backend:
1. **Performance**: Compiled language, excellent concurrency
2. **Simplicity**: Clean syntax, easy for AI agents to maintain
3. **Ecosystem**: Rich standard library, excellent tooling
4. **Cross-compilation**: Easy to build for multiple platforms
5. **Testing**: Excellent testing frameworks and coverage tools

### Why Keep React Frontend:
1. **Existing Investment**: Already have React components
2. **Rich Ecosystem**: Vast library of UI components
3. **Developer Familiarity**: Team already knows React
4. **Testing**: Mature testing ecosystem (Playwright, Jest)
5. **Performance**: Virtual DOM, efficient updates

## Alternatives Considered

### 1. Electron
**Rejected**: Too heavy (100-200MB), security concerns, performance overhead

### 2. Tauri (Rust + Web)
**Rejected**: Steeper learning curve, less mature ecosystem, team unfamiliarity with Rust

### 3. Native Web Server + Browser
**Rejected**: Poor user experience, no native features, security limitations

### 4. Pure Desktop Frameworks (Qt, GTK)
**Rejected**: Complex UI development, poor cross-platform support, no web tech reuse

## Consequences

### Positive:
- ✅ **5-10x Performance Improvement**: Faster startup, lower memory usage
- ✅ **Native Desktop Features**: Proper system tray, notifications, overlays
- ✅ **WSL Compatibility**: Build and develop in WSL, run natively on Windows
- ✅ **Better User Experience**: True overlays, multiple windows, native behavior
- ✅ **Reduced Complexity**: 90% less code for system tray, built-in features
- ✅ **AI Maintainability**: Clear Go code structure, excellent documentation
- ✅ **Production Ready**: Mature framework, good testing support

### Negative:
- ❌ **Learning Curve**: Team needs to learn Go (mitigated by Go's simplicity)
- ❌ **Migration Effort**: Need to port Python logic to Go (1-2 weeks)
- ❌ **New Toolchain**: Different build and deployment processes

### Neutral:
- 🔄 **React Frontend**: Minimal changes needed, existing components work
- 🔄 **Feature Parity**: All current features can be implemented better
- 🔄 **Testing Strategy**: Need new backend tests, but frontend tests mostly unchanged

## Implementation Plan

### Phase 1: Foundation (Week 1)
- Set up Wails project structure
- Port core server management logic from Python
- Implement basic React integration

### Phase 2: Feature Parity (Week 2)
- Implement system tray (simplified)
- Add overlay system (enhanced)
- Port all existing functionality

### Phase 3: Enhanced Features (Week 3)
- Add native notifications
- Implement advanced overlays
- Add performance optimizations

### Phase 4: Production Polish (Week 4)
- Comprehensive testing
- Documentation
- Deployment automation

## Validation Criteria

### Performance Targets:
- [ ] Startup time < 300ms
- [ ] Memory usage < 35MB
- [ ] Binary size < 15MB

### Feature Targets:
- [ ] WSL development support
- [ ] Native system tray working
- [ ] Overlay system functional
- [ ] All existing features ported

### Quality Targets:
- [ ] 90%+ test coverage
- [ ] Comprehensive documentation
- [ ] AI maintainability score > 8/10

## References

- [Wails v2 Documentation](https://wails.io/docs/introduction)
- [Go Best Practices](https://golang.org/doc/effective_go.html)
- [React + Wails Integration Guide](https://wails.io/docs/guides/frontend)
- [Performance Comparison Analysis](./ULTRA_PERFORMANCE_WAILS.md)

---

**This ADR supersedes**: None (initial architecture decision)  
**Related ADRs**: ADR-002 (Project Structure), ADR-003 (Testing Strategy)
