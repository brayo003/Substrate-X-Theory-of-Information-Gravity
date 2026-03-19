import re
import pandas as pd

with open('Data_analysis/backend_info/ibmq_toronto.txt', 'r') as f:
    content = f.read()

# Regex to find qubit number and the following T1 and T2 values (handles line breaks)
pattern = r"'qubits': \[(\d+)\].*?'T1'.*?'value': ([\d.eE+-]+).*?'T2'.*?'value': ([\d.eE+-]+)"
matches = re.findall(pattern, content, re.DOTALL)

data = []
for q, t1, t2 in matches:
    data.append({
        'qubit': int(q),
        'T1_us': float(t1),
        'T2_us': float(t2)
    })

df = pd.DataFrame(data)
print(f"Extracted {len(df)} qubits")
print(df.head(10))
df.to_csv('ibmq_toronto_t1t2.csv', index=False)
print("Saved to ibmq_toronto_t1t2.csv")
