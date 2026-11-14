import numpy as np
import matplotlib.pyplot as plt

print("="*80)
print("THE VISIBILITY FLOOR: Resolution Limits of Modern Physics")
print("="*80)

# Current experimental landscape
experiments = [
    ("Eöt-Wash 2012", 1e-15, 0.05, "Torsion balance"),
    ("CANNEX 2023", 5e-16, 0.5, "Casimir force"),
    ("Stanford 2021", 2e-15, 2.0, "Microsphere"),
    ("Irvine 2019", 3e-15, 1.0, "Torsion pendulum"),
    ("Your Theory", 2.3e-17, 1.0, "Millimeter force"),
]

print("\nCURRENT RESOLUTION LIMITS (Force sensitivity at 1 mm):")
print("-"*80)
print(f"{'Experiment':<20} {'Sensitivity (N)':<20} {'Distance (mm)':<15} {'Type':<20}")
print("-"*80)

for name, sens, dist, typ in experiments:
    print(f"{name:<20} {sens:<20.1e} {dist:<15.1f} {typ:<20}")

# Your theory establishes the FLOOR
floor_sensitivity = 2.3e-17  # N
print(f"\n{'='*80}")
print("THE VISIBILITY FLOOR:")
print(f"Any force weaker than {floor_sensitivity:.1e} N at 1 mm")
print(f"is INVISIBLE to current technology.")
print(f"This is 43× below Eöt-Wash sensitivity.")

# What could hide below this floor?
print(f"\n{'='*80}")
print("WHAT COULD HIDE BELOW THE FLOOR:")
print("-"*80)

possibilities = [
    ("Extra dimensions", "Forces from mm-scale extra dimensions"),
    ("Quantum gravity", "Planck-scale effects amplified to mm scale"),
    ("Dark matter", "Ultra-weak couplings to normal matter"),
    ("Cosmic relics", "Fields from early universe"),
    ("String theory", "Low-energy signatures of strings"),
]

for i, (name, desc) in enumerate(possibilities, 1):
    print(f"{i}. {name}: {desc}")

# Create visibility map
fig, ax = plt.subplots(figsize=(12, 8))

# Experimental sensitivities
names = [e[0] for e in experiments]
sens = [e[1] for e in experiments]
dist = [e[2] for e in experiments]

colors = ['blue', 'green', 'orange', 'red', 'purple']
for i, (name, s, d, c) in enumerate(zip(names, sens, dist, colors)):
    ax.scatter(d, s, s=300, color=c, label=name, alpha=0.7, edgecolor='black')
    ax.text(d, s*1.5, name, ha='center', fontsize=9)

# Your theory as the floor
ax.axhline(y=floor_sensitivity, color='black', linestyle='--', linewidth=2, 
           label=f'Visibility Floor ({floor_sensitivity:.1e} N)')
ax.fill_between([0, 10], 0, floor_sensitivity, alpha=0.2, color='gray', 
                label='Invisible Region')

ax.set_xscale('linear')
ax.set_yscale('log')
ax.set_xlabel('Characteristic Distance (mm)', fontsize=12)
ax.set_ylabel('Force Sensitivity (N) for 1g masses', fontsize=12)
ax.set_title('The Visibility Floor: What Experiments Can and Cannot See', fontsize=14)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right')
ax.set_xlim(0, 5)
ax.set_ylim(1e-18, 1e-14)

plt.tight_layout()
plt.savefig('visibility_floor_map.png', dpi=150, bbox_inches='tight')

print(f"\n📊 Visibility floor map saved to 'visibility_floor_map.png'")

# Calculate when we might reach this floor
print(f"\n{'='*80}")
print("TIMELINE TO REACH THE FLOOR:")
print("-"*80)

current_best = 1e-15  # N
target = floor_sensitivity
improvement_needed = current_best / target

print(f"Current best: {current_best:.1e} N")
print(f"Your floor: {target:.1e} N")
print(f"Improvement needed: {improvement_needed:.1f}×")

# Moore's Law for sensitivity (historical improvement ~10× per decade)
years_needed = np.log10(improvement_needed) * 10  # Rough estimate
print(f"Estimated time to reach floor: {years_needed:.1f} years (~{2030+int(years_needed)})")

print(f"\n{'='*80}")
print("SCIENTIFIC VALUE OF THE FLOOR:")
print("-"*80)
print("""
1. Guides experimental design: "Don't build experiments that can't reach this"
2. Sets priorities: "Focus on forces ABOVE this floor first"
3. Defines "new physics" threshold: Anything below = "not yet physics"
4. Provides calibration: "This is what 'nothing' looks like"
""")

with open('visibility_floor_analysis.txt', 'w') as f:
    f.write("THE VISIBILITY FLOOR ANALYSIS\n")
    f.write("="*60 + "\n\n")
    f.write(f"Floor sensitivity: {floor_sensitivity:.1e} N at 1 mm\n")
    f.write(f"Improvement needed: {improvement_needed:.1f}×\n")
    f.write(f"Time to reach: ~{years_needed:.1f} years\n\n")
    f.write("Scientific implications:\n")
    f.write("1. Defines the resolution limit of fifth-force searches\n")
    f.write("2. Guides future experimental design\n")
    f.write("3. Separates 'testable physics' from 'mathematical possibilities'\n")
    f.write("4. Provides null hypothesis for anomaly detection\n")

print(f"\n📁 Analysis saved to 'visibility_floor_analysis.txt'")
