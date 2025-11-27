#!/usr/bin/env python3
"""
Apply the gamma term fix: γ∇·F → γ|F|²
"""
import re

# Read the current solver
with open('src/numerical_solver.py', 'r') as f:
    content = f.read()

# Find and replace the gamma term in RHS method
old_gamma_line = '        force_term = self.gamma * self.compute_divergence(self.F)'
new_gamma_line = '        force_term = self.gamma * (self.F[:,:,0]**2 + self.F[:,:,1]**2)  # |F|²'

# Replace the line
if old_gamma_line in content:
    content = content.replace(old_gamma_line, new_gamma_line)
    print("✅ Successfully replaced γ∇·F → γ|F|²")
else:
    print("❌ Could not find the gamma term line")
    print("Looking for similar lines...")
    # Find similar lines
    gamma_lines = [line for line in content.split('\n') if 'gamma' in line and 'F' in line]
    for line in gamma_lines:
        print(f"  Found: {line.strip()}")

# Also update the docstring to reflect the change
old_docstring = '                 + αE + β∇·(E v_sub) + γF - σ_irr'
new_docstring = '                 + αE + β∇·(E v_sub) + γ|F|² - σ_irr'

if old_docstring in content:
    content = content.replace(old_docstring, new_docstring)
    print("✅ Updated docstring")

# Write the fixed version
with open('src/numerical_solver_fixed_gamma.py', 'w') as f:
    f.write(content)

print("Fixed version saved as: src/numerical_solver_fixed_gamma.py")
