#!/bin/bash
set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE="$1"
BACKUP_DIR="/backups"
FULL_PATH="$BACKUP_DIR/$BACKUP_FILE"

if [[ ! -f "$FULL_PATH" ]]; then
    echo "Error: Backup file $FULL_PATH does not exist"
    exit 1
fi

# Determine backup type
if [[ "$BACKUP_FILE" == db_* ]]; then
    echo "Restoring database from $BACKUP_FILE..."
    
    # Drop and recreate database
    PGPASSWORD=$POSTGRES_PASSWORD dropdb -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB || true
    PGPASSWORD=$POSTGRES_PASSWORD createdb -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB
    
    # Restore database
    gunzip -c "$FULL_PATH" | PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_DB
    
    echo "Database restore completed successfully!"

elif [[ "$BACKUP_FILE" == media_* ]]; then
    echo "Restoring media files from $BACKUP_FILE..."
    
    # Clear existing media files
    rm -rf /data/media/*
    
    # Restore media files
    tar -xzf "$FULL_PATH" -C /data/media
    
    echo "Media files restore completed successfully!"

else
    echo "Error: Unknown backup file type"
    exit 1
fi 