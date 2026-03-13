import sympy
from sympy import *

from sympy import symbols, simplify, solve

x = symbols('x')
R_sigma =  symbols('R_sigma') 
f = symbols('f')

# define the resolvent equation
equation = R_sigma * f 

# solve for f to get an explicit formula of the function
solution = solve(equation) 

print(solution) 
