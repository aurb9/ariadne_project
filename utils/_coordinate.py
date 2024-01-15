import re

from typing import Any
from typing import List
from typing import Optional

from pyariadne import Decimal
from pyariadne import Dyadic
from pyariadne import Rational
from pyariadne import Real

from utils._scalar import is_scalar
from utils.add_lists_elementwise import add_lists_elementwise


def _format_expression(expression) -> str:
    expression = re.sub(r"/pow\((\w+),(\w+)\)", r"*pow(\1,-\2)", expression)
    expression = re.sub(r"/x(\d+)", r"*pow(x\1,-1)", expression)
    expression = re.sub(r"(\w+)\*\*(\d+)", r"pow(\1,\2)", expression)
    expression = re.sub(r"(-?\w+)\*(.*)", r"\2*\1", expression)
    expression = re.sub(r"\*1$", r"", expression)

    return expression


def _custom_sort(list_of_strings: List[str]) -> List[str]:
    def criterion(item: str) -> int:
        match = re.search(r"x(\d+)", item)
        return int(match.group(1))

    return sorted(set(list_of_strings), key=criterion)


class Coordinate:
    _coefficient: Dyadic = Dyadic("1")
    _powers: List[int] = None

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
        else:
            if "/" in expression:
                numerator, denominator = expression.split("/")
                self._coefficient = Dyadic(Rational(int(numerator), int(denominator)))
            if "." in expression:
                self._coefficient = Dyadic(Decimal(expression))
            else:
                coefficient = Dyadic(expression)
                if not self._coefficient:
                    self._coefficient = coefficient
                else:
                    self._coefficient *= coefficient

    def __init__(self, n_variables: int, expression: str) -> None:
        expression = _format_expression(expression=expression)
        if not expression or expression == "0" or "*0" in expression:
            return

        self._powers = [0 for _ in range(n_variables)]
        self._case_multiple_x(expression=expression)

    def __new__(
        cls,
        n_variables: Optional[int] = None,
        expression: Optional[str] = None,
        coefficient: Optional[float] = None,
        powers: Optional[List[int]] = None
    ) -> "Coordinate":
        if expression is not None:
            return super(Coordinate, cls).__new__(cls)
        elif coefficient is not None and powers is not None:
            instance = super(Coordinate, cls).__new__(cls)
            instance._coefficient = coefficient
            instance._powers = powers
            return instance
        else:
            raise Exception()

    def __repr__(self) -> str:
        return "Coordinate({" + str(tuple(self._powers)) + ": " + str(self._coefficient) + "})"

    def __neg__(self) -> "Coordinate":
        result = Coordinate.__new__(
            cls=Coordinate,
            coefficient=-self._coefficient,
            powers=self._powers
        )
        return result

    def __add__(self, other: "Coordinate") -> "Coordinate":
        assert self.powers == other.powers, "Cannot perform operation on different coordinates"
        result = Coordinate.__new__(
            cls=Coordinate,
            coefficient=self._coefficient + other._coefficient,
            powers=self._powers
        )
        return result

    def __sub__(self, other: "Coordinate") -> "Coordinate":
        return self.__add__(other=-other)

    def __mul__(self, other: Any) -> "Coordinate":
        if is_scalar(x=other):
            result = Coordinate.__new__(
                cls=Coordinate,
                coefficient=self._coefficient * other,
                powers=self._powers
            )
        elif isinstance(other, Coordinate):
            powers = add_lists_elementwise(self._powers, other._powers)
            result = Coordinate.__new__(
                cls=Coordinate,
                coefficient=self._coefficient * other._coefficient,
                powers=powers
            )
        else:
            raise Exception()

        return result

    def __rmul__(self, other: Any) -> "Coordinate":
        return self.__mul__(other=other)

    def _reciprocal(self) -> "Coordinate":
        result = Coordinate.__new__(
            cls=Coordinate,
            coefficient=Dyadic(Rational(1, self._coefficient)),
            powers=[-x for x in self._powers]
        )
        return result

    def __truediv__(self, other: Any) -> "Coordinate":
        if is_scalar(x=other):
            other_reciprocal = Dyadic(Rational(1, other))
        elif isinstance(other, Coordinate):
            other_reciprocal = other._reciprocal()
        else:
            raise Exception()

        result = self.__mul__(other=other_reciprocal)
        return result

    def __rtruediv__(self, other: Any) -> "Coordinate":
        if not is_scalar(x=other):
            raise Exception()

        self_reciprocal = self._reciprocal()
        result = self_reciprocal.__mul__(other=other)
        return result

    def one_over_x(self) -> "Coordinate":
        result = Coordinate.__new__(
            cls=Coordinate,
            coefficient=self._coefficient,
            powers=[-x for x in self._powers]
        )
        return result

    @property
    def coefficient(self) -> Real:
        return self._coefficient

    @property
    def powers(self) -> List[int]:
        return self._powers

    @property
    def degree(self) -> int:
        if not self._powers:
            return 0

        return max(self._powers)
