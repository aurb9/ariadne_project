from typing import Dict
from typing import List
from typing import Optional
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


# TODO: I think this is completely wrong actually
def _compute_boxes_to_optimise_over(
    D: FloatDPExactBox, endpoints_infinity: Dict[int, Dict[str, bool]]
) -> Dict[int, Dict[str, FloatDPExactBox]]:
    domains_per_variable = {}
    for x in range(D.dimension()):
        b1 = intersection(B1, D[x])
        b2 = intersection(B2, D[x])
        b3 = intersection(B3, D[x])

        if endpoints_infinity[x][B1_STR]:
            b1 = box_reciprocal(b1)
        if endpoints_infinity[x][B3_STR]:
            b3 = box_reciprocal(b3)

        domains = {}
        if not b1.empty():
            domains[B1_STR] = b1
        if not b2.empty():
            domains[B2_STR] = b2
        if not b3.empty():
            domains[B3_STR] = b3

        domains_per_variable[x] = domains

    return domains_per_variable


def _check_endpoints_infinity(D: FloatDPExactBox) -> Dict[int, Dict[str, bool]]:
    """
    Checks if the lower or upperbound is infinite
    :param D: domain
    :return: list of booleans for each dimension if one of bounds is infinite
    """
    results = {
        x: {
            B1_STR: is_inf(D[x].lower_bound()),
            B3_STR: is_inf(D[x].upper_bound())
        }
        for x in range(D.dimension())
    }
    return results


def _compute_polynomial_trick_of_function_for_nth_variable(
    f_derivative: PolynomialFunction, n: int
) -> PolynomialFunction:
    n_variables = f_derivative.n_variables
    x = MultivariatePolynomial[FloatDPBounds].coordinates(n_variables, dp)

    max_degree = f_derivative.max_degree_nth_variable(n=n)
    x_power_degree = PolynomialFunction(n_variables=n_variables, f=x[n] ** max_degree)
    f_derivative_at_one_over_x = f_derivative.evaluate_at_one_over_x(n=n)
    q = x_power_degree * f_derivative_at_one_over_x

    return q


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

    def _create_subproblems(self, f: PolynomialFunction, D: FloatDPExactBox) -> List[PolynomialOptimisationProblem]:
        n_variables = f.n_variables

        endpoints_infinity = _check_endpoints_infinity(D=D)
        # We do not need to compute the boxes if INF is not an endpoint
        # But how to later combine the boxes? --> Need to fix _compute_boxes_to_optimise_over
        all_domains = _compute_boxes_to_optimise_over(D=D, endpoints_infinity=endpoints_infinity)
        possible_domains_per_variable = [list(x.keys()) for x in all_domains.values()]
        domains_per_problem = list(product(*possible_domains_per_variable, repeat=1))
        # Problem, we need to get the same list of conversions as we constructed problems

        # TODO: 3. depending on the domains_per_problem, we determine if we need q or not.
        # However, #functions << #domains for large dimensional problems.
        # We can use endpoints_infinity to determine if we should get q :)
        # TODO: 3. so that we do not necessarily compute q (if no inf then no need to compute it at all)
        all_functions_per_variable = {}
        for n in range(n_variables):
            f_derivative = f.derivative(n=n)
            need_to_compute_trick = any(list(endpoints_infinity[n].values()))
            functions = [f_derivative]
            if need_to_compute_trick:
                f_trick = _compute_polynomial_trick_of_function_for_nth_variable(f_derivative=f_derivative, n=n)
                functions.append(f_trick)

            all_functions_per_variable[n] = functions

        problems = []
        for x in domains_per_problem:
            functions = []
            domains = []
            list_of_booleans_converting = []
            for n in range(n_variables):
                box = x[n]
                possible_functions_for_nth_variable = all_functions_per_variable[n]
                need_to_convert = False
                function = possible_functions_for_nth_variable[0]
                if box != B2_STR and endpoints_infinity[n][box]:
                    need_to_convert = True
                    function = possible_functions_for_nth_variable[1]

                functions.append(function.function)
                list_of_booleans_converting.append(need_to_convert)

                domain = all_domains[n][box]
                domains.append(domain)

            problem = PolynomialOptimisationProblem(
                f=ValidatedVectorMultivariateFunction(functions),
                D=FloatDPExactBox(domains),
                is_conversion_needed_per_dimension=list_of_booleans_converting
            )
            problems.append(problem)

        return problems

    def _find_all_minima_within_box(
        self, f: PolynomialFunction, p: PolynomialOptimisationProblem
    ) -> List[FloatDPBoundsVector]:
        solver = IntervalNewtonSolver(1e-8, 20)
        solutions = self.solve_of_system_of_equations_within_box(solver=solver, system_of_equations=p.f, domain=p.D)

        minima = []
        for i, x in enumerate(solutions):
            if p.is_conversion_needed_per_dimension[i]:
                for dimension in range(x.size()):
                    x[dimension] = 1 / x[dimension]

            second_derivative_test = [possibly(f.second_derivative(n_1=dim)(x) > 0) for dim in range(x.size())]
            if all(second_derivative_test):
                minima.append(solutions[i])

        return solutions

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

    def minimise(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> FloatDPBoundsVector:
        all_minima = self.minimise_all(f=f, D=D)
        global_minimum = self._compute_global_minimum(f=f, all_minima=all_minima)

        return global_minimum
