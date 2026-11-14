"""Protocol-level consequence search; reports non-predictions explicitly."""
import json,numpy as np
from stress_common import finite_memory_envelope,write_artifacts,savefig
import matplotlib.pyplot as plt
def run():
 t=np.linspace(0,10,400); gamma=.3; ram=np.exp(-gamma*t); echo=np.exp(-gamma*t); cpmg=echo.copy()
 # Frozen Markov Lindblad model has no temperature, pulse-spacing, or qubit-count symbol.
 protocols={'Ramsey':'exp(-Gamma_phi t)','spin_echo':'same Markov pure-dephasing envelope; no refocusing advantage without a non-Markov/static-noise model','CPMG/dynamical_decoupling':'no pulse-spacing dependence follows from a time-local Markov generator','noise_spectroscopy':'only zero-frequency integrated correlation enters the frozen rate','frequency_response':'Gamma_phi=k_rot omega_rot^2','temperature_scaling':'not specified by frozen equations','multi_qubit_scaling':'not specified by frozen equations'}
 w=np.linspace(.05,3,100); r=.08*w*w
 plt.figure(figsize=(5.2,3.5));plt.plot(w,r,label='frozen rate law');plt.xlabel('omega_rot');plt.ylabel('Gamma_phi');plt.title('Only documented frequency consequence');plt.grid(alpha=.3);savefig('05_predictive_sweep')
 summary={'status':'PARTIAL','reference_only_predictions':protocols,'computed':{'frequency_exponent_fit':float(np.polyfit(np.log(w),np.log(r),1)[0]),'ramsey_vs_echo_max_difference':float(max(abs(ram-echo)))},
 'falsifiability':{'direct_test':'fit Gamma_phi versus omega_rot and test exponent 2 plus intercept 0','limitation':'An observed deviation cannot uniquely diagnose the frozen mechanism because standard dephasing models can share the same envelope.'},
 'verdict':'No additional protocol-specific deviation is entailed by the frozen Markov pure-dephasing equations; claiming echo, CPMG, temperature, or multi-qubit novelty would invent evidence.'}
 write_artifacts('05_predictive_stress',summary,{'time':t,'ramsey':ram,'echo':echo,'omega':w,'gamma':r},['protocol consequence search executed; unsupported spaces recorded'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
