from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPExactBox

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.string_parsing_version.polynomial_function import PolynomialFunction

f = PolynomialFunction(n_variables=2, f="-2*x[0]+x[0]**2+100*x[1]**2-200*x[1]*x[0]**2+100*x[0]**4+1")  # Min should be at (1, 1)
opt = PolynomialOptimiser()
opt.minimise(f, D=FloatDPExactBox([(-FloatDP.inf(dp), "-1")]), convert_problem=True)
