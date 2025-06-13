# AI Project Management System

## Data Persistence & Backup

This system now uses local bind mounts for data persistence, providing better control and backup capabilities.

### Data Structure
```
ai-pm/
├── data/                 # Persistent data (excluded from git)
│   ├── postgres/        # PostgreSQL database files
│   ├── redis/           # Redis cache files
│   └── minio/           # MinIO object storage files
├── backups/             # Backup archives (excluded from git)
└── scripts/
    ├── backup.sh        # Create backup
    └── restore.sh       # Restore from backup
```

### Backup Procedures

#### Create Backup
```bash
./scripts/backup.sh
```
- Automatically stops services for consistent backup
- Creates timestamped archive in `./backups/`
- Restarts services after backup
- Keeps last 10 backups (auto-cleanup)

#### Restore from Backup
```bash
./scripts/restore.sh ./backups/ai-pm-backup-TIMESTAMP.tar.gz
```
- Backs up current data before restore
- Completely replaces current data
- Requires manual service restart

### Best Practices

1. **Regular Backups**: Create backups before major changes
2. **Pre-Change Backup**: Always backup before infrastructure modifications
3. **Test Restores**: Periodically test restore procedures
4. **Monitor Disk Space**: Backups accumulate over time

### Recovery from Data Loss

If data is lost:
1. Stop services: `docker-compose down`
2. List available backups: `ls -la ./backups/`
3. Restore: `./scripts/restore.sh <backup-file>`
4. Start services: `docker-compose up -d`

### Emergency Procedures

If corruption occurs:
1. Immediate backup: `./scripts/backup.sh` (even if corrupted)
2. Stop services: `docker-compose down -v`
3. Remove data: `rm -rf data/`
4. Restore from last good backup
5. Restart: `docker-compose up -d`

### Data Location

All persistent data is stored locally in the `./data/` directory:
- **PostgreSQL**: `./data/postgres/` - All database content
- **Redis**: `./data/redis/` - Cache and session data  
- **MinIO**: `./data/minio/` - File storage and uploads

This approach provides:
- ✅ Easy backup and restore
- ✅ Version control friendly (data excluded)
- ✅ Transparent data access
- ✅ No Docker volume complexity
- ✅ Cross-platform compatibility
