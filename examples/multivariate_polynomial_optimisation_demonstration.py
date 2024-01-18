from pyariadne import dp, MultivariatePolynomial, FloatDPBounds

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction

x = MultivariatePolynomial[FloatDPBounds].coordinates(2, dp)

# f = PolynomialFunction(n_variables=2, f=(1-x[0])**2+100*(x[1]-x[0]**2)**2)  # Min should be at (1, 1)
f = PolynomialFunction(n_variables=2, f=x[0]**2+x[1]**2)  # (0, 0)
opt = PolynomialOptimiser()

critical_points = opt.minimise_all(f=f)
print('Critical_points', critical_points)

x_global, fx_global = opt._compute_global_optima(f, critical_points)
print(f'Global minimum x = {x_global} with f(x) = {fx_global}')
