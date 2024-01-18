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
NAN = ValidatedNumber(FloatDP.nan(dp))


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

def _convert_problem_wrt_var(
        f: PolynomialFunction, n: int
) -> Tuple[PolynomialFunction, PolynomialFunction]:
    n_variables = f.n_variables
    x = MultivariatePolynomial[FloatDPBounds].coordinates(n_variables, dp)

    f_derivative = f.derivative(n=n)

    max_degree = f.max_degree_nth_variable(n=n) - 1
    x_power_degree = PolynomialFunction(n_variables=n_variables, f=x[n] ** max_degree)
    q = x_power_degree * f_derivative.evaluate_at_one_over_x()

    return f_derivative, q


def _convert_problem(
        f: PolynomialFunction, D: FloatDPExactBox
) -> Tuple[ValidatedVectorMultivariateFunction, FloatDPExactBox]:
    q_by_variable = []
    n_variables = f.n_variables
    x = MultivariatePolynomial[FloatDPBounds].coordinates(n_variables, dp)
    for n in range(n_variables):
        max_degree = f.max_degree_nth_variable(n=n) - 1
        x_power_degree = PolynomialFunction(n_variables=n_variables, f=x[n] ** max_degree)
        f_derivative = f.derivative(n=n)
        f_derivative_evaluated_at_one_over_x = f_derivative.evaluate_at_one_over_x()
        q = x_power_degree * f_derivative_evaluated_at_one_over_x
        q_by_variable.append(q)
        print(q)
        input()

    functions_to_optimise = ValidatedVectorMultivariateFunction(q_by_variable)

    domain = box_reciprocal(box=D)

    return functions_to_optimise, domain


