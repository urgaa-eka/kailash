#!/bin/bash

# MongoDB Backup Script for Kailash - KAILASH AI
# This script creates a complete backup of the database

BACKUP_DIR="/app/backups/mongodb"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="kailash_backup_$TIMESTAMP"
DATABASE="kailash"

echo "=================================================="
echo "Kailash - MongoDB Backup Script"
echo "=================================================="
echo ""
echo "Database: $DATABASE"
echo "Backup Directory: $BACKUP_DIR"
echo "Backup Name: $BACKUP_NAME"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup
echo "🔄 Starting backup..."
mongodump --db=$DATABASE --out="$BACKUP_DIR/$BACKUP_NAME" --quiet

if [ $? -eq 0 ]; then
    echo "✅ Backup completed successfully!"
    echo ""
    echo "Backup location: $BACKUP_DIR/$BACKUP_NAME"
    
    # Calculate backup size
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
    echo "Backup size: $BACKUP_SIZE"
    
    # Compress backup
    echo ""
    echo "🗜️  Compressing backup..."
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✅ Compression completed!"
        
        # Remove uncompressed backup
        rm -rf "$BACKUP_NAME"
        
        COMPRESSED_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
        echo "Compressed size: $COMPRESSED_SIZE"
        echo "Saved: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    else
        echo "❌ Compression failed"
    fi
    
    # List recent backups
    echo ""
    echo "📋 Recent backups (last 5):"
    ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -5 | awk '{print "  " $9 " (" $5 ")"}'
    
    # Cleanup old backups (keep last 10)
    echo ""
    echo "🧹 Cleaning up old backups (keeping last 10)..."
    cd "$BACKUP_DIR"
    ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm
    echo "✅ Cleanup complete"
    
else
    echo "❌ Backup failed!"
    exit 1
fi

echo ""
echo "=================================================="
echo "Backup completed at: $(date)"
echo "=================================================="
