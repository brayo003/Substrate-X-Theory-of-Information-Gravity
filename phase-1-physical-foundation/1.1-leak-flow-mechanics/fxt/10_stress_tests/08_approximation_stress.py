"""Green/yellow/red approximation validity map using stated dimensionless controls."""
import json,numpy as np
from stress_common import rate,write_artifacts,heatmap
def run():
 g=np.logspace(-3,1,100); omega_tau=np.logspace(-3,2,100); z=np.empty((100,100))
 # with tau=s0=rq=hbar=1: Born control g*tau and Markov control tau*Gamma.
 for j,w in enumerate(omega_tau): z[j]=np.maximum(g, np.array([rate(g=a,omega=w) for a in g]))
 colors=np.where(z<.01,2,np.where(z<.1,1,0)); heatmap(colors,g,omega_tau,'Approximation validity: green/yellow/red','Born proxy g tau_B','omega_rot tau_B','08_approximation_map','RdYlGn')
 summary={'status':'PARTIAL','controls':{'Born_proxy':'g tau_B (dimensionless proxy after frozen normalization)','Markov':'tau_B Gamma_phi','secular_note':'for pure sigma_z coupling it is algebraically inactive; no independent numerical threshold supplied by frozen sources'},'thresholds':{'green':'both controls < 0.01','yellow':'max control in [0.01,0.1)','red':'max control >= 0.1'},'fractions':{'green':float(np.mean(colors==2)),'yellow':float(np.mean(colors==1)),'red':float(np.mean(colors==0))},'verdict':'Validity is a region, not a pass/fail property. The red region must not be cited as validation of the Markov-Born derivation.'}
 write_artifacts('08_approximation_stress',summary,{'g_tau':g,'omega_tau':omega_tau,'max_control':z,'validity_code':colors},['approximation map generated from frozen controls'])
 return summary
if __name__=='__main__': print(json.dumps(run(),indent=2))
