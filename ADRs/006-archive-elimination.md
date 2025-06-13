# ADR-006: Archive Directory Elimination

**Date**: 2024-12-31  
**Status**: Accepted  

## Decision
Remove the `docs/archive/` directory and eliminate the practice of archiving old documentation.

## Context
The project maintained an archive of 10+ legacy documentation files that overlapped with existing ADRs and documentation. This creates:
- Redundant information maintenance burden
- Confusion about authoritative sources
- Unnecessary repository bloat
- Unclear information hierarchy

## Rationale
1. **Git provides history**: All historical context is preserved in version control
2. **ADRs capture decisions**: Architecture Decision Records already document evolution
3. **Single source of truth**: Active documentation should be the only reference
4. **Lean development**: Minimal, essential-only documentation approach

## Implementation
- Deleted `docs/archive/` directory containing 10 legacy files
- Rely on git history for archaeological purposes
- Update documentation philosophy in README
- Commit practices for significant milestones

## Consequences
- **Positive**: Cleaner repository, reduced maintenance, clear information hierarchy
- **Negative**: Historical context requires git archaeology
- **Mitigation**: ADRs and commit messages capture decision rationale
