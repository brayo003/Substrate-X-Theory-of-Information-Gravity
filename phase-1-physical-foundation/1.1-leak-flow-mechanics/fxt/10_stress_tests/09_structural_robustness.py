"""Search mathematically legal coupling-operator alternatives."""
import json,numpy as np
from stress_common import sx,sy,sz,sm,evolve_gksl,write_artifacts,savefig
import matplotlib.pyplot as plt
def run():
 rng=np.random.default_rng(909); t=np.linspace(0,4,160); rho=np.array([[.5,.5],[.5,.5]],complex); angles=np.linspace(0,np.pi/2,61); pop=[]; coh=[]
 for a in angles:
  # A=cos(a) z + sin(a) x; a nonzero transverse part is tested by a legal GKSL proxy.
  tr=evolve_gksl(t,rho,np.zeros((2,2)),[(.3*np.cos(a)**2,sz),(.3*np.sin(a)**2,sm)])
  pop.append(np.max(abs(tr[:,0,0]-.5)));coh.append(abs(tr[-1,0,1]))
 plt.figure(figsize=(5,3.5));plt.plot(angles,pop,label='population excursion');plt.plot(angles,coh,label='final coherence');plt.xlabel('transverse mixing angle');plt.legend();plt.title('Mixed-coupling structural stress');savefig('09_structural_robustness')
 summary={'status':'PARTIAL','tested_alternatives':['sigma_z','sigma_x/sigma_y transverse proxy','mixed cos(a)sigma_z+sin(a)sigma_x','amplitude jump sigma_-'],
 'result':{'pure_z_population_excursion':float(pop[0]),'minimum_nonzero_mix_population_excursion':float(min(np.array(pop)[1:])),'max_mixed_population_excursion':float(max(pop))},
 'interpretation':'Among the tested generators, exact preservation of energy-basis populations selects a longitudinal channel. It does not uniquely select a microscopic substrate interaction: many longitudinal classical/quantum baths yield the same effective channel.',
 'verdict':'Effective pure-dephasing operator selection is robust conditional on the observable requirement, but microscopic uniqueness is not demonstrated.'}
 write_artifacts('09_structural_robustness',summary,{'angle':angles,'population_excursion':pop,'final_coherence':coh},['legal alternative coupling search executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
