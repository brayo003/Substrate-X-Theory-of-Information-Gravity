import json
import pandas as pd
import ast

# Load the file (it's Python dict syntax, not pure JSON)
with open('Data_analysis/backend_info/ibmq_toronto.txt', 'r') as f:
    content = f.read()

# Convert to Python object using ast.literal_eval (safe)
data = ast.literal_eval(content)

# Extract qubit data
qubit_data = []
for item in data['qubits']:
    qubit_idx = item['qubits'][0]  # Single qubit
    t1 = None
    t2 = None
    freq = None
    readout_error = None
    sx_error = None
    
    for param in item['parameters']:
        if param['name'] == 'T1':
            t1 = param['value']
        elif param['name'] == 'T2':
            t2 = param['value']
        elif param['name'] == 'freq':
            freq = param['value']
        elif param['name'] == 'readout_error':
            readout_error = param['value']
    
    qubit_data.append({
        'qubit': qubit_idx,
        'T1_us': t1,
        'T2_us': t2,
        'freq_Hz': freq,
        'readout_error': readout_error
    })

# Extract single-qubit gate errors (sx gates)
gate_errors = []
for item in data['gates']:
    if item['gate'] == 'sx' and len(item['qubits']) == 1:
        qubit = item['qubits'][0]
        for param in item['parameters']:
            if param['name'] == 'gate_error':
                gate_errors.append({
                    'qubit': qubit,
                    'sx_error': param['value']
                })

# Convert to DataFrames
qubit_df = pd.DataFrame(qubit_data)
gate_df = pd.DataFrame(gate_errors)

# Merge
final_df = pd.merge(qubit_df, gate_df, on='qubit', how='left')

print("=== PARSED IBM TORONTO DATA ===")
print(final_df.head(10))
print(f"\nTotal qubits: {len(final_df)}")

# Save
final_df.to_csv('ibmq_toronto_parsed.csv', index=False)
print("\nSaved to ibmq_toronto_parsed.csv")
