#!/bin/bash
set -e

# Configuration
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_BACKUP_PATH="$BACKUP_DIR/db_$TIMESTAMP.sql.gz"
MEDIA_BACKUP_PATH="$BACKUP_DIR/media_$TIMESTAMP.tar.gz"

# Ensure backup directory exists
mkdir -p $BACKUP_DIR

# Database backup
echo "Starting database backup..."
PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB | gzip > $DB_BACKUP_PATH
echo "Database backup completed: $DB_BACKUP_PATH"

# Media files backup
echo "Starting media files backup..."
tar -czf $MEDIA_BACKUP_PATH -C /data/media .
echo "Media backup completed: $MEDIA_BACKUP_PATH"

# Upload to S3
echo "Uploading backups to S3..."
python /app/upload_to_s3.py $DB_BACKUP_PATH $MEDIA_BACKUP_PATH

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -name "*.gz" -delete

echo "Backup process completed successfully!" 