from typing import List
from typing import Tuple

from itertools import product

from pyariadne import dp
from pyariadne import is_nan
from pyariadne import FloatDP
from pyariadne import evaluate
from pyariadne import FloatDPBounds
from pyariadne import ValidatedNumber
from pyariadne import FloatDPExactBox
from pyariadne import FloatDPBoundsVector
from pyariadne import IntervalNewtonSolver
from pyariadne import ValidatedVectorMultivariateFunction

from utils.box_operations import box_reciprocal
from utils.polynomial_function import PolynomialFunction

INF = FloatDP.inf(dp)


def multiple_solutions(f: PolynomialFunction, solutions: List[FloatDPBoundsVector]) -> FloatDPBounds:
    """
    When there are multiple solutions are found by the Interval Newton Solver (INS),
    we need to ensure the lowest function value is returned. This method returns the
    location of the lowest value (so the x, not f(x)).
    :param f: original function
    :param solutions: multiple solutions for the root
    :return: location_min which is the location of the lowest minima in the solutions
    """
    total_min = INF
    location_min = None
    for sol in solutions:
        f_val = evaluate(f.function, sol).value()  # hard-coded 0 for 1D problem

        # if current point is less than previous best point,
        # then assign current point to be new best
        if f_val < total_min:
            total_min = f_val
            location_min = sol
    return location_min[0]


def eval_f(f: PolynomialFunction, x: FloatDP) -> FloatDP:
    return f.function([x])


def _convert_problem(
        f: PolynomialFunction, D: FloatDPExactBox
) -> Tuple[ValidatedVectorMultivariateFunction, FloatDPExactBox]:
    q_by_variable = []
    for n in range(f.n_variables):
        max_degree = f.max_degree_nth_variable(n=n) - 1
        x_power_degree = PolynomialFunction(n_variables=f.n_variables, f=f"x[{n}]**{max_degree}")
        f_derivative = PolynomialFunction(n_variables=f.n_variables, f=f.function.derivative(n))
        # one_over_x = PolynomialFunction(n_variables=f.n_variables, f=f"1/x[{n}]")
        # q = x_power_degree * f_derivative(one_over_x)
        q = x_power_degree * f_derivative.evaluate_at_one_over_x()
        q_by_variable.append(q.function)

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

        return FloatDP.nan(dp)

    def minimise(self, f: PolynomialFunction, D: FloatDPExactBox, convert_problem: bool = True) -> ValidatedNumber:
        solver = IntervalNewtonSolver(1e-8, 12)
        if convert_problem:
            f_to_optimise, domain = _convert_problem(f=f, D=D)
        else:
            f_to_optimise = ValidatedVectorMultivariateFunction([f.function.derivative(0)])

        domain = box_reciprocal(box=D) if convert_problem else D
        solution = self.find_roots_of_q_over_box(
            solver=solver, system_of_equations=f_to_optimise, domain=domain
        )
        if isinstance(solution, FloatDP):
            solution = solution  # this could also be removed technically, but kept in for safety
        elif len(solution) > 1:
            solution = multiple_solutions(f, solution)
        else:
            solution = solution[0][0]

        solution = ValidatedNumber(1 / solution) if convert_problem else ValidatedNumber(solution)
        return solution

    # TODO: implement technique when user knowns that the optimum is in a certain box
    def minise_all(self, f: PolynomialFunction) -> List[ValidatedNumber]:
        dim = f.n_variables  # Number of dimensions

        # Split on 3 boxes (default)
        box_1 = (-INF, -1)
        box_2 = (-1, 1)
        box_3 = (1, INF)
        boxes = [box_1, box_2, box_3]

        # TODO: also product of all functions and zip them together
        # then we can remove the boolean list with converting
        all_possible_boxes = list(product(boxes, repeat=dim))

        all_boxes = []
        convert_list = []  # list with booleans whether or not to convert problem
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
        # print(len(all_boxes))  # boxes^dim

        # Now that we know all boxes, we can use the default minimise function
        assert (len(all_boxes) == len(convert_list))

        optima = []
        for i in range(len(all_boxes)):
            d = all_boxes[i]
            convert_problem = convert_list[i]
            optimum = self.minimise(f=f, D=d, convert_problem=convert_problem)
            optima.append(optimum)

        return optima

    def final_solution(self, f: PolynomialFunction, all_solutions: list[ValidatedNumber]) -> (ValidatedNumber, FloatDP):
        # First check for incompatible solutions (NaNs)
        print(all_solutions)
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
            print(type(verified_float_solutions[0]))
            verified_float_solutions_fx = [eval_f(f, value) for value in verified_float_solutions]  # Calculate fx
            verified_combined_solutions = [(i, j) for i, j in
                                           zip(verified_float_solutions, verified_float_solutions_fx)]  # Combine them

            # Get the minimum function value of the solutions returned
            verified_global_solution_fx = INF
            # verified_global_solution_fx = min(verified_float_solutions_fx)

            index_location = -1
            for i in range(len(verified_float_solutions_fx)):
                solution_fx = verified_float_solutions_fx[i]
                if str(solution_fx < verified_global_solution_fx) == 'true':
                    verified_global_solution_fx = solution_fx
                    index_location = i

            # Get the original x back
            print(index_location)
            verified_global_solution = verified_combined_solutions[i][0]
            return (verified_global_solution, verified_global_solution_fx)
