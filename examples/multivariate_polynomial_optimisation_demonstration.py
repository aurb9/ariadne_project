from pyariadne import dp, MultivariatePolynomial, FloatDPBounds, FloatDPExactBox

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction

x = MultivariatePolynomial[FloatDPBounds].coordinates(2, dp)


# f = PolynomialFunction(n_variables=2, f=(1-x[0])**2+100*(x[1]-x[0]**2)**2)  # Min (1, 1)
f = PolynomialFunction(n_variables=2, f=(x[0]-2)**2+(x[1]+3)**2)  # min (2,-3) b3, b1
# f = PolynomialFunction(n_variables=2, f=(x[0]-2)**2+x[1]**2)  # min (2,0) b3,b2 (q_0, f'_1)
# f = PolynomialFunction(n_variables=1, f=(x[0]-2)**2) # min 0 b2
# f = PolynomialFunction(n_variables=1, f=x[0]**2) # min 0 b2
# f = PolynomialFunction(n_variables=2, f=x[0]**2+x[1]**2)  # (0, 0)
opt = PolynomialOptimiser()

# d = FloatDPExactBox([(1, 3), (-1, 1)])
x_global_minimum = opt.minimise(f=f)
fx_global_minimum = f(x_global_minimum)
print(f'Global minimum x = {x_global_minimum} with f(x) = {fx_global_minimum}')
