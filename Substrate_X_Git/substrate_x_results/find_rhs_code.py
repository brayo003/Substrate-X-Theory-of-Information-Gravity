#!/usr/bin/env python3
"""Find the exact RHS code"""
import re

with open('src/numerical_solver.py', 'r') as f:
    content = f.read()

# Find the RHS method
rhs_match = re.search(r'def rhs\(.*?(?=def|\Z)', content, re.DOTALL)
if rhs_match:
    print("RHS METHOD FOUND:")
    print("=" * 60)
    print(rhs_match.group(0))
    print("=" * 60)
    
    # Find gamma term specifically
    gamma_lines = re.findall(r'.*gamma.*', rhs_match.group(0))
    if gamma_lines:
        print("\nGAMMA TERM LINES:")
        for line in gamma_lines:
            print(f"  {line.strip()}")
