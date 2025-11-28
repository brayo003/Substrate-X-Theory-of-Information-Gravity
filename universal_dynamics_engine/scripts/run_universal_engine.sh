#!/bin/bash

echo "🌌 STARTING UNIVERSAL DYNAMICS ENGINE"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "universal_pde_engine.py" ]; then
    echo "❌ Error: Run this script from universal_dynamics_engine/ directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Run the engine
python3 universal_pde_engine.py

# Save validation log
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "Engine completed at $(date)" >> logs/validation_$TIMESTAMP.log

echo "✅ Engine execution complete"
echo "📁 Logs saved to: logs/validation_$TIMESTAMP.log"
