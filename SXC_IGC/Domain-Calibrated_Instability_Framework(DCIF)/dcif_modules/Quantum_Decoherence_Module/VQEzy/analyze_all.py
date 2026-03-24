import h5py
import numpy as np
import pandas as pd

class SXCOmegaEngine:
    def __init__(self):
        self.T_sys = 0.0
        self.phase = 'NOMINAL'
        self.gamma = 0.8
        self.beta = 3.5
        self.dt = 0.05
        self.decay_rate = 0.0005
    
    def excitation_flux(self, signal):
        if signal < 45:
            return 1 - np.exp(-signal / 40.0)
        return 0.675 + ((signal - 45.0) / 20.0)
    
    def step(self, signal):
        self.gamma *= (1 - self.decay_rate)
        E = self.excitation_flux(signal)
        gamma_eff = 2.2 if self.phase == 'FIREWALL' else 1.0
        inflow = E * self.beta
        outflow = gamma_eff * self.gamma * self.T_sys
        self.T_sys += (inflow - outflow) * self.dt
        
        if self.T_sys > 1.0:
            self.phase = 'FIREWALL'
        elif self.phase == 'FIREWALL' and self.T_sys < 0.4:
            self.phase = 'NOMINAL'
        
        return self.T_sys, self.phase

files = [
    'qchem/h2_4_qubit.h5',
    'qchem/hehp_4_qubit.h5', 
    'qmanybody/fh_4_qubit.h5',
    'qmanybody/xyz_4_qubit.h5'
]

for file in files:
    print(f'\n=== {file} ===')
    with h5py.File(file, 'r') as f:
        opt_params = f['opt_params']
        keys = sorted(opt_params.keys(), key=lambda x: int(x.split('_')[1]))
        
        param_changes = []
        prev = None
        for key in keys:
            current = opt_params[key][()]
            if prev is not None:
                change = np.mean(np.abs(current - prev))
                param_changes.append(change)
            prev = current
        
        signals = np.array(param_changes) * 100
        
        engine = SXCOmegaEngine()
        results = []
        for sig in signals:
            T, phase = engine.step(sig)
            results.append([T, phase])
        
        df = pd.DataFrame(results, columns=['T_sys', 'phase'])
        print(f'Final T_sys: {df["T_sys"].iloc[-1]:.4f}')
        print(f'FIREWALL proportion: {(df["phase"] == "FIREWALL").mean():.2%}')
