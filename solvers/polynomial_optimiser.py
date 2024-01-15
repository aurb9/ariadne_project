from typing import List
from typing import Tuple

from itertools import product

from pyariadne import dp
from pyariadne import ValidatedVectorMultivariateFunction
from pyariadne import evaluate
from pyariadne import FloatDP
from pyariadne import FloatDPBounds
from pyariadne import FloatDPExactBox
from pyariadne import IntervalNewtonSolver
from pyariadne import ValidatedNumber

from utils.box_operations import box_reciprocal
from utils.polynomial_function import PolynomialFunction


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
        print("Function at point:", f_val)
        if f_val < total_min:
            total_min = f_val
            location_min = sol
        print("Total min:", total_min)
        print("Location min:", location_min)

    return location_min[0]


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
            return min(solutions)[0]

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
            solution = multiple_solutions(solution)
        else:
            solution = solution[0][0]

        solution = ValidatedNumber(1 / solution) if convert_problem else ValidatedNumber(solution)
        return solution

    # TODO: implement technique when user knowns that the optimum is in a certain box
    def minimise_all(self, f: PolynomialFunction) -> List[ValidatedNumber]:
        INF = FloatDP.inf(dp)
        DIM = f.n_variables

        # Split on 3 boxes (default)
        box_1 = (-INF, -1)
        box_2 = (-1, 1)
        box_3 = (1, INF)
        boxes = [box_1, box_2, box_3]

        all_possible_boxes = list(product(boxes, repeat=DIM))

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

        # Now that we know all boxes, we can use the default minimise function
        assert (len(all_boxes) == len(convert_list))

        optima = []
        for i in range(len(all_boxes)):
            d = all_boxes[i]
            convert_problem = convert_list[i]
            optimum = self.minimise(f=f, D=d, convert_problem=convert_problem)
            optima.append(optimum)

        return optima
