"""Full parameter-space benchmark against standard Lindblad alternatives."""
import json,numpy as np
from stress_common import sx,sy,sz,sm,evolve_gksl,write_artifacts,heatmap
def run():
 rates=np.logspace(-3,1,55); times=np.linspace(0,8,160); rho0=np.array([[.5,.5],[.5,.5]],complex); errors={}; maps={}
 models={'amplitude_damping':lambda q:[(q,sm)],'bit_flip':lambda q:[(q,sx)],'depolarizing':lambda q:[(q/3,sx),(q/3,sy),(q/3,sz)]}
 ref=np.array([abs(evolve_gksl(times,rho0,np.zeros((2,2)),[(q,sz)])[:,0,1]) for q in rates])
 for name,maker in models.items():
  alt=np.array([abs(evolve_gksl(times,rho0,np.zeros((2,2)),maker(q))[:,0,1]) for q in rates]); maps[name]=abs(alt-ref); errors[name]=float(maps[name].max())
  heatmap(maps[name],times,rates,'|coherence difference|: '+name,'time','channel rate','06_'+name+'_difference')
 summary={'status':'PARTIAL','grid':{'rate_range':rates[[0,-1]].tolist(),'time_range':times[[0,-1]].tolist(),'points':int(rates.size*times.size)},'max_coherence_differences':errors,
  'coincidence':'A z dephasing Lindblad channel is exactly the repository effective equation; therefore agreement with that channel is not independent evidence for the derivation.',
  'experimental_measurability':'Not determined: no experimental noise floor, sample size, or apparatus model is frozen in the repository. Difference maps are numerical separations, not detection claims.',
  'verdict':'Standard non-z channels diverge over much of the grid, but calibrated Pauli mixtures can mimic an envelope. Benchmarking establishes model non-uniqueness for coherence-only observables.'}
 write_artifacts('06_lindblad_benchmark',summary,{'rates':rates,'times':times,'reference':ref,**{k:v for k,v in maps.items()}},['multi-channel parameter maps executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
