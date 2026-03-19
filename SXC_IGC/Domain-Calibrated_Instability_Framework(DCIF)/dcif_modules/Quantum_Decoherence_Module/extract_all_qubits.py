import re
import pandas as pd

qubit_data = {}
current_qubit = None

with open('Data_analysis/backend_info/ibmq_toronto.txt', 'r') as f:
    for line in f:
        # Detect new qubit block
        qubit_match = re.search(r"'qubits': \[(\d+)\]", line)
        if qubit_match:
            current_qubit = int(qubit_match.group(1))
            if current_qubit not in qubit_data:
                qubit_data[current_qubit] = {}
            continue
        
        if current_qubit is None:
            continue
        
        # Look for T1
        t1_match = re.search(r"'name': 'T1', 'unit': '[^']*', 'value': ([\d.eE+-]+)", line)
        if t1_match:
            qubit_data[current_qubit]['T1_us'] = float(t1_match.group(1))
        
        # Look for T2
        t2_match = re.search(r"'name': 'T2', 'unit': '[^']*', 'value': ([\d.eE+-]+)", line)
        if t2_match:
            qubit_data[current_qubit]['T2_us'] = float(t2_match.group(1))
        
        # Look for readout error (optional, but useful)
        ro_match = re.search(r"'name': 'readout_error', 'unit': '[^']*', 'value': ([\d.eE+-]+)", line)
        if ro_match:
            qubit_data[current_qubit]['readout_error'] = float(ro_match.group(1))

# Convert to DataFrame
records = []
for q, vals in qubit_data.items():
    if 'T1_us' in vals and 'T2_us' in vals:
        records.append({
            'qubit': q,
            'T1_us': vals['T1_us'],
            'T2_us': vals['T2_us'],
            'readout_error': vals.get('readout_error', None)
        })

df = pd.DataFrame(records).sort_values('qubit')
print(f"Extracted {len(df)} qubits")
print(df.head(10))
df.to_csv('ibmq_toronto_all.csv', index=False)
print("Saved to ibmq_toronto_all.csv")
