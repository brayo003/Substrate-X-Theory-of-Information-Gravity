import json
import pandas as pd
import ast
import datetime

# Custom parser for datetime objects
def parse_ibm_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Replace datetime objects with strings
    import re
    content = re.sub(r'datetime\.datetime\([^)]+\)', '"TIMESTAMP"', content)
    content = re.sub(r'tzinfo=tzlocal\(\)', '"UTC"', content)
    
    # Now try to parse
    try:
        data = ast.literal_eval(content)
    except:
        # If still failing, try eval (dangerous but sometimes needed)
        data = eval(content)
    
    return data

print("Loading IBM Toronto data...")
data = parse_ibm_file('Data_analysis/backend_info/ibmq_toronto.txt')

# Extract qubit data
qubit_records = []
for item in data['qubits']:
    qubit = item['qubits'][0]
    record = {'qubit': qubit}
    
    for param in item['parameters']:
        if param['name'] == 'T1':
            record['T1_us'] = param['value']
        elif param['name'] == 'T2':
            record['T2_us'] = param['value']
        elif param['name'] == 'freq':
            record['freq_Hz'] = param['value']
        elif param['name'] == 'readout_error':
            record['readout_error'] = param['value']
        elif param['name'] == 'gate_error' and 'sx' in item.get('name', ''):
            record['sx_error'] = param['value']
    
    qubit_records.append(record)

df = pd.DataFrame(qubit_records)
print(f"\nParsed {len(df)} qubits")
print(df.head(10))

# Save
df.to_csv('ibmq_toronto_parsed.csv', index=False)
print("\nSaved to ibmq_toronto_parsed.csv")

# Show available columns
print("\nColumns:", df.columns.tolist())
