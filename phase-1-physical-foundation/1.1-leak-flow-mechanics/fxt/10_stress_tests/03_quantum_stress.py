"""Channel-uniqueness stress test against standard and random GKSL dynamics."""
import json, numpy as np
from scipy.optimize import least_squares
from stress_common import sx,sy,sz,sm,I2,evolve_gksl,write_artifacts,heatmap
def run():
 t=np.linspace(0,6,240); rho0=np.array([[.5,.5],[.5,.5]],complex); target=.5*np.exp(-.7*t)
 channels={'pure_z':[(.35,sz)],'amplitude_damping':[(.7,sm)],'bit_flip':[(.35,sx)],'depolarizing':[(.35/3,sx),(.35/3,sy),(.35/3,sz)],'mixed_pauli':[(.1,sx),(.2,sy),(.35,sz)]}
 scores={}; population={}
 for name,jumps in channels.items():
  tr=evolve_gksl(t,rho0,np.zeros((2,2)),jumps); scores[name]=float(np.max(abs(abs(tr[:,0,1])-target))); population[name]=float(np.max(abs(tr[:,0,0]-.5)))
 # Legal random GKSL generators: how often can an unconstrained Pauli mixture mimic the envelope?
 rng=np.random.default_rng(404); samples=600; parms=10**rng.uniform(-4,0,(samples,3)); fits=[]
 for p in parms:
  tr=evolve_gksl(t,rho0,np.zeros((2,2)),list(zip(p,[sx,sy,sz]))); fits.append(np.max(abs(abs(tr[:,0,1])-target)))
 fits=np.array(fits); z=np.empty((50,50)); xx=np.logspace(-4,0,50); yy=np.logspace(-4,0,50)
 for i,a in enumerate(xx):
  for j,b in enumerate(yy): z[j,i]=np.max(abs(np.exp(-2*(a+b)*t)-np.exp(-.7*t)))
 heatmap(np.log10(z+1e-12),xx,yy,'Pauli-channel envelope mismatch (z rate fixed at 0)','x-flip rate','y-flip rate','03_quantum_channel_map')
 summary={'status':'PARTIAL','seed':404,'target':'pure sigma_z GKSL coherence with Gamma_phi=0.7',
  'named_channel_max_envelope_error':scores,'named_channel_population_excursion':population,
  'random_general_pauli_GKSL':{'samples':samples,'best_max_error':float(fits.min()),'fraction_with_error_below_1e-3':float(np.mean(fits<1e-3))},
  'verdict':'The exact pure-dephasing channel is reproduced by z dephasing (and mixtures calibrated to the same transverse decay); Ramsey envelope data alone do not establish a unique microscopic channel. Population-sensitive data reject amplitude damping but not all Pauli alternatives.'}
 write_artifacts('03_quantum_stress',summary,{'t':t,'target':target,'rates':parms,'random_errors':fits},['standard channels and random GKSL search executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
