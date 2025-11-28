#!/bin/bash
# Secure IP Backup Script - Backs up to ~/.backup/substrate_x/

BACKUP_ROOT="$HOME/.backup/substrate_x"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directories
mkdir -p "$BACKUP_ROOT/ip_documents"
mkdir -p "$BACKUP_ROOT/code_snapshots" 
mkdir -p "$BACKUP_ROOT/legal_documents"

echo "🔒 Starting secure backup to ~/.backup/substrate_x/..."

# 1. Backup IP documents
tar -czf "$BACKUP_ROOT/ip_documents/ip_backup_$TIMESTAMP.tar.gz" legal/ip_protection/
echo "✅ IP documents backed up: ip_documents/ip_backup_$TIMESTAMP.tar.gz"

# 2. Backup legal contracts
tar -czf "$BACKUP_ROOT/legal_documents/legal_backup_$TIMESTAMP.tar.gz" legal/contracts/ legal/business/
echo "✅ Legal documents backed up: legal_documents/legal_backup_$TIMESTAMP.tar.gz"

# 3. Backup code snapshot (for IP evidence) - FIXED: exclude options before files
tar -czf "$BACKUP_ROOT/code_snapshots/code_snapshot_$TIMESTAMP.tar.gz" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    universal_dynamics_engine/ \
    tests/test_regime_transition*.py \
    demo_breakthrough_prediction.py
echo "✅ Code snapshot backed up: code_snapshots/code_snapshot_$TIMESTAMP.tar.gz"

# 4. Create backup manifest
cat > "$BACKUP_ROOT/backup_manifest_$TIMESTAMP.md" << MANIFEST
# BACKUP MANIFEST - SUBSTRATE X ENGINE
Backup created: $(date)
Location: $BACKUP_ROOT

## Contents:
- IP Documents: ip_documents/ip_backup_$TIMESTAMP.tar.gz
- Legal Documents: legal_documents/legal_backup_$TIMESTAMP.tar.gz  
- Code Snapshot: code_snapshots/code_snapshot_$TIMESTAMP.tar.gz

## Purpose:
Intellectual Property protection and evidence of development timeline.

## Security:
- Backups stored in $HOME/.backup/ (user-private)
- Regular backups recommended for IP protection
MANIFEST

echo "📋 Backup manifest created: backup_manifest_$TIMESTAMP.md"

# Show backup summary
echo ""
echo "🎯 BACKUP COMPLETE"
echo "📍 Location: ~/.backup/substrate_x/"
echo "📦 Files:"
find "$BACKUP_ROOT" -name "*$TIMESTAMP*" -type f | while read file; do
    echo "   - $(basename "$file") ($(du -h "$file" | cut -f1))"
done

echo ""
echo "🚫 REMINDER: These backups contain trade secrets"
echo "   Never upload to cloud services without encryption"
echo "   Keep backup location secure"
