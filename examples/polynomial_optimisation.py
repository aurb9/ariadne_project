from pyariadne import FloatDPExactBox, FloatDP, dp, evaluate, FloatDPApproximation

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction


solver = PolynomialOptimiser()

INF = FloatDP.inf(dp)

CASE_1 = False
CASE_2 = True

## CASE 1:
if CASE_1:
## f(x) = x^2 + 2x
## f'(x) = 2x + 2 = 0 --> x_star = -1
    f = PolynomialFunction(n_variables=1, f="[x[0]**2+2*x[0]]")
    domain1 = FloatDPExactBox([(-INF, "-1")])
    opt1 = solver.minimise(f=f, D=domain1)
    print(opt1)

    domain2 = FloatDPExactBox([(-1, 1)])
    # converting this problem actually returns [-1, 1]
    opt2 = solver.minimise(f=f, D=domain2, convert_problem=False)
    print(opt2)

    domain3 = FloatDPExactBox([(1, INF)])
    opt3 = solver.minimise(f=f, D=domain3)
    print(opt3)
# print('p:', f)
# print('D:', domain)


# CASE 2:
if CASE_2:
    # TODO: add checking and selection between opt1 and opt2
    f = PolynomialFunction(n_variables=1, f="[2*x[0]**2-6*x[0]+5]")
    f = PolynomialFunction(n_variables=1, f="[2*x[0]**2-6*x[0]+5]")
    domain1 = FloatDPExactBox([(-INF, "-1")])
    opt1 = solver.minimise(f=f, D=domain1)
    print(opt1)

    domain2 = FloatDPExactBox([(-1, 1)])
    # converting this problem actually returns [-1, 1]
    opt2 = solver.minimise(f=f, D=domain2, convert_problem=False)
    print(opt2)

    domain3 = FloatDPExactBox([(1, INF)])
    opt3 = solver.minimise(f=f, D=domain3)
    print(opt3)
