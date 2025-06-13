#!/bin/bash
# Clean up current repository and prepare for Wails migration
# Usage: ./scripts/cleanup-repository.sh

set -e

echo "🧹 ComfyUI Launcher Repository Cleanup"
echo "======================================"

# Function to safely move files
safe_move() {
    local src="$1"
    local dest="$2"
    
    if [[ -e "$src" ]]; then
        mkdir -p "$(dirname "$dest")"
        mv "$src" "$dest"
        echo "✅ Moved: $src → $dest"
    else
        echo "⚠️  File not found: $src"
    fi
}

# Function to safely remove files/directories
safe_remove() {
    local target="$1"
    
    if [[ -e "$target" ]]; then
        rm -rf "$target"
        echo "🗑️  Removed: $target"
    else
        echo "⚠️  Already removed: $target"
    fi
}

echo ""
echo "📁 Creating archive directory structure..."
mkdir -p docs/archive/{analysis,legacy-python,build-artifacts}

echo ""
echo "📄 Archiving analysis and planning documents..."
# Move analysis files to archive
safe_move "ELECTRON_OPTION.md" "docs/archive/analysis/ELECTRON_OPTION.md"
safe_move "LIGHTWEIGHT_ANALYSIS.md" "docs/archive/analysis/LIGHTWEIGHT_ANALYSIS.md"
safe_move "MULTI_FRONTEND_PLAN.md" "docs/archive/analysis/MULTI_FRONTEND_PLAN.md"
safe_move "TAURI_MIGRATION_PLAN.md" "docs/archive/analysis/TAURI_MIGRATION_PLAN.md"
safe_move "WAILS_OPTION.md" "docs/archive/analysis/WAILS_OPTION.md"
safe_move "PERFORMANCE_ROADMAP.md" "docs/archive/analysis/PERFORMANCE_ROADMAP.md"
safe_move "EXTREME_PERFORMANCE_ADDONS.md" "docs/archive/analysis/EXTREME_PERFORMANCE_ADDONS.md"
safe_move "ULTRA_PERFORMANCE_WAILS.md" "docs/archive/analysis/ULTRA_PERFORMANCE_WAILS.md"
safe_move "WAILS_IMPLEMENTATION.md" "docs/archive/analysis/WAILS_IMPLEMENTATION.md"
safe_move "WAILS_TRAY_OVERLAY_FEATURES.md" "docs/archive/analysis/WAILS_TRAY_OVERLAY_FEATURES.md"
safe_move "PRODUCTION_IMPLEMENTATION_PLAN.md" "docs/archive/analysis/PRODUCTION_IMPLEMENTATION_PLAN.md"
safe_move "REACT_MIGRATION.md" "docs/archive/analysis/REACT_MIGRATION.md"
safe_move "gemini-context.md" "docs/archive/analysis/gemini-context.md"

echo ""
echo "🐍 Archiving legacy Python implementation..."
# Archive Python codebase (might be useful for reference)
if [[ -d "comfy_launcher" ]]; then
    cp -r "comfy_launcher" "docs/archive/legacy-python/"
    echo "✅ Archived Python codebase to docs/archive/legacy-python/"
fi

# Archive Python tests
if [[ -d "tests" ]] && [[ -f "tests/test_config.py" ]]; then
    cp -r "tests" "docs/archive/legacy-python/tests"
    echo "✅ Archived Python tests to docs/archive/legacy-python/tests"
fi

echo ""
echo "🏗️ Archiving build artifacts..."
# Archive build artifacts before removing
if [[ -d "build" ]]; then
    cp -r "build" "docs/archive/build-artifacts/"
    echo "✅ Archived build artifacts to docs/archive/build-artifacts/"
fi

echo ""
echo "🗑️ Removing legacy files and artifacts..."

# Remove Python implementation
safe_remove "comfy_launcher/"
safe_remove "requirements.txt"
safe_remove "requirements.in"
safe_remove "concept_web_server.py"

# Remove build artifacts
safe_remove "build/"

# Remove Python tests (keeping directory structure for Go tests)
safe_remove "tests/test_*.py"
safe_remove "tests/__pycache__/"
safe_remove "tests/conftest.py"

# Remove Windows-specific scripts (will create cross-platform versions)
safe_remove "build_web_ui.bat"
safe_remove "build_web_ui.ps1"
safe_remove "setup_dev_env.bat"
safe_remove "start_comfyui.bat"

# Remove web-ui build artifacts
safe_remove "web-ui/dist/"
safe_remove "web-ui/node_modules/"

echo ""
echo "📝 Creating enhanced .gitignore..."
cat > .gitignore << 'EOF'
# Build artifacts
/build/
/dist/
*.exe
*.app
*.dmg
*.deb
*.rpm

# Development artifacts
coverage.out
coverage.html
*.test
*.prof
*.pprof

# Frontend artifacts
node_modules/
frontend/dist/
frontend/build/
web-ui/dist/
web-ui/node_modules/

# Go artifacts
vendor/
*.so
*.dylib

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# OS-specific files
.DS_Store
Thumbs.db
ehthumbs.db

# Logs
*.log
logs/
comfy_launcher/logs/

# Temporary files
*.tmp
*.temp

# Python artifacts (legacy cleanup)
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
.pytest_cache/

# Environment files
.env
.env.local
.env.development
.env.test
.env.production

# Dependencies
go.sum
EOF

