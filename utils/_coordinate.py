from typing import Any
from typing import List
from typing import Optional

from pyariadne import Dyadic
from pyariadne import FloatDPBounds
from pyariadne import MultiIndex
from pyariadne import Rational

from utils._scalar import is_scalar
from utils.add_lists_elementwise import add_lists_elementwise

_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE = f"Operation not possible for objects of type Coordinate and "


class Coordinate:
    _coefficient: FloatDPBounds = None
    # _powers: MultiIndex = None
    _powers: List[int] = None

    def __init__(self, coefficient: FloatDPBounds, powers: Optional[MultiIndex] = MultiIndex([])) -> None:
        self._coefficient = coefficient
        powerss = []
        for x in str(powers):
            if x == ";":
                break
            if x.isnumeric():
                powerss.append(int(x))
        self._powers = powerss
        # self._powers = powers

    def __repr__(self) -> str:
        return "Coordinate({" + str(self._powers) + ": " + str(self._coefficient) + "})"

    def __neg__(self) -> "Coordinate":
        result = Coordinate(coefficient=-self._coefficient, powers=MultiIndex(self._powers))

        return result

    def __add__(self, other: "Coordinate") -> "Coordinate":
        assert self.powers == other.powers, "Cannot perform operation on different coordinates"
        result = Coordinate(coefficient=self._coefficient + other._coefficient, powers=MultiIndex(self._powers))

        return result

    def __sub__(self, other: "Coordinate") -> "Coordinate":
        return self.__add__(other=-other)

    def __mul__(self, other: Any) -> "Coordinate":
        if is_scalar(x=other):
            result = Coordinate(coefficient=self._coefficient * other, powers=MultiIndex(self._powers))
        elif isinstance(other, Coordinate):
            powers = add_lists_elementwise(self._powers, other._powers)
            result = Coordinate(coefficient=self._coefficient * other._coefficient, powers=MultiIndex(powers))
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __rmul__(self, other: Any) -> "Coordinate":
        return self.__mul__(other=other)

    def _reciprocal(self) -> "Coordinate":
        result = Coordinate(
            coefficient=Dyadic(Rational(1, self._coefficient)),
            powers=MultiIndex([-x for x in self._powers])
        )

        return result

    def __truediv__(self, other: Any) -> "Coordinate":
        if is_scalar(x=other):
            other_reciprocal = Dyadic(Rational(1, other))
        elif isinstance(other, Coordinate):
            other_reciprocal = other._reciprocal()
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        result = self.__mul__(other=other_reciprocal)
        return result

    def __rtruediv__(self, other: Any) -> "Coordinate":
        if not is_scalar(x=other):
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        self_reciprocal = self._reciprocal()
        result = self_reciprocal.__mul__(other=other)

        return result

    def one_over_x(self) -> "Coordinate":
        result = Coordinate(coefficient=self._coefficient, powers=MultiIndex([-x for x in self._powers]))

        return result

    @property
    def coefficient(self) -> FloatDPBounds:
        return self._coefficient

    @property
    def powers(self) -> MultiIndex:
        return MultiIndex(self._powers)
