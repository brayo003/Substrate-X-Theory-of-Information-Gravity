import re
import pandas as pd

data = []
current_qubit = None
t1 = t2 = None

with open('Data_analysis/backend_info/ibmq_toronto.txt', 'r') as f:
    for line in f:
        # Look for qubit number
        qubit_match = re.search(r"'qubits': \[(\d+)\]", line)
        if qubit_match:
            current_qubit = int(qubit_match.group(1))
            t1 = t2 = None
            continue
        
        # Look for T1
        t1_match = re.search(r"'name': 'T1', 'unit': '[^']*', 'value': ([\d.eE+-]+)", line)
        if t1_match and current_qubit is not None:
            t1 = float(t1_match.group(1))
        
        # Look for T2
        t2_match = re.search(r"'name': 'T2', 'unit': '[^']*', 'value': ([\d.eE+-]+)", line)
        if t2_match and current_qubit is not None:
            t2 = float(t2_match.group(1))
        
        # If we have both T1 and T2 for the current qubit, save them
        if current_qubit is not None and t1 is not None and t2 is not None:
            data.append({'qubit': current_qubit, 'T1_us': t1, 'T2_us': t2})
            # Reset for next qubit (optional – but we can keep them)
            current_qubit = None
            t1 = t2 = None

df = pd.DataFrame(data)
print(f"Extracted {len(df)} qubits")
print(df.head(10))
df.to_csv('ibmq_toronto_t1t2.csv', index=False)
print("Saved to ibmq_toronto_t1t2.csv")
