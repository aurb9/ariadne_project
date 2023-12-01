import re
from typing import List

from pyariadne import BoxDomainType, nul
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPPoint
from pyariadne import Function
from pyariadne import ValidatedFeasibilityProblem
from pyariadne import ValidatedKleenean
from pyariadne import ValidatedNumberVector


ZERO = FloatDP(0, dp)


def _convert_function_to_expression_to_function(function: Function) -> Function:
    function_str: str = function.__crepr__()[1: -1]
    function_split = re.split(r"(\*|\+)", function_str)
    function_split = [item.strip() for item in function_split if item]
    print(function_split)
    function_representation = {}
    index = 0
    append = []
    for expression in function_split:
        if "x" in expression:
            function_representation[index] = 0
            index += 1
            for i in append:
                ...
            append.clear()
        else:
            append.append(expression)

    return function


def _convert_polynomial(p: ValidatedFeasibilityProblem) -> List[ValidatedFeasibilityProblem]:
    div = Function(1, lambda x: x)
    g = p.g[0] / div[0]  # TODO: convert function to 1/x ==> look at the bottom
    domain = p.D  # TODO: convert domain also to be 1/D
    if domain.contains(FloatDPPoint(ZERO)):
        domain_left, domain_right = domain.split(0, ZERO)
        problems = [
            ValidatedFeasibilityProblem(domain_left, g, p.C),
            ValidatedFeasibilityProblem(domain_right, g, p.C)
        ]
    else:
        problems = [ValidatedFeasibilityProblem(p.D, g, p.C)]

    return problems


class PolynomialOptimiser:  # (ValidatedOptimiserInterface):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _feasible_problem(self, p: ValidatedFeasibilityProblem) -> ValidatedKleenean:
        # TODO: implement

        return ValidatedKleenean(False)

    # TODO: should be either feasible point
    #  or "certificate of feasibility" (collection of pairs of boxes and multipliers)
    def feasible(self, p: ValidatedFeasibilityProblem) -> ValidatedKleenean:
        problems = _convert_polynomial(p=p)
        for problem in problems:
            if self._feasible_problem(p=problem) == "false":  # TODO: can be changed to not self._feasible?
                return ValidatedKleenean(False)

        return ValidatedKleenean(True)

    def _solve_problem(self, p: ValidatedFeasibilityProblem) -> ValidatedNumberVector:
        # TODO: implement using Newton approach
        pass

    def minimise(self, p: ValidatedFeasibilityProblem) -> ValidatedNumberVector:
        problems = _convert_polynomial(p=p)
        opt = nul(0)
        for problem in problems:
            pass
            # TODO: solve each and return lowest value
        # TODO: set gradient to 0 and use Newton approach

        return opt


solver = PolynomialOptimiser()
g = Function(1, lambda x: 3*x)
print(_convert_function_to_expression_to_function(function=g))
print()

# p(x) = a_0 + a_1*x + ...
# q(x) = x^2 * p / x

# ==> either dict or use expression from ariadne then use RealValuation

# Make polynomial class / function that returns list of index and coefficients ==> parse that back to polynomial ariadne function
# C = BoxDomainType([{"-0.0625": "0.0625"}])
# D1 = BoxDomainType([(-1, FloatDP.inf(dp))])
# fp1 = ValidatedFeasibilityProblem(D1, g, C)
# print(solver.feasible(fp1))
