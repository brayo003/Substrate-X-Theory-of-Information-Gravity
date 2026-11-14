"""Fisher, profile, and posterior-grid identifiability analysis for frozen law."""
import json,numpy as np
from stress_common import write_artifacts,savefig
import matplotlib.pyplot as plt
def run():
 rng=np.random.default_rng(13); omega=np.linspace(.3,2,16); k=.12; sig=.015; y=k*omega**2+rng.normal(0,sig,len(omega))
 # parameterization theta=(log g, log s0), fixed r_q,tau,hbar: only sum is visible.
 g=np.logspace(-2,1,160); s=np.logspace(-2,1,160)
 # profile grid uses vectorized residual directly
 chi=np.array([[np.sum(((8*gv**2*sv**2*omega**2/3-y)/sig)**2) for gv in g] for sv in s])
 J=np.column_stack((2*k*omega**2,2*k*omega**2))/sig; F=J.T@J; ev=np.linalg.eigvalsh(F); cond=float(np.inf if ev[0]<1e-12 else ev[-1]/ev[0])
 post=np.exp(-.5*(chi-chi.min())); post/=post.sum()
 plt.figure(figsize=(5.4,4)); plt.contourf(g,s,-.5*(chi-chi.min()),levels=30); plt.xscale('log');plt.yscale('log');plt.xlabel('g');plt.ylabel('s0');plt.title('Log-likelihood: exact ridge');plt.colorbar(label='relative log likelihood');savefig('04_inverse_problem')
 summary={'status':'PARTIAL','seed':13,'data_model':'synthetic Gamma=k omega^2 with known Gaussian noise','fisher_information':F.tolist(),'eigenvalues':ev.tolist(),'condition_number':cond,
  'structural_identifiability':{'k_rot':True,'g':False,'s0':False,'g_times_s0':True,'reason':'rate contains g^2 s0^2 only'},
  'practical_identifiability':{'posterior_grid_shape':list(post.shape),'credible_ridge_mass_delta_chi2_lt_2_30':float(post[chi-chi.min()<2.30].sum()),'profile_minimum':float(chi.min())},
  'verdict':'A rate-versus-frequency experiment identifies only the composite coefficient. The singular Fisher matrix quantitatively rules out separate recovery of g and s0 without an additional observable or externally fixed parameter.'}
 write_artifacts('04_inverse_problem_stress',summary,{'omega':omega,'observations':y,'g_grid':g,'s0_grid':s,'chi2':chi,'posterior':post,'fisher':F},['Fisher, profile likelihood, and posterior grid executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
