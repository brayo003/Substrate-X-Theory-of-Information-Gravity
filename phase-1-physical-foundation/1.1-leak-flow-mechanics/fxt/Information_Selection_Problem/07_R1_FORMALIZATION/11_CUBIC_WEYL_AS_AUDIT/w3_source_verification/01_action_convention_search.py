#!/usr/bin/env python3
"""
W3 Source Verification - Step 1: Action Convention Resolution

This script determines the actual α₂ normalization used by the project
by searching for the canonical action definition.
"""

import sys
import os
from pathlib import Path

# Search for action definition in project files
search_path = Path("/home/lenovo/Git/Substrate_X_Theory_of_Information_Gravity/phase-1-physical-foundation/1.1-leak-flow-mechanics/fxt/Information_Selection_Problem")

# Search patterns for action definition
patterns = [
    r"Γ_k.*C²",
    r"action.*C²",
    r"int.*C.*squared",
    r"w̃₂.*int",
    r"tilde.*w.*2.*int",
]

# Key files to check
key_files = [
    "07_R1_FORMALIZATION/11_CUBIC_WEYL_AS_AUDIT/42_GATE2_FINAL.md",
    "07_R1_FORMALIZATION/11_CUBIC_WEYL_AS_AUDIT/25_FRGE_W3_ACTUAL_COMPUTATION.md",
    "07_R1_FORMALIZATION/11_CUBIC_WEYL_AS_AUDIT/41_GATE2_W3_PROJECTION_RESULT.md",
]

print("=" * 70)
print("ACTION CONVENTION SEARCH")
print("=" * 70)

for key_file in key_files:
    file_path = search_path / key_file
    if file_path.exists():
        print(f"\n--- File: {key_file} ---")
        with open(file_path, 'r') as f:
            content = f.read()
            # Search for action definition
            for line_num, line in enumerate(content.split('\n'), 1):
                if 'Γ_k' in line and 'C²' in line:
                    print(f"Line {line_num}: {line.strip()}")
                if 'action' in line.lower() and 'C²' in line:
                    print(f"Line {line_num}: {line.strip()}")
                if 'w̃₂' in line and '∫' in line:
                    print(f"Line {line_num}: {line.strip()}")

print("\n" + "=" * 70)
print("SEARCHING FOR EXPLICIT α₂ MENTIONS")
print("=" * 70)

for key_file in key_files:
    file_path = search_path / key_file
    if file_path.exists():
        print(f"\n--- File: {key_file} ---")
        with open(file_path, 'r') as f:
            content = f.read()
            for line_num, line in enumerate(content.split('\n'), 1):
                if 'α₂' in line or 'alpha_2' in line:
                    print(f"Line {line_num}: {line.strip()}")

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)
print("Based on the search results above, determine the actual project convention.")
print("The key question is: does the action use w̃₂·∫C² or (w̃₂/2)·∫C²?")
