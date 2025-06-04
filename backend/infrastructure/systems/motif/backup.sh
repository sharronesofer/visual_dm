#!/bin/bash

# Motif System Backup Script
# Usage: ./backup.sh [--config-only] [--data-only] [--full]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Parse command line arguments
BACKUP_CONFIG=true
BACKUP_DATA=true

for arg in "$@"
do
    case $arg in
        --config-only)
        BACKUP_CONFIG=true
        BACKUP_DATA=false
        shift
        ;;
        --data-only)
        BACKUP_CONFIG=false
        BACKUP_DATA=true
        shift
        ;;
        --full)
        BACKUP_CONFIG=true
        BACKUP_DATA=true
        shift
        ;;
        --help)
        echo "Usage: $0 [--config-only] [--data-only] [--full]"
        echo "  --config-only  Backup only configuration files"
        echo "  --data-only    Backup only database and cache data"
        echo "  --full         Backup everything (default)"
        exit 0
        ;;
    esac
done

echo "🔄 Starting Motif System Backup ($(date))"
echo "   Backup Directory: $BACKUP_DIR"
echo "   Timestamp: $DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Configuration backup
if [ "$BACKUP_CONFIG" = true ]; then
    echo "📁 Backing up configuration files..."
    
    CONFIG_BACKUP="$BACKUP_DIR/config_backup_$DATE.tar.gz"
    
    tar -czf "$CONFIG_BACKUP" \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='logs/*' \
        --exclude='backups/*' \
        .env \
        docker/ \
        database/ \
        monitoring/ \
        schemas/ \
        models/ \
        routers/ \
        repositories/ \
        cache/ \
        utils/ \
        *.py \
        *.md \
        *.sh \
        2>/dev/null || echo "⚠️  Some configuration files may not exist"
    
    if [ -f "$CONFIG_BACKUP" ]; then
        echo "✅ Configuration backup created: $CONFIG_BACKUP"
        echo "   Size: $(du -h "$CONFIG_BACKUP" | cut -f1)"
    else
        echo "❌ Configuration backup failed"
    fi
fi

# Data backup
if [ "$BACKUP_DATA" = true ]; then
    echo "🗄️  Backing up database and cache data..."
    
    # Check if Docker is available
    if command -v docker &> /dev/null; then
        
        # Database backup
        echo "   • Backing up PostgreSQL database..."
        DB_BACKUP="$BACKUP_DIR/motif_db_$DATE.sql"
        
        if docker compose -f docker/docker-compose.yml exec -T postgres pg_dump -U motif_user motif_db > "$DB_BACKUP" 2>/dev/null; then
            echo "   ✅ Database backup created: $DB_BACKUP"
            echo "      Size: $(du -h "$DB_BACKUP" | cut -f1)"
            
            # Compress database backup
            gzip "$DB_BACKUP"
            echo "   📦 Database backup compressed: ${DB_BACKUP}.gz"
        else
            echo "   ❌ Database backup failed (container may not be running)"
        fi
        
        # Redis backup
        echo "   • Backing up Redis cache..."
        REDIS_BACKUP="$BACKUP_DIR/redis_$DATE.rdb"
        
        # Trigger Redis save
        if docker compose -f docker/docker-compose.yml exec -T redis redis-cli BGSAVE >/dev/null 2>&1; then
            sleep 2  # Wait for background save to complete
            
            if docker cp motif_redis:/data/dump.rdb "$REDIS_BACKUP" 2>/dev/null; then
                echo "   ✅ Redis backup created: $REDIS_BACKUP"
                echo "      Size: $(du -h "$REDIS_BACKUP" | cut -f1)"
                
                # Compress Redis backup
                gzip "$REDIS_BACKUP"
                echo "   📦 Redis backup compressed: ${REDIS_BACKUP}.gz"
            else
                echo "   ❌ Redis backup failed (dump file may not exist)"
            fi
        else
            echo "   ❌ Redis backup failed (container may not be running)"
        fi
        
        # Docker volumes backup
        echo "   • Backing up Docker volumes..."
        VOLUMES_BACKUP="$BACKUP_DIR/volumes_$DATE.tar.gz"
        
        # Get volume names
        POSTGRES_VOLUME=$(docker volume ls --format "{{.Name}}" | grep postgres || echo "")
        REDIS_VOLUME=$(docker volume ls --format "{{.Name}}" | grep redis || echo "")
        
        if [ -n "$POSTGRES_VOLUME" ] || [ -n "$REDIS_VOLUME" ]; then
            docker run --rm \
                ${POSTGRES_VOLUME:+-v "$POSTGRES_VOLUME:/backup/postgres"} \
                ${REDIS_VOLUME:+-v "$REDIS_VOLUME:/backup/redis"} \
                -v "$BACKUP_DIR:/backup/output" \
                alpine:latest \
                sh -c "cd /backup && tar -czf output/volumes_$DATE.tar.gz postgres redis 2>/dev/null || true"
            
            if [ -f "$VOLUMES_BACKUP" ]; then
                echo "   ✅ Volumes backup created: $VOLUMES_BACKUP"
                echo "      Size: $(du -h "$VOLUMES_BACKUP" | cut -f1)"
            fi
        else
            echo "   ⚠️  No Docker volumes found to backup"
        fi
        
    else
        echo "   ❌ Docker not available. Skipping data backup."
    fi
fi

# Create backup manifest
MANIFEST="$BACKUP_DIR/manifest_$DATE.txt"
echo "Motif System Backup Manifest" > "$MANIFEST"
echo "Created: $(date)" >> "$MANIFEST"
echo "Backup Directory: $BACKUP_DIR" >> "$MANIFEST"
echo "Configuration Backup: $BACKUP_CONFIG" >> "$MANIFEST"
echo "Data Backup: $BACKUP_DATA" >> "$MANIFEST"
echo "" >> "$MANIFEST"
echo "Files:" >> "$MANIFEST"
ls -lh "$BACKUP_DIR"/*_"$DATE"* >> "$MANIFEST" 2>/dev/null || echo "No backup files found" >> "$MANIFEST"

echo "📋 Backup manifest created: $MANIFEST"

# Cleanup old backups
echo "🧹 Cleaning up old backups (retention: $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.rdb.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "manifest_*.txt" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# Summary
echo ""
echo "🎉 Backup Complete!"
echo "   Backup Location: $BACKUP_DIR"
echo "   Files Created:"
ls -lh "$BACKUP_DIR"/*_"$DATE"* 2>/dev/null || echo "   No backup files created"

echo ""
echo "💡 Tips:"
echo "   • Schedule regular backups with cron: 0 2 * * * /path/to/backup.sh"
echo "   • Test restores periodically to verify backup integrity"
echo "   • Consider offsite backup storage for production systems"
echo "   • Monitor backup logs for any errors or warnings"

exit 0 