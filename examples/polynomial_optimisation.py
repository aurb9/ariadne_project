from pyariadne import FloatDPExactBox, FloatDP, dp

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction


solver = PolynomialOptimiser()

f = PolynomialFunction(n_variables=1, f="[x[0]**2+2*x[0]]")
domain = FloatDPExactBox([(-1, FloatDP.inf(dp))])

opt = solver.minimise(f=f, D=domain)
print(opt)
