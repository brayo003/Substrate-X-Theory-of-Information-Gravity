import numpy as np
import matplotlib.pyplot as plt

# Your predictions
distances = np.array([0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01])
F_X_pred = np.array([6.04e-12, 1.62e-13, 2.46e-14, 2.26e-15, 1.80e-17, 3.03e-20])

# Eöt-Wash 2012 constraints (approximate from their paper)
# Distance (m) : Max allowed force (N) for 1g masses
eotwash_data = {
    'distance': [5e-5, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2],
    'max_force': [1e-12, 3e-13, 1e-13, 3e-14, 1e-14, 5e-15, 2e-15, 1e-15]
}

print("="*70)
print("COMPARISON WITH EÖT-WASH 2012 DATA")
print("="*70)
print("\nDistance | Your Prediction | Eöt-Wash Limit | Status")
print("-"*55)

ruled_out = False
for i, r in enumerate(distances):
    # Find closest Eöt-Wash data point
    idx = np.argmin(np.abs(np.array(eotwash_data['distance']) - r))
    eot_dist = eotwash_data['distance'][idx]
    eot_limit = eotwash_data['max_force'][idx]
    
    if r <= 0.002:  # Only compare where we have predictions
        status = "❌ RULED OUT" if F_X_pred[i] > eot_limit else "✅ Allowed"
        if F_X_pred[i] > eot_limit:
            ruled_out = True
        
        print(f"{r*1000:6.1f} mm | {F_X_pred[i]:8.2e} N | {eot_limit:8.2e} N | {status}")

print("\n" + "="*70)
if ruled_out:
    print("THEORY IS ALREADY RULED OUT BY EÖT-WASH 2012!")
    print("Your prediction at 0.1 mm is 20× ABOVE their limit.")
else:
    print("Theory not yet ruled out (but close to limits).")

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(np.array(distances)*1000, F_X_pred, 'bo-', linewidth=2, markersize=8, label='Your Theory')
ax.plot(np.array(eotwash_data['distance'])*1000, eotwash_data['max_force'], 'r--', linewidth=2, label='Eöt-Wash 2012 Limit')
ax.fill_between(np.array(eotwash_data['distance'])*1000, 0, eotwash_data['max_force'], alpha=0.2, color='red', label='Excluded Region')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Distance (mm)', fontsize=12)
ax.set_ylabel('Force (N) for 1g masses', fontsize=12)
ax.set_title('Your Theory vs Experimental Limits', fontsize=14)
ax.grid(True, alpha=0.3)
ax.legend()

# Highlight critical region
ax.axvspan(0.05, 2.0, alpha=0.1, color='yellow', label='Critical test region')

plt.tight_layout()
plt.savefig('theory_vs_experiment.png', dpi=150)

print(f"\n📊 Plot saved to 'theory_vs_experiment.png'")
print("\n" + "="*70)
print("NEXT STEP: Check CANNEX (2023) and other experiments")
print("If still above limits → Theory is falsified.")
print("="*70)
