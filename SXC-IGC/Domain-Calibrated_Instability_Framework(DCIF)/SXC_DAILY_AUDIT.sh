#!/bin/bash
# SXC-IGC Daily Stability Reporter

# 1. Extract the last 24 hours of logs from the Docker container
docker logs sxc-active-node > logs/daily_telemetry.log

# 2. Run the Dashboard script against the fresh data
# Note: Ensure DASHBOARD.py is set to read from 'logs/daily_telemetry.log'
python3 DASHBOARD.py --source logs/daily_telemetry.log --output docs/reports/$(date +%Y-%m-%d)_stability.png

# 3. Cleanup old logs to prevent disk bloat
find logs/ -name "*.log" -mtime +7 -exec rm {} \;

echo "[AUDIT COMPLETE] Report generated: docs/reports/$(date +%Y-%m-%d)_stability.png"
