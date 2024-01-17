from pyariadne import FloatDPExactBox, FloatDP, dp, is_nan, ValidatedNumber, evaluate

from solvers.polynomial_optimiser import PolynomialOptimiser
from utils.string_parsing_version.polynomial_function import PolynomialFunction


def eval_f(f: PolynomialFunction, x: FloatDP) -> FloatDP:
    return evaluate(f.function, [x])[0].value()  # hard-coded 0 for 1D problem


def final_solution(f: PolynomialFunction, all_solutions: list[ValidatedNumber]) -> (ValidatedNumber, FloatDP):
    # First check for incompatible solutions (NaNs)
    verified_solutions = [solution for solution in all_solutions if not is_nan(solution.get(dp).value())]

    if len(verified_solutions) == 0:
        print('ERROR: NO REAL SOLUTION FOUND')
        print('All solutions found:', all_solutions)
        return (FloatDP.nan(dp), FloatDP.nan(dp))
    elif len(verified_solutions) == 1:  # Only 1 solution found
        verified_global_solution = verified_solutions[0].get(dp).value()
        verified_global_solution_fx = eval_f(f, verified_global_solution)
        return (verified_global_solution, verified_global_solution_fx)
    else:  # Multiple solutions found
        verified_float_solutions = [sol.get(dp).value() for sol in verified_solutions]  # Get the values x
        verified_float_solutions_fx = [eval_f(f, value) for value in verified_float_solutions]  # Calculate fx
        verified_combined_solutions = [(i, j) for i, j in
                                       zip(verified_float_solutions, verified_float_solutions_fx)]  # Combine them

        # Get the minimum function value of the solutions returned
        verified_global_solution_fx = INF
        for solution_fx in verified_float_solutions_fx:
            verified_global_solution_fx = min(verified_global_solution_fx, solution_fx)

        # Get the original x back
        verified_global_solution = next(
            (v[0] for _, v in enumerate(verified_combined_solutions) if v[1] == verified_global_solution_fx))
        return (verified_global_solution, verified_global_solution_fx)


solver = PolynomialOptimiser()

INF = FloatDP.inf(dp)

# converting DOMAIN_2 problem actually returns [-1, 1],
# so do not convert for computational reasons
DOMAIN_1 = FloatDPExactBox([(-INF, "-1")])
DOMAIN_2 = FloatDPExactBox([(-1, 1)])
DOMAIN_3 = FloatDPExactBox([(1, INF)])

CASE_1 = False #opt in DOMAIN_1
CASE_2 = False #opt in DOMAIN_3
CASE_3 = False #opt in DOMAIN_2
CASE_4 = False #opt in DOMAIN_2
CASE_5 = False #opt in DOMAIN_1, but 0.25 as a in (ax^2+bx+c) --> 25

if CASE_1:
    ## f(x) = x^2 + 2x
    ## f'(x) = 2x + 2 = 0 --> x_star = -1
    f = PolynomialFunction(n_variables=1, f="[x[0]**2+2*x[0]]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    x_global, fx_global = final_solution(f, all_solutions)
    print('Global minimum x:', x_global)
    print('Global minimum f(x): ', fx_global)

if CASE_2:
    ## f(x) = 2x^2 -6x + 5
    ## f'(x) = 4x - 6 = 0 --> x_star = 3/2
    f = PolynomialFunction(n_variables=1, f="[2*x[0]**2-6*x[0]+5]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    x_global, fx_global = final_solution(f, all_solutions)
    print('Global minimum x:', x_global)
    print('Global minimum f(x): ', fx_global)

if CASE_3:
    ## f(x) = 5x^2 -2x + 10
    ## f'(x) = 10x -2 = 0 --> x_star = 2/10
    f = PolynomialFunction(n_variables=1, f="[5*x[0]**2-2*x[0]+10]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    x_global, fx_global = final_solution(f, all_solutions)
    print('Global minimum x:', x_global)
    print('Global minimum f(x): ', fx_global)

if CASE_4:
    ## f(x) = 3x^2 -3x + 1
    ## f'(x) = 6x -3 = 0 --> x_star = 3/6 = 1/2
    f = PolynomialFunction(n_variables=1, f="[3*x[0]**2-3*x[0]+1]")
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    x_global, fx_global = final_solution(f, all_solutions)
    print('Global minimum x:', x_global)
    print('Global minimum f(x): ', fx_global)

if CASE_5:
    ## f(x) = 0.25x^2 +2x - 1
    ## f'(x) = 0.5x +2 = 0 --> x_star = -2/0.5 = -4
    f = PolynomialFunction(n_variables=1, f="[2*x[0]+0.25*x[0]**2 -1]")
    print(f.function)
    f_temp  =f.function
    x = FloatDP("-4", dp)
    fx = evaluate(f_temp, [x])
    print(fx)
    opt1 = solver.minimise(f=f, D=DOMAIN_1)
    opt2 = solver.minimise(f=f, D=DOMAIN_2, convert_problem=False)
    opt3 = solver.minimise(f=f, D=DOMAIN_3)

    # Combine all solutions and check them
    all_solutions = [opt1, opt2, opt3]
    x_global, fx_global = final_solution(f, all_solutions)
    print('Global minimum x:', x_global)
    print('Global minimum f(x): ', fx_global)
