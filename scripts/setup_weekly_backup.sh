#!/bin/bash
# Setup weekly automated backups (run once)

CRON_JOB="0 2 * * 0 $PWD/scripts/backup_ip.sh > /dev/null 2>&1"

echo "Setting up weekly Sunday 2 AM backups..."
(crontab -l 2>/dev/null | grep -v "backup_ip.sh"; echo "$CRON_JOB") | crontab -

echo "✅ Weekly backups scheduled"
echo "To view: crontab -l"
echo "To remove: crontab -e"
