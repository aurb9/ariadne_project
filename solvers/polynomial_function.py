import inspect
import re

from typing import Any
from typing import List

from pyariadne import Function
from pyariadne import pow

from solvers._literal_expression import LiteralExpression


_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE = f"Operation not possible for objects of type PolynomialFunction and "


class PolynomialFunction:  # TODO: this should extend Function -- but it seems like it just constructs the ariadne object without running this code...
    _n_variables: int
    _input_function: callable
    _function_as_literal_expressions: List[LiteralExpression]
    _function_as_ariadne_function: Function

    def __init__(self, n_variables: int, function: callable) -> None:
        self._n_variables = n_variables
        self._input_function = function
        self._function_as_literal_expressions = _convert_polynomial_function_to_literal_expressions(
            polynomial_function=self
        )
        self._function_as_ariadne_function = _convert_function_as_literal_expressions_to_ariadne_function(
            polynomial_function=self
        )

    def __add__(self, other: Any) -> "PolynomialFunction":
        result = None
        if isinstance(other, PolynomialFunction):
            ...
        elif isinstance(other, float) or isinstance(other, int):
            ...
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __sub__(self, other: Any) -> "PolynomialFunction":
        result = None
        if isinstance(other, PolynomialFunction):
            other_as_literal_expressions = other._convert_function_to_literal_expressions()
        elif isinstance(other, float) or isinstance(other, int):
            ...
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __mul__(self, other: Any) -> "PolynomialFunction":  # TODO: this is for obj * obj
        result = None
        if isinstance(other, PolynomialFunction):
            ...
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __rmul__(self, other: Any) -> "PolynomialFunction":  # TODO: this is for ... * obj
        result = None
        if isinstance(other, float) or isinstance(other, int):
            ...
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    @property
    def input(self) -> callable:
        return self._input_function

    @property
    def representation(self) -> List[LiteralExpression]:
        return self._function_as_literal_expressions

    @property
    def n_variables(self) -> int:
        return self._n_variables


def _convert_polynomial_function_to_literal_expressions(
    polynomial_function: PolynomialFunction
) -> List[LiteralExpression]:
    function_str = inspect.getsource(polynomial_function.input)
    lambda_match = re.search(r"lambda x: (.*)", function_str)
    if lambda_match:
        lambda_expression = (
            lambda_match.group(1)
            .replace("-", "+-")
            .replace("[", "")
            .replace("]", "")
            .replace(" ", "")
        )
        function_split_by_literals = re.split(r"\+", lambda_expression)
    else:
        raise Exception("Function not parsable, please use the right format")

    function_as_literal_expression = [
        LiteralExpression(n_variables=polynomial_function.n_variables, expression=x) for x in function_split_by_literals
    ]
    return function_as_literal_expression


def _convert_function_as_literal_expressions_to_ariadne_function(polynomial_function: PolynomialFunction) -> Function:
    elements_to_add = []
    for expression in polynomial_function.representation:
        coefficients = expression.coefficients
        powers = expression.powers
        if all(power == 0 for power in powers):
            elements_to_add.append(str(coefficients[0]))
        else:
            elements_to_multiply = []
            for i, (coefficient, power) in enumerate(zip(coefficients, powers)):
                if coefficient == 0:
                    continue
                x_i = f"x[{i}]"
                term = f"{coefficient}*" if coefficient != 1 else ""
                term += f"pow({x_i},{power})" if power != 1 else x_i

                elements_to_multiply.append(term)

            elements_to_add.append("*".join(elements_to_multiply))

    function_as_string = "lambda x: " + "+".join(elements_to_add)
    function = eval(function_as_string)

    return Function(polynomial_function.n_variables, function)


f = PolynomialFunction(3, lambda x: x[0]**2 + 3*x[1] - 7*x[2])
print(f._function_as_ariadne_function)
