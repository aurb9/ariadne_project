from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from itertools import product

from pyariadne import dp
from pyariadne import is_inf
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

from utils.box_operations import box_reciprocal, _convert_single_box
# TODO: _convert_single_box is actually not meant to be accessed like this...
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


def _compute_boxes_to_optimise_over(D: FloatDPExactBox, endpoints_infinity: List[bool]) -> Dict[str, Union[FloatDPExactBox, None]]:
    b1s = []
    b2s = []
    b3s = []
    for x in range(D.dimension()):
        b1 = intersection(B1, D[x])
        b2 = intersection(B2, D[x])
        b3 = intersection(B3, D[x])

        if b1 != EMPTY_INTERVAL:
            if endpoints_infinity[x]:
                b1 = _convert_single_box(b1)
            b1s.append(b1)
        if b2 != EMPTY_INTERVAL:
            if endpoints_infinity[x]:
                b2 = _convert_single_box(b2)
            b2s.append(b2)
        if b3 != EMPTY_INTERVAL:
            if endpoints_infinity[x]:
                b3 = _convert_single_box(b3)
            b3s.append(b3)

    b1 = FloatDPExactBox(b1s)
    b2 = FloatDPExactBox(b2s)
    b3 = FloatDPExactBox(b3s)

    result = {}
    if b1.dimension() != 0:
        result[B1_STR] = b1
    if b2.dimension() != 0:
        result[B2_STR] = b2
    if b3.dimension() != 0:
        result[B3_STR] = b3

    return result

def _check_endpoints_infinity(D: FloatDPExactBox) -> List[bool]:
    """
    Checks if the lower or upperbound is infinite
    :param D: domain
    :return: a list of booleans for each dimensions if one of bounds is infinite
    """
    results = []
    for dim in range(D.dimension()):
        if is_inf(D[dim].lower_bound()) or is_inf(D[dim].upper_bound()):
            results.append(True)
        else:
            results.append(False)
    return results


# TODO: 4. then this should change (perhaps make another method to compute derivative,
#  compute this first for all variables in _create_subproblems and then compute the q for those we need)
#  or anything else you can think of that is efficient (I feel like we will double-compute quite some stuff with this
#  suggestion, but I feel like this would be the case for any way we go)
def _compute_derivative_and_polynomial_trick_of_function(
        f: PolynomialFunction, n: int
) -> Tuple[ValidatedScalarMultivariateFunction, ValidatedScalarMultivariateFunction]:
    n_variables = f.n_variables
    x = MultivariatePolynomial[FloatDPBounds].coordinates(n_variables, dp)

    f_derivative = f.derivative(n=n)

    max_degree = f.max_degree_nth_variable(n=n) - 1
    x_power_degree = PolynomialFunction(n_variables=n_variables, f=x[n] ** max_degree)
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
        print(system_of_equations)
        print(domain)
        try:
            solutions = solver.solve_all(system_of_equations, domain)
        except RuntimeError:
            solutions = []

        return solutions if isinstance(solutions, list) else [solutions]

    def _find_all_minima_within_box(self, f: PolynomialFunction, p: PolynomialOptimisationProblem) -> List[
        FloatDPBoundsVector]:
        solver = IntervalNewtonSolver(1e-8, 20)
        solutions = self.solve_of_system_of_equations_within_box(solver=solver, system_of_equations=p.f, domain=p.D)

        minima = []
        for i, x in enumerate(solutions):
            if p.domains[i] == True:
                for dimension in range(x.size()):
                    x[dimension] = 1 / x[dimension]

            # Check the second derivative f''(x)
            # > 0 --> minimum
            # < 0 --> maximum
            # = 0 --> inconclusive
            second_derivative_test = [possibly(f.second_derivative(n_1=dim)(x) > 0) for dim in range(x.size())]
            if all(second_derivative_test):
                minima.append(solutions[i])

        return solutions

    def minimise(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> FloatDPBoundsVector:
        all_minima = self.minimise_all(f=f, D=D)
        global_minimum_location = self._compute_global_minimum(f=f, all_minima=all_minima)

        return global_minimum_location

    def _create_subproblems(self, f: PolynomialFunction, D: FloatDPExactBox) -> List[PolynomialOptimisationProblem]:
        n_variables = f.n_variables

        endpoints_infinity = _check_endpoints_infinity(D=D)
        # We do not need to compute the boxes if INF is not an endpoint
        # But how to later combine the boxes? --> Need to fix _compute_boxes_to_optimise_over
        all_domains = _compute_boxes_to_optimise_over(D=D, endpoints_infinity=endpoints_infinity)
        print('all_domains:', all_domains)
        domains_per_problem = list(product(all_domains.keys(), repeat=n_variables))
        # Problem, we need to get the same list of conversions as we constructed problems

        # TODO: 3. depending on the domains_per_problem, we determine if we need q or not.
        # However, #functions << #domains for large dimensional problems.
        # We can use endpoints_infinity to determine if we should get q :)
        # TODO: 3. so that we do not necessarily compute q (if no inf then no need to compute it at all)
        all_functions = [_compute_derivative_and_polynomial_trick_of_function(f=f, n=n) for n in range(n_variables)]

        problems = []
        for x in domains_per_problem:
            functions = []
            domains = []
            list_of_booleans_converting = []
            for n in range(n_variables):
                box = x[n]
                function = all_functions[n][0] if endpoints_infinity[n] else all_functions[n][1]
                functions.append(function)
                list_of_booleans_converting.append(endpoints_infinity[n])

                domain = all_domains[box][n]
                domains.append(domain)

            problem = PolynomialOptimisationProblem(
                f=ValidatedVectorMultivariateFunction(functions),
                D=FloatDPExactBox(domains),
                domains=list_of_booleans_converting
            )
            problems.append(problem)

        return problems

    def minimise_all(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> List[FloatDPBoundsVector]:
        n_variables = f.n_variables
        if D is None:
            D = FloatDPExactBox([(-INF, INF) for _ in range(n_variables)])

        assert D.dimension() == n_variables, "Boxes not specified for all variables"

        problems = self._create_subproblems(f=f, D=D)
        minima = []
        for p in problems:
            solutions_to_problem = self._find_all_minima_within_box(f=f, p=p)
            minima = [*minima, *solutions_to_problem]

        return minima

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
