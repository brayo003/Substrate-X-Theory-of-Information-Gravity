#!/bin/bash
echo "=== QFT-GR BRIDGE EXECUTION ==="
echo "Date: $(date)"
echo ""

echo "1. Running main bridge analysis..."
python3 unified_bridge_v12.py

echo ""
echo "2. Quick validation..."
python3 validate.py

echo ""
echo "=== EXECUTION COMPLETE ==="
echo "Bridge analysis finished successfully"