class PolynomialOptimiser:
    @staticmethod
    def find_roots_of_q_over_box(
            solver: IntervalNewtonSolver,
            system_of_equations: ValidatedVectorMultivariateFunction,
            domain: FloatDPExactBox
    ) -> List[FloatDPBoundsVector]:
        #print(system_of_equations)
        #print(domain)
        #solver_2 = IntervalNewtonSolver(1e-8, 12)
        try:
            solutions = solver.solve_all(system_of_equations, domain)
            #print('solver:', solver_2.solve_all(system_of_equations, domain))
            #print('SOLUTIONS:', solutions)
        except RuntimeError:
            solutions = NAN
        #print('SOLUTIONS:', solutions)
        if isinstance(solutions, list):
            return solutions
        else: return []


    def _find_local_minima_over_box(
            self,
            f: ValidatedVectorMultivariateFunction,
            D: FloatDPExactBox,
            convert_problems: List[bool]
    ) -> List[ValidatedNumber]:
        solver = IntervalNewtonSolver(1e-8, 12)

        solutions = self.find_roots_of_q_over_box(
            solver=solver, system_of_equations=f, domain=D
        )

        for solution in solutions:
            for dim in range(len(convert_problems)):
                if convert_problems[dim]:
                    solution[dim] = 1/solution[dim]

        #if len(solution) == 1:
        return solutions
        #if isinstance(solution, FloatDP):
        #    solution = solution
        #elif len(solution) > 1:
        #    solution = multiple_solutions(f, solution)
        #else:
        #    solution = solution[0][0]

        #solution = ValidatedNumber(1 / solution) if convert_problem else ValidatedNumber(solution)
        #return solution

    # TODO: decide if D is optional for minimise or minimise_all
    def minimise(self, f: PolynomialFunction, D: Optional[FloatDPExactBox]) -> ValidatedNumber:
        minima = self.minimise_all(f=f, D=D)
        print(minima)
        global_minimum_location = self._compute_global_minimum(f=f, minima=minima)

        return global_minimum_location

    # TODO: implement technique when user knowns that the optimum is in a certain box
    # TODO: this should return only minima, not all critical points (second derivative check?)
    def minimise_all(self, f: PolynomialFunction, D: Optional[FloatDPExactBox] = None) -> List[ValidatedNumber]:
        """
        This function returns all minima. The user can specify a domain over which to minimise.
        If the domain is not specified, then the function assumes an unbounded domain.
        :param f: normal function
        :param D: the optional domain
        :return: list of ValidatedNumber which resembles the minima location
        """
        # TODO: find correct minima

        # Assumes unbounded domain
        if D is None:
            # For each function, we store the derivative and the polynomial trick one
            # in possible_functions, because we need to find their roots.
            # So possible_functions[i] returns (f'_i(x), q_i(x))
            total_dimensions = f.n_variables
            possible_functions = []
            for dimension in range(total_dimensions):
                f_derivative, q = _convert_problem_wrt_var(f=f, n=dimension)
                print('q',q)
                print('q.coor', q._coordinates)
                print('q.fun', q.function)
                #input()
                possible_functions.append([f_derivative, q])

            # We split the unbounded domain into 3 subdomains and change 2 of these subdomains
            # 1. (-inf, -1) --> [-1, 0) with q(x) = 0
            # 2. (-1, 1) --> [-1, 1] with f'(x) = 0
            # 1. (1, inf) --> (0, 1] with q(x) = 0

            b1 = (-1, 0)
            b2 = (-1, 1)
            b3 = (0, 1)

            domains_dict = {"b1": b1, "b2": b2, "b3": b3}
            domains = list(domains_dict.keys())
            all_possible_domains = list(product(domains, repeat=total_dimensions))

            # Now, we need to combine the domains with their functions. Since #functions < #domains, we need
            # to check it
            # Lists that resemble all combination of possible domains and functions for them.
            all_boxes = []
            all_boxes_strings = []
            all_functions = []

            for combination in all_possible_domains:
                # First construct the subdomains
                subdomain_strings = [comb_part for comb_part in combination]
                all_boxes_strings.append(subdomain_strings)
                # Use dictionary look-up to get the actual box
                subdomain_boxes = [domains_dict[comb_part] for comb_part in subdomain_strings]
                box = FloatDPExactBox(subdomain_boxes)
                all_boxes.append(box)

                # Now, construct the functions belonging to the subdomains
                functions = []
                for dim in range(len(possible_functions)):
                    if subdomain_strings[dim] == "b2":
                        functions.append(possible_functions[dim][0])  # f'(x)
                    else:
                        functions.append(possible_functions[dim][1])  # q(x)
                all_functions.append(functions)

            assert (len(all_boxes) == len(all_functions))

            # Use the solver to solve roots for the functions (f'(x) or q(x)).
            critical_points = []
            for i in range(len(all_boxes)):
                d = all_boxes[i]
                f_to_optimise = all_functions[i]
                conversions = [not "b2" == subdomain for subdomain in all_boxes_strings[i]]
                print('box strings', all_boxes_strings[i])
                print('f[0]', f_to_optimise[0].function)
                #print('f[1]', f_to_optimise[1].function)
                print(type(f_to_optimise[0]))
                print('Box', d)
                print('convert', conversions)
                f_to_optimise = ValidatedVectorMultivariateFunction([fun.function for fun in f_to_optimise])
                optimum = self._find_local_minima_over_box(f=f_to_optimise, D=d, convert_problems=conversions)

                # Convert 1/x where necessary
                print('optimum', optimum)
                critical_points.append(optimum)
                print(len(critical_points))

            return critical_points

        else:
            a = 0
            # Check subdomains and compute functions (f_der, q) where necessary

        # Compare critical point

    def _compute_global_minimum(self, f: PolynomialFunction, minima: List[ValidatedNumber]) -> ValidatedNumber:
        verified_solutions = [solution for solution in minima if not is_nan(solution.get(dp).value())]
        if not verified_solutions:
            print("ERROR: NO REAL SOLUTION FOUND")
            print("All solutions found:", minima)
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
