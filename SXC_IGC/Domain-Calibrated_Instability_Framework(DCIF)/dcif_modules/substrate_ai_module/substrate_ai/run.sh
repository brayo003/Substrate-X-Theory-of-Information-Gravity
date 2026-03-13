#!/bin/bash
# RUN SCRIPT - Execute the system

echo "🚀 SUBSTRATE AI SYSTEM - COGNITIVE GOVERNOR"
echo "=========================================="

# Check Python
python3 --version || { echo "Python 3 required"; exit 1; }

# Install dependencies if needed
pip install -r requirements.txt 2>/dev/null || {
    echo "Installing requirements..."
    pip install numpy sympy requests > /dev/null 2>&1
}

# Run tests
echo -e "\n🧪 Running test suite..."
python3 test_system.py

echo -e "\n🎮 Interactive mode:"
echo "python3 -c \"from cognitive_governor import CognitiveGovernor; cg = CognitiveGovernor(); print(cg.process_question('YOUR_QUESTION_HERE'))\""
