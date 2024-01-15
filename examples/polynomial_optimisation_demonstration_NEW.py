from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction

# Examples of polynomials of degree 2
# f = PolynomialFunction(n_variables=1, f="[x[0]**2+2*x[0]]")
# f = PolynomialFunction(n_variables=1, f="[2*x[0]**2-6*x[0]+5]")

# Examples with polynomials of degrees 4 and 5
# 2x^4-5x^3+2x
#f = PolynomialFunction(n_variables=1, f="[2*x[0]**4-5*x[0]**3+2*x[0]]")

# x^4-3x^3+2x
# f = PolynomialFunction(n_variables=1, f="[x[0]**4-3*x[0]**3+2*x[0]]")
# 4x^5+2x^4+3x^2+2x
# f = PolynomialFunction(n_variables=1, f="[4*x[0]**5+2*x[0]**4+3*x[0]**2+2*x[0]")
# x^5 -5x^4 +3x^2+2x
#f = PolynomialFunction(n_variables=1, f="[x[0]**5-5*x[0]**4+3*x[0]**2+2*x[0]")
# x^5-3x^4+3x^2+2
# f = PolynomialFunction(n_variables=1, f="[x[0]**5-3*x[0]**4+3*x[0]**2+2")
# x^5+5x^4-3x^2+2x
# f = PolynomialFunction(n_variables=1, f="[x[0]**5+5*x[0]**4-3*x[0]**2+2*x[0]")
# x^5+3x^4-3x^2+2x
# f = PolynomialFunction(n_variables=1, f="[x[0]**5+3*x[0]**4-3*x[0]**2+2*x[0]")
# x^5-5x^4+3x^2
f = PolynomialFunction(n_variables=1, f="[x[0]**5-5*x[0]**4+3*x[0]**2") #solver exceptions, works correctly

solver = PolynomialOptimiser()

all_solutions = solver.minise_all(f=f)
print(all_solutions)

x_global, fx_global = solver.final_solution(f, all_solutions)
print(f'Global minimum x = {x_global} with f(x) = {fx_global}')
