"""Adversarial algebra/assumption stress test for the frozen rate law."""
import json, numpy as np, sympy as sp
from stress_common import write_artifacts, heatmap, rate

def run():
    g,s,r,tau,h,w=sp.symbols('g s0 r_q tau hbar omega', positive=True)
    gamma=8*g**2*s**2*r**2*tau*w**2/(3*h**2)
    # Every dependency is declared from cited frozen derivations; removal means
    # the stated reduction no longer entails the exponential Lindblad equation.
    dependencies={"quadratic_rate": ["linear coupling", "rotation variance ∝ omega^2", "Born", "Markov", "stationary bath", "single-exponential correlation"],
                  "GKSL_form": ["Born", "Markov", "secular", "stationary bath"],
                  "pure_dephasing": ["longitudinal sigma_z coupling"]}
    limits={"omega_to_0":str(sp.limit(gamma,w,0)), "g_to_0":str(sp.limit(gamma,g,0)),
            "tau_to_0":str(sp.limit(gamma,tau,0)), "hbar_to_0":str(sp.limit(gamma,h,0,dir='+'))}
    # Units M,L,T,I: independently recomputed from DIM-g in the derivation.
    dim={'g':(1,4,-1,-1),'s':(0,-3,0,1),'r':(0,1,0,0),'tau':(0,0,1,0),'h':(1,2,-1,0),'w':(0,0,-1,0)}
    gd=tuple(2*dim['g'][i]+2*dim['s'][i]+2*dim['r'][i]+dim['tau'][i]-2*dim['h'][i]+2*dim['w'][i] for i in range(4))
    # x = tau Gamma is exactly the documented Markov self-consistency metric.
    gs=np.logspace(-3,1,80); wt=np.logspace(-3,1,80); z=np.array([[rate(g=a,tau=1,omega=b) for a in gs] for b in wt])
    heatmap(np.log10(z), gs, wt, 'Markov control parameter: log10(tau Gamma)', 'coupling g (tau=s0=rq=hbar=1)', 'omega_rot', '01_approximation_validity')
    singular=np.isfinite(np.array([float(gamma.subs({g:1,s:1,r:1,tau:1,h:hv,w:1})) for hv in np.logspace(-12,2,100)])).all()
    summary={'status':'PARTIAL','seed':0,'reference_equation':'Gamma_phi=8 g^2 s0^2 r_q^2 tau omega_rot^2/(3 hbar^2)',
      'symbolic':{'log_derivatives':{x:str(sp.simplify(v*sp.diff(gamma,v)/gamma)) for x,v in [('g',g),('s0',s),('r_q',r),('tau',tau),('omega',w),('hbar',h)]},'limits':limits},
      'dimension_check':{'Gamma_dimensions_M_L_T_info':gd,'expected':(0,0,-1,0),'passes':gd==(0,0,-1,0)},
      'assumption_removal':{'dependency_graph':dependencies,'result':'Removing Born, Markov, stationarity, or single-exponential correlation removes the derivational route to the stated time-local quadratic-rate equation; this suite does not claim it survives.'},
      'validity_map':{'metric':'tau*Gamma','green':'<0.01','yellow':'0.01–0.1','red':'>=0.1','grid_red_fraction':float(np.mean(z>=.1))},
      'singularity_search':{'hbar_scan_finite':bool(singular),'analytic_divergence_at_hbar_zero':True},
      'verdict':'Algebra and dimensions pass, but the mathematical formula alone does not establish approximation validity.'}
    write_artifacts('01_mathematical_stress',summary,{'g_grid':gs,'omega_grid':wt,'tau_gamma':z},['symbolic perturbation and dependency audit executed'])
    return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
