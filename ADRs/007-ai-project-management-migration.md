# ADR 007: AI-Driven Project Management System Migration

**Status:** Accepted  
**Date:** 2025-06-13  
**Deciders:** AI Development Team  

## Context

We needed a robust, AI-friendly project management system for the universal AI tool launcher project. Initially attempted to use Plane (open source project management) but encountered platform compatibility issues in the WSL2/Docker Desktop environment.

## Decision

Migrate from Plane to a custom AI Project Manager system that:

1. **Reuses Solid Infrastructure**: Keeps PostgreSQL, Redis, and MinIO components
2. **Custom Implementation**: Uses our own project management CLI and database schema
3. **AI-Friendly Design**: Built specifically for AI agent interaction
4. **Meaningful Naming**: Containers renamed to reflect AI Project Manager purpose

## Implementation

### Container Renaming
- `plane-redis` → `ai-pm-cache` (Redis cache)
- `plane-db` → `ai-pm-database` (PostgreSQL database)  
- `plane-minio` → `ai-pm-storage` (MinIO object storage)
- `plane-api` → `ai-pm-api` (API backend)
- `plane-web` → `ai-pm-web` (Web frontend)

### Database Schema
Simple, effective schema for project management:
- `projects`: Project information and status
- `tasks`: Task management with priorities and status
- `notes`: Comments and progress tracking

### CLI Interface
Custom `project-manager.sh` script providing:
- Project creation and management
- Task tracking and status updates
- Note/comment system
- Direct database interaction

### Environment Migration
- Updated `.env` variables from `PLANE_*` to `AI_PM_*`
- Updated Makefile commands from `plane-*` to `ai-pm-*`
- Renamed Docker Compose file to `docker-compose.ai-pm.yml`

## Consequences

### Positive
- ✅ **Working Infrastructure**: Database, cache, and storage are fully operational
- ✅ **AI-Friendly**: Command-line interface perfect for AI agent automation
- ✅ **Lightweight**: No complex web UI dependencies, direct database access
- ✅ **Customizable**: Can extend schema and functionality as needed
- ✅ **Platform Independent**: Core functionality works regardless of frontend issues

### Negative
- ❌ **Limited Web UI**: No immediate web interface (API/Web services have platform issues)
- ❌ **Manual Setup**: Requires custom tooling vs. off-the-shelf solution

### Neutral
- 🔄 **Migration Path**: Can still add web UI later or integrate with other tools
- 🔄 **API Integration**: Can build REST API on top of existing database

## Implementation Status

**Completed:**
- ✅ Container renaming and environment migration
- ✅ Database schema creation and initialization
- ✅ CLI project management interface
- ✅ First project and tasks created
- ✅ Documentation and ADR creation

**In Progress:**
- 🔄 Resolving platform compatibility for API/Web services

**Future:**
- 📋 Web UI development (custom or alternative)
- 📋 REST API for external integrations
- 📋 Enhanced reporting and analytics

## Related ADRs

- ADR 001: Technology Stack Selection
- ADR 002: Project Structure Architecture  
- ADR 005: Complete Implementation Strategy
