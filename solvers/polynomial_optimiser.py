from typing import List
from typing import Tuple

from pyariadne import FloatDPBounds
from pyariadne import FloatDPExactBox
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPExactInterval
from pyariadne import IntervalNewtonSolver
from pyariadne import ValidatedNumber
from pyariadne import ValidatedVectorMultivariateFunction

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


def _box_reciprocal(box: FloatDPExactBox) -> FloatDPExactBox:
    """
    Converting the entire domain to 1/domain by going over every subdomain and converting that
    :param box: a box containing the domain (can be single or multiple)
    :return: the new_domain which is 1/input_domain
    """
    sub_boxes = []
    for dim_i in range(box.dimension()):
        sub_boxes.append(_convert_single_box(box[dim_i]))

    new_box = FloatDPExactBox(sub_boxes)
    return new_box


def _convert_problem_with_respect_to_nth_variable(f: PolynomialFunction, n: int) -> PolynomialFunction:
    max_degree = f.max_degree_nth_variable(n=n) - 1
    x_power_degree = PolynomialFunction(n_variables=f.n_variables, f=f"[x[{n}**{max_degree}]")
    f_derivative = PolynomialFunction(n_variables=f.n_variables, f=f.function.derivative(n))
    q = x_power_degree * f_derivative.evaluate_at_one_over_x()

    return q


class PolynomialOptimiser:
    def _minimise_over_box(
        self, solver: IntervalNewtonSolver, system_of_equations: List[PolynomialFunction], domain: FloatDPExactBox
    ) -> FloatDPBounds:
        # TODO: solve system of linear equations
        function_to_minimise = ValidatedVectorMultivariateFunction(function.function)
        solutions = solver.solve_all(function_to_minimise, domain)
        if solutions:
            return min(solutions)[0]

        return FloatDP.nan(dp)

    def minimise(self, f: PolynomialFunction, D: FloatDPExactBox, convert_problem: bool = True) -> ValidatedNumber:
        solver = IntervalNewtonSolver(1e-8, 12)
        system_of_equations_to_solve = []
        for n in range(f.n_variables):
            system_of_equations_to_solve.append(
                _convert_problem_with_respect_to_nth_variable(f=f, n=n) if convert_problem
                else PolynomialFunction(n_variables=f.n_variables, f=f.function.derivative(n))
            )

        domain = _box_reciprocal(box=D) if convert_problem else D
        solution = self._minimise_over_box(
            solver=solver, system_of_equations=system_of_equations_to_solve, domain=domain
        )
        solution = ValidatedNumber(1 / solution) if convert_problem else ValidatedNumber(solution)

        return solution


f = PolynomialFunction(n_variables=2, f="[-2*x[0]+x[0]**2+100*x[1]**2-200*x[1]*x[0]**2+100*x[0]**4+1]")  # Min should be at (1, 1)
opt = PolynomialOptimiser()
opt.minimise(f, D=FloatDPExactBox([(-FloatDP.inf(dp), "-1")]), convert_problem=True)
