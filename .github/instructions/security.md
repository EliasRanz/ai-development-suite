Comprehensive input validation for all user inputs and external data.

Path traversal protection - reject paths containing "..".

Never commit credentials - use .env files for secrets (already in .gitignore).

WSL `777` permissions are normal DRVFS behavior, not a security risk.

Verify dependencies with `go mod verify` and `npm audit`.
