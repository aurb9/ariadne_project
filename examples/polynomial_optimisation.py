from pyariadne import FloatDPExactBox, FloatDP, dp, is_nan, ValidatedNumber

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.polynomial_function import PolynomialFunction


def final_solution(all_solutions: list[ValidatedNumber]) -> None:
    verified_solutions = [solution for solution in all_solutions if not is_nan(solution.get(dp).value())]

    if len(verified_solutions) == 0:
        print('ERROR: NO REAL SOLUTION FOUND')
        print('All solutions found:', all_solutions)
    elif len(verified_solutions) == 1:
        verified_global_solution = verified_solutions[0]
    else:
        verified_float_solutions = [sol.get(dp).value() for sol in verified_solutions]
        verified_global_solution = INF

        for float_solution in verified_float_solutions:
            verified_global_solution = min(verified_global_solution, float_solution)

    return verified_global_solution


solver = PolynomialOptimiser()

INF = FloatDP.inf(dp)

# converting DOMAIN_2 problem actually returns [-1, 1],
# so do not convert for computational reasons
DOMAIN_1 = FloatDPExactBox([(-INF, "-1")])
DOMAIN_2 = FloatDPExactBox([(-1, 1)])
DOMAIN_3 = FloatDPExactBox([(1, INF)])

CASE_1 = False #opt in DOMAIN_1
CASE_2 = True #opt in DOMAIN_3
CASE_3 = False #opt in DOMAIN_2 #THIS CASE DOES NOT WORK, see below
CASE_4 = False #opt in DOMAIN_2

if CASE_1:
    ## f(x) = x^2 + 2x
    ## f'(x) = 2x + 2 = 0 --> x_star = -1
    f = PolynomialFunction(n_variables=1, f="[x[0]**2+2*x[0]]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    verified_global_solution = final_solution(all_solutions)
    print('Verified global solution:', verified_global_solution)

elif CASE_2:
    ## f(x) = 2x^2 -6x + 5
    ## f'(x) = 4x - 6 = 0 --> x_star = 3/2
    f = PolynomialFunction(n_variables=1, f="[2*x[0]**2-6*x[0]+5]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    verified_global_solution = final_solution(all_solutions)
    print('Verified global solution:', verified_global_solution)

elif CASE_3: #THIS EXAMPLE DOES NOT WORK
#TODO: CASE_3 does not work, although the Function conversion is correct and the intervals are too.
#It is a similar one to CASE_1
    ## f(x) = 5x^2 -2x + 10
    ## f'(x) = 10x -2 = 0 --> x_star = 2/10
    f = PolynomialFunction(n_variables=1, f="[5*x[0]**2-2*x[0]+10]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    verified_global_solution = final_solution(all_solutions)
    print('Verified global solution:', verified_global_solution)

elif CASE_4:
    ## f(x) = 3x^2 -3x + 1
    ## f'(x) = 6x -3 = 0 --> x_star = 3/6 = 1/2
    f = PolynomialFunction(n_variables=1, f="[3*x[0]**2-3*x[0]+1]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    verified_global_solution = final_solution(all_solutions)
    print('Verified global solution:', verified_global_solution)
else:
    print('Please enable an example of polynomial')