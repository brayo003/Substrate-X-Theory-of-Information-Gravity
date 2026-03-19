import pandas as pd
from qiskit_ibm_runtime import QiskitRuntimeService
import os

try:
    # Initialize service
    service = QiskitRuntimeService()
    # Using 'ibm_brisbane' or 'ibm_kyoto' as they are common 127-qubit backends
    # Replace with "ibm_marrakesh" if you have specific access
    backend = service.backend("ibm_brisbane") 
    
    print(f"Connected to {backend.name}. Extracting DCIF metrics...")
    
    data = []
    props = backend.properties()
    
    for i in range(backend.num_qubits):
        t1 = props.qubit_property(i, 'T1')[0]
        t2 = props.qubit_property(i, 'T2')[0]
        
        # DCIF Mappings:
        # Gamma (Damping) = 1/T2 (rate of information loss)
        # Stability = T2/T1 ratio
        data.append({
            'qubit_id': i,
            'T1_us': t1 * 1e6,
            'T2_us': t2 * 1e6,
            'gamma_decoherence': 1.0 / (t2 + 1e-9), 
            'instability_index': 1.0 - (t2 / (2 * t1)) # Theoretical limit check
        })

    df = pd.DataFrame(data)
    df.to_csv('quantum_hardware_state.csv', index=False)
    print("Success: 'quantum_hardware_state.csv' generated for DCIF analysis.")

except Exception as e:
    print(f"Error: {e}")
    print("Tip: Ensure you have run 'qiskit-ibm-runtime' and saved your API key.")
