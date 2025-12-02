#!/usr/bin/env python3
"""
Simple visualization of UTD results.
"""
import json
import matplotlib.pyplot as plt
import numpy as np

# Load results
with open("results/utd_final_results.json", "r") as f:
    data = json.load(f)

S = data['S_spectral_entropy']
Q = data['Q_coherence']
delta2 = data['delta2_volatility']
C = data['C_scaled']

print("📊 UTD RESULTS VISUALIZATION")
print("=" * 50)

# 1. Bar chart of components
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

# Component values
components = ['S', 'Q', 'δ²']
values = [S, Q, delta2]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

ax1.bar(components, values, color=colors)
ax1.set_ylabel('Value')
ax1.set_title('UTD Components')
ax1.grid(True, alpha=0.3)

# Add component explanations
ax1.text(0.5, -0.15, f'S={S:.4f}\nNetwork decentralization', 
         transform=ax1.transAxes, ha='center', fontsize=9)
ax1.text(0.5, -0.25, f'Q={Q:.8f}\nTraffic concentration', 
         transform=ax1.transAxes, ha='center', fontsize=9)
ax1.text(0.5, -0.35, f'δ²={delta2:.8f}\nWeight inequality', 
         transform=ax1.transAxes, ha='center', fontsize=9)

# 2. C-score with thresholds
ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='High tension (70)')
ax2.axhline(y=30, color='orange', linestyle='--', alpha=0.5, label='Moderate (30)')
ax2.bar(['C-score'], [C], color='purple')
ax2.set_ylabel('C-score')
ax2.set_title(f'Information Gravity: C = {C:.2f}')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Color based on value
if C > 70:
    ax2.patches[0].set_facecolor('red')
elif C > 30:
    ax2.patches[0].set_facecolor('orange')
else:
    ax2.patches[0].set_facecolor('green')

# 3. Radar chart of components (normalized)
ax3 = fig.add_subplot(223, projection='polar')
angles = np.linspace(0, 2*np.pi, len(components), endpoint=False)
values_norm = [S/5.64, Q/1.0, delta2/1.0]  # Normalize to 0-1
values_norm += values_norm[:1]  # Close the polygon
angles = np.concatenate((angles, [angles[0]]))

ax3.plot(angles, values_norm, 'o-', linewidth=2)
ax3.fill(angles, values_norm, alpha=0.25)
ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(['S', 'Q', 'δ²'])
ax3.set_title('Component Balance (Normalized)')
ax3.grid(True)

# 4. Geometric mean explanation
ax4.text(0.1, 0.8, f'C = k × (S × Q × δ²)^(¹/₃)', fontsize=12)
ax4.text(0.1, 0.6, f'  = 100 × ({S:.4f} × {Q:.8f} × {delta2:.8f})^(¹/₃)', fontsize=10)
ax4.text(0.1, 0.5, f'  = 100 × {(S*Q*delta2):.10f}^(¹/₃)', fontsize=10)
ax4.text(0.1, 0.4, f'  = 100 × {data["C_raw"]:.6f}', fontsize=10)
ax4.text(0.1, 0.3, f'  = {C:.2f}', fontsize=14, weight='bold')

# Interpretation
if C > 70:
    interpretation = "🚨 HIGH INFORMATION GRAVITY\nStrong centralization & concentration"
elif C > 30:
    interpretation = "⚠️  MODERATE TENSION\nBalanced structure"
else:
    interpretation = "✅ STABLE STRUCTURE\nRelative decentralization"

ax4.text(0.1, 0.1, interpretation, fontsize=11, 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
ax4.axis('off')
ax4.set_title('Calculation & Interpretation')

plt.tight_layout()
plt.savefig('results/utd_visualization.png', dpi=150, bbox_inches='tight')
print("✅ Visualization saved to: results/utd_visualization.png")

# Show in terminal too
print(f"""
┌─────────────────────────────────────┐
│         WIKIPEDIA UTD RESULTS       │
├─────────────────────────────────────┤
│ Spectral Entropy (S): {S:>10.4f}    │
│ Coherence (Q):        {Q:>10.8f}    │
│ Volatility (δ²):      {delta2:>10.8f}│
├─────────────────────────────────────┤
│ INFORMATION GRAVITY (C): {C:>8.2f}  │
└─────────────────────────────────────┘
""")

if C > 70:
    print("🚨 CONCLUSION: Wikipedia shows HIGH INFORMATION GRAVITY")
    print("   - Strong centralization (low-moderate S)")
    print("   - Traffic concentrates on few pages (high Q)")
    print("   - Edge weights highly unequal (high δ²)")
elif C > 30:
    print("⚠️  CONCLUSION: Wikipedia shows MODERATE TENSION")
    print("   - Balanced network structure")
    print("   - Some centralization, some diversity")
else:
    print("✅ CONCLUSION: Wikipedia shows STABLE STRUCTURE")
    print("   - Relatively decentralized")
    print("   - Distributed traffic and weights")
