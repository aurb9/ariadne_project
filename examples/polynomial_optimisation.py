from pyariadne import FloatDPExactBox, FloatDP, dp

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction


solver = PolynomialOptimiser()

# f = PolynomialFunction(n_variables=1, f="[x[0]**2+2*x[0]]")
f = PolynomialFunction(n_variables=1, f="[2*x[0]**2-6*x[0]+5]")
domain = FloatDPExactBox([(0, 3)])

opt = solver.minimise(f=f, D=domain)
print(opt)
