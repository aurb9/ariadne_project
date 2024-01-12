from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pyariadne import Function
from pyariadne import Real

from utils._convert_function_as_literal_expressions_to_function import (
    convert_function_as_literal_expressions_to_function
)
from utils._convert_function_to_literal_expressions import convert_function_to_literal_expressions
from utils._literal_expression_with_coordinates import LiteralExpression
from utils._scalar import is_scalar
from utils.set_operations import get_joint_and_disjoint_sets

_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE = f"Operation not possible for objects of type PolynomialFunction and "


class PolynomialFunction:
    # TODO: this should extend Function but it seems like it just constructs the ariadne object
    #  without running this code...
    _n_variables: int
    _coordinates: Dict[List[int], Real]
    _function_as_literal_expressions: Dict[str, LiteralExpression]

    def __init__(self, n_variables: int, f: Union[str, Function]) -> None:
        self._n_variables = n_variables
        self._function_as_literal_expressions = convert_function_to_literal_expressions(f=f)

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
        f = convert_function_as_literal_expressions_to_function(
            n_variables=self._n_variables, function_as_literal_expressions=self._function_as_literal_expressions
        )
        return Function(self._n_variables, f).__repr__()

    def __call__(self, x: Any) -> Any:
        return self.function(x)

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

    def __add__(self, other: Any) -> "PolynomialFunction":
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

    # TODO
    # def __radd__(self, other: Any) -> "PolynomialFunction":
    #     return PolynomialFunction()

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

    def _reciprocal(self) -> "PolynomialFunction":
        function_as_literal_expressions = {}
        for expression in self._function_as_literal_expressions.values():
            new_expression = 1/expression
            function_as_literal_expressions[new_expression.format] = new_expression

        result = PolynomialFunction.__new__(
            cls=PolynomialFunction,
            n_variables=self._n_variables,
            function_as_literal_expressions=function_as_literal_expressions
        )
        return result

    # TODO: division does not support types x/(x + 1) for instance, it instead computes x/x + x/1
    def __truediv__(self, other: Any) -> "PolynomialFunction":
        if is_scalar(x=other):
            other_reciprocal = int(1 / other)
        elif isinstance(other, PolynomialFunction):
            other_reciprocal = other._reciprocal()
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        result = self.__mul__(other=other_reciprocal)
        return result

    def __rtruediv__(self, other: Any) -> "PolynomialFunction":
        if not is_scalar(x=other):
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        self_reciprocal = self._reciprocal()
        result = self_reciprocal.__mul__(other=other)
        return result

    def evaluate_at_one_over_x(self) -> "PolynomialFunction":
        function_as_literal_expressions = {}
        for expression in self._function_as_literal_expressions.values():
            new_expression = expression.one_over_x()
            function_as_literal_expressions[new_expression.powers] = new_expression.coefficient

        result = PolynomialFunction.__new__(
            cls=PolynomialFunction,
            n_variables=self._n_variables,
            function_as_literal_expressions=function_as_literal_expressions
        )
        return result

    @property
    def n_variables(self) -> int:
        return self._n_variables

    @property
    def function(self) -> Function:
        f = convert_function_as_literal_expressions_to_function(
            n_variables=self.n_variables, function_as_literal_expressions=self._function_as_literal_expressions
        )
        return Function(self._n_variables, f)

    @property
    def degree(self) -> Union[int, float]:
        degrees = [expression.degree for expression in self._function_as_literal_expressions.values()]
        return max(degrees)

    def max_degree_nth_variable(self, n: int) -> float:
        assert n < self._n_variables, f"{n}th variable does not exist, there are at most {self._n_variables} variables"
        values_containing_n = [
            expression.powers for format, expression in self._function_as_literal_expressions.items()
            if str(n) in format
        ]
        max_degree = max([x[n] for x in values_containing_n])

        return max_degree

    # TODO
    # @staticmethod
    # def coordinate(n: int, i: int):
    #     # n variables, and i index
    #     # return function?
    #     pass

    @staticmethod
    def constant(c: Real) -> "PolynomialFunction":
        return PolynomialFunction(n_variables=0, f=str(c))
