from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction

from pyariadne import FloatDPBounds, dp, FloatDPBoundsVector

# Examples of polynomials of degree 2
# f = PolynomialFunction(n_variables=1, f="[x[0]**2+2*x[0]]")
# f = PolynomialFunction(n_variables=1, f="[2*x[0]**2-6*x[0]+5]")

# Examples with polynomials of degrees 4 and 5
# 2x^4-5x^3+2x
f = PolynomialFunction(n_variables=1, f="[2*x[0]**4-5*x[0]**3+2*x[0]]")

# x^4-3x^3+2x
# f = PolynomialFunction(n_variables=1, f="[x[0]**4-3*x[0]**3+2*x[0]]")
# 4x^5+2x^4+3x^2+2x
# f = PolynomialFunction(n_variables=1, f="[4*x[0]**5+2*x[0]**4+3*x[0]**2+2*x[0]")
# x^5 -5x^4 +3x^2+2x
# f = PolynomialFunction(n_variables=1, f="[x[0]**5-5*x[0]**4+3*x[0]**2+2*x[0]")
# x^5-3x^4+3x^2+2
# f = PolynomialFunction(n_variables=1, f="[x[0]**5-3*x[0]**4+3*x[0]**2+2")
# x^5+5x^4-3x^2+2x
# f = PolynomialFunction(n_variables=1, f="[x[0]**5+5*x[0]**4-3*x[0]**2+2*x[0]")
# x^5+3x^4-3x^2+2x
# f = PolynomialFunction(n_variables=1, f="[x[0]**5+3*x[0]**4-3*x[0]**2+2*x[0]")
# x^5-5x^4+3x^2
# f = PolynomialFunction(n_variables=1, f="[x[0]**5-5*x[0]**4+3*x[0]**2") #solver exceptions, works correctly

# f = PolynomialFunction(n_variables=2, f="2*x[0]**2+x[1]**2")

solver = PolynomialOptimiser()

#TODO: check why x = 0.59 is missing, probably due to early comparison
#print([f(FloatDPBoundsVector([x], dp)) for x in all_solutions])
critical_points = solver.minimise_all(f=f)
print('Critical_points', critical_points)

x_global, fx_global = solver.compute_global_optima(f, critical_points)
print(f'Global minimum x = {x_global} with f(x) = {fx_global}')
