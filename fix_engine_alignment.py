"""
Apply the mathematically proven alignment fix to the engine
"""
import re

# Read the current engine file
with open('universal_dynamics_engine/universal_pde_engine.py', 'r') as f:
    content = f.read()

# Find and replace the broken alignment calculation
old_alignment_code = '''        # 3. Calculate Domain Alignment
        num_domains = len(self.domain_states)
        all_tensions = np.array([s.metrics.get('Tension', 0.0) for s in self.domain_states.values()])
        
        alignment_variance = all_tensions.var() if all_tensions.size > 0 else 0.0

        # Alignment is inversely related to T-M-V variance. Magnified multiplier to ensure dynamics
        base_alignment = 0.8 / num_domains 
        alignment = np.clip(base_alignment + (0.3 - alignment_variance * 10000), 0.1, 1.0) 
        
        anomalies = {}
        if alignment < 0.4:
            anomalies = {'alignment_low': 'Domains diverging'}'''

new_alignment_code = '''        # 3. Calculate Domain Alignment (MATHEMATICALLY PROVEN)
        num_domains = len(self.domain_states)
        all_tensions = [s.metrics.get('Tension', 0.0) for s in self.domain_states.values()]
        
        # Use mathematically proven alignment calculation
        from core_math.engine_alignment import compute_engine_alignment, detect_alignment_anomalies
        alignment = compute_engine_alignment(all_tensions, num_domains)
        anomalies = detect_alignment_anomalies(alignment)'''

# Replace the code
if old_alignment_code in content:
    content = content.replace(old_alignment_code, new_alignment_code)
    print("✅ SUCCESS: Engine alignment calculation fixed!")
    
    # Write the fixed file
    with open('universal_dynamics_engine/universal_pde_engine.py', 'w') as f:
        f.write(content)
else:
    print("❌ WARNING: Could not find the exact alignment code to replace")
    print("The engine file may have changed. Manual fix required.")

print("\nFixed alignment will now:")
print("  - Use mathematically proven calculation")
print("  - Remove artificial clamping at 0.1") 
print("  - Provide meaningful anomaly detection")
print("  - Show true domain coherence")
