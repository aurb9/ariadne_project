from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from itertools import product

from pyariadne import definitely
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPBounds
from pyariadne import FloatDPBoundsVector
from pyariadne import FloatDPExactBox
from pyariadne import FloatDPExactInterval
from pyariadne import intersection
from pyariadne import IntervalNewtonSolver
from pyariadne import MultivariatePolynomial
from pyariadne import possibly
from pyariadne import ValidatedScalarMultivariateFunction
from pyariadne import ValidatedVectorMultivariateFunction

from utils.box_operations import box_reciprocal
from utils.polynomial_optimisation_problem import PolynomialOptimisationProblem
from utils.polynomial_function import PolynomialFunction

INF = FloatDP.inf(dp)
NAN = FloatDP.nan(dp)

B1_STR = "b1"
B2_STR = "b2"
B3_STR = "b3"

B1 = FloatDPExactInterval((-INF, -1))
B2 = FloatDPExactInterval((-1, 1))
B3 = FloatDPExactInterval((1, INF))

EMPTY_INTERVAL = FloatDPExactInterval((1, -1))


def multiple_solutions(f: PolynomialFunction, solutions: List[FloatDPBoundsVector]) -> FloatDPBounds:
    """
    When there are multiple solutions are found by the Interval Newton Solver (INS),
    we need to ensure the lowest function value is returned. This method returns the
    location of the lowest value (so the x, not f(x)).
    :param f: original function
    :param solutions: multiple solutions for the root
    :return: location_min which is the location of the lowest minima in the solutions
    """
    global_minimum = INF
    location_of_minimum = None
    for x in solutions:
        f_value = f(x)
        if definitely(f_value < global_minimum):
            global_minimum = f_value
            location_of_minimum = x

    return location_of_minimum[0]


def _compute_boxes_to_optimise_over(D: FloatDPExactBox) -> Dict[str, Union[FloatDPExactBox, None]]:
    b1s = []
    b2s = []
    b3s = []
    for x in range(D.dimension()):
        b1 = intersection(B1, D[x])
        b2 = intersection(B2, D[x])
        b3 = intersection(B3, D[x])

        if b1 != EMPTY_INTERVAL:
            b1s.append(b1)
        if b2 != EMPTY_INTERVAL:
            b2s.append(b2)
        if b3 != EMPTY_INTERVAL:
            b3s.append(b3)

    b1 = FloatDPExactBox(b1s)
    b2 = FloatDPExactBox(b2s)
    b3 = FloatDPExactBox(b3s)

    result = {}
    if b1.dimension() != 0:
        result[B1_STR] = box_reciprocal(box=b1)
    if b2.dimension() != 0:
        result[B2_STR] = b2
    if b3.dimension() != 0:
        result[B3_STR] = box_reciprocal(box=b3)

    return result


def _compute_derivative_and_polynomial_trick_of_function(
    f: PolynomialFunction, n: int
) -> Tuple[ValidatedScalarMultivariateFunction, ValidatedScalarMultivariateFunction]:
    n_variables = f.n_variables
    x = MultivariatePolynomial[FloatDPBounds].coordinates(n_variables, dp)

    f_derivative = f.derivative(n=n)

    max_degree = f.max_degree_nth_variable(n=n) - 1
    x_power_degree = PolynomialFunction(n_variables=n_variables, f=x[n]**max_degree)
    f_derivative_at_one_over_x = f_derivative.evaluate_at_one_over_x(n=n)
    q = x_power_degree * f_derivative_at_one_over_x

    return f_derivative.function, q.function


class PolynomialOptimiser:
    @staticmethod
    def solve_of_system_of_equations_within_box(
        solver: IntervalNewtonSolver,
        system_of_equations: ValidatedVectorMultivariateFunction,
        domain: FloatDPExactBox
    ) -> List[FloatDPBoundsVector]:
        try:
            solutions = solver.solve_all(system_of_equations, domain)
        except RuntimeError:
            solutions = []

        return solutions if isinstance(solutions, list) else [solutions]

    def _find_all_critical_points_within_box(self, p: PolynomialOptimisationProblem) -> List[FloatDPBoundsVector]:
        solver = IntervalNewtonSolver(1e-8, 20)
        solutions = self.solve_of_system_of_equations_within_box(solver=solver, system_of_equations=p.f, domain=p.D)
        for i, x in enumerate(solutions):
            if p.domains[i] != B2_STR:
                for dimension in range(x.size()):
                    x[dimension] = 1/x[dimension]

        return solutions

    def minimise(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> FloatDPBoundsVector:
        all_minima = self.minimise_all(f=f, D=D)
        global_minimum_location = self._compute_global_minimum(f=f, all_minima=all_minima)

        return global_minimum_location

    # TODO: refactor this
    def _compute_global_minimum(
        self, f: PolynomialFunction, all_minima: List[FloatDPBoundsVector]
    ) -> FloatDPBoundsVector:
        verified_solutions = [x for x in all_minima if x]
        if not verified_solutions:
            print("ERROR: NO REAL SOLUTION FOUND")
            print("All solutions found:", all_minima)
            verified_global_solution = NAN
        elif len(verified_solutions) == 1:
            verified_global_solution = verified_solutions[0].get(dp).value()
        else:
            verified_float_solutions = [sol.get(dp).value() for sol in verified_solutions]
            verified_float_solutions_fx = [f(value) for value in verified_float_solutions]
            verified_combined_solutions = [
                (i, j) for i, j in zip(verified_float_solutions, verified_float_solutions_fx)
            ]
            verified_global_solution_fx = INF
            index_location = -1
            for i in range(len(verified_float_solutions_fx)):
                solution_fx = verified_float_solutions_fx[i]
                if possibly(solution_fx < verified_global_solution_fx):
                    verified_global_solution_fx = solution_fx
                    index_location = i

            verified_global_solution = verified_combined_solutions[index_location][0]

        return verified_global_solution
    
    def _create_subproblems(self, f: PolynomialFunction, D: FloatDPExactBox) -> List[PolynomialOptimisationProblem]:
        n_variables = f.n_variables
        all_functions = [_compute_derivative_and_polynomial_trick_of_function(f=f, n=n) for n in range(n_variables)]

        all_domains = _compute_boxes_to_optimise_over(D=D)
        domains_per_problem = list(product(all_domains.keys(), repeat=n_variables))

        problems = []
        for x in domains_per_problem:
            functions = []
            domains = []
            for n in range(n_variables):
                box = x[n]
                function = all_functions[n][0] if box == B2_STR else all_functions[n][1]
                functions.append(function)

                domain = all_domains[box][n]
                domains.append(domain)

            problem = PolynomialOptimisationProblem(
                f=ValidatedVectorMultivariateFunction(functions),
                D=FloatDPExactBox(domains),
                domains=x
            )
            problems.append(problem)

        return problems

    # TODO: this should return only minima, not all critical points (second derivative check?)
    def minimise_all(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> List[FloatDPBoundsVector]:
        n_variables = f.n_variables
        if D is None:
            D = FloatDPExactBox([(-INF, INF) for _ in range(n_variables)])

        assert D.dimension() == n_variables, "Boxes not specified for all variables"

        problems = self._create_subproblems(f=f, D=D)
        critical_points = []
        for p in problems:
            solutions_to_problem = self._find_all_critical_points_within_box(p=p)
            critical_points = [*critical_points, *solutions_to_problem]

        return critical_points
