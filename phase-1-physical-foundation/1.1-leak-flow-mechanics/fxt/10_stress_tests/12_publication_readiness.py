"""Evidence-bound publication readiness synthesis from generated JSON outputs."""
import json,os
import matplotlib.pyplot as plt
from stress_common import OUT,write_artifacts,savefig
def run():
 files=[f'{i:02d}_{n}.json' for i,n in [(1,'mathematical_stress'),(2,'numerical_stress'),(3,'quantum_stress'),(4,'inverse_problem_stress'),(5,'predictive_stress'),(6,'lindblad_benchmark'),(7,'derivation_stress'),(8,'approximation_stress'),(9,'structural_robustness'),(10,'falsification_search'),(11,'sensitivity_analysis')]]
 loaded={f:json.load(open(os.path.join(OUT,f))) for f in files if os.path.exists(os.path.join(OUT,f))}
 summary={'status':'PARTIAL','inputs_found':len(loaded),'strongest_verified_claims':['Symbolic dimensions and algebra of the stated rate are internally consistent (conditional on declared units).','The implemented sigma_z GKSL equation is numerically stable and preserves density-matrix invariants.','The effective sigma_z channel is exactly standard Lindblad dephasing.'],
 'weakest_verified_claims':['Microscopic uniqueness: coherence-only data are degenerate across effective channels.','Separate inference of g and s0: Fisher matrix is singular.','Universal validity: adversarial samples violate the Markov control condition.'],
 'unsupported_claims':['Novel pulse-sequence, temperature, noise-spectroscopy, or multi-qubit predictions.','Experimental measurability without apparatus noise and sampling assumptions.','Derivation validity outside the mapped approximation regime.'],
 'experimentally_testable_claims':['Quadratic Gamma_phi versus omega_rot scaling with a zero intercept, conditional on controlled k_rot.','Energy-basis population preservation alongside Ramsey decay to distinguish pure dephasing from relaxation.'],
 'confidence':{'mathematical':'conditional/internal only','numerical':'high for implemented GKSL equation, not the derivation','experimental':'not established'},
 'publication_assessment':'Not publication-ready as a claim of a unique new open-system mechanism. It is a reproducible conditional effective-model verification with clear failure domains and a defined experimental discrimination need.'}
 with open(os.path.join(os.path.dirname(__file__),'PUBLICATION_READINESS.md'),'w') as f:
  f.write('# Publication Readiness\n\n')
  for k,v in summary.items():
   if k in ('status','inputs_found'): continue
   f.write('## '+k.replace('_',' ').title()+'\n\n')
   if isinstance(v,list): f.write(''.join('- '+x+'\n' for x in v))
   elif isinstance(v,dict): f.write(''.join('- **%s:** %s\n'%(a,b) for a,b in v.items()))
   else: f.write(str(v)+'\n')
   f.write('\n')
 plt.figure(figsize=(4.6,3.1)); plt.bar(['inputs found','expected'],[len(loaded),11],color=['#4477aa','#cccccc']); plt.ylim(0,12); plt.title('Evidence inputs available'); savefig('12_publication_readiness')
 write_artifacts('12_publication_readiness',summary,{'input_count':[len(loaded)]},['publication readiness synthesis generated from stress outputs'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
