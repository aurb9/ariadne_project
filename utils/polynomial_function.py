from typing import Any
from typing import Dict
from typing import Optional

from pyariadne import Function, sqr, FloatDP, dp, pow, Real, Rational

from utils._convert_function_as_literal_expressions_to_function import (
    _convert_function_as_literal_expressions_to_function
)
from utils._convert_function_to_literal_expressions import _convert_function_to_literal_expressions
from utils._literal_expression import LiteralExpression
from utils._scalar import is_scalar
from utils.set_operations import get_joint_and_disjoint_sets

_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE = f"Operation not possible for objects of type PolynomialFunction and "


class PolynomialFunction:
    # TODO: this should extend Function but it seems like it just constructs the ariadne object
    #  without running this code...
    _n_variables: int
    _function_as_literal_expressions: Dict[str, LiteralExpression]

    def __init__(self, n_variables: int, f: callable) -> None:
        self._n_variables = n_variables
        self._function_as_literal_expressions = _convert_function_to_literal_expressions(n_variables=n_variables, f=f)

    def __new__(
        cls,
        n_variables: int,
        f: Optional[callable] = None,
        function_as_literal_expressions: Optional[Dict[str, LiteralExpression]] = None
    ) -> "PolynomialFunction":
        if function_as_literal_expressions is not None:
            instance = super(PolynomialFunction, cls).__new__(cls)
            instance._n_variables = n_variables
            instance._function_as_literal_expressions = function_as_literal_expressions
            return instance
        else:
            return super(PolynomialFunction, cls).__new__(cls)

    def __repr__(self) -> str:
        f = _convert_function_as_literal_expressions_to_function(
            function_as_literal_expressions=self._function_as_literal_expressions
        )
        return Function(self._n_variables, f).__repr__()

    def __call__(self, x: Any):
        f = _convert_function_as_literal_expressions_to_function(
            function_as_literal_expressions=self._function_as_literal_expressions
        )
        return Function(self._n_variables, f)(x)

    def __neg__(self) -> "PolynomialFunction":
        function_as_literal_expressions = {}
        for expression_format, expression_literal in self._function_as_literal_expressions.items():
            new_expression = -expression_literal
            function_as_literal_expressions[expression_format] = new_expression

        return PolynomialFunction.__new__(
            cls=PolynomialFunction,
            n_variables=self._n_variables,
            function_as_literal_expressions=function_as_literal_expressions
        )

    def __add__(self, other: Any) -> "PolynomialFunction":  # TODO: done!
        function_as_literal_expressions = {}
        if is_scalar(x=other):
            function_as_literal_expressions = self._function_as_literal_expressions.copy()
            other_as_literal_expression = LiteralExpression(expression=str(other))
            if "" in self._function_as_literal_expressions.keys():
                function_as_literal_expressions[""] = (
                    self._function_as_literal_expressions[""] + other_as_literal_expression
                )
            else:
                function_as_literal_expressions[""] = other_as_literal_expression

            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=self._n_variables,
                function_as_literal_expressions=function_as_literal_expressions
            )

        elif isinstance(other, PolynomialFunction):
            self_literal_expressions = set(self._function_as_literal_expressions.keys())
            other_literal_expressions = set(other._function_as_literal_expressions.keys())
            common_literal_expressions, missing_self_expressions, missing_other_expressions = (
                get_joint_and_disjoint_sets(self_literal_expressions, other_literal_expressions)
            )
            for x in common_literal_expressions:
                new_expression = self._function_as_literal_expressions[x] + other._function_as_literal_expressions[x]
                function_as_literal_expressions[new_expression.format] = new_expression

            for x in missing_self_expressions:
                function_as_literal_expressions[x] = self._function_as_literal_expressions[x]

            for x in missing_other_expressions:
                function_as_literal_expressions[x] = other._function_as_literal_expressions[x]

            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=max(self._n_variables, other._n_variables),
                function_as_literal_expressions=function_as_literal_expressions
            )

        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __sub__(self, other: Any) -> "PolynomialFunction":
        return self.__add__(other=-other)

    def __mul__(self, other: Any) -> "PolynomialFunction":
        function_as_literal_expressions = {}
        if is_scalar(x=other):
            for expression in self._function_as_literal_expressions.values():
                new_expression = expression * other
                function_as_literal_expressions[new_expression.format] = new_expression

            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=self._n_variables,
                function_as_literal_expressions=function_as_literal_expressions
            )

        elif isinstance(other, PolynomialFunction):
            for self_expression in self._function_as_literal_expressions.values():
                for other_expression in other._function_as_literal_expressions.values():
                    new_expression = self_expression * other_expression
                    function_as_literal_expressions[new_expression.format] = new_expression

            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=max(self._n_variables, other._n_variables),
                function_as_literal_expressions=function_as_literal_expressions
            )

        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __rmul__(self, other: Any) -> "PolynomialFunction":
        return self.__mul__(other=other)

    def __truediv__(self, other: Any) -> "PolynomialFunction":
        function_as_literal_expressions = {}
        if is_scalar(x=other):
            for expression in self._function_as_literal_expressions.values():
                new_expression = expression / other
                function_as_literal_expressions[new_expression.format] = new_expression

            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=self._n_variables,
                function_as_literal_expressions=function_as_literal_expressions
            )

        elif isinstance(other, PolynomialFunction):
            for self_expression in self._function_as_literal_expressions.values():
                for other_expression in other._function_as_literal_expressions.values():
                    new_expression = self_expression / other_expression
                    function_as_literal_expressions[new_expression.format] = new_expression

            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=max(self._n_variables, other._n_variables),
                function_as_literal_expressions=function_as_literal_expressions
            )

        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __rtruediv__(self, other: Any) -> "PolynomialFunction":  # TODO: this does not work
        return self.__truediv__(other=other)

    @property
    def n_variables(self) -> int:
        return self._n_variables


f = PolynomialFunction(n_variables=2, f=lambda x: 5*x[1] + 10)
g = PolynomialFunction(n_variables=2, f=lambda x: x[1] * x[0])

print(f/g)
