from typing import Any
from typing import List
from typing import Optional
from typing import Union

from pyariadne import Dyadic
from pyariadne import Function
from pyariadne import Rational

from utils._convert_coordinates_to_function import (
    convert_coordinates_to_function
)
from utils._convert_function_to_coordinates import convert_function_to_coordinates
from utils._coordinate import Coordinate
from utils._scalar import is_scalar

_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE = f"Operation not possible for objects of type PolynomialFunction and "


class PolynomialFunction:
    _n_variables: int
    _coordinates: List[Coordinate]

    def __init__(self, n_variables: int, f: Union[str, Function]) -> None:
        self._n_variables = n_variables
        self._coordinates = convert_function_to_coordinates(n_variables=self._n_variables, f=f)

    def __new__(
        cls,
        n_variables: int,
        f: Optional[callable] = None,
        coordinates: Optional[List[Coordinate]] = None
    ) -> "PolynomialFunction":
        if coordinates is not None:
            instance = super(PolynomialFunction, cls).__new__(cls)
            instance._n_variables = n_variables
            instance._coordinates = coordinates
            return instance
        else:
            return super(PolynomialFunction, cls).__new__(cls)

    def __repr__(self) -> str:
        return self.function.__repr__()

    def __call__(self, x: Any) -> Any:
        if is_scalar(x=x):
            return self.function(x)
        elif isinstance(x, PolynomialFunction):
            pass
        else:
            raise Exception(f"'PolynomialFunction' object is not callable with object of type {type(x)}")

    def __neg__(self) -> "PolynomialFunction":
        coordinates = [-x for x in self._coordinates]
        return PolynomialFunction.__new__(
            cls=PolynomialFunction,
            n_variables=self._n_variables,
            coordinates=coordinates
        )

    def __add__(self, other: Any) -> "PolynomialFunction":
        coordinates = self._coordinates.copy()
        if is_scalar(x=other):
            other_coordinate = Coordinate(n_variables=self._n_variables, expression=str(other))
            constant_coordinate = (0 for _ in range(self._n_variables))
            did_update = False
            for i, x in enumerate(coordinates):
                if x.powers == constant_coordinate:
                    coordinates[i] = x + other_coordinate
                    did_update = True
                    break

            if not did_update:
                coordinates.append(other_coordinate)

        elif isinstance(other, PolynomialFunction):
            other_coordinates = other._coordinates
            for y in other_coordinates:
                did_update = False
                for i, x in enumerate(coordinates):
                    if x.powers == y.powers:
                        coordinates[i] = x + y
                        did_update = True
                        break
                if not did_update:
                    coordinates.append(y)
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        result = PolynomialFunction.__new__(
            cls=PolynomialFunction,
            n_variables=max(self._n_variables, other.n_variables),
            coordinates=coordinates
        )
        return result

    def __radd__(self, other: Any) -> "PolynomialFunction":
        return self.__add__(other=other)

    def __sub__(self, other: Any) -> "PolynomialFunction":
        return self.__add__(other=-other)

    def __mul__(self, other: Any) -> "PolynomialFunction":
        if is_scalar(x=other):
            coordinates = [x*other for x in self._coordinates]
            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=self._n_variables,
                coordinates=coordinates
            )
        elif isinstance(other, PolynomialFunction):
            coordinates = [x * y for x in self._coordinates for y in other._coordinates]
            result = PolynomialFunction.__new__(
                cls=PolynomialFunction,
                n_variables=max(self._n_variables, other._n_variables),
                coordinates=coordinates
            )
        else:
            raise Exception(_OPERATION_NOT_POSSIBLE_ERROR_MESSAGE, type(other))

        return result

    def __rmul__(self, other: Any) -> "PolynomialFunction":
        return self.__mul__(other=other)

    def _reciprocal(self) -> "PolynomialFunction":
        coordinates = [1/x for x in self._coordinates]
        result = PolynomialFunction.__new__(
            cls=PolynomialFunction,
            n_variables=self._n_variables,
            coordinates=coordinates
        )
        return result

    def __truediv__(self, other: Any) -> "PolynomialFunction":
        if is_scalar(x=other):
            other_reciprocal = Dyadic(Rational(1, other))
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

    # TODO: eventually this should go to __call__
    def evaluate_at_one_over_x(self) -> "PolynomialFunction":
        coordinates = [x.one_over_x() for x in self._coordinates]
        result = PolynomialFunction.__new__(
            cls=PolynomialFunction,
            n_variables=self._n_variables,
            coordinates=coordinates
        )
        return result

    @property
    def n_variables(self) -> int:
        return self._n_variables

    @property
    def function(self) -> Function:
        f = convert_coordinates_to_function(function_as_coordinates=self._coordinates)
        return Function(self._n_variables, f)

    def max_degree_nth_variable(self, n: int) -> int:
        assert n < self._n_variables, f"{n}th variable does not exist, there are at most {self._n_variables} variables"

        max_degree = max([x.powers[n] for x in self._coordinates])
        return max_degree

    # TODO
    # @staticmethod
    # def coordinate(n: int, i: int):
    #     # n variables, and i index
    #     # return function?
    #     pass

    @staticmethod
    def constant(c: Any) -> "PolynomialFunction":
        return PolynomialFunction(n_variables=0, f=str(c))
