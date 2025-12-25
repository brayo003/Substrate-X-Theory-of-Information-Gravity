#!/bin/bash

# Simple run script for DCII Framework

echo "DCII Framework - Quick Start"
echo "============================"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check for main files
if [ -f "main.py" ]; then
    echo "Running from modular files..."
    python3 main.py
elif [ -f "enhanced_dcii_solver.py" ]; then
    echo "Running from single file..."
    python3 enhanced_dcii_solver.py
elif [ -f "dcii_framework.py" ]; then
    echo "Running from standard framework..."
    python3 dcii_framework.py
else
    echo "Error: No DCII Python file found!"
    echo ""
    echo "To create a basic implementation, run:"
    echo "  curl -O https://raw.githubusercontent.com/example/dcii/main/dcii_framework.py"
    echo "  python3 dcii_framework.py"
    exit 1
fi
