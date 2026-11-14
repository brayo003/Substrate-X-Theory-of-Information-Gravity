"""Seeded adversarial parameter search; records counterexample regions."""
import json,numpy as np
from stress_common import finite_memory_envelope,rate,write_artifacts,savefig
import matplotlib.pyplot as plt
def run():
 rng=np.random.default_rng(10010); n=100000
 g=10**rng.uniform(-5,1,n); s=10**rng.uniform(-3,2,n); rq=10**rng.uniform(-3,2,n); tau=10**rng.uniform(-5,2,n); omega=10**rng.uniform(-4,3,n)
 G=rate(g,s,rq,tau,1,omega); control=tau*G; # Outside this, frozen Markov condition fails.
 # adversarial finite-memory mismatch at five decoherence times
 q=np.clip(control,1e-12,1e6); mismatch=np.max(abs(finite_memory_envelope(np.array([.1,1,3,5])[:,None],1,q)-np.exp(-np.array([.1,1,3,5])[:,None])),axis=0)
 kill=(control>=.1)|(mismatch>.01); idx=np.argsort(control)[-10:]
 plt.figure(figsize=(5.2,3.8));plt.scatter(np.log10(control[::40]),np.log10(mismatch[::40]+1e-14),s=2,alpha=.25);plt.axvline(-1,color='r');plt.xlabel('log10(tau Gamma)');plt.ylabel('log10 finite-memory mismatch');plt.title('Adversarial random search');savefig('10_falsification_search')
 summary={'status':'FAIL' if np.any(kill) else 'PASS','seed':10010,'samples':n,'log_uniform_ranges':{'g':[-5,1],'s0':[-3,2],'r_q':[-3,2],'tau':[-5,2],'omega_rot':[-4,3]},
 'falsification_criteria':{'Markov_failure':'tau Gamma >= 0.1','finite_memory_failure':'max envelope mismatch > 0.01'},'results':{'markov_failure_fraction':float(np.mean(control>=.1)),'finite_memory_failure_fraction':float(np.mean(mismatch>.01)),'combined_failure_fraction':float(np.mean(kill)),'worst_tauGamma':float(control[idx[-1]])},
 'verdict':'The unrestricted admissible-positive search readily finds regions violating the frozen Markov condition. This falsifies any universal-domain claim, not the conditional weak-coupling derivation.'}
 write_artifacts('10_falsification_search',summary,{'g':g,'s0':s,'rq':rq,'tau':tau,'omega':omega,'Gamma':G,'tauGamma':control,'mismatch':mismatch,'fail':kill},['100000-point seeded adversarial search executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
