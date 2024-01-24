from pyariadne import dp, MultivariatePolynomial, FloatDPBounds, FloatDP, FloatDPExactBox, exact, cos, cast_exact

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction

x = MultivariatePolynomial[FloatDPBounds].coordinates(2, dp)


# Three-hump camel function
f = PolynomialFunction(n_variables=2, f=12*x[0]**2-cast_exact(6+3/10)*x[0]**4+x[0]**6 +6*x[1]*(x[1]-x[0]))
# FloatDP issue with function

# Levy No. 1.
# f = PolynomialFunction(n_variables=1, f=x[0]**6 -15*x[0]**4 +27*x[0]**2 + 250)
# Correct, however, there are two equal global minima --> only returning 1

# Beale function = Schwefel No. 2.1 = More No. 5.
# f = PolynomialFunction(n_variables=2, f=(cast_exact(1.5)-x[0]+x[0]*x[1])**2 +(cast_exact(2.25) -x[0] +x[0]*x[1]**2)**2 + (cast_exact(2.625) -x[0] + x[0]*x[1]**3)**2)
# Incorrect, Finds nothing

# Schwefel No. 3.1
# SUM_{i=1}^{3} {[(x_1-x_i^2)^2 + (x_i-1)^2]}
# f = PolynomialFunction(n_variables=3, f=(x[0]-x[0]**2)**2 + (x[0]-1)**2 + (x[0]-x[1]**2)**2 + (x[1]-1)**2 + (x[0]-x[2]**2)**2 + (x[2]-1)**2)
#Memory issue? "MemoryError: std::bad_alloc"

# Booth problem = Schwefel No. 2.5
# f = PolynomialFunction(n_variables=2, f=(x[0]+2*x[1]-7)**2+(2*x[0]+x[1]-5)**2)
# Does not return the correct result. Min should be at (1,3) and reports around (3.17, 3.55)


opt = PolynomialOptimiser()

minima = opt.minimise_all(f=f, D=d)
# minima = opt.minimise_all(f=f)
print('Minima:', minima)

x_global_minimum = opt._compute_global_minimum(f=f, minima=minima) #private function
# x_global_minimum = opt.minimise(f=f, D=d)
#x_global_minimum = opt.minimise(f=f)
fx_global_minimum = f(x_global_minimum)
print(f'Global minimum x = {x_global_minimum} with f(x) = {fx_global_minimum}')
