# Security Instructions for AI Agents

## Security-First Development Policy

### Primary Rule
**ALL code MUST follow the comprehensive coding standards defined in `coding-standards.md` (including security, quality, and workflow requirements).**

### Critical Security Requirements
1. **Input Validation**: Use centralized validation utilities (see coding-standards.md)
2. **No Hardcoded Secrets**: Use .env files, never commit credentials
3. **Path Security**: Prevent traversal attacks using proper validation
4. **SQL Injection Prevention**: Parameterized queries only
5. **Error Handling**: No sensitive information in error messages

### Environment-Specific Notes
- **Production**: Use proper file permissions and security headers

### Dependency Security
```bash
# ALWAYS verify dependencies before deployment
go mod verify
npm audit
```

### Security Review Checklist
- [ ] All inputs validated using utility functions
- [ ] No hardcoded credentials or secrets
- [ ] Parameterized database queries
- [ ] Error messages don't leak sensitive data
- [ ] Security headers implemented for HTTP responses

**For detailed implementation examples and requirements, see `coding-standards.md`.**
