"""Assumption ablation: finite-memory counterexample to the Markov reduction."""
import json,numpy as np
from stress_common import finite_memory_envelope,write_artifacts,heatmap
def run():
 x=np.logspace(-4,2,80) # tau Gamma
 u=np.linspace(0,8,120) # Gamma t
 E=np.empty((len(x),len(u)))
 for i,q in enumerate(x): E[i]=abs(finite_memory_envelope(u,1,q)-np.exp(-u))
 heatmap(np.log10(E+1e-14),u,x,'Finite-memory vs Markov envelope','Gamma t','tau_B Gamma','07_markov_ablation')
 ablations={'Born':'No computation can validate a factorized system-bath state from the reduced equation; weak coupling is indispensable to the stated derivation.',
 'Markov':'Finite correlation produces a nonexponential initial slip; maximum mismatch grows with tau_B Gamma.',
 'Secular':'For longitudinal sigma_z coupling [H_S,sigma_z]=0, no +/-2 omega_q transverse terms occur; secular removal does not alter this pure-dephasing algebra, but it is relevant to mixed/transverse alternatives.',
 'Stationary bath':'Without time-translation-invariant C_JJ, the integral used to define a constant rate is not justified.',
 'single_exponential_correlation':'The integral rate can remain defined, but the finite-time envelope need not be the single exponential used by the Markov reduction.'}
 summary={'status':'PARTIAL','assumption_ablation':ablations,'markov_counterexample':{'metric':'max_t |finite-memory envelope - exp(-Gamma t)|','at_tauGamma_0_01':float(E[np.argmin(abs(x-.01))].max()),'at_tauGamma_1':float(E[np.argmin(abs(x-1))].max()),'at_tauGamma_10':float(E[np.argmin(abs(x-10))].max())},'verdict':'The quadratic Markov rate is not established outside its small tau_B Gamma region; this is a derivational limitation, not a numerical failure.'}
 write_artifacts('07_derivation_stress',summary,{'tau_gamma':x,'gamma_t':u,'envelope_error':E},['one-at-a-time assumption ablation executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
