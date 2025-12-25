#!/bin/bash

echo "Installing DCII Framework..."
echo "============================="

# Check Python version
echo "Python version: $(python3 --version)"

# Create virtual environment (optional)
if [ "$1" == "--venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
        USE_VENV=true
    fi
fi

# Install requirements if file exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Installing core dependencies..."
    pip install pandas numpy scipy matplotlib
fi

echo ""
echo "Checking dependencies..."
python3 -c "import pandas; import numpy; import scipy; import matplotlib; print('✓ All dependencies installed')"

echo ""
echo "Running DCII Framework..."
echo "========================="
echo ""

# Run the main script
if [ -f "main.py" ]; then
    python3 main.py
elif [ -f "enhanced_dcii_solver.py" ]; then
    python3 enhanced_dcii_solver.py
else
    echo "Error: No main Python file found!"
    echo "Available Python files:"
    ls *.py
    exit 1
fi

# Deactivate virtual environment if used
if [ "$USE_VENV" = true ]; then
    deactivate
    echo "Virtual environment deactivated."
fi
