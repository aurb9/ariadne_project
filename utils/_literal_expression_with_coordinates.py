import re
from decimal import Decimal

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pyariadne import Rational
from pyariadne import FloatDP

from utils._scalar import is_scalar
from utils.set_operations import get_joint_and_disjoint_sets


def _format_expression(expression) -> str:
    expression = re.sub(r"/pow\((\w+),(\w+)\)", r"*pow(\1,-\2)", expression)
    expression = re.sub(r"/x(\d+)", r"*pow(x\1,-1)", expression)
    expression = re.sub(r"(\w+)\*\*(\d+)", r"pow(\1,\2)", expression)
    expression = re.sub(r"(-?\d+)\*(.*)", r"\2*\1", expression)
    expression = re.sub(r"\*1$", r"", expression)

    return expression


def _custom_sort(list_of_strings: List[str]) -> List[str]:
    def criterion(item: str) -> int:
        match = re.search(r"x(\d+)", item)
        return int(match.group(1))

    return sorted(set(list_of_strings), key=criterion)


def _get_expression_format(powers: Dict[int, float]) -> str:
    expression_formats = []
    for i, power in powers.items():
        if power == 0:
            continue
        x_i = f"x{i}"
        if power == 1:
            term = x_i
        elif power == 0.5:
            term = f"sqr({x_i})"
        else:
            term = f"pow({x_i}, {power})"

        expression_formats.append(term)

    expression_formats = _custom_sort(list_of_strings=expression_formats)

    return "*".join(expression_formats)


class LiteralExpression:
    _coefficient: int = 1  # TODO: further allow floats?
    _powers: Dict[int, int] = None

    def _case_multiple_x(self, expression: str) -> None:
        expressions = re.split(r"\*", expression)
        for x in expressions:
            self._case_single_x(expression=x)

    def _case_single_x(self, expression: str) -> None:
        if "x" in expression:
            index = int(re.search(r"x(\d+)", expression).group(1))
            self._powers[index] = 1
            if "pow" in expression:
                power = int(re.search(rf"pow\(x{index},(-?\d+)\)", expression).group(1))
                self._powers[index] = power
            if "sqr" in expression:
                self._powers[index] = 0.5
        else:
            if "/" in expression:
                numerator, denominator = expression.split("/")
                self._coefficient = Rational(int(numerator), int(denominator))
            if "." in expression:
                self._coefficient = Decimal(expression)
            else:
                coefficient = int(expression)
                if not self._coefficient:
                    self._coefficient = coefficient
                else:
                    self._coefficient *= coefficient

    def __init__(self, expression: str) -> None:
        expression = _format_expression(expression=expression)
        self._powers = {}
        self._case_multiple_x(expression=expression)
        self._expression_format = _get_expression_format(powers=self._powers)

    def __new__(
        cls,
        expression: Optional[str] = None,
        coefficient: Optional[float] = None,
        powers: Optional[Dict[int, float]] = None
    ) -> "LiteralExpression":
        if expression is not None:
            return super(LiteralExpression, cls).__new__(cls)
        elif coefficient is not None and powers is not None:
            instance = super(LiteralExpression, cls).__new__(cls)
            instance._expression_format = _get_expression_format(powers=powers)
            instance._coefficient = coefficient
            instance._powers = powers
            return instance
        else:
            raise Exception()

    def __repr__(self) -> str:
        return f"LiteralExpression({self._coefficient}, {self._powers})"

    def __neg__(self) -> "LiteralExpression":
        result = LiteralExpression.__new__(
            cls=LiteralExpression,
            coefficient=-self._coefficient,
            powers=self._powers
        )
        return result

    def __add__(self, other: "LiteralExpression") -> "LiteralExpression":
        assert other._expression_format == self._expression_format

        result = LiteralExpression.__new__(
            cls=LiteralExpression,
            coefficient=self._coefficient + other._coefficient,
            powers=self._powers
        )
        return result

    def __sub__(self, other: "LiteralExpression") -> "LiteralExpression":
        return self.__add__(other=-other)

    def __mul__(self, other: Any) -> "LiteralExpression":
        if is_scalar(x=other):
            result = LiteralExpression.__new__(
                cls=LiteralExpression,
                coefficient=self._coefficient * other,
                powers=self._powers
            )
        elif isinstance(other, LiteralExpression):
            self_powers_indexes = set(self._powers.keys())
            other_powers_indexes = set(other._powers.keys())
            common_indexes, missing_self_indexes, missing_other_indexes = get_joint_and_disjoint_sets(
                self_powers_indexes, other_powers_indexes
            )
            powers = {}
            for x in common_indexes:
                powers[x] = self._powers[x] + other._powers[x]

            for x in missing_self_indexes:
                powers[x] = self._powers[x]

            for x in missing_other_indexes:
                powers[x] = other._powers[x]

            result = LiteralExpression.__new__(
                cls=LiteralExpression,
                coefficient=self._coefficient * other._coefficient,
                powers=powers
            )
        else:
            raise Exception()

        return result

    def __rmul__(self, other: Any) -> "LiteralExpression":
        return self.__mul__(other=other)

    def _reciprocal(self) -> "LiteralExpression":
        result = LiteralExpression.__new__(
            cls=LiteralExpression,
            coefficient=int(1 / self._coefficient),
            powers={k: -power for k, power in self._powers.items()}
        )
        return result

    def __truediv__(self, other: Any) -> "LiteralExpression":
        if is_scalar(x=other):
            other_reciprocal = int(1 / other)
        elif isinstance(other, LiteralExpression):
            other_reciprocal = other._reciprocal()
        else:
            raise Exception()

        result = self.__mul__(other=other_reciprocal)
        return result

    def __rtruediv__(self, other: Any) -> "LiteralExpression":
        if not is_scalar(x=other):
            raise Exception()

        self_reciprocal = self._reciprocal()
        result = self_reciprocal.__mul__(other=other)
        return result

    def one_over_x(self) -> "LiteralExpression":
        result = LiteralExpression.__new__(
            cls=LiteralExpression,
            coefficient=self._coefficient,
            powers={k: -power for k, power in self._powers.items()}
        )
        return result

    @property
    def coefficient(self) -> Union[float, FloatDP]:
        return self._coefficient

    @property
    def powers(self) -> List[int]:
        return list(self._powers.values())

    @property
    def degree(self) -> Union[int, float]:
        if not self._powers:
            return 0

        return max(self._powers.values())
