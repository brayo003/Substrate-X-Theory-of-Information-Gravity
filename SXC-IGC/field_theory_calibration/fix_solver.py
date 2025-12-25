# Script to fix the CompleteSystemSolver class
import re

with open('complete_system_solver.py', 'r') as f:
    content = f.read()

# Fix the class definition to accept dim parameter
old_init = '''class CompleteSystemSolver(SubstrateXSolver):
    def __init__(self, grid_size=32, domain_size=1e21, alpha=1e-5, beta=1.0, 
                 gamma=1e6, chi=1.0, tau=1.0):
        super().__init__(grid_size, domain_size, alpha, beta, gamma, chi, tau)'''

new_init = '''class CompleteSystemSolver(SubstrateXSolver):
    def __init__(self, grid_size=32, domain_size=1e21, alpha=1e-5, beta=1.0, 
                 gamma=1e6, chi=1.0, tau=1.0, dim=2):
        super().__init__(dim, grid_size, domain_size, alpha, beta, gamma, chi, tau)'''

content = content.replace(old_init, new_init)

with open('complete_system_solver.py', 'w') as f:
    f.write(content)

print("Fixed CompleteSystemSolver class")