echo ""
echo "📋 Creating project status documentation..."
cat > PROJECT_STATUS.md << 'EOF'
# ComfyUI Launcher - Project Status

## Current State: Preparation for Wails Migration

### ✅ Completed
- [x] React frontend implementation (in web-ui/)
- [x] Python-React integration working
- [x] Architecture Decision Records (ADRs/)
- [x] Comprehensive analysis and planning
- [x] Repository cleanup and organization

### 🚧 In Progress
- [ ] Wails implementation setup
- [ ] Go backend development
- [ ] Clean project structure implementation

### 📋 Next Steps
1. **Initialize Wails Project**
   ```bash
   wails init -n comfyui-launcher -t typescript
   ```

2. **Port Core Logic to Go**
   - Server management (from comfy_launcher/server_manager.py)
   - Configuration handling (from comfy_launcher/config.py)
   - Event system (from comfy_launcher/event_system.py)

3. **Integrate React Frontend**
   - Copy React components from web-ui/
   - Update Wails bindings
   - Implement overlay system

4. **Testing Setup**
   - Unit tests for Go backend
   - Integration tests for Wails handlers
   - E2E tests with Playwright

### 📁 Directory Structure
```
Current Structure:
├── ADRs/                    # Architecture decisions ✅
├── docs/                    # Documentation ✅
│   └── archive/            # Archived analysis files ✅
├── web-ui/                 # Working React frontend ✅
├── scripts/                # Build and dev scripts ✅
└── tests/                  # Test directory (cleaned) ✅

Target Structure (after Wails migration):
├── cmd/app/                # Main application
├── internal/               # Go backend code
├── frontend/               # React frontend (from web-ui/)
├── tests/                  # All tests separate
├── docs/                   # Documentation
├── scripts/                # Build scripts
└── ADRs/                   # Architecture decisions
```

### 🎯 Performance Targets
- Startup time: <200ms (vs 800ms+ Python)
- Memory usage: <30MB (vs 80-120MB Python)
- Binary size: <15MB (vs 50-80MB Python)
- WSL compatibility: Full support

### 📚 Reference Materials
All analysis and implementation plans archived in:
- `docs/archive/analysis/` - Implementation strategies
- `docs/archive/legacy-python/` - Original Python code
- `ADRs/` - Architecture decisions

### 🚀 Getting Started
1. Review ADRs for context
2. Check web-ui/ for working React frontend
3. Follow WSL setup guide in docs/WSL_SETUP.md
4. Run cleanup validation: `./scripts/validate-cleanup.sh`
EOF

echo ""
echo "🔍 Creating cleanup validation script..."
cat > scripts/validate-cleanup.sh << 'EOF'
#!/bin/bash
# Validate repository cleanup

echo "🔍 Validating repository cleanup..."

# Check that legacy files are removed
LEGACY_FILES=(
    "comfy_launcher/"
    "requirements.txt"
    "build/"
    "*.bat"
    "*.ps1"
)

echo ""
echo "Checking legacy files are removed:"
for file in "${LEGACY_FILES[@]}"; do
    if [[ -e $file ]]; then
        echo "❌ Legacy file still exists: $file"
    else
        echo "✅ Removed: $file"
    fi
done

# Check that important files are preserved
IMPORTANT_FILES=(
    "ADRs/"
    "web-ui/"
    "docs/"
    "scripts/"
    "PROJECT_STATUS.md"
    ".gitignore"
)

echo ""
echo "Checking important files are preserved:"
for file in "${IMPORTANT_FILES[@]}"; do
    if [[ -e $file ]]; then
        echo "✅ Preserved: $file"
    else
        echo "❌ Missing important file: $file"
    fi
done

# Check archive structure
echo ""
echo "Checking archive structure:"
if [[ -d "docs/archive/analysis" ]] && [[ $(ls docs/archive/analysis/ | wc -l) -gt 5 ]]; then
    echo "✅ Analysis files archived ($(ls docs/archive/analysis/ | wc -l) files)"
else
    echo "❌ Analysis files not properly archived"
fi

if [[ -d "docs/archive/legacy-python" ]] && [[ -d "docs/archive/legacy-python/comfy_launcher" ]]; then
    echo "✅ Python code archived"
else
    echo "❌ Python code not properly archived"
fi

echo ""
echo "🎯 Repository size:"
du -sh . | cut -f1 | xargs echo "Total size:"
du -sh docs/archive/ 2>/dev/null | cut -f1 | xargs echo "Archive size:" || echo "Archive size: 0"

echo ""
echo "✅ Cleanup validation complete!"
EOF

chmod +x scripts/validate-cleanup.sh

echo ""
echo "📊 Repository cleanup summary:"
echo "=============================="
echo "✅ Analysis files archived to docs/archive/analysis/"
echo "✅ Python codebase archived to docs/archive/legacy-python/"
echo "✅ Build artifacts archived to docs/archive/build-artifacts/"
echo "✅ Legacy files removed"
echo "✅ Enhanced .gitignore created"
echo "✅ PROJECT_STATUS.md created"
echo "✅ Validation script created"

echo ""
echo "🎯 Next steps:"
echo "1. Run validation: ./scripts/validate-cleanup.sh"
echo "2. Review PROJECT_STATUS.md for current state"
echo "3. Check docs/archive/ for reference materials"
echo "4. Ready for Wails migration!"

echo ""
echo "🧹 Repository cleanup completed successfully!"
