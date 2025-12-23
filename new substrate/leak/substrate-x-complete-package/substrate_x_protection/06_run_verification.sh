#!/bin/bash
echo "RUNNING SUBSTRATE X THEORY VERIFICATION"
echo "========================================"
cd ..
echo "MERCURY TEST:"
python3 mercury_precession_test.py
echo ""
echo "LENSING TEST:"
python3 gravitational_lensing_test.py
echo ""
echo "PULSAR TEST:"
python3 binary_pulsar_test.py
