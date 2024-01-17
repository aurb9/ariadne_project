from typing import List
from typing import Tuple

from itertools import product

from pyariadne import dp, MultivariatePolynomial
from pyariadne import definitely
from pyariadne import is_nan
from pyariadne import FloatDP
from pyariadne import FloatDPBounds
from pyariadne import ValidatedNumber
from pyariadne import FloatDPExactBox
from pyariadne import FloatDPBoundsVector
from pyariadne import IntervalNewtonSolver
from pyariadne import ValidatedVectorMultivariateFunction

from utils.box_operations import box_reciprocal
from utils.string_parsing_version.polynomial_function import PolynomialFunction

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
        solutions = solver.solve_all(system_of_equations, domain)
        if solutions:
            return solutions

        return NAN

    def minimise(self, f: PolynomialFunction, D: FloatDPExactBox, convert_problem: bool = True) -> ValidatedNumber:
        solver = IntervalNewtonSolver(1e-8, 12)
        if convert_problem:
            f_to_optimise, domain = _convert_problem(f=f, D=D)
        else:
            f_to_optimise = ValidatedVectorMultivariateFunction([f.derivative(0)])
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
        box_1 = (-INF, -1)
        box_2 = (-1, 1)
        box_3 = (1, INF)
        boxes = [box_1, box_2, box_3]

        n_dimensions = f.n_variables
        # TODO: also product of all functions and zip them together
        # then we can remove the boolean list with converting
        all_possible_boxes = list(product(boxes, repeat=n_dimensions))

        all_boxes = []
        convert_list = []
        for box_combination in all_possible_boxes:
            subdomain = [comb_part for comb_part in box_combination]
            box = FloatDPExactBox(subdomain)

            # TODO: later we probably want to know which part of the subdomain needs to be converted
            # But then we need to know how to convert when more than 1 part needs to be converted
            if subdomain.__contains__(box_1) or subdomain.__contains__(box_3):
                convert_list.append(True)
            else:
                convert_list.append(False)
            all_boxes.append(box)

        assert len(all_boxes) == len(convert_list)

        critical_points = []
        for i in range(len(all_boxes)):
            d = all_boxes[i]
            convert_problem = convert_list[i]
            optimum = self.minimise(f=f, D=d, convert_problem=convert_problem)
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
                if definitely(solution_fx < verified_global_solution_fx):
                    verified_global_solution_fx = solution_fx
                    index_location = i

            verified_global_solution = verified_combined_solutions[index_location][0]
            return verified_global_solution, verified_global_solution_fx


f = PolynomialFunction(n_variables=1, f="x[0]**4+10/7*x[0]**3-4*x[0]**2-5/6*x[0]+1")
print(f)
