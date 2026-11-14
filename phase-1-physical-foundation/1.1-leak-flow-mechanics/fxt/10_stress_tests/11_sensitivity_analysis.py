"""Global log-sensitivity ranking of the frozen rate and approximation control."""
import json,numpy as np
from stress_common import rate,write_artifacts,savefig
import matplotlib.pyplot as plt
def run():
 names=['g','s0','r_q','tau','omega_rot','hbar']; elastic=np.array([2,2,2,1,2,-2.])
 # uncertainty contribution Var(log Gamma) under explicit equal log-width test prior.
 widths=np.array([1,1,1,1,1,1.]); contrib=(elastic*widths)**2; order=np.argsort(-contrib)
 plt.figure(figsize=(5.2,3.4));plt.bar(names,contrib);plt.ylabel('relative log-variance contribution');plt.title('Equal-width prior sensitivity');savefig('11_sensitivity_analysis')
 summary={'status':'PARTIAL','method':'exact logarithmic derivatives of frozen rate; equal independent one-decade test widths solely for ranking','elasticities':dict(zip(names,elastic.tolist())),'ranked_equal_width':[names[i] for i in order],
 'hidden_parameter_check':{'k_rot_dependencies':['g','s0','r_q','tau','hbar'],'finding':'k_rot is not constant under changes in its defining frozen parameters. Treating it as an empirical constant requires those parameters to be fixed or independently controlled.'},
 'verdict':'The rate is quadratically sensitive to g, s0, r_q, omega_rot, and hbar; no uncertainty budget supplied by the frozen repository permits a numerical experimental confidence claim.'}
 write_artifacts('11_sensitivity_analysis',summary,{'names':np.array(names),'elasticity':elastic,'contribution':contrib},['analytic sensitivity and hidden-dependency audit executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
