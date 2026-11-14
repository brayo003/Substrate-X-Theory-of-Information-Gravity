import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load the IBMQ Toronto data
# (Copy-paste the data from your file or load directly)
data_text = """
Qubit 0: T1=7.454831472920902e-05, T2=5.0828874708691155e-05, freq=5.224961924528425
Qubit 1: T1=9.869954629989627e-05, T2=0.00016050957456666769, freq=5.00346206485203
Qubit 2: T1=0.00010751065321450604, T2=0.00015801175048698557, freq=5.143794434139562
Qubit 3: T1=9.55225853454598e-05, T2=0.00014526970922268515, freq=5.209638183181166
Qubit 4: T1=8.184036746319997e-05, T2=0.00013010724417479444, freq=5.087700952423628
Qubit 5: T1=6.240292204878482e-05, T2=7.77468934869886e-05, freq=5.167262816407263
Qubit 6: T1=5.679380424778603e-05, T2=5.380655099562861e-05, freq=5.151658898685126
Qubit 7: T1=9.81700628671721e-05, T2=0.00011476308945481127, freq=4.915430796539375
Qubit 8: T1=0.00011447405698780169, T2=9.904161539478106e-05, freq=5.03335269551928
Qubit 9: T1=0.00011251043845322021, T2=0.0001404608919625233, freq=5.082176878905189
Qubit 10: T1=0.0001376107324747894, T2=0.00019245898616796362, freq=5.097827978552644
Qubit 11: T1=0.00011081594566397705, T2=0.00014174834558365428, freq=5.116582120241518
Qubit 12: T1=0.00012778361586889543, T2=0.00016815504271637394, freq=4.927751343588881
Qubit 13: T1=0.00013313574503801676, T2=0.0002003881743743491, freq=5.127657601813056
Qubit 14: T1=5.22542992511683e-05, T2=9.072103198776557e-05, freq=5.017289218619044
Qubit 15: T1=9.295140869126164e-05, T2=5.2727771744931393e-05, freq=5.091636867440041
Qubit 16: T1=7.881049944004595e-05, T2=0.00011788391147473943, freq=4.943171457911177
Qubit 17: T1=7.222755446011417e-05, T2=7.77589784308235e-05, freq=5.157798324861983
Qubit 18: T1=0.0001300398370927949, T2=0.00019480198278757556, freq=5.059726081642532
Qubit 19: T1=0.00012259462735571923, T2=0.000123013826448126, freq=5.069445332220715
Qubit 20: T1=0.00016422821234194344, T2=9.914262851831638e-05, freq=4.916064114242551
Qubit 21: T1=7.197934645088046e-05, T2=5.1375911768724474e-05, freq=5.144737861334316
Qubit 22: T1=0.00011400139205741425, T2=8.69717166457178e-05, freq=5.120620048303412
Qubit 23: T1=0.00011724988088081546, T2=4.4792035920235544e-05, freq=5.099400104285206
Qubit 24: T1=0.00012018210887296258, T2=0.0001658082620145725, freq=4.96336200786154
Qubit 25: T1=8.368379767143988e-05, T2=0.00012977653469397859, freq=5.064632902466971
Qubit 26: T1=7.720479486225803e-05, T2=9.062598814722715e-05, freq=5.21572996990376
"""

# Parse the data into a DataFrame
qubits = []
for line in data_text.strip().split('\n'):
    if 'Qubit' in line:
        parts = line.split(',')
        qubit_num = int(parts[0].split()[1].replace(':', ''))
        t1 = float(parts[0].split('=')[1])
        t2 = float(parts[1].split('=')[1])
        freq = float(parts[2].split('=')[1])
        qubits.append({'qubit': qubit_num, 'T1_us': t1, 'T2_us': t2, 'freq_GHz': freq})

df = pd.DataFrame(qubits)

print("=== IBMQ TORONTO DATA LOADED ===")
print(f"Total qubits: {len(df)}")
print(df.head())

# Map to V12 parameters
measurement_time = 50e-6  # 50 microseconds

df['E'] = 1 - np.exp(-measurement_time / df['T1_us'])
df['F'] = np.exp(-measurement_time / df['T2_us'])

print("\n=== V12 MAPPED PARAMETERS ===")
print(df[['qubit', 'E', 'F']].head(10))

# Calibrate β and γ to match quantum behavior
# We want T = βE - γF to be between 0 and 1
# For a "good" qubit, T should be low (E small, F large)

from scipy.optimize import curve_fit

def v12_model(X, beta, gamma):
    E, F = X
    T = beta * E - gamma * F
    return np.clip(T, 0, 1)

# Use qubit 0 as reference (typical good qubit)
# We want T ≈ 0.3 for a moderately good qubit
target_T = 0.3

# Solve for beta/gamma ratio
# βE - γF = 0.3
# For qubit 0: E=0.49, F=0.62
# β*0.49 - γ*0.62 = 0.3

# One equation, two unknowns. We need a constraint.
# From quantum theory, β/γ ≈ 24 from your earlier calibration
ratio = 24.0
beta = target_T / (df.loc[0, 'E'] - (1/ratio) * df.loc[0, 'F'])
gamma = beta / ratio

print(f"\n=== CALIBRATED PARAMETERS ===")
print(f"β = {beta:.4f}")
print(f"γ = {gamma:.4f}")
print(f"β/γ = {beta/gamma:.1f}")

# Apply to all qubits
df['T'] = beta * df['E'] - gamma * df['F']
df['T'] = df['T'].clip(0, 1)

print("\n=== QUANTUM TENSION BY QUBIT ===")
print(df[['qubit', 'T1_us', 'T2_us', 'E', 'F', 'T']].sort_values('T').head(10))

# Identify best and worst qubits
print("\n=== BEST QUBITS (Lowest T) ===")
print(df.nsmallest(5, 'T')[['qubit', 'T1_us', 'T2_us', 'T']])

print("\n=== WORST QUBITS (Highest T) ===")
print(df.nlargest(5, 'T')[['qubit', 'T1_us', 'T2_us', 'T']])

# Save to file
df.to_csv('quantum_v12_calibration.csv', index=False)
print("\nSaved to quantum_v12_calibration.csv")

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(df['T1_us']*1e6, df['T2_us']*1e6, c=df['T'], cmap='viridis', s=100)
plt.colorbar(label='V12 Tension (T)')
plt.xlabel('T1 (μs)')
plt.ylabel('T2 (μs)')
plt.title('IBMQ Toronto: V12 Tension by Qubit')
plt.grid(True, alpha=0.3)
plt.savefig('quantum_v12_tension.png')
print("Plot saved to quantum_v12_tension.png")
