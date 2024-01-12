from typing import List
from typing import Tuple

from pyariadne import FloatDPBounds, EffectiveVectorMultivariateFunction
from pyariadne import FloatDPExactBox
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPExactInterval
from pyariadne import IntervalNewtonSolver
from pyariadne import ValidatedNumber
from pyariadne import ValidatedVectorMultivariateFunction
from pyariadne import evaluate

from utils.polynomial_function import PolynomialFunction

# TODO: add branch and bound and look at the test.py file


ZERO = FloatDP(0, dp)
ONE = FloatDP(1, dp)


def _convert_single_box(box: FloatDPExactInterval) -> Tuple[FloatDP, FloatDP]:
    """
    Convert a single box by 1/box. E.g., box=[-5, 10] --> new_box = [-1/5, 1/10]
    :param subdomain: an interval with a lowerbound and upperbound in the original domain
    :return: tuple of (new_lowerbound and new_upperbound) for the creation of a new box
    """
    box_lower_bound = box.lower_bound()
    box_upper_bound = box.upper_bound()
    if box_lower_bound > ZERO and box_upper_bound > ZERO:
        new_box_lower_bound = ONE / box_upper_bound
        new_box_upper_bound = ONE / box_lower_bound
    elif box_lower_bound < ZERO < box_upper_bound:
        new_box_lower_bound = ONE / box_lower_bound
        new_box_upper_bound = ONE / box_upper_bound
    else:
        new_box_lower_bound = ONE / box_upper_bound
        new_box_upper_bound = ONE / box_lower_bound

    new_box_lower_bound = new_box_lower_bound.lower().raw()
    new_box_upper_bound = new_box_upper_bound.lower().raw()

    return new_box_lower_bound, new_box_upper_bound

def multiple_solutions(solutions):
    """
    When there are multiple solutions found by the Interval Newton Solver (INS),
    we need to ensure the lowest function value is returned.
    :param solutions: multiple solutions for the root
    :return: location_min which is the location of the lowest minima in the solutions
    """

    total_min = FloatDP.inf(dp)
    location_min = None
    for sol in solutions:
        print(sol)
        f_val = evaluate(f.function, sol)[0].value()  # hard-coded 0 for 1D problem
        print('Function at point:', f_val)
        if f_val < total_min:
            total_min = f_val
            location_min = sol
        print('Total min:', total_min)
        print('Location min:', location_min)
    return location_min[0]

# TODO: this should go to utils
def _box_reciprocal(box: FloatDPExactBox) -> FloatDPExactBox:
    """
    Converting the entire domain to 1/domain by going over every subdomain and converting that
    :param box: a box containing the domain (can be single or multiple)
    :return: the new_domain which is 1/input_domain
    """
    sub_boxes = [_convert_single_box(box[x]) for x in range(box.dimension())]
    new_box = FloatDPExactBox(sub_boxes)

    return new_box


def _convert_problem(
    f: PolynomialFunction, D: FloatDPExactBox
) -> Tuple[EffectiveVectorMultivariateFunction, FloatDPExactBox]:
    q_by_variable = []
    for n in range(f.n_variables):
        max_degree = f.max_degree_nth_variable(n=n) - 1
        x_power_degree = PolynomialFunction(n_variables=f.n_variables, f=f"[x[{n}**{max_degree}]")
        f_derivative = PolynomialFunction(n_variables=f.n_variables, f=f.function.derivative(n))
        q = x_power_degree * f_derivative.evaluate_at_one_over_x()
        q_by_variable.append(q.function)

    functions_to_optimise = EffectiveVectorMultivariateFunction(q_by_variable)

    domain = _box_reciprocal(box=D)

    return functions_to_optimise, domain


class PolynomialOptimiser:
    @staticmethod
    def find_roots_of_q_over_box(
        solver: IntervalNewtonSolver,
        system_of_equations: EffectiveVectorMultivariateFunction,
        domain: FloatDPExactBox
    ) -> FloatDPBounds:
        # TODO: here we should branch and bound (if we use our own solver :))
        solutions = solver.solve_all(system_of_equations, domain)
        if solutions:
            return min(solutions)[0]

        return FloatDP.nan(dp)

    def minimise(self, f: PolynomialFunction, D: FloatDPExactBox, convert_problem: bool = True) -> ValidatedNumber:
        solver = IntervalNewtonSolver(1e-8, 12)
        if convert_problem:
            f_to_optimise, domain = _convert_problem(f=f, D=D)
        else:
            f_to_optimise = f.function.derivative(0)

        domain = _box_reciprocal(box=D) if convert_problem else D
        solution = self.find_roots_of_q_over_box(
            solver=solver, system_of_equations=f_to_optimise, domain=domain
        )
        if type(solution) == FloatDP:
            solution = solution #this could also be removed technically, but kept in for safety
        elif len(solution) > 1:
            solution = multiple_solutions(solution)
        else:
            solution = solution[0][0]

        solution = ValidatedNumber(1 / solution) if convert_problem else ValidatedNumber(solution)
        return solution

f = PolynomialFunction(n_variables=2, f="[x[0]]")
# f = PolynomialFunction(n_variables=2, f="[-2*x[0]+x[0]**2+100*x[1]**2-200*x[1]*x[0]**2+100*x[0]**4+1]")  # Min should be at (1, 1)
opt = PolynomialOptimiser()
opt.minimise(f, D=FloatDPExactBox([(-FloatDP.inf(dp), "-1")]), convert_problem=True)
