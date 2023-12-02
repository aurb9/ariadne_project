import re
from typing import List
from typing import Union

from pyariadne import BoxDomainType
from pyariadne import nul
from pyariadne import dp
from pyariadne import FloatDP
from pyariadne import FloatDPPoint
from pyariadne import Function
from pyariadne import pow
from pyariadne import ValidatedFeasibilityProblem
from pyariadne import ValidatedKleenean
from pyariadne import ValidatedNumberVector


ZERO = FloatDP(0, dp)


class _LiteralExpression:
    _powers: List[float] = None
    _coefficients: List[float] = None

    def __init__(self, n_parameters: int, expression: List[str]) -> None:
        # TODO: convert expression
        default = [0 for _ in range(n_parameters)]
        self._powers = default
        self._coefficients = default

    @property
    def powers(self) -> List[float]:
        return self._powers

    @property
    def coefficients(self) -> List[float]:
        return self._coefficients

    @property
    def value(self) -> List[Union[List, float]]:
        return [self._powers, self._coefficients]


def _convert_function_to_literal_expressions(function: Function) -> List[_LiteralExpression]:
    """
    Converts an ariadne Function to a list of coefficients / powers describing the function.
    e.g., x_0^2 + 3x_1 + 1 ==> [((2, 0), (1, 0)), ((0, 1), (0, 3)), ((0, 0), (1, 0))]

    :param function: function to be transformed
    :return: list of literal expressions
    """
    function_str: str = function.__repr__()
    argument_match = re.search(r"Function\((\d+)", function_str)
    if argument_match:
        n_arguments = int(argument_match.group(1))
    else:
        raise Exception("Number of arguments not found")

    # TODO: split for each ()
    lambda_match = re.search(r"lambda x: \[(.*)\]", function_str)
    if lambda_match:
        lambda_expression = lambda_match.group(1)[1: -1]
        function_as_literal_expressions = re.split(r'(\(\))', lambda_expression)
    else:
        raise Exception("Function not found")

    # TODO: convert to literal expressions
    print(function)
    print(n_arguments)
    print(function_as_literal_expressions)
    input()

    return function_as_literal_expressions


# TODO: should return polynomial ariadne function
def _convert_literal_expressions_to_function(function_as_literal_expressions: List[_LiteralExpression]) -> Function:
    # TODO: implement
    return Function()


def _convert_function_to_TODO(function: Function) -> Function:
    function_as_literal_expressions = _convert_function_to_literal_expressions(function=function)
    # TODO: swap around or whatever to get x^2 p(1/x)

    return _convert_literal_expressions_to_function(function_as_literal_expressions=function_as_literal_expressions)


def _convert_polynomial(p: ValidatedFeasibilityProblem) -> List[ValidatedFeasibilityProblem]:
    div = Function(1, lambda x: x)
    g = _convert_function_to_TODO(function=p.g)
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
g = Function(2, lambda x: [pow(x[0], 2) + 3 * x[1] - 1])
C = BoxDomainType([{"-0.0625": "0.0625"}])
D1 = BoxDomainType([(-1, FloatDP.inf(dp))])
fp1 = ValidatedFeasibilityProblem(D1, g, C)
print(solver.feasible(fp1))
