from typing import List
from typing import Optional
from typing import Tuple

from itertools import product

from pyariadne import definitely
from pyariadne import dp
from pyariadne import is_nan
from pyariadne import FloatDP
from pyariadne import FloatDPBounds
from pyariadne import FloatDPBoundsVector
from pyariadne import FloatDPExactBox
from pyariadne import IntervalNewtonSolver
from pyariadne import MultivariatePolynomial
from pyariadne import possibly
from pyariadne import ValidatedNumber
from pyariadne import ValidatedVectorMultivariateFunction

from utils.box_operations import box_reciprocal
from utils.polynomial_function import PolynomialFunction

INF = FloatDP.inf(dp)
NAN = FloatDP.nan(dp)


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


def _convert_problem(
    f: PolynomialFunction, D: FloatDPExactBox
) -> Tuple[ValidatedVectorMultivariateFunction, FloatDPExactBox]:
    q_by_variable = []
    n_variables = f.n_variables
    x = MultivariatePolynomial[FloatDPBounds].coordinates(n_variables, dp)
    for n in range(n_variables):
        max_degree = f.max_degree_nth_variable(n=n) - 1
        x_power_degree = PolynomialFunction(n_variables=n_variables, f=x[n]**max_degree)
        f_derivative = f.derivative(n=n)
        f_derivative_evaluated_at_one_over_x = f_derivative.evaluate_at_one_over_x()
        q = x_power_degree * f_derivative_evaluated_at_one_over_x
        q_by_variable.append(q)

    functions_to_optimise = ValidatedVectorMultivariateFunction(q_by_variable)

    domain = box_reciprocal(box=D)

    return functions_to_optimise, domain


class PolynomialOptimiser:
    @staticmethod
    def find_roots_of_q_over_box(
        solver: IntervalNewtonSolver,
        system_of_equations: ValidatedVectorMultivariateFunction,
        domain: FloatDPExactBox
    ) -> FloatDPBounds:
        print(system_of_equations)
        solutions = solver.solve_all(system_of_equations, domain)
        if solutions:
            return solutions

        return NAN

    def minimise(
        self,
        f: PolynomialFunction,
        D: FloatDPExactBox,
        f_to_optimise: Optional[List] = None,
        convert_problem: bool = True
    ) -> ValidatedNumber:
        solver = IntervalNewtonSolver(1e-8, 12)
        if f_to_optimise is None:
            if convert_problem:
                f_to_optimise, domain = _convert_problem(f=f, D=D)
            else:
                f_to_optimise = ValidatedVectorMultivariateFunction([f.function.derivative(0)])
                domain = D
        else:
            f_to_optimise = [fun.function for fun in f_to_optimise]
            f_to_optimise = ValidatedVectorMultivariateFunction(f_to_optimise)
            domain = D

        solution = self.find_roots_of_q_over_box(
            solver=solver, system_of_equations=f_to_optimise, domain=domain
        )
        if isinstance(solution, FloatDP):
            solution = solution
        elif len(solution) > 1:
            solution = multiple_solutions(f, solution)
        else:
            solution = solution[0][0]

        solution = ValidatedNumber(1 / solution) if convert_problem else ValidatedNumber(solution)
        return solution

    # TODO: implement technique when user knowns that the optimum is in a certain box
    def minimise_all(self, f: PolynomialFunction) -> List[ValidatedNumber]:
        b1 = (-1, 0)
        b2 = (-1, 1)
        b3 = (0, 1)

        domains_dict = {"b1": b1, "b2": b2, "b3": b3}
        domains = list(domains_dict.keys())

        total_dimensions = f.n_variables
        x = MultivariatePolynomial[FloatDPBounds].coordinates(total_dimensions, dp)
        possible_functions = []  # contains functions wrt index [derivative, trick]
        for dimension in range(total_dimensions):
            # Normal derivative wrt dimension
            f_derivative = f.derivative(n=dimension)

            # Polynomial trick wrt dimension
            max_degree = f.max_degree_nth_variable(n=dimension) - 1
            x_power_degree = PolynomialFunction(n_variables=total_dimensions, f=x[dimension]**max_degree)
            # q = x_power_degree.function * f_derivative.evaluate_at_one_over_x().function
            q = x_power_degree * f_derivative.evaluate_at_one_over_x()
            possible_functions.append([f_derivative, q])

        all_possible_domains = list(product(domains, repeat=total_dimensions))

        # Lists that resemble all combination of possible domains and functions for them.
        all_boxes = []
        all_boxes_strings = []
        all_functions = []

        for combination in all_possible_domains:
            subdomain_strings = [comb_part for comb_part in combination]
            all_boxes_strings.append(subdomain_strings)
            # Use dictionary look-up to get the actual box
            subdomain_boxes = [domains_dict[comb_part] for comb_part in subdomain_strings]

            functions = []
            for dim in range(len(possible_functions)):
                if subdomain_strings[dim] == 'b2':
                    functions.append(possible_functions[dim][0])
                else:
                    functions.append(possible_functions[dim][1])
            all_functions.append(functions)

            box = FloatDPExactBox(subdomain_boxes)
            all_boxes.append(box)

        assert (len(all_boxes) == len(all_functions))

        critical_points = []
        for i in range(len(all_boxes)):
            d = all_boxes[i]
            f_to_optimise = all_functions[i]
            convert_problem = 'b2' not in all_boxes_strings[i]
            optimum = self.minimise(f=f, D=d, f_to_optimise=f_to_optimise, convert_problem=convert_problem)
            critical_points.append(optimum)

        return critical_points

    def compute_global_optima(
        self, f: PolynomialFunction, critical_points: List[ValidatedNumber]
    ) -> Tuple[ValidatedNumber, FloatDP]:
        verified_solutions = [solution for solution in critical_points if not is_nan(solution.get(dp).value())]
        if not verified_solutions:
            print("ERROR: NO REAL SOLUTION FOUND")
            print("All solutions found:", critical_points)
            return NAN, NAN
        elif len(verified_solutions) == 1:
            verified_global_solution = verified_solutions[0].get(dp).value()
            verified_global_solution_fx = f(verified_global_solution)
            return verified_global_solution, verified_global_solution_fx
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
            return verified_global_solution, verified_global_solution_fx
