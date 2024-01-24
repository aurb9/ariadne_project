from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from itertools import product

from pyariadne import dp
from pyariadne import is_inf
from pyariadne import FloatDP
from pyariadne import definitely
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
EPS = FloatDP.eps(dp)

B1_STR = "b1"
B2_STR = "b2"
B3_STR = "b3"

B1 = FloatDPExactInterval((-INF, -1))
B2 = FloatDPExactInterval((-1, 1))
B3 = FloatDPExactInterval((1, INF))


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
            new_lower_bound = (b1.lower_bound()-EPS).lower().raw()
            b1 = FloatDPExactInterval((new_lower_bound, -EPS))
            domains[B1_STR] = b1
        if not b2.empty():
            new_lower_bound = (b2.lower_bound()-EPS).lower().raw()
            new_upper_bound = (b2.upper_bound()+EPS).upper().raw()
            b2 = FloatDPExactInterval((new_lower_bound, new_upper_bound))
            domains[B2_STR] = b2
        if not b3.empty():
            new_upper_bound = (b3.upper_bound()+EPS).upper().raw()
            b3 = FloatDPExactInterval((EPS, new_upper_bound))
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
            if solutions:
                for x in solutions:
                    print("dom", domain)
                    print("sol", x)
                    print("f(sol)", system_of_equations(x))
        except RuntimeError:
            solutions = []

        return solutions if isinstance(solutions, list) else [solutions]

    def _create_subproblems(
        self, f: PolynomialFunction, D: FloatDPExactBox
    ) -> Tuple[List[PolynomialFunction], List[PolynomialOptimisationProblem]]:
        n_variables = f.n_variables

        endpoints_infinity = _check_endpoints_infinity(D=D)
        all_domains = _compute_boxes_to_optimise_over(D=D, endpoints_infinity=endpoints_infinity)
        possible_domains_per_variable = [list(x.keys()) for x in all_domains.values()]
        domains_per_problem = list(product(*possible_domains_per_variable, repeat=1))

        all_functions_per_variable = {}
        f_derivatives = []
        for n in range(n_variables):
            f_derivative = f.derivative(n=n)
            f_derivatives.append(f_derivative)

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

        return f_derivatives, problems

    def _find_all_minima_within_box(
        self, f: PolynomialFunction, p: PolynomialOptimisationProblem
    ) -> List[FloatDPBoundsVector]:
        solver = IntervalNewtonSolver(1e-8, 100)
        solutions = self.solve_of_system_of_equations_within_box(solver=solver, system_of_equations=p.f, domain=p.D)

        minima = []
        for i, x in enumerate(solutions):
            for dimension in range(len(p.is_conversion_needed_per_dimension)):
                if p.is_conversion_needed_per_dimension[dimension]:
                    x[dimension] = 1 / x[dimension]

            second_derivative_test = [possibly(f.second_derivative(n_1=dim)(x) > 0) for dim in range(x.size())]
            if all(second_derivative_test):
                minima.append(solutions[i])

        return minima

    def _get_endpoints_if_minima(
        self, f_derivatives: List[PolynomialFunction], D: FloatDPExactBox
    ) -> List[FloatDPBoundsVector]:
        lower_endpoints = []
        upper_endpoints = []
        for x in range(D.dimension()):
            lower_endpoints.append(D[x].lower_bound())
            upper_endpoints.append(D[x].upper_bound())

        to_add = []
        if all([definitely(f(x) > 0) for f, x in zip(f_derivatives, lower_endpoints)]):
            to_add.append(FloatDPBoundsVector(lower_endpoints))
        if all([definitely(f(x) < 0) for f, x in zip(f_derivatives, upper_endpoints)]):
            to_add.append(FloatDPBoundsVector(upper_endpoints))

        return to_add


    def minimise_all(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> List[FloatDPBoundsVector]:
        n_variables = f.n_variables
        domain = FloatDPExactBox([(-INF, INF) for _ in range(n_variables)]) if D is None else D

        assert domain.dimension() == n_variables, "Boxes not specified for all variables"

        f_derivatives, problems = self._create_subproblems(f=f, D=domain)
        minima = []
        for p in problems:
            solutions_to_problem = self._find_all_minima_within_box(f=f, p=p)
            minima = [*minima, *solutions_to_problem]

        if D is not None:
            minima = [*minima, *self._get_endpoints_if_minima(f_derivatives=f_derivatives, D=domain)]

        return minima

    def _compute_global_minimum(
        self, f: PolynomialFunction, minima: List[FloatDPBoundsVector]
    ) -> Union[FloatDPBoundsVector, None]:
        if not minima:
            return None

        global_minimum = INF
        global_minimum_objective_value = INF
        for x in minima:
            x_objective_value = f(x)
            if definitely(x_objective_value < global_minimum_objective_value):
                global_minimum = x
                global_minimum_objective_value = x_objective_value

        return global_minimum

    def minimise(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> FloatDPBoundsVector:
        all_minima = self.minimise_all(f=f, D=D)
        global_minimum = self._compute_global_minimum(f=f, minima=all_minima)

        return global_minimum
