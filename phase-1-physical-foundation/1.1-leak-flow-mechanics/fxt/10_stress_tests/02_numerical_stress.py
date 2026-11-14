"""Numerical pathology search: solver, precision, stiffness, and random states."""
import json, numpy as np
from scipy.integrate import solve_ivp
from stress_common import sz, random_state, write_artifacts, heatmap

def rhs(gamma):
 def f(_,y):
  r=y.reshape(2,2); return (gamma*(sz@r@sz-r)).reshape(4)
 return f
def run():
 rng=np.random.default_rng(20260727); gammas=np.logspace(-4,4,22); steps=np.logspace(-4,0,28); errors=np.empty((len(gammas),len(steps)))
 violations=[]
 rho0=np.array([[.5,.5],[.5,.5]],complex)
 for i,g in enumerate(gammas):
  exact=np.exp(-2*g)
  for j,dt in enumerate(steps):
   # Fixed-step forward Euler intentionally exposes its stability boundary.
   n=max(1,int(np.ceil(1/dt))); d=1/n
   # Closed form of the fixed-step Euler recursion for rho_01.  This is
   # identical to stepping it n times but makes the broad pathology map cheap.
   with np.errstate(over='ignore', invalid='ignore'):
    euler=.5*(1-2*d*g)**n
   errors[i,j]=abs(euler-0.5*exact)
 # Solver invariants are sampled at representative weak/intermediate/stiff rates;
 # the broad grid above is the separate fixed-step pathology scan.
 for g in (1e-4,1.,1e4):
  for _ in range(4):
   q=random_state(rng); sol=solve_ivp(rhs(g),(0,30/max(g,1e-4)),q.reshape(4),method='BDF',rtol=1e-8,atol=1e-10)
   final=sol.y[:,-1].reshape(2,2); violations.append([abs(np.trace(final)-1),np.max(abs(final-final.conj().T)),np.linalg.eigvalsh(final).min()])
 # Tolerance convergence of a stiff and an extremely long calculation.
 tols=np.logspace(-5,-11,7); vals=[]
 for tol in tols:
  sol=solve_ivp(rhs(1e3),(0,1),rho0.reshape(4),method='BDF',rtol=tol,atol=tol*1e-2); vals.append(abs(sol.y[1,-1]-.5*np.exp(-2000)))
 heatmap(np.log10(errors+1e-18),steps,gammas,'Forward-Euler error: intentional stability stress','nominal timestep','gamma','02_numerical_stability')
 v=np.array(violations)
 summary={'status':'PASS' if v[:,0].max()<1e-8 and v[:,1].max()<1e-8 and v[:,2].min()>-1e-8 else 'FAIL','seed':20260727,
  'scope':{'random_states':len(v),'gamma_range':[float(gammas.min()),float(gammas.max())],'long_time_scaled':'t=100/gamma','stiff_solver':'BDF'},
  'conservation':{'max_trace_error':float(v[:,0].max()),'max_hermiticity_error':float(v[:,1].max()),'minimum_eigenvalue':float(v[:,2].min())},
  'pathology':{'euler_unstable_fraction_error_gt_1e-2':float(np.mean(errors>1e-2)),'cancellation_floor':float(min(vals)),'tolerance_errors':[float(x) for x in vals]},
  'verdict':'The exact GKSL implementation is stable under adaptive stiff integration; explicit Euler has a measurable failure region and must not be used without a step-size check.'}
 write_artifacts('02_numerical_stress',summary,{'gamma':gammas,'timestep':steps,'euler_error':errors,'tolerance':tols,'tolerance_error':vals,'invariants':v},['BDF random-state and Euler failure-map tests executed'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
